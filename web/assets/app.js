/**
 * BST Alpine.js application — all UI logic.
 *
 * Implements 9 user stories (UC-01a through UC-06b) and the
 * recommendation engine (architecture §13.7).
 *
 * No inline scripts (CSP compliance). No external CDN calls (FR-P06).
 */

/* global Alpine */

// ── Weight vector (FD §14.5.5) ──────────────────────────────────────────
const BASE_WEIGHTS = {
  issuer_name: 0, issuer_type: 1, baseline_type: 2, baseline_version: 0,
  initial_release_date: 0, country_of_origin: 0, target_platforms: 0,
  platform_type: 1, role_targeting: 2, scope_depth: 3, composability: 2,
  prescriptiveness: 3, version_granularity: 1, setting_count: 1,
  rationale_per_setting: 2, default_value_documented: 2,
  audit_procedure_specificity: 2, fix_procedure_specificity: 2,
  impact_assessment: 2, severity_classification: 2,
  conflict_documentation: 1, update_cadence: 2, last_update_date: 2,
  new_os_coverage_lag: 2, changelog_transparency: 1, review_process: 2,
  reviewer_diversity: 1, errata_process: 1, retirement_process: 1,
  access_cost: 0, licence_type: 1, language_availability: 0,
  primary_format: 2, scap_compliance_level: 2, remediation_formats: 2,
  variable_parameterisation: 1, assessment_tooling: 2, diff_tooling: 1,
  continuous_compliance: 2, management_tool_alignment: 2,
  profile_inheritance: 1, compliance_framework_mapping: 2,
  regulatory_recognition: 2, adoption_breadth: 1, cross_baseline_mapping: 1
};

// ── EQ-driven weight modifiers (FD §14.5.6) ────────────────────────────
const EQ_MODIFIERS = {
  EQ_02: {
    condition: (a) => a === 'government_defence' || a === 'regulated_industry',
    attrs: ['compliance_framework_mapping', 'regulatory_recognition']
  },
  EQ_03: {
    condition: (a) => a === 'yes',
    attrs: ['primary_format', 'scap_compliance_level', 'remediation_formats', 'variable_parameterisation']
  },
  EQ_05: {
    condition: (a) => a === 'yes',
    attrs: ['assessment_tooling', 'continuous_compliance', 'management_tool_alignment']
  },
  EQ_06: {
    condition: (a) => a === 'yes',
    attrs: ['review_process', 'reviewer_diversity', 'errata_process']
  },
  EQ_07: {
    condition: (a) => a === 'per_setting',
    attrs: ['setting_count', 'audit_procedure_specificity', 'fix_procedure_specificity']
  }
};

// ── Compatibility scoring rules (FD §14.5.7) ───────────────────────────

// Category C: ordered enum scores
const ORDERED_ENUM_SCORES = {
  issuer_type: { standards_body: 1.0, government_military: 0.75, open_source_community: 0.5, academic: 0.5, vendor: 0.25 },
  baseline_type: { technical_benchmark: 1.0, checklist_repository: 0.75, strategic_framework: 0.5, isms_module: 0.5 },
  scope_depth: { full_surface: 1.0, component_specific: 0.5, strategic_subset: 0.5, architectural: 0.25 },
  composability: { standalone: 1.0, modular_framework: 0.75, composition_required: 0.5 },
  version_granularity: { per_build: 1.0, per_major_version: 0.75, per_os_family: 0.5, version_agnostic: 0.25 },
  rationale_per_setting: { yes_all: 1.0, yes_partial: 0.5, no: 0.0 },
  default_value_documented: { yes_all: 1.0, yes_partial: 0.5, no: 0.0 },
  audit_procedure_specificity: { machine_verifiable: 1.0, step_by_step: 0.75, descriptive: 0.25, none: 0.0 },
  fix_procedure_specificity: { machine_executable: 1.0, step_by_step: 0.75, descriptive: 0.25, none: 0.0 },
  impact_assessment: { per_setting: 1.0, aggregate_only: 0.5, none: 0.0 },
  severity_classification: { yes_granular: 1.0, yes_tiered: 0.5, no: 0.0 },
  changelog_transparency: { per_setting_diff: 1.0, summary_changelog: 0.75, version_number_only: 0.25, none: 0.0 },
  review_process: { formal_consensus: 1.0, government_authority: 0.75, open_source_pr: 0.5, vendor_internal: 0.25, unknown: 0.0 },
  reviewer_diversity: { multi_stakeholder: 1.0, single_org_multi_team: 0.75, single_team: 0.25, unknown: 0.0 },
  errata_process: { formal_published: 1.0, inline_revision: 0.5, unknown: 0.0 },
  retirement_process: { explicit_eol: 1.0, not_applicable: 0.5, implicit_abandonment: 0.25, unknown: 0.0 },
  new_os_coverage_lag: { days_to_weeks: 1.0, one_to_six_months: 0.75, six_to_twelve_months: 0.25, twelve_plus_months: 0.0 },
  update_cadence: { continuous: 1.0, quarterly: 0.75, per_os_release: 0.5, annual: 0.25, irregular: 0.0 },
  scap_compliance_level: { scap_validated: 1.0, scap_conformant: 0.5, none: 0.0 },
  assessment_tooling: { dedicated_tool: 1.0, integrated_platform: 0.75, third_party_only: 0.25, none: 0.0 },
  adoption_breadth: { widespread: 1.0, sector_standard: 0.75, niche: 0.25, emerging: 0.0 },
  licence_type: { open_source: 1.0, government_public: 0.75, proprietary_free: 0.5, proprietary_paid: 0.25 }
};

