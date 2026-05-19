---
name: ecom-performance
description: E-commerce performance audit. Checks Core Web Vitals (LCP, INP, CLS), page speed, image optimization, app bloat, and CDN usage. Uses PageSpeed Insights API for live data. Use when user says slow site, page speed, Core Web Vitals, or performance.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Performance Audit

User-invokable: `/ecom performance <url>`

## When to Use

Run when the user asks about page speed, Core Web Vitals, LCP/INP/CLS, app bloat, or slow site.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch HTML via `scripts/fetch_page.py`
3. Run `scripts/pagespeed.py <url>` to get live CrUX + Lighthouse data
4. Detect platform (see `skills/ecom/SKILL.md` routing table)
5. Spawn `agents/ecom-performance.md` with the HTML, PageSpeed JSON, platform, and URL
6. Format the agent's JSON output using the user-facing template below

## Data Sources

1. **PageSpeed Insights API** (primary): `scripts/pagespeed.py <url>` — returns CrUX field data if available, else Lighthouse lab data
2. **HTML analysis** (secondary): scripts, images, third-party domains
3. **Platform baseline** (fallback): known ranges per platform

## Scoring Rubric & Check Criteria

See `agents/ecom-performance.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
PERFORMANCE SCORE: XX/100

CORE WEB VITALS:
LCP: Xs — [GOOD/NEEDS WORK/POOR] — root cause
INP: Xms — [GOOD/NEEDS WORK/POOR] — root cause
CLS: X.XX — [GOOD/NEEDS WORK/POOR] — root cause
FCP: Xs — status
TTFB: Xms — status

TOP FIXES (ordered by LCP improvement):
1. [fix] — estimated −Xs LCP — [LOW/MEDIUM/HIGH effort]
2. [fix] — estimated −Xs LCP
3. [fix] — estimated −Xms INP

READY-TO-USE CODE:
[preload link tag, WebP snippet, CSS CLS fix, etc.]
```
