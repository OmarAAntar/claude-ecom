---
name: ecom-competitors
description: Competitor scan for an e-commerce store — finds 3-5 direct competitors via web search (scoped to the store's market), fetches their homepages and flagship product pages, builds a comparison matrix across pricing, shipping, returns, reviews, payment methods, and content depth, and outputs a positioning recommendation plus quick wins to copy or differentiate from. Use when the user wants to benchmark, find positioning gaps, or pick which competitor tactics to imitate. Natural trigger phrases include: competitor analysis, who am I competing with, how do I compare, find competitors, competitive benchmark, what are others doing, positioning vs competitors, competitor pricing, competitor offers.
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
