# Claude ECOM — Project Instructions

## What This Is

Claude ECOM is a Claude Code skill that audits e-commerce stores and
generates a scored PDF action plan **in under 5 minutes**. It targets
the Lebanese market by default (COD, WhatsApp, Whish Pay, USD/LBP,
Wakilni/Toters/Bosta).

## Repository Structure

```
claude-ecom/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── skills/
│   ├── ecom/SKILL.md         # Orchestrator + command router
│   ├── ecom-audit/SKILL.md   # Full store audit (spawns the 5 agents)
│   ├── ecom-quick/SKILL.md   # 3-agent triage, under 2 min
│   ├── ecom-products/SKILL.md   # Standalone products deep-dive
│   ├── ecom-performance/SKILL.md # Standalone perf + CWV
│   └── ecom-competitors/SKILL.md # Opt-in competitor scan
├── agents/
│   ├── ecom-storefront.md    # Header + hero + copy
│   ├── ecom-products.md      # Product page checks
│   ├── ecom-conversion.md    # CRO + cart + mobile friction
│   ├── ecom-trust-offers.md  # Trust + offers + upsells
│   ├── ecom-performance.md   # CWV + perf
│   ├── ecom-competitors.md   # Opt-in
│   └── ecom-report.md        # Aggregator + PDF trigger
├── scripts/
│   ├── fetch_page.py         # HTML fetcher with UA spoofing
│   ├── pagespeed.py          # PageSpeed Insights API wrapper
│   ├── competitor_scan.py    # Web search competitor analysis
│   ├── extract_brand.py      # Logo / color extractor for the PDF
│   └── ecom_report.py        # WeasyPrint PDF report generator
├── requirements.txt
└── pyproject.toml
```

## Architecture

### 3-Layer Model

1. **Orchestration**: `skills/ecom/SKILL.md` routes commands.
2. **Sub-skills**: Each command has its own SKILL.md.
3. **Agents**: 5 sub-agents do the analysis in parallel.

### Full Audit Flow

```
/ecom audit <url>
  → fetch homepage + mobile HTML + 2-3 product pages
  → detect platform (Shopify / WooCommerce / custom)
  → spawn 5 agents in parallel:
      ecom-storefront, ecom-products, ecom-conversion,
      ecom-trust-offers, ecom-performance
  → collect scores
  → compute weighted ECOM Health Score
  → generate PDF via ecom_report.py
```

Competitors are **not** spawned by default — they're an opt-in
`/ecom competitors <url>` command.

### Scoring Weights

| Category | Weight |
|---|---|
| Conversion | 30% |
| Products | 25% |
| Trust & Offers | 18% |
| Storefront | 15% |
| Performance (CWV) | 12% |

Weights sum to 100.

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
- All URLs validated through `scripts/fetch_page.py validate_url()`
- Revenue-impact framing: every issue states what conversion % it costs

## Output Files

Every full audit produces:
- `ECOM-AUDIT-REPORT.md` — Full findings markdown
- `ACTION-PLAN.md` — Prioritized checklist
- `ecom-report.pdf` — Professional A4 PDF

## Install

```bash
bash install.sh   # macOS/Linux
.\install.ps1     # Windows
```

## Usage

```
/ecom audit <url>             # Full audit + PDF (< 5 min)
/ecom quick <url>             # 3-agent triage (< 2 min)
/ecom products <url>          # Standalone products
/ecom performance <url>       # Standalone CWV
/ecom competitors <url>       # Opt-in competitor scan
```
