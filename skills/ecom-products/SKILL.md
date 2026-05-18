---
name: ecom-products
description: Product page audit for e-commerce stores. Analyzes descriptions, images, specifications, variants, reviews, schema markup, and content depth. Use when user says product pages, product descriptions, product images, or fix my listings.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Product Page Audit

## Scoring Weights (100 pts total)

| Check | Points |
|---|---|
| Description word count ≥ 300 words | 10 |
| Description is benefit-led (not spec-led) | 8 |
| Description is original (not manufacturer copy) | 10 |
| ≥ 4 product images per product | 8 |
| Lifestyle image present (product in use) | 6 |
| Product video present | 5 |
| Image zoom / lightbox available | 4 |
| Images served as WebP | 4 |
| Images ≤ 200KB each | 4 |
| Specifications table present | 6 |
| "What's in the box" list present | 4 |
| Variant selectors are visual (swatches > dropdowns) | 5 |
| Review count visible on product page | 8 |
| FAQ section on product page | 6 |
| Product schema with offers markup | 7 |
| Related/upsell products shown | 5 |

## Content Depth Checks

### Description Quality
- Is the first sentence benefit-focused? (What problem does it solve?)
- Are there specific claims with numbers? (89 lb suction force, not "strong")
- Is there Lebanon/local context if relevant?
- Is the copy written for humans, not search engines?
- Word count: <150 (CRITICAL), 150–299 (FAIL), 300–499 (PARTIAL), 500+ (PASS)

### Image Quality Checklist
- Studio shot: white/neutral background, product centered — REQUIRED
- Lifestyle shot: product in real-world use — REQUIRED
- Detail shot: close-up of key feature — HIGH
- Scale shot: next to common object to show size — MEDIUM
- Packaging shot: what arrives at customer's door — MEDIUM
- Video: 15–60 second demo — HIGH (especially for gadgets)

### Specification Gaps (flag if missing)
For gadgets/tech: dimensions, weight, material, compatibility, power input, certifications
For apparel: size guide, material %, care instructions, fit type
For home goods: dimensions, weight capacity, material, assembly required?
For gifts: dimensions, personalization options, shelf life (if perishable)

### Schema Audit
Check for Product schema on each product page:
- `@type: Product` present?
- `offers` with `price`, `priceCurrency`, `availability`?
- `brand` present?
- `aggregateRating` present if reviews exist?
- `@context` using https:// not http://?

## Thin Content Detection

Flag as thin if:
- Description < 150 words
- Description matches text findable on AliExpress/Amazon (duplicate)
- No specifications
- No images beyond 1 generic photo
- No reviews and no review request

## Output Format

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
