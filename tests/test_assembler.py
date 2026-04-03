"""Tests for assembler, validator, and staleness (U7+U8+U9)."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from src.assembler.assembler import assemble, merge_baseline
from src.assembler.staleness import compute_staleness
from src.assembler.validator import validate_kb


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def empty_kb_path(tmp_path: Path) -> Path:
    kb_path = Path(__file__).resolve().parent.parent / "data" / "baselines.json"
    # Copy empty KB to tmp
    target = tmp_path / "baselines.json"
    target.write_text(kb_path.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def _make_baseline(baseline_id: str = "test") -> dict[str, Any]:
    return {
        "baseline_id": baseline_id,
        "tenant_id": "default",
        "display_name": f"Test Baseline {baseline_id}",
        "issuer": "Test Org",
        "baseline_type": "technical_benchmark",
        "attributes": {},
    }


# ── Assembler ────────────────────────────────────────────────────────────

class TestAssembler:
    def test_assemble_adds_new_baseline(self, empty_kb_path: Path) -> None:
        result = assemble([_make_baseline()], kb_path=empty_kb_path)
        assert len(result["baselines"]) == 1
        assert result["meta"]["baseline_count"] == 1

    def test_assemble_replaces_existing(self, empty_kb_path: Path) -> None:
        b1 = _make_baseline("a")
        b1["issuer"] = "Original"
        result = assemble([b1], kb_path=empty_kb_path)

        # Write and re-assemble with replacement
        empty_kb_path.write_text(json.dumps(result), encoding="utf-8")
        b1_updated = _make_baseline("a")
        b1_updated["issuer"] = "Updated"
        result2 = assemble([b1_updated], kb_path=empty_kb_path)
        assert len(result2["baselines"]) == 1
        assert result2["baselines"][0]["issuer"] == "Updated"

    def test_assemble_preserves_unaffected(self, empty_kb_path: Path) -> None:
        result = assemble([_make_baseline("a"), _make_baseline("b")], kb_path=empty_kb_path)
        empty_kb_path.write_text(json.dumps(result), encoding="utf-8")

        result2 = assemble([_make_baseline("c")], kb_path=empty_kb_path)
        assert len(result2["baselines"]) == 3
        ids = {b["baseline_id"] for b in result2["baselines"]}
        assert ids == {"a", "b", "c"}

    def test_assemble_disclaimer_present(self, empty_kb_path: Path) -> None:
        result = assemble([], kb_path=empty_kb_path)
        assert result["disclaimer"]["text"]
        assert result["disclaimer"]["attribution"] == "Quality Factory"

    def test_merge_baseline_function(self) -> None:
        kb: dict[str, Any] = {"baselines": [_make_baseline("a")], "meta": {"baseline_count": 1}}
        updated = merge_baseline(kb, _make_baseline("b"))
        assert len(updated["baselines"]) == 2


# ── Validator ────────────────────────────────────────────────────────────

class TestValidator:
    def test_valid_kb(self) -> None:
        kb_path = Path(__file__).resolve().parent.parent / "data" / "baselines.json"
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        errors = validate_kb(kb)
        assert errors == []

    def test_missing_disclaimer(self) -> None:
        kb: dict[str, Any] = {
            "meta": {
                "schema_version": "1",
                "generated_at": "2026-01-01T00:00:00Z",
                "generated_by": "test",
                "baseline_count": 0,
                "tenant_id": "default",
            },
            "attribute_schema": [],
            "baselines": [],
        }
        errors = validate_kb(kb)
        assert any("disclaimer" in e.lower() or "Disclaimer" in e for e in errors)

    def test_empty_disclaimer_text(self) -> None:
        kb_path = Path(__file__).resolve().parent.parent / "data" / "baselines.json"
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        kb["disclaimer"]["text"] = ""
        errors = validate_kb(kb)
        assert any("text" in e.lower() for e in errors)


# ── Staleness ────────────────────────────────────────────────────────────

class TestStaleness:
    def test_no_stale_empty_kb(self) -> None:
        kb: dict[str, Any] = {"baselines": []}
        result = compute_staleness(kb)
        assert result["stale_count"] == 0
        assert result["stale_attributes"] == []

    def test_stale_attribute_detected(self) -> None:
        review_date = (date.today() - timedelta(days=400)).isoformat()
        kb: dict[str, Any] = {
            "baselines": [{
                "baseline_id": "test",
                "attributes": {
                    "attr1": {
                        "review_date": review_date,
                        "ttl_days": 365,
                    }
                }
            }]
        }
        result = compute_staleness(kb)
        assert result["stale_count"] == 1
        assert result["stale_attributes"][0]["days_overdue"] > 0

    def test_not_stale_within_ttl(self) -> None:
        review_date = date.today().isoformat()
        kb: dict[str, Any] = {
            "baselines": [{
                "baseline_id": "test",
                "attributes": {
                    "attr1": {
                        "review_date": review_date,
                        "ttl_days": 365,
                    }
                }
            }]
        }
        result = compute_staleness(kb)
        assert result["stale_count"] == 0

    def test_boundary_exactly_at_ttl(self) -> None:
        review_date = (date.today() - timedelta(days=365)).isoformat()
        kb: dict[str, Any] = {
            "baselines": [{
                "baseline_id": "test",
                "attributes": {
                    "attr1": {
                        "review_date": review_date,
                        "ttl_days": 365,
                    }
                }
            }]
        }
        result = compute_staleness(kb)
        # Exactly at TTL = not overdue (0 days overdue is not > 0)
        assert result["stale_count"] == 0
