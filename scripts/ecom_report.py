#!/usr/bin/env python3
"""
ecom_report.py — Generate a professional A4 PDF e-commerce audit report.

Usage:
    python ecom_report.py \
        --report ECOM-AUDIT-REPORT.md \
        --action-plan ACTION-PLAN.md \
        [--scores '{"overall": 41, "categories": {...}}'  \
         | --agent-outputs path/to/agent_outputs.json] \
        --url https://example.com \
        --platform shopify \
        --output ecom-report.pdf \
        [--store-name "My Store"] \
        [--brand-color "#1d4ed8"] \
        [--logo path/to/logo.png or https://example.com/logo.png]

Score sources
-------------
Exactly one of ``--scores`` or ``--agent-outputs`` must be supplied:

- ``--scores`` is the pre-aggregated form: a JSON object with
  ``overall`` and ``categories`` keys, produced upstream by the
  ``ecom-report`` orchestrator agent. Used as-is.

- ``--agent-outputs`` is the raw form: a JSON file containing either
  a list of agent payloads, or an object keyed by agent name. Each
  payload is validated against ``scripts.schemas.AgentOutput``.

Validation behavior (``--agent-outputs`` path)
---------------------------------------------
Every incoming agent JSON is validated before aggregation. If an
agent's payload is malformed — e.g. ``score: "N/A"``, ``score: null``,
``score: 150``, missing required fields, or non-list ``critical`` /
``high`` — its payload is rejected. The script:

1. Logs the offending agent name and the specific field error to
   stderr.
2. **Excludes the rejected agent from aggregation entirely**, so the
   weighted-average denominator drops by that category's share and
   the remaining valid agents are renormalized over the remaining
   weight. This prevents a single malformed agent from silently
   producing a "0 score" pull on the overall.
3. Exits 0 with a partial report when at least one valid agent
   contributed, exits 2 when every agent failed validation.

Dependencies: weasyprint, matplotlib, pillow, requests, pydantic
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Schema + aggregation helpers live in scripts/schemas.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schemas import (  # noqa: E402
    AgentOutput,
    aggregate,
    discoverability_score,
    validate_agent_payload,
)


def _score_color(score: int) -> str:
    if score >= 70:
        return "#22c55e"   # green
    if score >= 50:
        return "#f59e0b"   # amber
    if score >= 30:
        return "#f97316"   # orange
    return "#ef4444"       # red


def _score_bg(score: int) -> str:
    """Light background tint matching score color."""
    if score >= 70:
        return "#f0fdf4"
    if score >= 50:
        return "#fffbeb"
    if score >= 30:
        return "#fff7ed"
    return "#fff1f2"


def _score_label(score: int) -> str:
    if score >= 80:
        return "GOOD"
    if score >= 60:
        return "FAIR"
    if score >= 40:
        return "POOR"
    return "CRITICAL"


def _score_tier(score: int) -> str:
    """Descriptive tier label for the cover page."""
    if score >= 80:
        return "High-Performing Store"
    if score >= 60:
        return "Growing Store — Good Foundation"
    if score >= 40:
        return "Developing Store — Key Gaps Found"
    if score >= 20:
        return "Early-Stage Store — Significant Improvements Needed"
    return "Critical Stage — Immediate Action Required"


def _extract_store_name(report_md: str, url: str) -> str:
    """Extract store name from first H1 in the report markdown, fallback to URL domain."""
    m = re.search(r'^#\s+([^—\n\r]+?)(?:\s+[—–].*)?$', report_md, re.MULTILINE)
    if m:
        name = m.group(1).strip()
        # Skip generic headings
        generic = {'ecom audit report', 'ecom health audit report', 'audit report'}
        if name and name.lower() not in generic:
            return name
    return url.replace("https://", "").replace("http://", "").split("/")[0]


def _load_logo(logo: str) -> str | None:
    """Load logo from file path or URL. Returns base64-encoded PNG/JPEG or None."""
    if not logo:
        return None
    try:
        if logo.startswith(("http://", "https://")):
            import urllib.request
            req = urllib.request.Request(logo, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
        else:
            with open(logo, "rb") as f:
                data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        print(f"Warning: could not load logo from {logo!r}: {e}", file=sys.stderr)
        return None


def _detect_logo_mime(logo_b64: str) -> str:
    """Detect image MIME type from base64 content."""
    try:
        data = base64.b64decode(logo_b64[:16])
        if data[:4] == b'\x89PNG':
            return "image/png"
        if data[:3] == b'\xff\xd8\xff':
            return "image/jpeg"
        if data[:4] in (b'GIF8', b'GIF9'):
            return "image/gif"
        if data[:4] == b'RIFF' or data[8:12] == b'WEBP':
            return "image/webp"
    except Exception:
        pass
    return "image/png"


def build_score_chart(scores: dict, brand_color: str = "#1d4ed8") -> str:
    """Build a horizontal bar chart of category scores. Returns base64 PNG."""
    categories = list(scores.items())
    labels = [c[0] for c in categories]
    values = [c[1] for c in categories]
    colors = [_score_color(v) for v in values]

    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 0.55)))
    bars = ax.barh(labels, values, color=colors, height=0.55, edgecolor="none")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score", fontsize=9, color="#6b7280")
    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=8, colors="#9ca3af")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.axvline(x=50, color="#e5e7eb", linewidth=0.8, linestyle="--")
    ax.axvline(x=70, color="#e5e7eb", linewidth=0.8, linestyle="--")
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{val}", va="center", fontsize=8.5, color="#374151", fontweight="bold")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def md_to_html_body(md: str) -> str:
    """Minimal Markdown → HTML converter (headings, bold, lists, code, horizontal rules)."""
    lines = md.split("\n")
    html_lines = []
    in_code = False
    in_ul = False
    in_table = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                html_lines.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                html_lines.append('<table class="audit-table">')
                in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            is_sep = all(re.match(r"^[-:]+$", c) for c in cells if c)
            if is_sep:
                continue
            tag = "th" if not any("---" in c for c in cells) else "td"
            row = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
            html_lines.append(f"<tr>{row}</tr>")
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            level = len(m.group(1))
            text = _inline_md(m.group(2))
            html_lines.append(f"<h{level}>{text}</h{level}>")
            continue

        # HR
        if re.match(r"^---+$", line.strip()):
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append("<hr>")
            continue

        # List items
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{_inline_md(m.group(1))}</li>")
            continue

        # Checkbox list items
        m = re.match(r"^- \[( |x)\]\s+(.*)", line)
        if m:
            if not in_ul:
                html_lines.append("<ul class='checklist'>")
                in_ul = True
            checked = "checked" if m.group(1) == "x" else ""
            html_lines.append(f"<li><input type='checkbox' {checked} disabled> {_inline_md(m.group(2))}</li>")
            continue

        # Empty line
        if not line.strip():
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            html_lines.append("<br>")
            continue

        # Regular paragraph
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        html_lines.append(f"<p>{_inline_md(line)}</p>")

    if in_ul:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</table>")

    return "\n".join(html_lines)


def _inline_md(text: str) -> str:
    """Apply inline markdown: bold, italic, code, links."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _build_css(brand_color: str = "#1d4ed8") -> str:
    return f"""
    @page {{
        size: A4;
        margin: 20mm 18mm 20mm 18mm;
        @bottom-center {{
            content: "Claude ECOM Audit Suite · " string(store-name) " · Page " counter(page);
            font-size: 8pt;
            color: #9ca3af;
        }}
    }}
    body {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 10pt;
        color: #111827;
        line-height: 1.6;
        margin: 0;
    }}
    .cover {{
        page-break-after: always;
    }}
    .cover-banner {{
        background: {brand_color};
        color: #ffffff;
        font-size: 13pt;
        font-weight: bold;
        letter-spacing: 3px;
        text-align: center;
        padding: 18px 24px;
        margin-bottom: 0;
    }}
    .cover-body {{
        text-align: center;
        padding: 40px 40px 30px 40px;
    }}
    .cover-logo {{
        max-height: 70px;
        max-width: 220px;
        object-fit: contain;
        margin-bottom: 24px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }}
    .cover-title {{
        font-size: 34pt;
        font-weight: bold;
        color: #1a1a2e;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }}
    .cover-url {{
        font-size: 10pt;
        color: #6b7280;
        margin-bottom: 4px;
    }}
    .cover-description {{
        font-size: 10pt;
        color: #9ca3af;
        margin-bottom: 28px;
        font-style: italic;
    }}
    .cover-meta {{
        display: flex;
        justify-content: center;
        gap: 40px;
        font-size: 9pt;
        color: #6b7280;
        border-top: 1px solid #e5e7eb;
        border-bottom: 1px solid #e5e7eb;
        padding: 14px 0;
        margin: 0 auto 28px auto;
        width: 80%;
    }}
    .cover-meta strong {{ color: #111827; }}
    .score-box {{
        background: {brand_color};
        border-radius: 10px;
        padding: 20px 30px 16px 30px;
        margin: 0 auto 28px auto;
        max-width: 280px;
    }}
    .score-box-label {{
        font-size: 9pt;
        font-weight: bold;
        letter-spacing: 2px;
        color: rgba(255,255,255,0.8);
        margin-bottom: 6px;
        text-transform: uppercase;
    }}
    .score-value {{
        font-size: 48pt;
        font-weight: bold;
        line-height: 1;
        margin-bottom: 4px;
    }}
    .score-denom {{
        font-size: 18pt;
        font-weight: normal;
        color: rgba(255,255,255,0.6);
    }}
    .score-tier {{
        font-size: 8pt;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 8px;
    }}
    .score-dashboard {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 20px 0;
        justify-content: center;
    }}
    .score-card {{
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
        min-width: 95px;
    }}
    .score-card .val {{
        font-size: 20pt;
        font-weight: bold;
    }}
    .score-card .lbl {{
        font-size: 7pt;
        color: #6b7280;
        margin-top: 2px;
    }}
    .critical-box {{
        background: #fff1f2;
        border-left: 4px solid #ef4444;
        border-radius: 4px;
        padding: 14px 18px;
        margin: 20px 0;
    }}
    .critical-box h3 {{ color: #b91c1c; margin: 0 0 8px 0; font-size: 11pt; }}
    h1 {{ font-size: 20pt; color: #111827; border-bottom: 2px solid #e5e7eb; padding-bottom: 6px; margin-top: 30px; }}
    h2 {{ font-size: 14pt; color: {brand_color}; margin-top: 24px; }}
    h3 {{ font-size: 11pt; color: #374151; margin-top: 16px; }}
    h4 {{ font-size: 10pt; color: #6b7280; margin-top: 12px; }}
    table.audit-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 9pt;
    }}
    table.audit-table th {{
        background: {brand_color};
        color: white;
        padding: 7px 10px;
        text-align: left;
        font-weight: 600;
    }}
    table.audit-table td {{
        padding: 6px 10px;
        border-bottom: 1px solid #f3f4f6;
    }}
    table.audit-table tr:nth-child(even) td {{ background: #f9fafb; }}
    pre {{
        background: #1e293b;
        color: #e2e8f0;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 8pt;
        overflow-wrap: break-word;
        white-space: pre-wrap;
        margin: 12px 0;
    }}
    code {{
        background: #f1f5f9;
        color: #0f172a;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 8.5pt;
    }}
    pre code {{ background: none; color: inherit; padding: 0; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 4px; }}
    ul.checklist {{ list-style: none; padding-left: 0; }}
    ul.checklist li {{ padding: 4px 0; border-bottom: 1px solid #f3f4f6; }}
    hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
    .page-break {{ page-break-before: always; }}
    .footer-note {{ font-size: 8pt; color: #9ca3af; text-align: center; margin-top: 40px; }}
    """


