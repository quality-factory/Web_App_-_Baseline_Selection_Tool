<!-- Audience: end users, non-technical stakeholders -->
<!-- Scope: purpose, usage, installation, limitations -->

# Baseline Selection Tool (BST)

A web-based tool for systematically selecting security hardening baselines.

## What it does

The BST helps security practitioners choose an appropriate hardening baseline for their workstation environment by providing structured comparison across multiple baselines, scored against environment-specific attributes. It replaces ad-hoc baseline selection with a systematic, transparent, and auditable process.

**Key capabilities:**

- Browse and filter 14 in-scope baselines across 45 attributes
- Side-by-side comparison with differences toggle
- Guided selection wizard with weighted scoring
- PDF and markdown export with mandatory disclaimer
- Full provenance chain for every attribute value

## How to use it

The BST is deployed at `https://www.qualityfactory.com/my/bst/` (requires GT&C acceptance).

### For developers

**Prerequisites:** Python 3.11+, pip

```bash
# Clone and install dependencies
git clone https://github.com/quality-factory/Web_App_-_Baseline_Selection_Tool.git
cd Web_App_-_Baseline_Selection_Tool
pip install -r requirements.txt

# Run tests
pytest

# Type checking
mypy src/

# Generate JSON schema from data dictionary
python -m src.llm_consensus.schema_gen
```

### Curation pipeline

The curation pipeline runs on the factory laptop. See `docs/operations.md` for operational procedures.

```bash
# Tier 2b: LLM consensus pipeline (requires Ollama with ≥3 models)
# Tier 2: human-assisted retrieval
# Tier 3: analyst scoring (two-pass, 48h gap)
# Assembler merges all tier outputs into data/baselines.json
```

## Architecture overview

```
Factory Laptop                  Shared Hosting (PHP, Plesk)
┌──────────────────────┐       ┌───────────────────────────┐
│ Curation Pipeline    │       │ web/index.php (router)    │
│ ├── Tier 1: parsers  │  PR   │ web/api/baselines.php     │
│ ├── Tier 2b: LLM     │──────▶│ web/index.html (SPA)      │
│ ├── Tier 2: human    │  CI   │ web/assets/app.js         │
│ ├── Tier 3: scoring  │       │ web/assets/app.css        │
│ └── Assembler        │       │ data/baselines.json (KB)  │
└──────────────────────┘       └───────────────────────────┘
```

## Version

Version placeholder: `src/__init__.py` contains `<BUILD_VERSION>`.

CI injects the resolved version before build/test per AGENTS.md §Version traceability.

## Operational scope

This tool operates within the following scope:

| System | Operations | Boundary |
|---|---|---|
| Local filesystem | Read/write: `data/`, `staging/` | Curation pipeline output |
| Ollama (localhost) | HTTP POST: structured output extraction | Local LLM models only |
| GitHub API (unauthenticated) | GET: release metadata | OpenSCAP/SSG parser |
| Primary source websites | GET: XCCDF, NCP API, GPO XML | Tier 1 parsers |
| Shared hosting | Read: `data/baselines.json` | PHP serves KB via gated endpoint |

No operations beyond this scope are performed.

## Limitations

- v1 scope: baseline selection and comparison only. Per-user accounts (v2), guidance integration, and compliance auditing are deferred.
- Decision-support tool only — not a professional security advisory service. Every recommendation carries a mandatory disclaimer.
- Knowledge base must be curated manually via the curation pipeline.

## Design documents

- `docs/functional-design.md` — What the system does
- `docs/architecture.md` — Design decisions, component design, data schemas
- `docs/operations.md` — Deployment pipeline, verification, operational notes
- `docs/functional-design_-_data-dictionary-v1.md` — 45-attribute catalogue

## De-identification

The de-identification shared module is defined in the Subscription Factory repository (`Infra_-_Subscription_Factory`). This project uses the factory's canonical implementation per AGENTS.md §De-identification and metadata minimization.

Built from this template: [Infra_-_Repo_Template](https://github.com/quality-factory/Infra_-_Repo_Template)

