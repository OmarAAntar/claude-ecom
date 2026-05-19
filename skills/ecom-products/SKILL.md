---
name: ecom-products
description: Product page audit for e-commerce stores. Analyzes descriptions, images, specifications, variants, reviews, schema markup, and content depth. Use when user says product pages, product descriptions, product images, or fix my listings.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Product Page Audit

User-invokable: `/ecom products <url>`

## When to Use

Run when the user asks about product pages, descriptions, images, specs, variants, schema, or thin content.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch homepage HTML via `scripts/fetch_page.py`
3. Identify product page URLs from the HTML (links to `/products/*`, `/product/*`, etc.)
4. Fetch the top 3 product pages
5. Detect platform (see `skills/ecom/SKILL.md` routing table)
6. Spawn `agents/ecom-products.md` with the product page HTML, platform, URL, and detected `market` (auto-detected by `scripts/fetch_page.py`; affects the market-context check per `docs/market-expectations.md`)
7. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-products.md` for the scoring rubric and check criteria.

## User-Facing Output Format

For each product page found, produce a mini-report:

```
PRODUCT: [product name]
URL: [product url]
DESCRIPTION: [word count] words — [CRITICAL/FAIL/PARTIAL/PASS]
IMAGES: [count] images — [issues]
SPECS: [PRESENT/MISSING]
REVIEWS: [count] reviews
SCHEMA: [PASS/FAIL] — [issues]
ISSUES: [bullet list]
FIXES: [specific copy improvements + schema snippets]
```

Then an aggregate product score.
