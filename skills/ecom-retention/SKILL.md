---
name: ecom-retention
description: Email and retention audit for e-commerce stores. Checks popups, email capture, lead magnets, abandoned cart flows, post-purchase sequences, and loyalty programs. Use when user says email, retention, repeat customers, popups, or Klaviyo.
user-invokable: true
argument-hint: <url>
version: 1.0.0
category: ecommerce
---

# Retention & Email Audit

## Scoring Weights (100 pts)

| Check | Points |
|---|---|
| Email capture popup present | 10 |
| Popup fires at exit intent or 5+ seconds (not immediately) | 6 |
| Popup offers genuine value (% off, free guide, early access) | 8 |
| Popup closeable (visible X button ≥ 44px) | 5 |
| Footer newsletter signup present | 5 |
| Abandoned cart email configured | 12 |
| Post-purchase email sequence exists | 10 |
| Review request email (triggered 7–14 days post-delivery) | 8 |
| Win-back email for lapsed customers | 6 |
| SMS capture present (optional but strong in MENA) | 4 |
| Loyalty / points program present | 5 |
| Referral program present | 5 |
| WhatsApp broadcast list or chat widget | 6 |
| Social follow prompt on thank-you page | 3 |
| Subscription option for consumables | 2 |

## Popup Audit

Good popup:
- Fires on exit intent OR after 5+ seconds (not on load)
- Offers a specific value ("Get 10% off your first order")
- Has a clear email input field
- Has a visible, easy-to-click close button
- Does NOT appear on every page on mobile (Google penalty risk)

Bad popup:
- Fires immediately on page load (highest bounce rate trigger)
- Just says "Subscribe to our newsletter" (no value prop)
- Covers the entire screen on mobile with no easy close
- Re-appears on every visit

## Email Flow Priority

| Flow | Revenue impact | Setup time |
|---|---|---|
| Abandoned cart (1hr / 24hr / 72hr) | Highest | 30 min |
| Post-purchase welcome + upsell | High | 1 hour |
| Review request (Day 7–14 post-ship) | High | 20 min |
| Browse abandonment | Medium | 1 hour |
| Win-back (90-day lapse) | Medium | 30 min |
| Loyalty milestone | Low | 2 hours |

## Platform-Specific Notes

### Shopify
- Native: Shopify Email (free, basic)
- Recommended: Klaviyo (free up to 250 contacts), Omnisend
- Abandoned cart: Shopify → Settings → Notifications → Abandoned checkout

### WooCommerce
- Recommended: Klaviyo, Mailchimp, FluentCRM

### Lebanon / MENA
- WhatsApp broadcasts are more effective than email
- Consider WhatsApp Business API for post-purchase flows
- SMS via local provider (e.g., MessageBird, Twilio with LB numbers)

## Output Format

```
RETENTION SCORE: XX/100

EMAIL CAPTURE:
Popup: [PRESENT/MISSING] — timing: [X seconds / exit intent / immediate]
Offer: "[offer text]" — [STRONG/WEAK/NONE]
Footer signup: [PRESENT/MISSING]

FLOWS:
Abandoned cart: [CONFIGURED/NOT CONFIGURED]
Post-purchase: [CONFIGURED/NOT CONFIGURED]
Review request: [CONFIGURED/NOT CONFIGURED]
Win-back: [CONFIGURED/NOT CONFIGURED]

CRITICAL GAPS:
- [gap] — estimated revenue recovery: [estimate]

QUICK WINS:
1. [action] — [platform-specific instructions] — [time]
2. [action]
3. [action]
```
