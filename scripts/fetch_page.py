#!/usr/bin/env python3
"""
fetch_page.py — Fetch e-commerce store HTML with desktop and mobile UAs.

Usage:
    python fetch_page.py <url> [--mobile] [--json]

Output: JSON with html, headers, status_code, redirect_chain, load_time_ms
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import time
import urllib.parse
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException

DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Mobile/15E148 Safari/604.1"
)
GOOGLEBOT_UA = "Googlebot/2.1 (+http://www.google.com/bot.html)"

TIMEOUT = 15
MAX_REDIRECTS = 5
ALLOWED_SCHEMES = {"http", "https"}

VALID_MARKETS = {"lebanon", "mena", "gcc", "eu", "us", "uk", "global"}

# Country-code TLD → market mapping. Source of truth for auto-detection.
# Keep aligned with docs/market-expectations.md.
TLD_TO_MARKET = {
    "lb": "lebanon",
    # GCC
    "ae": "gcc", "sa": "gcc", "kw": "gcc",
    "qa": "gcc", "bh": "gcc", "om": "gcc",
    # MENA (non-GCC)
    "eg": "mena", "jo": "mena", "ma": "mena",
    "tn": "mena", "dz": "mena",
    # UK
    "uk": "uk", "co.uk": "uk",
    # EU
    "de": "eu", "fr": "eu", "es": "eu", "it": "eu",
    "nl": "eu", "be": "eu",
}


def detect_market_from_tld(hostname: str) -> str | None:
    """Return a market for a recognized ccTLD, or None.

    Checks the two-segment suffix first (e.g. co.uk) before falling back to
    the final segment, so amazon.co.uk maps to uk rather than getting lost.
    """
    if not hostname:
        return None
    host = hostname.lower().rstrip(".")
    parts = host.split(".")
    if len(parts) >= 2:
        two = ".".join(parts[-2:])
        if two in TLD_TO_MARKET:
            return TLD_TO_MARKET[two]
    if parts:
        one = parts[-1]
        if one in TLD_TO_MARKET:
            return TLD_TO_MARKET[one]
    return None


def detect_market(url: str, html: str | None = None) -> str:
    """Auto-detect market from URL TLD, with HTML language as fallback.

    Returns one of VALID_MARKETS. Defaults to 'us' for .com / generic TLDs
    that render in English; falls back to 'global' if signals are absent.
    """
    parsed = urlparse(url if "://" in url else f"https://{url}")
    market = detect_market_from_tld(parsed.hostname or "")
    if market:
        return market

    # Fallback: scan HTML for explicit language hints
    if html:
        lowered = html.lower()
        # Arabic content suggests MENA/GCC — leave it to the caller to refine
        if 'lang="ar"' in lowered or 'dir="rtl"' in lowered:
            return "mena"
        # Default English on .com → us
        if 'lang="en"' in lowered:
            return "us"

    # Final fallback: .com defaults to us; anything else → global
    host = (parsed.hostname or "").lower()
    if host.endswith(".com"):
        return "us"
    return "global"


def normalize_market(value: str | None, url: str, html: str | None = None) -> str:
    """Validate an explicit market value, or auto-detect if not provided."""
    if value:
        value = value.lower().strip()
        if value not in VALID_MARKETS:
            raise ValueError(
                f"Invalid market {value!r}. Choose from: {sorted(VALID_MARKETS)}"
            )
        return value
    return detect_market(url, html)


CARRIER_GRADE_NAT = ipaddress.ip_network("100.64.0.0/10")
# Hostnames that are never publicly routable, regardless of DNS.
ALWAYS_BLOCKED_HOSTNAMES = {"localhost", "ip6-localhost", "ip6-loopback"}


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> tuple[bool, str]:
    """Return (blocked?, reason). Covers IPv4 + IPv6 unroutable ranges."""
    if ip.is_loopback:
        return True, "loopback"
    if ip.is_unspecified:
        return True, "unspecified (0.0.0.0 / ::)"
    if ip.is_link_local:
        return True, "link-local (169.254.0.0/16, fe80::/10)"
    if ip.is_private:
        # Covers RFC1918 (10/8, 172.16/12 incl. Docker 172.17, 192.168/16),
        # IPv4-mapped IPv6, IPv6 ULA (fc00::/7), site-local (fec0::/10), etc.
        return True, "private (RFC1918 / ULA)"
    if ip.is_reserved:
        return True, "reserved"
    if ip.is_multicast:
        return True, "multicast"
    if isinstance(ip, ipaddress.IPv4Address) and ip in CARRIER_GRADE_NAT:
        return True, "carrier-grade NAT (100.64.0.0/10)"
    return False, ""


def _resolve_all(hostname: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Resolve a hostname to every IPv4 + IPv6 address it currently maps to.

    Raises ValueError on DNS failure. Returns a deduplicated, sorted list.
    """
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for {hostname!r}: {exc}") from exc

    addrs: set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
    for *_unused, sockaddr in infos:
        if not sockaddr:
            continue
        ip_str = sockaddr[0]
        # Strip IPv6 zone identifier (fe80::1%eth0)
        if "%" in ip_str:
            ip_str = ip_str.split("%", 1)[0]
        try:
            addrs.add(ipaddress.ip_address(ip_str))
        except ValueError:
            continue
    return sorted(addrs, key=str)


