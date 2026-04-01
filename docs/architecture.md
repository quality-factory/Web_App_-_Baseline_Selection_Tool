<!-- Audience: developers, automation agents -->
<!-- Scope: system overview, module layout, design decisions, capability model -->
<!-- Factory alignment: SubscriptionFactory.md v13.5.0 -->
<!-- Input document: docs/functional-design-v1.md -->

# Architecture

## Technical Constraints

| # | Constraint | Derived from | Effect on design |
|---|---|---|---|
| TC-01 | Shared PHP hosting via Plesk; no persistent non-PHP server process | FD BC-07 | Server layer must be PHP or static files |
| TC-02 | Deployment via push to dedicated branch, auto-deployed by Plesk webhook | Existing hosting infrastructure | All deployable artefacts committed to repository |
| TC-03 | Python is the factory's primary application language | §Target Language Scope | Curation pipeline in Python |
| TC-04 | Factory CI/CD pipeline applies to all repositories | §Enforcement Scope | Standard enforcement: lint, type check, secrets scan, dependency scan |
| TC-05 | All dependencies pinned via lockfiles | §Dependency and Supply-Chain Security | No unpinned dependencies |
| TC-06 | All tools and libraries free and open-source or free for internal use | §Dependency and Supply-Chain Security #5 | No paid frameworks or commercial JS libraries |
| TC-07 | No external services called at request time | FD FR-P06 | No CDN calls; all assets bundled |
| TC-08 | Knowledge base version-controlled alongside application code | FD FR-K01, FR-K02 | KB is a committed file |
| TC-09 | Knowledge base must not be directly bulk-downloadable | FD FR-P09, BC-10 | Static file serving is insufficient; PHP gating required |
| TC-10 | Rate limiting must be server-side | FD FR-P12 | PHP execution required on content requests |
| TC-11 | robots.txt must be published | FD FR-P13 | Deployed artefact in the repository |

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Factory Laptop (sovereign execution environment)             │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Curation Pipeline  [Python]                         │     │
│  │  ├── Tier 1: automated source parsers               │     │
│  │  ├── Tier 2: human-assisted retrieval CLI           │     │
│  │  ├── Tier 2b: multi-model LLM consensus pipeline   │     │
│  │  ├── Tier 3: analyst scoring CLI (two-pass, 48h)    │     │
│  │  └── Assembler + validator                          │     │
│  │  Output: data/baselines.json                        │     │
│  └─────────────────────────────────────────────────────┘     │
│                        │                                      │
│           committed to default branch (PR + CI)               │
└────────────────────────┼─────────────────────────────────────┘
                         │ merged to deployment branch
                         │ Plesk webhook (auto-deploy)
┌────────────────────────▼─────────────────────────────────────┐
│  Shared Hosting (PHP, Plesk-managed)                          │
│                                                               │
│  ┌─────────────────┐   ┌─────────────────────────────────┐   │
│  │ data/           │   │ web/                             │   │
│  │ baselines.json  │◄──│ index.php  (router, headers,     │   │
│  │ (write-once KB) │   │            rate limit, auth log) │   │
│  └─────────────────┘   │ api/baselines.php  (gated KB)    │   │
│                        │ index.html  (SPA shell)          │   │
│                        │ assets/     (JS + CSS bundled)   │   │
│                        │ robots.txt                       │   │
│                        └─────────────────────────────────┘   │
│                                    ▲ HTTPS                    │
└────────────────────────────────────┼──────────────────────────┘
                                     │
                            ┌────────┴────────┐
                            │  Browser (user)  │
                            └─────────────────┘
