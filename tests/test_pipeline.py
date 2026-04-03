"""Tests for pipeline orchestrator (U5).

LLM adapters are mocked per AGENTS.md §Test external call isolation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.llm_consensus.adapters.base import AdapterError, BaseAdapter
from src.llm_consensus.pipeline import (
    build_provenance,
    load_sources,
    qualify_models,
    render_prompt,
    run_pipeline,
    _compute_prompt_version,
)


class MockAdapter(BaseAdapter):
    def __init__(self, name: str, output: dict[str, Any] | None = None, qualify_result: bool = True) -> None:
        self._name = name
        self._output = output
        self._qualify_result = qualify_result

    def extract(self, prompt: str, schema: dict[str, Any], *, timeout: float = 120.0) -> dict[str, Any]:
        if self._output is None:
            raise AdapterError("mock failure")
        return self._output

    def qualify(self, schema: dict[str, Any]) -> bool:
        return self._qualify_result

    @property
    def provider(self) -> str:
        return "mock"

    @property
    def model_id(self) -> str:
        return self._name

    @property
    def model_version(self) -> str:
        return "1.0"


def test_load_sources() -> None:
    sources = load_sources()
    assert "disa_stig" in sources
    assert "urls" in sources["disa_stig"]
    assert "display_name" in sources["disa_stig"]


def test_render_prompt(tmp_path: Path) -> None:
    template = tmp_path / "test.txt"
    template.write_text("ID={{BASELINE_ID}} NAME={{DISPLAY_NAME}} URLS={{SOURCE_URLS}} SCHEMA={{SCHEMA}}")

    result = render_prompt(
        "test_id", "Test Name", ["http://a.com"], {"type": "object"},
        template_path=template,
    )
    assert "test_id" in result
    assert "Test Name" in result
    assert "http://a.com" in result


def test_compute_prompt_version() -> None:
    v1 = _compute_prompt_version("hello")
    v2 = _compute_prompt_version("hello")
    v3 = _compute_prompt_version("different")
    assert v1 == v2
    assert v1 != v3
    assert len(v1) == 8


def test_qualify_models() -> None:
    adapters: list[BaseAdapter] = [
        MockAdapter("good1", qualify_result=True),
        MockAdapter("bad", qualify_result=False),
        MockAdapter("good2", qualify_result=True),
    ]
    qualified = qualify_models(adapters, {})
    assert len(qualified) == 2


def test_build_provenance_success() -> None:
    adapter = MockAdapter("test")
    prov = build_provenance(adapter, {"key": "val"}, "abc12345")
    assert prov["provider"] == "mock"
    assert prov["model_id"] == "test"
    assert prov["output"] == {"key": "val"}
    assert "successful" in prov["justification"]


def test_build_provenance_failure() -> None:
    adapter = MockAdapter("test")
    prov = build_provenance(adapter, None, "abc12345", error_reason="timeout")
    assert prov["output"] is None
    assert prov["justification"] == "timeout"


def test_run_pipeline_success(tmp_path: Path) -> None:
    # Create sources
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps({
        "test_baseline": {"display_name": "Test", "urls": ["http://example.com"]}
    }))

    # Create prompt template
    prompt_path = tmp_path / "prompt.txt"
    prompt_path.write_text("Extract {{BASELINE_ID}} {{DISPLAY_NAME}} {{SOURCE_URLS}} {{SCHEMA}}")

    output = {"attr_a": "value1"}
    adapters: list[BaseAdapter] = [
        MockAdapter("m1", output=output),
        MockAdapter("m2", output=output),
        MockAdapter("m3", output=output),
    ]

    result = run_pipeline(
        "test_baseline", adapters, {"type": "object"},
        sources_path=sources_path,
        prompt_template_path=prompt_path,
    )
    assert result["baseline_id"] == "test_baseline"
    assert result["consensus"]["attr_a"]["consensus_reached"] is True
    assert len(result["provenance"]) == 3


def test_run_pipeline_insufficient_models(tmp_path: Path) -> None:
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps({
        "test": {"display_name": "Test", "urls": ["http://example.com"]}
    }))
    prompt_path = tmp_path / "prompt.txt"
    prompt_path.write_text("{{BASELINE_ID}} {{DISPLAY_NAME}} {{SOURCE_URLS}} {{SCHEMA}}")

    adapters: list[BaseAdapter] = [MockAdapter("m1", qualify_result=False)]

    with pytest.raises(RuntimeError, match="qualified"):
        run_pipeline(
            "test", adapters, {},
            sources_path=sources_path,
            prompt_template_path=prompt_path,
        )


def test_run_pipeline_unknown_baseline(tmp_path: Path) -> None:
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(json.dumps({}))
    prompt_path = tmp_path / "prompt.txt"
    prompt_path.write_text("{{BASELINE_ID}} {{DISPLAY_NAME}} {{SOURCE_URLS}} {{SCHEMA}}")

    with pytest.raises(RuntimeError, match="not found"):
        run_pipeline("unknown", [], {}, sources_path=sources_path, prompt_template_path=prompt_path)
