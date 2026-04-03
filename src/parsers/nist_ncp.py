"""NIST National Checklist Program REST API parser (Tier 1).

Queries the NCP repository API for checklist metadata. All HTTP calls
are made via ``httpx`` and are mockable in tests.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from .base_parser import BaseParser, ParsedAttribute, ParserResult

NCP_API_BASE = "https://web.nvd.nist.gov/view/ncp/repository"


class NistNcpParser(BaseParser):
    """Parses NIST NCP checklist metadata from the REST API."""

    def __init__(self, *, http_client: httpx.Client | None = None) -> None:
        self._client = http_client or httpx.Client(timeout=30.0)

    def parse(self, source_path: str, **kwargs: Any) -> ParserResult:
        """Query the NCP API for checklist metadata.

        Args:
            source_path: API URL or checklist identifier.
        """
        result = ParserResult(baseline_id="nist_ncp")
        today = date.today().isoformat()

        try:
            resp = self._client.get(source_path)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            result.errors.append(f"NCP API request failed: {exc}")
            return result
        except Exception as exc:
            result.errors.append(f"Failed to parse NCP response: {exc}")
            return result

        # Extract from NCP response structure
        checklist = data if isinstance(data, dict) else {}

        name = checklist.get("name", "")
        if name:
            result.attributes.append(ParsedAttribute(
                attribute_id="issuer_name",
                value="NIST (National Institute of Standards and Technology)",
                source_url=source_path,
                source_document=name,
                source_section="Checklist name",
                accessed=today,
            ))

        version = checklist.get("version", "")
        if version:
            result.attributes.append(ParsedAttribute(
                attribute_id="baseline_version",
                value=version,
                source_url=source_path,
                source_document=name or "NCP checklist",
                source_section="version",
                accessed=today,
            ))

        # Target platforms from the NCP product list
        products = checklist.get("products", [])
        if products:
            platform_names = [p.get("name", "") for p in products if p.get("name")]
            if platform_names:
                result.attributes.append(ParsedAttribute(
                    attribute_id="target_platforms",
                    value=platform_names,
                    source_url=source_path,
                    source_document=name or "NCP checklist",
                    source_section="products",
                    accessed=today,
                ))

        # Static metadata for NCP
        result.attributes.append(ParsedAttribute(
            attribute_id="baseline_type",
            value="checklist_repository",
            source_url=source_path,
            source_document="NIST NCP",
            source_section="Known metadata",
            accessed=today,
        ))

        return result