// Category B: boolean attributes
const BOOLEAN_ATTRS = ['conflict_documentation', 'diff_tooling', 'continuous_compliance', 'variable_parameterisation', 'profile_inheritance'];

// Category E: multi-value scoring rules
const REMEDIATION_FORMAT_COUNT = 8;
const COMPLIANCE_FRAMEWORK_COUNT = 11;
const REGULATORY_RECOGNITION_COUNT = 8;

const PRIMARY_FORMAT_SCORES = {
  scap_xccdf: 1.0, gpo_export: 0.75, intune_template: 0.75,
  ansible_role: 0.75, script: 0.75, structured_data: 0.75, pdf_prose: 0.25
};

const MANAGEMENT_TOOL_SCORES = {
  gpo_native: 1.0, intune_native: 1.0, ansible_native: 1.0,
  openscap_native: 1.0, other: 0.5, tool_agnostic: 0.25
};

// ── Wizard questions (FD §14.5.4) ──────────────────────────────────────
const WIZARD_QUESTIONS = [
  {
    id: 'EQ_01', question: 'What is your target operating system?',
    context: 'This determines which baselines are applicable to your environment.',
    options: [
      { value: 'windows_11', label: 'Windows 11' },
      { value: 'windows_server_2022', label: 'Windows Server 2022' },
      { value: 'ubuntu_22', label: 'Ubuntu 22.04' },
      { value: 'ubuntu_24', label: 'Ubuntu 24.04' },
      { value: 'rhel_8_9', label: 'Red Hat Enterprise Linux 8/9' },
      { value: 'macos', label: 'macOS' },
      { value: 'other', label: 'Other / not listed' }
    ]
  },
  {
    id: 'EQ_02', question: 'What is your organisational context?',
    context: 'Regulated environments value formal compliance mappings and regulatory recognition.',
    options: [
      { value: 'government_defence', label: 'Government or defence organisation' },
      { value: 'regulated_industry', label: 'Finance, healthcare, critical infrastructure, or other regulated sector' },
      { value: 'commercial_unregulated', label: 'Commercial organisation without sector-specific mandates' }
    ]
  },
  {
    id: 'EQ_03', question: 'Is a machine-readable format required?',
    context: 'Machine-readable formats enable automated enforcement and compliance scanning.',
    options: [
      { value: 'yes', label: 'Yes — machine-readable format required' },
      { value: 'no', label: 'No — not required' }
    ]
  },
  {
    id: 'EQ_04', question: 'Must the baseline be free to access?',
    context: 'Some baselines require paid subscriptions or licences for full content access.',
    options: [
      { value: 'yes', label: 'Yes — baseline must be free' },
      { value: 'no', label: 'No — paid baselines are acceptable' }
    ]
  },
  {
    id: 'EQ_05', question: 'Do you need continuous compliance tooling?',
    context: 'Continuous compliance monitoring detects configuration drift after initial hardening.',
    options: [
      { value: 'yes', label: 'Yes — continuous compliance tooling needed' },
      { value: 'no', label: 'No — not required' }
    ]
  },
  {
    id: 'EQ_06', question: 'Does formal review process rigour matter?',
    context: 'Governance-conscious environments value transparent, multi-stakeholder review processes.',
    options: [
      { value: 'yes', label: 'Yes — formal review rigour matters' },
      { value: 'no', label: 'No — not a priority' }
    ]
  },
  {
    id: 'EQ_07', question: 'What level of prescriptiveness do you need?',
    context: 'Per-setting guidance provides exact registry keys and values. Principle-level guidance provides strategic goals.',
    options: [
      { value: 'per_setting', label: 'Exact setting paths and values' },
      { value: 'per_control', label: 'Control-level guidance' },
      { value: 'principle_level', label: 'Strategic goals without implementation detail' }
    ]
  }
];


