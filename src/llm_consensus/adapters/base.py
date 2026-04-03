"""Abstract base class for LLM adapters (provider-agnostic)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Provider-agnostic interface for LLM structured output extraction."""

    @abstractmethod
    def extract(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        timeout: float = 120.0,
    ) -> dict[str, Any]:
        """Send a prompt with a JSON schema and return structured output.

        Args:
            prompt: Rendered extraction prompt.
            schema: JSON Schema the model must conform to.
            timeout: Request timeout in seconds.

        Returns:
            Parsed JSON object conforming to *schema*.

        Raises:
            AdapterError: On network, auth, or structured-output failure.
        """

    @abstractmethod
    def qualify(self, schema: dict[str, Any]) -> bool:
        """Run a structured output compliance check against *schema*.

        Returns:
            ``True`` if the model produces valid structured output.
        """

    @property
    @abstractmethod
    def provider(self) -> str:
        """Provider name (e.g. ``'ollama'``, ``'openai'``)."""

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Model identifier as reported by the provider."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Model version string."""


class AdapterError(Exception):
    """Raised when an adapter operation fails."""
