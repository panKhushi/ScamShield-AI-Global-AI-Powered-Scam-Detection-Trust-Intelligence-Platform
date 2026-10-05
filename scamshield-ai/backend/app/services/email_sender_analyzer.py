import re
from urllib.parse import urlparse

from app.models import ScoreFactor

EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
KNOWN_BRANDS = {"paypal", "microsoft", "apple", "amazon", "google", "bank", "irs"}
FREE_PROVIDERS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me"}


def analyze_email_sender(value: str) -> list[ScoreFactor]:
    addresses = EMAIL_PATTERN.findall(value)
    if not addresses:
        return [ScoreFactor(
            name="Email Sender Analysis",
            weight=0.15,
            status="warning",
            detail="No sender email address was found; sender authenticity is unknown",
        )]

    address = addresses[0].lower()
    domain = address.rsplit("@", 1)[-1]
    local_part = address.split("@", 1)[0]
    brand_impersonation = any(brand in local_part or brand in domain for brand in KNOWN_BRANDS)
    if brand_impersonation and domain in FREE_PROVIDERS:
        status = "bad"
        detail = f"Sender claims a recognizable brand but uses a free email provider ({domain})"
    elif domain in FREE_PROVIDERS:
        status = "warning"
        detail = f"Sender uses a free email provider ({domain}); verify independently"
    else:
        status = "good"
        detail = f"Sender domain detected: {domain}"

    return [ScoreFactor(name="Email Sender Analysis", weight=0.15, status=status, detail=detail)]
