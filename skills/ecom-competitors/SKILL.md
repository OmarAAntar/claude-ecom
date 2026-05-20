---
name: ecom-competitors
description: Competitor analysis for e-commerce stores. Finds 3-5 direct competitors via web search, compares pricing, offers, trust signals, catalog depth, and positioning. Identifies gaps and opportunities. Use when user says competitors, competitive analysis, what are others doing, or how do I compare.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Competitor Analysis

User-invokable: `/ecom competitors <url>`

## When to Use

Run when the user asks about competitors, competitive positioning, how they stack up, or which gaps to exploit.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch the audited store's HTML via `scripts/fetch_page.py`
3. Detect the product category and target market from the HTML
4. Run `scripts/competitor_scan.py` to identify 3–5 direct competitors via web search
5. Fetch each competitor's homepage + flagship product page (filter out marketplaces like Amazon/Noon)
6. Spawn `agents/ecom-competitors.md` with the audited store HTML, competitor HTML, and detected market
7. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-competitors.md` for the scoring rubric and comparison matrix.

## User-Facing Output Format

```
COMPETITOR ANALYSIS

Audited Store: [url]
Market: [detected market]

COMPETITORS FOUND:
1. [name] — [url] — [price of comparable item]
2. [name] — [url] — [price of comparable item]
3. [name] — [url] — [price of comparable item]

COMPARISON MATRIX:
[table: signal × competitor]

KEY GAPS (opportunities):
CRITICAL: [things competitors do that are table stakes — you must match]
HIGH: [things competitors do well that give them an edge]
MEDIUM: [differentiators you could build]

POSITIONING RECOMMENDATION:
[1 paragraph: how to position vs competitors based on gaps]

QUICK WINS:
1. [specific thing to copy from competitor #1]
2. [specific thing to copy from competitor #2]
3. [specific gap to exploit as a differentiator]
```
