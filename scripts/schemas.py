#!/usr/bin/env python3
"""
schemas.py — Pydantic models and aggregation helpers for agent outputs.

All ecom-* agents must return JSON conforming to ``AgentOutput``. The
report generator validates each agent's JSON before aggregation. If an
agent returns malformed JSON (e.g. ``"score": "N/A"`` or ``null``),
its output is rejected and excluded from the weighted score, and its
weight is removed from the denominator so the remaining agents still
sum to 1.0.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------- #
# Schema                                                                      #
# --------------------------------------------------------------------------- #


class AgentOutput(BaseModel):
    """Canonical shape returned by every ecom-* agent.

    Extra fields are permitted (`extra="allow"`) so agent-specific
    payloads (e.g. ecom-trust's market/reviews/policies block) don't
    fail validation.
    """

    model_config = ConfigDict(extra="allow")

    agent: str = Field(..., min_length=1)
    score: int = Field(..., ge=0, le=100)
    critical: list[str] = Field(default_factory=list)
    high: list[str] = Field(default_factory=list)
    medium: list[str] = Field(default_factory=list)
    low: list[str] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list)
    notes: str = ""


# --------------------------------------------------------------------------- #
# Weights — must match agents/ecom-report.md and skills/ecom/SKILL.md         #
# --------------------------------------------------------------------------- #

# Category → agents that contribute to it (averaged when more than one).
CATEGORY_AGENTS: dict[str, tuple[str, ...]] = {
    "First Impression":              ("ecom-header", "ecom-hero"),
    "Product Presentation":          ("ecom-products",),
    "Conversion Rate Optimization":  ("ecom-cro", "ecom-cart"),
    "Offer & Pricing Strategy":      ("ecom-offers", "ecom-upsells"),
    "Trust & Social Proof":          ("ecom-trust",),
    "Mobile Experience":             ("ecom-mobile",),
    "Performance (CWV)":             ("ecom-performance",),
    "Copy & Messaging":              ("ecom-copy",),
    "Retention & Email":             ("ecom-retention",),
}

CATEGORY_WEIGHTS: dict[str, float] = {
    "Product Presentation":          0.18,
    "Conversion Rate Optimization":  0.18,
    "Offer & Pricing Strategy":      0.13,
    "Trust & Social Proof":          0.12,
    "Mobile Experience":             0.10,
    "Performance (CWV)":             0.10,
    "First Impression":              0.08,
    "Copy & Messaging":              0.06,
    "Retention & Email":             0.05,
}

# Agents whose score does NOT feed the ECOM Health Score:
#   - ecom-seo: reported separately as the Discoverability Score
#   - ecom-competitors: produces gap analysis, not a health-score input
EXCLUDED_FROM_HEALTH: frozenset[str] = frozenset({"ecom-seo", "ecom-competitors"})


# --------------------------------------------------------------------------- #
# Validation                                                                  #
# --------------------------------------------------------------------------- #


def validate_agent_payload(raw: Any) -> tuple[AgentOutput | None, str | None]:
    """Validate a single agent's JSON payload.

    Returns (output, None) on success or (None, error_message) on failure.
    Never raises. The error message includes the agent name (if extractable)
    and the offending field so the caller can log it cleanly.
    """
    if not isinstance(raw, dict):
        return None, f"agent payload must be a JSON object, got {type(raw).__name__}"

    agent_hint = raw.get("agent") if isinstance(raw.get("agent"), str) else "<unknown>"

    try:
        return AgentOutput.model_validate(raw), None
    except Exception as exc:  # pydantic.ValidationError
        details = []
        errors = getattr(exc, "errors", None)
        if callable(errors):
            for err in errors():
                loc = ".".join(str(p) for p in err.get("loc", ()))
                msg = err.get("msg", "invalid")
                details.append(f"{loc}={raw.get(loc)!r} ({msg})")
        suffix = "; ".join(details) if details else str(exc)
        return None, f"agent {agent_hint!r}: {suffix}"


# --------------------------------------------------------------------------- #
# Aggregation                                                                 #
# --------------------------------------------------------------------------- #


def aggregate(
    valid_outputs: list[AgentOutput],
) -> dict[str, Any]:
    """Compute the overall ECOM Health Score and per-category breakdown.

    Categories whose contributing agents are all invalid or missing are
    excluded from the denominator. The remaining weights are renormalized
    so a partial run still produces a defensible score on the 0-100 scale.

    Returns:
        {
          "overall": int,                  # 0-100
          "categories": {name: int, ...},  # only those that scored
          "weight_used": float,            # sum of weights that contributed
          "skipped_categories": [name, ...]
        }
    """
    by_agent = {a.agent: a for a in valid_outputs}

    category_scores: dict[str, int] = {}
    weight_used = 0.0
    weighted_sum = 0.0
    skipped: list[str] = []

    for category, agent_names in CATEGORY_AGENTS.items():
        weight = CATEGORY_WEIGHTS[category]
        present = [by_agent[name].score for name in agent_names if name in by_agent]
        if not present:
            skipped.append(category)
            continue
        cat_score = round(sum(present) / len(present))
        category_scores[category] = cat_score
        weighted_sum += cat_score * weight
        weight_used += weight

    if weight_used == 0:
        overall = 0
    else:
        overall = round(weighted_sum / weight_used)

    return {
        "overall": overall,
        "categories": category_scores,
        "weight_used": round(weight_used, 4),
        "skipped_categories": skipped,
    }


def discoverability_score(valid_outputs: list[AgentOutput]) -> int | None:
    """Pull the ecom-seo score, if present. Reported separately."""
    for output in valid_outputs:
        if output.agent == "ecom-seo":
            return output.score
    return None
