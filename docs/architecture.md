# Technical Design — Baseline Selection Tool (BST)

| Field | Value |
|---|---|
| **Document ID** | TD-BST-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Author** | Author TD (agent) |
| **Validator** | TBD (assigned at Review TD) |
| **Creation date** | 2026-04-03 |
| **Sign-off date** | Pending |
| **Sign-off authority** | Human Maintainer (Factory Owner) |
| **Factory alignment** | SubscriptionFactory.md v14.0.0 |
| **Principles alignment** | fd-td-design-principles.md v3.4 |

---

## Table of Contents

1. [Stable Identifiers](#1-stable-identifiers)
2. [Version History](#2-version-history)
3. [Glossary](#3-glossary)
4. [Scope](#4-scope)
5. [Assumptions and Constraints](#5-assumptions-and-constraints)
6. [Risk Cross-Reference](#6-risk-cross-reference)
7. [Cross-Reference](#7-cross-reference)
8. [Change Management](#8-change-management)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [System Architecture](#10-system-architecture)
11. [Data Model](#11-data-model)
12. [API Contracts](#12-api-contracts)
13. [Component Design](#13-component-design)
14. [Integration Design](#14-integration-design)
15. [Transition Design](#15-transition-design)
16. [Error Handling and Logging](#16-error-handling-and-logging)
17. [Infrastructure and Deployment](#17-infrastructure-and-deployment)
18. [Testing Strategy](#18-testing-strategy)
19. [Design Decisions Log](#19-design-decisions-log)

---

## 1. Stable Identifiers

Every design element, constraint, requirement, and decision in this document carries a persistent, unique identifier that does not change across versions. These identifiers anchor the project traceability matrix.

| Prefix | Scope | Example |
|---|---|---|
| `TC-` | Technical constraints | TC-01, TC-11 |
| `NFR-` | Non-functional requirements | NFR-01, NFR-07 |
| `S-` | Architecture decision scenarios | S1-B, S7-B |
| `FM-` | Failure modes | FM-C01, FM-D04 |
| `OTD-` | Open technical decisions | OTD-01, OTD-07 |
| `DD-` | Design decisions log entries | DD-01, DD-06 |
| `INT-` | Integration points | INT-01, INT-05 |

Lifecycle rules per fd-td-design-principles.md v3.4 §Stable identifiers: deleted identifiers are never reused; splits, merges, and material rewrites create new identifiers and deprecate originals with recorded lineage.

---

## 2. Version History

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-04-03 | — | Pre-template architecture.md and operations.md produced (design decisions, component design, data schemas, failure modes, deployment pipeline) | Author TD (agent) |
| 2026-04-03 | 1.0.0 | Restructured to fd-td-design-principles.md v3.4 template. Added: metadata, stable identifiers, version history, glossary, scope, assumptions and constraints (with deployment context declaration), risk cross-reference, cross-reference, change management, non-functional requirements (derived from FD QR-01–QR-07), integration design, transition design, testing strategy, design decisions log. All existing technical content preserved. | Author TD (agent) |

---

## 3. Glossary

Terms defined in the FD glossary (FD-BST-001 §3) are not restated here. This glossary defines additional terms introduced by the TD.

| Term | Definition | Source | First used in |
|---|---|---|---|
| Alpine.js | A lightweight (~15 KB) JavaScript framework providing reactive state management via HTML attributes. Selected as S3-B. | [alpinejs.dev](https://alpinejs.dev/) | §10 |
| APCu | PHP userland cache extension providing in-memory key-value storage scoped to the PHP process. Used for rate-limit counters. | [php.net/apcu](https://www.php.net/manual/en/book.apcu.php) | §13 |
| Content Security Policy (CSP) | HTTP response header restricting the origins from which browsers load resources. | W3C CSP Level 3 | §13 |
| Degradation rules | The consensus pipeline's behaviour when fewer than 3 qualified models produce valid responses. Defines consensus thresholds for 3, 2, and 0–1 responses. | Project-defined | §14 |
| HSTS | HTTP Strict Transport Security header instructing browsers to enforce HTTPS. | RFC 6797 | §13 |
| JSON Schema | A vocabulary for annotating and validating JSON documents. Used for structured output compliance and KB validation. | [json-schema.org](https://json-schema.org/) | §11 |
| Model qualification | A structured output compliance check run against each LLM before use in the consensus pipeline. Models that fail are excluded. | Project-defined | §14 |
| Ollama | A local model server providing an HTTP API compatible with structured output for running LLMs on the factory laptop. | [ollama.com](https://ollama.com/) | §13 |
| Prompt version | SHA-256 short hash (first 8 hex characters) of the rendered prompt content, used as `curator_id` for Tier 2b provenance. | Project-defined | §13 |
| SPA | Single Page Application — a web application that loads a single HTML shell and updates content dynamically via JavaScript. | Industry standard | §10 |
| Structured output | LLM response mode where the model produces JSON conforming to a provided JSON schema, enabling deterministic parsing. | Project-defined | §13 |

---

## 4. Scope

This document is the technical design for the Baseline Selection Tool (BST) v1. It defines how the system achieves the requirements specified in FD-BST-001. This document covers:

- System architecture and design decisions with rationale
- Non-functional requirements derived from FD quality requirements
- Data model, API contracts, and component design
- Integration points with external systems
- Transition design for greenfield deployment
- Error handling, failure modes, and logging
- Testing strategy
- Infrastructure and deployment (detailed in the companion [`operations.md`](operations.md))

This TD covers the full BST v1 scope as a single unit of delivery (per FD §5.1 assumption A-06).

---

## 5. Assumptions and Constraints

### 5.1 Deployment context declaration

**Greenfield deployment.** The BST is a new application with no predecessor system to replace or migrate from. No legacy data, no existing users, no prior deployed version. Transition design (§15) addresses greenfield-specific concerns per fd-td-design-principles.md §Transition design.

### 5.2 Assumptions

| ID | Assumption | Implication |
|---|---|---|
| TA-01 | The shared hosting environment runs LiteSpeed on Ubuntu 24.04 with PHP 8.x and Plesk management | PHP features (APCu, file operations, htaccess equivalent) must be verified against LiteSpeed behaviour |
| TA-02 | The factory laptop has sufficient resources to run ≥3 LLM models simultaneously via Ollama | If memory is insufficient, models are run sequentially (not parallel); pipeline design must support both |
| TA-03 | Alpine.js ~15 KB transfer size is acceptable for the hosting environment | No build step required; served as a static asset |
| TA-04 | APCu may not be available on the shared hosting environment | File-based rate limiting fallback is required (OTD-06) |
| TA-05 | The complete knowledge base (14 baselines × 45 attributes × provenance) fits within ~200–400 KB uncompressed JSON | If growth exceeds this, chunking or pagination must be introduced |
| TA-06 | Iterative delivery granularity: this FD/TD pair covers the full BST v1 scope as a single unit of delivery | Per fd-td-design-principles.md §Applicability and FD §5.1 A-06 |

### 5.3 Technical constraints

Each constraint derives from an FD business constraint or factory specification. All constraints are actionable design boundaries.

| ID | Constraint | Derived from | Effect on design |
|---|---|---|---|
| TC-01 | Shared PHP hosting via Plesk; no persistent non-PHP server process | FD BC-07 | Server layer must be PHP or static files |
| TC-02 | Deployment via push to dedicated branch, auto-deployed by Plesk webhook | Existing hosting infrastructure | All deployable artefacts committed to repository |
| TC-03 | Python is the factory's primary application language | [Factory Spec §Target Language Scope] | Curation pipeline in Python |
| TC-04 | Factory CI/CD pipeline applies to all repositories | [Factory Spec §Enforcement Scope] | Standard enforcement: lint, type check, secrets scan, dependency scan |
| TC-05 | All dependencies pinned via lockfiles | [Factory Spec §Dependency and Supply-Chain Security] | No unpinned dependencies |
| TC-06 | All tools and libraries free and open-source or free for internal use | [Factory Spec §Dependency and Supply-Chain Security #5] | No paid frameworks or commercial JS libraries |
| TC-07 | No external services called at request time | FD FR-P06 | No CDN calls; all assets bundled |
| TC-08 | Knowledge base version-controlled alongside application code | FD FR-K01, FR-K02 | KB is a committed file |
| TC-09 | Knowledge base must not be directly bulk-downloadable | FD FR-P09, BC-10 | Static file serving is insufficient; PHP gating required |
| TC-10 | Rate limiting must be server-side | FD FR-P12 | PHP execution required on content requests |
| TC-11 | robots.txt must be published | FD FR-P13 | Deployed artefact in the repository |

### 5.4 Risk cross-reference note

Technical risks are documented in §6. Business constraints (BC-01 through BC-11) are defined in FD-BST-001 §5.2.

---

## 6. Risk Cross-Reference

This section identifies technical risks relevant to the TD scope. Business risks (RR-01 through RR-06) are documented in FD-BST-001 §6.

| ID | Risk | Impact | Likelihood | Mitigation | Residual risk |
|---|---|---|---|---|---|
| TR-01 | APCu unavailable on shared hosting (TA-04) | Rate limiting falls back to file-based counters with lower performance | Medium | File-based fallback implemented; OTD-06 tracks verification | Functional but slower rate limiting under high load |
| TR-02 | Alpine.js version contains security vulnerability post-deployment | XSS or DOM manipulation attack surface | Low | Pin to specific release (OTD-02); CSP restricts script sources to 'self'; no inline scripts | Vulnerability window between disclosure and update |
| TR-03 | LiteSpeed .htaccess handling differs from Apache | SPA routing or data directory blocking may fail | Low | Deployment verification checklist (operations.md) tests both conditions; LiteSpeed supports Apache-compatible .htaccess | Manual fix required if discrepancy found |
| TR-04 | Knowledge base JSON exceeds browser memory on low-end devices | Application non-functional on constrained clients | Low | v1 dataset ~200–400 KB (TA-05); modern browsers handle multi-MB JSON | Reassess if baseline count exceeds 20 |
| TR-05 | Plesk webhook unreliable or misconfigured | Deployment succeeds on git but hosting not updated | Medium | Verification checklist after every deployment; manual Plesk UI fallback (FM-D01) | Delay between merge and live update |
| TR-06 | Structured output quality varies across local LLM models | Consensus pipeline produces more disagreements than expected | Medium | Model qualification check gates entry; degradation rules handle partial failures; Tier 2 manual fallback | Some attributes may require manual curation |

---

## 7. Cross-Reference

| Document | ID | Version | Relationship |
|---|---|---|---|
| Functional Design — BST | FD-BST-001 (`docs/functional-design.md`) | 1.0.0 | Paired FD for this TD. This TD defines how the system achieves the FD requirements. |
| Operations Guide — BST | — (`docs/operations.md`) | 1.0.0 | Companion to this TD. Covers infrastructure, deployment pipeline, verification, and operational procedures (§17 of this document references it). |
| Data Dictionary — BST | — (`docs/functional-design_-_data-dictionary-v1.md`) | 1.0 | Defines all 45 attributes. Authoritative source for schema generation and data model (§11). |
| Factory Specification | — (`Infra_-_Subscription_Factory/SubscriptionFactory.md`) | v14.0.0 | Governing factory policies. Technical constraints (§5.3) trace to this document. |
| Project traceability matrix | — | TBD | Links business objectives → FD requirements → TD design elements → test cases. |

Cross-references will be updated with formal version numbers when both FD and TD are formalised, per fd-td-design-principles.md §Cross-reference.

---

## 8. Change Management

### 8.1 Baselining mechanics

This document is baselined when its status transitions to **Formalised** following Human Maintainer sign-off. The permitted state transitions are defined in fd-td-design-principles.md §Metadata.

### 8.2 Sign-off authority

The Human Maintainer (Factory Owner) holds sign-off authority for this TD, covering technical architecture, security and privacy, and quality assurance per the project approval matrix (FD-BST-001 §11).

### 8.3 Change-vs-clarification heuristic

Per fd-td-design-principles.md §Change management: any modification that alters NFRs, architecture decisions, stable identifiers, API contracts, data schemas, or the meaning of any specification is a **change** requiring re-review. Typographical corrections, grammatical fixes, and formatting adjustments that do not alter meaning are **clarifications**. Administrative updates to cross-references are a distinct category with their own lighter process. In cases of doubt, the modification is treated as a change.

### 8.4 Post-formalisation changes

Any change to this document after formalisation requires:

1. The change is recorded in §2 (Version History) with rationale.
2. The validator reviews the change.
3. The sign-off authority approves the change.
4. The document version is incremented.
5. The FD cross-reference is updated if the change affects the FD's scope.

---

## 9. Non-Functional Requirements

Each NFR derives from an FD quality requirement (QR-xx) and adds system-level measurability. Per fd-td-design-principles.md §Non-functional requirements, NFRs cite the originating FD requirement, specify metrics not present in the FD, and are verifiable at the system level.

### NFR-01: Performance — page load

**Traces to:** FD QR-01 (interactive within 3 seconds on standard broadband)

The SPA shell (`index.html`), Alpine.js application (`app.js`), and stylesheet (`app.css`) must achieve Time to Interactive (TTI) ≤ 3 seconds on a 10 Mbps connection with 50 ms latency. Measured as: browser `DOMContentLoaded` event fires and Alpine.js `x-data` components are interactive.

**Budget:**

| Asset | Max transfer size (gzipped) |
|---|---|
| `index.html` | 5 KB |
| `app.js` (including Alpine.js) | 25 KB |
| `app.css` | 10 KB |
| `baselines.json` (via API) | 400 KB |
| **Total** | **440 KB** |

At 10 Mbps, 440 KB transfers in ~0.35 seconds. JSON parsing and Alpine.js initialisation must complete within the remaining ~2.6 seconds. Verification: browser DevTools Performance tab on a throttled 10 Mbps connection.

### NFR-02: Performance — interaction latency

**Traces to:** FD QR-02 (200 ms interaction latency after initial load)

All client-side interactions — filtering, sorting, comparison column toggling, wizard state transitions, and export generation — must complete within 200 ms. No server round-trip is required for UI state changes. The knowledge base is loaded once at SPA initialisation; all subsequent operations are in-memory.

Verification: browser DevTools Performance tab; no interaction exceeds 200 ms from user input to UI update.

### NFR-03: Usability

**Traces to:** FD QR-03 (usable without training by a security practitioner)

- All five primary navigation areas (browser, comparison, wizard, dictionary, about) reachable from any view in one click.
- No interaction requires a tooltip, help overlay, or external documentation to discover.
- Empty states (no filter results, no baselines selected for comparison) present explicit recovery actions.
- The wizard question flow (UC-04a) is self-explanatory: each question includes context text explaining why it matters (per FD §14.5.1).

Verification: deployment verification checklist includes a usability walk-through of all nine user stories (operations.md).

### NFR-04: Maintainability — operational overhead

**Traces to:** FD QR-04 (single-operator maintenance; staleness detection automated)

- Curation pipeline invocable via a single CLI command per baseline.
- Staleness detection computed automatically by the assembler; CI emits advisory warnings.
- No scheduled jobs, cron tasks, or background processes required for maintenance.
- Deployment requires one merge operation (main → deploy); Plesk webhook handles the rest.
- Configuration changes (GT&C URL, privacy statement URL) require only `config/settings.php` edit + deployment.

Verification: the Human Maintainer can complete a full curation → deployment cycle for one baseline without assistance, using only the procedures in operations.md.

### NFR-05: Auditability — traceability

**Traces to:** FD QR-05 (full traceability and reproducibility)

- Every attribute value in `baselines.json` carries a provenance record: source URL, document, section, access date, collection method, curator ID, review date, TTL.
- For Tier 2b values: additional `llm_provenance` block with model identifiers, prompt version (content hash), individual model outputs, and consensus outcome.
- Recommendation engine is deterministic: same `baselines.json` version + same environment profile answers = same ranked output.
- Knowledge base version and generation date visible on every data-presenting view (FR-P14).

Verification: for any displayed value, the provenance chain from source through collection to display can be reconstructed. Determinism verified by running the same profile twice against the same KB version.

### NFR-06: Sovereignty

**Traces to:** FD QR-06 (sovereignty taxonomy classification before deployment)

All infrastructure components classified per the factory sovereignty taxonomy (§10.3). Components classified as "(b) Tolerable with exit strategy" have documented exit strategies. The classification is reviewed before go-live and when infrastructure changes.

Verification: sovereignty classification table (§10.3) is complete with no "Pending" entries at go-live.

### NFR-07: Security — data handling

**Traces to:** FD QR-07 (no user data stored; standard web security headers)

- The application stores no user-supplied data as a primary function (FR-P02). Environment profile answers exist only in browser session memory.
- GT&C acceptance log (FR-P16) is the only personal data processed; governed by privacy statement §8.2.1.
- Security headers enforced on every response: CSP, HSTS, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy no-referrer (§13.4).
- No cookies set by the BST application itself. Website-layer GT&C popup cookie is managed by the webmaster.

Verification: deployment verification checklist tests all headers. No user data persisted beyond acceptance log.

---

## 10. System Architecture

### 10.1 Architecture overview

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
│  │ (write-once KB) │   │            rate limit, GT&C log) │   │
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

The PHP layer handles routing, security headers, rate limiting, GT&C acceptance logging (FR-P16), and knowledge base access gating. The frontend is otherwise static. The knowledge base is not web-accessible directly — only through `api/baselines.php`.

Each material architectural element is annotated with the decision record that governs it:

| Element | Decision record |
|---|---|
| PHP thin layer | S1-B (§10.2) |
| Single JSON file for KB | S2-A (§10.2) |
| Alpine.js frontend | S3-B (§10.2) |
| CLI-only curation pipeline | S4-A (§10.2) |
| PHP-gated KB endpoint | S7-B (§10.2) |

### 10.2 Design decisions

#### S1-B: PHP thin layer + static frontend

TC-09 (KB not bulk-downloadable) and TC-10 (rate limiting) both require PHP execution. S1-A (static-only) cannot satisfy TC-09 without Apache module support that is not guaranteed on shared hosting. S1-B satisfies all requirements with minimal added complexity and positions the PHP layer for v2 auth extension without structural change. S1-C (full PHP application) is disproportionate to v1 scope.

| Scenario | Description | Verdict |
|---|---|---|
| S1-A | Static site, .htaccess only | ❌ Cannot satisfy TC-09 or TC-10 reliably |
| **S1-B** | **PHP thin layer + static frontend** | **✅ Selected** |
| S1-C | PHP application serving data server-side | ❌ Disproportionate complexity |

#### S2-A: Single versioned JSON file

The JSON file satisfies all FD functional requirements (FR-K01 through FR-K04) with minimal complexity. Git provides richer version history than any audit table. File size (14 baselines × 45 attributes × provenance ≈ 200–400 KB uncompressed) is acceptable. Combined with PHP-gated serving (S7-B), it meets BC-10. MySQL (S2-B) adds operational overhead not justified by v1 scale. S2-C (split storage) is the natural v2 migration path when tenant and session data are introduced.

| Scenario | Description | Verdict |
|---|---|---|
| **S2-A** | **Single versioned JSON file** | **✅ Selected** |
| S2-B | MySQL database on shared hosting | ❌ Unnecessary complexity for v1 |
| S2-C | Split: JSON catalogue + MySQL for dynamic data | Equivalent to S2-A in v1; v2 migration path |

#### S3-B: Alpine.js

Alpine.js (~15 KB, MIT licence) provides reactive state management for UC-03 (comparison table) and UC-04a/UC-04b (wizard state) at negligible dependency cost and with no build step. S3-A (vanilla JS) is viable but produces significantly more complex code for interactive stories. S3-C (Vue/React) is disproportionate and introduces a build toolchain with supply-chain implications.

| Scenario | Description | Verdict |
|---|---|---|
| S3-A | Vanilla JavaScript | ❌ Viable but disproportionately complex |
| **S3-B** | **Alpine.js (~15 KB, MIT, no build step)** | **✅ Selected** |
| S3-C | Vue.js or React (full framework) | ❌ Disproportionate; build toolchain adds supply-chain risk |

#### S4-A: CLI only

CLI is sufficient for a single curator and keeps the pipeline simple, auditable, and consistent with the factory's CLI-first approach. The two-pass Tier 3 scoring is straightforward to implement as a CLI workflow with a time-gate check. A local web UI (S4-B) adds development time not justified by v1 scope.

| Scenario | Description | Verdict |
|---|---|---|
| **S4-A** | **CLI only** | **✅ Selected** |
| S4-B | Local web UI (localhost, on-demand) | ❌ Disproportionate for v1 |

#### S7-B: PHP-gated endpoint with rate limiting

S7-A (static file with .htaccess restriction) provides only cosmetic protection — `curl` retrieves the complete KB regardless of browser navigation blocks. S7-B routes all KB access through a PHP endpoint that enforces per-IP rate limiting, user-agent filtering, and response headers. The residual risk (full JSON visible in browser devtools for legitimate users) is accepted — the protection goal is automated bulk extraction prevention, not cryptographic inaccessibility.

| Scenario | Description | Verdict |
|---|---|---|
| S7-A | Static file with .htaccess restriction | ❌ Cosmetic only; curl bypasses it |
| **S7-B** | **PHP-gated endpoint with rate limiting** | **✅ Selected** |

#### Selected architecture summary

| Decision | Selected | Rationale summary |
|---|---|---|
| Server-side technology | S1-B: PHP thin layer + static frontend | Required for rate limiting, KB gating, acceptance logging |
| Data storage | S2-A: Single versioned JSON file | Satisfies all FD requirements; minimal complexity |
| Frontend framework | S3-B: Alpine.js | Reactive state at negligible cost; no build step |
| Curation pipeline interface | S4-A: CLI only | Sufficient for single curator; consistent with factory approach |
| Knowledge base serving | S7-B: PHP-gated endpoint | Required by BC-10 and FR-P09; S7-A is cosmetic only |

### 10.3 Sovereignty classification

| Component | Provider | Classification | Exit strategy |
|---|---|---|---|
| Shared hosting | Hosting.nl (NL) | (a) Sovereign | N/A |
| GitHub (source control, CI) | Microsoft (US) | (b) Tolerable with exit strategy | Git distributed; full local copy always available; CI workflows portable YAML |
| GitHub Actions (CI) | Microsoft (US) | (b) Tolerable with exit strategy | Workflow definitions portable to GitLab CI, Forgejo, or equivalent |

Factory-wide sovereignty taxonomy and classifications: SubscriptionFactory.md §Operational Constraints #5 and §Production Enabler Inventory.

---

## 11. Data Model

### 11.1 Knowledge base schema

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
    "text": "<full disclaimer text as defined in FD §10.1.2>",
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

For Tier 2b records, `curator_id` is `llm_consensus/<prompt_version>` where `<prompt_version>` is the SHA-256 short hash of the rendered prompt content (see §13.6). For other collection methods, `curator_id` is an anonymised reference to the human curator.

#### Trust tier to collection method mapping

The `collection_method` enum values in the schema correspond to the trust tier model defined in FD §14.1.3:

| Trust tier | FD §14.1.3 name | Schema `collection_method` | Confidence ceiling |
|---|---|---|---|
| 1 | Machine-extractable | `automated_parse` | High |
| 2 | Document-verifiable | `human_curation` | High |
| 2b | LLM-consensus-extracted | `llm_consensus` | Medium |
| 3 | Analyst-scored | `analyst_scoring` | Medium |
| 4 | Community-aggregated | `community_aggregation` | Low |

### 11.2 Stale attributes report schema

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

### 11.3 Acceptance log schema

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

---

## 12. API Contracts

### 12.1 HTTP API — `api/baselines.php`

| Method | Path | Description |
|---|---|---|
| GET | `/api/baselines.php` | Returns the knowledge base content |

**Request** — No parameters. No request body.

**Response — 200 OK:**
- Body: contents of `data/baselines.json` (application/json)
- Headers: `Content-Type: application/json; charset=utf-8`, security headers per §13.4, `Cache-Control: public, max-age=3600` (KB is static between deployments)

**Error responses:**

| Status | Condition | Body |
|---|---|---|
| 429 Too Many Requests | Per-IP rate limit exceeded | `{"error": "rate_limit_exceeded"}` with `Retry-After` header |
| 403 Forbidden | Known bot user-agent detected | `{"error": "forbidden"}` |
| 500 Internal Server Error | `baselines.json` unreadable or missing | `{"error": "internal_error"}` (no implementation details exposed) |

The endpoint does not accept query parameters for filtering or pagination. The full knowledge base is served per request — the dataset size (~200–400 KB) is within acceptable bounds for v1.

### 12.2 Versioning strategy

No API versioning in v1. The endpoint path (`/api/baselines.php`) is the only contract. If a breaking change to the response schema is required in v2 (e.g., tenant-scoped responses), a new endpoint path is introduced; the v1 endpoint is deprecated with a timeline.

### 12.3 Communication protocol

HTTPS only. HSTS header enforces TLS. No HTTP fallback.

---

## 13. Component Design

### 13.1 Repository structure

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
│   ├── index.php               — SPA router, security headers, rate limiting, GT&C acceptance logging
│   ├── api/
│   │   └── baselines.php       — PHP-gated KB endpoint
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
│   ├── functional-design.md
│   ├── functional-design_-_data-dictionary-v1.md
│   ├── architecture.md         — this file
│   ├── operations.md
│   └── archive/
│       └── functional-design-v1.md
├── governance/
└── CLAUDE.md
```

`web/config/settings.php` holds the configurable GT&C and privacy statement URLs (FR-P15). Updating these URLs requires no code change — only a config file edit and deployment.

### 13.2 Curation pipeline modules

| Module | Responsibility |
|---|---|
| `base_parser.py` | Abstract base class; defines output contract for all Tier 1 parsers |
| `disa_stig.py` | Downloads and parses DISA STIG XCCDF/OVAL from DoD Cyber Exchange |
| `nist_ncp.py` | Queries NIST NCP REST API for checklist metadata |
| `openscap_ssg.py` | Reads OpenSCAP/SSG release metadata via GitHub API (unauthenticated) |
| `microsoft_sct.py` | Downloads and parses Microsoft SCT GPO backup XML |
| `llm_consensus/` | Tier 2b pipeline: multi-model LLM extraction with local-first adapter (Ollama-compatible), structured output schema generation from data dictionary, majority-rules consensus aggregation, provenance recording. Remote provider adapters added for diversity. See §13.6 below. |
| `retrieval_cli.py` | Tier 2 interactive CLI: presents retrieved source passages for curator confirmation |
| `scoring_cli.py` | Tier 3 interactive CLI: enforces two-pass workflow with minimum 48h gap; fixes confidence at Medium |
| `assembler.py` | Merges all tier outputs; embeds disclaimer block from canonical source |
| `validator.py` | Validates schema conformance and disclaimer block presence; rejects on failure |
| `staleness.py` | Computes stale-attributes report from TTL metadata |

### 13.3 Curation pipeline dependencies

All packages pinned in `requirements.txt` (TC-05). All free and open-source (TC-06).

| Package | Used by | Purpose |
|---|---|---|
| `httpx` | Tier 1 parsers, Ollama adapter | HTTP client for source retrieval and local LLM API calls |
| `jsonschema` | `validator.py`, `schema_gen.py` | KB schema validation; structured output compliance check |
| `defusedxml` | `disa_stig.py`, `microsoft_sct.py` | Safe XML parsing of XCCDF/OVAL and GPO backup files |
| `pytest` | `tests/` | Test framework (dev dependency) |
| `mypy` | CI | Static type checking (dev dependency) |

Standard library modules (`json`, `hashlib`, `datetime`, `pathlib`, `argparse`) are used throughout but not listed — they require no pinning.

### 13.4 Web application modules

| File | Technology | Responsibility |
|---|---|---|
| `index.php` | PHP | SPA routing; security headers; per-IP rate limiting; GT&C acceptance logging (FR-P16) |
| `api/baselines.php` | PHP | PHP-gated KB endpoint: rate limit, bot user-agent rejection, serve baselines.json |
| `config/settings.php` | PHP | Configurable GT&C URL and privacy statement URL for footer (FR-P15) |
| `index.html` | HTML | SPA shell; loads Alpine.js and app.js |
| `app.js` | JS (Alpine.js) | All UI logic: data loading, browse/filter, compare, wizard, export (with disclaimer injection) |
| `app.css` | CSS | Styling; print stylesheet for UC-06a (disclaimer non-suppressible) |
| `robots.txt` | Text | Disallow known AI crawlers and scrapers |

#### Security headers

| Header | Value |
|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `no-referrer` |

#### Rate limiting

Per-IP rate limiting implemented in PHP via APCu (preferred) or file-based counters (fallback if APCu unavailable — see OTD-06). Returns HTTP 429 with `Retry-After` on limit exceeded. Rate limit events logged. Internal counters and configuration not exposed in error responses.

#### robots.txt

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

### 13.5 Disclaimer handling

Disclaimer behavioral requirements are defined in FR-P08 and FR-P11. `app.js` implements these by reading the `disclaimer` block from `baselines.json` at startup. Disclaimer text is sourced exclusively from the knowledge base — not hardcoded — so updates flow through the standard curation and deployment pipeline without code changes.

### 13.6 Tier 2b pipeline design

#### Module structure

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

#### Prompt template

The prompt template (`prompts/extract_v1.txt`) contains the system instructions, attribute schema, and extraction rules sent to each model. The template is parameterised with:
- The baseline identifier and display name
- The primary source URLs for that baseline (from `sources.json`)
- The JSON schema for structured output (generated by `schema_gen.py`)

`prompt_version` in the provenance block is the SHA-256 short hash (first 8 hex characters) of the rendered prompt content, ensuring traceability to the exact prompt that produced each extraction.

#### Primary source manifest

`sources.json` maps each baseline identifier to its primary source URLs as registered in the data dictionary §3.1. The manifest is the pipeline's operational input — URLs are verified by the Human Maintainer before execution. CLI arguments MAY override manifest URLs for a specific run.

```json
{
  "disa_stig": {
    "display_name": "DISA STIG",
    "urls": ["<verified URL 1>", "<verified URL 2>"]
  }
}
```

#### Model qualification

Not all locally hosted models reliably support structured output (JSON schema mode). Before a model is used in the consensus pipeline:

1. The adapter runs a qualification check: a minimal structured output request against the data dictionary schema.
2. Models that fail the check are excluded from the run with a warning.
3. The pipeline aborts if fewer than 3 qualified models are available (or fewer than 2 if operating in degraded mode — see FR-C08(e)).

Qualified model configurations (provider, model ID, version) are logged in the pipeline output for reproducibility.

#### Degradation rules

Per FR-C08(e), when a model fails during extraction (timeout, malformed output after retry, structured output non-compliance):

| Successful responses | Consensus rule | Notes |
|---|---|---|
| 3 | 2-of-3 majority | Normal operation |
| 2 | 2-of-2 unanimous | One model failed or was excluded |
| 0–1 | No consensus possible | All attributes → `consensus-disagreement` |

Failed models are recorded in `llm_provenance.models` with `output: null` and `justification` explaining the failure reason.

#### Pipeline output and assembly

The pipeline produces one intermediate JSON file per baseline in a staging directory. The assembler (`src/assembler/assembler.py`) merges these into `data/baselines.json`:
- Existing baselines not included in the current run are preserved unchanged.
- Baselines included in the run are replaced with the new output.
- The assembler validates the merged output against the knowledge base schema before writing.

This supports incremental runs (re-process a single baseline) without affecting the rest of the knowledge base.

#### `curator_id` for Tier 2b

For LLM consensus extraction, `curator_id` is set to `llm_consensus/<prompt_version>`, where `<prompt_version>` is the prompt content hash defined above. This traces each attribute value to the exact pipeline configuration that produced it.

### 13.7 Recommendation engine

Implements FD §14.5 (environment profile questions, hard filters, weighted scoring, confidence adjustment). All recommendation logic executes client-side in `app.js`.

**Weight vector storage** — The weight vector and compatibility mapping are defined as a static configuration object within `app.js`. They are explicit, documented rules — not trained parameters (FD §14.5.2). The vector covers all 45 attributes; environment profile answers (EQ-01 through EQ-07) select which weight profile applies.

**Hard filters** — EQ-01 (OS mismatch) and EQ-04 (paid when free required) exclude baselines before scoring. Excluded baselines are retained in a separate array for the exclusion list (UC-04b AC3).

**Scoring** — Weighted sum of attribute-level compatibility scores. Each attribute's compatibility is computed from its value against the environment profile. Missing values contribute zero to the score but increment the missing-count for the confidence adjustment.

**Confidence adjustment** — Missing or low-confidence values on high-weight attributes reduce the recommendation's stated confidence. More than three missing high-weight attributes triggers a low-confidence flag (UC-04b AC2).

**Determinism** — Same `baselines.json` version + same environment profile answers = same ranked output. No randomness, no external data, no session state.

**Multi-tenancy provision** — The engine reads `tenant_id` from the knowledge base `meta` block but does not filter by it in v1 (single tenant). When a second tenant is added (FD §5.3), the engine filters baselines by tenant before scoring — no structural change required.

---

## 14. Integration Design

This section documents external systems and third-party services that the BST interacts with, communication patterns, and failure modes at integration boundaries.

### INT-01: Ollama (local LLM API)

| Aspect | Detail |
|---|---|
| System | Ollama local model server |
| Direction | Outbound from curation pipeline |
| Protocol | HTTP (localhost, no TLS required for loopback) |
| Pattern | Request-response; synchronous per model call |
| Data exchanged | Prompt + JSON schema (request); structured JSON output (response) |
| Authentication | None (localhost only) |
| Failure modes | FM-C01 (unreachable), FM-C02 (malformed output), FM-C04 (insufficient models) |
| Trust level | Semi-trusted (local process, but output treated as untrusted — schema-validated before acceptance) |

### INT-02: Remote LLM providers

| Aspect | Detail |
|---|---|
| System | Third-party LLM APIs (e.g., OpenAI, Anthropic, Google) |
| Direction | Outbound from curation pipeline |
| Protocol | HTTPS |
| Pattern | Request-response; synchronous per model call |
| Data exchanged | Prompt + JSON schema (request); structured JSON output (response) |
| Authentication | API key per provider, collected via interactive prompt, held in memory only (per AGENTS.md §Interactive configuration input) |
| Failure modes | FM-C01 (unreachable), FM-C02 (malformed output), FM-C09 (auth failure) |
| Trust level | Untrusted (output schema-validated; URLs cross-referenced against allowlist per FR-C10) |
| Cost | Tracked against BC-01 (€300/month cap); verified by HM after each run |

### INT-03: GitHub API (unauthenticated)

| Aspect | Detail |
|---|---|
| System | GitHub REST API |
| Direction | Outbound from `openscap_ssg.py` parser |
| Protocol | HTTPS |
| Pattern | Request-response; reads release metadata |
| Data exchanged | Release list and asset metadata (response only) |
| Authentication | None (unauthenticated; 60 requests/hour rate limit) |
| Failure modes | HTTP 403 (rate limit exceeded) → parser skips with warning; HTTP 5xx → retry once, then skip |
| Trust level | Semi-trusted (public API; response validated against expected schema) |

### INT-04: Primary source websites

| Aspect | Detail |
|---|---|
| System | DISA Cyber Exchange, NIST NCP, Microsoft Download Centre |
| Direction | Outbound from Tier 1 parsers |
| Protocol | HTTPS |
| Pattern | File download; synchronous |
| Data exchanged | XCCDF/OVAL XML (DISA), JSON API responses (NIST), GPO backup XML (Microsoft) |
| Authentication | None (public resources) |
| Failure modes | FM-C06 (URL 404 or moved); network timeout → retry once, then report as stale |
| Trust level | Trusted (authoritative primary sources per data dictionary §3.1) |

### INT-05: Plesk webhook

| Aspect | Detail |
|---|---|
| System | Plesk hosting management panel |
| Direction | Triggered by git push to `deploy` branch |
| Protocol | HTTPS (Plesk-managed) |
| Pattern | Event-driven; webhook fires on branch update |
| Data exchanged | Git ref update notification (request); file synchronisation (Plesk-internal) |
| Authentication | Plesk-managed (configured by webmaster) |
| Failure modes | FM-D01 (webhook fails) → manual deployment via Plesk UI |
| Trust level | Trusted (infrastructure managed by webmaster) |

---

## 15. Transition Design

### 15.1 Deployment context

**Greenfield deployment.** No predecessor system exists. No legacy data, users, or infrastructure to migrate from. Per fd-td-design-principles.md §Transition design, this section addresses greenfield-specific concerns.

### 15.2 Initial data seeding

The knowledge base (`data/baselines.json`) starts empty (zero baselines, valid schema). Initial population proceeds baseline-by-baseline via the curation pipeline:

1. Run Tier 1 parsers for machine-extractable baselines (DISA STIG, NIST NCP, OpenSCAP/SSG, Microsoft SCT).
2. Run Tier 2b consensus pipeline for LLM-extractable attributes.
3. Run Tier 2 retrieval CLI for document-verifiable attributes requiring human confirmation.
4. Run Tier 3 scoring CLI for subjective attributes (two passes, 48h gap).
5. Assemble, validate, and commit after each baseline is complete.

UAT entry criteria (FD §18.1) require at least one complete baseline before acceptance testing begins.

### 15.3 First-deployment go-live sequencing

1. **Pre-deployment:** Hosting infrastructure confirmed (Infra_-_Subscription_Factory#18). Domain restriction configured. HTTP Basic Auth enabled on BST URL.
2. **Initial deployment:** Merge `main` → `deploy`. Plesk webhook deploys. Run deployment verification checklist (operations.md).
3. **Internal testing:** BST accessible behind HTTP Basic Auth. HM executes UAT (FD §18).
4. **Go-live gate:** GT&C published (Infra_-_Subscription_Factory#17). Footer links configured. HTTP Basic Auth removed.
5. **Post-go-live:** Monitor rate limiting, acceptance logging, and hosting performance.

### 15.4 Rollback procedure for initial release

Since no predecessor system exists, "rollback" means removing public access:

1. Re-enable HTTP Basic Auth on the BST URL via Plesk.
2. Diagnose the issue.
3. Fix on `main`, re-run CI, merge to `deploy`.
4. Re-run deployment verification checklist.
5. Remove HTTP Basic Auth when resolved.

For KB data issues: revert `data/baselines.json` to a prior git commit, re-deploy.

### 15.5 Phased rollout strategy

No phased rollout required for v1. The BST launches as a single application instance on a single domain. The single-operator model (BC-08) means the Human Maintainer is the sole initial user. Public access is gated by GT&C publication (RR-01). When external clients are onboarded (v2+), a phased rollout by tenant becomes relevant.

---

## 16. Error Handling and Logging

### 16.1 Error handling principles

- Errors are surfaced to the appropriate audience: curation pipeline errors to the Human Maintainer (CLI output); presentation errors to the browser user (UI message).
- No internal implementation details exposed in user-facing error messages.
- Schema validation failures are blocking — invalid data is never written or served.
- Partial pipeline failures are handled via degradation rules (§13.6); the pipeline continues where possible.

### 16.2 Logging

| Layer | Mechanism | Content | Retention |
|---|---|---|---|
| Curation pipeline | Stdout/stderr | Model qualification results, extraction progress, consensus outcomes, validation results, failures | Session (terminal output) |
| PHP layer | PHP `error_log()` | Rate limit events, file read errors, GT&C log write failures | Server-managed (hosting default) |
| GT&C acceptance log | Custom write-once log | Acceptance events per §11.3 schema | 2 years (privacy statement §8.2.1) |
| CI | GitHub Actions logs | Lint, type check, test, schema validation, staleness advisory | GitHub retention policy |

### 16.3 Failure-mode inventory

Enumerated failure modes across all subsystems with detection, impact, and mitigation.

#### Curation subsystem

| # | Failure mode | Detection | Impact | Mitigation |
|---|---|---|---|---|
| FM-C01 | LLM API unreachable (network error, service down) | Adapter raises connection error | Pipeline cannot extract attributes for affected model | Adapter catches connection errors, logs model as excluded. Pipeline continues if ≥2 models remain; aborts with actionable error if <2 (per degradation rules §13.6). |
| FM-C02 | LLM returns malformed structured output | JSON schema validation failure after parsing | Model output unusable for consensus | One retry per FR-C08(c). On second failure, model excluded with `structured-output-failure` justification. Pipeline continues per degradation rules. |
| FM-C03 | LLM cites URL not in primary source manifest | URL validation against `sources.json` allowlist | Potential hallucination accepted as fact | Pipeline rejects any URL not in the manifest per FR-C10. Attribute value from that model for that field is treated as invalid for consensus purposes. |
| FM-C04 | Fewer than 2 models qualify (structured output check) | Model qualification check at pipeline startup | Pipeline cannot produce consensus output | Pipeline aborts before extraction with actionable error listing which models failed and why. No partial output written. |
| FM-C05 | Consensus disagreement on many/all attributes | Consensus aggregation finds <2-of-3 agreement | Baseline entry has many missing values | Values recorded as missing with reason `consensus-disagreement`. Provenance preserves individual model outputs for HM review. Pipeline continues — sparse output is valid. |
| FM-C06 | Primary source URL returns 404 or has moved | HTTP error during source retrieval (Tier 1) or LLM reports inability to access source | Stale or missing attribute values | Tier 1 parsers report retrieval failures per attribute. For Tier 2b, LLMs are instructed to report inaccessible sources. HM verifies source manifest URLs before each run (per operations.md). |
| FM-C07 | Schema validation failure on assembled output | Validator rejects merged `baselines.json` | Invalid KB not written to `data/` | Validator aborts with human-readable explanation per FR-C05. Previous valid `baselines.json` is preserved. |
| FM-C08 | Pipeline interrupted mid-run (crash, Ctrl+C) | Process termination | Partial intermediate files in staging directory | Assembler reads from staging directory; incomplete files are detected by schema validation. Staging directory is cleaned on next run. `data/baselines.json` is only written after successful validation — no partial writes. |
| FM-C09 | LLM API key invalid or expired (remote providers) | HTTP 401/403 from provider API | Remote model unavailable | Adapter catches auth errors, logs model as excluded with reason. Pipeline continues per degradation rules. Key re-entry via interactive prompt on next run. |

#### Knowledge store

| # | Failure mode | Detection | Impact | Mitigation |
|---|---|---|---|---|
| FM-K01 | `baselines.json` corrupted or truncated | JSON parse failure in validator or PHP endpoint | KB unreadable | Validator catches parse errors and rejects the file. PHP endpoint returns 500 (not a partial response). Git history provides recovery to any prior valid state. |
| FM-K02 | Schema drift between data dictionary and `baselines.json` | CI schema validation step; validator rejects non-conformant files | Attributes missing from schema or unknown attributes present | Data dictionary §7 consistency obligations require synchronized updates. CI enforces schema match before merge. |
| FM-K03 | All attribute TTLs expired (stale knowledge base) | Staleness report in CI (advisory); all `days_overdue > 0` | Knowledge base may contain outdated values | CI emits advisory warning (not blocking). FR-P14 ensures KB version and generation date are visible to users. HM decides when to re-run pipeline. |

#### Presentation subsystem

| # | Failure mode | Detection | Impact | Mitigation |
|---|---|---|---|---|
| FM-P01 | `baselines.json` fails to load (PHP error, file missing) | `app.js` fetch returns non-200 or unparseable response | Application displays no baseline data | `app.js` displays a user-facing error message with the HTTP status. No fallback data — blank state with explanation is safer than stale data. |
| FM-P02 | `baselines.json` is valid but contains zero baselines | `baselines` array is empty after parsing | All views are empty | `app.js` displays "No baselines available" with KB version/date. Not an error — this is a valid state during initial development. |
| FM-P03 | Rate limit exceeded by legitimate user | HTTP 429 returned by PHP rate limiter | User temporarily blocked from KB access | 429 response includes `Retry-After` header. `app.js` displays a user-friendly message with the retry delay. Rate limits are tuned for normal human browsing cadence. |
| FM-P04 | APCu unavailable on shared hosting | Runtime check for APCu extension | File-based rate limiting less performant | PHP falls back to file-based counters (OTD-06). Rate limiting remains functional; only performance characteristics change. |
| FM-P05 | GT&C acceptance log write fails (disk full, permissions) | PHP `error_log` or write operation returns failure | Acceptance event not recorded | Log write uses fail-safe mechanism per AGENTS.md §Operational transparency. Write failure is logged to PHP error log but does not block user access — logging is important but not a gating function. Accepted residual risk: some acceptance events may be lost. |
| FM-P06 | Browser does not support Alpine.js | Alpine.js requires ES6+ (all modern browsers) | Application non-functional | Alpine.js minimum: Chrome 61+, Firefox 60+, Safari 11+, Edge 16+. No polyfill — these versions cover >98% of active browsers. Unsupported browsers see the static HTML shell without interactivity. |
| FM-P07 | Print stylesheet renders differently across browsers | Visual inspection during deployment verification | PDF export (UC-06a) layout varies | Print stylesheet tested against Chrome and Firefox (dominant print engines). Disclaimer presence is CSS-enforced (`display: block !important` in print media query) — layout may vary but content completeness is guaranteed. |
| FM-P08 | Markdown export encoding issues | User reports garbled characters | Downloaded `.md` file displays incorrectly | Export sets `charset=utf-8` in the download blob. `baselines.json` is UTF-8 by schema. No transcoding occurs. |

#### Deployment

| # | Failure mode | Detection | Impact | Mitigation |
|---|---|---|---|---|
| FM-D01 | Plesk webhook fails (hosting outage, webhook misconfiguration) | Deployment verification checklist fails | `deploy` branch updated but hosting not refreshed | HM runs verification checklist after every deployment. Manual deployment via Plesk UI is the fallback. |
| FM-D02 | `deploy` branch merged with invalid `baselines.json` | CI should catch this on `main` before merge to `deploy` | Broken KB deployed to production | CI validates `baselines.json` schema on every PR to `main`. The `deploy` branch only receives merges from `main` — never direct pushes. Two-gate protection. |
| FM-D03 | `.htaccess` misconfiguration (SPA routing broken, data/ exposed) | Deployment verification checklist: direct `data/baselines.json` URL test | Either SPA navigation breaks or KB becomes directly downloadable | Verification checklist includes explicit tests for both conditions. `.htaccess` is version-controlled and reviewed in PR. |
| FM-D04 | Security headers missing or duplicated | Deployment verification checklist: response header inspection | Reduced security posture or browser rejection of duplicate headers | Verification checklist tests for exactly one `X-Frame-Options: DENY` header (not duplicated with SAMEORIGIN from hosting defaults). CSP header presence verified. |

---

## 17. Infrastructure and Deployment

Infrastructure and deployment procedures are documented in the companion [`operations.md`](operations.md). That document covers:

- Git hooks configuration
- Branch model (main + deploy)
- Deployment pipeline (feature branch → PR + CI → main → deploy → Plesk webhook)
- Deployment verification checklist
- GT&C acceptance log management
- Curation pipeline operational procedures
- Operational decisions (OTD-06, OTD-07)
- Release workflow

The split follows the principle that architecture.md defines **what** the deployment infrastructure looks like; operations.md defines **how** to operate it.

---

## 18. Testing Strategy

### 18.1 Overview

The testing strategy covers quality gates the BST must pass before go-live. Tests are traceable to design elements and FD requirements via the project traceability matrix.

### 18.2 Unit tests (pytest)

| Scope | What is tested | Coverage target |
|---|---|---|
| Tier 1 parsers | Each parser produces correctly structured output from sample input files | 100% statement coverage per parser module |
| `schema_gen.py` | Generated JSON schema matches data dictionary attribute definitions | All data types and enum values covered |
| `consensus.py` | Majority-rules logic for 3-of-3, 2-of-3, 2-of-2, 1-of-N, 0-of-N scenarios | All degradation rule branches covered |
| `validator.py` | Schema validation accepts valid KB, rejects invalid KB, rejects missing disclaimer | Positive and negative cases for each validation rule |
| `assembler.py` | Merge logic: new baseline added, existing baseline replaced, unaffected baseline preserved | All merge scenarios covered |
| `staleness.py` | Correct computation of stale attributes from TTL metadata | Boundary cases: exactly at TTL, one day overdue, no stale attributes |

All external calls (HTTP, LLM APIs) are mocked in unit tests per AGENTS.md §Test external call isolation. Mocks use pytest's `monkeypatch` or module-scoped fixtures.

### 18.3 Integration tests

| Scope | What is tested |
|---|---|
| Tier 2b pipeline end-to-end | Pipeline orchestration with mocked LLM adapters: source loading → model calls → consensus → per-baseline JSON output → assembly → validation |
| KB schema round-trip | Generated schema from `schema_gen.py` validates a known-good `baselines.json` fixture |

### 18.4 Schema validation (CI)

CI validates `data/baselines.json` against `src/schemas/baselines.schema.json` on every PR. This is a blocking gate — PRs with invalid KB data cannot merge.

Additional CI checks:
- Disclaimer block presence in `baselines.json`
- Staleness advisory (non-blocking)
- robots.txt presence
- Secrets scan (detect-secrets)
- Static type checking (mypy)
- Linting (configured per factory CI template)

### 18.5 Deployment verification (manual)

The deployment verification checklist in operations.md serves as the end-to-end acceptance test for the deployed application. It covers:
- Application availability and routing
- Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy)
- KB gating (direct URL → 403; API endpoint → 200)
- Rate limiting
- robots.txt
- Disclaimer visibility
- Export completeness

### 18.6 Security testing

| Test | Method | Frequency |
|---|---|---|
| Security headers | Deployment verification checklist; automated header inspection | Every deployment |
| Direct KB access blocked | `curl` test against `data/baselines.json` URL | Every deployment |
| Rate limiting | Rapid repeated requests; verify 429 response | Every deployment |
| Bot user-agent rejection | Request with known bot user-agent; verify 403 | Every deployment |
| CSP enforcement | Browser DevTools console; verify no CSP violations during normal use | UAT |
| XSS resilience | Verify no inline scripts; CSP blocks `unsafe-inline` | Code review + UAT |

### 18.7 Accessibility testing

Not in scope for v1. The BST is an internal tool used by the Human Maintainer. Accessibility testing will be introduced when external clients are onboarded (v2+).

### 18.8 UAT integration

The FD defines UAT entry criteria (§18.1), scope (§18.3), and exit criteria (§18.4). The testing strategy ensures all automated quality gates pass before UAT begins. UAT is the final gate before go-live.

---

## 19. Design Decisions Log

Technical design decisions that arose during authoring. Each decision records status, rationale, and traceability to the section it affects.

| ID | Decision | Status | Rationale | Affects |
|---|---|---|---|---|
| DD-01 | Split TD into architecture.md + operations.md | Resolved | Architecture decisions and operational procedures serve different audiences (developers vs. operators) and change at different frequencies. Keeps each document focused. | §17 (cross-reference) |
| DD-02 | Client-side recommendation engine (not server-side) | Resolved | TC-01 (no persistent server process) and FR-P06 (no external calls at request time) require all logic to execute in the browser. Eliminates server-side state and reduces PHP complexity. Trade-off: weight vector visible in `app.js` source; accepted per RR-03 (IP extraction via devtools is accepted residual risk). | §13.7 |
| DD-03 | Disclaimer sourced from KB JSON, not hardcoded | Resolved | Updates to disclaimer text flow through the standard curation pipeline without code changes. Version-controlled alongside the data it describes. Eliminates drift between KB version and disclaimer version. | §13.5 |
| DD-04 | No API versioning in v1 | Resolved | Single endpoint, single consumer (the SPA). Versioning overhead is not justified until v2 introduces tenant-scoped responses or external API consumers. | §12.2 |
| DD-05 | Sequential model calls (not parallel) for Tier 2b | Resolved | Factory laptop memory constraints (TA-02) may not support running 3 models simultaneously. Sequential execution is simpler, debuggable, and sufficient for manual curation cadence. Parallel execution is an optimisation for v2 if pipeline runtime becomes a bottleneck. | §13.6 |
| DD-06 | No accessibility testing in v1 | Resolved | Single-operator internal tool (BC-08, A-01). EN 301 549 and WCAG compliance required when external clients are onboarded (v2+). Noted in §18.7. | §18.7 |

### Open technical decisions

Architecture-scoped decisions pending resolution before or during implementation.

| ID | Decision | Status |
|---|---|---|
| OTD-01 | PHP framework vs. vanilla PHP for index.php | Vanilla PHP sufficient for v1. Revisit if v2 auth complexity justifies a micro-framework (Slim). |
| OTD-02 | Alpine.js version pinning | Pin to a specific release before implementation. |
| OTD-03 | GitHub API authentication for SSG parser | Unauthenticated rate limit (60 req/hr) sufficient for manual curation. Add token if pipeline is run frequently. |
| OTD-04 | CIS PDF parsing approach | Free CIS PDF is not machine-readable. Tier 1 limited to metadata visible in PDF structure. Full attribute coverage requires Tier 2. Accepted constraint. |
| OTD-05 | Export format implementation | Both UC-06a and UC-06b confirmed in v1. Print CSS for UC-06a; JS file generation for UC-06b. |

Operational decisions (OTD-06, OTD-07) are tracked in [`operations.md`](operations.md) §Operational decisions.

---

*End of Technical Design — Baseline Selection Tool*

*Paired document: [`functional-design.md`](functional-design.md) (FD-BST-001 v1.0.0)*
*Companion: [`operations.md`](operations.md)*
