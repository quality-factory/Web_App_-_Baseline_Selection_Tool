"""Tier 2b pipeline orchestrator.

Orchestrates: load sources → model qualification → call models →
consensus → per-baseline JSON with provenance. Implements FR-C08–FR-C12.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .adapters.base import AdapterError, BaseAdapter
from .consensus import compute_consensus

SOURCES_PATH = Path(__file__).resolve().parent / "sources.json"
PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent / "prompts" / "extract_v1.txt"


def load_sources(path: Path | None = None) -> dict[str, Any]:
    """Load the primary source URL manifest.

    Args:
        path: Override path to sources.json. Defaults to the package-local file.

    Returns:
        Dict mapping baseline_id to ``{"display_name": str, "urls": list[str]}``.
    """
    p = path or SOURCES_PATH
    return json.loads(p.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def render_prompt(
    baseline_id: str,
    display_name: str,
    source_urls: list[str],
    schema: dict[str, Any],
    template_path: Path | None = None,
) -> str:
    """Render the extraction prompt template with parameters.

    Args:
        baseline_id: Stable baseline identifier.
        display_name: Human-readable baseline name.
        source_urls: List of primary source URLs.
        schema: JSON Schema for structured output.
        template_path: Override path to the prompt template.

    Returns:
        Rendered prompt string.
    """
    p = template_path or PROMPT_TEMPLATE_PATH
    template = p.read_text(encoding="utf-8")
    rendered = template.replace("{{BASELINE_ID}}", baseline_id)
    rendered = rendered.replace("{{DISPLAY_NAME}}", display_name)
    rendered = rendered.replace("{{SOURCE_URLS}}", "\n".join(f"- {u}" for u in source_urls))
    rendered = rendered.replace("{{SCHEMA}}", json.dumps(schema, indent=2))
    return rendered


def qualify_models(
    adapters: list[BaseAdapter],
    schema: dict[str, Any],
) -> list[BaseAdapter]:
    """Run model qualification check on all adapters.

    Args:
        adapters: List of adapters to qualify.
        schema: JSON Schema to test against.

    Returns:
        List of adapters that passed qualification.
    """
    qualified: list[BaseAdapter] = []
    for adapter in adapters:
        print(f"  Qualifying {adapter.provider}/{adapter.model_id}...", end=" ")
        if adapter.qualify(schema):
            print("PASSED")
            qualified.append(adapter)
        else:
            print("FAILED — excluded")
    return qualified


def build_provenance(
    adapter: BaseAdapter,
    output: dict[str, Any] | None,
    prompt_version: str,
    *,
    error_reason: str | None = None,
) -> dict[str, Any]:
    """Construct a provenance record for a single model's extraction.

    Args:
        adapter: The adapter that produced the output.
        output: Extracted value dict, or ``None`` on failure.
        prompt_version: SHA-256 short hash of the rendered prompt.
        error_reason: Failure reason if output is None.
    """
    return {
        "provider": adapter.provider,
        "model_id": adapter.model_id,
        "model_version": adapter.model_version,
        "output": output,
        "justification": error_reason or "extraction successful",
    }


def _compute_prompt_version(rendered_prompt: str) -> str:
    """Compute prompt_version: SHA-256 short hash (first 8 hex chars)."""
    return hashlib.sha256(rendered_prompt.encode("utf-8")).hexdigest()[:8]


def run_pipeline(
    baseline_id: str,
    adapters: list[BaseAdapter],
    schema: dict[str, Any],
    *,
    sources_path: Path | None = None,
    prompt_template_path: Path | None = None,
    min_models: int = 3,
    min_consensus_models: int = 2,
) -> dict[str, Any]:
    """Run the full Tier 2b pipeline for a single baseline.

    Args:
        baseline_id: Stable baseline identifier.
        adapters: List of LLM adapters to use.
        schema: JSON Schema for structured output.
        sources_path: Override path to sources.json.
        prompt_template_path: Override path to the prompt template.
        min_models: Minimum qualified models to start (default 3).
        min_consensus_models: Minimum for degraded consensus (default 2).

    Returns:
        Dict with ``attributes`` (consensus results) and ``provenance``.

    Raises:
        RuntimeError: If fewer than *min_consensus_models* qualify.
    """
    # Load sources
    sources = load_sources(sources_path)
    baseline_info = sources.get(baseline_id)
    if baseline_info is None:
        raise RuntimeError(
            f"Baseline '{baseline_id}' not found in sources manifest"
        )

    display_name = baseline_info["display_name"]
    source_urls = baseline_info["urls"]

    # Render prompt
    rendered = render_prompt(
        baseline_id, display_name, source_urls, schema,
        template_path=prompt_template_path,
    )
    prompt_version = _compute_prompt_version(rendered)
    print(f"Prompt version: {prompt_version}")

    # Qualify models
    print(f"Qualifying {len(adapters)} model(s)...")
    qualified = qualify_models(adapters, schema)

    if len(qualified) < min_consensus_models:
        raise RuntimeError(
            f"Only {len(qualified)} model(s) qualified — "
            f"need at least {min_consensus_models}. "
            f"Pipeline aborted."
        )
    if len(qualified) < min_models:
        print(
            f"WARNING: Only {len(qualified)} models qualified "
            f"(wanted {min_models}). Operating in degraded mode."
        )

    # Extract from each model sequentially (DD-05)
    model_outputs: list[dict[str, Any]] = []
    provenance_records: list[dict[str, Any]] = []

    for adapter in qualified:
        print(f"  Extracting from {adapter.provider}/{adapter.model_id}...")
        output: dict[str, Any] | None = None
        error_reason: str | None = None

        for attempt in range(2):  # FR-C08(c): one retry
            try:
                output = adapter.extract(rendered, schema)
                break
            except AdapterError as exc:
                error_reason = str(exc)
                if attempt == 0:
                    print(f"    Retry ({error_reason})...")

        if output is not None:
            model_outputs.append(output)
        else:
            print(f"    EXCLUDED: {error_reason}")

        provenance_records.append(
            build_provenance(adapter, output, prompt_version, error_reason=error_reason)
        )

    # Compute consensus
    print(f"Computing consensus from {len(model_outputs)} output(s)...")
    consensus = compute_consensus(model_outputs)

    return {
        "baseline_id": baseline_id,
        "display_name": display_name,
        "prompt_version": prompt_version,
        "provenance": provenance_records,
        "consensus": consensus,
    }
