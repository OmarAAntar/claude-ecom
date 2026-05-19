---
name: ecom-mobile
description: Mobile experience audit for e-commerce stores. Checks 390px viewport rendering, tap targets, thumb zones, mobile CRO, and mobile-specific trust signals. Use when user says mobile, phone experience, or mobile conversion.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Mobile Experience Audit

User-invokable: `/ecom mobile <url>`

## When to Use

Run when the user asks about mobile experience, phone rendering, tap targets, mobile conversion, or sticky ATC.

## Scope

Mobile-specific failure modes at the 390px viewport. Owns: tap target sizing, sticky ATC presence, mobile keyboard types, horizontal scroll, mobile font size, thumb-zone placement, mobile popup closeability.

Does **NOT** cover:
- Desktop CTA quality or copy (handled by `agents/ecom-cro.md`, `agents/ecom-hero.md`, `agents/ecom-header.md`)
- Mobile Core Web Vitals (handled by `agents/ecom-performance.md`)

When a CTA already audited elsewhere also has a mobile-specific problem (e.g., a checkout CTA that's too small), only score the mobile failure mode — do not re-score the CTA itself.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch HTML with the iPhone 14 UA: `Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15`
3. Detect platform (see `skills/ecom/SKILL.md` routing table)
4. Spawn `agents/ecom-mobile.md` with the mobile HTML, URL, and detected `market` (auto-detected by `scripts/fetch_page.py`; rules in `docs/market-expectations.md`)
5. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-mobile.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
MOBILE SCORE: XX/100

VIEWPORT CHECK (390px):
Hero CTA above fold: [YES/NO]
Price visible without scroll: [YES/NO]
ATC button visible without scroll: [YES/NO]

CRITICAL MOBILE ISSUES:
- [issue] — [fix]

HIGH MOBILE ISSUES:
- [issue] — [fix]

QUICK WINS:
1. [specific CSS/HTML fix with code snippet]
2. [specific fix]
3. [specific fix]
```
