# Function Manifest — BST v1 (#10)

**Version:** 1.0.0
**CR:** quality-factory/Web_App_-_Baseline_Selection_Tool#10
**Architecture:** TD-BST-001 v1.0.2
**Purpose:** Lists every function, method, endpoint, or equivalent unit of change to be created by this CR. Used for cross-CR collision detection via the in-flight change registry per SubscriptionFactory.md §Author Phase 1, field (vi).

All entries are **Create** — this is a greenfield project with no existing code.

---

## U1+U2: Project scaffolding and JSON schema generation (#21)

| File | Unit | Type | Description |
|---|---|---|---|
| `requirements.txt` | — | Config | Pinned dependencies |
| `src/schemas/baselines.schema.json` | — | Generated artifact | JSON schema from data dictionary |
| `src/llm_consensus/schema_gen.py` | `generate_schema()` | Function | Generates JSON schema from data dictionary attribute catalogue |
| `src/llm_consensus/schema_gen.py` | `load_data_dictionary()` | Function | Parses data dictionary for attribute definitions, types, enums |
| `data/baselines.json` | — | Data artifact | Empty valid KB (zero baselines, valid schema) |
| `data/stale-attributes.json` | — | Data artifact | Empty valid stale report |
| `.gitignore` | — | Config | Python artifact exclusions |
| `.gitattributes` | — | Config | Binary/output file markers |

## U3+U4: LLM adapter layer and consensus engine (#22)

| File | Unit | Type | Description |
|---|---|---|---|
| `src/llm_consensus/__init__.py` | — | Package init | Package exports |
| `src/llm_consensus/adapters/base.py` | `class BaseAdapter` | Abstract class | Provider-agnostic adapter interface |
| `src/llm_consensus/adapters/base.py` | `BaseAdapter.extract()` | Abstract method | Sends prompt, returns structured JSON |
| `src/llm_consensus/adapters/base.py` | `BaseAdapter.qualify()` | Abstract method | Structured output compliance check |
| `src/llm_consensus/adapters/ollama.py` | `class OllamaAdapter` | Class | Ollama HTTP API adapter (local-first) |
| `src/llm_consensus/adapters/ollama.py` | `OllamaAdapter.extract()` | Method | Calls Ollama structured output endpoint |
| `src/llm_consensus/adapters/ollama.py` | `OllamaAdapter.qualify()` | Method | Model qualification check against schema |
| `src/llm_consensus/consensus.py` | `compute_consensus()` | Function | Field-level comparison, majority-rules logic |
| `src/llm_consensus/consensus.py` | `apply_degradation_rules()` | Function | 3-of-3, 2-of-3, 2-of-2, 1-of-N, 0-of-N |

## U5: Pipeline orchestrator (#23)

| File | Unit | Type | Description |
|---|---|---|---|
| `src/llm_consensus/pipeline.py` | `run_pipeline()` | Function | Orchestrates: load sources → qualify models → call models → consensus → per-baseline JSON with provenance |
| `src/llm_consensus/pipeline.py` | `load_sources()` | Function | Loads primary source URL manifest |
| `src/llm_consensus/pipeline.py` | `qualify_models()` | Function | Runs qualification check on all configured models |
| `src/llm_consensus/pipeline.py` | `build_provenance()` | Function | Constructs provenance record with prompt version (SHA-256 short hash) |
| `src/llm_consensus/pipeline.py` | `render_prompt()` | Function | Renders prompt template with baseline ID, source URLs, schema |
| `src/llm_consensus/prompts/extract_v1.txt` | — | Prompt template | Versioned by content hash |
| `src/llm_consensus/sources.json` | — | Config | Primary source URL manifest |

## U6: Tier 1 source parsers (#24)

