---
name: ecom-trust
description: Trust and social proof audit for e-commerce stores. Checks reviews, badges, guarantees, policies, contact visibility, founder story, and press mentions. Use when user says trust issues, people aren't buying, or why don't customers trust my store.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Trust & Social Proof Audit

## Scoring Weights (100 pts)

| Check | Points |
|---|---|
| Reviews present on product pages | 12 |
| Review count ≥ 10 per flagship product | 8 |
| Review photos / UGC present | 6 |
| Star rating visible on collection page | 5 |
| Third-party review platform (Trustpilot/Google) | 6 |
| Money-back guarantee visible | 8 |
| Return policy clearly stated (days + process) | 7 |
| Contact method above fold (WhatsApp/email/chat) | 8 |
| Phone number or physical address visible | 5 |
| Founder / About Us page exists | 6 |
| SSL badge / secure checkout icon visible | 4 |
| Payment method icons in footer | 4 |
| "As Seen In" press bar | 4 |
| Customer count / orders served social proof | 4 |
| Trust badge on product page (near ATC button) | 5 |
| Policy pages crawlable (not JS-only) | 4 |
| No unsubstantiated superlatives (#1 in Lebanon) | 4 |

## Market-Specific Trust Signals

### Lebanon / MENA
- Cash on Delivery: CRITICAL — must be prominent
- WhatsApp contact: CRITICAL — primary customer service channel
- Lebanese phone number: HIGH
- Delivery to all governorates stated: HIGH
- USD pricing with LBP note: MEDIUM

### US / EU
- Trustpilot or Google reviews widget: HIGH
- BNPL option (Klarna/Afterpay/Shop Pay): MEDIUM
- "Free returns" prominently stated: HIGH
- SSL padlock visible in nav: MEDIUM

### General
- Founder photo humanizes brand: HIGH
- "X orders delivered" counter: MEDIUM
- Instagram/TikTok feed showing real customers: HIGH

## Review Gap Analysis

If review count < 10:
- Flag as CRITICAL for high-price items (> $30)
- Flag as HIGH for low-price items
- Recommend: Judge.me (free), Stamped.io, or Shopify native reviews
- Provide review request email template

If reviews exist but no photos:
- Flag as MEDIUM
- Add photo incentive: "Send a photo, get 10% off your next order"

## Policy Visibility Check

Policies must be:
- Linked in footer (REQUIRED)
- Written in plain language (not legalese)
- Accessible without login
- Not hidden behind a JS modal on first visit

Refund policy must state:
- Number of days (30-day minimum recommended)
- Condition of return (unopened / any condition)
- Who pays return shipping

## Output Format

```
TRUST SCORE: XX/100

TRUST BREAKDOWN:
Reviews: XX/30 — [status]
Policies: XX/20 — [status]
Contact: XX/20 — [status]
Brand Authority: XX/15 — [status]
Badges: XX/15 — [status]

CRITICAL TRUST GAPS:
- [issue] — conversion impact: [estimate]

QUICK WINS:
1. [action] — [time estimate] — [app or tool]
2. [action]
3. [action]

MARKET-SPECIFIC GAPS:
[issues specific to detected market]
```
