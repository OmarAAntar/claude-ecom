---
name: ecom-trust
description: Trust and social proof audit for e-commerce stores. Checks reviews, badges, guarantees, policies, contact visibility, founder story, and press mentions. Use when user says trust issues, people aren't buying, or why don't customers trust my store.
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
