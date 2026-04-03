"""DISA STIG XCCDF/OVAL parser (Tier 1).

Parses XCCDF benchmark files using ``defusedxml`` to extract baseline
metadata attributes. Produces structured output per the base parser contract.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from defusedxml import ElementTree

from .base_parser import BaseParser, ParsedAttribute, ParserResult

# XCCDF 1.2 namespace
XCCDF_NS = "http://checklists.nist.gov/xccdf/1.2"


class DisaStigParser(BaseParser):
    """Parses DISA STIG XCCDF benchmark XML."""

    def parse(self, source_path: str, **kwargs: Any) -> ParserResult:
        result = ParserResult(baseline_id="disa_stig")
        today = date.today().isoformat()

        try:
            tree = ElementTree.parse(source_path)
        except Exception as exc:
            result.errors.append(f"Failed to parse XCCDF: {exc}")
            return result

        root = tree.getroot()
        ns = {"x": XCCDF_NS}

        # Extract title
        title_el = root.find("x:title", ns)
        if title_el is not None and title_el.text:
            result.attributes.append(ParsedAttribute(
                attribute_id="issuer_name",
                value="DISA (Defense Information Systems Agency)",
                source_url=kwargs.get("source_url", ""),
                source_document=title_el.text,
                source_section="Benchmark title",
                accessed=today,
            ))

        # Extract version
        version_el = root.find("x:version", ns)
        if version_el is not None and version_el.text:
            result.attributes.append(ParsedAttribute(
                attribute_id="baseline_version",
                value=version_el.text,
                source_url=kwargs.get("source_url", ""),
                source_document="XCCDF Benchmark",
                source_section="version",
                accessed=today,
            ))

        # Count rules (settings)
        rules = root.findall(".//x:Rule", ns)
        if rules:
            result.attributes.append(ParsedAttribute(
                attribute_id="setting_count",
                value=len(rules),
                source_url=kwargs.get("source_url", ""),
                source_document="XCCDF Benchmark",
                source_section="Rule count",
                accessed=today,
            ))

        # Extract severity distribution (indicates severity classification)
        severities = set()
        for rule in rules:
            sev = rule.get("severity", "")
            if sev:
                severities.add(sev)
        if severities:
            result.attributes.append(ParsedAttribute(
                attribute_id="severity_classification",
                value="yes_granular",
                source_url=kwargs.get("source_url", ""),
                source_document="XCCDF Benchmark",
                source_section="Rule severity attributes",
                accessed=today,
            ))

        # Static metadata
        static_attrs = [
            ("issuer_type", "government_military"),
            ("baseline_type", "technical_benchmark"),
            ("prescriptiveness", "per_setting"),
            ("audit_procedure_specificity", "machine_verifiable"),
            ("fix_procedure_specificity", "step_by_step"),
        ]
        for attr_id, value in static_attrs:
            result.attributes.append(ParsedAttribute(
                attribute_id=attr_id,
                value=value,
                source_url=kwargs.get("source_url", ""),
                source_document="DISA STIG documentation",
                source_section="Known metadata",
                accessed=today,
            ))

        return result