def build_html(
    report_md: str,
    action_plan_md: str,
    scores: dict,
    url: str,
    platform: str,
    audit_date: str,
    brand_color: str = "#1d4ed8",
    logo_b64: str = None,
    store_name_override: str = None,
    store_description: str = None,
) -> str:
    """Build full A4 HTML document from markdown content and scores."""
    overall = scores.get("overall", 0)
    categories = scores.get("categories", {})
    chart_b64 = build_score_chart(categories, brand_color) if categories else None

    score_color = _score_color(overall)
    score_bg = _score_bg(overall)
    tier = _score_tier(overall)

    # Derive store name: prefer explicit override, then extract from markdown, fallback to domain
    if store_name_override:
        store_name = store_name_override
    else:
        store_name = _extract_store_name(report_md, url)

    # Logo HTML
    logo_html = ""
    if logo_b64:
        mime = _detect_logo_mime(logo_b64)
        logo_html = f'<img class="cover-logo" src="data:{mime};base64,{logo_b64}" alt="{store_name} logo">'

    # Description line
    description_html = ""
    if store_description:
        description_html = f'<div class="cover-description">{store_description}</div>'

    # Score cards for category dashboard
    score_cards = ""
    for cat, val in categories.items():
        color = _score_color(val)
        score_cards += f"""
        <div class="score-card">
          <div class="val" style="color:{color}">{val}</div>
          <div class="lbl">{cat}</div>
        </div>"""

    cover = f"""
    <div class="cover">
      <div class="cover-banner">ECOM HEALTH AUDIT REPORT</div>
      <div class="cover-body">
        {logo_html}
        <div class="cover-title">{store_name}</div>
        <div class="cover-url">{url}</div>
        {description_html}
        <div class="cover-meta">
          <div><strong>Platform</strong><br>{platform.title()}</div>
          <div><strong>Date</strong><br>{audit_date}</div>
          <div><strong>Audited By</strong><br>Claude ECOM Audit Suite</div>
        </div>
        <div class="score-box">
          <div class="score-box-label">ECOM Health Score</div>
          <div class="score-value" style="color:#ffffff;">{overall}<span class="score-denom"> /100</span></div>
          <div class="score-tier" style="background:rgba(255,255,255,0.15); color:#ffffff;">{tier}</div>
        </div>
        <div class="score-dashboard">{score_cards}</div>
      </div>
    </div>"""

    # Chart page
    chart_section = ""
    if chart_b64:
        chart_section = f"""
        <div class="page-break">
          <h2>Score Breakdown</h2>
          <img src="data:image/png;base64,{chart_b64}" style="width:100%; max-width:540px; display:block; margin: 0 auto;">
        </div>"""

    report_body = md_to_html_body(report_md)
    action_body = md_to_html_body(action_plan_md)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>{_build_css(brand_color)}</style>