```

The PHP layer handles routing, security headers, rate limiting, acceptance logging (FR-P16), and knowledge base access gating. The frontend is otherwise static. The knowledge base is not web-accessible directly — only through `api/baselines.php`.

## Design Decisions

### Server-side technology — S1-B: PHP thin layer + static frontend

TC-09 (KB not bulk-downloadable) and TC-10 (rate limiting) both require PHP execution. S1-A (static-only) cannot satisfy TC-09 without Apache module support that is not guaranteed on shared hosting. S1-B satisfies all requirements with minimal added complexity and positions the PHP layer for v2 auth extension without structural change. S1-C (full PHP application) is disproportionate to v1 scope.

| Scenario | Description | Verdict |
|---|---|---|
| S1-A | Static site, .htaccess only | ❌ Cannot satisfy TC-09 or TC-10 reliably |
| **S1-B** | **PHP thin layer + static frontend** | **✅ Selected** |
| S1-C | PHP application serving data server-side | ❌ Disproportionate complexity |

### Data storage — S2-A: Single versioned JSON file

The JSON file satisfies all FD functional requirements (FR-K01 through FR-K04) with minimal complexity. Git provides richer version history than any audit table. File size (14 baselines × 45 attributes × provenance ≈ 200–400 KB uncompressed) is acceptable. Combined with PHP-gated serving (S7-B), it meets BC-10. MySQL (S2-B) adds operational overhead not justified by v1 scale. S2-C (split storage) is the natural v2 migration path when tenant and session data are introduced.

| Scenario | Description | Verdict |
|---|---|---|
| **S2-A** | **Single versioned JSON file** | **✅ Selected** |
| S2-B | MySQL database on shared hosting | ❌ Unnecessary complexity for v1 |
| S2-C | Split: JSON catalogue + MySQL for dynamic data | Equivalent to S2-A in v1; v2 migration path |

### Frontend framework — S3-B: Alpine.js

Alpine.js (~15 KB, MIT licence) provides reactive state management for UC-03 (comparison table) and UC-04a/UC-04b (wizard state) at negligible dependency cost and with no build step. S3-A (vanilla JS) is viable but produces significantly more complex code for interactive stories. S3-C (Vue/React) is disproportionate and introduces a build toolchain with supply-chain implications.

| Scenario | Description | Verdict |
|---|---|---|
| S3-A | Vanilla JavaScript | ❌ Viable but disproportionately complex |
| **S3-B** | **Alpine.js (~15 KB, MIT, no build step)** | **✅ Selected** |
| S3-C | Vue.js or React (full framework) | ❌ Disproportionate; build toolchain adds supply-chain risk |

### Curation pipeline interface — S4-A: CLI only

CLI is sufficient for a single curator and keeps the pipeline simple, auditable, and consistent with the factory's CLI-first approach. The two-pass Tier 3 scoring is straightforward to implement as a CLI workflow with a time-gate check. A local web UI (S4-B) adds development time not justified by v1 scope.

| Scenario | Description | Verdict |
|---|---|---|
| **S4-A** | **CLI only** | **✅ Selected** |
| S4-B | Local web UI (localhost, on-demand) | ❌ Disproportionate for v1 |

### Knowledge base serving — S7-B: PHP-gated endpoint with rate limiting

S7-A (static file with .htaccess restriction) provides only cosmetic protection — `curl` retrieves the complete KB regardless of browser navigation blocks. S7-B routes all KB access through a PHP endpoint that enforces per-IP rate limiting, user-agent filtering, and response headers. The residual risk (full JSON visible in browser devtools for legitimate users) is accepted — the protection goal is automated bulk extraction prevention, not cryptographic inaccessibility.

| Scenario | Description | Verdict |
|---|---|---|
| S7-A | Static file with .htaccess restriction | ❌ Cosmetic only; curl bypasses it |
| **S7-B** | **PHP-gated endpoint with rate limiting** | **✅ Selected** |

### Selected architecture summary

| Decision | Selected | Rationale summary |
|---|---|---|
| Server-side technology | S1-B: PHP thin layer + static frontend | Required for rate limiting, KB gating, acceptance logging |
| Data storage | S2-A: Single versioned JSON file | Satisfies all FD requirements; minimal complexity |
| Frontend framework | S3-B: Alpine.js | Reactive state at negligible cost; no build step |
| Curation pipeline interface | S4-A: CLI only | Sufficient for single curator; consistent with factory approach |
| Knowledge base serving | S7-B: PHP-gated endpoint | Required by BC-10 and FR-P09; S7-A is cosmetic only |

## Data Format Specification

### Knowledge base schema

```json
{
  "meta": {
    "schema_version": "1",
    "generated_at": "<ISO8601 datetime>",
    "generated_by": "<pipeline version>",
    "baseline_count": "<integer>",
    "tenant_id": "default"
  },
  "disclaimer": {
    "version": "1",
    "text": "<full disclaimer text as defined in FD §2.1.2>",
    "attribution": "<Factory Owner name>"
  },
  "attribute_schema": [
    {
      "attribute_id": "<stable slug>",
      "label": "<human-readable name>",
      "category": "<one of 8 categories>",
      "data_type": "Boolean | Enum | Enum (multi) | Date | Integer | Free text | Free text (list)",
      "objective_subjective": "Objective | Subjective",
      "stability": "Static | Per release | Continuous",
      "obtainability": "Easy | Moderate | Difficult",
      "enum_values": [{ "value": "<string>", "definition": "<string>" }],
      "rubric": "<scoring rubric for Tier 3 attributes; null otherwise>"
    }
  ],
  "baselines": [
    {
      "baseline_id": "<stable slug>",
      "tenant_id": "default",
      "display_name": "<string>",
      "issuer": "<string>",
      "baseline_type": "<Enum value>",
      "attributes": {
        "<attribute_id>": {
          "value": "<typed per schema; null if missing>",
          "missing": false,
          "missing_reason": "paywalled | empirical-only | no source found | disputed | not applicable | consensus-disagreement | null",
          "confidence": "High | Medium | Low",
          "trust_tier": 1,
          "source": {
            "url": "<string>",
            "document": "<string>",
            "section": "<string>",
            "accessed": "<ISO8601 date>"
          },
          "llm_provenance": {
            "models": [
              {
                "provider": "<string>",
                "model_id": "<string>",
                "model_version": "<string>",
                "output": "<extracted value or null>",
                "justification": "<string>"
              }
            ],
            "prompt_version": "<string>",
            "consensus_reached": true,
            "agreed_value": "<value or null>"
          },
          "collection_method": "automated_parse | human_curation | llm_consensus | analyst_scoring | community_aggregation",
          "curator_id": "<anonymised reference>",
          "review_date": "<ISO8601 date>",
          "ttl_days": 365
        }
      }
    }
  ]
}
```

The `disclaimer` block is version-controlled alongside the data it accompanies. Any rendering of a recommendation or export reads the disclaimer from this block — not from hardcoded strings.

The `llm_provenance` block is populated only when `collection_method` is `llm_consensus` (Tier 2b). For all other collection methods it is `null`. When `consensus_reached` is `false`, the attribute's `missing` flag is `true` with `missing_reason: "consensus-disagreement"`, and the individual model outputs in `llm_provenance.models` are preserved for Human Maintainer review.

For Tier 2b records, `curator_id` is `llm_consensus/<prompt_version>` where `<prompt_version>` is the SHA-256 short hash of the rendered prompt content (see §Tier 2b pipeline design). For other collection methods, `curator_id` is an anonymised reference to the human curator.

#### Trust tier to collection method mapping

The `collection_method` enum values in the schema correspond to the trust tier model defined in FD §5.3:

| Trust tier | FD §5.3 name | Schema `collection_method` | Confidence ceiling |
|---|---|---|---|
| 1 | Machine-extractable | `automated_parse` | High |
| 2 | Document-verifiable | `human_curation` | High |
| 2b | LLM-consensus-extracted | `llm_consensus` | Medium |
| 3 | Analyst-scored | `analyst_scoring` | Medium |
| 4 | Community-aggregated | `community_aggregation` | Low |

### Stale attributes report schema

Generated by the assembler; not deployed to the shared host. Used by CI for advisory warnings.

```json
{
  "generated_at": "<ISO8601 datetime>",
  "stale_count": "<integer>",
  "stale_attributes": [
    {
      "baseline_id": "<string>",
      "attribute_id": "<string>",
      "review_date": "<ISO8601 date>",
      "ttl_days": 365,
      "days_overdue": "<integer>"
    }
  ]
}
```

### Acceptance log schema

Write-once log file (or append-only table if hosting supports it). Each row is one event.

```json
{
  "timestamp": "<ISO8601 datetime, server-side>",
  "ip_address": "<pseudonymised or raw per privacy statement §8.2.1>",
  "gtc_version": "<GT&C version identifier accepted>",
  "action": "accepted | declined",
  "user_agent_hash": "<SHA-256 of user agent string, not raw>"
}
```

Retention: 2 years per privacy statement §8.2.1. Log is write-once; erasure handled per privacy statement §12.1.5 (administrative "beyond use" marking).

## Component Design

### Repository structure

```
Web_App_-_Baseline_Selection_Tool/
├── src/                        — curation pipeline (Python)
│   ├── parsers/
│   │   ├── base_parser.py
│   │   ├── disa_stig.py
│   │   ├── nist_ncp.py
│   │   ├── openscap_ssg.py
│   │   └── microsoft_sct.py
│   ├── llm_consensus/
│   │   ├── __init__.py
│   │   ├── pipeline.py          — orchestrates extraction, consensus, provenance
│   │   ├── adapters/
│   │   │   ├── base.py          — abstract adapter interface
│   │   │   └── ollama.py        — local-first default adapter
│   │   ├── schema_gen.py        — JSON schema from data dictionary enums/types
│   │   ├── consensus.py         — field-level comparison, majority-rules
│   │   ├── prompts/
│   │   │   └── extract_v1.txt   — prompt template (versioned by content hash)
│   │   └── sources.json         — primary source URL manifest (per DD §3.1)
│   ├── retrieval/
│   │   └── retrieval_cli.py
│   ├── scorer/
│   │   └── scoring_cli.py      — enforces 48h gap between passes
│   ├── assembler/
│   │   ├── assembler.py        — embeds disclaimer block
│   │   ├── validator.py        — validates schema + disclaimer presence
│   │   └── staleness.py
│   └── schemas/
│       └── baselines.schema.json
├── data/
│   ├── baselines.json          — KB (served via PHP, not directly)
│   └── stale-attributes.json  — CI-generated, not deployed
├── web/                        — deployed artefact
│   ├── index.php               — SPA router, security headers, rate limiting
│   ├── api/
│   │   └── baselines.php       — PHP-gated KB endpoint + acceptance logging
│   ├── config/
│   │   └── settings.php        — GT&C URL, privacy statement URL (deployment-time config)
│   ├── index.html
│   ├── assets/
│   │   ├── app.js              — Alpine.js application (bundled)
│   │   └── app.css             — includes print stylesheet for UC-06a
│   ├── robots.txt
│   └── .htaccess               — SPA routing; blocks /data/ direct access
├── tests/                      — pytest
├── docs/
│   ├── functional-design-v1.md — what the system does (technology-agnostic)
│   ├── functional-design_-_data-dictionary-v1.md — attribute catalogue
│   ├── architecture.md         — this file
│   └── operations.md
├── governance/
└── CLAUDE.md
```

`web/config/settings.php` holds the configurable GT&C and privacy statement URLs (FR-P15). Updating these URLs requires no code change — only a config file edit and deployment.

### Curation pipeline modules

| Module | Responsibility |
|---|---|
| `base_parser.py` | Abstract base class; defines output contract for all Tier 1 parsers |
| `disa_stig.py` | Downloads and parses DISA STIG XCCDF/OVAL from DoD Cyber Exchange |
| `nist_ncp.py` | Queries NIST NCP REST API for checklist metadata |
| `openscap_ssg.py` | Reads OpenSCAP/SSG release metadata via GitHub API (unauthenticated) |
| `microsoft_sct.py` | Downloads and parses Microsoft SCT GPO backup XML |
| `llm_consensus/` | Tier 2b pipeline: multi-model LLM extraction with local-first adapter (Ollama-compatible), structured output schema generation from data dictionary, majority-rules consensus aggregation, provenance recording. Remote provider adapters added for diversity. See §Tier 2b pipeline design below. |
| `retrieval_cli.py` | Tier 2 interactive CLI: presents retrieved source passages for curator confirmation |
| `scoring_cli.py` | Tier 3 interactive CLI: enforces two-pass workflow with minimum 48h gap; fixes confidence at Medium |
| `assembler.py` | Merges all tier outputs; embeds disclaimer block from canonical source |
| `validator.py` | Validates schema conformance and disclaimer block presence; rejects on failure |
| `staleness.py` | Computes stale-attributes report from TTL metadata |

### Web application modules

| File | Technology | Responsibility |
|---|---|---|
| `index.php` | PHP | SPA routing; security headers; per-IP rate limiting; GT&C acceptance logging (FR-P16) |
| `api/baselines.php` | PHP | PHP-gated KB endpoint: rate limit, bot user-agent rejection, serve baselines.json |
| `config/settings.php` | PHP | Configurable GT&C URL and privacy statement URL for footer (FR-P15) |
| `index.html` | HTML | SPA shell; loads Alpine.js and app.js |
| `app.js` | JS (Alpine.js) | All UI logic: data loading, browse/filter, compare, wizard, export (with disclaimer injection) |
| `app.css` | CSS | Styling; print stylesheet for UC-06a (disclaimer non-suppressible) |
| `robots.txt` | Text | Disallow known AI crawlers and scrapers |

### Security headers

| Header | Value |
|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `no-referrer` |

### Rate limiting

Per-IP rate limiting implemented in PHP via APCu (preferred) or file-based counters (fallback if APCu unavailable — see open decisions). Returns HTTP 429 with `Retry-After` on limit exceeded. Rate limit events logged. Internal counters and configuration not exposed in error responses.

### robots.txt

Minimum required disallow entries:

```
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: *
Crawl-delay: 10
```

robots.txt is advisory; rate limiting is the enforcement layer.

### Disclaimer handling

Disclaimer behavioral requirements are defined in FR-P08 and FR-P11. `app.js` implements these by reading the `disclaimer` block from `baselines.json` at startup. Disclaimer text is sourced exclusively from the knowledge base — not hardcoded — so updates flow through the standard curation and deployment pipeline without code changes.

### Recommendation engine

Implements FD §8 (environment profile questions, hard filters, weighted scoring, confidence adjustment). All recommendation logic executes client-side in `app.js`.

**Weight vector storage** — The weight vector and compatibility mapping are defined as a static configuration object within `app.js`. They are explicit, documented rules — not trained parameters (FD §8.2). The vector covers all 45 attributes; environment profile answers (EQ-01 through EQ-07) select which weight profile applies.

**Hard filters** — EQ-01 (OS mismatch) and EQ-04 (paid when free required) exclude baselines before scoring. Excluded baselines are retained in a separate array for the exclusion list (UC-04b AC3).

**Scoring** — Weighted sum of attribute-level compatibility scores. Each attribute's compatibility is computed from its value against the environment profile. Missing values contribute zero to the score but increment the missing-count for the confidence adjustment.

**Confidence adjustment** — Missing or low-confidence values on high-weight attributes reduce the recommendation's stated confidence. More than three missing high-weight attributes triggers a low-confidence flag (UC-04b AC2).

**Determinism** — Same `baselines.json` version + same environment profile answers = same ranked output. No randomness, no external data, no session state.

**Multi-tenancy provision** — The engine reads `tenant_id` from the knowledge base `meta` block but does not filter by it in v1 (single tenant). When a second tenant is added (§9.3), the engine filters baselines by tenant before scoring — no structural change required.

## Sovereignty Classification

| Component | Provider | Classification | Exit strategy |
|---|---|---|---|
| Shared hosting | Pending classification | Pending | Required if class (b) |
| GitHub (source control, CI) | Microsoft (US) | (b) Tolerable with exit strategy | Git distributed; full local copy always available; CI workflows portable YAML |
| GitHub Actions (CI) | Microsoft (US) | (b) Tolerable with exit strategy | Workflow definitions portable to GitLab CI, Forgejo, or equivalent |

Factory-wide sovereignty taxonomy and classifications: SubscriptionFactory.md §Operational Constraints #5 and §Production Enabler Inventory.

## Tier 2b Pipeline Design

### Module structure

```
src/llm_consensus/
├── __init__.py
├── pipeline.py          — orchestrates: load sources → call models → consensus → per-baseline JSON
├── adapters/
│   ├── base.py          — abstract adapter interface (provider-agnostic)
│   └── ollama.py        — local-first default adapter (Ollama HTTP API)
├── schema_gen.py        — generates JSON schema from data dictionary enums/types
├── consensus.py         — field-level comparison, majority-rules logic
├── prompts/
│   └── extract_v1.txt   — prompt template (versioned by content hash)
└── sources.json         — primary source URL manifest (per data dictionary §3.1)
```

### Prompt template

The prompt template (`prompts/extract_v1.txt`) contains the system instructions, attribute schema, and extraction rules sent to each model. The template is parameterised with:
- The baseline identifier and display name
- The primary source URLs for that baseline (from `sources.json`)
- The JSON schema for structured output (generated by `schema_gen.py`)

`prompt_version` in the provenance block is the SHA-256 short hash (first 8 hex characters) of the rendered prompt content, ensuring traceability to the exact prompt that produced each extraction.

### Primary source manifest

`sources.json` maps each baseline identifier to its primary source URLs as registered in the data dictionary §3.1. The manifest is the pipeline's operational input — URLs are verified by the Human Maintainer before execution. CLI arguments MAY override manifest URLs for a specific run.

```json
{
  "disa_stig": {
    "display_name": "DISA STIG",
    "urls": ["<verified URL 1>", "<verified URL 2>"]
  }
}
```

### Model qualification

Not all locally hosted models reliably support structured output (JSON schema mode). Before a model is used in the consensus pipeline:

1. The adapter runs a qualification check: a minimal structured output request against the data dictionary schema.
2. Models that fail the check are excluded from the run with a warning.
3. The pipeline aborts if fewer than 3 qualified models are available (or fewer than 2 if operating in degraded mode — see FR-C08(e)).

Qualified model configurations (provider, model ID, version) are logged in the pipeline output for reproducibility.

### Degradation rules

Per FR-C08(e), when a model fails during extraction (timeout, malformed output after retry, structured output non-compliance):

| Successful responses | Consensus rule | Notes |
|---|---|---|
| 3 | 2-of-3 majority | Normal operation |
| 2 | 2-of-2 unanimous | One model failed or was excluded |
| 0–1 | No consensus possible | All attributes → `consensus-disagreement` |

Failed models are recorded in `llm_provenance.models` with `output: null` and `justification` explaining the failure reason.

### Pipeline output and assembly

The pipeline produces one intermediate JSON file per baseline in a staging directory. The assembler (`src/assembler/assembler.py`) merges these into `data/baselines.json`:
- Existing baselines not included in the current run are preserved unchanged.
- Baselines included in the run are replaced with the new output.
- The assembler validates the merged output against the knowledge base schema before writing.

This supports incremental runs (re-process a single baseline) without affecting the rest of the knowledge base.

### `curator_id` for Tier 2b

For LLM consensus extraction, `curator_id` is set to `llm_consensus/<prompt_version>`, where `<prompt_version>` is the prompt content hash defined above. This traces each attribute value to the exact pipeline configuration that produced it.

## Open Technical Decisions

Architecture-scoped decisions are tracked here. Operational decisions are tracked in [`operations.md`](operations.md) §Operational decisions.

| # | Decision | Status |
|---|---|---|
| OTD-01 | PHP framework vs. vanilla PHP for index.php | Vanilla PHP sufficient for v1. Revisit if v2 auth complexity justifies a micro-framework (Slim). |
| OTD-02 | Alpine.js version pinning | Pin to a specific release before implementation. |
| OTD-03 | GitHub API authentication for SSG parser | Unauthenticated rate limit (60 req/hr) sufficient for manual curation. Add token if pipeline is run frequently. |
| OTD-04 | CIS PDF parsing approach | Free CIS PDF is not machine-readable. Tier 1 limited to metadata visible in PDF structure. Full attribute coverage requires Tier 2. Accepted constraint. |
| OTD-05 | Export format implementation | Both UC-06a and UC-06b confirmed in v1. Print CSS for UC-06a; JS file generation for UC-06b. |
