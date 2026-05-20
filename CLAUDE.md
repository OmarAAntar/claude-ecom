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
      ecom-storefront     → first_impression, copy
      ecom-products       → products
      ecom-conversion     → cro, mobile
      ecom-trust-offers   → trust, offers, retention
      ecom-performance    → performance
  → aggregate the 9 sub-scores using the 9-category weights below
  → generate PDF via ecom_report.py (9-row category dashboard)
```

Competitors are **not** spawned by default — they're an opt-in
`/ecom competitors <url>` command.

### Scoring Weights

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

Weights sum to 100. The 9 category sub-scores are emitted by the 5
execution agents (each agent produces 1–3 sub-scores per its rubric).

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
