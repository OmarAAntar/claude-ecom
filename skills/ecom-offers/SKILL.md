---
name: ecom-offers
description: Pricing and offer strategy audit for e-commerce stores. Analyzes price anchoring, bundles, upsells, promotions, free shipping thresholds, and psychological pricing. Use when user says pricing, offers, bundles, promotions, or how to increase average order value.
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
4. Spawn `agents/ecom-offers.md` with the fetched HTML, URL
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
