# Data Dictionary — Baseline Selection Tool (BST) v1.0

**Status:** Final — pending Human Maintainer approval
**Parent document:** [`functional-design-v1.md`](functional-design-v1.md) §5.5
**Date:** 2026-04-01

---

## 1. Purpose

This document defines the complete attribute catalogue for the BST knowledge base. Each attribute represents a named dimension of comparison across security hardening baselines. Together, the attributes form the data model that powers browsing, filtering, comparison, and recommendation.

This is the authoritative source for attribute definitions. The knowledge base schema in [`architecture.md`](architecture.md) implements this catalogue as the `attribute_schema` array in `data/baselines.json`.

## 2. Attribute structure

Each attribute is defined by:

| Field | Description |
|---|---|
| `attribute_id` | Stable slug identifier. Once assigned, never changes. |
| Label | Human-readable name displayed in the UI. |
| Data type | `Boolean`, `Enum`, `Enum (multi)`, `Date`, `Integer`, `Free text`, `Free text (list)` |
| Obj/Subj | `Objective` (measurable without judgment) or `Subjective` (requires analyst assessment). Subjective attributes are collected via the Tier 3 process (see functional design §5.3). |
| Stability | How often the value changes for a given baseline: `Static` (never changes), `Per release` (changes with new baseline version), `Continuous` (can change at any time). |
| Obtainability | How hard the value is to collect: `Easy` (publicly visible metadata), `Moderate` (requires reading documentation), `Difficult` (requires research or analyst judgment). |
| Enum values / Rubric | For Enum and Subjective attributes: the complete set of permitted values with definitions. For Tier 3 attributes: the scoring rubric. |

## 3. Evidence base

Attribute selection informed by:

- **NIST** — SP 800-70 (NCP metadata schema), SP 800-128 (Security-Focused Configuration Management)
- **DISA** — STIG documentation, SRG structure, severity categorisation, quarterly release process
- **CIS** — Benchmarks structure, profile levels, CIS Controls mapping, consensus development process
- **ACSC** — Essential Eight Maturity Model, platform-specific hardening guides, ISM control mappings
- **ANSSI** — GNU/Linux, Windows, and Active Directory hardening guides, hardening level methodology
- **BSI** — IT-Grundschutz Compendium (Bausteine), BSI Standards 200-series, protection level methodology
- **ComplianceAsCode** — SCAP Security Guide profile metadata, multi-framework profile implementation
- **Microsoft** — Security Compliance Toolkit, Intune security baselines, Policy Analyzer
- **Academic/practitioner** — SANS GIAC Gold papers comparing baseline families on operational dimensions; peer-reviewed research on cross-baseline setting overlap and conflict detection

### 3.1 Primary source registry

Canonical documentation URLs per in-scope baseline. The Tier 2b pipeline (FR-C10) directs LLMs exclusively to these URLs — any URL not listed here is rejected as a potential hallucination. URLs are verified by the Human Maintainer before each pipeline run; stale URLs are updated here before re-execution.

| Baseline | Primary source URLs | Access |
|---|---|---|
| DISA STIG | DoD Cyber Exchange STIG library; STIG Viewer | Free |
| OpenSCAP / SCAP Security Guide | ComplianceAsCode GitHub repository; OpenSCAP project documentation | Free / OSS |
| NIST National Checklist Program | NIST NCP repository; SP 800-70 | Free |
| Microsoft Security Compliance Toolkit | Microsoft Download Center SCT page; SCT documentation | Free |
| CIS Benchmarks | CIS Benchmarks download portal (PDF); CIS Controls mapping | Free (PDF) |
| ACSC Essential Eight | ACSC Essential Eight guidance; ISM control mappings | Free |
| ANSSI Linux Guide | ANSSI hardening recommendations (GNU/Linux, Windows, AD) | Free |
| Microsoft Intune Baselines | Microsoft Learn Intune security baselines documentation | Free (metadata) |
| PCI DSS | PCI SSC document library (public summaries and guidance) | Metadata only |
| ISO/IEC 27001 | ISO catalogue entry; publicly available scope descriptions | Metadata only |
| HIPAA / HHS Guidance | HHS HIPAA guidance; Security Rule resources | Free |
| NIS2 / Cyber Resilience Act | EUR-Lex NIS2 Directive text; ENISA guidance | Free |
| SOC 2 | AICPA SOC 2 criteria descriptions (public summaries) | Metadata only |

