#!/usr/bin/env python3
"""
ecom_report.py — Generate a professional A4 PDF e-commerce audit report.

Usage:
    python ecom_report.py \
        --report ECOM-AUDIT-REPORT.md \
        --action-plan ACTION-PLAN.md \
        --scores '{"overall": 41, "categories": {...}}' \
        --url https://example.com \
        --platform shopify \
        --output ecom-report.pdf

Dependencies: weasyprint, matplotlib, pillow
"""

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


def _score_color(score: int) -> str:
    if score >= 70:
        return "#22c55e"   # green
    if score >= 50:
        return "#f59e0b"   # amber
    if score >= 30:
        return "#f97316"   # orange
    return "#ef4444"       # red


def _score_label(score: int) -> str:
    if score >= 80:
        return "GOOD"
    if score >= 60:
        return "FAIR"
    if score >= 40:
        return "POOR"
    return "CRITICAL"


def build_score_chart(scores: dict) -> str:
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


def build_gauge_svg(score: int) -> str:
    """Build an SVG gauge for the overall score."""
    color = _score_color(score)
    label = _score_label(score)
    pct = score / 100
    # Simple arc gauge using SVG path
    r = 70
    cx, cy = 90, 90
    start_angle = 210
    end_angle = start_angle - pct * 240

    def polar(angle_deg: float, radius: float):
        import math
        rad = math.radians(angle_deg)
        return cx + radius * math.cos(rad), cy - radius * math.sin(rad)

    x1, y1 = polar(start_angle, r)
    x2, y2 = polar(end_angle, r)
    large = 1 if (start_angle - end_angle) > 180 else 0

    arc_bg_x, arc_bg_y = polar(start_angle - 240, r)
    return f"""<svg width="180" height="120" viewBox="0 0 180 120" xmlns="http://www.w3.org/2000/svg">
  <path d="M {polar(210, r)[0]:.1f} {polar(210, r)[1]:.1f} A {r} {r} 0 1 0 {polar(-30, r)[0]:.1f} {polar(-30, r)[1]:.1f}"
        fill="none" stroke="#f3f4f6" stroke-width="12" stroke-linecap="round"/>
  <path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 0 {x2:.1f} {y2:.1f}"
        fill="none" stroke="{color}" stroke-width="12" stroke-linecap="round"/>
  <text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="32" font-weight="bold" fill="{color}">{score}</text>
  <text x="{cx}" y="{cy + 26}" text-anchor="middle" font-size="10" fill="#9ca3af">/100</text>
  <text x="{cx}" y="{cy + 42}" text-anchor="middle" font-size="9" font-weight="bold" fill="{color}">{label}</text>
</svg>"""


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


