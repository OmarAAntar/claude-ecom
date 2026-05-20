---
name: ecom-audit
description: Full e-commerce store audit. Fetches store HTML, detects platform, spawns 5 specialist agents in parallel, computes a weighted ECOM Health Score (0-100), and generates a PDF action plan in under 5 minutes. Use when user says full audit, audit my store, or complete store review.
user-invokable: true
argument-hint: <url>
version: 2.0.0
category: ecommerce
---

# Full E-Commerce Store Audit

Target: **under 5 minutes** from URL to PDF.

## Step 1 — Fetch & Detect

Run `scripts/fetch_page.py <url>` to get:
- Raw HTML (desktop UA)
- Raw HTML (mobile UA: iPhone 14)
- HTTP headers
- Page load time estimate

From the homepage HTML, identify the top 2–3 product page URLs and
fetch them. Detect platform (Shopify / WooCommerce / BigCommerce /
custom — see `skills/ecom/SKILL.md`).

## Step 2 — Spawn the 5 Agents in Parallel

Use the Agent tool in a single message to spawn all 5 simultaneously.
Pass each agent the relevant HTML, the detected platform, and the
store URL.

| Agent | File | Inputs | Analyzes |
|---|---|---|---|
| Storefront | `agents/ecom-storefront.md` | Homepage HTML | H1 + value prop, hero CTA, announcement bar, nav, AI-content markers, superlatives |
| Products | `agents/ecom-products.md` | Top 2–3 product page HTMLs | Description quality, images, schema, reviews, ATC visibility, Lebanese delivery context |
| Conversion | `agents/ecom-conversion.md` | Product + cart + checkout HTML (desktop + mobile) | ATC, sticky-ATC mobile, tap targets, checkout step count, guest checkout, exit intent |
| Trust & Offers | `agents/ecom-trust-offers.md` | Homepage + product page HTML | Reviews, policies, Lebanon trust signals (COD / WhatsApp / Whish / dual currency), pricing anchoring, bundles, upsell stack |
| Performance | `agents/ecom-performance.md` | PageSpeed Insights JSON + homepage HTML | Mobile LCP / INP / CLS, render-blocking scripts, image optimization, Lebanon TTFB note |

**Competitors are opt-in.** Do not spawn `agents/ecom-competitors.md`
during the default `/ecom audit` flow. Users who want a competitive
benchmark run `/ecom competitors <url>` separately. This keeps the
audit under 5 minutes — competitor scans are the slowest leg.

## Step 3 — Compute ECOM Health Score

Collect scores from the 5 agents. Apply weights:

| Category | Agent | Weight |
|---|---|---|
| Conversion | ecom-conversion | 30% |
| Products | ecom-products | 25% |
| Trust & Offers | ecom-trust-offers | 18% |
| Storefront | ecom-storefront | 15% |
| Performance (CWV) | ecom-performance | 12% |

Sum = 100. Overall = sum of (score × weight).

## Step 4 — Identify Critical Issues

Critical issues are anything that:
- Blocks purchasing (broken cart, no payment icons, no mobile CTA)
- Destroys trust (no COD, no WhatsApp, no reviews, no return policy visible)
- Loses visitors before they see a product (hero has no value prop, LCP > 5s mobile)
- Costs >5% conversion on its own

Flag these in a red "Fix Before Anything Else" box in the report.

## Step 5 — Generate Reports

Write `ECOM-AUDIT-REPORT.md` and `ACTION-PLAN.md` to the current
directory.

Then delegate to the `ecom-report` agent (`agents/ecom-report.md`)
which will:
1. Run `scripts/extract_brand.py <url> --download-logo` for brand
   color and logo.
2. Run `scripts/ecom_report.py` with the full scores JSON and brand
   signals to generate `ecom-report.pdf`.

## Report Structure

### Cover Page
- Store name + URL
- Platform + date
- Overall ECOM Health Score (large, colored)
- 5 category scores

### Existential Issues Box
Any Critical issues that block all other progress.

### Executive Summary
- Top 5 critical issues
- Top 5 quick wins (under 1 hour each)

### Section 1: Storefront
### Section 2: Products
### Section 3: Conversion
### Section 4: Trust & Offers
### Section 5: Performance

Each section: pass/fail table → critical findings → ready-to-use fixes → code snippets.

### 30-Day Sprint Plan
Week-by-week checklist with effort and impact labels.

## Error Handling

| Scenario | Response |
|---|---|
| URL returns 4xx/5xx | Report error, ask user to verify URL |
| Geo-blocked (returns error page to crawler) | Flag as CRITICAL |
| JS-only rendering (empty HTML body) | Note CSR limitation; analyze what IS accessible |
| No products found | Report thin catalog; flag as HIGH issue |
| Timeout | Analyze partial content; note limitations in report |
