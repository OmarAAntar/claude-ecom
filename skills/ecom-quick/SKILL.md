---
name: ecom-quick
description: Fast e-commerce triage. Runs only 3 agents (storefront, conversion, trust & offers) and returns a top-line score and the top 3 critical issues in under 2 minutes. No PDF. Use when user says quick audit, fast check, triage, top issues, or just looking to spot-check a store before committing to a full audit.
user-invokable: true
argument-hint: <url>
version: 2.0.0
category: ecommerce
---

# E-Commerce Quick Audit

User-invokable: `/ecom quick <url>`

## When to Use

Run when the user wants a fast spot-check — under 2 minutes — to
decide whether the store needs a full audit. Not a replacement for
`/ecom audit`; intentionally narrow.

## What It Covers

Only three agents, the highest-leverage subset of the full audit:

- `agents/ecom-storefront.md` — H1 + value prop, hero CTA,
  announcement bar, AI-content markers
- `agents/ecom-conversion.md` — product/cart/checkout CTAs, sticky
  ATC, guest checkout, exit intent, mobile friction
- `agents/ecom-trust-offers.md` — reviews, policies, Lebanon trust
  signals (COD / WhatsApp / Whish), pricing anchoring, upsell stack

Deliberately excluded from quick: products deep-dive, performance,
competitors. If the quick audit raises red flags, recommend the
full audit.

## Orchestration

1. Validate URL via `scripts/fetch_page.py validate_url()`
2. Fetch desktop + mobile HTML via `scripts/fetch_page.py`
3. Detect platform (see `skills/ecom/SKILL.md`)
4. Spawn the three agents in parallel with HTML, platform, and URL
5. Compute the Quick Score (see below)
6. Render the user-facing output

## Quick Score

This is **not** the ECOM Health Score. It is a triage signal.

Re-normalized weighted average using the full-audit relative weights:

```
storefront_w   = 15
conversion_w   = 30
trust_offers_w = 18
total_w        = 63

quick_score = round(
  (storefront_score   * storefront_w   +
   conversion_score   * conversion_w   +
   trust_offers_score * trust_offers_w)
  / total_w
)
```

Label the score explicitly as **Quick Score** in the output — never
as "ECOM Health Score" — so users don't conflate the two.

## User-Facing Output Format

```
QUICK SCORE: XX / 100 — [CRITICAL/POOR/FAIR/GOOD/EXCELLENT]

URL:       [url]
Platform:  [detected platform]

Sub-scores:
- Storefront:    XX/100
- Conversion:    XX/100
- Trust & Offers: XX/100

TOP 3 CRITICAL ISSUES:
1. [issue]
2. [issue]
3. [issue]

TOP 3 QUICK WINS:
1. [fix — effort estimate]
2. [fix]
3. [fix]

Run `/ecom audit <url>` for the full 5-agent analysis with PDF report.
```

The trailing line is required — do not omit it.

## Hard Rules

- No PDF generation. Markdown output only.
- Target time-to-output: under 2 minutes. Skip PageSpeed Insights and
  competitor scan entirely.
- If fewer than 3 CRITICAL issues exist across all three agents,
  promote HIGH-severity items to fill the slot — label them "(HIGH)".
