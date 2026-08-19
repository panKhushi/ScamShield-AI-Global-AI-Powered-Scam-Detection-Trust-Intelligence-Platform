import requests
from bs4 import BeautifulSoup
from app.models import ScoreFactor
from app.services.ssrf_guard import is_safe_url

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

MAX_RESPONSE_BYTES = 2_000_000  # 2 MB cap
FETCH_TIMEOUT = 8


def fetch_page_safely(url: str) -> tuple[str | None, str]:
    """
    Fetches HTML content with SSRF protection, timeout, and size limits.
    Returns (html_or_none, error_reason).
    """
    safe, reason = is_safe_url(url)
    if not safe:
        return None, reason

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=FETCH_TIMEOUT,
            allow_redirects=True,
            stream=True,
        )

        content = b""
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > MAX_RESPONSE_BYTES:
                return None, "Response exceeded size limit"

        return content.decode(errors="ignore"), ""

    except requests.RequestException as e:
        return None, f"Fetch failed: {str(e)}"


def analyze_website_content(url: str) -> list[ScoreFactor]:
    """
    Analyzes a website's static HTML for login/credential/payment form
    presence — never executes JavaScript, only parses markup.
    """
    html, error = fetch_page_safely(url)

    if html is None:
        return [ScoreFactor(
            name="Website Content Analysis",
            weight=0.20,
            status="warning",
            detail=f"Could not analyze page content: {error}",
        )]

    soup = BeautifulSoup(html, "html.parser")
    factors = []

    # 1. Login/credential form detection
    password_fields = soup.find_all("input", {"type": "password"})
    if password_fields:
        factors.append(ScoreFactor(
            name="Login Form Detected",
            weight=0.10,
            status="warning",
            detail=f"Page contains {len(password_fields)} password field(s) — verify this is the legitimate site before entering credentials",
        ))
    else:
        factors.append(ScoreFactor(
            name="Login Form Detected",
            weight=0.10,
            status="good",
            detail="No login/password form detected on this page",
        ))

    # 2. OTP field detection (common patterns: name/id containing "otp", "verification", "code")
    otp_indicators = soup.find_all("input", attrs={
        "name": lambda x: x and any(k in x.lower() for k in ["otp", "verification", "verifycode"]),
    }) + soup.find_all("input", attrs={
        "placeholder": lambda x: x and "otp" in x.lower(),
    })
    if otp_indicators:
        factors.append(ScoreFactor(
            name="OTP Request Detected",
            weight=0.15,
            status="warning",
            detail="Page requests an OTP/verification code — legitimate services rarely ask for this via a random link",
        ))
    else:
        factors.append(ScoreFactor(
            name="OTP Request Detected",
            weight=0.15,
            status="good",
            detail="No OTP/verification code field detected",
        ))

    # 3. Payment/card field detection
    payment_indicators = soup.find_all("input", attrs={
        "name": lambda x: x and any(k in x.lower() for k in ["card", "cvv", "cardnumber", "expiry"]),
    })
    if payment_indicators:
        factors.append(ScoreFactor(
            name="Payment Form Detected",
            weight=0.15,
            status="warning",
            detail="Page contains payment/card entry fields — confirm this is a trusted, secure checkout before proceeding",
        ))
    else:
        factors.append(ScoreFactor(
            name="Payment Form Detected",
            weight=0.15,
            status="good",
            detail="No payment/card form detected",
        ))

    # 4. Contact info / policy presence (legitimacy signal)
    text_lower = soup.get_text().lower()
    has_contact = any(k in text_lower for k in ["contact us", "contact@", "support@"])
    has_policy = any(k in text_lower for k in ["privacy policy", "terms of service", "terms & conditions"])

    if has_contact and has_policy:
        factors.append(ScoreFactor(
            name="Business Legitimacy Signals",
            weight=0.10,
            status="good",
            detail="Page includes contact information and policy pages",
        ))
    elif has_contact or has_policy:
        factors.append(ScoreFactor(
            name="Business Legitimacy Signals",
            weight=0.10,
            status="warning",
            detail="Page includes some but not all expected legitimacy signals (contact info, policies)",
        ))
    else:
        factors.append(ScoreFactor(
            name="Business Legitimacy Signals",
            weight=0.10,
            status="bad",
            detail="Page lacks visible contact information or policy pages — common on hastily built scam sites",
        ))

    return factors