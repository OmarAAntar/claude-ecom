# Claude ECOM

> E-commerce store audit suite for [Claude Code](https://claude.ai/code). Scores your store /100 across CRO, product pages, offers, trust, mobile, copy, and competitors. Generates a professional PDF action plan.

Inspired by [claude-seo](https://github.com/AgriciDaniel/claude-seo).

---

## What It Does

Drop a store URL, get back a scored audit report with:

- **ECOM Health Score** (0–100) across 9 weighted categories
- **Discoverability Score** (0–100) — reported separately. SEO + AI-search (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) crawler access, schema, sitemap/robots, canonicals, link depth
- **Competitor scan** — finds 3–5 direct competitors, builds a comparison matrix
- **CRO analysis** — checkout friction, CTA quality, purchase barriers
- **Product page audit** — content depth, image quality, schema, reviews
- **Offer strategy** — bundles, upsells, pricing psychology, AOV optimization
- **Trust audit** — reviews, policies, contact, badges, market-specific signals
- **Mobile experience** — 390px viewport, tap targets, sticky ATC, keyboard types
- **Copy audit** — with ready-to-use rewrites for every weak headline and CTA
- **Performance** — Core Web Vitals (LCP, INP, CLS) via PageSpeed Insights
- **Retention** — email capture, abandoned cart, post-purchase flows
- **Accessibility** — folded into CRO, product, and mobile scoring: CTA contrast, focus states, keyboard-accessible variants, alt text, tap targets, viewport zoom, form labels. A11y failures both cost conversion **and** expose US stores to ADA lawsuits (a growing risk for Shopify and WooCommerce merchants).
- **PDF report** — professional A4 with charts, pass/fail tables, and a 30-day sprint plan

## Sample Output

```
ECOM Health Score: 41 / 100 — CRITICAL

First Impression:    38/100
Product Pages:       45/100
CRO:                 28/100
Offer Strategy:      35/100
Trust:               52/100
Mobile:              30/100
Copy:                44/100
Retention:           20/100
Performance:         38/100
```

## Install

### macOS / Linux
```bash
git clone https://github.com/your-handle/claude-ecom
cd claude-ecom
bash install.sh
```

### Windows
```powershell
git clone https://github.com/your-handle/claude-ecom
cd claude-ecom
.\install.ps1
```

**Requirements:** Python 3.10+, Claude Code

## Usage

```
/ecom audit <url>             # Full store audit + PDF report
/ecom cro <url>               # CRO-only deep dive
/ecom products <url>          # Product page analysis
/ecom competitors <url>       # Competitor scan
/ecom copy <url>              # Copy & messaging audit
/ecom mobile <url>            # Mobile experience check
/ecom offers <url>            # Pricing & offer strategy
/ecom trust <url>             # Trust & social proof audit
/ecom retention <url>         # Email & retention audit
/ecom performance <url>       # Speed & Core Web Vitals
/ecom seo <url>               # SEO + AI-search discoverability (separate score)
```

## Architecture

```
13 parallel agents → score aggregation → markdown reports → PDF
```

| Layer | Files | Role |
|---|---|---|
| Orchestrator | `skills/ecom/SKILL.md` | Routes commands |
| Full audit | `skills/ecom-audit/SKILL.md` | Spawns all agents |
| Sub-skills | `skills/ecom-*/SKILL.md` | Domain-specific logic |
| Agents | `agents/ecom-*.md` | Parallel analysis |
| Scripts | `scripts/*.py` | Fetch, PSI API, PDF |

## Scoring Weights

| Category | Weight |
|---|---|
| Product Presentation | 18% |
| Conversion Rate Optimization | 18% |
| Offer & Pricing Strategy | 13% |
| Trust & Social Proof | 12% |
| Mobile Experience | 10% |
| Performance (Core Web Vitals) | 10% |
| First Impression (Header + Hero) | 8% |
| Copy & Messaging | 6% |
| Retention & Email | 5% |

## Optional: PageSpeed Insights API Key

Without an API key, performance scores use Lighthouse lab data.
With a key, you get real CrUX field data (actual user measurements).

```bash
export PSI_API_KEY=your_key_here
```

Get a free key at [console.cloud.google.com](https://console.cloud.google.com).

## License

MIT — free to use, fork, and build on.

---

*Generated reports include a footer: "Audited by Claude ECOM Audit Suite"*
