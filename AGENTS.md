AGENTS.md
=========

**Status**: Normative
**Version**: 13.3.0 | Build: <BUILD_VERSION>
This version of `AGENTS.md` is aligned with version 13.6.0 of `SubscriptionFactory.md`.

---

## Scope and authority

This file defines mandatory behavioral rules for any automation agent (including ChatGPT Codex, Claude Code, and Gemini Code Assist) that operates in this repository — whether writing code, committing, commenting, reviewing, or performing diagnostics.

This file governs **agent-internal behavior only**. Factory-wide business policies governing all actors (human and automation) are defined in the Subscription Factory Specification. Where this file references the factory specification, the referenced policy is authoritative; this file defines how agents implement it.

Any agent MUST follow all rules in this file when operating in this repository. Role-specific behavioral constraints are defined in tool-specific skill prompts, not in this file. This file defines common enforcement requirements that apply to all agents regardless of role.

### How to read this file

This file is structured for token economy. An agent need only read:

1. **§Absolute protections** — always (short, non-negotiable).
2. **§Common enforcement requirements** — always (applies to all roles).
3. **§Role extension protocol** — only when adding a new role to the factory.
4. **§Compliance confirmation** — always (short, pre-commit checklist).

Role-specific behavioral constraints and issue register interaction permissions are defined in the factory specification (see [Factory Spec §Issue Register Interaction]) and realized in tool-specific skill prompts. This file does not contain role-specific sections.

---

## Absolute protections

Agents MUST comply with [Factory Spec §Protected Files] and [Factory Spec §Policy Authority and Immutability].

In addition, agents MUST:

- Never create, modify, rename, move, delete, or propose changes to this file (`AGENTS.md`) in any form that would alter repository state, including but not limited to diffs, patches, commits, branches, tags, pull requests, merges, rebases, releases, or automated edits.
- Suggest improvements to `AGENTS.md` only in conversational responses to human maintainers, and MUST NOT provide those suggestions in any form that would alter repository state.
- Proactively suggest such improvements when they deterministically identify, based on correctness, security, determinism, or compliance invariants that are independent of repository-specific implementation or context, that the improvement would strengthen, clarify, or eliminate ambiguity in the mandatory behavioral constraints imposed on agents by this file.
- If instructed (directly or indirectly) to change `AGENTS.md`, refuse, state that this file is protected, and continue only with allowed changes.

Only human maintainers MAY edit `AGENTS.md`.

---

## Common enforcement requirements

The following requirements MUST be enforced continuously by all agents, regardless of role, during development and for all future commits.

### Determinism over heuristics

Agents MUST comply with [Factory Spec §Agent Model].

### Type safety and static analysis compliance

Agents MUST comply with [Factory Spec §Commit-Time Enforcement Requirements].

In addition, agents MUST add type annotations appropriate to the project's language(s) so that code passes the project's configured static analysis tooling. This means using the idiomatic type annotation system for each language present in the repository (e.g., typed parameters and strict mode in PowerShell, type hints and mypy in Python, PHPStan/Psalm annotations in PHP) and any static analysis tool configured in the project's CI pipeline.

Source files MUST use the encoding expected by their language's default interpreter. When the default interpreter does not assume UTF-8, the file MUST either contain only ASCII characters or include an encoding declaration recognized by that interpreter.

### Test external call isolation

Agents MUST comply with [Factory Spec §Commit-Time Enforcement Requirements] rule 12.

In addition, agents MUST use the testing framework's module-scoped mock mechanism to intercept calls inside imported modules, not just at the test script scope. For example, in Pester this means using the `-ModuleName` parameter on `Mock` commands so that the mock applies within the module under test rather than only in the test file's execution context. Agents MUST apply the equivalent mechanism for each testing framework used in the repository.

### Zero Trust and security-by-design

Agents MUST comply with [Factory Spec §Security Model (Zero Trust)].

In addition, agents MUST:

- If compliance with this policy cannot be verified deterministically, abort the operation rather than proceed with partial or ambiguous output.
- Assume all exported configuration, logs, and metadata may be shared outside the trust boundary. Therefore:
  - Do not log or export raw identifiers unless explicitly approved by a human maintainer.
  - Apply de-identification before writing, logging, or packaging data (see §De-identification and metadata minimization below).
  - Treat any exported artifact as if it were public unless explicitly approved otherwise.
