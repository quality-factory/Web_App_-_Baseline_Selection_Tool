"""Field-level comparison and majority-rules consensus logic.

Implements the degradation rules from architecture.md §13.6:
- 3 responses: 2-of-3 majority per field
- 2 responses: 2-of-2 unanimous per field
- 0–1 responses: no consensus possible
"""

from __future__ import annotations

from typing import Any


def compute_consensus(
    model_outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute field-level consensus from multiple model outputs.

    Args:
        model_outputs: List of extracted attribute dicts from each model.
            Each dict maps ``attribute_id`` to extracted value.

    Returns:
        Dict mapping ``attribute_id`` to ``{"value": ..., "consensus_reached": bool}``.
        When consensus is not reached, ``value`` is ``None``.
    """
    result = apply_degradation_rules(model_outputs)
    return result


def apply_degradation_rules(
    model_outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply degradation rules based on the number of valid responses.

    Returns:
        Dict mapping ``attribute_id`` to consensus result.
    """
    n = len(model_outputs)

    if n == 0:
        return {}

    # Collect all attribute IDs across all outputs
    all_attribute_ids: set[str] = set()
    for output in model_outputs:
        all_attribute_ids.update(output.keys())

    result: dict[str, Any] = {}

    if n == 1:
        # 0–1 responses: no consensus possible
        for attr_id in all_attribute_ids:
            result[attr_id] = {
                "value": None,
                "consensus_reached": False,
            }
        return result

    for attr_id in sorted(all_attribute_ids):
        values = [
            _normalise_value(output.get(attr_id))
            for output in model_outputs
            if attr_id in output
        ]

        valid_count = len(values)

        if valid_count < 2:
            result[attr_id] = {
                "value": None,
                "consensus_reached": False,
            }
            continue

        if n >= 3 and valid_count >= 2:
            # 2-of-3 majority rule
            consensus_value = _find_majority(values, threshold=2)
        elif n == 2:
            # 2-of-2 unanimous rule
            consensus_value = _find_unanimous(values)
        else:
            consensus_value = None

        if consensus_value is not None:
            result[attr_id] = {
                "value": consensus_value,
                "consensus_reached": True,
            }
        else:
            result[attr_id] = {
                "value": None,
                "consensus_reached": False,
            }

    return result


def _normalise_value(value: Any) -> Any:
    """Normalise a value for comparison purposes.

    Lists are sorted and converted to tuples for hashability.
    Strings are stripped and lowercased.
    """
    if isinstance(value, list):
        return tuple(sorted(str(v).strip().lower() for v in value))
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _find_majority(values: list[Any], *, threshold: int = 2) -> Any | None:
    """Find a value that appears at least *threshold* times."""
    counts: dict[Any, int] = {}
    original: dict[Any, Any] = {}
    for v in values:
        key = _make_hashable(v)
        counts[key] = counts.get(key, 0) + 1
        if key not in original:
            original[key] = v

    for key, count in counts.items():
        if count >= threshold:
            return original[key]
    return None


def _find_unanimous(values: list[Any]) -> Any | None:
    """Return the value if all entries agree, else ``None``."""
    if len(values) < 2:
        return None

    first = _make_hashable(values[0])
    for v in values[1:]:
        if _make_hashable(v) != first:
            return None
    return values[0]


def _make_hashable(value: Any) -> Any:
    """Convert a value to a hashable form for dict keys."""
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return value
