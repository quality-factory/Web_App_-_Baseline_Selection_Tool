# Technical Design — Baseline Selection Tool (BST) v1.0

**Status:** Final — pending Human Maintainer approval
**Scope:** Phase a — baseline selection and comparison
**Input document:** Functional Design — BST v1.0
**Factory alignment:** SubscriptionFactory.md v13.3.0
**Date:** 2026-03-31

---

## Table of Contents

1. [Technical Constraints](#1-technical-constraints)
2. [Architecture Overview](#2-architecture-overview)
3. [Scenario Evaluation — Server-Side Technology](#3-scenario-evaluation--server-side-technology)
4. [Scenario Evaluation — Data Storage](#4-scenario-evaluation--data-storage)
5. [Scenario Evaluation — Frontend Framework](#5-scenario-evaluation--frontend-framework)
6. [Scenario Evaluation — Curation Pipeline Interface](#6-scenario-evaluation--curation-pipeline-interface)
7. [Scenario Evaluation — Knowledge Base Serving Mechanism](#7-scenario-evaluation--knowledge-base-serving-mechanism)
8. [Selected Architecture](#8-selected-architecture)
9. [Data Format Specification](#9-data-format-specification)
10. [Component Design](#10-component-design)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Sovereignty Classification](#12-sovereignty-classification)
13. [Open Technical Decisions](#13-open-technical-decisions)

---

## 1. Technical Constraints

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

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Factory Laptop (sovereign execution environment)             │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Curation Pipeline  [Python]                         │     │
│  │  ├── Tier 1: automated source parsers               │     │
│  │  ├── Tier 2: human-assisted retrieval CLI           │     │
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

---

## 3. Scenario Evaluation — Server-Side Technology

**Selected: S1-B — PHP thin layer + static frontend**

**Rationale:** TC-09 (KB not bulk-downloadable) and TC-10 (rate limiting) both require PHP execution. S1-A (static-only) cannot satisfy TC-09 without Apache module support that is not guaranteed on shared hosting. Additionally, FR-P16 (acceptance log) and FR-P15 (configurable footer URLs) both benefit from PHP. S1-B satisfies all requirements with minimal added complexity and positions the PHP layer for v2 auth extension without structural change. S1-C (full PHP application) is disproportionate to v1 scope.

| Scenario | Description | Verdict |
|---|---|---|
| S1-A | Static site, .htaccess only | ❌ Cannot satisfy TC-09 or TC-10 reliably |
| **S1-B** | **PHP thin layer + static frontend** | **✅ Selected** |
| S1-C | PHP application serving data server-side | ❌ Disproportionate complexity |

---

## 4. Scenario Evaluation — Data Storage

**Selected: S2-A — Single versioned JSON file**

**Rationale:** The JSON file satisfies all FD functional requirements (FR-K01 through FR-K04) with minimal complexity. Git provides richer version history than any audit table. File size (14 baselines × 40 attributes × provenance ≈ 200–400 KB uncompressed) is acceptable. Combined with PHP-gated serving (S7-B), it meets BC-10. MySQL (S2-B) adds operational overhead — credentials, migration scripts, PHP PDO layer — not justified by v1 scale. S2-C (split storage) is the natural v2 migration path when tenant and session data are introduced.

| Scenario | Description | Verdict |
|---|---|---|
| **S2-A** | **Single versioned JSON file** | **✅ Selected** |
| S2-B | MySQL database on shared hosting | ❌ Unnecessary complexity for v1 |
| S2-C | Split: JSON catalogue + MySQL for dynamic data | Equivalent to S2-A in v1; v2 migration path |

---

## 5. Scenario Evaluation — Frontend Framework

**Selected: S3-B — Alpine.js**

**Rationale:** Alpine.js (~15 KB, MIT licence) provides reactive state management for UC-03 (comparison table) and UC-04a/UC-04b (wizard state) at negligible dependency cost and with no build step. The disclaimer rendering (FR-P08) benefits from reactive components. S3-A (vanilla JS) is viable but produces significantly more complex code for interactive stories. S3-C (Vue/React) is disproportionate for nine stories and introduces a build toolchain with supply-chain implications.

| Scenario | Description | Verdict |
|---|---|---|
| S3-A | Vanilla JavaScript | ❌ Viable but disproportionately complex |
| **S3-B** | **Alpine.js (~15 KB, MIT, no build step)** | **✅ Selected** |
| S3-C | Vue.js or React (full framework) | ❌ Disproportionate; build toolchain adds supply-chain risk |

---

## 6. Scenario Evaluation — Curation Pipeline Interface

**Selected: S4-A — Command-line interface only**

**Rationale:** CLI is sufficient for a single curator and keeps the pipeline simple, auditable, and consistent with the factory's CLI-first approach. The two-pass Tier 3 scoring (OFD-01 resolution) is straightforward to implement as a CLI workflow with a time-gate check. A local web UI (S4-B) adds development time not justified by v1 scope.

| Scenario | Description | Verdict |
|---|---|---|
| **S4-A** | **CLI only** | **✅ Selected** |
| S4-B | Local web UI (localhost, on-demand) | ❌ Disproportionate for v1; revisit if usability evidence warrants |

---

## 7. Scenario Evaluation — Knowledge Base Serving Mechanism

**Selected: S7-B — PHP-gated endpoint with rate limiting**

**Rationale:** S7-A (static file with .htaccess restriction) provides only cosmetic protection — `curl https://example.com/data/baselines.json` retrieves the complete KB regardless of .htaccess browser navigation blocks. This is inconsistent with BC-10 and FR-P09. S7-B routes all KB access through a PHP endpoint that enforces per-IP rate limiting, user-agent filtering, and response headers. The residual risk (full JSON visible in browser devtools network tab for legitimate users) is accepted — the protection goal is automated bulk extraction prevention, not cryptographic inaccessibility. S7-B requires S1-B (confirmed above).

| Scenario | Description | Verdict |
|---|---|---|
| S7-A | Static file with .htaccess restriction | ❌ Cosmetic only; curl bypasses it |
| **S7-B** | **PHP-gated endpoint with rate limiting** | **✅ Selected** |

---

## 8. Selected Architecture

| Decision | Selected scenario | Rationale summary |
|---|---|---|
| Server-side technology | S1-B: PHP thin layer + static frontend | Required for rate limiting, KB gating, acceptance logging |
| Data storage | S2-A: Single versioned JSON file | Satisfies all FD requirements; minimal complexity |
| Frontend framework | S3-B: Alpine.js | Reactive state at negligible cost; no build step |
| Curation pipeline interface | S4-A: CLI only | Sufficient for single curator; consistent with factory approach |
| Knowledge base serving | S7-B: PHP-gated endpoint | Required by BC-10 and FR-P09; S7-A is cosmetic only |

---

## 9. Data Format Specification

### 9.1 Knowledge base schema

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
      "data_type": "Boolean | Enum | Date | Integer | Free text | URL",
      "objective_subjective": "Objective | Subjective",
      "stability": "Static | Per release | Annual | Continuous",
      "obtainability": "Easy | Moderate | Difficult",
      "primary_source_type": "<string>",
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
          "missing_reason": null,
          "confidence": "High | Medium | Low | Inferred",
          "trust_tier": 1,
          "source": {
            "url": "<string>",
            "document": "<string>",
            "section": "<string>",
            "accessed": "<ISO8601 date>"
          },
          "collection_method": "automated_parse | human_curation | analyst_scoring | community_aggregation",
          "curator_id": "<anonymised reference>",
          "review_date": "<ISO8601 date>",
          "ttl_days": 365
        }
      }
    }
  ]
}
```

*The `disclaimer` block is version-controlled alongside the data it accompanies. Any rendering of a Recommendation or Export Result reads the disclaimer from this block — not from hardcoded strings.*

### 9.2 Stale attributes report schema

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

### 9.3 Acceptance log schema

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

*Retention: 2 years per privacy statement §8.2.1. Log is write-once; erasure handled per privacy statement §12.1.5 (administrative "beyond use" marking).*

---

## 10. Component Design

### 10.1 Repository structure

```
bst/
├── src/                        — curation pipeline (Python)
│   ├── parsers/
│   │   ├── base_parser.py
│   │   ├── disa_stig.py
│   │   ├── nist_ncp.py
│   │   ├── openscap_ssg.py
│   │   └── microsoft_sct.py
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
│   ├── architecture.md
│   ├── operations.md
│   └── xla.md
├── governance/
└── CLAUDE.md
```

*`web/config/settings.php` holds the configurable GT&C and privacy statement URLs (FR-P15). Updating these URLs requires no code change — only a config file edit and deployment.*

### 10.2 Curation pipeline modules

| Module | Responsibility |
|---|---|
| `base_parser.py` | Abstract base class; defines output contract for all Tier 1 parsers |
| `disa_stig.py` | Downloads and parses DISA STIG XCCDF/OVAL from DoD Cyber Exchange |
| `nist_ncp.py` | Queries NIST NCP REST API for checklist metadata |
| `openscap_ssg.py` | Reads OpenSCAP/SSG release metadata via GitHub API (unauthenticated) |
| `microsoft_sct.py` | Downloads and parses Microsoft SCT GPO backup XML |
| `retrieval_cli.py` | Tier 2 interactive CLI: presents retrieved source passages for curator confirmation |
| `scoring_cli.py` | Tier 3 interactive CLI: enforces two-pass workflow with minimum 48h gap; fixes confidence at Medium |
| `assembler.py` | Merges all tier outputs; embeds disclaimer block from canonical source |
| `validator.py` | Validates schema conformance and disclaimer block presence; rejects on failure |
| `staleness.py` | Computes stale-attributes report from TTL metadata |

### 10.3 Web application modules

| File | Technology | Responsibility |
|---|---|---|
| `index.php` | PHP | SPA routing; security headers; per-IP rate limiting; GT&C acceptance logging (FR-P16) |
| `api/baselines.php` | PHP | PHP-gated KB endpoint: rate limit, bot user-agent rejection, serve baselines.json |
| `config/settings.php` | PHP | Configurable GT&C URL and privacy statement URL for footer (FR-P15) |
| `index.html` | HTML | SPA shell; loads Alpine.js and app.js |
| `app.js` | JS (Alpine.js) | All UI logic: data loading from /api/baselines.php, UC-01a/b, UC-02, UC-03, UC-04a/b (disclaimer rendering), UC-05, UC-06a/b (attribution + disclaimer injection) |
| `app.css` | CSS | Styling; print stylesheet for UC-06a (disclaimer non-suppressible) |
| `robots.txt` | Text | Disallow known AI crawlers and scrapers |

### 10.4 Security headers

| Header | Value |
|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `no-referrer` |

### 10.5 Rate limiting design

Per-IP rate limiting implemented in PHP via APCu (preferred) or file-based counters (fallback if APCu unavailable — see OTD-07). Returns HTTP 429 with `Retry-After` on limit exceeded. Rate limit events logged. Internal counters and configuration not exposed in error responses.

### 10.6 robots.txt

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

*robots.txt is advisory; rate limiting (§10.5) is the enforcement layer.*

### 10.7 Disclaimer handling in JavaScript

The disclaimer text is read from the `disclaimer` block in `baselines.json` at startup. `app.js` must:

1. Extract disclaimer on load.
2. Render disclaimer as a non-removable, non-collapsible component in UC-04b results.
3. Inject disclaimer into all UC-06a (print CSS) and UC-06b (markdown generation) exports.
4. Never render a recommendation without the accompanying disclaimer.

Disclaimer text is sourced exclusively from the knowledge base — not hardcoded — so updates flow through the standard curation and deployment pipeline without code changes.

### 10.8 GT&C acceptance logging

The acceptance event is logged in `index.php` when the user submits the GT&C agreement (from the website-layer popup). The log entry (§9.3 schema) is written server-side before the user is permitted to load the SPA. Log file is write-once/append-only where the hosting environment supports it. APCu availability for deduplication within a session is OTD-07.

---

## 11. Deployment Architecture

### 11.1 Branch model

| Branch | Purpose | Protection |
|---|---|---|
| `main` | Default; all development merges here | CI required; squash merge; no direct push |
| `deploy` | Plesk deploys from here | Human Maintainer merge only; no direct push |

### 11.2 Deployment pipeline

```
Feature branch
      │  PR + CI pass:
      │    lint, type check, tests, secrets scan
      │    baselines.json schema validation
      │    disclaimer block presence check
      │    staleness advisory check
      │    robots.txt presence check
      ▼
main
      │  Human Maintainer merges to deploy
      ▼
deploy branch → Plesk webhook → shared host
  Target: httpdocs/my/bst/ → qualityfactory.com/my/bst/
  Deployed: web/ contents + data/baselines.json
  Excluded: src/, tests/, docs/, governance/,
            data/stale-attributes.json
  Pre-condition: webmaster CR changes 1a and 4 must be in
    place before first deployment (domain restriction on
    httpdocs/my/ + X-Frame-Options override in .htaccess)
```

### 11.3 Deployment verification checklist

After every deployment, verify:

- [ ] Application loads at `https://www.qualityfactory.com/my/bst/`
- [ ] Same path on any other mapped domain → 403 Forbidden (domain restriction working)
- [ ] `https://www.qualityfactory.com/my/bst/data/baselines.json` → 403 Forbidden
- [ ] `https://www.qualityfactory.com/my/bst/api/baselines.php` → KB content with correct headers
- [ ] Rate limiter triggers on rapid repeated requests
- [ ] `https://www.qualityfactory.com/my/bst/robots.txt` → accessible, contains required entries
- [ ] Disclaimer visible on wizard results without any dismissal action
- [ ] Footer links point to correct GT&C and privacy statement URLs
- [ ] Response headers for BST page: exactly one `X-Frame-Options: DENY` (not SAMEORIGIN, not both)
- [ ] CSP header present and correct

Full checklist maintained in `docs/operations.md`.

---

## 12. Sovereignty Classification

| Component | Provider | Classification | Exit strategy |
|---|---|---|---|
| Shared hosting | See sovereignty classification artefact | Pending | Required if class (b) |
| GitHub (source control, CI) | Microsoft (US) | (b) Tolerable with exit strategy | Git distributed; full local copy always available; CI workflows portable YAML |
| GitHub Actions (CI) | Microsoft (US) | (b) Tolerable with exit strategy | Workflow definitions portable to GitLab CI, Forgejo, or equivalent |

*Full sovereignty classification is maintained in the separate BST Sovereignty Classification artefact.*

---

## 13. Open Technical Decisions

| # | Decision | Unblock condition |
|---|---|---|
| OTD-01 | PHP framework vs. vanilla PHP for index.php | S1-B is selected; vanilla PHP is sufficient for v1. Revisit if auth middleware complexity justifies a micro-framework (Slim) in v2. |
| OTD-02 | Alpine.js version pinning | Pin to a specific Alpine.js release in the lockfile before implementation. |
| OTD-03 | GitHub API authentication for SSG parser | Unauthenticated rate limit (60 req/hr) is sufficient for manual curation. Add token if pipeline is run frequently. |
| OTD-04 | CIS PDF parsing approach | Free CIS PDF is not machine-readable. Tier 1 limited to metadata visible in PDF structure. Full attribute coverage requires Tier 2. Document in operations guide as accepted constraint. |
| OTD-05 | Shared hosting sovereignty classification | Complete the BST Sovereignty Classification artefact (task 8). Required before first deployment. |
| OTD-06 | Export format implementation | Both UC-06a and UC-06b confirmed in v1 (OFD-03). Print CSS for UC-06a; JS file generation for UC-06b. |
| OTD-07 | APCu availability on shared hosting | Verify before implementation. File-based rate limiting is the fallback. Document in operations guide. |
| OTD-08 | Acceptance log write-once implementation | Depends on hosting environment capabilities. Assess whether append-only file or database table is available. Document in operations guide. |
| OTD-09 | Subdomain migration path | The BST is deployed at `qualityfactory.com/my/bst/` — the `/my/` prefix mirrors the future subdomain name, making migration a clean path promotion. When the factory grows sufficiently, migration to `my.qualityfactory.com/bst/` simply requires creating the subdomain with a dedicated document root; the `/bst/` path segment and all application code remain unchanged. Future tools follow the same pattern: `qualityfactory.com/my/[tool]/` → `my.qualityfactory.com/[tool]/`. The domain restriction rule on `httpdocs/my/` covers all current and future tools in one rule. Hosting.nl has confirmed the required DNS records: A-record `my.qualityfactory.com → 37.46.140.10`, AAAA-record `my.qualityfactory.com → 2a01:518:1:1041::10`. No application code changes required on migration. |

---

*End of Technical Design — BST v1.0*
*Related: Functional Design — BST v1.0*
