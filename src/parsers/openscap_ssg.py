"""OpenSCAP / SCAP Security Guide GitHub API release metadata parser (Tier 1).

Reads release metadata from the ComplianceAsCode GitHub repository via
the unauthenticated REST API (60 requests/hour limit — INT-03).
"""

from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from .base_parser import BaseParser, ParsedAttribute, ParserResult

GITHUB_API_RELEASES = (
    "https://api.github.com/repos/ComplianceAsCode/content/releases"
)


class OpenscapSsgParser(BaseParser):
    """Parses OpenSCAP/SSG release metadata from GitHub API."""

    def __init__(self, *, http_client: httpx.Client | None = None) -> None:
        self._client = http_client or httpx.Client(
            timeout=30.0,
            headers={"Accept": "application/vnd.github.v3+json"},
        )

    def parse(self, source_path: str, **kwargs: Any) -> ParserResult:
        """Fetch release metadata from the GitHub API.

        Args:
            source_path: GitHub API releases URL.
        """
        result = ParserResult(baseline_id="openscap_ssg")
        today = date.today().isoformat()

        try:
            resp = self._client.get(source_path, params={"per_page": 5})
            resp.raise_for_status()
            releases = resp.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403:
                result.errors.append("GitHub API rate limit exceeded (60/hr unauthenticated)")
            else:
                result.errors.append(f"GitHub API error: {exc}")
            return result
        except httpx.HTTPError as exc:
            result.errors.append(f"GitHub API request failed: {exc}")
            return result

        if not isinstance(releases, list) or len(releases) == 0:
            result.errors.append("No releases found")
            return result

        latest = releases[0]

        # Version from tag name
        tag = latest.get("tag_name", "")
        if tag:
            result.attributes.append(ParsedAttribute(
                attribute_id="baseline_version",
                value=tag,
                source_url=source_path,
                source_document="ComplianceAsCode/content",
                source_section="Latest release tag",
                accessed=today,
            ))

        # Last update date
        published = latest.get("published_at", "")
        if published:
            result.attributes.append(ParsedAttribute(
                attribute_id="last_update_date",
                value=published[:10],
                source_url=source_path,
                source_document="ComplianceAsCode/content",
                source_section="Latest release date",
                accessed=today,
            ))

        # Static metadata
        static_attrs: list[tuple[str, Any]] = [
            ("issuer_name", "ComplianceAsCode / SCAP Security Guide"),
            ("issuer_type", "open_source_community"),
            ("baseline_type", "technical_benchmark"),
            ("licence_type", "open_source"),
            ("update_cadence", "continuous"),
            ("review_process", "open_source_pr"),
            ("scap_compliance_level", "scap_conformant"),
        ]
        for attr_id, value in static_attrs:
            result.attributes.append(ParsedAttribute(
                attribute_id=attr_id,
                value=value,
                source_url=source_path,
                source_document="ComplianceAsCode/content",
                source_section="Known metadata",
                accessed=today,
            ))

        return result
