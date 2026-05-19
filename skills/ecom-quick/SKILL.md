---
name: ecom-quick
description: Fast e-commerce triage in under 2 minutes — runs only the hero, CRO, and trust agents to surface a top-line Quick Score and the top 3 critical issues, with no PDF. Use when the user wants a spot-check before deciding whether to invest in a full audit, or is in a hurry and wants the headline issues only. Natural trigger phrases include: quick audit, fast check, triage my store, spot-check this store, give me the top issues, what's the worst problem, ballpark score, take a quick look, just the highlights, 2-minute audit.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# E-Commerce Quick Audit

User-invokable: `/ecom quick <url>`

## When to Use

Run when the user wants a fast spot-check — under 2 minutes — to
decide whether the store needs a full audit. Not a replacement for
`/ecom audit`; intentionally narrow.

## What It Covers

Only three agents, chosen because they cover the highest-leverage
above-the-fold + conversion + trust signals:

- `agents/ecom-hero.md` — H1, value prop, hero CTA, hero trust
- `agents/ecom-cro.md` — product/cart/checkout CTAs and purchase
  barriers
- `agents/ecom-trust.md` — reviews, policies, contact, market-specific
  trust signals

Deliberately excluded: header, product page deep-dive, cart deep-dive,
offers, upsells, mobile, performance, copy, retention, competitors,
SEO. If the quick audit raises red flags, recommend the full audit.

## Orchestration

1. Validate URL via `scripts/fetch_page.py validate_url()`
2. Fetch desktop HTML via `scripts/fetch_page.py` (auto-detects market)
3. Detect platform (see `skills/ecom/SKILL.md`)
4. Spawn the three agents in parallel with HTML, platform, URL, and
   detected `market` (rules: `docs/market-expectations.md`)
5. Compute the Quick Score (see below)
6. Render the user-facing output

## Quick Score

This is **not** the ECOM Health Score. It is a triage signal.

Compute as a re-normalized weighted average of just the three agent
scores, using the same relative weights from the full rubric:

```
hero_w  = 8   # First Impression (Header+Hero) — using hero only here
cro_w   = 18
trust_w = 12
total_w = hero_w + cro_w + trust_w  # = 38

quick_score = round(
  (hero_score  * hero_w  +
   cro_score   * cro_w   +
   trust_score * trust_w)
  / total_w
)
```

Label the score explicitly as **Quick Score** in the output — never
as "ECOM Health Score" — so users don't conflate the two.

## User-Facing Output Format

```
QUICK SCORE: XX / 100 — [CRITICAL/POOR/FAIR/GOOD/EXCELLENT]

URL:       [url]
Market:    [detected market]
Platform:  [detected platform]

Sub-scores:
- Hero:  XX/100
- CRO:   XX/100
- Trust: XX/100

TOP 3 CRITICAL ISSUES:
1. [issue from any of the three agents]
2. [issue]
3. [issue]

TOP 3 QUICK WINS:
1. [fix — effort estimate]
2. [fix]
3. [fix]

Run `/ecom audit <url>` for the full 13-agent analysis with PDF report.
```

The trailing line is required — do not omit it. It is how users learn
that quick is a triage tool, not a full audit.

## Hard Rules

- No PDF generation. Markdown output only.
- Target time-to-output: under 2 minutes. Do not call optional helpers
  (no PageSpeed Insights, no competitor scan, no robots.txt fetch).
- If fewer than 3 CRITICAL issues exist across all three agents,
  promote HIGH-severity items to fill the slot — and label them
  "(HIGH)" so the user knows they were promoted.
- If `market = global` (no specific market detected), apply only
  universal trust/hero/CRO checks per the agents' rules.
