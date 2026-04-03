"""Tier 2 interactive CLI — human-assisted retrieval (FR-C02).

Presents retrieved source passages for curator confirmation. The curator
verifies that the extracted value matches the primary source before
committing it to the knowledge base.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from ..llm_consensus.schema_gen import load_data_dictionary

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def present_source_passage(
    attribute_id: str,
    label: str,
    passage: str,
    proposed_value: Any,
) -> bool:
    """Display a retrieved passage for curator confirmation.

    Returns:
        ``True`` if the curator accepts the proposed value.
    """
    print(f"\n{'=' * 60}")
    print(f"Attribute: {label} ({attribute_id})")
    print(f"{'=' * 60}")
    print(f"\nSource passage:\n  {passage}")
    print(f"\nProposed value: {proposed_value}")
    response = input("\nAccept? [Y/n]: ").strip().lower()
    return response in ("", "y", "yes")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tier 2 human-assisted retrieval CLI"
    )
    parser.add_argument("baseline_id", help="Baseline identifier")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_DIR / "staging",
        help="Output directory for intermediate files",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    catalogue = load_data_dictionary()
    today = date.today().isoformat()

    print(f"Tier 2 retrieval for baseline: {args.baseline_id}")
    print(f"Total attributes: {len(catalogue)}")

    attributes: dict[str, Any] = {}
    for attr in catalogue:
        aid = attr["attribute_id"]
        label = attr["label"]

        passage = input(f"\nPaste source passage for '{label}' (or SKIP): ").strip()
        if passage.upper() == "SKIP" or not passage:
            continue

        proposed = input(f"Proposed value for '{label}': ").strip()
        if not proposed:
            continue

        if present_source_passage(aid, label, passage, proposed):
            attributes[aid] = {
                "value": proposed,
                "missing": False,
                "missing_reason": None,
                "confidence": "High",
                "trust_tier": 2,
                "source": {
                    "url": input("Source URL: ").strip(),
                    "document": input("Document name: ").strip(),
                    "section": input("Section: ").strip(),
                    "accessed": today,
                },
                "llm_provenance": None,
                "collection_method": "human_curation",
                "curator_id": "human",
                "review_date": today,
                "ttl_days": 365,
            }

    output_file = output_dir / f"{args.baseline_id}_tier2.json"
    output_file.write_text(
        json.dumps(attributes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nSaved {len(attributes)} attributes to {output_file}")


if __name__ == "__main__":
    main()
