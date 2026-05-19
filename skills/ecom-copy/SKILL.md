---
name: ecom-copy
description: Copy and messaging audit for e-commerce stores. Analyzes headlines, CTAs, product descriptions, value propositions, tone of voice, and persuasion elements. Use when user says copy, messaging, headlines, descriptions, or writing.
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
4. Spawn `agents/ecom-copy.md` with the fetched HTML and URL
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
