"""CI-equivalent checks implemented as tests.

These replace the project-specific CI steps described in #27:
- Schema validation of data/baselines.json (blocking)
- Disclaimer block presence check (blocking)
- Staleness advisory (non-blocking, informational)
- robots.txt presence check
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from src.assembler.staleness import compute_staleness
from src.assembler.validator import validate_kb
from src.llm_consensus.schema_gen import generate_schema

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_baselines_json_schema_valid() -> None:
    """CI gate: data/baselines.json validates against generated schema."""
    schema = generate_schema()
    kb_path = PROJECT_ROOT / "data" / "baselines.json"
    kb = json.loads(kb_path.read_text(encoding="utf-8"))
    validate(kb, schema)


def test_baselines_json_disclaimer_present() -> None:
    """CI gate: disclaimer block present and substantive."""
    kb_path = PROJECT_ROOT / "data" / "baselines.json"
    kb = json.loads(kb_path.read_text(encoding="utf-8"))
    errors = validate_kb(kb)
    assert errors == [], f"Validation errors: {errors}"


def test_staleness_advisory() -> None:
    """CI advisory: report stale attributes (non-blocking)."""
    kb_path = PROJECT_ROOT / "data" / "baselines.json"
    kb = json.loads(kb_path.read_text(encoding="utf-8"))
    result = compute_staleness(kb)
    if result["stale_count"] > 0:
        print(f"ADVISORY: {result['stale_count']} stale attribute(s) detected")
        for entry in result["stale_attributes"]:
            print(f"  {entry['baseline_id']}/{entry['attribute_id']}: "
                  f"{entry['days_overdue']} days overdue")


def test_robots_txt_exists() -> None:
    """CI gate: robots.txt must be present in web/."""
    robots = PROJECT_ROOT / "web" / "robots.txt"
    assert robots.exists(), "web/robots.txt is missing"
    content = robots.read_text(encoding="utf-8")
    assert "GPTBot" in content
    assert "ClaudeBot" in content
    assert "Disallow" in content
