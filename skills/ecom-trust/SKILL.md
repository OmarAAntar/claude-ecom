---
name: ecom-trust
description: Trust and social-proof audit for an e-commerce store — reviews and ratings, third-party review platforms (Trustpilot, Judge.me, Google), money-back guarantees, return/refund policy clarity, contact-method visibility (WhatsApp, phone, address), founder/About page, payment-method icons, and market-specific trust signals (e.g. COD + WhatsApp for Lebanon, BNPL + Arabic surface for GCC). Use when the user suspects visitors don't trust the store enough to buy, or wants to make a new DTC brand feel legitimate. Natural trigger phrases include: trust issues, people don't trust my store, why aren't customers buying, social proof audit, do I look legit, fix my reviews, no one trusts my brand, look at my return policy, trust badges check.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Trust & Social Proof Audit

User-invokable: `/ecom trust <url>`

## When to Use

Run when the user asks about reviews, trust signals, refund/return policy, contact visibility, badges, or founder story.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch HTML via `scripts/fetch_page.py`
3. Detect platform (see `skills/ecom/SKILL.md` routing table)
4. Spawn `agents/ecom-trust.md` with the HTML, URL, and detected `market` (auto-detected by `scripts/fetch_page.py`; the trust agent applies market-specific benchmarks from `docs/market-expectations.md`)
5. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-trust.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
TRUST SCORE: XX/100

TRUST BREAKDOWN:
Reviews: XX/30 — [status]
Policies: XX/20 — [status]
Contact: XX/20 — [status]
Brand Authority: XX/15 — [status]
Checkout Trust: XX/15 — [status]

CRITICAL TRUST GAPS:
- [issue] — conversion impact: [estimate]

QUICK WINS:
1. [action] — [time estimate] — [app or tool]
2. [action]
3. [action]

MARKET-SPECIFIC GAPS:
[issues specific to detected market]
```
