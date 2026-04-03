# Project Traceability Matrix — Baseline Selection Tool (BST)

| Field | Value |
|---|---|
| **Document ID** | TM-BST-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Owner** | Human Maintainer (Factory Owner) — default per fd-td-design-principles.md §Project traceability matrix |
| **Creation date** | 2026-04-03 |
| **FD baseline** | FD-BST-001 v1.1.0 |
| **TD baseline** | TD-BST-001 v1.0.2 |
| **OPS baseline** | OPS-BST-001 v1.0.0 |

---

## Version History

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-04-03 | 1.0.0 | Initial matrix covering all FD requirements, TD design elements, and test cases for BST v1. Created to fulfil fd-td-design-principles.md §Project traceability matrix as identified during Review TD. | Author TD (agent) |

---

## Scope

This matrix links business objectives (FD-BST-001 §9) through FD requirements to TD design elements and test cases. It covers the full BST v1 scope as a single unit of delivery (FD A-06, TD TA-06).

**Column definitions:**

| Column | Content |
|---|---|
| Business objective | Problem statement reference or business constraint driving the requirement |
| FD requirement | Stable identifier from FD-BST-001 |
| TD design element | Section or stable identifier from TD-BST-001 / OPS-BST-001 |
| Test case | Reference to TD-BST-001 §18 test scope or deployment verification checklist |

---

## 1. Curation Subsystem

| Business objective | FD requirement | TD design element | Test case |
|---|---|---|---|
| Systematic data collection (§9) | FR-C01 | §13.2 (`base_parser.py`, `disa_stig.py`, `nist_ncp.py`, `openscap_ssg.py`, `microsoft_sct.py`); INT-04 | §18.2 unit: Tier 1 parsers |
| Systematic data collection (§9) | FR-C02 | §13.2 (`retrieval_cli.py`) | §18.2 unit: retrieval CLI (implicit) |
| Systematic data collection (§9) | FR-C03 | §13.2 (`scoring_cli.py`); 48h gap enforcement | §18.2 unit: scoring CLI (implicit) |
| Maintainability (QR-04) | FR-C04 | §13.2 (`staleness.py`); §11.2 (stale attributes schema) | §18.2 unit: `staleness.py`; §18.4 CI: staleness advisory |
| Data integrity (QR-05) | FR-C05 | §13.2 (`validator.py`); §11.1 (KB schema); FM-C07 | §18.2 unit: `validator.py`; §18.4 CI: schema validation |
| Auditability (QR-05) | FR-C06 | §11.1 (provenance record in KB schema) | §18.2 unit: provenance record coverage; §18.3 integration: KB schema round-trip |
| Single-operator (BC-08) | FR-C07 | TC-03; S4-A; NFR-04 | §18.5 deployment verification: HM completes cycle |
| AI-assisted curation (§9) | FR-C08 | §13.6 (Tier 2b pipeline design); INT-01; INT-02; FM-C01–FM-C05 | §18.2 unit: `consensus.py`; §18.3 integration: Tier 2b end-to-end |
| AI-assisted curation (§9) | FR-C09 | §13.6 model qualification; provenance `models` block | §18.2 unit: model qualification (implicit in consensus tests) |
| Data integrity (QR-05) | FR-C10 | §13.6 primary source manifest (`sources.json`); FM-C03 | §18.2 unit: URL validation against allowlist |
| Sovereignty (BC-08, QR-06) | FR-C11 | §13.6 adapters (`ollama.py`); §10.3 sovereignty classification; INT-01 | §18.3 integration: pipeline with mocked local adapters |
| Data quality (horizon) | FR-C12 | Deferred (horizon 1) | N/A — not in v1 scope |

## 2. Knowledge Store

| Business objective | FD requirement | TD design element | Test case |
|---|---|---|---|
| Auditability (QR-05) | FR-K01 | S2-A (single versioned JSON file); TC-08; Git version history | §18.4 CI: schema validation on every PR |
| Deployability (QR-04) | FR-K02 | TC-02; S2-A; deployment pipeline (OPS §Deployment pipeline) | §18.5 deployment verification |
| Data integrity (§9) | FR-K03 | §11.1 (missing value representation: `missing`, `missing_reason`) | §18.2 unit: `validator.py` (missing value handling) |
| Maintainability (QR-04) | FR-K04 | §11.1 (`ttl_days` field); §13.2 (`staleness.py`) | §18.2 unit: `staleness.py` |

## 3. Presentation Subsystem