Actual URLs are not embedded in this document — they are maintained in the pipeline's primary source manifest (`src/llm_consensus/sources.json`) where they can be verified and updated operationally without a specification change. This table defines which sources are authoritative; the manifest provides the current URLs.

## 4. Attribute catalogue

### 4.1 Identity & Classification (6 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 1 | `issuer_name` | Issuing organisation | Free text | Objective | Static | Easy | — |
| 2 | `issuer_type` | Issuer authority type | Enum | Objective | Static | Easy | `standards_body` — consensus-driven standards organisation (e.g., CIS); `government_military` — government or military agency (e.g., DISA, ANSSI, BSI, ACSC); `vendor` — product vendor (e.g., Microsoft); `open_source_community` — open-source project (e.g., ComplianceAsCode); `academic` — academic or research institution |
| 3 | `baseline_type` | Baseline type | Enum | Objective | Static | Easy | `technical_benchmark` — per-setting hardening checklist; `strategic_framework` — principle-level mitigation strategies (e.g., Essential Eight); `isms_module` — building block within an ISMS methodology (e.g., IT-Grundschutz Baustein); `checklist_repository` — index/aggregator of checklists from multiple sources (e.g., NIST NCP) |
| 4 | `baseline_version` | Current version identifier | Free text | Objective | Per release | Easy | — |
| 5 | `initial_release_date` | Date of first publication | Date | Objective | Static | Moderate | — |
| 6 | `country_of_origin` | Country or jurisdiction of issuing body | Free text | Objective | Static | Easy | — |

### 4.2 Platform & Coverage (7 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 7 | `target_platforms` | Target platforms | Free text (list) | Objective | Per release | Easy | Enumerated list of covered OS/application/service targets (e.g., "Windows 11, Windows Server 2022, Edge") |
| 8 | `platform_type` | Platform category | Enum (multi) | Objective | Per release | Easy | `operating_system`; `application`; `cloud_service`; `network_device`; `container_orchestration`; `database`; `management_layer`; `mobile` |
| 9 | `role_targeting` | Environment role targeting | Enum (multi) | Objective | Per release | Easy | `workstation`; `server`; `domain_controller`; `network_appliance`; `cloud_tenant`; `not_role_specific` |
| 10 | `scope_depth` | Scope depth | Enum | Subjective | Per release | Moderate | `full_surface` — covers the complete hardening surface of its target (e.g., CIS OS benchmark); `component_specific` — covers one component on the target (e.g., a DISA browser STIG); `strategic_subset` — covers a prioritised subset of mitigations, not all settings (e.g., ACSC Essential Eight); `architectural` — covers design principles and high-level controls, not individual settings (e.g., BSI IT-Grundschutz Baustein) |
| 11 | `composability` | Composability requirement | Enum | Objective | Static | Moderate | `standalone` — self-contained for its target scope; `composition_required` — must be combined with other baselines for full coverage (e.g., DISA: OS STIG + browser STIG + office STIG); `modular_framework` — formally modelled composition system (e.g., BSI Modellierung) |
| 12 | `prescriptiveness` | Level of prescriptiveness | Enum | Subjective | Per release | Moderate | `per_setting` — specifies exact setting paths and values (e.g., registry keys, sysctl parameters); `per_control` — specifies controls but not exact settings; `principle_level` — specifies goals and strategies without implementation detail. **Rubric:** Per-setting = every recommendation includes a verifiable machine-state assertion. Per-control = recommendations describe what to achieve but not the specific setting. Principle-level = recommendations are outcome statements without technical specificity. |
| 13 | `version_granularity` | Version targeting granularity | Enum | Objective | Static | Easy | `per_build` — separate baseline per OS build/feature update (e.g., Microsoft SCT per Windows semi-annual release); `per_major_version` — one baseline per OS major version (e.g., CIS per Windows 11); `per_os_family` — one baseline per OS family (e.g., ANSSI GNU/Linux guide); `version_agnostic` — not tied to a specific version (e.g., ACSC Essential Eight) |