def _build_css() -> str:
    return """
    @page {
        size: A4;
        margin: 20mm 18mm 20mm 18mm;
        @bottom-center {
            content: "Claude ECOM Audit Suite · " string(store-name) " · Page " counter(page);
            font-size: 8pt;
            color: #9ca3af;
        }
    }
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 10pt;
        color: #111827;
        line-height: 1.6;
        margin: 0;
    }
    .cover {
        page-break-after: always;
        text-align: center;
        padding-top: 60px;
    }
    .cover-title {
        font-size: 36pt;
        font-weight: bold;
        color: #111827;
        margin-bottom: 8px;
    }
    .cover-subtitle {
        font-size: 14pt;
        color: #6b7280;
        margin-bottom: 40px;
    }
    .cover-meta {
        display: flex;
        justify-content: center;
        gap: 40px;
        font-size: 10pt;
        color: #6b7280;
        border-top: 1px solid #e5e7eb;
        border-bottom: 1px solid #e5e7eb;
        padding: 16px 0;
        margin: 0 auto;
        width: 80%;
    }
    .cover-meta strong { color: #111827; }
    .score-dashboard {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 20px 0;
        justify-content: center;
    }
    .score-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        min-width: 100px;
    }
    .score-card .val {
        font-size: 22pt;
        font-weight: bold;
    }
    .score-card .lbl {
        font-size: 8pt;
        color: #6b7280;
        margin-top: 2px;
    }
    .critical-box {
        background: #fff1f2;
        border-left: 4px solid #ef4444;
        border-radius: 4px;
        padding: 14px 18px;
        margin: 20px 0;
    }
    .critical-box h3 { color: #b91c1c; margin: 0 0 8px 0; font-size: 11pt; }
    h1 { font-size: 20pt; color: #111827; border-bottom: 2px solid #e5e7eb; padding-bottom: 6px; margin-top: 30px; }
    h2 { font-size: 14pt; color: #1d4ed8; margin-top: 24px; }
    h3 { font-size: 11pt; color: #374151; margin-top: 16px; }
    h4 { font-size: 10pt; color: #6b7280; margin-top: 12px; }
    table.audit-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 9pt;
    }
    table.audit-table th {
        background: #1d4ed8;
        color: white;
        padding: 7px 10px;
        text-align: left;
        font-weight: 600;
    }
    table.audit-table td {
        padding: 6px 10px;
        border-bottom: 1px solid #f3f4f6;
    }
    table.audit-table tr:nth-child(even) td { background: #f9fafb; }
    pre {
        background: #1e293b;
        color: #e2e8f0;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 8pt;
        overflow-wrap: break-word;
        white-space: pre-wrap;
        margin: 12px 0;
    }
    code {
        background: #f1f5f9;
        color: #0f172a;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 8.5pt;
    }
    pre code { background: none; color: inherit; padding: 0; }
    ul { padding-left: 20px; }
    li { margin-bottom: 4px; }
    ul.checklist { list-style: none; padding-left: 0; }
    ul.checklist li { padding: 4px 0; border-bottom: 1px solid #f3f4f6; }
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
    .page-break { page-break-before: always; }
    .footer-note { font-size: 8pt; color: #9ca3af; text-align: center; margin-top: 40px; }
    """


def build_html(
    report_md: str,
    action_plan_md: str,
    scores: dict,
    url: str,
    platform: str,
    audit_date: str,
) -> str:
    """Build full A4 HTML document from markdown content and scores."""
    overall = scores.get("overall", 0)
    categories = scores.get("categories", {})
    gauge_svg = build_gauge_svg(overall)
    chart_b64 = build_score_chart(categories) if categories else None
    store_name = url.replace("https://", "").replace("http://", "").split("/")[0]

    # Cover page
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
      <div class="cover-title">{store_name}</div>
      <div class="cover-subtitle">ECOM Audit Report</div>
      <div class="cover-meta">
        <div><strong>Site</strong><br>{url}</div>
        <div><strong>Platform</strong><br>{platform.title()}</div>
        <div><strong>Date</strong><br>{audit_date}</div>
        <div><strong>Audited By</strong><br>Claude ECOM Audit Suite</div>
      </div>
      <br>
      <div style="margin: 30px auto; width: 200px;">
        {gauge_svg}
      </div>
      <div style="font-size:11pt; color:#6b7280; margin-bottom: 20px;">Overall ECOM Health Score</div>
      <div class="score-dashboard">{score_cards}</div>
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
<style>{_build_css()}</style>
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


def main():
    parser = argparse.ArgumentParser(description="Generate ECOM audit PDF report")
    parser.add_argument("--report", required=True, help="Path to ECOM-AUDIT-REPORT.md")
    parser.add_argument("--action-plan", required=True, help="Path to ACTION-PLAN.md")
    parser.add_argument("--scores", required=True, help='JSON scores: {"overall": 41, "categories": {...}}')
    parser.add_argument("--url", required=True, help="Store URL")
    parser.add_argument("--platform", default="shopify", help="Platform name")
    parser.add_argument("--output", default="ecom-report.pdf", help="Output PDF path")
    args = parser.parse_args()

    report_md = Path(args.report).read_text(encoding="utf-8")
    action_plan_md = Path(args.action_plan).read_text(encoding="utf-8")
    scores = json.loads(args.scores)
    audit_date = date.today().strftime("%B %d, %Y")

    html = build_html(report_md, action_plan_md, scores, args.url, args.platform, audit_date)
    generate_pdf(html, args.output)


if __name__ == "__main__":
    main()
