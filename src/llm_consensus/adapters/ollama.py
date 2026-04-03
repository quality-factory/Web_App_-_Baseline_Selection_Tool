"""Ollama adapter — local-first default for the LLM consensus pipeline.

Communicates with a locally running Ollama server via its HTTP API,
using the structured output (JSON schema) mode.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from jsonschema import ValidationError, validate

from .base import AdapterError, BaseAdapter


class OllamaAdapter(BaseAdapter):
    """Adapter for a single Ollama-hosted model."""

    def __init__(
        self,
        model_name: str,
        *,
        base_url: str = "http://localhost:11434",
    ) -> None:
        self._model_name = model_name
        self._base_url = base_url.rstrip("/")
        self._model_version_cache: str | None = None

    # ── BaseAdapter interface ────────────────────────────────────────────

    def extract(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        timeout: float = 120.0,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
            "format": schema,
        }
        try:
            resp = httpx.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise AdapterError(
                f"Ollama request failed for model {self._model_name}: {exc}"
            ) from exc

        body = resp.json()
        raw_text = body.get("response", "")
        try:
            result: dict[str, Any] = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise AdapterError(
                f"Model {self._model_name} returned non-JSON: {raw_text[:200]}"
            ) from exc

        try:
            validate(result, schema)
        except ValidationError as exc:
            raise AdapterError(
                f"Model {self._model_name} output failed schema validation: {exc.message}"
            ) from exc

        return result

    def qualify(self, schema: dict[str, Any]) -> bool:
        """Run a minimal structured output test."""
        test_prompt = (
            "Return a JSON object with a single field 'test' set to true. "
            "Respond ONLY with valid JSON matching the provided schema."
        )
        test_schema: dict[str, Any] = {
            "type": "object",
            "required": ["test"],
            "properties": {"test": {"type": "boolean"}},
            "additionalProperties": False,
        }
        try:
            result = self.extract(test_prompt, test_schema, timeout=30.0)
            return result.get("test") is True
        except AdapterError:
            return False

    @property
    def provider(self) -> str:
        return "ollama"

    @property
    def model_id(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        if self._model_version_cache is None:
            self._model_version_cache = self._fetch_version()
        return self._model_version_cache

    # ── Internal ─────────────────────────────────────────────────────────

    def _fetch_version(self) -> str:
        """Retrieve model version from Ollama API."""
        try:
            resp = httpx.post(
                f"{self._base_url}/api/show",
                json={"name": self._model_name},
                timeout=10.0,
            )
            resp.raise_for_status()
            details = resp.json()
            digest: str = details.get("modelfile_digest", "unknown")
            return digest[:12]
        except httpx.HTTPError:
            return "unknown"
