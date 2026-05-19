#!/usr/bin/env python3
"""
extract_brand.py — Extract brand colors, logo, and store name from an e-commerce website.

Usage:
    python extract_brand.py <url>
    python extract_brand.py <url> --download-logo

Output JSON:
    {
        "store_name": "My Store",
        "description": "Tagline here",
        "primary_color": "#e63329",
        "logo_url": "https://...",
        "logo_b64": "<base64>"   # only with --download-logo
    }

Dependencies: requests
"""

import argparse
import base64
import json
import re
import sys
from urllib.parse import urljoin, urlparse

import requests

DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 15
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
    blocked = ["localhost", "127.", "10.", "192.168.", "172.16.", "169.254.", "::1", "0.0.0.0"]
    for b in blocked:
        if hostname.startswith(b) or hostname == b.rstrip("."):
            raise ValueError(f"Private/internal addresses not allowed: {hostname}")
    return url


def fetch_html(url: str) -> tuple[str, str]:
    """Fetch page HTML. Returns (html, final_url)."""
    resp = requests.get(
        url,
        headers={
            "User-Agent": DESKTOP_UA,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    return resp.text, resp.url


def _meta(html: str, name: str = None, prop: str = None) -> str | None:
    """Extract a meta tag content by name or property."""
    if name:
        patterns = [
            rf'<meta[^>]+name=["\'](?i:{re.escape(name)})["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\'](?i:{re.escape(name)})["\']',
        ]
    elif prop:
        patterns = [
            rf'<meta[^>]+property=["\'](?i:{re.escape(prop)})["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\'](?i:{re.escape(prop)})["\']',
        ]
    else:
        return None
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_store_name(html: str) -> str | None:
    """Extract store/brand name from title tag or og:site_name."""
    # og:site_name is most reliable
    name = _meta(html, prop="og:site_name")
    if name:
        return name.strip()

    # title tag with common suffix stripping
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if m:
        title = m.group(1).strip()
        for sep in [' | ', ' – ', ' — ', ' - ', ' :: ', ' · ']:
            if sep in title:
                title = title.split(sep)[0].strip()
        if title:
            return title
    return None


def extract_description(html: str) -> str | None:
    """Extract store description from meta description or og:description."""
    desc = _meta(html, prop="og:description") or _meta(html, name="description")
    if desc:
        # Truncate to a reasonable length
        desc = desc.strip()
        if len(desc) > 120:
            desc = desc[:117] + "..."
        return desc
    return None


def extract_primary_color(html: str) -> str | None:
    """
    Extract primary brand color using multiple strategies:
    1. meta theme-color
    2. CSS custom properties (--primary, --brand-color, etc.)
    3. Shopify/common framework color variables
    """
    # 1. meta theme-color
    color = _meta(html, name="theme-color")
    if color and re.match(r'^#[0-9a-fA-F]{3,8}$', color):
        return color

    # 2. CSS custom properties in <style> blocks
    css_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.IGNORECASE | re.DOTALL)
    priority_vars = [
        '--color-primary', '--primary-color', '--primary', '--brand-color',
        '--accent-color', '--accent', '--main-color', '--color-accent',
        '--color-button', '--button-color', '--link-color',
    ]
    for css in css_blocks[:5]:
        for var in priority_vars:
            m = re.search(rf'{re.escape(var)}\s*:\s*(#[0-9a-fA-F]{{3,8}})', css)
            if m:
                c = m.group(1)
                # Skip very dark or very light colors (near black/white)
                if not re.match(r'^#(?:[0-1][0-9a-fA-F]{5}|[fF][eEfF][eEfF][eEfF][eEfF][eEfF])$', c):
                    return c

    # 3. Inline style on <header> or <nav> background-color
    m = re.search(
        r'<(?:header|nav)[^>]+style=["\'][^"\']*background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8})',
        html, re.IGNORECASE
    )
    if m:
        c = m.group(1)
        if not re.match(r'^#(?:fff|ffffff|000|000000)$', c, re.IGNORECASE):
            return c

    return None


def extract_logo_url(html: str, base_url: str) -> str | None:
    """
    Extract logo URL using multiple strategies:
    1. <img> with logo in class/id/alt
    2. apple-touch-icon (good quality, usually the brand icon)
    3. og:image (sometimes the logo, often hero image — lower priority)
    4. favicon as last resort
    """
    # 1. <img> tags with logo-related attributes
    logo_img_patterns = [
        r'<img[^>]+class=["\'][^"\']*\b(?:logo|brand|site-logo|header-logo)[^"\']*["\'][^>]+src=["\']([^"\'?#\s]+)',
        r'<img[^>]+src=["\']([^"\'?#\s]+)["\'][^>]+class=["\'][^"\']*\b(?:logo|brand|site-logo|header-logo)[^"\']*["\']',
        r'<img[^>]+id=["\'][^"\']*\b(?:logo|brand)[^"\']*["\'][^>]+src=["\']([^"\'?#\s]+)',
        r'<img[^>]+src=["\']([^"\'?#\s]+)["\'][^>]+id=["\'][^"\']*\b(?:logo|brand)[^"\']*["\']',
        r'<img[^>]+alt=["\'][^"\']*\b(?:logo|brand)[^"\']*["\'][^>]+src=["\']([^"\'?#\s]+)',
        r'<img[^>]+src=["\']([^"\'?#\s]+)["\'][^>]+alt=["\'][^"\']*\b(?:logo|brand)[^"\']*["\']',
    ]
    for pat in logo_img_patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            src = m.group(1)
            if src and not src.startswith('data:'):
                return urljoin(base_url, src)

    # 2. apple-touch-icon (clean, usually brand icon)
    for pat in [
        r'<link[^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
        r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\']',
    ]:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return urljoin(base_url, m.group(1))

    # 3. og:image — only use if it looks like a logo (has "logo" in path)
    og_image = _meta(html, prop="og:image")
    if og_image and 'logo' in og_image.lower():
        return og_image

    # 4. Favicon (last resort, may be low quality)
    for pat in [
        r'<link[^>]+rel=["\'][^"\']*\bicon\b[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
        r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*\bicon\b[^"\']*["\']',
    ]:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            href = m.group(1)
            # Skip .ico files — they don't embed well in PDFs
            if not href.lower().endswith('.ico'):
                return urljoin(base_url, href)

    return None


def download_logo(logo_url: str) -> str | None:
    """Download logo and return base64-encoded bytes, or None if failed."""
    try:
        resp = requests.get(
            logo_url,
            headers={"User-Agent": DESKTOP_UA},
            timeout=10,
            allow_redirects=True,
        )
        content_type = resp.headers.get("content-type", "")
        if resp.status_code == 200 and "image" in content_type:
            return base64.b64encode(resp.content).decode()
    except Exception as e:
        print(f"Warning: logo download failed: {e}", file=sys.stderr)
    return None


def extract_brand(url: str, download_logo_flag: bool = False) -> dict:
    """Fetch website and extract all brand signals."""
    url = validate_url(url)
    html, final_url = fetch_html(url)

    result: dict = {
        "store_name": extract_store_name(html),
        "description": extract_description(html),
        "primary_color": extract_primary_color(html),
        "logo_url": extract_logo_url(html, final_url),
    }

    if download_logo_flag and result["logo_url"]:
        b64 = download_logo(result["logo_url"])
        if b64:
            result["logo_b64"] = b64

    return result


def main():
    parser = argparse.ArgumentParser(description="Extract brand info from an e-commerce website")
    parser.add_argument("url", help="Store URL")
    parser.add_argument(
        "--download-logo", action="store_true",
        help="Download the logo and include as base64 in output"
    )
    args = parser.parse_args()

    try:
        brand = extract_brand(args.url, download_logo_flag=args.download_logo)
        print(json.dumps(brand, ensure_ascii=False))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
