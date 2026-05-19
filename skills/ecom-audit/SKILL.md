---
name: ecom-audit
description: Run the complete e-commerce store audit — fetches the store, detects platform and market, spawns 14 specialist agents in parallel, computes a weighted ECOM Health Score plus a separate Discoverability Score, and generates a PDF action plan with a 30-day sprint. Use when the user wants a thorough end-to-end review, a one-shot conversion + trust + mobile + performance + SEO check, or a PDF deliverable to share with their team. Natural trigger phrases include: full audit, audit my store, complete store review, run the full audit, deep audit, give me the whole report, comprehensive ecommerce review, score my store, run the audit suite.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Full E-Commerce Store Audit

## Step 1 — Fetch all inputs once at the orchestrator level

The orchestrator does **all network fetches up front**, then passes
the bytes to every agent. Agents do **not** re-fetch the store. This
avoids hammering the target site (which can trigger rate limits or
WAFs) and avoids the implicit serialization that 14 agents each
making their own HTTP calls would create.

Fetches to make once (in parallel with one another where independent):

| What | UA / source | Used by |
|---|---|---|
| Homepage HTML (desktop) | `scripts/fetch_page.py <url>` | header, hero, copy, products discovery, seo |
| Homepage HTML (mobile, iPhone 14) | `scripts/fetch_page.py <url> --mobile` | mobile agent |
| Top 2–3 product page HTML (desktop) | `scripts/fetch_page.py` per URL | products, cro, offers, trust, upsells, seo, cart |
| `/robots.txt` | direct GET | seo |
| `/sitemap.xml` | direct GET | seo |
| PageSpeed Insights JSON (mobile) | `scripts/pagespeed.py <url>` | performance |
| Web search for competitors | `scripts/competitor_scan.py` | competitors |

`scripts/fetch_page.py` also returns:
- HTTP headers, redirect chain, page load time estimate
- **`market`** — one of `lebanon`, `gcc`, `mena`, `eu`, `us`, `uk`,
  `global`. Auto-detected from the URL TLD (and HTML `lang`) unless
  `--market` is passed explicitly.
- The detected platform (Shopify / WooCommerce / BigCommerce /
  Next.js / Squarespace / Wix / custom)

Surface the detected market to the user at the start of the audit so
they can override it if it's wrong. The full set of locale-conditional
rules lives in `docs/market-expectations.md`. **Do not hardcode
market rules in this file or in agent files.**

Detect business type from the homepage HTML:
- **Dropship** — generic descriptions, AliExpress image patterns, no brand story
- **DTC Brand** — original branding, founder story, branded packaging mentions
- **Marketplace** — multiple sellers, varying branding
- **Service + Products** — hybrid (e.g., a salon selling products)

## Step 2 — Spawn agents in batches that share inputs

Group agents by their input dependencies so each fetched payload is
analyzed by every agent that needs it, instead of being re-fetched
per agent. Spawn agents within a batch via the Agent tool in a single
message (Claude Code dispatches Task calls in that message
concurrently).

Each agent receives: the relevant HTML(s), the detected platform, the
store URL, the resolved `market`, and any agent-specific inputs noted
below.

### Batch A — Homepage HTML consumers

Inputs: desktop homepage HTML, platform, URL, market.

| Agent | File | Analyzes |
|---|---|---|
| Header | `agents/ecom-header.md` | Logo, nav, announcement bar, cart icon, search |
| Hero  | `agents/ecom-hero.md`   | Value prop, H1, hero CTA, above-fold content |
| Copy  | `agents/ecom-copy.md`   | Headlines, value-prop framing, AI-content markers, superlatives |

### Batch B — Product page HTML consumers

Inputs: top 2–3 product page HTMLs (desktop), platform, URL, market.
Trust also needs the homepage HTML (footer + policy links).

| Agent | File | Analyzes |
|---|---|---|
| Products | `agents/ecom-products.md` | Descriptions, images, specs, variants, Product schema, alt text + variant a11y |
| CRO      | `agents/ecom-cro.md`      | Product/cart/checkout CTAs, purchase barriers, CTA-level accessibility |
| Offers   | `agents/ecom-offers.md`   | Pricing, anchoring, bundles, promotions, free-shipping threshold |
| Trust    | `agents/ecom-trust.md`    | Reviews, badges, guarantees, policies, contact, market-specific signals |

### Batch C — Independent inputs

Each of these agents needs a payload nobody else uses, so they can
all run alongside Batches A and B.

