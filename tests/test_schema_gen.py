"""Tests for schema generation (U1+U2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

from src.llm_consensus.schema_gen import (
    generate_schema,
    load_data_dictionary,
)


def test_load_data_dictionary_returns_45_attributes() -> None:
    catalogue = load_data_dictionary()
    assert len(catalogue) == 45


def test_load_data_dictionary_all_have_required_fields() -> None:
    required = {"attribute_id", "label", "category", "data_type",
                "objective_subjective", "stability", "obtainability"}
    for attr in load_data_dictionary():
        assert required.issubset(attr.keys()), f"Missing fields in {attr['attribute_id']}"


def test_load_data_dictionary_unique_ids() -> None:
    ids = [a["attribute_id"] for a in load_data_dictionary()]
    assert len(ids) == len(set(ids))


def test_generate_schema_structure() -> None:
    schema = generate_schema()
    assert schema["type"] == "object"
    assert "meta" in schema["properties"]
    assert "disclaimer" in schema["properties"]
    assert "attribute_schema" in schema["properties"]
    assert "baselines" in schema["properties"]


def test_empty_kb_validates_against_schema() -> None:
    schema = generate_schema()
    kb_path = Path(__file__).resolve().parent.parent / "data" / "baselines.json"
    kb = json.loads(kb_path.read_text(encoding="utf-8"))
    validate(kb, schema)


def test_schema_rejects_missing_disclaimer() -> None:
    schema = generate_schema()
    kb = {
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
    with pytest.raises(ValidationError):
        validate(kb, schema)


def test_schema_rejects_invalid_baseline() -> None:
    schema = generate_schema()
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

    kb = {
        "meta": {
            "schema_version": "1",
            "generated_at": "2026-01-01T00:00:00Z",
            "generated_by": "test",
            "baseline_count": 1,
            "tenant_id": "default",
        },
        "disclaimer": {"version": "1", "text": "Test disclaimer.", "attribution": "Test"},
        "attribute_schema": attr_schema,
        "baselines": [
            {"baseline_id": "test", "extra_field": True}
        ],
    }
    with pytest.raises(ValidationError):
        validate(kb, schema)


def test_generated_schema_file_exists() -> None:
    path = Path(__file__).resolve().parent.parent / "src" / "schemas" / "baselines.schema.json"
    assert path.exists()
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert "$schema" in schema