// ── Compatibility scoring functions ─────────────────────────────────────

function computeCompatibility(attrId, value, answers, kbMeta, allBaselines) {
  if (value === null || value === undefined) return null;

  // Category B: Boolean
  if (BOOLEAN_ATTRS.includes(attrId)) {
    return value === true ? 1.0 : 0.0;
  }

  // Category C: Ordered enum
  if (ORDERED_ENUM_SCORES[attrId]) {
    var score = ORDERED_ENUM_SCORES[attrId][value];
    return score !== undefined ? score : 0.0;
  }

  // Category D: Preference-dependent (prescriptiveness)
  if (attrId === 'prescriptiveness') {
    var eq07 = answers.EQ_07;
    var matrix = {
      per_setting:     { per_setting: 1.0, per_control: 0.5, principle_level: 0.0 },
      per_control:     { per_setting: 0.5, per_control: 1.0, principle_level: 0.5 },
      principle_level: { per_setting: 0.0, per_control: 0.5, principle_level: 1.0 }
    };
    if (matrix[eq07] && matrix[eq07][value] !== undefined) {
      return matrix[eq07][value];
    }
    return 0.0;
  }

  // Category E: Multi-value
  if (attrId === 'platform_type') {
    if (!Array.isArray(value)) return 0.0;
    return value.includes('operating_system') ? 1.0 : 0.0;
  }

  if (attrId === 'role_targeting') {
    if (!Array.isArray(value)) return 0.0;
    if (value.includes('workstation')) return 1.0;
    if (value.includes('not_role_specific')) return 0.75;
    return 0.0;
  }

  if (attrId === 'primary_format') {
    if (!Array.isArray(value)) return 0.0;
    var best = 0.0;
    value.forEach(function(v) {
      if (PRIMARY_FORMAT_SCORES[v] && PRIMARY_FORMAT_SCORES[v] > best) {
        best = PRIMARY_FORMAT_SCORES[v];
      }
    });
    return best;
  }

  if (attrId === 'remediation_formats') {
    if (!Array.isArray(value)) return 0.0;
    var nonNone = value.filter(function(v) { return v !== 'none'; });
    if (nonNone.length === 0 && value.includes('none')) return 0.0;
    return nonNone.length / REMEDIATION_FORMAT_COUNT;
  }

  if (attrId === 'compliance_framework_mapping') {
    if (!Array.isArray(value)) return 0.0;
    var mapped = value.filter(function(v) { return v !== 'none_explicit'; });
    if (mapped.length === 0) return 0.0;
    return mapped.length / COMPLIANCE_FRAMEWORK_COUNT;
  }

  if (attrId === 'regulatory_recognition') {
    if (!Array.isArray(value)) return 0.0;
    var recognised = value.filter(function(v) { return v !== 'none_known'; });
    if (recognised.length === 0) return 0.0;
    return recognised.length / REGULATORY_RECOGNITION_COUNT;
  }

  if (attrId === 'management_tool_alignment') {
    if (!Array.isArray(value)) return 0.0;
    var best2 = 0.0;
    value.forEach(function(v) {
      if (MANAGEMENT_TOOL_SCORES[v] && MANAGEMENT_TOOL_SCORES[v] > best2) {
        best2 = MANAGEMENT_TOOL_SCORES[v];
      }
    });
    return best2;
  }

  // Category F: Recency (last_update_date)
  if (attrId === 'last_update_date') {
    var genDate = kbMeta ? new Date(kbMeta.generated_at) : new Date();
    var updateDate = new Date(value);
    var months = (genDate.getFullYear() - updateDate.getFullYear()) * 12 + (genDate.getMonth() - updateDate.getMonth());
    if (months <= 6) return 1.0;
    if (months <= 12) return 0.75;
    if (months <= 24) return 0.5;
    if (months <= 36) return 0.25;
    return 0.0;
  }

  // Category G: Range-normalised (setting_count)
  if (attrId === 'setting_count') {
    if (typeof value !== 'number') return null;
    var values = [];
    allBaselines.forEach(function(b) {
      var ad = b.attributes[attrId];
      if (ad && !ad.missing && typeof ad.value === 'number') {
        values.push(ad.value);
      }
    });
    if (values.length === 0) return null;
    var min = Math.min.apply(null, values);
    var max = Math.max.apply(null, values);
    if (max === min) return 1.0;
    return (value - min) / (max - min);
  }

  return null;
}

