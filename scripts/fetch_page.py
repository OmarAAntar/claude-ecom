#!/usr/bin/env python3
"""
fetch_page.py — Fetch e-commerce store HTML with desktop and mobile UAs.

Usage:
    python fetch_page.py <url> [--mobile] [--json]

Output: JSON with html, headers, status_code, redirect_chain, load_time_ms
"""

import argparse
import json
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


def validate_url(url: str) -> str:
    """Validate and normalize URL. Raises ValueError on invalid input (SSRF protection)."""
    if not url:
        raise ValueError("URL is required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Scheme {parsed.scheme!r} not allowed")
    hostname = parsed.hostname or ""
    # Block private/internal addresses
    blocked = ["localhost", "127.", "10.", "192.168.", "172.16.", "169.254.", "::1", "0.0.0.0"]
    for b in blocked:
        if hostname.startswith(b) or hostname == b.rstrip("."):
            raise ValueError(f"Private/internal addresses not allowed: {hostname}")
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
    args = parser.parse_args()

    try:
        if args.both:
            result = fetch_both(args.url)
            result["platform"] = detect_platform(result["desktop"]["html"])
        elif args.mobile:
            result = fetch(args.url, ua=MOBILE_UA)
            result["platform"] = detect_platform(result["html"])
        elif args.googlebot:
            result = fetch(args.url, ua=GOOGLEBOT_UA)
            result["platform"] = detect_platform(result["html"])
        elif args.platform:
            result = fetch(args.url, ua=DESKTOP_UA)
            result = {"platform": detect_platform(result["html"]), "url": args.url}
        else:
            result = fetch(args.url, ua=DESKTOP_UA)
            result["platform"] = detect_platform(result["html"])

        print(json.dumps(result, ensure_ascii=False))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
