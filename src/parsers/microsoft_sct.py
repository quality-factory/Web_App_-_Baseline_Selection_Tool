"""Microsoft Security Compliance Toolkit GPO backup XML parser (Tier 1).

Parses GPO backup XML files from the Microsoft SCT package using
``defusedxml`` for safe XML processing.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from defusedxml import ElementTree

from .base_parser import BaseParser, ParsedAttribute, ParserResult


class MicrosoftSctParser(BaseParser):
    """Parses Microsoft SCT GPO backup XML files."""

    def parse(self, source_path: str, **kwargs: Any) -> ParserResult:
        """Parse a GPO backup XML directory or file.

        Args:
            source_path: Path to the GPO backup XML file or directory.
        """
        result = ParserResult(baseline_id="microsoft_sct")
        today = date.today().isoformat()
        src_url = kwargs.get("source_url", "")

        path = Path(source_path)

        if path.is_dir():
            xml_files = list(path.glob("**/*.xml"))
        elif path.is_file():
            xml_files = [path]
        else:
            result.errors.append(f"Source path not found: {source_path}")
            return result

        setting_count = 0
        gpo_names: list[str] = []

        for xml_file in xml_files:
            try:
                tree = ElementTree.parse(str(xml_file))
            except Exception as exc:
                result.errors.append(f"Failed to parse {xml_file.name}: {exc}")
                continue

            root = tree.getroot()

            # Count policy settings via tag iteration (namespace-safe)
            for elem in root.iter():
                local_tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if local_tag in ("RegistryPolicy", "Policy"):
                    setting_count += 1

            # Extract GPO name from Backup.xml
            name_el = root.find(".//DisplayName")
            if name_el is None:
                name_el = root.find(".//{*}DisplayName")
            if name_el is not None and name_el.text:
                gpo_names.append(name_el.text)

        if setting_count > 0:
            result.attributes.append(ParsedAttribute(
                attribute_id="setting_count",
                value=setting_count,
                source_url=src_url,
                source_document="Microsoft SCT GPO Backup",
                source_section="Policy count",
                accessed=today,
            ))

        # Static metadata
        static_attrs: list[tuple[str, Any]] = [
            ("issuer_name", "Microsoft"),
            ("issuer_type", "vendor"),
            ("baseline_type", "technical_benchmark"),
            ("prescriptiveness", "per_setting"),
            ("licence_type", "proprietary_free"),
            ("access_cost", "free_open"),
            ("audit_procedure_specificity", "machine_verifiable"),
            ("fix_procedure_specificity", "machine_executable"),
            ("version_granularity", "per_build"),
            ("changelog_transparency", "per_setting_diff"),
        ]
        for attr_id, value in static_attrs:
            result.attributes.append(ParsedAttribute(
                attribute_id=attr_id,
                value=value,
                source_url=src_url,
                source_document="Microsoft SCT",
                source_section="Known metadata",
                accessed=today,
            ))

        return result
