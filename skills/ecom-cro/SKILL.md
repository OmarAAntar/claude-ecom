---
name: ecom-cro
description: Conversion Rate Optimization audit for e-commerce stores. Analyzes checkout flow, CTAs, form friction, exit intent, and purchase barriers. Use when user says CRO, conversion, checkout issues, or why aren't people buying.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# CRO Audit

User-invokable: `/ecom cro <url>`

## When to Use

Run when the user asks about conversion, checkout issues, CTAs, why visitors aren't converting, or wants a CRO deep dive without a full audit.

## Scope

Product page + cart + checkout CTAs and purchase barriers.

Does **NOT** cover:
- Hero/above-the-fold CTA (handled by `agents/ecom-hero.md`)
- Nav and announcement-bar CTAs (handled by `agents/ecom-header.md`)
- Mobile-specific CTA failure modes — tap target size, sticky ATC presence (handled by `agents/ecom-mobile.md`)

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch desktop + mobile HTML via `scripts/fetch_page.py`
3. Detect platform (see `skills/ecom/SKILL.md` routing table)
4. Spawn `agents/ecom-cro.md` with the fetched HTML, detected platform, and URL
5. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-cro.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
CRO SCORE: XX/100

CRITICAL (fix immediately):
- [issue] — estimated ~X% conversion impact

HIGH (fix within 1 week):
- [issue] — estimated ~X% conversion impact

MEDIUM (fix within 1 month):
- [issue]

QUICK WINS (under 1 hour):
1. [specific fix with exact instructions]
2. [specific fix with exact instructions]
3. [specific fix with exact instructions]

READY-TO-USE CODE:
[paste-ready Liquid/CSS/JS snippets for top fixes]
```
