---
name: ecom-copy
description: Copy and messaging audit for e-commerce stores. Analyzes headlines, CTAs, product descriptions, value propositions, tone of voice, and persuasion elements. Use when user says copy, messaging, headlines, descriptions, or writing.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Copy & Messaging Audit

## Scoring Weights (100 pts)

| Check | Points |
|---|---|
| Homepage hero has clear value proposition (who + what + why) | 12 |
| H1 present and benefit-focused | 8 |
| CTA copy is specific ("Get 40% Off Today" vs "Shop Now") | 7 |
| Product descriptions are benefit-led | 8 |
| No unsubstantiated superlatives ("best", "#1", "world's finest") | 6 |
| No overused AI content markers ("unique", "elevate", "seamlessly") | 6 |
| Product copy addresses the main objection | 7 |
| Social proof copy is specific (numbers, names, outcomes) | 6 |
| Urgency copy is honest and specific | 5 |
| Tone is consistent across all pages | 5 |
| Copy is readable at ≤ Grade 9 level | 5 |
| No spelling or grammar errors | 6 |
| Meta descriptions are action-oriented | 5 |
| Announcement bar copy has a clear offer | 4 |
| Footer copy is not generic | 4 |
| About page copy is personal and credible | 6 |

## Hero Copy Framework

A strong hero follows this structure:
```
H1: [What you get] — [For whom] — [Key differentiator]
Subheadline: [Expand on the most important benefit or remove friction]
CTA: [Specific action] → [Specific outcome]
```

Examples:
- WEAK: "Premium Gadgets & Unique Gifts"
- STRONG: "Tech Gifts That Actually Get Used — Delivered Across Lebanon in 1–4 Days"

## CTA Copy Grading

| CTA Text | Grade | Notes |
|---|---|---|
| "Shop Now" | D | Generic, no benefit |
| "Buy Now" | C | Clear but no hook |
| "Get Free Shipping Today" | B | Benefit-focused |
| "Claim Your 20% Off" | A | Ownership + urgency |
| "Send a Gift — Free Delivery" | A+ | Addresses the use case |

## AI Content Detection

Flag if 3+ of these words appear in product descriptions:
- "unique", "elevate", "seamlessly", "effortlessly", "stunning", "innovative", "exceptional", "meticulously", "unparalleled", "embark", "delve"

These patterns are associated with low-quality AI content by Google's QRG evaluators.

## Objection Handling Check

For each product, identify the #1 customer objection and check if the copy addresses it:
- Gadgets: "Will it work with my phone?" → compatibility statement required
- Gifts: "Will it arrive on time?" → delivery date estimate required
- High-price: "Is it worth it?" → comparison to alternatives + ROI framing needed
- COD markets: "Is this store legit?" → trust copy + WhatsApp required

## Readability Check

Target: Grade 8–9 (Flesch-Kincaid).
- Sentences > 25 words: flag for splitting
- Paragraphs > 4 sentences: flag for breaking up
- Passive voice > 20% of sentences: flag for rewriting

## Output Format

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