| Business objective | FD requirement | TD design element | Test case |
|---|---|---|---|
| Systematic selection (§9) | FR-P01 | S1-B; S3-B; §13.4 (`index.html`, `app.js`); NFR-01 | §18.5 deployment verification: application loads |
| Privacy (BC-05, QR-07) | FR-P02 | NFR-07; §13.4 (no server-side session state) | §18.5 deployment verification; §18.6 security: no user data persisted |
| Transparency (§9) | FR-P03 | §13.4 (`app.js`); §11.1 (confidence, trust_tier fields) | §18.5 deployment verification: usability walkthrough |
| Transparency (§9) | FR-P04 | §13.4 (`app.js`); §11.1 (missing, missing_reason fields) | §18.5 deployment verification: usability walkthrough |
| Governance documentation (§9) | FR-P05 | §13.4 (`app.js` export logic, `app.css` print stylesheet); FM-P07, FM-P08 | §18.5 deployment verification: export completeness |
| Sovereignty (QR-06, BC-08) | FR-P06 | TC-07; S1-B; NFR-02 (no server round-trip) | §18.5 deployment verification; §18.6 security: CSP enforcement |
| Deployability (BC-07) | FR-P07 | TC-01; S1-B; TA-01 | §18.5 deployment verification: application loads |
| Liability limitation (BC-11) | FR-P08 | §13.5 (disclaimer handling); §11.1 (disclaimer block) | §18.5 deployment verification: disclaimer visible on wizard results |
| IP protection (BC-10) | FR-P09 | S7-B; TC-09; §13.4 (`api/baselines.php`); §12.1 | §18.6 security: direct KB access blocked |
| Legal compliance (BC-11) | FR-P10 | §13.4 (`index.php` GT&C gating); FM-P05 | §18.5 deployment verification: GT&C notice visible |
| Liability limitation (BC-11) | FR-P11 | §13.5; §13.4 (`app.js` export logic) | §18.5 deployment verification: export completeness (attribution, disclaimer, KB version) |
| IP protection (BC-10) | FR-P12 | TC-10; §13.4 rate limiting (60 req/min/IP, APCu/file fallback); FM-P03, FM-P04 | §18.6 security: rate limiting |
| IP protection (BC-10) | FR-P13 | TC-11; §13.4 (`robots.txt`); specific bot user-agents listed | §18.5 deployment verification: robots.txt accessible; §18.6 security: bot rejection |
| Auditability (QR-05) | FR-P14 | §13.4 (`app.js`); §11.1 (`meta.generated_at`) | §18.5 deployment verification: KB version/date visible |
| Legal compliance (BC-11) | FR-P15 | §13.4 (`config/settings.php`); configurable GT&C and privacy URLs | §18.5 deployment verification: footer links correct |
| Legal compliance (BC-05) | FR-P16 | §11.3 (acceptance log schema); §13.4 (`index.php` logging); FM-P05 | §18.5 deployment verification: acceptance logging functional |

## 4. Recommendation Logic

| Business objective | FD requirement | TD design element | Test case |
|---|---|---|---|
| Systematic selection (§9) | EQ-01–EQ-07 | §13.7 (environment profile questions in `app.js`) | §18.5 deployment verification: wizard walkthrough |
| Systematic selection (§9) | §14.5.2 hard filters | §13.7 (hard filters: EQ-01 OS mismatch, EQ-04 cost) | §18.5 deployment verification: wizard results show exclusions |
| Systematic selection (§9) | §14.5.5 weight vector | §13.7 (weight vector as static config in `app.js`); DD-02 | §18.5 deployment verification: wizard produces ranked results |
| Systematic selection (§9) | §14.5.6 EQ modifiers | §13.7 (EQ-driven weight modifiers) | §18.5 deployment verification: different profiles produce different rankings |
| Systematic selection (§9) | §14.5.7 scoring rules | §13.7 (compatibility scoring, weighted sum) | §18.5 deployment verification: determinism check (same input = same output) |
| Transparency (§9) | §14.5.8 high-weight def | §13.7 (confidence adjustment); NFR-05 | §18.5 deployment verification: low-confidence flag visible |

## 5. User Stories → TD Design Elements

