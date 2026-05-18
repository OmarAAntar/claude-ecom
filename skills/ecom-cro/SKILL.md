---
name: ecom-cro
description: Conversion Rate Optimization audit for e-commerce stores. Analyzes checkout flow, CTAs, form friction, exit intent, and purchase barriers. Use when user says CRO, conversion, checkout issues, or why aren't people buying.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# CRO Audit

## Scoring Weights (100 pts total)

| Check | Points |
|---|---|
| Primary CTA visible above fold (desktop + mobile) | 10 |
| CTA button contrast ratio ≥ 4.5:1 | 5 |
| Add-to-Cart button size ≥ 44px height | 5 |
| Guest checkout option available | 8 |
| Checkout step count ≤ 3 | 8 |
| Form field count at checkout ≤ 8 | 7 |
| Autofill supported (name, address, card) | 5 |
| Progress bar/indicator in checkout | 5 |
| Trust badges visible at checkout | 7 |
| Payment method icons shown | 5 |
| Exit-intent popup present | 5 |
| Sticky ATC bar on product pages (mobile) | 6 |
| Error messages are descriptive (not just red outline) | 4 |
| Cart summary visible during checkout | 5 |
| Free shipping threshold shown in cart | 5 |
| "You save X" shown on discounted items | 5 |

## What to Check Per Page

### Homepage / Landing Page
- Is the primary CTA the most visually dominant element?
- Does the hero answer: What is it? Who is it for? Why buy here?
- Are there competing CTAs confusing the visitor?
- Is the value proposition visible without scrolling?

### Product Page
- Is "Add to Cart" visible without scrolling on mobile?
- Is the price visible without scrolling?
- Is there a sticky ATC bar that appears on scroll?
- Are variant selectors (size, color) intuitive — swatches vs dropdowns?
- Is stock level shown? ("Only 3 left" adds urgency)
- Is shipping estimate on the product page?
- Is the return policy a single visible sentence on the page?

### Cart Page
- Is editing quantity easy (not buried)?
- Is the checkout button above the fold?
- Is there a "continue shopping" link (not just browser back)?
- Does the cart show product images?
- Is the free-shipping-upsell message shown? ("Add $X for free shipping")

### Checkout
- How many steps? (1-page vs multi-step)
- Is guest checkout offered?
- Is the form autofill-friendly?
- Are error messages specific and helpful?
- Is the order summary always visible?
- Is the CTA button text action-oriented? ("Place Order" vs "Continue")
- Are security badges visible near the submit button?

## Revenue Impact Framing

For each issue found, attach a conversion impact estimate:
- Missing sticky ATC (mobile): ~3–6% conversion loss
- No guest checkout: ~35% of visitors abandon at account creation
- Checkout > 3 steps: ~20% drop-off per extra step
- Poor CTA contrast: ~1–3% conversion loss
- No free shipping indicator: ~5–8% cart abandonment increase

## Output Format

```
CRO SCORE: XX/100

CRITICAL (fix immediately):
- [issue] — estimated ~X% conversion impact

HIGH (fix within 1 week):
- [issue] — estimated ~X% conversion impact

MEDIUM (fix within 1 month):
- [issue]

QUICK WINS (under 1 hour):
1. [specific fix with exact instructions]
2. [specific fix with exact instructions]
3. [specific fix with exact instructions]

READY-TO-USE CODE:
[paste-ready Liquid/CSS/JS snippets for top fixes]
```
