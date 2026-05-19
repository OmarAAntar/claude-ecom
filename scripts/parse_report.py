#!/usr/bin/env python3
"""
parse_report.py — Extract score table and findings from a prior
ECOM-AUDIT-REPORT.md, so /ecom recheck can compute deltas.

Usage:
    python parse_report.py <path-to-ECOM-AUDIT-REPORT.md>

Output: JSON on stdout with shape:
    {
      "overall_score": <int|null>,
      "overall_tier": <str|null>,
      "discoverability_score": <int|null>,
      "categories": { "First Impression": 38, ... },
      "issues": {
        "critical": [<str>, ...],
        "high":     [<str>, ...],
        "medium":   [<str>, ...],
        "low":      [<str>, ...]
      },
      "source_path": <str>,
      "warnings": [<str>, ...]
    }

Design: defensive — return whatever can be parsed; never raise on a
mildly-malformed report. The recheck flow treats missing fields as
"unknown" and reports that to the user.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCORE_HEADER_RE = re.compile(
    r"^##\s*ECOM\s+Health\s+Score:\s*(\d+)\s*/\s*100\s*(?:—|--|-)?\s*(\w+)?",
    re.IGNORECASE,
)
DISCOVERABILITY_HEADER_RE = re.compile(
    r"^##\s*Discoverability\s+Score:\s*(\d+)\s*/\s*100",
    re.IGNORECASE,
)
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*/\s*100\s*\|")
SEVERITY_BULLET_RE = re.compile(
    r"^\s*-\s*\*?\*?(CRITICAL|HIGH|MEDIUM|LOW)\*?\*?\s*[:\-—]\s*(.+?)\s*$",
    re.IGNORECASE,
)
SEVERITY_HEADER_RE = re.compile(
    r"^##+\s*[^A-Za-z0-9]*\s*(CRITICAL|HIGH|MEDIUM|LOW)\b",
    re.IGNORECASE,
)
BULLET_RE = re.compile(r"^\s*[-*]\s*(?:\[\s\]\s*)?(.+?)\s*$")


def _clean(line: str) -> str:
    """Strip Markdown emphasis and trailing junk from a bullet's text."""
    line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
    line = re.sub(r"\*(.+?)\*", r"\1", line)
    line = re.sub(r"`([^`]+)`", r"\1", line)
    return line.strip().rstrip(".")


def parse(text: str) -> dict:
    out: dict = {
        "overall_score": None,
        "overall_tier": None,
        "discoverability_score": None,
        "categories": {},
        "issues": {"critical": [], "high": [], "medium": [], "low": []},
        "warnings": [],
    }

    current_severity_section: str | None = None
    in_category_table = False

    for raw in text.splitlines():
        line = raw.rstrip()

        if out["overall_score"] is None:
            m = SCORE_HEADER_RE.match(line)
            if m:
                out["overall_score"] = int(m.group(1))
                out["overall_tier"] = (m.group(2) or "").strip() or None
                in_category_table = True
                continue

        if out["discoverability_score"] is None:
            m = DISCOVERABILITY_HEADER_RE.match(line)
            if m:
                out["discoverability_score"] = int(m.group(1))
                continue

        if in_category_table:
            m = TABLE_ROW_RE.match(line)
            if m:
                name = m.group(1).strip()
                if name.lower() in {"category", "score"} or set(name) <= {"-", " "}:
                    continue
                out["categories"][name] = int(m.group(2))
                continue
            if line.startswith("---") or line.startswith("##"):
                in_category_table = False

        # Inline-prefixed bullets like "- CRITICAL: foo"
        m = SEVERITY_BULLET_RE.match(line)
        if m:
            sev = m.group(1).lower()
            out["issues"][sev].append(_clean(m.group(2)))
            continue

        # Section header for a severity bucket (## CRITICAL ...)
        m = SEVERITY_HEADER_RE.match(line)
        if m:
            current_severity_section = m.group(1).lower()
            continue

        # Plain bullet inside a severity section
        if current_severity_section:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                current_severity_section = None
                continue
            bm = BULLET_RE.match(line)
            if bm:
                out["issues"][current_severity_section].append(_clean(bm.group(1)))

    if out["overall_score"] is None:
        out["warnings"].append("Overall ECOM Health Score line not found.")
    if not out["categories"]:
        out["warnings"].append("Category score table not found.")
    if not any(out["issues"].values()):
        out["warnings"].append("No CRITICAL/HIGH/MEDIUM/LOW issues parsed.")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse a prior ECOM audit report.")
    parser.add_argument("path", help="Path to ECOM-AUDIT-REPORT.md")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(json.dumps({"error": f"Report not found: {path}"}))
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")
    result = parse(text)
    result["source_path"] = str(path.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