### 4.3 Content Quality (8 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 14 | `setting_count` | Number of settings or recommendations | Integer | Objective | Per release | Moderate | Null if not applicable (strategic frameworks) |
| 15 | `rationale_per_setting` | Per-setting rationale documented | Enum | Objective | Per release | Easy | `yes_all` — every recommendation includes a documented rationale; `yes_partial` — some recommendations include rationale; `no` — no per-setting rationale published |
| 16 | `default_value_documented` | Default (out-of-box) value documented | Enum | Objective | Per release | Easy | `yes_all`; `yes_partial`; `no` |
| 17 | `audit_procedure_specificity` | Audit/check procedure specificity | Enum | Objective | Per release | Moderate | `machine_verifiable` — provides exact check commands, registry paths, or OVAL definitions; `step_by_step` — provides manual verification steps; `descriptive` — describes what to verify without exact steps; `none` — no audit procedure |
| 18 | `fix_procedure_specificity` | Remediation/fix specificity | Enum | Objective | Per release | Moderate | `machine_executable` — provides scripts, GPO exports, or Ansible tasks; `step_by_step` — provides manual remediation steps; `descriptive` — describes what to change without exact steps; `none` — no remediation guidance |
| 19 | `impact_assessment` | Operational impact assessment | Enum | Objective | Per release | Moderate | `per_setting` — each recommendation documents operational impact; `aggregate_only` — impact discussed at tier/profile level only; `none` — no impact assessment |
| 20 | `severity_classification` | Per-finding severity/priority classification | Enum | Objective | Per release | Easy | `yes_granular` — each finding has a severity rating (e.g., DISA CAT I/II/III, CIS Scored/Not Scored); `yes_tiered` — severity by profile level only (e.g., L1 vs. L2); `no` — no severity classification |
| 21 | `conflict_documentation` | Known conflicts with other baselines documented | Boolean | Objective | Per release | Difficult | — |

### 4.4 Governance & Maintenance (8 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 22 | `update_cadence` | Typical update frequency | Enum | Objective | Continuous | Moderate | `continuous` — updates published as changes arise, no fixed schedule (e.g., ComplianceAsCode); `quarterly` — regular quarterly releases (e.g., DISA STIGs); `per_os_release` — new baseline per OS release, updates between releases (e.g., Microsoft SCT); `annual` — annual compendium or revision cycle (e.g., BSI IT-Grundschutz); `irregular` — no predictable cadence (e.g., ANSSI, ACSC) |
| 23 | `last_update_date` | Date of most recent published update | Date | Objective | Continuous | Easy | — |
| 24 | `new_os_coverage_lag` | Typical lag between OS GA and baseline availability | Enum | Subjective | Continuous | Moderate | `days_to_weeks` — baseline available within ~30 days of OS GA (e.g., Microsoft SCT); `one_to_six_months` — (e.g., ComplianceAsCode); `six_to_twelve_months` — (e.g., CIS); `twelve_plus_months` — (e.g., DISA, BSI, ANSSI). **Rubric:** Based on observed publication dates for the three most recent OS releases covered by the baseline family. |
| 25 | `changelog_transparency` | Changelog detail level | Enum | Objective | Per release | Easy | `per_setting_diff` — exact setting-level changelog between versions (e.g., Microsoft SCT Policy Analyzer delta); `summary_changelog` — descriptive list of changes per release; `version_number_only` — new version published without detailed changelog; `none` — no changelog |
| 26 | `review_process` | Development and review process | Enum | Subjective | Static | Moderate | `formal_consensus` — multi-stakeholder consensus process with public comment period (e.g., CIS community benchmark process); `government_authority` — internal government review and approval chain (e.g., DISA, ANSSI, BSI, ACSC); `vendor_internal` — vendor-internal review process (e.g., Microsoft); `open_source_pr` — open-source pull request review with maintainer approval (e.g., ComplianceAsCode); `unknown` — process not publicly documented. **Rubric:** Classify based on the publisher's own documentation of their authoring process. If no process documentation is publicly available, classify as unknown. |
| 27 | `reviewer_diversity` | Reviewer/author diversity | Enum | Subjective | Static | Difficult | `multi_stakeholder` — reviewers from multiple independent organisations (e.g., CIS volunteer community); `single_org_multi_team` — multiple teams within one organisation (e.g., DISA field offices); `single_team` — authored and reviewed by same team; `unknown` — reviewer composition not publicly documented. **Rubric:** Based on published contributor lists, acknowledgement sections, or process documentation. |
| 28 | `errata_process` | Formal errata/correction process | Enum | Objective | Static | Moderate | `formal_published` — dedicated errata notices or revision notes documenting corrections; `inline_revision` — corrections folded into next regular release without separate errata; `unknown` — process not publicly documented |
| 29 | `retirement_process` | End-of-life / retirement process | Enum | Objective | Static | Moderate | `explicit_eol` — published sunset dates or end-of-support declarations (e.g., DISA STIG Sunset list); `implicit_abandonment` — no update for 2+ years without formal retirement; `not_applicable` — framework is version-agnostic; `unknown` — no retirement information published |

