---
name: ecom-retention
description: Email and retention audit for an e-commerce store — popup quality (timing, offer, closeability), footer signup, abandoned-cart flow detection, post-purchase welcome and review-request flows, win-back sequences, loyalty/referral programs, WhatsApp/SMS channels, and market-specific weighting (full credit for Lebanon/GCC/MENA where WhatsApp is the primary channel; email-first for EU/UK; email + SMS for US). Use when the user wants to boost repeat purchase rate or recover abandoned carts. Natural trigger phrases include: improve repeat purchases, abandoned cart flow, email marketing audit, Klaviyo setup, fix my popups, post-purchase flow, customers don't come back, win-back emails, loyalty program ideas.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Retention & Email Audit

User-invokable: `/ecom retention <url>`

## When to Use

Run when the user asks about email, popups, abandoned cart, post-purchase flows, loyalty, referral, or Klaviyo/Omnisend setup.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch HTML via `scripts/fetch_page.py`
3. Detect platform (see `skills/ecom/SKILL.md` routing table)
4. Spawn `agents/ecom-retention.md` with the HTML, platform, URL, and detected `market` (auto-detected by `scripts/fetch_page.py`; affects WhatsApp/SMS weighting per `docs/market-expectations.md`)
5. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-retention.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
RETENTION SCORE: XX/100

EMAIL CAPTURE:
Popup: [PRESENT/MISSING] — timing: [X seconds / exit intent / immediate]
Offer: "[offer text]" — [STRONG/WEAK/NONE]
Footer signup: [PRESENT/MISSING]

FLOWS:
Abandoned cart: [CONFIGURED/NOT CONFIGURED]
Post-purchase: [CONFIGURED/NOT CONFIGURED]
Review request: [CONFIGURED/NOT CONFIGURED]
Win-back: [CONFIGURED/NOT CONFIGURED]

CRITICAL GAPS:
- [gap] — estimated revenue recovery: [estimate]

QUICK WINS:
1. [action] — [platform-specific instructions] — [time]
2. [action]
3. [action]
```
