# Claude ECOM — Project Instructions

## What This Is

Claude ECOM is a Claude Code skill that audits e-commerce stores and generates a scored PDF report with prioritized fixes. It covers conversion rate optimization, product presentation, pricing strategy, trust signals, competitor positioning, mobile experience, and more.

## Repository Structure

```
claude-ecom/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── skills/
│   ├── ecom/SKILL.md         # Main orchestrator + command router
│   ├── ecom-audit/SKILL.md   # Full store audit (spawns all agents)
│   ├── ecom-cro/SKILL.md     # Conversion rate optimization
│   ├── ecom-products/SKILL.md # Product page analysis
│   ├── ecom-competitors/SKILL.md # Competitor scan
│   ├── ecom-performance/SKILL.md # Speed & Core Web Vitals
│   ├── ecom-trust/SKILL.md   # Trust & social proof
│   ├── ecom-offers/SKILL.md  # Pricing, bundles, upsells
│   ├── ecom-copy/SKILL.md    # Copy & messaging audit
│   ├── ecom-mobile/SKILL.md  # Mobile experience
│   └── ecom-retention/SKILL.md # Email & retention
├── agents/                   # Sub-agents for parallel execution
│   ├── ecom-header.md
│   ├── ecom-hero.md
│   ├── ecom-products.md
│   ├── ecom-cart.md
│   ├── ecom-cro.md
│   ├── ecom-offers.md
│   ├── ecom-upsells.md
│   ├── ecom-trust.md
│   ├── ecom-mobile.md
│   ├── ecom-performance.md
│   ├── ecom-copy.md
│   ├── ecom-competitors.md
│   ├── ecom-retention.md
│   └── ecom-report.md
├── scripts/
│   ├── fetch_page.py         # HTML fetcher with UA spoofing
│   ├── pagespeed.py          # PageSpeed Insights API wrapper
│   ├── competitor_scan.py    # Web search competitor analysis
│   └── ecom_report.py        # WeasyPrint PDF report generator
├── requirements.txt
└── pyproject.toml
```

## Architecture

### 3-Layer Model

1. **Orchestration**: `skills/ecom/SKILL.md` routes commands to sub-skills
2. **Sub-skills**: Each domain area has its own SKILL.md with specialized logic
3. **Agents**: Parallel sub-agents do the actual page fetching, analysis, and scoring

### Full Audit Flow

```
/ecom audit <url>
  → fetch all inputs once at the orchestrator
      (homepage desktop + mobile HTML, top 2-3 product pages,
       robots.txt, sitemap.xml, PageSpeed Insights, competitor SERPs)
  → detect platform + market
  → spawn 14 specialist agents in three input-sharing batches:
      Batch A — header, hero, copy            (homepage HTML)
      Batch B — products, cro, offers, trust  (product page HTML)
      Batch C — mobile, performance, competitors, retention,
                upsells, cart, seo            (independent inputs)
  → collect agent JSONs, validate against scripts/schemas.py
  → compute weighted ECOM Health Score
      (drop malformed agents, renormalize denominator)
  → generate PDF via ecom_report.py
```

Note on "parallel": Claude Code's Task tool dispatches sub-agents
concurrently within a single message, but the model API rate-limits
total in-flight Tasks to roughly 3–4 effective parallel agents. The
batching above pipelines work so the audit's wall time is bounded by
the slowest batch (plus the slowest network fetch in Step 1), not by
14 × per-agent time. See `skills/ecom-audit/SKILL.md` for details.

### Scoring Weights

| Category | Weight |
|---|---|
| Product Presentation | 18% |
| Conversion Rate Optimization | 18% |
| Offer & Pricing Strategy | 13% |
| Trust & Social Proof | 12% |
| Mobile Experience | 10% |
| Performance (CWV) | 10% |
| First Impression (Header + Hero) | 8% |
| Copy & Messaging | 6% |
| Retention & Email | 5% |

### Priority Tiers

- **CRITICAL** — Actively losing sales today (fix immediately)
- **HIGH** — Significant conversion lift available (fix within 1 week)
- **MEDIUM** — Optimization opportunity (fix within 1 month)
- **LOW** — Backlog polish

## Conventions

- All skills use kebab-case directories
- SKILL.md files stay under 500 lines / 5000 tokens
- Agents are invoked via the Agent tool, never Bash
- Python scripts must include docstrings + argparse CLI + JSON output
- All URLs validated through `scripts/fetch_page.py validate_url()` (SSRF protection)
- Revenue-impact framing: every issue states what conversion % it costs

## Output Files

Every full audit produces:
- `ECOM-AUDIT-REPORT.md` — Full findings markdown
- `ACTION-PLAN.md` — Prioritized checklist
- `ecom-report.pdf` — Professional A4 PDF with charts and score cards

## Install

```bash
bash install.sh   # macOS/Linux
.\install.ps1     # Windows
```

## Usage

```
/ecom audit <url>             # Full store audit
/ecom cro <url>               # CRO-only deep dive
/ecom products <url>          # Product page analysis
/ecom competitors <url>       # Competitor scan
/ecom copy <url>              # Copy & messaging audit
/ecom mobile <url>            # Mobile experience check
/ecom offers <url>            # Pricing & offer strategy
/ecom trust <url>             # Trust & social proof audit
/ecom retention <url>         # Email & retention audit
/ecom performance <url>       # Speed & Core Web Vitals
```