### 4.5 Access & Licensing (3 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 30 | `access_cost` | Cost to access full content | Enum | Objective | Continuous | Easy | `free_open` — freely available without registration; `free_registration` — free but requires account registration (e.g., CIS Benchmarks PDF); `free_subscription` — free tier of a paid product provides access (e.g., Intune built-in baselines require licence); `paid` — full content behind paywall (e.g., CIS-CAT Pro, ISO 27001 standard) |
| 31 | `licence_type` | Usage/redistribution licence | Enum | Objective | Static | Moderate | `open_source` — OSI-approved licence (e.g., ComplianceAsCode under BSD/MIT); `government_public` — government publication, public domain or crown copyright (e.g., DISA STIGs, ACSC, ANSSI); `proprietary_free` — proprietary but free to use, redistribution restricted (e.g., CIS Benchmarks, Microsoft SCT); `proprietary_paid` — proprietary and paid |
| 32 | `language_availability` | Languages in which the baseline is published | Free text (list) | Objective | Static | Easy | — |

### 4.6 Format & Parseability (4 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 33 | `primary_format` | Primary publication format | Enum (multi) | Objective | Per release | Easy | `scap_xccdf` — SCAP/XCCDF datastream; `gpo_export` — Group Policy Object backup; `intune_template` — Intune security baseline template; `structured_data` — JSON, XML, YAML, or equivalent machine-readable format; `pdf_prose` — PDF or web document with prose guidance; `ansible_role` — Ansible playbook/role; `script` — shell script, PowerShell script, or equivalent |
| 34 | `scap_compliance_level` | SCAP specification compliance | Enum | Objective | Per release | Moderate | `scap_validated` — NIST SCAP Validated product (NCP Tier I); `scap_conformant` — publishes SCAP content but not NIST-validated; `none` — no SCAP content published |
| 35 | `remediation_formats` | Available remediation/enforcement formats | Enum (multi) | Objective | Per release | Moderate | `gpo`; `intune`; `ansible`; `puppet`; `chef`; `bash_script`; `powershell_script`; `scap_remediation`; `none` |
| 36 | `variable_parameterisation` | Site-specific value customisation | Boolean | Objective | Per release | Moderate | True if the baseline supports variable/parameter substitution for site-specific values (e.g., password length, lockout threshold). False if all values are fixed. |

### 4.7 Tooling & Automation (5 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 37 | `assessment_tooling` | Native assessment/scanning tool | Enum | Objective | Continuous | Easy | `dedicated_tool` — publisher provides a dedicated scanning tool (e.g., CIS-CAT, DISA SCC, OpenSCAP); `integrated_platform` — assessment built into a management platform (e.g., Intune compliance, Red Hat Insights); `third_party_only` — no publisher tool, but third-party tools support this baseline; `none` — no known automated assessment tooling |
| 38 | `diff_tooling` | Baseline version comparison tooling | Boolean | Objective | Continuous | Moderate | True if publisher provides tooling to diff between baseline versions (e.g., Microsoft Policy Analyzer, ComplianceAsCode profile diff). |
| 39 | `continuous_compliance` | Continuous compliance monitoring support | Boolean | Objective | Continuous | Moderate | True if the baseline is designed for ongoing monitoring (drift detection), not one-time application. |
| 40 | `management_tool_alignment` | Management tool alignment | Enum (multi) | Objective | Per release | Easy | `gpo_native` — directly importable as GPO; `intune_native` — built-in Intune template; `ansible_native` — publisher-provided Ansible content; `openscap_native` — publisher-provided SCAP content for OpenSCAP; `tool_agnostic` — published as prose/settings without tool-specific packaging; `other` |
| 41 | `profile_inheritance` | Profile inheritance or extension support | Boolean | Objective | Per release | Moderate | True if profiles can formally extend or inherit from other profiles (e.g., ComplianceAsCode STIG profile extends CIS profile). |

