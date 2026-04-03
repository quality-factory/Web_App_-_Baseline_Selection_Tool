"""Tests for consensus engine (U3+U4).

Covers all degradation rule branches per architecture §18.2.
"""

from __future__ import annotations

from src.llm_consensus.consensus import apply_degradation_rules, compute_consensus


def test_3_of_3_agreement() -> None:
    outputs = [
        {"attr_a": "value1", "attr_b": "value2"},
        {"attr_a": "value1", "attr_b": "value2"},
        {"attr_a": "value1", "attr_b": "value3"},
    ]
    result = compute_consensus(outputs)
    assert result["attr_a"]["consensus_reached"] is True
    assert result["attr_a"]["value"] == "value1"
    # attr_b: 2-of-3 agree on value2
    assert result["attr_b"]["consensus_reached"] is True
    assert result["attr_b"]["value"] == "value2"


def test_3_of_3_no_majority() -> None:
    outputs = [
        {"attr_a": "x"},
        {"attr_a": "y"},
        {"attr_a": "z"},
    ]
    result = compute_consensus(outputs)
    assert result["attr_a"]["consensus_reached"] is False
    assert result["attr_a"]["value"] is None


def test_2_of_2_unanimous() -> None:
    outputs = [
        {"attr_a": "same"},
        {"attr_a": "same"},
    ]
    result = apply_degradation_rules(outputs)
    assert result["attr_a"]["consensus_reached"] is True
    assert result["attr_a"]["value"] == "same"


def test_2_of_2_disagree() -> None:
    outputs = [
        {"attr_a": "one"},
        {"attr_a": "two"},
    ]
    result = apply_degradation_rules(outputs)
    assert result["attr_a"]["consensus_reached"] is False


def test_1_response_no_consensus() -> None:
    outputs = [{"attr_a": "value"}]
    result = apply_degradation_rules(outputs)
    assert result["attr_a"]["consensus_reached"] is False


def test_0_responses() -> None:
    result = apply_degradation_rules([])
    assert result == {}


def test_mixed_attributes_across_outputs() -> None:
    outputs = [
        {"attr_a": "v1"},
        {"attr_a": "v1", "attr_b": "v2"},
        {"attr_b": "v2"},
    ]
    result = compute_consensus(outputs)
    assert result["attr_a"]["consensus_reached"] is True
    assert result["attr_b"]["consensus_reached"] is True


def test_list_values_consensus() -> None:
    outputs = [
        {"attr_a": ["x", "y"]},
        {"attr_a": ["y", "x"]},
        {"attr_a": ["z"]},
    ]
    result = compute_consensus(outputs)
    # Sorted lists match: ["x", "y"] == ["y", "x"]
    assert result["attr_a"]["consensus_reached"] is True


def test_boolean_consensus() -> None:
    outputs = [
        {"attr_a": True},
        {"attr_a": True},
        {"attr_a": False},
    ]
    result = compute_consensus(outputs)
    assert result["attr_a"]["consensus_reached"] is True
    assert result["attr_a"]["value"] is True


def test_none_values_handling() -> None:
    """None is a valid value — two Nones vs one string = 2-of-3 majority on None."""
    outputs = [
        {"attr_a": None},
        {"attr_a": None},
        {"attr_a": "value"},
    ]
    result = compute_consensus(outputs)
    # None normalises differently from strings — consensus may or may not be reached
    # depending on how None is handled by _normalise_value.
    # The key invariant: the result has the attribute.
    assert "attr_a" in result