</head>
<body>
{cover}
{chart_section}
<div class="page-break">
{report_body}
</div>
<div class="page-break">
{action_body}
</div>
<div class="footer-note">
  Report generated by Claude ECOM Audit Suite · {audit_date} · CONFIDENTIAL
</div>
</body>
</html>"""


def generate_pdf(html: str, output_path: str) -> None:
    """Convert HTML to PDF using WeasyPrint."""
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(output_path)
    except ImportError:
        # Fallback: save HTML if WeasyPrint not installed
        html_path = output_path.replace(".pdf", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"WeasyPrint not installed. Saved HTML to: {html_path}", file=sys.stderr)
        return
    print(f"PDF report saved to: {output_path}")


def _load_and_validate_agent_outputs(path: str) -> tuple[list[AgentOutput], list[str]]:
    """Load agent outputs from a JSON file. Returns (valid_outputs, error_log)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        # Allow keyed-by-agent-name form: {"ecom-cro": {...}, ...}
        items = list(raw.values())
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError(
            f"--agent-outputs JSON must be a list or object, got {type(raw).__name__}"
        )

    valid: list[AgentOutput] = []
    errors: list[str] = []
    for item in items:
        output, err = validate_agent_payload(item)
        if output is not None:
            valid.append(output)
        else:
            errors.append(err or "unknown validation error")
    return valid, errors


