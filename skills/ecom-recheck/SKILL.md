---
name: ecom-recheck
description: Re-audits a store and produces a delta report against a prior ECOM audit. Re-runs the full 14-agent audit, parses the previous ECOM-AUDIT-REPORT.md, and shows score changes, resolved issues, persistent issues, and new issues. Use when user says recheck, re-audit, what changed, score delta, or follow-up audit.
user-invokable: true
argument-hint: <url> <previous-report-path>
version: 1.0.0
category: ecommerce
---

# E-Commerce Re-Audit (Delta)

User-invokable: `/ecom recheck <url> <previous-report-path>`

## When to Use

Run when the user has previously audited a store and wants to see
what changed since the last report. The previous report path can be
absolute or relative; it must point at the `ECOM-AUDIT-REPORT.md`
produced by an earlier `/ecom audit` run.

## Inputs

- `<url>` — store URL (re-audited fresh; do not trust the URL in the
  previous report to be current)
- `<previous-report-path>` — path to a prior `ECOM-AUDIT-REPORT.md`.
  Validate it exists and is readable **before** kicking off the
  re-audit — failing fast is cheaper than running 14 agents and
  discovering the path is wrong.

## Orchestration

1. Validate the report path: `Path(previous_report_path).is_file()`.
   If missing, abort and ask the user to confirm the path.
2. Parse the prior report:
   ```
   python scripts/parse_report.py <previous-report-path>
   ```
   Capture the JSON. The parser is defensive — if it returns warnings,
   surface them to the user but continue.
3. Run the full audit pipeline exactly as `skills/ecom-audit/SKILL.md`
   describes: fetch, detect platform + market, spawn all 14 agents,
   compute scores, write `ECOM-AUDIT-REPORT.md` and `ACTION-PLAN.md`,
   generate the PDF.
4. After the new report is written, parse it the same way to get the
   new score table and issue lists.
5. Compute the delta (see below) and write
   `ECOM-RECHECK-DELTA.md` to the current directory.

## Delta Computation

### Score deltas

For each category present in both reports:

```
delta = new_score - previous_score
direction =
  "improved" if delta > 0
  else "regressed" if delta < 0
  else "unchanged"
```

Also compute overall ECOM Health Score delta and (if both reports
include it) Discoverability Score delta.

### Issue diffs

Match issues by normalized text (lowercase, strip punctuation, collapse
whitespace) since two audits won't produce byte-identical bullets:

- **Resolved**: present in previous CRITICAL/HIGH, absent in new
- **Persistent**: present in previous CRITICAL/HIGH, still in new
- **New**: present in new CRITICAL/HIGH, absent in previous
- **Promoted/demoted**: same issue text but different severity bucket

Fuzziness rules:
- Compare on lowercased, punctuation-stripped, whitespace-collapsed
  strings.
- Treat synonyms loosely — e.g. "no exit intent popup" and
  "missing exit-intent popup" should match. If unsure, prefer NOT
  matching (better to surface as both Resolved + New than to lose
  a real change).

## User-Facing Output Format

Render the user-facing summary AND write `ECOM-RECHECK-DELTA.md`:

```
ECOM RE-AUDIT DELTA

URL:                 [url]
Previous report:     [path]
Previous audit date: [date from report, or "unknown"]
Current audit date:  [today]

OVERALL:
  ECOM Health Score:  [prev] → [new]   ([±delta])  [improved/regressed/unchanged]
  Discoverability:    [prev] → [new]   ([±delta])  [improved/regressed/unchanged]

PER CATEGORY:
  First Impression:           [prev] → [new]   ([±delta])
  Product Presentation:       [prev] → [new]   ([±delta])
  Conversion Rate:            [prev] → [new]   ([±delta])
  Offer & Pricing:            [prev] → [new]   ([±delta])
  Trust & Social Proof:       [prev] → [new]   ([±delta])
  Mobile Experience:          [prev] → [new]   ([±delta])
  Copy & Messaging:           [prev] → [new]   ([±delta])
  Retention & Email:          [prev] → [new]   ([±delta])
  Performance:                [prev] → [new]   ([±delta])

RESOLVED (was CRITICAL/HIGH, now clear):
- [issue]
- [issue]

PERSISTENT (was CRITICAL/HIGH, still flagged):
- [issue]
- [issue]

NEW (CRITICAL/HIGH in this audit, not in previous):
- [issue]
- [issue]

SEVERITY CHANGES:
- "[issue]" — [old severity] → [new severity]

NOTES:
- [parser warnings, if any]
- [market detection note if it changed since last audit]
```

If the previous report could not be parsed cleanly, render the new
audit's full output as normal, and prepend a NOTE explaining that the
delta could not be computed.

## Hard Rules

- Always run a fresh full audit. Never just re-render the previous
  report.
- Do not "fix" the previous report. Treat it as immutable history.
- The new audit's `ECOM-AUDIT-REPORT.md`, `ACTION-PLAN.md`, and PDF
  are produced normally. The delta is an additional artifact.
- If category names changed between runs (e.g. weight rebalance
  introduced a new category), include unmatched-category rows with a
  note rather than silently dropping them.
