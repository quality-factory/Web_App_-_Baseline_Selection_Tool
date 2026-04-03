"""Generate JSON Schema for the BST knowledge base from the data dictionary.

This module produces ``src/schemas/baselines.schema.json`` which is used by
the validator, CI, and the structured-output compliance check in the LLM
consensus pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_data_dictionary() -> list[dict[str, Any]]:
    """Return the complete attribute catalogue as structured data.

    The catalogue is defined inline (derived from
    ``docs/functional-design_-_data-dictionary-v1.md``) rather than parsed at
    runtime — the data dictionary is a specification document, not a data file.
    """
    return [
        # ── 4.1 Identity & Classification ────────────────────────────────
        {
            "attribute_id": "issuer_name",
            "label": "Issuing organisation",
            "category": "Identity & Classification",
            "data_type": "Free text",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Easy",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "issuer_type",
            "label": "Issuer authority type",
            "category": "Identity & Classification",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "standards_body", "definition": "Consensus-driven standards organisation"},
                {"value": "government_military", "definition": "Government or military agency"},
                {"value": "vendor", "definition": "Product vendor"},
                {"value": "open_source_community", "definition": "Open-source project"},
                {"value": "academic", "definition": "Academic or research institution"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "baseline_type",
            "label": "Baseline type",
            "category": "Identity & Classification",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "technical_benchmark", "definition": "Per-setting hardening checklist"},
                {"value": "strategic_framework", "definition": "Principle-level mitigation strategies"},
                {"value": "isms_module", "definition": "Building block within an ISMS methodology"},
                {"value": "checklist_repository", "definition": "Index/aggregator of checklists from multiple sources"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "baseline_version",
            "label": "Current version identifier",
            "category": "Identity & Classification",
            "data_type": "Free text",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "initial_release_date",
            "label": "Date of first publication",
            "category": "Identity & Classification",
            "data_type": "Date",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "country_of_origin",
            "label": "Country or jurisdiction of issuing body",
            "category": "Identity & Classification",
            "data_type": "Free text",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Easy",
            "enum_values": None,
            "rubric": None,
        },
        # ── 4.2 Platform & Coverage ──────────────────────────────────────
        {
            "attribute_id": "target_platforms",
            "label": "Target platforms",
            "category": "Platform & Coverage",
            "data_type": "Free text (list)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "platform_type",
            "label": "Platform category",
            "category": "Platform & Coverage",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "operating_system", "definition": "Operating system"},
                {"value": "application", "definition": "Application"},
                {"value": "cloud_service", "definition": "Cloud service"},
                {"value": "network_device", "definition": "Network device"},
                {"value": "container_orchestration", "definition": "Container orchestration"},
                {"value": "database", "definition": "Database"},
                {"value": "management_layer", "definition": "Management layer"},
                {"value": "mobile", "definition": "Mobile"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "role_targeting",
            "label": "Environment role targeting",
            "category": "Platform & Coverage",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "workstation", "definition": "Workstation"},
                {"value": "server", "definition": "Server"},
                {"value": "domain_controller", "definition": "Domain controller"},
                {"value": "network_appliance", "definition": "Network appliance"},
                {"value": "cloud_tenant", "definition": "Cloud tenant"},
                {"value": "not_role_specific", "definition": "Not role-specific"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "scope_depth",
            "label": "Scope depth",
            "category": "Platform & Coverage",
            "data_type": "Enum",
            "objective_subjective": "Subjective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "full_surface", "definition": "Covers the complete hardening surface of its target"},
                {"value": "component_specific", "definition": "Covers one component on the target"},
                {"value": "strategic_subset", "definition": "Covers a prioritised subset of mitigations"},
                {"value": "architectural", "definition": "Covers design principles and high-level controls"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "composability",
            "label": "Composability requirement",
            "category": "Platform & Coverage",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "standalone", "definition": "Self-contained for its target scope"},
                {"value": "composition_required", "definition": "Must be combined with other baselines"},
                {"value": "modular_framework", "definition": "Formally modelled composition system"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "prescriptiveness",
            "label": "Level of prescriptiveness",
            "category": "Platform & Coverage",
            "data_type": "Enum",
            "objective_subjective": "Subjective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "per_setting", "definition": "Specifies exact setting paths and values"},
                {"value": "per_control", "definition": "Specifies controls but not exact settings"},
                {"value": "principle_level", "definition": "Specifies goals without implementation detail"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "version_granularity",
            "label": "Version targeting granularity",
            "category": "Platform & Coverage",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "per_build", "definition": "Separate baseline per OS build"},
                {"value": "per_major_version", "definition": "One baseline per OS major version"},
                {"value": "per_os_family", "definition": "One baseline per OS family"},
                {"value": "version_agnostic", "definition": "Not tied to a specific version"},
            ],
            "rubric": None,
        },
        # ── 4.3 Content Quality ──────────────────────────────────────────
        {
            "attribute_id": "setting_count",
            "label": "Number of settings or recommendations",
            "category": "Content Quality",
            "data_type": "Integer",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "rationale_per_setting",
            "label": "Per-setting rationale documented",
            "category": "Content Quality",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "yes_all", "definition": "Every recommendation includes a documented rationale"},
                {"value": "yes_partial", "definition": "Some recommendations include rationale"},
                {"value": "no", "definition": "No per-setting rationale published"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "default_value_documented",
            "label": "Default (out-of-box) value documented",
            "category": "Content Quality",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "yes_all", "definition": "All defaults documented"},
                {"value": "yes_partial", "definition": "Some defaults documented"},
                {"value": "no", "definition": "No defaults documented"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "audit_procedure_specificity",
            "label": "Audit/check procedure specificity",
            "category": "Content Quality",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "machine_verifiable", "definition": "Provides exact check commands or OVAL definitions"},
                {"value": "step_by_step", "definition": "Provides manual verification steps"},
                {"value": "descriptive", "definition": "Describes what to verify without exact steps"},
                {"value": "none", "definition": "No audit procedure"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "fix_procedure_specificity",
            "label": "Remediation/fix specificity",
            "category": "Content Quality",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "machine_executable", "definition": "Provides scripts, GPO exports, or Ansible tasks"},
                {"value": "step_by_step", "definition": "Provides manual remediation steps"},
                {"value": "descriptive", "definition": "Describes what to change without exact steps"},
                {"value": "none", "definition": "No remediation guidance"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "impact_assessment",
            "label": "Operational impact assessment",
            "category": "Content Quality",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "per_setting", "definition": "Each recommendation documents operational impact"},
                {"value": "aggregate_only", "definition": "Impact discussed at tier/profile level only"},
                {"value": "none", "definition": "No impact assessment"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "severity_classification",
            "label": "Per-finding severity/priority classification",
            "category": "Content Quality",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "yes_granular", "definition": "Each finding has a severity rating"},
                {"value": "yes_tiered", "definition": "Severity by profile level only"},
                {"value": "no", "definition": "No severity classification"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "conflict_documentation",
            "label": "Known conflicts with other baselines documented",
            "category": "Content Quality",
            "data_type": "Boolean",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Difficult",
            "enum_values": None,
            "rubric": None,
        },
        # ── 4.4 Governance & Maintenance ─────────────────────────────────
        {
            "attribute_id": "update_cadence",
            "label": "Typical update frequency",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Continuous",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "continuous", "definition": "Updates published as changes arise"},
                {"value": "quarterly", "definition": "Regular quarterly releases"},
                {"value": "per_os_release", "definition": "New baseline per OS release"},
                {"value": "annual", "definition": "Annual compendium or revision cycle"},
                {"value": "irregular", "definition": "No predictable cadence"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "last_update_date",
            "label": "Date of most recent published update",
            "category": "Governance & Maintenance",
            "data_type": "Date",
            "objective_subjective": "Objective",
            "stability": "Continuous",
            "obtainability": "Easy",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "new_os_coverage_lag",
            "label": "Typical lag between OS GA and baseline availability",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Subjective",
            "stability": "Continuous",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "days_to_weeks", "definition": "Available within ~30 days of OS GA"},
                {"value": "one_to_six_months", "definition": "1-6 months after OS GA"},
                {"value": "six_to_twelve_months", "definition": "6-12 months after OS GA"},
                {"value": "twelve_plus_months", "definition": "12+ months after OS GA"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "changelog_transparency",
            "label": "Changelog detail level",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "per_setting_diff", "definition": "Exact setting-level changelog between versions"},
                {"value": "summary_changelog", "definition": "Descriptive list of changes per release"},
                {"value": "version_number_only", "definition": "New version without detailed changelog"},
                {"value": "none", "definition": "No changelog"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "review_process",
            "label": "Development and review process",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Subjective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "formal_consensus", "definition": "Multi-stakeholder consensus process"},
                {"value": "government_authority", "definition": "Internal government review and approval chain"},
                {"value": "vendor_internal", "definition": "Vendor-internal review process"},
                {"value": "open_source_pr", "definition": "Open-source pull request review"},
                {"value": "unknown", "definition": "Process not publicly documented"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "reviewer_diversity",
            "label": "Reviewer/author diversity",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Subjective",
            "stability": "Static",
            "obtainability": "Difficult",
            "enum_values": [
                {"value": "multi_stakeholder", "definition": "Reviewers from multiple independent organisations"},
                {"value": "single_org_multi_team", "definition": "Multiple teams within one organisation"},
                {"value": "single_team", "definition": "Authored and reviewed by same team"},
                {"value": "unknown", "definition": "Reviewer composition not publicly documented"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "errata_process",
            "label": "Formal errata/correction process",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "formal_published", "definition": "Dedicated errata notices or revision notes"},
                {"value": "inline_revision", "definition": "Corrections folded into next regular release"},
                {"value": "unknown", "definition": "Process not publicly documented"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "retirement_process",
            "label": "End-of-life / retirement process",
            "category": "Governance & Maintenance",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "explicit_eol", "definition": "Published sunset dates or end-of-support declarations"},
                {"value": "implicit_abandonment", "definition": "No update for 2+ years without formal retirement"},
                {"value": "not_applicable", "definition": "Framework is version-agnostic"},
                {"value": "unknown", "definition": "No retirement information published"},
            ],
            "rubric": None,
        },
        # ── 4.5 Access & Licensing ───────────────────────────────────────
        {
            "attribute_id": "access_cost",
            "label": "Cost to access full content",
            "category": "Access & Licensing",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Continuous",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "free_open", "definition": "Freely available without registration"},
                {"value": "free_registration", "definition": "Free but requires account registration"},
                {"value": "free_subscription", "definition": "Free tier of a paid product provides access"},
                {"value": "paid", "definition": "Full content behind paywall"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "licence_type",
            "label": "Usage/redistribution licence",
            "category": "Access & Licensing",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "open_source", "definition": "OSI-approved licence"},
                {"value": "government_public", "definition": "Government publication, public domain"},
                {"value": "proprietary_free", "definition": "Proprietary but free to use"},
                {"value": "proprietary_paid", "definition": "Proprietary and paid"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "language_availability",
            "label": "Languages in which the baseline is published",
            "category": "Access & Licensing",
            "data_type": "Free text (list)",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Easy",
            "enum_values": None,
            "rubric": None,
        },
        # ── 4.6 Format & Parseability ────────────────────────────────────
        {
            "attribute_id": "primary_format",
            "label": "Primary publication format",
            "category": "Format & Parseability",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "scap_xccdf", "definition": "SCAP/XCCDF datastream"},
                {"value": "gpo_export", "definition": "Group Policy Object backup"},
                {"value": "intune_template", "definition": "Intune security baseline template"},
                {"value": "structured_data", "definition": "JSON, XML, YAML, or equivalent"},
                {"value": "pdf_prose", "definition": "PDF or web document with prose guidance"},
                {"value": "ansible_role", "definition": "Ansible playbook/role"},
                {"value": "script", "definition": "Shell script, PowerShell script, or equivalent"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "scap_compliance_level",
            "label": "SCAP specification compliance",
            "category": "Format & Parseability",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "scap_validated", "definition": "NIST SCAP Validated product"},
                {"value": "scap_conformant", "definition": "Publishes SCAP content but not validated"},
                {"value": "none", "definition": "No SCAP content published"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "remediation_formats",
            "label": "Available remediation/enforcement formats",
            "category": "Format & Parseability",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "gpo", "definition": "Group Policy Object"},
                {"value": "intune", "definition": "Intune"},
                {"value": "ansible", "definition": "Ansible"},
                {"value": "puppet", "definition": "Puppet"},
                {"value": "chef", "definition": "Chef"},
                {"value": "bash_script", "definition": "Bash script"},
                {"value": "powershell_script", "definition": "PowerShell script"},
                {"value": "scap_remediation", "definition": "SCAP remediation"},
                {"value": "none", "definition": "None"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "variable_parameterisation",
            "label": "Site-specific value customisation",
            "category": "Format & Parseability",
            "data_type": "Boolean",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
        # ── 4.7 Tooling & Automation ─────────────────────────────────────
        {
            "attribute_id": "assessment_tooling",
            "label": "Native assessment/scanning tool",
            "category": "Tooling & Automation",
            "data_type": "Enum",
            "objective_subjective": "Objective",
            "stability": "Continuous",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "dedicated_tool", "definition": "Publisher provides a dedicated scanning tool"},
                {"value": "integrated_platform", "definition": "Assessment built into a management platform"},
                {"value": "third_party_only", "definition": "No publisher tool, third-party tools available"},
                {"value": "none", "definition": "No known automated assessment tooling"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "diff_tooling",
            "label": "Baseline version comparison tooling",
            "category": "Tooling & Automation",
            "data_type": "Boolean",
            "objective_subjective": "Objective",
            "stability": "Continuous",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "continuous_compliance",
            "label": "Continuous compliance monitoring support",
            "category": "Tooling & Automation",
            "data_type": "Boolean",
            "objective_subjective": "Objective",
            "stability": "Continuous",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
        {
            "attribute_id": "management_tool_alignment",
            "label": "Management tool alignment",
            "category": "Tooling & Automation",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "gpo_native", "definition": "Directly importable as GPO"},
                {"value": "intune_native", "definition": "Built-in Intune template"},
                {"value": "ansible_native", "definition": "Publisher-provided Ansible content"},
                {"value": "openscap_native", "definition": "Publisher-provided SCAP content for OpenSCAP"},
                {"value": "tool_agnostic", "definition": "Published as prose/settings without tool-specific packaging"},
                {"value": "other", "definition": "Other tool alignment"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "profile_inheritance",
            "label": "Profile inheritance or extension support",
            "category": "Tooling & Automation",
            "data_type": "Boolean",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
        # ── 4.8 Applicability & Adoption ─────────────────────────────────
        {
            "attribute_id": "compliance_framework_mapping",
            "label": "Compliance framework mappings",
            "category": "Applicability & Adoption",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Easy",
            "enum_values": [
                {"value": "nist_800_53", "definition": "NIST 800-53"},
                {"value": "cis_controls", "definition": "CIS Controls"},
                {"value": "pci_dss", "definition": "PCI DSS"},
                {"value": "hipaa", "definition": "HIPAA"},
                {"value": "iso_27001", "definition": "ISO 27001"},
                {"value": "fedramp", "definition": "FedRAMP"},
                {"value": "nis2", "definition": "NIS2"},
                {"value": "ism_au", "definition": "ISM (Australia)"},
                {"value": "rgs_fr", "definition": "RGS (France)"},
                {"value": "it_grundschutz", "definition": "IT-Grundschutz"},
                {"value": "none_explicit", "definition": "No explicit framework mapping"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "regulatory_recognition",
            "label": "Recognised by regulatory or compliance regimes",
            "category": "Applicability & Adoption",
            "data_type": "Enum (multi)",
            "objective_subjective": "Objective",
            "stability": "Static",
            "obtainability": "Moderate",
            "enum_values": [
                {"value": "dod_rmf", "definition": "Accepted for DoD Risk Management Framework"},
                {"value": "fedramp", "definition": "Accepted for FedRAMP"},
                {"value": "pci_dss", "definition": "Recognised as acceptable hardening standard"},
                {"value": "australian_gov", "definition": "Referenced by PSPF/ISM"},
                {"value": "french_gov", "definition": "Referenced by RGS"},
                {"value": "german_gov", "definition": "Referenced by BSI/KRITIS"},
                {"value": "eu_nis2", "definition": "Referenced in NIS2 compliance guidance"},
                {"value": "none_known", "definition": "No known regulatory recognition"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "adoption_breadth",
            "label": "Estimated adoption breadth",
            "category": "Applicability & Adoption",
            "data_type": "Enum",
            "objective_subjective": "Subjective",
            "stability": "Continuous",
            "obtainability": "Difficult",
            "enum_values": [
                {"value": "widespread", "definition": "De facto standard in its domain"},
                {"value": "sector_standard", "definition": "Standard within a specific sector or jurisdiction"},
                {"value": "niche", "definition": "Limited adoption, typically regional"},
                {"value": "emerging", "definition": "Recently published, adoption trajectory unclear"},
            ],
            "rubric": None,
        },
        {
            "attribute_id": "cross_baseline_mapping",
            "label": "Published mapping to other baselines",
            "category": "Applicability & Adoption",
            "data_type": "Free text (list)",
            "objective_subjective": "Objective",
            "stability": "Per release",
            "obtainability": "Moderate",
            "enum_values": None,
            "rubric": None,
        },
    ]


def _attribute_value_schema(attr: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON Schema for a single attribute's value field."""
    dt = attr["data_type"]
    enum_values = attr.get("enum_values")

    if dt == "Boolean":
        return {"type": ["boolean", "null"]}
    elif dt == "Integer":
        return {"type": ["integer", "null"]}
    elif dt == "Date":
        return {"type": ["string", "null"], "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}
    elif dt == "Free text":
        return {"type": ["string", "null"]}
    elif dt == "Free text (list)":
        return {
            "oneOf": [
                {"type": "array", "items": {"type": "string"}},
                {"type": "null"},
            ]
        }
    elif dt == "Enum" and enum_values:
        values = [ev["value"] for ev in enum_values]
        return {"enum": values + [None]}
    elif dt == "Enum (multi)" and enum_values:
        values = [ev["value"] for ev in enum_values]
        return {
            "oneOf": [
                {"type": "array", "items": {"enum": values}, "uniqueItems": True},
                {"type": "null"},
            ]
        }
    else:
        return {"type": ["string", "null"]}


def generate_schema() -> dict[str, Any]:
    """Generate the complete JSON Schema for ``baselines.json``."""
    catalogue = load_data_dictionary()

    # Build attribute properties for each baseline's attributes object
    attribute_properties: dict[str, Any] = {}
    for attr in catalogue:
        aid = attr["attribute_id"]
        value_schema = _attribute_value_schema(attr)

        attribute_properties[aid] = {
            "type": "object",
            "required": [
                "value", "missing", "missing_reason", "confidence",
                "trust_tier", "source", "collection_method",
                "curator_id", "review_date", "ttl_days",
            ],
            "additionalProperties": False,
            "properties": {
                "value": value_schema,
                "missing": {"type": "boolean"},
                "missing_reason": {
                    "enum": [
                        "paywalled", "empirical-only", "no source found",
                        "disputed", "not applicable", "consensus-disagreement",
                        None,
                    ]
                },
                "confidence": {"enum": ["High", "Medium", "Low"]},
                "trust_tier": {"type": "integer", "minimum": 1, "maximum": 4},
                "source": {
                    "type": "object",
                    "required": ["url", "document", "section", "accessed"],
                    "additionalProperties": False,
                    "properties": {
                        "url": {"type": "string"},
                        "document": {"type": "string"},
                        "section": {"type": "string"},
                        "accessed": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                    },
                },
                "llm_provenance": {
                    "oneOf": [
                        {"type": "null"},
                        {
                            "type": "object",
                            "required": [
                                "models", "prompt_version",
                                "consensus_reached", "agreed_value",
                            ],
                            "additionalProperties": False,
                            "properties": {
                                "models": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "provider", "model_id",
                                            "model_version", "output",
                                            "justification",
                                        ],
                                        "additionalProperties": False,
                                        "properties": {
                                            "provider": {"type": "string"},
                                            "model_id": {"type": "string"},
                                            "model_version": {"type": "string"},
                                            "output": {},
                                            "justification": {"type": "string"},
                                        },
                                    },
                                },
                                "prompt_version": {"type": "string"},
                                "consensus_reached": {"type": "boolean"},
                                "agreed_value": {},
                            },
                        },
                    ]
                },
                "collection_method": {
                    "enum": [
                        "automated_parse", "human_curation",
                        "llm_consensus", "analyst_scoring",
                        "community_aggregation",
                    ]
                },
                "curator_id": {"type": "string"},
                "review_date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "ttl_days": {"type": "integer", "minimum": 1},
            },
        }

    # Build the attribute_schema array item schema
    attribute_schema_item: dict[str, Any] = {
        "type": "object",
        "required": [
            "attribute_id", "label", "category", "data_type",
            "objective_subjective", "stability", "obtainability",
        ],
        "additionalProperties": False,
        "properties": {
            "attribute_id": {"type": "string"},
            "label": {"type": "string"},
            "category": {"type": "string"},
            "data_type": {
                "enum": [
                    "Boolean", "Enum", "Enum (multi)", "Date",
                    "Integer", "Free text", "Free text (list)",
                ]
            },
            "objective_subjective": {"enum": ["Objective", "Subjective"]},
            "stability": {"enum": ["Static", "Per release", "Continuous"]},
            "obtainability": {"enum": ["Easy", "Moderate", "Difficult"]},
            "enum_values": {
                "oneOf": [
                    {"type": "null"},
                    {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["value", "definition"],
                            "additionalProperties": False,
                            "properties": {
                                "value": {"type": "string"},
                                "definition": {"type": "string"},
                            },
                        },
                    },
                ]
            },
            "rubric": {"type": ["string", "null"]},
        },
    }

    schema: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "BST Knowledge Base",
        "description": "Schema for data/baselines.json — the BST knowledge base.",
        "type": "object",
        "required": ["meta", "disclaimer", "attribute_schema", "baselines"],
        "additionalProperties": False,
        "properties": {
            "meta": {
                "type": "object",
                "required": [
                    "schema_version", "generated_at", "generated_by",
                    "baseline_count", "tenant_id",
                ],
                "additionalProperties": False,
                "properties": {
                    "schema_version": {"const": "1"},
                    "generated_at": {"type": "string"},
                    "generated_by": {"type": "string"},
                    "baseline_count": {"type": "integer", "minimum": 0},
                    "tenant_id": {"type": "string"},
                },
            },
            "disclaimer": {
                "type": "object",
                "required": ["version", "text", "attribution"],
                "additionalProperties": False,
                "properties": {
                    "version": {"type": "string"},
                    "text": {"type": "string", "minLength": 1},
                    "attribution": {"type": "string", "minLength": 1},
                },
            },
            "attribute_schema": {
                "type": "array",
                "items": attribute_schema_item,
                "minItems": 45,
                "maxItems": 45,
            },
            "baselines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "baseline_id", "tenant_id", "display_name",
                        "issuer", "baseline_type", "attributes",
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "baseline_id": {"type": "string"},
                        "tenant_id": {"type": "string"},
                        "display_name": {"type": "string"},
                        "issuer": {"type": "string"},
                        "baseline_type": {"type": "string"},
                        "attributes": {
                            "type": "object",
                            "properties": attribute_properties,
                            "additionalProperties": False,
                        },
                    },
                },
            },
        },
    }

    return schema


def main() -> None:
    """Generate and write the schema file."""
    schema = generate_schema()
    output_path = Path(__file__).resolve().parent.parent / "schemas" / "baselines.schema.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Schema written to {output_path}")


if __name__ == "__main__":
    main()
