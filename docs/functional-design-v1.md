# Functional Design — Baseline Selection Tool (BST) v1.0

**Status:** Final — pending Human Maintainer approval
**Scope:** Phase a — baseline selection and comparison
**Factory alignment:** SubscriptionFactory.md v13.5.0
**Date:** 2026-03-31

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Business Constraints](#2-business-constraints)
   - [2.1 Usage Governance Policy](#21-usage-governance-policy)
3. [Functional Context](#3-functional-context)
4. [Users and User Stories](#4-users-and-user-stories)
5. [Conceptual Data Model](#5-conceptual-data-model) — attribute catalogue in companion [`data-dictionary-v1`](functional-design_-_data-dictionary-v1.md)
6. [Subsystem Functional Requirements](#6-subsystem-functional-requirements)
7. [User Interface Requirements](#7-user-interface-requirements)
8. [Recommendation Logic](#8-recommendation-logic)
9. [Multi-Tenancy Requirements](#9-multi-tenancy-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Functional Decision Log](#11-functional-decision-log)
12. [Out of Scope — v1](#12-out-of-scope--v1)

---

## 1. Purpose and Scope

### 1.1 What this document covers

This functional design specifies the Baseline Selection Tool (BST) v1 — a web-based application that helps users select an appropriate security hardening baseline for their workstation environment. It defines what the system must do, for whom, and under which constraints, expressed entirely in functional terms. It does not specify how the system achieves this; those decisions are in the companion [`architecture.md`](architecture.md).

This document is technology-agnostic. It remains valid regardless of which technical scenario the architecture selects.

### 1.2 Problem statement

Security hardening baselines are numerous, structurally different, and poorly compared in publicly available resources. Practitioners currently choose baselines by familiarity or mandate rather than by systematic fit with their environment. The BST makes this choice systematic, transparent, and auditable — first for the factory's own workstation hardening, then as a commercial SaaS product.

### 1.3 Immediate use case

The factory's own Ubuntu 24.04 LTS workstation baseline was chosen opportunistically without research. The BST is first applied to re-evaluate that choice systematically, then the result is integrated into the laptop initiation guide with the selected baseline properly justified.

### 1.4 Commercial trajectory

The BST is designed to be commercialised as a SaaS subscription product. IP protection is achieved by delivering the tool as a web service rather than distributable software — clients interact via browser; the knowledge base and selection logic remain server-side. The factory eats its own dog food first.

### 1.5 Phase scope

This FD covers phase a (baseline selection) only. Phase b (guidance integration) and phase c (compliance auditing) are separate future deliverables, explicitly deferred. No architectural decision in v1 may foreclose those phases.

### 1.6 Scope of protection and accepted risk

The BST is a commercially developed and maintained tool representing a significant investment of time and expertise. This document governs two categories of business risk as first-class design requirements: intellectual property extraction and legal liability. See §2.1.

GT&C preparation status and accepted risk: see §2.1.1. Go-live gate: see §12. Legal review requirements: see §10.6.

---

## 2. Business Constraints

| # | Constraint | Source |
|---|---|---|
| BC-01 | Operating expenditure cap: 300 EUR/month total factory spend | §Operational Constraints #2 |
| BC-02 | Baseline data sources must be freely and publicly accessible; no paid memberships | Factory Owner decision |
| BC-03 | Zero Trust posture applies throughout | §Security Model (Zero Trust) |
| BC-04 | The system must not write to managed devices or management systems | §Operational Constraints #10 |
| BC-05 | No PII is processed by the BST as a primary application function. Infrastructure logging — including GT&C acceptance events — is governed by the Factory Owner's privacy statement §8.2.1 (user action logs, Art. 6(1)(f) AVG, 2-year retention) | §Explicit Non-Goals; Factory Owner privacy statement v5.2 |
| BC-06 | All infrastructure must be classifiable under the factory's sovereignty taxonomy | §Operational Constraints #5 |
| BC-07 | The presentation subsystem must be deployable on the factory's existing shared hosting environment | Q5 decision |
| BC-08 | The curation subsystem must be executable on the factory laptop without external services beyond LLM API calls used by the curation subsystem | §Operational Constraints #5 |
| BC-09 | All tools and libraries must have clearly understood licensing terms | §Operational Constraints #4 |
| BC-10 | The knowledge base content, attribute scoring methodology, recommendation logic, and selection rubrics are proprietary intellectual property of the Factory Owner and must be protected against extraction and unauthorised reuse | Factory Owner business requirement |
| BC-11 | The BST is a decision-support tool, not a professional security advisory service. The Factory Owner's liability must be explicitly and consistently limited through mandatory disclaimers, terms of use, and design choices that prevent the tool from being mistaken for professional advice | Factory Owner business requirement |

### 2.1 Usage Governance Policy

#### 2.1.1 Intellectual property

The DevOps investment required to develop, curate, and maintain the BST represents a significant commercial asset. This asset must be protected by design.

**What is protected:** The complete knowledge base, scoring rubrics, recommendation methodology, and comparative analysis approach. These are proprietary even where underlying source data is publicly derivable, because their curation, validation, organisation, and contextualisation represent the Factory Owner's intellectual work.

**Protection requirements:**

1. The knowledge base must not be exposed as a directly accessible or bulk-downloadable resource. Users access results of queries — not the knowledge base itself.
2. No single user action may retrieve the complete dataset in a single operation.
3. Exports (UC-06a, UC-06b) are scoped to the comparison or recommendation result only — not the underlying knowledge base. Exports carry attribution identifying the Factory Owner as the source.
4. Automated access by bots, scrapers, crawlers, or AI agents must be technically deterred and contractually prohibited.
5. The GT&C must prohibit: systematic data extraction, use of tool outputs to train machine learning models, reproduction of tool content without attribution, and commercial use of extracted data.

**GT&C status:** The GT&C is currently in preparation. This is an accepted risk contingent on the BST remaining non-public until the GT&C is published. HTTP Basic Auth on the BST URL is the interim access control. See §12 (go-live gate) and §10.6.

#### 2.1.2 Limitation of liability

The Factory Owner operates exclusively B2B. Dutch commercial law (Boek 6 BW) applies to the contracting relationship. EU consumer protection law does not apply to the primary client base.

**Liability limitation requirements:**

1. Every recommendation output must carry a mandatory, prominent disclaimer — an integral, non-collapsible part of the result — stating:
   - The BST is a decision-support tool, not a professional security advisory service.
   - The recommendation is generated from a knowledge base that may contain inaccuracies, omissions, or outdated information.
   - The knowledge base version and generation date are shown; the user must assess currency.
   - The recommendation is based solely on the environment profile provided; other factors are not considered.
   - The user is solely responsible for independent validation before implementation.
   - The Factory Owner accepts no liability for security outcomes resulting from reliance on BST recommendations.

2. The disclaimer must be integral and non-collapsible. It must appear as part of the recommendation output, never as a dismissible modal.

3. The GT&C must be displayed before access to tool outputs. In v1, a cookie-based agreement popup at the website layer provides acceptance recording (implemented by the webmaster). The BST application logs acceptance events server-side per FR-P16.

4. The tool must never use language implying certainty, guarantee, or endorsement.

5. Every data point displayed must show its source and access date.

#### 2.1.3 Agentic access policy

1. The tool must publish a robots.txt prohibiting access by known AI crawler and scraper user agents.
2. The server must implement rate limiting constraining requests per IP address, regardless of user agent.
3. The GT&C must explicitly prohibit automated access, crawling, scraping, and feeding BST output into AI training pipelines.
4. The BST must not expose any programmatic API enabling automated bulk extraction of knowledge base content.

---

## 3. Functional Context

### 3.1 Subsystem overview

**Curation Subsystem** — Collects, validates, scores, and assembles attribute values via a multi-model LLM consensus pipeline. Calls multiple LLM APIs to extract structured attribute values from publicly accessible baseline documentation, aggregates results via majority-rules consensus, and outputs knowledge store-conformant JSON with full provenance records. Operates on the factory laptop. LLM API calls are the only external dependency. Never runs in the hosted environment.

**Knowledge Store** — Persists curated attribute values with full provenance, versioning, and staleness tracking. Single source of truth for the presentation subsystem.

**Presentation Subsystem** — Delivers the selection and comparison interface via web browser. Stores no user data as a primary function. Enforces IP and liability protections from §2.1.

### 3.2 Subsystem interaction model

```
Primary sources ──► Curation Subsystem ──► Knowledge Store ──► Presentation Subsystem ──► User
(URLs to public       (factory laptop)        (versioned,          (hosted environment)
 documentation)       │                        deployed artefact)   IP + liability controls
                      ├── LLM API calls
                      │   (structured extraction)
                      └── Consensus aggregation
```

The curation subsystem directs LLMs to known primary source URLs rather than relying on general web search (source grounding principle). The curation subsystem and presentation subsystem never interact directly at runtime. The knowledge store is the only transfer mechanism between them.

---

## 4. Users and User Stories

### 4.1 Users — v1

| User role | Description | v1 access model |
|---|---|---|
| Security Practitioner | A person responsible for selecting and implementing a security hardening baseline | Browser access; GT&C agreement popup (website layer); no application-level auth in v1 |
| Automated agent / bot | Any non-human system attempting programmatic access | Prohibited by GT&C; deterred by robots.txt and rate limiting |
| Future SaaS client | An organisation subscribing to the BST as a service | Subscription-gated; not implemented in v1 |

In v1, the Security Practitioner role is fulfilled by the Human Maintainer.

### 4.2 User stories

---

#### UC-01a — View baseline catalogue

**Story**

As a Security Practitioner,
I want to view all available baselines with their key attributes at a glance,
So that I can quickly identify candidates worth investigating further without opening each one individually.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅

**Acceptance criteria**

```gherkin
Given the BST is open
When I navigate to the baseline browser
Then I see the GT&C agreement notice before any baseline content is visible

Given the BST is open
When I navigate to the baseline browser
Then I see all in-scope baselines, each displaying name, issuer,
  baseline type, OS platform support indicators, and an overall
  confidence indicator

Given at least one baseline has a missing value on a displayed attribute
When I view the baseline browser
Then that missing state is visually distinct from a low-confidence value

Given the knowledge base contains baselines
When the browser loads
Then the total baseline count and the knowledge base version and
  generation date are visible
```

---

#### UC-01b — Filter baseline catalogue

**Story**

As a Security Practitioner,
I want to filter the baseline catalogue by operating system and baseline category,
So that I can reduce the visible set to baselines relevant to my environment without leaving the page.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅ *(Note on I: logical dependency on UC-01a, no technical dependency)*

**Acceptance criteria**

```gherkin
Given I am on the baseline browser
When I select "Ubuntu 24.04" as the OS filter
Then only baselines with Ubuntu 24.04 coverage are displayed
  and the visible baseline count updates immediately

Given I am on the baseline browser
When I select a baseline category filter
Then only baselines of that category are displayed

Given I have applied one or more filters
When I clear all filters
Then all baselines are displayed again

Given I apply filters that match no baselines
When the filter is applied
Then a message states that no baselines match the current filter
  and a "clear filters" action is available
```

---

#### UC-02 — View baseline detail

**Story**

As a Security Practitioner,
I want to view the complete attribute profile of a single baseline including the provenance of each value,
So that I can assess the basis for every attribute before relying on it in a selection decision.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅

**Acceptance criteria**

```gherkin
Given I select a baseline
When the detail view opens
Then all 45 attributes are displayed grouped by category,
  each showing value, confidence level, and trust tier

Given I am viewing a baseline detail
When I expand the provenance record for an attribute
Then I see source document name, section reference, URL,
  access date, collection method, and curator reference

Given a baseline has a missing attribute value
When I view that attribute in the detail view
Then the missing state is clearly indicated and the reason for
  absence is visible without further interaction

Given I am viewing a baseline detail
When I collapse one attribute category
Then all other categories are unaffected

Given I am viewing a baseline detail
When I view the page
Then a notice states that attribute values are sourced from
  third parties and may not reflect the current state of the
  referenced baseline

Given I am viewing an attribute value I believe is incorrect
When I select "Flag this value"
Then a pre-filled GitHub issue opens in a new tab containing
  the baseline ID, attribute ID, current value, and a field
  for the user to describe the correction
```

---

#### UC-03 — Compare baselines

**Story**

As a Security Practitioner,
I want to compare two to four baselines side by side across all attributes,
So that I can identify the differences that are material to my selection decision.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅

**Acceptance criteria**

```gherkin
Given I have selected two baselines for comparison
When the comparison view renders
Then a table is displayed with one column per baseline and one row
  per attribute, showing value, confidence level, and missing state

Given I am viewing a comparison
When I enable the "differences only" toggle
Then only rows where the selected baselines have non-identical values
  are displayed

Given a cell contains a missing value
When I view the comparison table
Then that cell is visually distinct from both low-confidence cells
  and high-confidence cells

Given I am viewing a comparison with two baselines
When I add a third baseline via the selector
Then a third column is added without resetting the current view state

Given I am viewing a comparison
When I collapse an attribute category
Then all rows in that category are hidden and the category header
  remains visible
```

---

#### UC-04a — Answer selection wizard questions

**Story**

As a Security Practitioner,
I want to answer structured questions about my environment and requirements,
So that the system has enough context to filter and rank applicable baselines on my behalf.

**INVEST** — I✅ N✅ V⚠️ E✅ S✅ T✅ *(Note on V: limited standalone value without UC-04b; delivered together)*

**Acceptance criteria**

```gherkin
Given I navigate to the wizard
When the wizard opens
Then I see the first question with a plain-language explanation of
  why it matters and a progress indicator showing position in the
  total question sequence

Given I am answering wizard questions
When I answer a question and advance
Then I can navigate back to any previous question and change my answer

Given I have answered all questions
When I confirm my answers
Then I am taken to the wizard results view (UC-04b)

Given I leave the wizard before completing all questions
When I return to the wizard
Then no partial state has been saved or pre-filled
```

---

#### UC-04b — View wizard recommendation

**Story**

As a Security Practitioner,
I want to see a ranked list of baselines with a plain-language explanation of each ranking,
So that I can make an informed selection decision and understand what drove it.

**INVEST** — I⚠️ N✅ V✅ E✅ S✅ T✅ *(Note on I: sequential dependency on UC-04a; delivered together)*

**Acceptance criteria**

```gherkin
Given I have completed the wizard
When the results are displayed
Then I see a ranked list of baselines, each with a match score and a
  plain-language explanation of which attributes drove the ranking

Given a recommended baseline has missing values on high-weight attributes
When that baseline appears in the ranked list
Then its entry is marked as low-confidence with an explicit statement
  of which attributes were missing and how that affected confidence

Given one or more baselines were excluded by hard filters
When I view the results
Then excluded baselines appear in a separate section with the
  reason for each exclusion stated

Given I am viewing wizard results
When I select "Compare top results"
Then the comparison view opens pre-populated with the top-ranked baselines

Given I am viewing wizard results
When I change any of my answers
Then the results update to reflect the revised environment profile

Given I am viewing wizard results
When the recommendation is displayed
Then the mandatory disclaimer per §2.1.2 is shown as an integral,
  non-collapsible part of the results

Given I am viewing wizard results
When I read the recommendation text
Then no language implies certainty, guarantee, or endorsement
```

---

#### UC-05 — Look up attribute definition

**Story**

As a Security Practitioner,
I want to look up the definition, scoring rubric, and metadata for any attribute,
So that I can understand what I am comparing before interpreting values.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅

**Acceptance criteria**

```gherkin
Given I navigate to the attribute dictionary
When the dictionary loads
Then all 45 attributes are listed alphabetically showing category,
  data type, and a one-sentence plain-language definition

Given I select an attribute in the dictionary
When the attribute detail opens
Then I see the full definition, objectivity classification, stability,
  obtainability, and — for subjective attributes — the complete
  scoring rubric with all Enum values defined

Given I am viewing an attribute entry
When I select "Compare this attribute across baselines"
Then the comparison view opens filtered to show that single attribute
  across all in-scope baselines
```

---

#### UC-06a — Export as PDF

**Story**

As a Security Practitioner,
I want to print the comparison view or wizard results as a PDF,
So that I have a self-contained document I can attach to governance records.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅

*IP note: the print path cannot technically prevent a user from printing a full detail view. The protection is that no single action exposes the entire knowledge base — one baseline at a time in detail view, two to four in comparison. Accepted residual risk.*

**Acceptance criteria**

```gherkin
Given I am viewing a comparison or wizard results
When I select "Export as PDF"
Then the browser print dialog opens with a print-optimised layout

Given the print dialog is open
When I preview the output
Then the document contains the baselines compared, the environment
  profile if from the wizard, all attribute values and confidence
  levels, and the export date — without truncation

Given the print dialog is open
When I preview the output
Then interactive elements and navigation chrome are not present

Given the print dialog is open
When I preview the output
Then the document carries the Factory Owner's attribution and a
  copy of the liability disclaimer as defined in §2.1.2

Given the print dialog is open
When I preview the output
Then the document does not contain attribute data for baselines
  not part of the current comparison or wizard result
```

---

#### UC-06b — Export as markdown

**Story**

As a Security Practitioner,
I want to download the comparison or wizard results as a markdown file,
So that I can include it directly in governance documentation such as the laptop initiation guide without reformatting.

**INVEST** — I✅ N✅ V✅ E✅ S✅ T✅

**Acceptance criteria**

```gherkin
Given I am viewing a comparison or wizard results
When I select "Export as markdown"
Then a markdown file is downloaded with a descriptive filename
  including the export date

Given the downloaded file is opened in a standard markdown renderer
When I view the file
Then the document contains the baselines compared, the environment
  profile if from the wizard, the recommendation with plain-language
  reasoning if from the wizard, and the export date

Given the downloaded file is opened in a standard markdown renderer
When I view the file
Then all tables render correctly and no raw HTML is present

Given the downloaded file is opened in a standard markdown renderer
When I view the file
Then the document carries the Factory Owner's attribution, the
  knowledge base version and generation date, and the liability
  disclaimer as defined in §2.1.2

Given the downloaded file is opened in a standard markdown renderer
When I view the file
Then the file does not contain attribute data for baselines
  not part of the current comparison or wizard result
```

---

### 4.3 Story map

| Story ID | Title | Depends on |
|---|---|---|
| UC-01a | View baseline catalogue | — |
| UC-01b | Filter baseline catalogue | UC-01a (logical) |
| UC-02 | View baseline detail | — |
| UC-03 | Compare baselines | — |
| UC-04a | Answer wizard questions | — |
| UC-04b | View wizard recommendation | UC-04a |
| UC-05 | Look up attribute definition | — |
| UC-06a | Export as PDF | UC-03 or UC-04b |
| UC-06b | Export as markdown | UC-03 or UC-04b |

---

## 5. Conceptual Data Model

### 5.1 Core entities

**Baseline** — A named security hardening specification issued by an authoritative body, described by 45 attributes.

**Attribute** — A named dimension of comparison across baselines, with definition, data type, objectivity classification, stability, and (for subjective attributes) a scoring rubric.

**Attribute Value** — The value of a specific attribute for a specific baseline, accompanied by a Provenance Record. Absent values are represented explicitly, never as blank or zero.

**Provenance Record** — Source identity, retrieval date, collection method, curator identity, and confidence assessment for every attribute value.

**Trust Tier** — Classification of the collection method (see §5.3). Governs acceptable uncertainty and required process.

**Disclaimer** — A mandatory structured text block carried by every recommendation output and every export. Defined in §2.1.2. First-class data entity inseparable from any Recommendation or Export Result.

**Environment Profile** — The set of answers provided by a user in UC-04a.

**Recommendation** — Ranked list of baselines for a given Environment Profile, with plain-language reasoning, hard-filter exclusions with reasons, and a mandatory Disclaimer.

**Export Result** — A user-generated document from a comparison or recommendation. Scoped to the generating view only — not the full knowledge base. Carries attribution and a copy of the Disclaimer.

### 5.2 Attribute categories

| Category | Count | Description |
|---|---|---|
| Identity & Classification | 6 | What the baseline is, who issues it, and for whom |
| Platform & Coverage | 7 | Which platforms, roles, and scope depths it addresses |
| Content Quality | 8 | How specific, well-maintained, and well-sourced the content is |
| Governance & Maintenance | 8 | How the baseline is governed, updated, reviewed, and retired |
| Access & Licensing | 3 | How the baseline can be obtained and used |
| Format & Parseability | 4 | In what form the baseline is published and whether it is programmatically processable |
| Tooling & Automation | 5 | What assessment and enforcement tooling exists |
| Applicability & Adoption | 4 | How widely used the baseline is and what it maps to |

### 5.3 Trust tier model

| Tier | Name | Collection method | Confidence ceiling |
|---|---|---|---|
| 1 | Machine-extractable | Automated ingestion from a machine-readable primary source | High |
| 2 | Document-verifiable | Human reads official publication, confirms value, records source citation | High |
| 2b | LLM-consensus-extracted | Multi-model LLM extraction with structured output constraints and majority-rules consensus (minimum 3 architecturally diverse models; 2-of-3 agreement required) | Medium |
| 3 | Analyst-scored | Two independent scoring passes by a qualified analyst, minimum 48h apart; confidence fixed at Medium regardless of agreement | Medium |
| 4 | Community-aggregated | Practitioner surveys or consensus; explicitly uncertain | Low |

### 5.4 Missing value policy

Missing values are never inferred, estimated, or filled with defaults. Every missing value is represented explicitly with a stated reason: paywalled, empirical-only, no source found, disputed, not applicable, or consensus-disagreement. Missing values on high-weight attributes reduce recommendation confidence — they are uncertainty signals, not negative scores.

When the Tier 2b consensus pipeline produces no agreement (fewer than 2 of 3 models agree), the value is recorded as missing with reason "consensus-disagreement." Individual model outputs are preserved in the provenance record for Human Maintainer review.

### 5.5 Attribute catalogue

The complete attribute catalogue — all 45 attributes with stable identifiers, data types, objectivity classifications, enum values, and scoring rubrics — is defined in the companion document [`data-dictionary-v1`](functional-design_-_data-dictionary-v1.md).

The data dictionary is the authoritative source for attribute definitions. Category counts and descriptions: see §5.2.

### 5.6 In-scope baselines — v1

| Baseline | In scope v1 | Access constraint |
|---|---|---|
| DISA STIG (Windows 11, Ubuntu 22.04) | Yes | Free |
| OpenSCAP / SCAP Security Guide | Yes | Free and open source |
| NIST National Checklist Program | Yes | Free |
| Microsoft Security Compliance Toolkit | Yes | Free |
| CIS Benchmarks | Yes | Free in PDF format |
| ACSC Essential Eight | Yes | Free |
| ANSSI Linux Guide | Yes | Free |
| Microsoft Intune Baselines | Metadata only | Full content requires Intune licence |
| CIS-CAT / SecureSuite | No | Paywalled |
| PCI DSS | Metadata only | Standard document is paid |
| ISO/IEC 27001 | Metadata only | Standard document is paid |
| HIPAA / HHS Guidance | Yes | Free |
| NIS2 / Cyber Resilience Act | Yes | Free |
| SOC 2 | Metadata only | AICPA criteria are paid |

---

## 6. Subsystem Functional Requirements

### 6.1 Curation Subsystem

**FR-C01** Tier 1 values collected from machine-readable primary sources without human inference. Process is repeatable.

**FR-C02** Tier 2 workflow: curator is presented with candidate content from official source and asked to confirm or correct. System assists retrieval; human makes the judgment.

**FR-C03** Tier 3 workflow: qualified analyst applies scoring rubric twice, minimum 48 hours apart. Disagreements flagged for resolution. Confidence fixed at Medium.

**FR-C04** Stale attribute values are detected automatically and the curator is alerted.

**FR-C05** Knowledge base is validated for completeness and schema conformance before deployment. Invalid output is rejected with a human-readable explanation.

**FR-C06** Full provenance record generated for every attribute value: source identity, retrieval date, collection method, curator identity, confidence assessment.

**FR-C07** Operable by a single person without external services beyond the ingested primary sources and LLM API calls.

**FR-C08** The curation subsystem MUST support Tier 2b collection via multi-model LLM consensus extraction. The pipeline MUST:
- (a) Accept a baseline identifier and one or more primary source URLs as input.
- (b) Call at least three LLM APIs from different providers using the same prompt and the same JSON schema derived from the data dictionary attribute catalogue.
- (c) Use structured output functions (JSON schema mode) to constrain LLM responses to the data dictionary's defined enum values and data types.
- (d) Require each LLM to produce a justification alongside each extracted value, citing the source document and reasoning, referencing one of the primary source URLs provided as input per FR-C10. URLs not provided as input MUST be rejected as potential hallucinations.
- (e) Aggregate via majority-rules consensus: a value is accepted when at least 2 of 3 models agree; values without consensus are recorded as missing with reason "consensus-disagreement."
- (f) Output one JSON file per baseline conforming to the knowledge store schema, with a complete provenance record per attribute value.

**FR-C09** The LLM models used in the consensus pipeline MUST be architecturally diverse (different model families from different providers). Architectural diversity MUST be verified, not assumed. Model selection MUST comply with BC-09 (licensing).

**FR-C10** The curation subsystem MUST direct LLMs to known primary source URLs listed in the data dictionary evidence base (§3), rather than relying on general web search. LLM outputs MUST be cross-referenced against published documentation.

**FR-C11** The curation subsystem MUST be executable on the factory laptop without external services beyond the LLM API calls themselves (BC-08). The default execution path is local-first, consistent with Operational Constraints #5 and BC-08: the pipeline MUST operate with locally hosted models (e.g., Ollama-compatible local HTTP API) as the primary path, requiring no remote API keys for default operation. Remote provider APIs are added when consensus diversity requires models not available locally. The core logic MUST use an API interface abstraction with no provider-specific dependencies; the local adapter is the first implementation built and tested. BC-05 confirms no PII is involved, permitting but not requiring public APIs.

**FR-C12 (Horizon 1, deferred)** Layer 2 (enum and schema validation) is implemented in Horizon 0 as part of FR-C08(c) and is therefore not listed here. The curation subsystem SHOULD support the following additional validation layers, to be implemented when triggered by catalogue expansion, commercial need, or Human Maintainer availability:
- (a) Layer 1: Human verification of Objective + Easy attributes against primary sources, using the initial Tier 2b knowledge base as the benchmark dataset.
- (b) Layer 3: Automated cross-attribute consistency rules enforced programmatically (e.g. `prescriptiveness: per_setting` requires `setting_count` to be non-null; `scap_compliance_level: scap_validated` requires `scap_xccdf` in `primary_format`).
- (c) Layer 4: Ongoing spot-checks on a random sample of values per pipeline run, with consensus disagreement rate drift monitoring.

### 6.2 Knowledge Store

**FR-K01** Complete history of attribute value changes is preserved. State at any prior point can be reconstructed.

**FR-K02** Deployable through the standard factory pipeline without manual transformation or migration steps.

**FR-K03** Explicit distinction between a value of zero or false, and the absence of a value.

**FR-K04** Staleness metadata per attribute value enables automated detection of values due for re-verification.

### 6.3 Presentation Subsystem

**FR-P01** All nine user stories (§4.2) delivered to a standard web browser without software installation on the client device.

**FR-P02** No user-supplied data stored in v1. No accounts, sessions, preferences, or interaction history persisted by the application.

**FR-P03** Confidence level and trust tier displayed for every attribute value. Uncertainty is visible.

**FR-P04** Missing values displayed as a distinct visual state, with the reason for absence visible on inspection. Never blank or zero.

**FR-P05** Exportable documents (UC-06a, UC-06b) are self-contained and suitable for governance documentation without further editing.

**FR-P06** No real-time calls to external data sources at request time. All data originates from the knowledge store.

**FR-P07** Operable on the factory's existing shared hosting environment without infrastructure changes.

**FR-P08** Mandatory disclaimer per §2.1.2 on every recommendation output (UC-04b). Integral, non-collapsible. The Disclaimer is a first-class component of the Recommendation entity.

**FR-P09** Knowledge base not exposed as a directly accessible or bulk-downloadable resource. No single user action retrieves the complete dataset. Exports scoped to the generating view's result set only.

**FR-P10** GT&C displayed before access to tool outputs. In v1, a cookie-based agreement popup at the website layer provides acceptance recording. Acknowledgment gating per FR-P16 is in place before go-live.

**FR-P11** All exports (UC-06a, UC-06b) carry: Factory Owner attribution, knowledge base version and generation date, and the full liability disclaimer as defined in §2.1.2.

**FR-P12** Server-side rate limiting on all content requests. Permits normal human browsing; constrains automated bulk extraction.

**FR-P13** robots.txt published, prohibiting known AI crawler, scraper, and automated agent user agents.

**FR-P14** Knowledge base version and generation date visible on every view presenting baseline data.

**FR-P15** Every page includes a persistent footer containing: (a) a configurable link to the Factory Owner's GT&C, and (b) a configurable link to the Factory Owner's privacy statement. Both URLs are deployment-time configuration values, not hardcoded, so they can be updated without a code change.

**FR-P16** GT&C acceptance events are logged server-side. Each event records at minimum: server-side timestamp, IP address, GT&C version identifier, and action type (accepted / declined). Log is write-once and tamper-evident, consistent with the Factory Owner's privacy statement §10.1.1. Processing is governed by privacy statement §8.2.1 (Art. 6(1)(f) AVG, 2-year retention). Log data is infrastructure-level and not accessible to the application's recommendation or comparison logic.

---

## 7. User Interface Requirements

### 7.1 Navigation structure

The interface provides five primary areas accessible from persistent top-level navigation: baseline browser, comparison view, selection wizard, attribute dictionary, and an about/terms section. Navigation remains accessible from every view without scrolling. A persistent footer on every page provides links to the GT&C and privacy statement (FR-P15). No application-level authentication gate in v1.

### 7.2 Baseline browser (UC-01a, UC-01b)

Default landing view. GT&C notice and knowledge base version/date must be visible before baseline content. Filter controls persistently visible without scrolling. Visible baseline count updates in real time. Empty filter result presents an explicit recovery action.

### 7.3 Baseline detail (UC-02)

Reachable from the browser and from comparison results. Attributes grouped by category with collapsible sections. Provenance accessible per attribute without navigating away. Missing state and low-confidence state are visually distinct. A notice of third-party sourcing is present. The "Flag this value" action opens a pre-filled GitHub issue (OFD-02 resolution).

### 7.4 Comparison view (UC-03, UC-06a, UC-06b)

Accepts two to four baselines. Baseline selection possible without leaving the view. Differences-only toggle does not reset selected baselines or scroll position. Category collapsing is independent per category. Export actions reachable without scrolling.

### 7.5 Selection wizard (UC-04a, UC-04b, UC-06a, UC-06b)

Sequential question flow (UC-04a) followed by results view (UC-04b). Transition requires no navigation away. The mandatory disclaimer per FR-P08 appears as a visually prominent, integral part of results — not below the fold, not collapsible. Ranked list and exclusion list are visually separated. Path from results to comparison view is a single action. Export actions reachable from results.

### 7.6 Attribute dictionary (UC-05)

Alphabetically ordered. Full rubric for subjective attributes visible without a separate page load. Link to filtered comparison view present on every entry.

### 7.7 Export (UC-06a, UC-06b)

Available from comparison view and wizard results. Two formats presented as distinct, labelled actions. Print stylesheet for UC-06a suppresses interactive elements and navigation chrome but retains the content required by FR-P11. Markdown file for UC-06b named descriptively with export date, carries the content required by FR-P11, does not require renaming for governance use.

### 7.8 Footer (FR-P15)

A persistent footer on every page contains: a configurable link to the Factory Owner's GT&C, a configurable link to the Factory Owner's privacy statement, and the Factory Owner's attribution. This is the primary access point for users seeking legal documentation. The footer is the same mechanism already used on the Factory Owner's website per privacy statement §2.1.

---

## 8. Recommendation Logic

### 8.1 Environment profile questions

| ID | Question | Why it matters |
|---|---|---|
| EQ-01 | Target operating system | Drives the OS hard filter |
| EQ-02 | Organisational context | Governs applicability of mandates and regulatory frameworks |
| EQ-03 | Machine-readable format required | Determines weight of parseability attributes |
| EQ-04 | Baseline must be free | Drives the cost hard filter |
| EQ-05 | Continuous compliance tooling needed | Increases weight of tooling and automation attributes |
| EQ-06 | Review process rigour matters | Increases weight of governance and maintenance attributes |
| EQ-07 | Required level of prescriptiveness | Distinguishes per-setting guidance from principles-level frameworks |

### 8.2 Filtering and ranking

**Hard filters** exclude baselines unconditionally before scoring. Excluded baselines appear in a separate section with reason stated (UC-04b AC3). Triggered by EQ-01 (OS mismatch) and EQ-04 (paid when free required).

**Scoring** applies a weight vector over 45 attributes derived from environment profile answers. Score is the weighted sum of attribute-level compatibility. Weight vector and compatibility mapping are explicit, documented rules — not trained parameters.

**Confidence adjustment** reduces stated confidence proportionally to missing or inferred values on high-weight attributes. More than three missing high-weight attributes triggers a low-confidence flag (UC-04b AC2).

### 8.3 Explainability and disclaimer requirement

Every recommendation includes:

1. A plain-language explanation of ranking, key influencing attributes, and uncertainty signals.
2. The mandatory Disclaimer per §2.1.2 and FR-P08.
3. The knowledge base version and generation date.
4. An explicit statement of what factors were NOT considered — factors outside the seven wizard questions are not reflected in the recommendation.

The recommendation engine is fully deterministic: the same knowledge base version and environment profile always produce the same recommendation.

---

## 9. Multi-Tenancy Requirements

### 9.1 Functional requirement

The BST is designed to serve multiple independent tenants in its commercial incarnation. A tenant is an organisation with its own subscription, environment profile, and visibility settings over the baseline catalogue.

### 9.2 v1 scope

In v1, only one tenant exists: the factory itself. No tenant management, authentication, or isolation is implemented. The provisions in §9.3 are design constraints on v1, not v1 features.

### 9.3 Architectural provisions required from v1

- All data structures that will be tenant-scoped must include a tenant identifier field, defaulting to a canonical single-tenant value.
- All interface contracts must accommodate a tenant identifier, even if implicit in v1.
- No v1 decision may require a breaking change when a second tenant is added.
- The GT&C acceptance mechanism must accommodate per-user identity in v2 without structural change. In v1, acceptance is recorded by IP address + timestamp + GT&C version (legally grounded under privacy statement §8.2.1 without per-user authentication). In v2, per-user account strengthens forensic quality to include verified user identity. The v1 log schema must not prevent adding a user identifier field in v2.

---

## 10. Non-Functional Requirements

### 10.1 Performance

- Interface interactive within 3 seconds on standard broadband.
- All interactions after initial load respond within 200 milliseconds.

### 10.2 Security

- No user-supplied data stored or transmitted as a primary application function.
- Knowledge base contains no secrets, credentials, or PII.
- Standard web security headers enforced including CSP and transport security.
- Curation subsystem complies with all applicable factory security policies.
- IP and agentic access protections per §2.1.3, FR-P12, FR-P13.

### 10.3 Sovereignty

- All infrastructure classified under the factory's sovereignty taxonomy before deployment.
- Components classified as tolerable with exit strategy have a documented exit strategy in the Cost Register before go-live.

### 10.4 Maintainability

- A single person can update the knowledge base, verify correctness, and deploy without assistance.
- Staleness detection requires no manual inspection.
- Disclaimer text maintained in a single location per §2.1.2 and referenced wherever rendered.

### 10.5 Auditability

- Every displayed value is traceable to its source through the provenance record.
- Every recommendation is reproducible: same knowledge base version + same environment profile = same recommendation.
- Knowledge base version and generation date visibility per FR-P14.

### 10.6 Legal and compliance

- GT&C preparation status and accepted risk: see §2.1.1. Go-live gate: see §12. Tracked as [Infra_-_Subscription_Factory#17](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/17).
- Before go-live, the GT&C liability limitation clause must be reviewed for compliance with Dutch commercial law (Boek 6 BW) — specifically: reasonableness of the limitation (Art. 6:248 BW), and whether intentional acts or gross negligence carve-outs are required. EU consumer protection law (Directive 93/13/EEC) does not apply to the B2B-only client base.
- GT&C version must be tracked. Changes to the GT&C that affect user rights trigger a new acceptance event requirement.
- The disclaimer text (§2.1.2) must be reviewed for legal adequacy before go-live. It is not a substitute for the GT&C.

---

## 11. Functional Decision Log

All open functional decisions from the design phase are resolved. This section serves as a traceable record.

| OFD | Decision | Implemented in |
|---|---|---|
| OFD-01 — Tier 3 single-rater risk | Two scoring passes by the same analyst, minimum 48 hours apart. Confidence fixed at Medium regardless of agreement. | §5.3 Trust tier model, FR-C03 |
| OFD-02 — Value challenge mechanism | GitHub issue pre-filled link. In scope for v1. | UC-02 AC6, §7.3 |
| OFD-03 — Export format scope | Both UC-06a (PDF) and UC-06b (markdown) in v1. | UC-06a, UC-06b |
| OFD-04 — Access control gate in v1 | IP-based acceptance log in v1 (no application-level auth required); legally grounded under privacy statement §8.2.1. HTTP Basic Auth on BST URL while GT&C is in preparation. Per-user forensic log in v2. | FR-P16, §9.3, §12 go-live gate |
| OFD-05 — Knowledge base serving mechanism | PHP-gated endpoint (S7-B). Direct static file URL blocked. Requires S1-B (PHP thin layer) — confirmed in [`architecture.md`](architecture.md) §Knowledge base serving. | FR-P09 |

---

## 12. Out of Scope — v1

The following are explicitly excluded from v1 and must not be introduced without a governance-change proposal:

- Phase b — integrating selected baseline into `laptop-initiation-guide.md`
- Phase c — compliance auditing against the selected baseline
- Ubuntu 24.04 audit tooling or Linux agent
- Multi-tenant authentication and provisioning
- Per-user forensic GT&C acceptance log (v1 uses IP-based logging; per-user log is v2)
- Real-time data ingestion or live source synchronisation at request time
- AI-generated attribute values or recommendations
- Per-user saved comparisons, profiles, or history
- Reproduction of baseline control content (BST describes and compares baselines; it does not republish CIS control text, STIG rule content, or other copyrighted material)
- Integration with the homemade Windows hardening tool
- CAPTCHA or advanced bot detection beyond robots.txt and rate limiting
- Legal drafting of the GT&C (separate legal task per §10.6)

**Pre-go-live gate — GT&C:** The BST must not be made publicly accessible until:
1. The Factory Owner's GT&C is published at a stable URL.
2. The footer link (FR-P15) points to the live GT&C document.
3. The GT&C liability limitation clause has been reviewed per §10.6.
4. HTTP Basic Auth on the BST URL is removed.

Until these conditions are met, HTTP Basic Auth remains in place as the access gate.

---

*End of Functional Design — BST v1.0*
*Companion documents: [`architecture.md`](architecture.md), [`operations.md`](operations.md), [`data-dictionary-v1`](functional-design_-_data-dictionary-v1.md)*
