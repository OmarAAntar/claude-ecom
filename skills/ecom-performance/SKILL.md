---
name: ecom-performance
description: E-commerce performance audit. Checks Core Web Vitals (LCP, INP, CLS), page speed, image optimization, app bloat, and CDN usage. Uses PageSpeed Insights API for live data. Use when user says slow site, page speed, Core Web Vitals, or performance.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Performance Audit

## Data Sources

1. **PageSpeed Insights API** (primary): `scripts/pagespeed.py <url>`
   - Returns real CrUX field data if available
   - Falls back to Lighthouse lab data
2. **HTML analysis** (secondary): count scripts, images, third-party domains
3. **Platform baseline** (fallback): known performance ranges per platform

## Core Web Vitals Thresholds (2025)

| Metric | Good | Needs Work | Poor |
|---|---|---|---|
| LCP | ≤ 2.5s | 2.5–4.0s | > 4.0s |
| INP | ≤ 200ms | 200–500ms | > 500ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| FCP | ≤ 1.8s | 1.8–3.0s | > 3.0s |
| TTFB | ≤ 800ms | 800–1800ms | > 1800ms |

Note: Use INP only. Never reference FID (deprecated March 2024).

## Scoring (100 pts)

| Check | Points |
|---|---|
| Mobile LCP ≤ 2.5s | 15 |
| Mobile INP ≤ 200ms | 12 |
| Mobile CLS ≤ 0.1 | 10 |
| Mobile FCP ≤ 1.8s | 8 |
| TTFB ≤ 800ms | 8 |
| Hero/LCP image preloaded | 7 |
| WebP/AVIF images served | 7 |
| No render-blocking scripts before LCP | 8 |
| Third-party scripts deferred | 6 |
| Shopify app count ≤ 10 (if Shopify) | 5 |
| Explicit width/height on all images | 5 |
| Font-display: swap on web fonts | 4 |
| CDN serving assets (not origin) | 5 |

## Platform-Specific Root Causes

### Shopify
- LCP: Hero image not preloaded; Canva/Figma PNG not compressed
- INP: Marquee announcement bar JS loop; Shop Pay event listeners
- CLS: Announcement bar height not reserved; Poppins font swap
- TTFB: Shopify CDN PoP may be far from target market

### WooCommerce
- Multiple plugin CSS/JS files not combined
- WordPress admin bar loaded for logged-in users (disable for frontend)
- No object cache (Redis/Memcached)

### Custom/Next.js
- CSR content not server-rendered — check for SSR/SSG
- Large JS bundle; check for tree-shaking

## Geographic Performance Note

If market is Lebanon, MENA, Southeast Asia, or Africa:
- Note that major CDN PoPs may be 200–600ms away
- Recommend Cloudflare as reverse proxy (has Beirut, Dubai, Singapore PoPs)
- Estimate TTFB improvement from Cloudflare: −300–500ms

## Output Format

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