function getEffectiveWeights(answers) {
  var weights = Object.assign({}, BASE_WEIGHTS);
  Object.keys(EQ_MODIFIERS).forEach(function(eqKey) {
    var mod = EQ_MODIFIERS[eqKey];
    if (mod.condition(answers[eqKey])) {
      mod.attrs.forEach(function(attr) {
        weights[attr] = Math.min(4, (weights[attr] || 0) + 1);
      });
    }
  });
  return weights;
}


// ── Alpine.js app ───────────────────────────────────────────────────────

function initApp() {
  return {
    // State
    kb: null,
    loadError: null,
    view: 'browser',
    filterOS: '',
    filterCategory: '',
    filteredBaselines: [],
    selectedBaseline: null,
    compareSelection: [],
    diffOnly: false,
    collapsedCategories: [],
    wizardStep: 0,
    wizardComplete: false,
    wizardAnswers: {},
    wizardQuestions: WIZARD_QUESTIONS,
    recommendations: [],
    wizardLowConfidence: false,
    availableOS: [],
    availableCategories: [],
    attributeCategories: [],

    // ── Init ──────────────────────────────────────────────────────────
    init() {
      var self = this;
      fetch('api/baselines.php')
        .then(function(resp) {
          if (!resp.ok) throw new Error('HTTP ' + resp.status);
          return resp.json();
        })
        .then(function(data) {
          self.kb = data;
          self.filteredBaselines = data.baselines || [];
          self._buildFilterOptions();
          self._buildAttributeCategories();
          self._loadFooterLinks();
        })
        .catch(function(err) {
          self.loadError = err.message;
        });
    },

    // ── Filter (UC-01b) ─────────────────────────────────────────────
    applyFilters() {
      this.filteredBaselines = filterBaselines(
        this.kb ? this.kb.baselines : [],
        this.filterOS,
        this.filterCategory
      );
    },

    // ── Baseline selection (UC-02) ──────────────────────────────────
    selectBaseline(b) {
      this.selectedBaseline = b;
    },

    // ── Compare (UC-03) ─────────────────────────────────────────────
    toggleCompare(bid) {
      var idx = this.compareSelection.indexOf(bid);
      if (idx >= 0) {
        this.compareSelection.splice(idx, 1);
      } else if (this.compareSelection.length < 4) {
        this.compareSelection.push(bid);
      }
    },

    compareAttributes(category) {
      var self = this;
      var attrs = this.attributesInCategory(category);
      if (!this.diffOnly) return attrs;

      return attrs.filter(function(attr) {
        var values = self.compareSelection.map(function(bid) {
          var ad = self.getBaselineAttr(bid, attr.attribute_id);
          return ad ? JSON.stringify(ad.value) : null;
        });
        return new Set(values).size > 1;
      });
    },

    // ── Wizard (UC-04a/b) ───────────────────────────────────────────
    runWizard() {
      var result = computeRecommendation(
        this.kb.baselines,
        this.wizardAnswers,
        this.kb.meta,
        this.kb.attribute_schema
      );
      this.recommendations = result.ranked;
      this.wizardLowConfidence = result.lowConfidence;
      this.wizardComplete = true;
    },

    // ── Export (UC-06a/b) ───────────────────────────────────────────
    exportPdf() {
      window.print();
    },

    exportMarkdown() {
      var md = generateMarkdownExport(
        this.view === 'wizard' ? this.recommendations : null,
        this.view === 'compare' ? this.compareSelection : null,
        this.kb,
        this.wizardAnswers
      );
      var blob = new Blob([md], { type: 'text/markdown; charset=utf-8' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'bst-export.md';
      a.click();
      URL.revokeObjectURL(url);
    },

    // ── Helpers ─────────────────────────────────────────────────────
    getAttrData(baseline, attrId) {
      if (!baseline || !baseline.attributes) return null;
      return baseline.attributes[attrId] || null;
    },

    getBaselineAttr(bid, attrId) {
      if (!this.kb) return null;
      var b = this.kb.baselines.find(function(bl) { return bl.baseline_id === bid; });
      return b ? (b.attributes[attrId] || null) : null;
    },

    getBaselineName(bid) {
      if (!this.kb) return bid;
      var b = this.kb.baselines.find(function(bl) { return bl.baseline_id === bid; });
      return b ? b.display_name : bid;
    },

    attributesInCategory(category) {
      if (!this.kb) return [];
      return this.kb.attribute_schema.filter(function(a) { return a.category === category; });
    },

    formatValue(val) {
      if (val === null || val === undefined) return '—';
      if (Array.isArray(val)) return val.join(', ');
      if (typeof val === 'boolean') return val ? 'Yes' : 'No';
      return String(val);
    },

    toggleCategory(cat) {
      var idx = this.collapsedCategories.indexOf(cat);
      if (idx >= 0) {
        this.collapsedCategories.splice(idx, 1);
      } else {
        this.collapsedCategories.push(cat);
      }
    },

    flagValueUrl(baselineId, attrId, currentValue) {
      var title = encodeURIComponent('Flag value: ' + baselineId + '/' + attrId);
      var body = encodeURIComponent(
        'Baseline: ' + baselineId + '\n' +
        'Attribute: ' + attrId + '\n' +
        'Current value: ' + JSON.stringify(currentValue) + '\n\n' +
        'Suggested correction:\n'
      );
      return 'https://github.com/quality-factory/Web_App_-_Baseline_Selection_Tool/issues/new?title=' + title + '&body=' + body;
    },

    _buildFilterOptions() {
      var osSet = new Set();
      var catSet = new Set();
      (this.kb.baselines || []).forEach(function(b) {
        if (b.attributes.target_platforms && !b.attributes.target_platforms.missing) {
          var platforms = b.attributes.target_platforms.value;
          if (Array.isArray(platforms)) {
            platforms.forEach(function(p) { osSet.add(p); });
          }
        }
        if (b.baseline_type) catSet.add(b.baseline_type);
      });
      this.availableOS = Array.from(osSet).sort();
      this.availableCategories = Array.from(catSet).sort();
    },

    _buildAttributeCategories() {
      var cats = [];
      (this.kb.attribute_schema || []).forEach(function(a) {
        if (cats.indexOf(a.category) < 0) cats.push(a.category);
      });
      this.attributeCategories = cats;
    },

    _loadFooterLinks() {
      // Footer links loaded from settings.php via a tiny fetch
      // In production these are set server-side; here we use defaults
      var gtcLink = document.getElementById('footer-gtc');
      var privacyLink = document.getElementById('footer-privacy');
      if (gtcLink) gtcLink.href = 'https://www.qualityfactory.com/general-terms-and-conditions/';
      if (privacyLink) privacyLink.href = 'https://www.qualityfactory.com/privacy-statement/';
    }
  };
}


// ── Standalone functions ────────────────────────────────────────────────

function filterBaselines(baselines, os, category) {
  return baselines.filter(function(b) {
    if (os) {
      var tp = b.attributes.target_platforms;
      if (!tp || tp.missing) return false;
      var platforms = tp.value;
      if (!Array.isArray(platforms)) return false;
      var match = platforms.some(function(p) {
        return p.toLowerCase().indexOf(os.toLowerCase()) >= 0;
      });
      if (!match) return false;
    }
    if (category && b.baseline_type !== category) return false;
    return true;
  });
}


function computeRecommendation(baselines, answers, kbMeta, attrSchema) {
  var weights = getEffectiveWeights(answers);
  var highWeightThreshold = 3;
  var scored = [];
  var excluded = [];
  var lowConfidence = false;

  baselines.forEach(function(b) {
    // Hard filter: EQ-01 OS mismatch
    if (answers.EQ_01 && answers.EQ_01 !== 'other') {
      var tp = b.attributes.target_platforms;
      if (tp && !tp.missing && Array.isArray(tp.value)) {
        var osMatch = tp.value.some(function(p) {
          return p.toLowerCase().indexOf(answers.EQ_01.replace(/_/g, ' ').toLowerCase().split(' ')[0]) >= 0;
        });
        if (!osMatch) {
          excluded.push({
            baseline_id: b.baseline_id,
            display_name: b.display_name,
            excluded: true,
            exclusion_reason: 'OS mismatch (target platform not supported)',
            score: 0
          });
          return;
        }
      }
    }

    // Hard filter: EQ-04 paid when free required
    if (answers.EQ_04 === 'yes') {
      var ac = b.attributes.access_cost;
      if (ac && !ac.missing && ac.value === 'paid') {
        excluded.push({
          baseline_id: b.baseline_id,
          display_name: b.display_name,
          excluded: true,
          exclusion_reason: 'Paid baseline (free access required)',
          score: 0
        });
        return;
      }
    }

    // Scoring
    var weightedSum = 0;
    var weightSum = 0;
    var missingHighWeight = 0;

    Object.keys(weights).forEach(function(attrId) {
      var w = weights[attrId];
      if (w === 0) return;

      var ad = b.attributes[attrId];
      if (!ad || ad.missing) {
        if (w >= highWeightThreshold) missingHighWeight++;
        return;
      }

      var compat = computeCompatibility(attrId, ad.value, answers, kbMeta, baselines);
      if (compat === null) return;

      weightedSum += w * compat;
      weightSum += w;
    });

    var score = weightSum > 0 ? weightedSum / weightSum : 0;

    if (missingHighWeight > 3) lowConfidence = true;

    var topAttrs = [];
    Object.keys(weights).forEach(function(attrId) {
      if (weights[attrId] >= highWeightThreshold) {
        var ad = b.attributes[attrId];
        if (ad && !ad.missing) {
          var c = computeCompatibility(attrId, ad.value, answers, kbMeta, baselines);
          if (c !== null && c >= 0.75) {
            var schema = attrSchema.find(function(a) { return a.attribute_id === attrId; });
            topAttrs.push(schema ? schema.label : attrId);
          }
        }
      }
    });

    scored.push({
      baseline_id: b.baseline_id,
      display_name: b.display_name,
      excluded: false,
      score: score,
      missingHighWeight: missingHighWeight,
      explanation: topAttrs.length > 0
        ? 'Strong on: ' + topAttrs.slice(0, 3).join(', ')
        : 'Moderate match across attributes'
    });
  });

  scored.sort(function(a, b) { return b.score - a.score; });
  var ranked = scored.concat(excluded);

  return { ranked: ranked, lowConfidence: lowConfidence };
}


function generateMarkdownExport(recommendations, compareIds, kb, answers) {
  var lines = ['# Baseline Selection Tool — Export\n'];
  lines.push('**KB version:** ' + (kb.meta.generated_by || 'unknown'));
  lines.push('**Generated:** ' + (kb.meta.generated_at || 'unknown'));
  lines.push('');

  // Disclaimer
  if (kb.disclaimer) {
    lines.push('## Disclaimer\n');
    lines.push(kb.disclaimer.text);
    lines.push('\n— ' + kb.disclaimer.attribution);
    lines.push('');
  }

  if (recommendations) {
    lines.push('## Recommendation Results\n');
    if (answers) {
      lines.push('### Environment Profile\n');
      Object.keys(answers).forEach(function(k) {
        lines.push('- **' + k + ':** ' + answers[k]);
      });
      lines.push('');
    }

    lines.push('### Ranked Baselines\n');
    lines.push('| Rank | Baseline | Score | Notes |');
    lines.push('|------|----------|-------|-------|');
    recommendations.forEach(function(rec, idx) {
      if (rec.excluded) {
        lines.push('| — | ' + rec.display_name + ' | — | Excluded: ' + rec.exclusion_reason + ' |');
      } else {
        lines.push('| ' + (idx + 1) + ' | ' + rec.display_name + ' | ' + (rec.score * 100).toFixed(1) + '% | ' + (rec.explanation || '') + ' |');
      }
    });
  }

  if (compareIds && kb) {
    lines.push('## Comparison\n');
    var baselines = compareIds.map(function(bid) {
      return kb.baselines.find(function(b) { return b.baseline_id === bid; });
    }).filter(Boolean);

    if (baselines.length > 0) {
      var header = '| Attribute |';
      var sep = '|-----------|';
      baselines.forEach(function(b) {
        header += ' ' + b.display_name + ' |';
        sep += '------|';
      });
      lines.push(header);
      lines.push(sep);

      (kb.attribute_schema || []).forEach(function(attr) {
        var row = '| ' + attr.label + ' |';
        baselines.forEach(function(b) {
          var ad = b.attributes[attr.attribute_id];
          if (ad && ad.missing) {
            row += ' Missing |';
          } else if (ad) {
            var v = ad.value;
            if (Array.isArray(v)) v = v.join(', ');
            if (typeof v === 'boolean') v = v ? 'Yes' : 'No';
            row += ' ' + String(v || '—') + ' |';
          } else {
            row += ' — |';
          }
        });
        lines.push(row);
      });
    }
  }

  return lines.join('\n');
}
