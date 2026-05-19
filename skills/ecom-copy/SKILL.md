---
name: ecom-copy
description: Copy and messaging audit for an e-commerce store — H1 and value-prop clarity (the 5-second test), CTA specificity grading, product-description benefit-led vs spec-led check, AI-content red-flag detection (unique / elevate / seamlessly / stunning / unparalleled / embark / delve), unsubstantiated-superlative flags ("#1 in market"), objection handling, and readability targets. Use when the user wants ready-to-paste rewrites for headlines, CTAs, and product descriptions. Natural trigger phrases include: rewrite my headlines, fix my copy, my product descriptions sound generic, my hero is weak, sounds AI-written, my CTAs are vague, my value proposition is unclear, ad copy audit, messaging review.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Copy & Messaging Audit

User-invokable: `/ecom copy <url>`

## When to Use

Run when the user asks about copy quality, headlines, product descriptions, value propositions, tone, or AI-content concerns.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch HTML via `scripts/fetch_page.py`
3. Detect platform (see `skills/ecom/SKILL.md` routing table)
4. Spawn `agents/ecom-copy.md` with the fetched HTML, URL, and detected `market` (auto-detected by `scripts/fetch_page.py`; rules in `docs/market-expectations.md`)
5. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-copy.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
COPY SCORE: XX/100

HOMEPAGE COPY:
H1: "[current text]" — [STRONG/WEAK/MISSING]
CTA: "[current text]" — Grade [A/B/C/D]
Value prop: [CLEAR/VAGUE/MISSING]
Readability: Grade [X]

TOP COPY ISSUES:
1. [issue] — [rewrite suggestion]
2. [issue] — [rewrite suggestion]
3. [issue] — [rewrite suggestion]

READY-TO-USE REWRITES:
H1: "[suggested rewrite]"
CTA: "[suggested rewrite]"
Hero subheadline: "[suggested rewrite]"
Product description opening for [product]: "[suggested rewrite]"
```