### 4.8 Applicability & Adoption (4 attributes)

| # | attribute_id | Label | Data type | Obj/Subj | Stability | Obtainability | Enum values / Rubric |
|---|---|---|---|---|---|---|---|
| 42 | `compliance_framework_mapping` | Compliance framework mappings | Enum (multi) | Objective | Per release | Easy | `nist_800_53`; `cis_controls`; `pci_dss`; `hipaa`; `iso_27001`; `fedramp`; `nis2`; `ism_au`; `rgs_fr`; `it_grundschutz`; `none_explicit` |
| 43 | `regulatory_recognition` | Recognised by regulatory or compliance regimes | Enum (multi) | Objective | Static | Moderate | `dod_rmf` — accepted for DoD Risk Management Framework; `fedramp` — accepted for FedRAMP; `pci_dss` — recognised as acceptable hardening standard; `australian_gov` — referenced by PSPF/ISM; `french_gov` — referenced by RGS; `german_gov` — referenced by BSI/KRITIS; `eu_nis2` — referenced in NIS2 compliance guidance; `none_known` |
| 44 | `adoption_breadth` | Estimated adoption breadth | Enum | Subjective | Continuous | Difficult | `widespread` — de facto standard in its domain, adopted across industries and geographies; `sector_standard` — standard within a specific sector or jurisdiction (e.g., DISA STIG in US DoD, IT-Grundschutz in German KRITIS); `niche` — limited adoption, typically regional or community-specific; `emerging` — recently published, adoption trajectory unclear. **Rubric:** Based on: (1) number of third-party tools that natively support the baseline, (2) frequency of citation in compliance documentation, (3) geographical breadth of adoption. Two independent scoring passes, 48h apart. |
| 45 | `cross_baseline_mapping` | Published mapping to other baselines | Free text (list) | Objective | Per release | Moderate | List of baselines to which the publisher provides an explicit mapping or crosswalk (e.g., CIS publishes a STIG profile; Microsoft documents SCT-to-STIG alignment; ComplianceAsCode implements CIS, STIG, and ANSSI profiles in a single toolchain) |

## 5. Attribute count summary

The catalogue defines 45 attributes across 8 categories. Category counts match [`functional-design-v1.md`](functional-design-v1.md) §5.2.

## 6. Collection tier assignment

Each attribute's initial collection tier is determined by its Obj/Subj and Obtainability classifications:

- **Objective + Easy/Moderate** attributes are candidates for Tier 2b (LLM-consensus-extracted) collection. See functional design §5.3 for tier definitions.
- Objective + Easy attributes collected via Tier 2b may be promoted to Tier 2 (Document-verifiable) after human verification (Horizon 1, Layer 1 per FR-C12).
- **Subjective** attributes collected via Tier 2b remain at confidence ceiling Medium regardless of consensus strength, consistent with the Tier 3 policy in functional design §5.3.
- Attributes requiring paywalled content are recorded as missing with reason `paywalled` regardless of collection method.

## 7. Consistency obligations

When this catalogue changes:

1. The `attribute_schema` array in [`architecture.md`](architecture.md) §Knowledge base schema MUST be updated to match.
2. The `data/baselines.schema.json` validation schema MUST be updated to match.
3. The category counts in [`functional-design-v1.md`](functional-design-v1.md) §5.2 MUST be updated to match.
4. The attribute count references throughout the functional design MUST be updated to reflect the actual count.
5. The environment profile weight vector in [`functional-design-v1.md`](functional-design-v1.md) §8.2 MUST cover all attributes.
