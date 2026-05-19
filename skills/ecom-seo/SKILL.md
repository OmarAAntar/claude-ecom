---
name: ecom-seo
description: E-commerce SEO and AI-search discoverability audit. Checks meta tags, product schema, organization schema, sitemap/robots, AI crawler accessibility (GPTBot, ClaudeBot, PerplexityBot, Google-Extended), internal linking depth, canonicals, and image alt SEO quality. Reports a separate Discoverability Score that does not factor into the ECOM Health Score. Use when user says SEO, schema, robots, sitemap, AI crawlers, GPTBot, ClaudeBot, discoverability, or AI Overviews.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# E-Commerce SEO & AI-Search Discoverability

User-invokable: `/ecom seo <url>`

## When to Use

Run when the user asks about SEO, schema markup, robots.txt, sitemap,
AI crawler access (GPTBot, ClaudeBot, PerplexityBot, Google-Extended),
canonical tags, internal linking, or AI Overview discoverability.

## Scope

This audit produces a separate **Discoverability Score**. It does
**not** factor into the ECOM Health Score, because SEO debt and
conversion debt have different fix timelines and risk profiles —
mixing them masks both.

## Orchestration

1. Validate the URL via `scripts/fetch_page.py validate_url()`
2. Fetch homepage HTML via `scripts/fetch_page.py`
3. Fetch `/robots.txt` and `/sitemap.xml`
4. Identify the top 2–3 product page URLs from the homepage
5. Fetch those product pages
6. Detect platform (see `skills/ecom/SKILL.md` routing table)
7. Spawn `agents/ecom-seo.md` with: homepage HTML, product page HTML,
   robots.txt content, sitemap.xml content, platform, and URL
8. Format the agent's JSON output using the user-facing template below

## Scoring Rubric & Check Criteria

See `agents/ecom-seo.md` for the scoring rubric and check criteria.

## User-Facing Output Format

```
DISCOVERABILITY SCORE: XX/100

META TAGS:
Title: "[current]" — [grade]
Description: "[current]" — [grade]
Open Graph: [COMPLETE/PARTIAL/MISSING]
Twitter Card: [COMPLETE/PARTIAL/MISSING]

STRUCTURED DATA:
Product schema: [PASS/FAIL] — [missing fields]
Organization schema: [PASS/FAIL]
Fabricated rating risk: [YES/NO]

CRAWL INFRASTRUCTURE:
sitemap.xml: [REACHABLE/MISSING]
Referenced in robots.txt: [YES/NO]
Product coverage in sitemap: XX%

AI CRAWLER ACCESS:
Blocked bots: [list, or NONE]

LINK GRAPH:
Max click depth to products: X
Orphan products: [list]

CANONICALS:
Canonical coverage on product pages: XX%
Cross-product canonical bugs: [list]

IMAGE ALT (SEO quality):
Alt coverage: XX% — descriptiveness: [GOOD/FAIR/POOR]

CRITICAL:
- [issue]

HIGH:
- [issue]

QUICK WINS:
1. [specific fix]
2. [specific fix]
3. [specific fix]
```