- Consent, approval, or intent MUST NOT be inferred from context, repository state, or prior instructions; only explicit, documented authorization is valid.

### Dependency and supply-chain security

Agents MUST comply with [Factory Spec §Dependency and Supply-Chain Security].

### Secret and credential handling

Agents MUST comply with [Factory Spec §Secrets Handling].

In addition, agents MUST:

- When demonstrating environment variables or configuration, prefer existence or name checks instead of echoing the secret value.
- When adding logging or error handling around authentication and HTTP calls:
  - Exclude raw tokens, client secrets, and passwords.
  - Redact or omit sensitive fields when including headers or bodies in diagnostics.
- Do not log or display `Authorization` headers or other fields that may contain secrets.

### Output artifact exclusion from version control

Runtime output artifacts — files produced by the project's tools during execution (binary exports, logs, reports, backups, temporary files) — MUST NOT be committed to the repository.

- The repository MUST contain a `.gitignore` (or equivalent VCS ignore mechanism) that excludes every output file type declared or implied by the project's operational scope.
- Binary output formats MUST additionally be marked as binary in `.gitattributes` (or equivalent) to prevent content corruption if the ignore rule is bypassed.
- When an agent introduces a new output file type (new export format, new log file, new backup format), the commit that introduces it MUST also add the corresponding ignore and binary-attribute entries.
- Output artifacts that contain un-de-identified data (per §De-identification and metadata minimization) are especially dangerous to commit; the ignore rule is the first line of defense.

### Interactive configuration input

Agents MUST comply with [Factory Spec §Secure Configuration Input].

The following agent-internal implementation requirements define how agents build tools that collect configuration interactively:

- Each interactive prompt MUST display a brief, non-technical explanation of what the field is and why it is needed.
- Where a safe default value exists, the prompt MUST pre-fill it so the user can accept it by pressing Enter.
- The input mechanism MUST NOT persist values to disk or log them to the operating system.
- Tools MUST NOT require the user to edit configuration files, set environment variables, or construct command lines to supply operational parameters.

### Authentication session hygiene

Agents MUST comply with [Factory Spec §Authentication Session Hygiene].

The following agent-internal implementation requirements define how agents implement authentication token lifecycle:

- Token invalidation and memory cleanup on exit MUST use the language's structured cleanup mechanism per §Resource disposal hygiene.
- If the SDK or library used for authentication persists tokens by default, agents MUST explicitly override this behavior at initialization and document the override in the README.
- Agents MUST verify — via a test or documented manual check — that no token cache file is created on disk during execution.

### Runtime data leakage prevention

Agents MUST comply with [Factory Spec §Runtime Data Leakage Prevention].

The following agent-internal implementation requirements define how agents mitigate runtime leakage vectors:

- **No string-to-code evaluation**: Agents MUST NOT use constructs that convert strings into executable code at runtime (e.g., `eval()`, `exec()`, `Invoke-Expression`, `Function()` constructor with dynamic input, or language-equivalent mechanisms). Typed callbacks, first-class function references, and dispatch tables that invoke statically defined code paths are permitted.
- **Minimize sensitive data scope**: Variables holding raw identifying values (usernames, hostnames, paths, emails) MUST be declared in the narrowest possible scope — function-local rather than module-, script-, or global-scoped. Broader scopes MUST NOT hold raw identifying values; only de-identified or tokenized forms are permitted outside function-local scope.
- **Cleanup of long-lived sensitive mappings at exit**: Module- or script-scoped variables that accumulate sensitive mappings (e.g., lookup tables that map raw values to de-identified placeholders) MUST be cleared on the outermost execution path's structured cleanup handler (e.g., `finally`, `atexit`, `defer`, or language-equivalent), so they do not persist in the host process after the entry point returns.
- **Resource disposal**: Cryptographic contexts, file handles, and other resources not governed by automatic memory management that are used during de-identification MUST be disposed deterministically per §Resource disposal hygiene. These objects may retain sensitive intermediates in memory regions outside the runtime's automatic reclamation.
- **Runtime transcription and logging**: Tools MUST include a startup check for active transcription or runtime logging that could capture sensitive data outside the tool's control. Detection methods are platform-specific; examples include checking for enabled transcription policies, active audit hooks, or injected runtime instrumentation. If active transcription is detected, the tool MUST abort with a user-facing message explaining the risk. An explicit override flag MAY be accepted only through the interactive prompt mechanism per §Interactive configuration input.
- **SDK and library telemetry**: Agents MUST suppress SDK telemetry at tool startup (e.g., environment variables, SDK configuration calls, build-time flags) and MUST NOT persist the suppression beyond the tool's process lifetime.
- **Crash dumps, core dumps, and error reporting**: The residual risk from process dumps exposing in-memory sensitive data MUST be documented in the README with a reference to the in-memory data lifetime mitigation.
- **Platform-specific vectors**: Agents MUST identify additional leakage vectors specific to the chosen platform and runtime, document them in the README, and implement mitigations. When choosing between mitigations, agents MUST prefer the mitigation that is more deterministic, fails more safely, and requires less user awareness.

