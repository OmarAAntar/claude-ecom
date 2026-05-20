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

5 agents execute. Each returns one or more sub-scores. Together they
produce the 9 sub-scores that feed the final ECOM Health Score.

| Agent | Sub-scores emitted | Inputs | Analyzes |
|---|---|---|---|
| Storefront | `first_impression`, `copy` | Homepage HTML | Hero composition + nav + in-fold trust (first_impression); H1, subheadline, CTA copy, AI markers, superlatives (copy) |
| Products | `products` | Top 2–3 product page HTMLs | Description quality, images, schema, reviews, ATC visibility, Lebanese delivery context |
| Conversion | `cro`, `mobile` | Product + cart + checkout HTML (desktop + mobile) | ATC, checkout, cart UX, purchase barriers (cro); sticky ATC, tap targets, no horizontal scroll, ≥16px font (mobile) |
| Trust & Offers | `trust`, `offers`, `retention` | Homepage + product page HTML | Reviews + policies + Lebanon signals (trust); pricing + bundles + pre-purchase upsells (offers); post-purchase 1-click upsell (retention) |
| Performance | `performance` | PageSpeed Insights JSON + homepage HTML | Mobile LCP / INP / CLS, render-blocking scripts, image optimization, Lebanon TTFB note |

**Competitors are opt-in.** Do not spawn `agents/ecom-competitors.md`
during the default `/ecom audit` flow. Users who want a competitive
benchmark run `/ecom competitors <url>` separately. This keeps the
audit under 5 minutes — competitor scans are the slowest leg.

## Step 3 — Compute ECOM Health Score

Collect the 9 sub-scores from the 5 agents. Apply weights:

| Category | Sub-score | Source agent | Weight |
|---|---|---|---|
| Product Presentation | `products` | ecom-products | 18% |
| Conversion Rate Optimization | `cro` | ecom-conversion | 18% |
| Offer & Pricing Strategy | `offers` | ecom-trust-offers | 13% |
| Trust & Social Proof | `trust` | ecom-trust-offers | 12% |
| Mobile Experience | `mobile` | ecom-conversion | 10% |
| Performance (CWV) | `performance` | ecom-performance | 10% |
| First Impression | `first_impression` | ecom-storefront | 8% |
| Copy & Messaging | `copy` | ecom-storefront | 6% |
| Retention & Email | `retention` | ecom-trust-offers | 5% |

Sum = 100. Overall = sum of (sub_score × weight).
Verify: 18 + 18 + 13 + 12 + 10 + 10 + 8 + 6 + 5 = 100.

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
- 9 category scores in the dashboard

### Existential Issues Box
Any Critical issues that block all other progress.

### Executive Summary
- Top 5 critical issues
- Top 5 quick wins (under 1 hour each)

### Section 1: First Impression
### Section 2: Copy & Messaging
### Section 3: Product Presentation
### Section 4: Conversion Rate Optimization
### Section 5: Mobile Experience
### Section 6: Trust & Social Proof
### Section 7: Offer & Pricing Strategy
### Section 8: Retention & Email
### Section 9: Performance (CWV)

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
