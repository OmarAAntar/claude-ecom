---
name: ecom-audit
description: Full e-commerce store audit with parallel sub-agent delegation. Fetches store HTML, detects platform, spawns 13 specialist agents, computes weighted ECOM Health Score (0-100), generates PDF report. Use when user says full audit, audit my store, or complete store review.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Full E-Commerce Store Audit

## Step 1 — Fetch & Detect

Run `scripts/fetch_page.py <url>` to get:
- Raw HTML (desktop UA)
- Raw HTML (mobile UA: iPhone 14)
- HTTP headers
- Redirect chain
- Page load time estimate

Detect platform from HTML (see ecom/SKILL.md routing table).

Detect business type:
- **Dropship** — generic descriptions, AliExpress image patterns, no brand story
- **DTC Brand** — original branding, founder story, branded packaging mentions
- **Marketplace** — multiple sellers, varying branding
- **Service + Products** — hybrid (e.g., a salon selling products)

## Step 2 — Spawn All Agents in Parallel

Use the Agent tool to spawn all 13 agents simultaneously. Pass each agent:
- The fetched HTML
- The detected platform
- The store URL

| Agent | File | Analyzes |
|---|---|---|
| Header | `agents/ecom-header.md` | Logo, nav, announcement bar, cart, search |
| Hero | `agents/ecom-hero.md` | Value prop, H1, CTA, above-fold content |
| Products | `agents/ecom-products.md` | Descriptions, images, specs, variants |
| Cart | `agents/ecom-cart.md` | Cart page UX, upsells, friction |
| CRO | `agents/ecom-cro.md` | Checkout flow, form friction, CTAs |
| Offers | `agents/ecom-offers.md` | Pricing, bundles, promotions, anchoring |
| Upsells | `agents/ecom-upsells.md` | Post-purchase, cross-sells, BOGO |
| Trust | `agents/ecom-trust.md` | Reviews, badges, guarantees, policies |
| Mobile | `agents/ecom-mobile.md` | 390px viewport, tap targets, mobile CRO |
| Performance | `agents/ecom-performance.md` | CWV, LCP, INP, CLS, app bloat |
| Copy | `agents/ecom-copy.md` | Headlines, descriptions, CTAs, tone |
| Competitors | `agents/ecom-competitors.md` | 3 competitors, price/offer/trust gaps |
| Retention | `agents/ecom-retention.md` | Popups, email capture, post-purchase flows |

## Step 3 — Compute ECOM Health Score

Collect scores from all agents. Apply weights:

| Category | Agents | Weight |
|---|---|---|
| First Impression | Header + Hero | 12% |
| Product Presentation | Products | 18% |
| Conversion Rate Optimization | CRO + Cart | 18% |
| Offer & Pricing Strategy | Offers + Upsells | 15% |
| Trust & Social Proof | Trust | 12% |
| Mobile Experience | Mobile | 10% |
| Copy & Messaging | Copy | 8% |
| Retention & Email | Retention | 4% |
| Performance (CWV) | Performance | 3% |

Overall = sum of (score × weight).

## Step 4 — Identify Critical Issues

Critical issues are anything that:
- Blocks purchasing (broken cart, no payment icons, no mobile CTA)
- Destroys trust (no reviews, no return policy visible, no contact method)
- Loses visitors before they see a product (hero has no value prop, LCP > 5s mobile)
- Costs >5% conversion on its own

Flag these in a red "Fix Before Anything Else" box in the report.

## Step 5 — Generate Reports

Write `ECOM-AUDIT-REPORT.md` and `ACTION-PLAN.md` to the current directory.

Then run:
```
scripts/ecom_report.py \
  --report ECOM-AUDIT-REPORT.md \
  --action-plan ACTION-PLAN.md \
  --url <url> \
  --platform <platform> \
  --score <overall_score> \
  --output ecom-report.pdf
```

## Report Structure

### Cover Page
- Store name + URL
- Platform + date
- Overall ECOM Health Score (large, colored)
- Score per category (dashboard)

### Existential Issues Box
Any Critical issues that block all other progress.

### Executive Summary
- Business type detected
- Top 5 critical issues
- Top 5 quick wins (under 1 hour each)

### Section 1: First Impression (Header + Hero)
### Section 2: Product Presentation
### Section 3: Conversion Rate Optimization
### Section 4: Offer & Pricing Strategy
### Section 5: Trust & Social Proof
### Section 6: Mobile Experience
### Section 7: Copy & Messaging
### Section 8: Retention & Email
### Section 9: Performance
### Section 10: Competitor Positioning

Each section: pass/fail table → critical findings → ready-to-use fixes → code snippets.

### 30-Day Sprint Plan
Week-by-week checklist with effort and impact labels.

### Expected Score Trajectory
Table: current score → after each week of fixes.

## Error Handling

| Scenario | Response |
|---|---|
| URL returns 4xx/5xx | Report error, ask user to verify URL |
| Geo-blocked (returns error page to crawler) | Flag as CRITICAL — same as google-bot blocking |
| JS-only rendering (empty HTML body) | Note CSR limitation; analyze what IS accessible; flag AI/crawler impact |
| No products found | Report thin catalog; flag as HIGH issue |
| Timeout | Analyze partial content; note limitations in report |
