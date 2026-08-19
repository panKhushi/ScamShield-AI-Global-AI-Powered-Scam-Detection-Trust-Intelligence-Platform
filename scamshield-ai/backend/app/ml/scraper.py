import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def fetch_page_html(url: str, timeout: int = 8) -> str | None:
    """Fetch raw HTML for a URL. Returns None if the site can't be reached."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def get_root_domain(domain: str) -> str:
    """Reduce 'commons.wikimedia.org' -> 'wikimedia.org' for a fairer same-site check."""
    parts = domain.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain


def get_anchor_url_score(html: str, base_url: str) -> int:
    """
    Analyzes <a> tag hrefs to determine what fraction point to an external domain.
    Returns: 1 (legitimate), 0 (suspicious), -1 (phishing)
    """
    if not html:
        return 0

    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url if base_url.startswith("http") else f"https://{base_url}").netloc.replace("www.", "")
    base_root = get_root_domain(base_domain)

    anchors = soup.find_all("a", href=True)
    if not anchors:
        return 0

    total = 0
    external = 0
    unusable = 0

    for tag in anchors:
        href = tag["href"].strip()
        total += 1

        if href in ("#", "") or href.lower().startswith("javascript:"):
            unusable += 1
            continue

        link_domain = urlparse(href).netloc.replace("www.", "")
        link_root = get_root_domain(link_domain) if link_domain else ""

        if link_root and link_root != base_root:
            external += 1

    if total == 0:
        return 0

    external_ratio = (external + unusable) / total

    if external_ratio < 0.31:
        return 1
    elif external_ratio <= 0.67:
        return 0
    else:
        return -1


def get_links_in_script_tags_score(html: str, base_url: str) -> int:
    """
    Analyzes <script src> and <link href> tags for what fraction point externally.
    Returns: 1 (legitimate), 0 (suspicious), -1 (phishing)
    """
    if not html:
        return 0

    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url if base_url.startswith("http") else f"https://{base_url}").netloc.replace("www.", "")
    base_root = get_root_domain(base_domain)

    resources = []
    resources += [tag.get("src") for tag in soup.find_all("script") if tag.get("src")]
    resources += [tag.get("href") for tag in soup.find_all("link") if tag.get("href")]

    total = len(resources)
    if total == 0:
        return 1

    external = 0
    for src in resources:
        src = src.strip()
        if src.startswith("//"):
            src = "https:" + src

        link_domain = urlparse(src).netloc.replace("www.", "")
        link_root = get_root_domain(link_domain) if link_domain else ""

        if link_root and link_root != base_root:
            external += 1

    external_ratio = external / total

    if external_ratio < 0.17:
        return 1
    elif external_ratio <= 0.81:
        return 0
    else:
        return -1


_tranco_ranks = None

def _load_tranco_ranks() -> dict:
    global _tranco_ranks
    if _tranco_ranks is None:
        path = Path(__file__).parent / "data" / "tranco_list.csv"
        df = pd.read_csv(path, names=["rank", "domain"], header=None)
        _tranco_ranks = dict(zip(df["domain"], df["rank"]))
    return _tranco_ranks


def get_website_traffic_score(domain: str) -> int:
    """
    Looks up domain rank in the Tranco top 1M list.
    Returns: 1 (legitimate/high traffic), 0 (suspicious/low traffic), -1 (phishing/no traffic)
    """
    ranks = _load_tranco_ranks()
    clean_domain = domain.replace("www.", "").lower().strip()

    rank = ranks.get(clean_domain)

    if rank is None:
        return -1
    elif rank <= 100_000:
        return 1
    else:
        return 0

import re


def get_https_score(url: str) -> int:
    """
    Checks HTTPS usage. Legit sites use HTTPS; phishing sites often don't
    (or use it inconsistently on suspicious domains).
    """
    return 1 if url.strip().lower().startswith("https://") else -1


def get_prefix_suffix_score(domain: str) -> int:
    """
    Checks for a hyphen in the domain (e.g. 'paypal-secure.com').
    Legit brands rarely use hyphens in their root domain.
    """
    domain = domain.replace("www.", "")
    return -1 if "-" in domain else 1


def get_subdomains_score(domain: str) -> int:
    """
    Counts dots in the domain to estimate subdomain depth.
    e.g. 'secure.login.paypal.verify.com' has many subdomains — a common phishing trick.
    """
    domain = domain.replace("www.", "")
    dot_count = domain.count(".")

    if dot_count <= 1:
        return 1       # e.g. "google.com"
    elif dot_count == 2:
        return 0        # e.g. "mail.google.com" — normal but worth a flag
    else:
        return -1       # e.g. "secure.mail.login.google.com" — suspicious depth


def get_domain_reg_len_score(domain_age_days: int | None) -> int:
    """
    Domains registered for a long time are more trustworthy.
    Approximates the dataset's 'DomainRegLen' (originally registration length,
    here approximated using domain age since expiry data isn't always available).
    """
    if domain_age_days is None:
        return -1  # unknown WHOIS data is itself a red flag

    if domain_age_days >= 365:
        return 1
    else:
        return -1