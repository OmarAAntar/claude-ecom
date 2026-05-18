#!/usr/bin/env python3
"""
competitor_scan.py — Find and analyze e-commerce competitors via web search.

Usage:
    python competitor_scan.py --product "car phone mount" --market "Lebanon" [--count 3]

Output: JSON with competitor URLs and basic extracted data.
"""

import argparse
import json
import re
import sys

import requests
from bs4 import BeautifulSoup

from fetch_page import fetch, validate_url

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def search_competitors(product: str, market: str, count: int = 5) -> list[str]:
    """
    Use DuckDuckGo HTML search to find competitor store URLs.
    Returns a list of URLs (no API key required).
    """
    queries = [
        f"{product} {market} buy online",
        f"best {product} store {market}",
        f"{product} {market} cash on delivery",
    ]
    found = []
    seen_domains = set()

    for query in queries:
        if len(found) >= count:
            break
        try:
            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers=HEADERS,
                timeout=10,
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.select("a.result__url"):
                href = link.get("href", "")
                if href.startswith("http"):
                    domain = re.sub(r"https?://(?:www\.)?", "", href).split("/")[0]
                    if domain not in seen_domains and not _is_marketplace(domain):
                        seen_domains.add(domain)
                        found.append(href.split("?")[0])
                        if len(found) >= count:
                            break
        except Exception:
            continue

    return found[:count]


def _is_marketplace(domain: str) -> bool:
    """Filter out large marketplaces — we want direct stores only."""
    marketplaces = [
        "amazon", "ebay", "noon", "aliexpress", "etsy", "walmart",
        "target", "bestbuy", "carrefour", "jumia", "souq",
    ]
    return any(m in domain.lower() for m in marketplaces)


def extract_competitor_data(url: str) -> dict:
    """Fetch a competitor homepage and extract key signals."""
    result = fetch(url)
    if result["error"] or not result["html"]:
        return {"url": url, "error": result["error"] or "No HTML returned"}

    soup = BeautifulSoup(result["html"], "html.parser")
    data = {
        "url": url,
        "title": _get_text(soup, "title"),
        "h1": _get_text(soup, "h1"),
        "announcement_bar": _find_announcement_bar(soup),
        "whatsapp": _has_whatsapp(result["html"]),
        "reviews_visible": _has_reviews(result["html"]),
        "cod_mentioned": _has_cod(result["html"]),
        "free_shipping": _has_free_shipping(result["html"]),
        "payment_icons": _count_payment_icons(soup),
        "social_links": _find_social_links(soup),
        "catalog_size_estimate": _estimate_catalog_size(soup),
        "has_blog": _has_blog(soup),
        "trustpilot": "trustpilot" in result["html"].lower(),
        "platform": result.get("platform", "unknown"),
        "load_time_ms": result.get("load_time_ms"),
    }
    return data


def _get_text(soup: BeautifulSoup, selector: str) -> str:
    el = soup.find(selector)
    return el.get_text(strip=True)[:150] if el else ""


def _find_announcement_bar(soup: BeautifulSoup) -> str:
    for sel in [".announcement-bar", ".announcement", "[data-section-type='announcement-bar']", ".header-top"]:
        el = soup.select_one(sel)
        if el:
            return el.get_text(strip=True)[:100]
    return ""


def _has_whatsapp(html: str) -> bool:
    return "whatsapp" in html.lower() or "wa.me" in html.lower()


def _has_reviews(html: str) -> bool:
    return any(x in html.lower() for x in ["judge.me", "stamped", "yotpo", "trustpilot", "review", "star-rating"])


def _has_cod(html: str) -> bool:
    return any(x in html.lower() for x in ["cash on delivery", "cod", "pay on delivery", "الدفع عند الاستلام"])


def _has_free_shipping(html: str) -> bool:
    return "free shipping" in html.lower() or "free delivery" in html.lower()


def _count_payment_icons(soup: BeautifulSoup) -> int:
    icons = soup.select("img[src*='visa'], img[src*='mastercard'], img[src*='paypal'], "
                        "img[alt*='visa'], img[alt*='mastercard'], img[alt*='paypal']")
    return len(icons)


def _find_social_links(soup: BeautifulSoup) -> list[str]:
    platforms = ["instagram", "facebook", "tiktok", "youtube", "twitter", "x.com"]
    found = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        for p in platforms:
            if p in href and p not in found:
                found.append(p)
    return found


def _estimate_catalog_size(soup: BeautifulSoup) -> str:
    product_links = soup.select("a[href*='/products/']")
    count = len(set(a["href"] for a in product_links))
    if count == 0:
        return "unknown"
    if count <= 5:
        return f"small (~{count} visible)"
    return f"medium+ ({count}+ visible)"


def _has_blog(soup: BeautifulSoup) -> bool:
    for a in soup.find_all("a", href=True):
        if "/blog" in a["href"].lower() or "/news" in a["href"].lower():
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Find and analyze e-commerce competitors")
    parser.add_argument("--product", required=True, help="Product category or name")
    parser.add_argument("--market", required=True, help="Target market (e.g. Lebanon, US)")
    parser.add_argument("--count", type=int, default=3, help="Number of competitors (default: 3)")
    parser.add_argument("--urls", nargs="+", help="Provide competitor URLs directly (skip search)")
    args = parser.parse_args()

    if args.urls:
        competitor_urls = args.urls
    else:
        competitor_urls = search_competitors(args.product, args.market, args.count)

    competitors = []
    for url in competitor_urls:
        try:
            data = extract_competitor_data(url)
            competitors.append(data)
        except Exception as e:
            competitors.append({"url": url, "error": str(e)})

    print(json.dumps({"competitors": competitors, "count": len(competitors)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
