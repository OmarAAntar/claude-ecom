---
name: ecom-offers
description: Pricing and offer-strategy audit for an e-commerce store — price anchoring (crossed-out compare-at), psychological pricing (.99 / .95 endings), free-shipping threshold prominence, bundle types (volume / complementary / gift), the full upsell stack (pre-ATC, in-cart, pre-checkout bump, post-purchase 1-click), legitimate vs fake urgency signals, BNPL, loyalty/referral, and a current-vs-potential AOV estimate. Use when the user wants to raise AOV, add bundles, or fix flat promotions. Natural trigger phrases include: increase average order value, raise AOV, bundle ideas, upsell strategy, pricing audit, my offers are flat, free shipping threshold, fake urgency check, set up bundles, AOV is too low.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Offer & Pricing Strategy Audit

User-invokable: `/ecom offers <url>`

## When to Use

Run when the user asks about pricing, bundles, promotions, AOV, upsells, free shipping thresholds, or offer strategy.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch HTML via `scripts/fetch_page.py`
3. Detect platform (see `skills/ecom/SKILL.md` routing table)
4. Spawn `agents/ecom-offers.md` with the fetched HTML, URL, and detected `market` (auto-detected by `scripts/fetch_page.py`; affects VAT/currency rules per `docs/market-expectations.md`)
5. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-offers.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
OFFERS SCORE: XX/100

PRICING ANALYSIS:
- Price anchoring: [PASS/FAIL/WARNING]
- Psychological pricing: [PASS/FAIL]
- Bundle strategy: [NONE/BASIC/STRONG]
- Upsell stack: [NONE/PARTIAL/COMPLETE]

CURRENT ESTIMATED AOV: $XX
POTENTIAL AOV WITH FULL UPSELL STACK: $XX (+XX%)

CRITICAL GAPS:
- [gap] — estimated AOV impact: +$X per order

QUICK WIN BUNDLES TO CREATE:
1. [bundle name] — [products] — [recommended price] — [estimated uptake %]
2. [bundle name]
3. [bundle name]

RECOMMENDED UPSELL APPS:
- [app name] (free/paid) — for [upsell type]
```
