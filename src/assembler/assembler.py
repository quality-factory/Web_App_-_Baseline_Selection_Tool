"""Assembler — merges tier outputs into the knowledge base.

Implements the merge logic: new baselines are added, existing baselines
are replaced, and unaffected baselines are preserved. The disclaimer
block is embedded from the canonical source (FR-C08(f)).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
KB_PATH = DATA_DIR / "baselines.json"

DISCLAIMER_TEXT = (
    "This tool is a decision-support aid only. It does not constitute "
    "professional security advice. The Factory Owner makes no warranties "
    "regarding the accuracy, completeness, or currentness of the information "
    "presented. Attribute values are sourced from third-party publications "
    "and may not reflect the current state of the referenced baselines. "
    "Users are solely responsible for verifying the applicability of any "
    "baseline to their specific environment and for all implementation "
    "decisions. The Factory Owner accepts no liability for damages arising "
    "from reliance on this tool."
)


def assemble(
    new_baselines: list[dict[str, Any]],
    *,
    kb_path: Path | None = None,
    generated_by: str = "assembler",
) -> dict[str, Any]:
    """Merge new baseline data into the existing knowledge base.

    Args:
        new_baselines: List of baseline dicts to add or replace.
        kb_path: Path to existing ``baselines.json``. Defaults to ``data/baselines.json``.
        generated_by: Pipeline version identifier.

    Returns:
        The merged knowledge base dict (not yet written to disk).
    """
    path = kb_path or KB_PATH

    if path.exists():
        kb: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    else:
        kb = _empty_kb()

    # Index existing baselines by ID
    existing_by_id = {b["baseline_id"]: b for b in kb.get("baselines", [])}

    # Merge: replace existing, add new
    for baseline in new_baselines:
        existing_by_id[baseline["baseline_id"]] = baseline

    kb["baselines"] = list(existing_by_id.values())
    kb["meta"]["baseline_count"] = len(kb["baselines"])
    kb["meta"]["generated_by"] = generated_by

    # Ensure disclaimer block is present
    kb["disclaimer"] = {
        "version": "1",
        "text": DISCLAIMER_TEXT,
        "attribution": "Quality Factory",
    }

    return kb


def merge_baseline(
    kb: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Merge a single baseline into a KB dict.

    Args:
        kb: Existing knowledge base.
        baseline: New baseline to add or replace.

    Returns:
        Updated KB dict.
    """
    existing = {b["baseline_id"]: b for b in kb.get("baselines", [])}
    existing[baseline["baseline_id"]] = baseline
    kb["baselines"] = list(existing.values())
    kb["meta"]["baseline_count"] = len(kb["baselines"])
    return kb


def _empty_kb() -> dict[str, Any]:
    """Return a minimal empty KB structure."""
    from ..llm_consensus.schema_gen import load_data_dictionary

    catalogue = load_data_dictionary()
    attr_schema = [
        {
            "attribute_id": a["attribute_id"],
            "label": a["label"],
            "category": a["category"],
            "data_type": a["data_type"],
            "objective_subjective": a["objective_subjective"],
            "stability": a["stability"],
            "obtainability": a["obtainability"],
            "enum_values": a["enum_values"],
            "rubric": a["rubric"],
        }
        for a in catalogue
    ]

    return {
        "meta": {
            "schema_version": "1",
            "generated_at": "",
            "generated_by": "",
            "baseline_count": 0,
            "tenant_id": "default",
        },
        "disclaimer": {
            "version": "1",
            "text": DISCLAIMER_TEXT,
            "attribution": "Quality Factory",
        },
        "attribute_schema": attr_schema,
        "baselines": [],
    }