| FD user story | TD design element(s) | Test case |
|---|---|---|
| UC-01a — View baseline catalogue | §13.4 (`app.js`); §12.1 (API endpoint); §11.1 (KB schema) | §18.5 deployment verification: browser view |
| UC-01b — Filter baseline catalogue | §13.4 (`app.js` filter logic); NFR-02 | §18.5 deployment verification: usability walkthrough |
| UC-02 — View baseline detail | §13.4 (`app.js`); §11.1 (provenance record) | §18.5 deployment verification: usability walkthrough |
| UC-03 — Compare baselines | §13.4 (`app.js` comparison); S3-B; NFR-02 | §18.5 deployment verification: usability walkthrough |
| UC-04a — Answer wizard questions | §13.7 (recommendation engine); §13.4 (`app.js`) | §18.5 deployment verification: wizard walkthrough |
| UC-04b — View wizard recommendation | §13.7; §13.5 (disclaimer); NFR-05 | §18.5 deployment verification: wizard results + disclaimer |
| UC-05 — Look up attribute definition | §13.4 (`app.js`); §11.1 (`attribute_schema` array) | §18.5 deployment verification: usability walkthrough |
| UC-06a — Export as PDF | §13.4 (`app.css` print stylesheet, `app.js`); FM-P07 | §18.5 deployment verification: export completeness |
| UC-06b — Export as markdown | §13.4 (`app.js` file generation); FM-P08 | §18.5 deployment verification: export completeness |

## 6. Quality Requirements → NFRs

| FD quality requirement | TD NFR | Verification |
|---|---|---|
| QR-01 — 3s page load | NFR-01 (TTI ≤ 3s, 440 KB budget) | §18.5: DevTools Performance tab on throttled connection |
| QR-02 — 200ms interaction | NFR-02 (no server round-trip) | §18.5: DevTools Performance tab |
| QR-03 — Usable without training | NFR-03 (1-click navigation, recovery actions) | §18.5: usability walkthrough of all 9 user stories |
| QR-04 — Single-operator maintenance | NFR-04 (single CLI command, one merge) | §18.5: HM completes curation → deployment cycle |
| QR-05 — Full traceability | NFR-05 (provenance chain, determinism) | §18.5: provenance reconstruction; determinism test |
| QR-06 — Sovereignty | NFR-06 (classification table §10.3) | §18.5: no "Pending" entries at go-live |
| QR-07 — Security data handling | NFR-07 (headers, no user data, privacy compliance) | §18.5 + §18.6: header inspection, no user data persisted |

## 7. Reporting and Analytics

| FD requirement | TD design element | Test case |
|---|---|---|
| RA-01 — Comparison export (PDF) | §13.4 (`app.css` print, `app.js`); §13.5 (disclaimer injection) | §18.5 deployment verification: export completeness |
| RA-02 — Comparison export (markdown) | §13.4 (`app.js` file generation) | §18.5 deployment verification: export completeness |
| RA-03 — Recommendation export (PDF) | §13.4 (`app.css`, `app.js`); §13.5; §13.7 | §18.5 deployment verification: export completeness |
| RA-04 — Recommendation export (markdown) | §13.4 (`app.js`); §13.5; §13.7 | §18.5 deployment verification: export completeness |
| RA-05 — KB version display | §13.4 (`app.js`); §11.1 (`meta.generated_at`, `meta.generated_by`) | §18.5 deployment verification: KB version/date visible |
| RA-06 — Staleness alerts | §13.2 (`staleness.py`); §11.2 | §18.4 CI: staleness advisory |
| RA-07 — Curation provenance report | §13.6 pipeline output; §11.1 (`llm_provenance` block) | §18.3 integration: Tier 2b end-to-end |
| RA-08 — GT&C acceptance log | §11.3 (acceptance log schema); §13.4 (`index.php`) | §18.5 deployment verification: acceptance logging |

---

## Coverage Summary

| FD artifact type | Total | Traced to TD | Traced to test |
|---|---|---|---|
| Functional requirements (FR-C) | 12 | 11 + 1 deferred | 11 + 1 N/A |
| Functional requirements (FR-K) | 4 | 4 | 4 |
| Functional requirements (FR-P) | 16 | 16 | 16 |
| User stories (UC-) | 9 | 9 | 9 |
| Quality requirements (QR-) | 7 | 7 (as NFR-01–07) | 7 |
| Reporting requirements (RA-) | 8 | 8 | 8 |
| Environment questions (EQ-) | 7 | 7 (in §13.7) | 7 |
| **Total** | **63** | **62 + 1 deferred** | **62 + 1 N/A** |

FR-C12 is explicitly deferred to horizon 1 and not traced to a v1 design element or test case.

---

*Paired documents: [`functional-design.md`](functional-design.md) (FD-BST-001 v1.1.0), [`architecture.md`](architecture.md) (TD-BST-001 v1.0.2), [`operations.md`](operations.md) (OPS-BST-001 v1.0.0)*
