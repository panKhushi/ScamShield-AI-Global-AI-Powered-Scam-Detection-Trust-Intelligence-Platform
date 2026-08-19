import socket
import ipaddress
from urllib.parse import urlparse

# Cloud metadata endpoints — a classic SSRF target, must always be blocked
BLOCKED_HOSTS = {"169.254.169.254", "metadata.google.internal"}


def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Checks whether a URL is safe to fetch — blocks private/internal IP ranges
    and known cloud metadata endpoints to prevent SSRF attacks.
    Returns (is_safe, reason_if_blocked).
    """
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")

    if parsed.scheme not in ("http", "https"):
        return False, f"Blocked non-HTTP(S) scheme: {parsed.scheme}"

    hostname = parsed.hostname
    if not hostname:
        return False, "Could not determine hostname"

    if hostname.lower() in BLOCKED_HOSTS:
        return False, "Blocked: known cloud metadata endpoint"

    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False, "Could not resolve hostname"

    for family, _, _, _, sockaddr in resolved_ips:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
        ):
            return False, f"Blocked: resolves to a private/internal IP ({ip_str})"

    return True, ""