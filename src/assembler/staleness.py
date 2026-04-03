"""Staleness computation — TTL-based attribute staleness detection (FR-C04).

Generates the stale-attributes report (``data/stale-attributes.json``)
from the knowledge base's TTL metadata.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def compute_staleness(
    kb: dict[str, Any],
    *,
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Compute stale attributes from the knowledge base.

    Args:
        kb: Knowledge base dict.
        reference_date: Date to compute staleness against. Defaults to today.

    Returns:
        Stale-attributes report conforming to architecture §11.2 schema.
    """
    ref = reference_date or date.today()
    stale: list[dict[str, Any]] = []

    for baseline in kb.get("baselines", []):
        baseline_id = baseline.get("baseline_id", "")
        attributes = baseline.get("attributes", {})

        for attr_id, attr_data in attributes.items():
            review_date_str = attr_data.get("review_date", "")
            ttl_days = attr_data.get("ttl_days", 365)

            if not review_date_str:
                continue

            try:
                review_date = date.fromisoformat(review_date_str)
            except ValueError:
                continue

            expiry = review_date.replace(
                year=review_date.year,
            )
            from datetime import timedelta

            expiry = review_date + timedelta(days=ttl_days)
            days_overdue = (ref - expiry).days

            if days_overdue > 0:
                stale.append({
                    "baseline_id": baseline_id,
                    "attribute_id": attr_id,
                    "review_date": review_date_str,
                    "ttl_days": ttl_days,
                    "days_overdue": days_overdue,
                })

    return {
        "generated_at": datetime.now().isoformat(),
        "stale_count": len(stale),
        "stale_attributes": stale,
    }
