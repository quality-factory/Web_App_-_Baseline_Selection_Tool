"""Tests for Tier 1 source parsers (U6).

All external HTTP calls mocked per AGENTS.md §Test external call isolation.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.parsers.base_parser import BaseParser, ParsedAttribute, ParserResult
from src.parsers.disa_stig import DisaStigParser
from src.parsers.microsoft_sct import MicrosoftSctParser
from src.parsers.nist_ncp import NistNcpParser
from src.parsers.openscap_ssg import OpenscapSsgParser


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def xccdf_file(tmp_path: Path) -> Path:
    """Create a minimal XCCDF 1.2 benchmark file."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2" id="test-stig">
    <title>Test DISA STIG</title>
    <version>V1R1</version>
    <Group id="G-001">
        <Rule id="SV-001" severity="high">
            <title>Test Rule 1</title>
        </Rule>
        <Rule id="SV-002" severity="medium">
            <title>Test Rule 2</title>
        </Rule>
    </Group>
</Benchmark>"""
    f = tmp_path / "stig.xml"
    f.write_text(xml, encoding="utf-8")
    return f


@pytest.fixture
def gpo_xml_dir(tmp_path: Path) -> Path:
    """Create a minimal GPO backup XML directory."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<PolFile>
    <DisplayName>Windows 11 Security</DisplayName>
    <RegistryPolicy>
        <Name>MinPasswordLength</Name>
        <Value>14</Value>
    </RegistryPolicy>
    <RegistryPolicy>
        <Name>LockoutThreshold</Name>
        <Value>5</Value>
    </RegistryPolicy>
</PolFile>"""
    f = tmp_path / "backup.xml"
    f.write_text(xml, encoding="utf-8")
    return tmp_path


# ── BaseParser ───────────────────────────────────────────────────────────

class TestBaseParser:
    def test_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            BaseParser()  # type: ignore[abstract]


# ── DISA STIG ────────────────────────────────────────────────────────────

class TestDisaStigParser:
    def test_parse_valid_xccdf(self, xccdf_file: Path) -> None:
        parser = DisaStigParser()
        result = parser.parse(str(xccdf_file), source_url="http://example.com")

        assert result.baseline_id == "disa_stig"
        assert len(result.errors) == 0
        assert len(result.attributes) > 0

        attr_ids = [a.attribute_id for a in result.attributes]
        assert "issuer_name" in attr_ids
        assert "baseline_version" in attr_ids
        assert "setting_count" in attr_ids

        version_attr = next(a for a in result.attributes if a.attribute_id == "baseline_version")
        assert version_attr.value == "V1R1"

        count_attr = next(a for a in result.attributes if a.attribute_id == "setting_count")
        assert count_attr.value == 2

    def test_parse_invalid_file(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.xml"
        bad_file.write_text("not xml")
        parser = DisaStigParser()
        result = parser.parse(str(bad_file))
        assert len(result.errors) > 0


# ── NIST NCP ─────────────────────────────────────────────────────────────

class TestNistNcpParser:
    def test_parse_success(self) -> None:
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "name": "Windows 11 Checklist",
            "version": "1.0",
            "products": [{"name": "Windows 11"}],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_resp

        parser = NistNcpParser(http_client=mock_client)
        result = parser.parse("http://ncp.example.com/checklist")

        assert result.baseline_id == "nist_ncp"
        assert len(result.errors) == 0
        attr_ids = [a.attribute_id for a in result.attributes]
        assert "baseline_version" in attr_ids
        assert "target_platforms" in attr_ids

    def test_parse_http_error(self) -> None:
        import httpx
        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.ConnectError("refused")

        parser = NistNcpParser(http_client=mock_client)
        result = parser.parse("http://ncp.example.com/checklist")
        assert len(result.errors) > 0


# ── OpenSCAP/SSG ────────────────────────────────────────────────────────

class TestOpenscapSsgParser:
    def test_parse_success(self) -> None:
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {
                "tag_name": "v0.1.73",
                "published_at": "2026-03-15T10:00:00Z",
            }
        ]
        mock_resp.raise_for_status = MagicMock()
        mock_resp.status_code = 200
        mock_client.get.return_value = mock_resp

        parser = OpenscapSsgParser(http_client=mock_client)
        result = parser.parse("http://api.github.com/repos/test/releases")

        assert result.baseline_id == "openscap_ssg"
        attr_ids = [a.attribute_id for a in result.attributes]
        assert "baseline_version" in attr_ids
        assert "last_update_date" in attr_ids

    def test_parse_rate_limited(self) -> None:
        import httpx
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "rate limited", request=MagicMock(), response=mock_resp
        )
        mock_client.get.return_value = mock_resp

        parser = OpenscapSsgParser(http_client=mock_client)
        result = parser.parse("http://api.github.com/repos/test/releases")
        assert len(result.errors) > 0
        assert "rate limit" in result.errors[0].lower()


# ── Microsoft SCT ────────────────────────────────────────────────────────

class TestMicrosoftSctParser:
    def test_parse_valid_gpo(self, gpo_xml_dir: Path) -> None:
        parser = MicrosoftSctParser()
        result = parser.parse(str(gpo_xml_dir), source_url="http://example.com")

        assert result.baseline_id == "microsoft_sct"
        assert len(result.errors) == 0

        attr_ids = [a.attribute_id for a in result.attributes]
        assert "issuer_name" in attr_ids
        assert "setting_count" in attr_ids

    def test_parse_nonexistent_path(self) -> None:
        parser = MicrosoftSctParser()
        result = parser.parse("/nonexistent/path")
        assert len(result.errors) > 0
