# Claude ECOM

> E-commerce store audit suite for [Claude Code](https://claude.ai/code). **Audit any Shopify, WooCommerce, or custom store in under 5 minutes — get a scored PDF action plan back.**

Inspired by [claude-seo](https://github.com/AgriciDaniel/claude-seo).

---

## What It Does

Drop a store URL, get back a scored audit report with:

- **ECOM Health Score** (0–100) across 9 weighted categories
- **CRITICAL / HIGH / MEDIUM / LOW** issue lists with ready-to-paste fixes
- **PDF action plan** with a 30-day sprint — professional A4 with charts and per-category score cards
- **5 minutes end-to-end**, not 30+

## Sample Output

```
ECOM Health Score: 51 / 100 — FAIR

Product Presentation:          55/100   18%
Conversion Rate Optimization:  45/100   18%
Offer & Pricing Strategy:      40/100   13%
Trust & Social Proof:          54/100   12%
Mobile Experience:             48/100   10%
Performance (CWV):             62/100   10%
First Impression:              60/100    8%
Copy & Messaging:              56/100    6%
Retention & Email:             25/100    5%
```

## Install

### macOS / Linux
```bash
git clone https://github.com/OmarAAntar/claude-ecom.git
cd claude-ecom
bash install.sh
```

### Windows
```powershell
git clone https://github.com/OmarAAntar/claude-ecom.git
cd claude-ecom
.\install.ps1
```

**Requirements:** Python 3.10+, Claude Code

## Usage

```
/ecom audit <url>             # Full store audit + PDF report (under 5 min)
/ecom quick <url>             # Fast triage — 3 agents, markdown only, under 2 min
/ecom products <url>          # Product page deep-dive
/ecom performance <url>       # Speed & Core Web Vitals
/ecom competitors <url>       # Competitor scan (opt-in; not part of full audit)
```

## Architecture

5 specialist agents execute the audit in parallel against one round
of HTML fetches. Each agent emits one or more sub-scores; the report
aggregator combines them into a 9-category weighted dashboard.

**Agents → sub-scores**

| Agent | File | Sub-scores emitted |
|---|---|---|
| Storefront | `agents/ecom-storefront.md` | `first_impression`, `copy` |
| Products | `agents/ecom-products.md` | `products` |
| Conversion | `agents/ecom-conversion.md` | `cro`, `mobile` |
| Trust & Offers | `agents/ecom-trust-offers.md` | `trust`, `offers`, `retention` |
| Performance | `agents/ecom-performance.md` | `performance` |

**ECOM Health Score weights**

| Category | Weight |
|---|---|
| Product Presentation | 18% |
| Conversion Rate Optimization | 18% |
| Offer & Pricing Strategy | 13% |
| Trust & Social Proof | 12% |
| Mobile Experience | 10% |
| Performance (CWV) | 10% |
| First Impression | 8% |
| Copy & Messaging | 6% |
| Retention & Email | 5% |

Sum: 100. Competitors is intentionally **not** in the default audit —
it's the slowest leg (web search across multiple domains) and most
users don't need it on every run.

## Output Files

Every full audit produces:
- `ECOM-AUDIT-REPORT.md` — Full findings markdown
- `ACTION-PLAN.md` — Prioritized checklist
- `ecom-report.pdf` — Professional A4 PDF with charts and score cards

## Optional: PageSpeed Insights API Key

Without an API key, performance scores use Lighthouse lab data.
With one, they use real CrUX field data. Set
`PAGESPEED_API_KEY=...` in your environment.

## Market Focus

Claude ECOM is built for the **Lebanese e-commerce market**. Trust
signals, payment expectations (COD + WhatsApp + Whish Pay + USD/LBP
dual currency), and delivery norms (Wakilni / Toters / Bosta) are
hardcoded for that context. The CRO and performance checks are
universal and work on any English-language storefront.
