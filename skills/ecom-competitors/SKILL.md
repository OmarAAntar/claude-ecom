---
name: ecom-competitors
description: Competitor analysis for e-commerce stores. Finds 3-5 direct competitors via web search, compares pricing, offers, trust signals, catalog depth, and positioning. Identifies gaps and opportunities. Use when user says competitors, competitive analysis, what are others doing, or how do I compare.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Competitor Analysis

## Step 1 — Identify Competitors

Use web search to find 3–5 direct competitors based on:
1. Same product category
2. Same geographic market (e.g., Lebanon, US, UK)
3. Similar price tier
4. Similar business model (DTC, dropship, marketplace)

Search queries to use:
- `[product category] [country] buy online`
- `[product name] alternative [country]`
- `best [product category] store [country]`
- `[product category] cash on delivery [country]` (if COD market)

Run `scripts/fetch_page.py` on each competitor homepage.

## Step 2 — Competitor Comparison Matrix

For each competitor, extract:

| Signal | How to find |
|---|---|
| Price of comparable product | Product page |
| Shipping offer | Homepage banner / product page |
| Return policy days | Footer / policies page |
| Review count (flagship product) | Product page |
| Review platform | Trustpilot badge / Judge.me / etc |
| WhatsApp / live chat | Bottom-right corner |
| Payment methods | Footer icons / checkout |
| Catalog size (approx) | Collections page |
| Hero offer | Homepage above fold |
| Trust badges | Homepage / checkout |
| Blog / content present | Nav / footer |
| Social proof (followers) | Social links in footer |

## Step 3 — Gap Analysis

### Price Gap
- Is the audited store priced above, below, or at market?
- Is the price difference justified by quality signals?
- What is the cheapest competitor's price for the same product?

### Offer Gap
- What promotions are competitors running that this store isn't?
- BOGO, bundles, free gift with purchase, loyalty points?
- Are competitors showing a more aggressive free-shipping threshold?

### Trust Gap
- Review count differential — how many more reviews do competitors have?
- Do competitors have Trustpilot / Google reviews widget?
- Do competitors have a "As Seen In" press bar?

### Content Gap
- Do competitors have a blog? How many posts?
- Do competitors have a YouTube channel?
- Do competitors have more product images / videos?

### UX Gap
- Is the competitor's checkout faster?
- Do they have a better mobile experience?
- Do they have a live chat / WhatsApp visible?

## Output Format

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