| Agent | File | Inputs | Analyzes |
|---|---|---|---|
| Mobile      | `agents/ecom-mobile.md`      | Mobile homepage HTML + mobile product page HTML | 390px viewport, tap targets, mobile CRO, mobile a11y |
| Performance | `agents/ecom-performance.md` | PageSpeed Insights JSON + homepage HTML | CWV (LCP/INP/CLS/FCP/TTFB), app bloat, render-blocking |
| Competitors | `agents/ecom-competitors.md` | Web search results + competitor HTML | 3–5 direct competitors, comparison matrix, positioning gaps |
| Retention   | `agents/ecom-retention.md`   | Homepage HTML (popup/footer markers) | Email capture, abandoned cart, post-purchase, WhatsApp/SMS |
| Upsells     | `agents/ecom-upsells.md`     | Product page HTML + cart page HTML | Pre-ATC / in-cart / pre-checkout / post-purchase upsells |
| Cart        | `agents/ecom-cart.md`        | Cart page HTML | Cart UX, checkout step count, guest checkout, payment icons |
| SEO         | `agents/ecom-seo.md`         | Homepage HTML + product page HTML + robots.txt + sitemap.xml | Meta tags, schema, sitemap/robots, AI crawler access, link depth, canonicals, alt SEO. **Separate Discoverability Score — not folded into ECOM Health.** |

### A note on actual parallelism

Claude Code's Task tool spawns sub-agents concurrently within a
single message, but each spawned sub-agent itself runs sequentially
through its own steps, and the underlying model API rate-limits the
total number of in-flight Task calls. Empirically that ceiling is
typically around 3–4 effective parallel agents, not 14. The batching
above is structured so that the **slowest dependency for each batch
overlaps with the slowest dependency for the others**:

- Batch A reads the homepage that's already in memory.
- Batch B reads product page HTML that the orchestrator fetched in
  parallel with the homepage.
- Batch C's heaviest legs (PageSpeed Insights, competitor web
  search) are wall-clock-bound on external APIs, so dispatching them
  alongside A and B is free.

Net effect: the audit's wall time is roughly
`max(homepage fetch, product fetches, PSI call, competitor search)
 + the slowest agent in the slowest batch`, not 14 × per-agent time.

Agents apply market-conditional rules from
`docs/market-expectations.md`. If `market = global`, agents skip
locale-conditional checks entirely.

### Accessibility coverage

A11y is **not a separate agent** and is **not a separate weight
category**. It is folded into the existing CRO, Products, and Mobile
scoring so that a11y wins lift the same scores that conversion wins
do. Coverage by agent:

- `ecom-cro` — CTA color contrast (≥ 4.5:1, WCAG 1.4.3), visible
  focus states on keyboard nav (WCAG 2.4.7), ATC button has an
  accessible name (WCAG 4.1.2). Worth 8 of the 100 CRO points.
- `ecom-products` — alt text on product images (WCAG 1.1.1),
  variant selectors keyboard-accessible (WCAG 2.1.1), price not
  conveyed by color alone (WCAG 1.4.1). Worth 5 of the 100 Products
  points.
- `ecom-mobile` — tap targets ≥ 44×44px (WCAG 2.5.5), viewport zoom
  not disabled (WCAG 1.4.4), form inputs have associated labels
  (WCAG 1.3.1 / 3.3.2). Worth 5 of the 100 Mobile points.

Frame a11y findings as **both a CRO issue and a legal-risk issue**:
ADA lawsuits against US e-commerce sites (Shopify and WooCommerce in
particular) have risen sharply, and even a Tier-A WCAG failure is
sufficient grounds for a demand letter.

## Step 3 — Compute ECOM Health Score

Collect scores from all agents. Apply weights:

| Category | Agents | Weight |
|---|---|---|
| Product Presentation | Products | 18% |
| Conversion Rate Optimization | CRO + Cart | 18% |
| Offer & Pricing Strategy | Offers + Upsells | 13% |
| Trust & Social Proof | Trust | 12% |
| Mobile Experience | Mobile | 10% |
| Performance (CWV) | Performance | 10% |
| First Impression | Header + Hero | 8% |
| Copy & Messaging | Copy | 6% |
| Retention & Email | Retention | 5% |

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

Then delegate to the `ecom-report` agent (`agents/ecom-report.md`) which will:
1. Run `scripts/extract_brand.py <url> --download-logo` to get brand colors and logo
2. Run `scripts/ecom_report.py` with the full scores JSON and brand signals:
```
scripts/ecom_report.py \
  --report ECOM-AUDIT-REPORT.md \
  --action-plan ACTION-PLAN.md \
  --scores '{"overall": <score>, "categories": {...}}' \
  --url <url> \
  --platform <platform> \
  --brand-color <primary_color> \
  --store-name "<store_name>" \
  --store-description "<description>" \
  --logo <logo_path> \
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
