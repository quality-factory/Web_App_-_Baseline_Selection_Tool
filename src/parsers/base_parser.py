"""Abstract base class for Tier 1 source parsers.

Every parser extracts structured attribute values from a machine-readable
primary source and returns them in a common output contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedAttribute:
    """One extracted attribute value with provenance metadata."""

    attribute_id: str
    value: Any
    source_url: str
    source_document: str
    source_section: str
    accessed: str  # ISO 8601 date


@dataclass
class ParserResult:
    """Output contract for a single parser run."""

    baseline_id: str
    attributes: list[ParsedAttribute] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class BaseParser(ABC):
    """Defines the output contract for all Tier 1 parsers."""

    @abstractmethod
    def parse(self, source_path: str, **kwargs: Any) -> ParserResult:
        """Parse a source file or API response and return extracted attributes.

        Args:
            source_path: Path to downloaded file or API URL.

        Returns:
            A ``ParserResult`` with extracted attributes and any errors.
        """
