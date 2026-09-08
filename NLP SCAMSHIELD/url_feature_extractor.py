"""Extract URL-only features using the phishing dataset's original encodings."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

import pandas as pd


URL_FEATURE_COLUMNS = [
    "having_IP_Address",
    "URL_Length",
    "Shortining_Service",
    "having_At_Symbol",
    "double_slash_redirecting",
    "Prefix_Suffix",
    "having_Sub_Domain",
    "HTTPS_token",
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
    """Extract the URL-derived columns expected by the trained model."""
    normalized = normalize_url(value)
    parsed = urlparse(normalized)
    hostname = (parsed.hostname or "").lower()
    registered_host = _registered_host(hostname)
    path_and_query = f"{parsed.path}{parsed.params}{parsed.query}"
    hostname_without_port = parsed.netloc.rsplit("@", 1)[-1].split(":", 1)[0]
    subdomain_count = max(len(hostname.split(".")) - 2, 0)

    features = {
        # Dataset convention: -1 means the suspicious condition is present.
        "having_IP_Address": -1 if _is_ip_address(hostname) else 1,
        "URL_Length": 1 if len(normalized) < 54 else (0 if len(normalized) <= 75 else -1),
        "Shortining_Service": -1 if registered_host in _SHORTENER_HOSTS else 1,
        "having_At_Symbol": -1 if "@" in normalized else 1,
        "double_slash_redirecting": -1 if "//" in path_and_query else 1,
        "Prefix_Suffix": -1 if "-" in registered_host else 1,
        "having_Sub_Domain": 1 if subdomain_count == 0 else (0 if subdomain_count == 1 else -1),
        "HTTPS_token": -1 if "https" in hostname_without_port.replace(registered_host, "") else 1,
    }
    return pd.DataFrame([features], columns=URL_FEATURE_COLUMNS, dtype="int64")


__all__ = ["URL_FEATURE_COLUMNS", "extract_url_features", "normalize_url"]
