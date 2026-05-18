---
name: ecom-offers
description: Pricing and offer strategy audit for e-commerce stores. Analyzes price anchoring, bundles, upsells, promotions, free shipping thresholds, and psychological pricing. Use when user says pricing, offers, bundles, promotions, or how to increase average order value.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Offer & Pricing Strategy Audit

## Scoring Weights (100 pts)

| Check | Points |
|---|---|
| Hero offer visible on homepage (not just "shop now") | 10 |
| Price anchoring shown (compare-at price crossed out) | 8 |
| Savings amount shown ("You save $10") | 5 |
| Psychological pricing used ($X.99 vs round numbers) | 4 |
| Free shipping threshold shown and prominent | 8 |
| Bundle offer present (buy 2 get X) | 8 |
| Volume discount tiers present | 5 |
| Post-purchase upsell present | 7 |
| In-cart upsell / cross-sell present | 7 |
| Pre-checkout bump offer | 6 |
| Urgency signal present (countdown, stock level) | 6 |
| Scarcity signal present ("Only 3 left") | 5 |
| Gift wrapping / personalization upsell | 3 |
| Subscription / repeat purchase option | 4 |
| Clearance / sale collection present | 4 |
| Loyalty / points program | 3 |
| Referral program present | 4 |
| BNPL option (Klarna, Afterpay, Shop Pay installments) | 3 |

## Pricing Analysis

### Price Anchoring
Is there a crossed-out "Compare at" price?
- PASS: Shown clearly next to the sale price
- FAIL: No anchor price shown (customer has no reference)
- WARNING: Fake anchoring — compare-at price that was never real (FTC/ASA risk)

### Bundle Opportunities
Based on catalog:
- Same category bundles: "Buy 2 car mounts, save 15%"
- Complementary bundles: "Car mount + phone cable"
- Gift bundles: "Set of 3 for gifting"

### Upsell Timing
| Upsell type | Best placement | Expected AOV lift |
|---|---|---|
| Pre-ATC (frequently bought with) | Product page | +8–12% |
| In-cart bump | Cart page | +5–10% |
| Pre-checkout bump | Before payment step | +10–20% |
| Post-purchase 1-click | Thank-you page | +15–30% |

## AOV Calculator

Current AOV estimate based on visible product prices.
Target AOV with bundle + upsell strategy.
Gap = opportunity to close.

## Urgency & Scarcity Audit

Legitimate urgency signals (use these):
- Real countdown to sale end
- Real stock levels ("Only 3 left in stock")
- "Order in next X hours for delivery by [date]"

Fake urgency signals (flag as risk):
- Perpetual countdowns that reset
- Fake "10 people viewing this" notifications
- False "Last 1 in stock" when stock is unlimited

## Output Format

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
