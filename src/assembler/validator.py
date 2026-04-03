"""Validator — schema conformance + disclaimer presence check (FR-C05).

Validates the assembled knowledge base against the generated JSON Schema
and checks for the presence of the required disclaimer block.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "schemas" / "baselines.schema.json"
)


def validate_kb(
    kb: dict[str, Any],
    *,
    schema_path: Path | None = None,
) -> list[str]:
    """Validate the knowledge base against the JSON Schema.

    Args:
        kb: Knowledge base dict.
        schema_path: Override path to the schema file.

    Returns:
        List of validation error messages. Empty list means valid.
    """
    path = schema_path or SCHEMA_PATH
    schema = json.loads(path.read_text(encoding="utf-8"))

    errors: list[str] = []

    # Schema validation
    try:
        validate(kb, schema)
    except ValidationError as exc:
        errors.append(f"Schema validation failed: {exc.message}")
        # Collect additional errors
        from jsonschema import Draft202012Validator

        validator = Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(kb), key=lambda e: list(e.path)):
            if str(error.message) != str(exc.message):
                errors.append(f"  {'.'.join(str(p) for p in error.path)}: {error.message}")

    # Disclaimer presence check
    disclaimer_errors = _check_disclaimer(kb)
    errors.extend(disclaimer_errors)

    return errors


def _check_disclaimer(kb: dict[str, Any]) -> list[str]:
    """Check the disclaimer block meets requirements."""
    errors: list[str] = []

    disclaimer = kb.get("disclaimer")
    if disclaimer is None:
        errors.append("Disclaimer block is missing")
        return errors

    if not isinstance(disclaimer, dict):
        errors.append("Disclaimer block is not a dict")
        return errors

    text = disclaimer.get("text", "")
    if not text or len(text.strip()) < 50:
        errors.append(
            "Disclaimer text is missing or too short (must be substantive)"
        )

    attribution = disclaimer.get("attribution", "")
    if not attribution:
        errors.append("Disclaimer attribution is missing")

    version = disclaimer.get("version", "")
    if not version:
        errors.append("Disclaimer version is missing")

    return errors
