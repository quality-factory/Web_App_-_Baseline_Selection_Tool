"""Tier 3 two-pass scoring CLI (FR-C03).

Implements the analyst scoring workflow with a mandatory 48-hour gap
between the first and second pass. Confidence is fixed at Medium for
Tier 3 (trust tier 3) per FD §14.1.3.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from ..llm_consensus.schema_gen import load_data_dictionary

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MIN_GAP_HOURS = 48


def enforce_gap(state_file: Path) -> bool:
    """Check whether the minimum gap since the first pass has elapsed.

    Args:
        state_file: Path to the pass-1 state file.

    Returns:
        ``True`` if the gap is satisfied (pass 2 may proceed).
    """
    if not state_file.exists():
        return False
    state = json.loads(state_file.read_text(encoding="utf-8"))
    pass1_time = datetime.fromisoformat(state["pass1_completed_at"])
    elapsed = datetime.now() - pass1_time
    return elapsed >= timedelta(hours=MIN_GAP_HOURS)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tier 3 analyst scoring CLI (two-pass, 48h gap)"
    )
    parser.add_argument("baseline_id", help="Baseline identifier")
    parser.add_argument(
        "--pass", dest="pass_number", type=int, choices=[1, 2],
        required=True, help="Pass number (1 or 2)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_DIR / "staging",
        help="Output directory for intermediate files",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    state_file = output_dir / f"{args.baseline_id}_tier3_state.json"

    if args.pass_number == 2:
        if not enforce_gap(state_file):
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding="utf-8"))
                pass1_time = datetime.fromisoformat(state["pass1_completed_at"])
                remaining = timedelta(hours=MIN_GAP_HOURS) - (datetime.now() - pass1_time)
                print(
                    f"48h gap not met. Pass 1 completed at {pass1_time.isoformat()}. "
                    f"Remaining: {remaining}"
                )
            else:
                print("Pass 1 has not been completed yet.")
            sys.exit(1)

    catalogue = load_data_dictionary()
    subjective_attrs = [
        a for a in catalogue if a["objective_subjective"] == "Subjective"
    ]

    print(f"Tier 3 scoring — pass {args.pass_number} for: {args.baseline_id}")
    print(f"Subjective attributes to score: {len(subjective_attrs)}")

    today = date.today().isoformat()
    scores: dict[str, Any] = {}

    for attr in subjective_attrs:
        aid = attr["attribute_id"]
        label = attr["label"]
        enum_values = attr.get("enum_values")

        print(f"\n{'─' * 40}")
        print(f"{label} ({aid})")

        if enum_values:
            print("Options:")
            for ev in enum_values:
                print(f"  {ev['value']} — {ev['definition']}")

        value = input("Your assessment (or SKIP): ").strip()
        if value.upper() == "SKIP" or not value:
            continue

        scores[aid] = {
            "value": value,
            "missing": False,
            "missing_reason": None,
            "confidence": "Medium",  # Fixed for Tier 3
            "trust_tier": 3,
            "source": {
                "url": "",
                "document": "Analyst assessment",
                "section": f"Pass {args.pass_number}",
                "accessed": today,
            },
            "llm_provenance": None,
            "collection_method": "analyst_scoring",
            "curator_id": "analyst",
            "review_date": today,
            "ttl_days": 365,
        }

    output_file = output_dir / f"{args.baseline_id}_tier3_pass{args.pass_number}.json"
    output_file.write_text(
        json.dumps(scores, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if args.pass_number == 1:
        state_file.write_text(
            json.dumps({"pass1_completed_at": datetime.now().isoformat()}) + "\n",
            encoding="utf-8",
        )
        print(f"\nPass 1 complete. Wait 48h before running pass 2.")

    print(f"Saved {len(scores)} scores to {output_file}")


if __name__ == "__main__":
    main()
