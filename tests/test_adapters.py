"""Tests for LLM adapters (U3+U4).

All HTTP calls mocked per AGENTS.md §Test external call isolation.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.llm_consensus.adapters.base import AdapterError, BaseAdapter
from src.llm_consensus.adapters.ollama import OllamaAdapter


class TestBaseAdapter:
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            BaseAdapter()  # type: ignore[abstract]


class TestOllamaAdapter:
    def _make_adapter(self) -> OllamaAdapter:
        return OllamaAdapter("test-model", base_url="http://localhost:11434")

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_extract_success(self, mock_post: MagicMock) -> None:
        adapter = self._make_adapter()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "response": json.dumps({"test": True})
        }
        mock_post.return_value = mock_resp

        schema = {
            "type": "object",
            "properties": {"test": {"type": "boolean"}},
            "required": ["test"],
        }
        result = adapter.extract("test prompt", schema)
        assert result == {"test": True}

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_extract_network_error(self, mock_post: MagicMock) -> None:
        import httpx
        adapter = self._make_adapter()
        mock_post.side_effect = httpx.ConnectError("connection refused")

        with pytest.raises(AdapterError, match="connection refused"):
            adapter.extract("prompt", {"type": "object"})

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_extract_invalid_json(self, mock_post: MagicMock) -> None:
        adapter = self._make_adapter()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"response": "not json{"}
        mock_post.return_value = mock_resp

        with pytest.raises(AdapterError, match="non-JSON"):
            adapter.extract("prompt", {"type": "object"})

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_extract_schema_validation_failure(self, mock_post: MagicMock) -> None:
        adapter = self._make_adapter()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "response": json.dumps({"wrong_field": True})
        }
        mock_post.return_value = mock_resp

        schema = {
            "type": "object",
            "required": ["test"],
            "properties": {"test": {"type": "boolean"}},
        }
        with pytest.raises(AdapterError, match="schema validation"):
            adapter.extract("prompt", schema)

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_qualify_passes(self, mock_post: MagicMock) -> None:
        adapter = self._make_adapter()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "response": json.dumps({"test": True})
        }
        mock_post.return_value = mock_resp

        assert adapter.qualify({}) is True

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_qualify_fails_on_error(self, mock_post: MagicMock) -> None:
        import httpx
        adapter = self._make_adapter()
        mock_post.side_effect = httpx.ConnectError("refused")

        assert adapter.qualify({}) is False

    def test_provider(self) -> None:
        adapter = self._make_adapter()
        assert adapter.provider == "ollama"

    def test_model_id(self) -> None:
        adapter = self._make_adapter()
        assert adapter.model_id == "test-model"

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_model_version_fetched(self, mock_post: MagicMock) -> None:
        adapter = self._make_adapter()
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"modelfile_digest": "abc123def456"}
        mock_post.return_value = mock_resp

        assert adapter.model_version == "abc123def456"

    @patch("src.llm_consensus.adapters.ollama.httpx.post")
    def test_model_version_fallback(self, mock_post: MagicMock) -> None:
        import httpx
        adapter = self._make_adapter()
        mock_post.side_effect = httpx.ConnectError("refused")

        assert adapter.model_version == "unknown"