def main():
    parser = argparse.ArgumentParser(description="Generate ECOM audit PDF report")
    parser.add_argument("--report", required=True, help="Path to ECOM-AUDIT-REPORT.md")
    parser.add_argument("--action-plan", required=True, help="Path to ACTION-PLAN.md")
    score_group = parser.add_mutually_exclusive_group(required=True)
    score_group.add_argument(
        "--scores",
        help='Pre-aggregated JSON scores: {"overall": 41, "categories": {...}}',
    )
    score_group.add_argument(
        "--agent-outputs",
        help="Path to a JSON file containing raw agent payloads (list or "
             "{agent_name: payload} object). Each payload is validated; "
             "invalid agents are dropped from aggregation with a stderr log.",
    )
    parser.add_argument("--url", required=True, help="Store URL")
    parser.add_argument("--platform", default="shopify", help="Platform name")
    parser.add_argument("--output", default="ecom-report.pdf", help="Output PDF path")
    parser.add_argument("--brand-color", default="#1d4ed8", help="Brand primary color hex (e.g. #e63329)")
    parser.add_argument("--store-name", default=None, help="Store display name (overrides auto-detection)")
    parser.add_argument("--logo", default=None, help="Logo image: file path or URL")
    parser.add_argument("--store-description", default=None, help="Short store description/tagline")
    args = parser.parse_args()

    report_md = Path(args.report).read_text(encoding="utf-8")
    action_plan_md = Path(args.action_plan).read_text(encoding="utf-8")

    if args.agent_outputs:
        valid_outputs, errors = _load_and_validate_agent_outputs(args.agent_outputs)
        for err in errors:
            print(f"[ecom_report] dropping malformed agent output: {err}", file=sys.stderr)
        if not valid_outputs:
            print(
                "[ecom_report] every agent payload failed validation; cannot aggregate.",
                file=sys.stderr,
            )
            sys.exit(2)
        agg = aggregate(valid_outputs)
        scores = {
            "overall": agg["overall"],
            "categories": agg["categories"],
        }
        disc = discoverability_score(valid_outputs)
        if disc is not None:
            scores["discoverability"] = disc
        if agg["skipped_categories"]:
            print(
                "[ecom_report] excluded categories (no valid agent output): "
                + ", ".join(agg["skipped_categories"]),
                file=sys.stderr,
            )
        print(
            f"[ecom_report] aggregated {len(valid_outputs)} valid agent(s); "
            f"denominator weight used = {agg['weight_used']}",
            file=sys.stderr,
        )
    else:
        scores = json.loads(args.scores)
    audit_date = date.today().strftime("%B %d, %Y")

    logo_b64 = _load_logo(args.logo) if args.logo else None

    html = build_html(
        report_md,
        action_plan_md,
        scores,
        args.url,
        args.platform,
        audit_date,
        brand_color=args.brand_color,
        logo_b64=logo_b64,
        store_name_override=args.store_name,
        store_description=args.store_description,
    )
    generate_pdf(html, args.output)


if __name__ == "__main__":
    main()
