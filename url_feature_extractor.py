"""Extract URL-only lexical features for phishing detection (v2).

v1 of this extractor only computed 8 coarse structural features (IP
address, URL length bucket, shortener, @ symbol, //, dash-in-domain,
subdomain count, https-token). Those 8 features are too coarse: two
completely different real websites can share the exact same 8-feature
"shape" (e.g. any long tracking URL on a single-subdomain domain with
no dash and no IP), causing the model to give them identical risk
scores.

v2 replaces this with 20 finer-grained lexical features -- character
counts and structural counts computed directly from the URL string,
its domain, and its query string. These are the same feature
definitions used in the "Phishing-Dataset" lexical feature set
(Vrbancic, Fister Jr., Podgorelec - Data in Brief, 2020), restricted
to columns that are genuinely derivable from the URL text alone (no
live DNS/WHOIS/SSL/web-traffic lookups, since this app only ever sees
a URL string typed by the user, not a live connection to the site).
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import parse_qsl, urlparse

import pandas as pd


URL_FEATURE_COLUMNS = [
    "length_url",
    "qty_dot_url",
    "qty_hyphen_url",
    "qty_underline_url",
    "qty_slash_url",
    "qty_questionmark_url",
    "qty_equal_url",
    "qty_at_url",
    "qty_and_url",
    "qty_percent_url",
    "domain_length",
    "qty_dot_domain",
    "qty_hyphen_domain",
    "qty_vowels_domain",
    "domain_in_ip",
    "qty_slash_directory",
    "qty_params",
    "params_length",
    "email_in_url",
    "url_shortened",
]

_SHORTENER_HOSTS = {
    "bit.ly",
    "bitly.com",
    "cutt.ly",
    "goo.gl",
    "is.gd",
    "ow.ly",
    "rb.gy",
    "rebrand.ly",
    "shorturl.at",
    "tiny.cc",
    "tinyurl.com",
    "t.co",
    "trib.al",
    "v.gd",
    "buff.ly",
}

_EMAIL_PATTERN = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.IGNORECASE)
_VOWELS = set("aeiouAEIOU")


def normalize_url(value: str) -> str:
    """Return a normalized URL or raise ValueError for malformed input."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Please enter a website URL.")

    candidate = value.strip()
    if not re.match(r"^[a-z][a-z0-9+.-]*://", candidate, re.IGNORECASE):
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS website URL.")
    if any(character.isspace() for character in parsed.hostname):
        raise ValueError("The URL hostname cannot contain spaces.")

    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("The URL contains an invalid port.") from exc

    return candidate


def _is_ip_address(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def _registered_host(hostname: str) -> str:
    parts = hostname.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else hostname


def extract_url_features(value: str) -> pd.DataFrame:
    """Extract the 20 URL-derived lexical columns the model expects."""
    normalized = normalize_url(value)
    parsed = urlparse(normalized)
    hostname = (parsed.hostname or "").lower()
    registered_host = _registered_host(hostname)

    path = parsed.path or ""
    directory = path.rsplit("/", 1)[0] if "/" in path.strip("/") else path
    query = parsed.query or ""

    # -1 mirrors the training dataset's convention for "not applicable"
    # (e.g. a URL with no query string has no params to count).
    if query:
        qty_params = len(parse_qsl(query))
        params_length = len(query)
    else:
        qty_params = -1
        params_length = -1

    if path in ("", "/"):
        qty_slash_directory = -1
    else:
        qty_slash_directory = directory.count("/")

    features = {
        "length_url": len(normalized),
        "qty_dot_url": normalized.count("."),
        "qty_hyphen_url": normalized.count("-"),
        "qty_underline_url": normalized.count("_"),
        "qty_slash_url": normalized.count("/"),
        "qty_questionmark_url": normalized.count("?"),
        "qty_equal_url": normalized.count("="),
        "qty_at_url": normalized.count("@"),
        "qty_and_url": normalized.count("&"),
        "qty_percent_url": normalized.count("%"),
        "domain_length": len(hostname),
        "qty_dot_domain": hostname.count("."),
        "qty_hyphen_domain": hostname.count("-"),
        "qty_vowels_domain": sum(1 for character in hostname if character in _VOWELS),
        "domain_in_ip": 1 if _is_ip_address(hostname) else 0,
        "qty_slash_directory": qty_slash_directory,
        "qty_params": qty_params,
        "params_length": params_length,
        "email_in_url": 1 if _EMAIL_PATTERN.search(normalized) else 0,
        "url_shortened": 1 if registered_host in _SHORTENER_HOSTS else 0,
    }
    return pd.DataFrame([features], columns=URL_FEATURE_COLUMNS, dtype="int64")


__all__ = ["URL_FEATURE_COLUMNS", "extract_url_features", "normalize_url"]
