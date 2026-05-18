---
name: ecom-mobile
description: Mobile experience audit for e-commerce stores. Checks 390px viewport rendering, tap targets, thumb zones, mobile CRO, and mobile-specific trust signals. Use when user says mobile, phone experience, or mobile conversion.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Mobile Experience Audit

## Scoring Weights (100 pts)

| Check | Points |
|---|---|
| Primary CTA visible without scrolling on 390px | 12 |
| Tap targets ≥ 44×44px (Apple HIG standard) | 10 |
| Body font size ≥ 16px (prevents iOS auto-zoom) | 8 |
| No horizontal scroll | 10 |
| Sticky ATC / bottom bar on product pages | 8 |
| Checkout form triggers correct keyboard type | 7 |
| Images not overflowing container | 6 |
| Navigation accessible (hamburger works correctly) | 6 |
| No overlapping elements | 5 |
| Checkout form is autofill-compatible | 6 |
| Product images swipeable (not just tap) | 5 |
| Video doesn't autoplay and block content | 4 |
| WhatsApp / chat widget thumb-reachable (bottom-right) | 5 |
| Font rendering sharp (not pixelated) | 4 |
| Modal/popup closeable on mobile (X button large enough) | 4 |

## Viewport Check (390px = iPhone 14 standard)

Fetch mobile HTML using iPhone 14 UA:
`Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15`

Check:
- Does the hero CTA appear above the fold (first 844px of height)?
- Is price visible without scrolling on product page?
- Is the ATC button visible without scrolling on product page?

## Thumb Zone Analysis

On mobile, the bottom-center of screen is easiest to reach. The top-left is hardest.
- ATC button should be in bottom-center or sticky at bottom
- Primary navigation items should be within 75px of screen bottom
- Cart icon should be top-right (thumb-reachable on right hand)
- Chat/WhatsApp widget should be bottom-right

## Keyboard Type Check (Checkout Form)

| Field | Expected input type |
|---|---|
| Phone number | `type="tel"` |
| Email | `type="email"` |
| Card number | `inputmode="numeric"` |
| Postal code | `inputmode="numeric"` |
| Name | `autocomplete="name"` |
| Address | `autocomplete="address-line1"` |

If wrong keyboard type shown → flag as HIGH (adds friction to every mobile checkout).

## Mobile-Specific CRO

- Bottom sticky bar for "Add to Cart" is the #1 mobile CRO improvement for product pages
- "Swipe to next image" hint on first product image
- Cart page: checkout button should be first thing visible, not below the cart items
- Popup close buttons must be ≥ 44px and in the top-right corner

## Output Format

```
MOBILE SCORE: XX/100

VIEWPORT CHECK (390px):
Hero CTA above fold: [YES/NO]
Price visible without scroll: [YES/NO]
ATC button visible without scroll: [YES/NO]

CRITICAL MOBILE ISSUES:
- [issue] — [fix]

HIGH MOBILE ISSUES:
- [issue] — [fix]

QUICK WINS:
1. [specific CSS/HTML fix with code snippet]
2. [specific fix]
3. [specific fix]
```
