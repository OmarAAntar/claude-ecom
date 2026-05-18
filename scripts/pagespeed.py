#!/usr/bin/env python3
"""
pagespeed.py — PageSpeed Insights API wrapper for e-commerce audits.

Usage:
    python pagespeed.py <url> [--api-key KEY] [--strategy mobile|desktop]

Output: JSON with Core Web Vitals, performance score, and top opportunities.
Falls back to lab data if CrUX field data is unavailable.
"""

import argparse
import json
import os
import sys

import requests


PSI_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def run_pagespeed(url: str, api_key: str = None, strategy: str = "mobile") -> dict:
    """Run PageSpeed Insights and return structured CWV data."""
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "accessibility", "best-practices"],
    }
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(PSI_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": str(e), "url": url, "strategy": strategy}

    result = {
        "url": url,
        "strategy": strategy,
        "error": None,
        "performance_score": None,
        "field_data_available": False,
        "lcp": None,
        "inp": None,
        "cls": None,
        "fcp": None,
        "ttfb": None,
        "opportunities": [],
    }

    # Performance score
    cats = data.get("lighthouseResult", {}).get("categories", {})
    perf = cats.get("performance", {})
    result["performance_score"] = round((perf.get("score") or 0) * 100)

    # CrUX field data (real user data — preferred)
    field = data.get("loadingExperience", {}).get("metrics", {})
    if field:
        result["field_data_available"] = True
        lcp = field.get("LARGEST_CONTENTFUL_PAINT_MS", {})
        if lcp:
            result["lcp"] = {
                "value_ms": lcp.get("percentile"),
                "category": lcp.get("category"),
            }
        inp = field.get("INTERACTION_TO_NEXT_PAINT", {})
        if inp:
            result["inp"] = {
                "value_ms": inp.get("percentile"),
                "category": inp.get("category"),
            }
        cls = field.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {})
        if cls:
            result["cls"] = {
                "value": cls.get("percentile", 0) / 100,
                "category": cls.get("category"),
            }
        fcp = field.get("FIRST_CONTENTFUL_PAINT_MS", {})
        if fcp:
            result["fcp"] = {
                "value_ms": fcp.get("percentile"),
                "category": fcp.get("category"),
            }

    # Lab data fallback (Lighthouse)
    audits = data.get("lighthouseResult", {}).get("audits", {})

    if not result["field_data_available"]:
        lcp_audit = audits.get("largest-contentful-paint", {})
        result["lcp"] = {
            "value_ms": int((lcp_audit.get("numericValue") or 0)),
            "category": _classify_lcp(lcp_audit.get("numericValue") or 0),
            "source": "lab",
        }
        cls_audit = audits.get("cumulative-layout-shift", {})
        result["cls"] = {
            "value": round(cls_audit.get("numericValue") or 0, 3),
            "category": _classify_cls(cls_audit.get("numericValue") or 0),
            "source": "lab",
        }
        fcp_audit = audits.get("first-contentful-paint", {})
        result["fcp"] = {
            "value_ms": int(fcp_audit.get("numericValue") or 0),
            "category": _classify_fcp(fcp_audit.get("numericValue") or 0),
            "source": "lab",
        }
        ttfb_audit = audits.get("server-response-time", {})
        result["ttfb"] = {
            "value_ms": int(ttfb_audit.get("numericValue") or 0),
            "category": _classify_ttfb(ttfb_audit.get("numericValue") or 0),
            "source": "lab",
        }

    # Top opportunities (sorted by potential savings)
    opps = []
    for key, audit in audits.items():
        savings = audit.get("details", {}).get("overallSavingsMs") or 0
        if savings > 300 and audit.get("score") is not None and audit.get("score") < 0.9:
            opps.append({
                "id": key,
                "title": audit.get("title", ""),
                "savings_ms": int(savings),
                "description": audit.get("description", "")[:200],
            })
    result["opportunities"] = sorted(opps, key=lambda x: x["savings_ms"], reverse=True)[:8]

    return result


def _classify_lcp(ms: float) -> str:
    if ms <= 2500:
        return "GOOD"
    if ms <= 4000:
        return "NEEDS_IMPROVEMENT"
    return "POOR"


def _classify_cls(val: float) -> str:
    if val <= 0.1:
        return "GOOD"
    if val <= 0.25:
        return "NEEDS_IMPROVEMENT"
    return "POOR"


def _classify_fcp(ms: float) -> str:
    if ms <= 1800:
        return "GOOD"
    if ms <= 3000:
        return "NEEDS_IMPROVEMENT"
    return "POOR"


def _classify_ttfb(ms: float) -> str:
    if ms <= 800:
        return "GOOD"
    if ms <= 1800:
        return "NEEDS_IMPROVEMENT"
    return "POOR"


def main():
    parser = argparse.ArgumentParser(description="Run PageSpeed Insights for e-commerce audit")
    parser.add_argument("url", help="URL to test")
    parser.add_argument("--api-key", default=os.environ.get("PSI_API_KEY"), help="PSI API key")
    parser.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile")
    parser.add_argument("--both", action="store_true", help="Run mobile + desktop")
    args = parser.parse_args()

    if args.both:
        mobile = run_pagespeed(args.url, args.api_key, "mobile")
        desktop = run_pagespeed(args.url, args.api_key, "desktop")
        print(json.dumps({"mobile": mobile, "desktop": desktop}, ensure_ascii=False))
    else:
        result = run_pagespeed(args.url, args.api_key, args.strategy)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