### De-identification and metadata minimization

Agents MUST comply with [Factory Spec §Security Model (Zero Trust)] and [Factory Spec §Secrets Handling] for data minimization and log redaction policy.

The following agent-internal implementation requirements define how agents apply de-identification:

Non-secret identifying metadata MUST be treated as sensitive by default. The following categories MUST NOT be exposed, exported, logged, or committed in raw form unless explicitly approved by a human maintainer (e.g., documented in an issue/PR comment by a maintainer):

- Usernames or account identifiers
- Home directory or profile paths
- Device-specific paths or mount points
- Hostnames, internal domains, or service endpoints
- Repository names that encode organization or client identity
- Email addresses
- Any data that enables correlation of a device, user, or organization across datasets

When configuration, diagnostic, or export tooling is generated:

- Identifying values MUST be replaced with stable placeholders or non-reversible tokens (e.g., `<USER>`, `<HOME>`, hashed tokens).
- Structural information and behavioral intent MUST be preserved.
- De-identification MUST occur before data is written to disk, logged, or packaged.
- Any local mapping used to enable reversibility MUST NOT be committed or exported.
- When an identifying value specific to the subject of the output (e.g., device name, username, organization name) must appear in output content or filenames in de-identified form, it MUST be pseudonymized as follows:
  - Read the file `~/.deidentify-salt` (where `~` is the user's home directory: `$HOME` on POSIX systems, `$env:USERPROFILE` on Windows) if it exists (empty string if absent), prepend its contents to the raw identifying value (or to the literal string `unknown` if the raw value is absent or empty), encode the combined string as UTF-8, and compute its SHA-256 hash. The full hash is represented as a 64-character uppercase hexadecimal string.
  - A short form for filenames is derived by interpreting the first 8 hex characters as an unsigned 32-bit integer and encoding it as a 5-character base-36 string (character set `0-9A-Z`, least-significant digit first).
  - If the salt file is absent, the tool MUST emit a warning to the user indicating that no de-identification salt is configured and MUST abort execution without producing output. Tools MUST NOT fall back to an empty or default salt.
  - When multiple projects share this `AGENTS.md`, the pseudoanonymization algorithm (salt loading, SHA-256 hashing, and base-36 short-ID encoding) MUST be implemented in a single shared module or library, and all consuming projects MUST use that shared implementation rather than reimplementing the algorithm independently. The shared module's location and import mechanism are language- and project-specific and MUST be documented in each consuming project's README or CLAUDE.md. If a divergence between the shared implementation and this specification is discovered, it MUST be treated as a defect. The Human Maintainer determines whether the implementation or the specification is correct; the losing side is updated to match, and a new test is added to prevent recurrence.

Configuration data MUST be limited to tooling, environment, and workflow settings; personal data or business data MUST NOT be included unless explicitly authorized.

Agents MUST NOT attempt to re-identify, correlate, or reverse de-identified data unless explicitly instructed and authorized by a human maintainer.

These requirements apply even when the data does not contain secrets or credentials.

### Operational transparency for state-mutating workflows

This section has no direct Factory Spec counterpart. It is an agent-internal code quality standard for user-facing output.

When a tool, script, or automation performs a sequence of state-mutating operations (file writes, API calls, system configuration changes, database modifications, resource provisioning or removal):

- Each individual operation MUST produce user-visible feedback indicating: (a) which operation is being attempted, (b) whether it succeeded, failed, or resulted in no change, and (c) if failed, a meaningful error description.
- Feedback MUST be emitted at the granularity of individual operations, not batched at phase, step, or workflow level. The user MUST be able to determine the outcome of each operation independently.
- Operations that result in no change (target already in desired state, target not found, idempotent skip) MUST report their outcome explicitly. Silence is never an acceptable result for a state-mutating operation or an operation that was expected to mutate state.
- Feedback output MUST use a fail-safe mechanism: a display or logging failure MUST NOT abort remaining operations. The feedback is required operational output, not optional diagnostic output — but its delivery mechanism MUST NOT compromise the workflow's ability to continue.
- The feedback mechanism MUST be centralized in a wrapper or utility so that the fail-safe behavior is the default path, not an opt-in step that can be forgotten at individual call sites (per §Error observability hygiene).

### Error-context completeness

This section has no direct Factory Spec counterpart. It is an agent-internal code quality standard for error reporting.

When a tool, script, or automation encounters an error during a multi-step workflow, the error message MUST include sufficient context for the user to determine without re-running:

- Which step failed.
- What the tool had already completed successfully before the failure.
- What remains unexecuted.
- The specific prerequisite or condition that was not met, reported as observable state (e.g., variable values, file existence, connection status) — not just a generic label (e.g., "prerequisite missing").

Error context MUST be reported using a fail-safe output mechanism so that a display failure in the context output does not suppress the primary error message or abort the workflow.

### Error observability hygiene

Agents MUST comply with [Factory Spec §Secrets Handling] for log redaction policy.

The following agent-internal implementation requirements define how agents handle error surfaces:

Handled errors MUST NOT leak into diagnostic, telemetry, or debug output. Many platforms accumulate errors in a global surface that catch/rescue/except blocks do not automatically clear. If the project captures that surface for diagnostics, every error handler MUST either:

1. **Prevent the error** — validate preconditions before the call so the error never occurs (preferred).
2. **Suppress at source** — use the platform's mechanism to prevent the error from being recorded globally (e.g., `-ErrorAction Ignore` in PowerShell, `contextlib.suppress` in Python, `@` error suppression operator or custom error handlers in PHP).
3. **Clean up after catch** — explicitly remove the handled error from the global surface in the catch/rescue/except block.

The global error surface varies by language (e.g., `$global:Error` in PowerShell, `sys.last_value` or logging handlers in Python, global exception handlers in PHP). Agents MUST identify and clean the applicable surface for the project's language(s).

Bare catch blocks that silently swallow errors without applying one of these strategies are not permitted in new or modified code.

When available, use or create a wrapper that internalizes strategy 2 or 3, so the correct behavior is the default path rather than an opt-in step that can be forgotten.

Tests MUST assert that functions exercising error paths do not leave residual entries in the global error surface.

Objects that hold unmanaged resources (cryptographic contexts, file handles, network connections, database connections) MUST be disposed deterministically. Relying on garbage collection or finalizers is not permitted for security-sensitive resources.

### Resource disposal hygiene

Agents MUST comply with [Factory Spec §Security Model (Zero Trust)] rules 1–2 for fail-closed and security-by-design policy.

The following agent-internal implementation requirement defines how agents apply deterministic resource disposal:

When a resource is acquired, the code path that releases it MUST execute regardless of whether the operation succeeds or fails. Use the language's structured cleanup mechanism (e.g., `try/finally` with `.Dispose()` in PowerShell/.NET, `with` statements in Python, `try/finally` in PHP) rather than placing disposal after the operation in linear flow.

### Progress feedback for long-running workflows

This section has no direct Factory Spec counterpart. It is an agent-internal code quality standard for user-facing output produced by this project.

When a script, tool, or automation executes a sequence of time-consuming tasks that blocks the user from interacting:

- The user MUST see continuous progress feedback throughout execution.
- Progress MUST be reported at two levels: overall workflow completion (which phase is active out of the total) and per-phase granularity (which item within the current phase).
- The total number of phases MUST be known before execution begins and MUST NOT change mid-run.
- Progress indicators MUST be removed from the display immediately when their level of work completes; stale or frozen indicators are not permitted.
- Phases with no iterative work still report at the workflow level; the per-phase level is only shown when a phase iterates over multiple items.

### Operational scope and least-privilege enforcement

Agents MUST comply with [Factory Spec §Operational Constraints].

This project's operational scope — the set of external systems, resources, and operation types (read, write, delete) that the tool is permitted to perform — is declared in the project's README or equivalent project documentation. All components and integrations MUST operate within the declared operational scope and MUST NOT perform operations on external systems or resources beyond that scope.

The declared operational scope MUST be explicit and machine-verifiable (for example, documented as an allowlist of external system types and permitted operation types).

All connectors, agents, and automation MUST operate with the minimum privileges required by the declared operational scope, and MUST NOT hold credentials or roles that grant capabilities beyond that scope.

Implementations MUST be auditable to demonstrate that:

- No permissions beyond the declared operational scope are granted.
- No operations beyond the declared scope are possible or performed during normal operation or error conditions.

The following categories of artifacts are exempt from operational scope restrictions. Each exemption applies only to files written to the local filesystem by the tool's own process; it does not extend to writes targeting external systems, services, APIs, or remote storage:

- Backup files created by the tool on the local filesystem to enable rollback of its own operations.
- Log files and diagnostic output written by the tool to the local filesystem.
- Exported reports, summaries, or other output artifacts that the tool is designed to produce, written to the local filesystem.
- Temporary files created on the local filesystem during execution, provided they are cleaned up per §Resource disposal hygiene.

These exempt artifacts remain subject to all other requirements in this document, including §De-identification and metadata minimization, §Secret and credential handling, and §Zero Trust and security-by-design.

If no operational scope is declared in the project documentation, agents MUST default to read-only and MUST NOT perform write, update, or delete operations against any external system or resource.

### Backward compatibility

Agents MUST comply with [Factory Spec §Operational Constraints] rule 11 for the backward compatibility threshold.

### Version traceability

Agents MUST comply with [Factory Spec §Artifact Handling Requirements] for lineage traceability policy.

The following agent-internal implementation requirements define how agents embed version identifiers:

Every user-visible artifact produced by this project MUST include a version identifier derived from the Git commit that produced it.

- Source code MUST contain a placeholder (e.g., `<BUILD_VERSION>`) that CI replaces with the resolved version string before building or testing. For tagged builds, the resolved version is `<tag>+<short-SHA>` (e.g., `v1.2.0+f3a9c1e`). For untagged builds, the resolved version is the short commit SHA only.
- When running outside CI, the code MUST resolve the version at runtime using a fallback chain: pre-injected value → short `git rev-parse --short HEAD` → file hash → `"unknown"`. The runtime fallback uses the short SHA for readable display.
- The version MUST never be a hardcoded value that requires manual updates.
- Agents adding new output surfaces (CLI, API, reports, UI) MUST include the version identifier in at least one discoverable location.
- Every CI/CD workflow that builds, tests, installs, or packages this project MUST include an "Inject build version" step before any build, install, or test step. This step MUST:
  1. Locate the source file containing the `<BUILD_VERSION>` placeholder.
  2. Verify the placeholder exists (fail the build if absent).
  3. Resolve the version string: if the build is triggered by a tag, use `<tag>+<short-SHA>`; otherwise use the short commit SHA.
  4. Replace the placeholder with the resolved version string.
  5. Log the injected version.

  Each project MUST document the location of its placeholder file and the injection mechanism in its README or CLAUDE.md. Agents adding new workflows MUST replicate this logic for the project's language and runtime, or fail the review.
- Every CI/CD workflow that produces a release from a Git tag MUST include the exact commit SHA in the release body or release notes. This ensures bidirectional traceability: users can resolve a commit SHA to a release tag, and a release tag to the commit SHA that produced it.
- Release tags used as version identifiers MUST be protected against mutation after creation. Repositories MUST enable tag protection rules (or equivalent mechanism) for the release tag pattern. A CI/CD workflow MUST fail the build if it detects that the triggering tag has been previously used and re-pointed to a different commit.

### Documentation enforcement

Agents MUST comply with [Factory Spec §Operations Guide Requirements] for operations guide maintenance policy and [Factory Spec §Documentation Governance Requirements] for documentation governance policy.

The following agent-internal implementation requirements define how agents maintain documentation:

- A README file MUST exist and be kept up to date with every functional change.
- The README MUST be written for non-technical users:
  - No assumed prior knowledge or experience.
  - Step-by-step instructions that can be followed exactly.
  - Clear explanation of purpose, limitations, and expected outcomes.
- Any behavioral or breaking change MUST be reflected in the README.
- The README is a required artifact for every release and for every commit that changes behavior.
- Any change to sanitization, de-identification, or export behavior MUST be documented clearly in the README, including what data is removed, transformed, or preserved.
- When agents select a development language, runtime, or framework for a new tool, the choice MUST be justified in the README against the constraints in this file and the task requirements. The justification MUST address type safety, static analysis compliance, security properties, and target execution environment compatibility.

### Commit and PR title format

This section has no direct Factory Spec counterpart. It is an agent-internal standard enforced by CI.

All commit messages and pull request titles MUST use conventional commit format:

    type(scope): description

Valid types: `feat`, `fix`, `refactor`, `test`, `ci`, `docs`, `chore`.

- `type` is required. `(scope)` is optional but encouraged.
- The description MUST be lowercase-initial, imperative mood, and under 70 characters total.
- This format is enforced by CI on pull request titles (`.github/workflows/pr-title.yml`).

### Audit methodology

This section has no direct Factory Spec counterpart. It is an agent-internal standard for audit governance.

This project maintains an audit system in `audit/`. The following artifacts are governance-controlled:

- `audit/AUDIT-PROMPT.md` — Defines the audit procedure. Agents performing audits MUST follow this prompt exactly.
- `audit/AUDIT-LESSONS.md` — Append-only registry of methodology lessons. Each entry defines a defect class that a prior audit missed. Agents performing audits MUST apply every lesson as a mandatory additional check. Lessons MUST be repository-agnostic and development-language-agnostic so they remain valid when this audit system is adopted by other repositories.
- `audit/AUDIT-TEMPLATE.md` — Canonical report schema. All audit reports MUST use this template.

Audit reports produced under this methodology are compliance artifacts. The audit history table in README.md provides traceability across runs.

### Clarification protocol

This section has no direct Factory Spec counterpart. It is an agent-internal standard for clarification quality.

Before presenting a clarifying question to a human, agents MUST apply an internal gate:

1. **Confidence assessment**: Estimate confidence that the agent can proceed without the answer. If confidence is sufficient, the question MUST NOT be asked.
2. **Data source identification**: Identify which data from which source would raise confidence. If the source is the codebase or other agent-accessible resource, the agent MUST collect it and resolve the question without asking.
3. **Blocker check**: Only questions where the required data is genuinely unavailable to the agent (for example, a business decision, a preference, or access to an external system the agent cannot reach) MAY be presented.

Questions that pass the gate MUST:

- Use plain language accessible to a non-technical audience.
- Include the agent's recommended answer.
- Be unambiguous: a yes/no response MUST NOT match more than one option.

### Plan execution discipline

This section has no direct Factory Spec counterpart. It is an agent-internal standard for execution efficiency.

When a plan defines clear next steps with dependency ordering, agents MUST execute sequentially without requesting confirmation at each step. Agents MUST pause only when genuinely blocked: a missing prerequisite, an ambiguous requirement, or a destructive action requiring human consent (see [Factory Spec §Policy Authority and Immutability]).

### Independent analysis

This section has no direct Factory Spec counterpart. It is an agent-internal standard for analytical independence.

Agents MUST design their own solution based on codebase evidence before adopting recommendations from external sources (issue descriptions, change requests, peer review comments). The agent MUST compare its independent analysis against proposed scenarios and present its recommendation with rationale. Where the agent's analysis conflicts with an external recommendation, the agent MUST state both positions and the evidence supporting each.

---

## Role extension protocol

When a new agent role is added to the factory (see [Factory Spec §Organization Map]):

1. A new skill MUST be created in the factory's skill directory containing the role's behavioral constraints: role identity, boundaries (referencing [Factory Spec] role definition), input/output artifacts, pipeline steps, and exit signal.
2. A new row MUST be added to the issue register interaction permission table in the factory specification (see [Factory Spec §Issue Register Interaction]).
3. All §Common enforcement requirements in this file apply automatically to the new role without enumeration.
4. The new role MUST be explicitly non-authoritative unless the factory specification grants it authority (which, under the current single-authority model, it will not).
5. This file's §Absolute protections apply to all roles, including new ones, without exception.

---

## Compliance confirmation

Agents MUST comply with [Factory Spec §Policy Authority and Immutability] for policy authority.

Before creating or updating any commit in this repository, the agent MUST:

- Inspect the current diff.
- Verify that the proposed changes follow all rules in this file (§Common enforcement requirements) and the agent's applicable role-specific skill prompt.
- Explicitly state in its response whether the changes comply with these rules, or list any rules it cannot satisfy and stop before committing. This statement MUST be included in the transient conversation associated with the change (e.g., commit message, pull request description, or code review comment) and explicitly reference this document (`AGENTS.md`) by name.