| File | Unit | Type | Description |
|---|---|---|---|
| `src/parsers/base_parser.py` | `class BaseParser` | Abstract class | Defines output contract for all Tier 1 parsers |
| `src/parsers/base_parser.py` | `BaseParser.parse()` | Abstract method | Returns structured attribute values from source |
| `src/parsers/disa_stig.py` | `class DisaStigParser` | Class | DISA STIG XCCDF/OVAL parser (via `defusedxml`) |
| `src/parsers/disa_stig.py` | `DisaStigParser.parse()` | Method | Parses XCCDF/OVAL XML |
| `src/parsers/nist_ncp.py` | `class NistNcpParser` | Class | NIST NCP REST API parser |
| `src/parsers/nist_ncp.py` | `NistNcpParser.parse()` | Method | Queries NCP API for checklist metadata |
| `src/parsers/openscap_ssg.py` | `class OpenscapSsgParser` | Class | OpenSCAP/SSG GitHub API release metadata parser |
| `src/parsers/openscap_ssg.py` | `OpenscapSsgParser.parse()` | Method | Reads release metadata via GitHub API |
| `src/parsers/microsoft_sct.py` | `class MicrosoftSctParser` | Class | Microsoft SCT GPO backup XML parser (via `defusedxml`) |
| `src/parsers/microsoft_sct.py` | `MicrosoftSctParser.parse()` | Method | Parses GPO backup XML |

## U7+U8+U9: Tier 2/3 CLIs, assembler, validator, staleness (#25)

| File | Unit | Type | Description |
|---|---|---|---|
| `src/retrieval/retrieval_cli.py` | `main()` | Entry point | Tier 2 interactive CLI (FR-C02) |
| `src/retrieval/retrieval_cli.py` | `present_source_passage()` | Function | Displays retrieved passage for curator confirmation |
| `src/scorer/scoring_cli.py` | `main()` | Entry point | Tier 3 two-pass scoring CLI (FR-C03) |
| `src/scorer/scoring_cli.py` | `enforce_gap()` | Function | Enforces 48h minimum gap between passes |
| `src/assembler/assembler.py` | `assemble()` | Function | Merges tier outputs; embeds disclaimer block (FR-C08(f)) |
| `src/assembler/assembler.py` | `merge_baseline()` | Function | Add new / replace existing / preserve unaffected |
| `src/assembler/validator.py` | `validate()` | Function | Schema conformance + disclaimer presence check |
| `src/assembler/staleness.py` | `compute_staleness()` | Function | TTL-based staleness computation (FR-C04) |

## U10+U11+U12: PHP layer and Alpine.js SPA (#26)

| File | Unit | Type | Description |
|---|---|---|---|
| `web/index.php` | — | PHP router | SPA routing, security headers, rate limiting, GT&C acceptance logging (FR-P16) |
| `web/api/baselines.php` | — | PHP endpoint | Rate limit check, bot UA rejection, serve baselines.json |
| `web/config/settings.php` | — | PHP config | GT&C URL, privacy statement URL |
| `web/.htaccess` | — | Server config | SPA routing; blocks `/data/` direct access |
| `web/robots.txt` | — | Text | Disallow known AI crawlers |
| `web/index.html` | — | HTML | SPA shell; loads Alpine.js and app.js |
| `web/assets/app.js` | `initApp()` | Alpine.js component | Root component: KB loading, routing, state |
| `web/assets/app.js` | `filterBaselines()` | Function | UC-01b: filter by OS and category |
| `web/assets/app.js` | `compareBaselines()` | Function | UC-03: side-by-side comparison, diff toggle, category collapse |
| `web/assets/app.js` | `runWizard()` | Function | UC-04a: wizard question flow (EQ-01–EQ-07) |
| `web/assets/app.js` | `computeRecommendation()` | Function | UC-04b: weighted scoring, hard filters, confidence adjustment (§13.7) |
| `web/assets/app.js` | `exportPdf()` | Function | UC-06a: triggers print CSS |
| `web/assets/app.js` | `exportMarkdown()` | Function | UC-06b: generates markdown file download |
| `web/assets/app.css` | — | CSS | Styling + print stylesheet (disclaimer `display: block !important`) |

## U13+U14: CI pipeline and documentation (#27)

| File | Unit | Type | Description |
|---|---|---|---|
| `.github/workflows/ci.yml` | Python dispatcher | CI step | mypy + pytest with coverage |
| `.github/workflows/ci.yml` | Schema validation | CI step | `data/baselines.json` against generated schema (blocking) |
| `.github/workflows/ci.yml` | Disclaimer check | CI step | Disclaimer block presence in KB |
| `.github/workflows/ci.yml` | Staleness advisory | CI step | Staleness report (non-blocking) |
| `.github/workflows/ci.yml` | robots.txt check | CI step | Presence verification |
| `README.md` | — | Documentation | Purpose, architecture overview, development setup, operational procedures |
| `docs/operations.md` | — | Documentation update | Operational notes discovered during implementation |