def validate_url(url: str) -> str:
    """Validate and normalize URL. Raises ValueError on invalid input.

    SSRF defenses applied, in order:
      1. Scheme allowlist (http/https only).
      2. Hostname denylist for unrouteable names (localhost, etc.).
      3. If the hostname is an IP literal, range-check it directly.
      4. Otherwise resolve via DNS and range-check every returned address
         (both IPv4 and IPv6). Reject if ANY resolved address is private,
         loopback, link-local, reserved, multicast, unspecified, or in
         100.64.0.0/10 (carrier-grade NAT).

    Residual TOCTOU note: the actual HTTP request re-resolves the
    hostname, so a sufficiently fast DNS rebinding attack could still
    swap in a private IP between this check and `requests.get`. To
    fully eliminate that, callers would have to dial the validated IP
    directly and pass the original Host header — a future hardening.
    """
    if not url:
        raise ValueError("URL is required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Scheme {parsed.scheme!r} not allowed")
    hostname = (parsed.hostname or "").strip()
    if not hostname:
        raise ValueError("URL must include a hostname")
    if hostname.lower() in ALWAYS_BLOCKED_HOSTNAMES:
        raise ValueError(f"Hostname {hostname!r} is not allowed")

    # IP literals (with or without IPv6 brackets) — skip DNS, check directly.
    literal = hostname[1:-1] if hostname.startswith("[") and hostname.endswith("]") else hostname
    try:
        ip = ipaddress.ip_address(literal)
    except ValueError:
        ip = None

    if ip is not None:
        blocked, reason = _is_blocked_ip(ip)
        if blocked:
            raise ValueError(f"IP {ip} is in a blocked range ({reason})")
        return url

    # Hostname: resolve and range-check every result.
    addrs = _resolve_all(hostname)
    if not addrs:
        raise ValueError(f"Could not resolve {hostname!r}")
    for resolved in addrs:
        blocked, reason = _is_blocked_ip(resolved)
        if blocked:
            raise ValueError(
                f"Hostname {hostname!r} resolves to blocked IP {resolved} ({reason})"
            )
    return url


def fetch(url: str, ua: str = DESKTOP_UA, timeout: int = TIMEOUT) -> dict:
    """Fetch a URL and return structured result."""
    url = validate_url(url)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    redirect_chain = []
    start = time.monotonic()
    try:
        resp = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            max_redirects=MAX_REDIRECTS,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        for r in resp.history:
            redirect_chain.append({"url": r.url, "status": r.status_code})
        return {
            "url": url,
            "final_url": resp.url,
            "status_code": resp.status_code,
            "html": resp.text,
            "headers": dict(resp.headers),
            "redirect_chain": redirect_chain,
            "load_time_ms": elapsed_ms,
            "ua": ua,
            "error": None,
        }
    except RequestException as e:
        return {
            "url": url,
            "final_url": url,
            "status_code": None,
            "html": "",
            "headers": {},
            "redirect_chain": redirect_chain,
            "load_time_ms": None,
            "ua": ua,
            "error": str(e),
        }


def fetch_both(url: str) -> dict:
    """Fetch with both desktop and mobile UAs."""
    return {
        "desktop": fetch(url, ua=DESKTOP_UA),
        "mobile": fetch(url, ua=MOBILE_UA),
        "googlebot": fetch(url, ua=GOOGLEBOT_UA),
    }


def detect_platform(html: str) -> str:
    """Detect e-commerce platform from HTML signals."""
    if not html:
        return "unknown"
    html_lower = html.lower()
    if "shopify.theme" in html or "cdn.shopify.com" in html_lower:
        return "shopify"
    if "woocommerce" in html_lower or 'class="wc-' in html_lower:
        return "woocommerce"
    if "bigcommerce" in html_lower or "cdn11.bigcommerce.com" in html_lower:
        return "bigcommerce"
    if "__next_data__" in html_lower or "_buildmanifest" in html_lower:
        return "nextjs"
    if "window.squarespace" in html_lower:
        return "squarespace"
    if "static.wixstatic.com" in html_lower:
        return "wix"
    return "custom"


def main():
    parser = argparse.ArgumentParser(description="Fetch e-commerce page HTML")
    parser.add_argument("url", help="Store URL to fetch")
    parser.add_argument("--mobile", action="store_true", help="Use mobile UA only")
    parser.add_argument("--googlebot", action="store_true", help="Use Googlebot UA")
    parser.add_argument("--both", action="store_true", help="Fetch with desktop + mobile + googlebot")
    parser.add_argument("--platform", action="store_true", help="Detect platform only")
    parser.add_argument(
        "--market",
        default=None,
        choices=sorted(VALID_MARKETS),
        help="Target market for locale-aware checks. Auto-detects from TLD/language if omitted.",
    )
    args = parser.parse_args()

    try:
        if args.both:
            result = fetch_both(args.url)
            result["platform"] = detect_platform(result["desktop"]["html"])
            result["market"] = normalize_market(
                args.market, args.url, result["desktop"]["html"]
            )
        elif args.mobile:
            result = fetch(args.url, ua=MOBILE_UA)
            result["platform"] = detect_platform(result["html"])
            result["market"] = normalize_market(args.market, args.url, result["html"])
        elif args.googlebot:
            result = fetch(args.url, ua=GOOGLEBOT_UA)
            result["platform"] = detect_platform(result["html"])
            result["market"] = normalize_market(args.market, args.url, result["html"])
        elif args.platform:
            fetched = fetch(args.url, ua=DESKTOP_UA)
            result = {
                "platform": detect_platform(fetched["html"]),
                "market": normalize_market(args.market, args.url, fetched["html"]),
                "url": args.url,
            }
        else:
            result = fetch(args.url, ua=DESKTOP_UA)
            result["platform"] = detect_platform(result["html"])
            result["market"] = normalize_market(args.market, args.url, result["html"])

        print(json.dumps(result, ensure_ascii=False))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
