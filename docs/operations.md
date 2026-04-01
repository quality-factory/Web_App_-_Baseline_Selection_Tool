<!-- Audience: DevOps, maintainers -->
<!-- Scope: CI/CD, git hooks, version tagging, releases -->
<!-- Factory alignment: SubscriptionFactory.md v13.5.0 -->

# Operations Guide

## Git hooks

Install hooks after cloning:

```sh
git config core.hooksPath hooks
```

## Branch model

| Branch | Purpose | Protection |
|---|---|---|
| `main` | Default; all development merges here | CI required; squash merge; no direct push |
| `deploy` | Plesk deploys from here | Human Maintainer merge only; no direct push |

## Deployment pipeline

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
```

Pre-condition: hosting infrastructure (Infra_-_Subscription_Factory#18) must be in place before first deployment (domain restriction + X-Frame-Options on `httpdocs/my/`).

## Deployment verification checklist

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

## GT&C acceptance logging

The acceptance event is logged in `index.php` when the user submits the GT&C agreement (from the website-layer popup). The log entry (see acceptance log schema in [`architecture.md`](architecture.md) §Acceptance log schema) is written server-side before the user is permitted to load the SPA. Log file is write-once/append-only where the hosting environment supports it.

### Acceptance log management

The acceptance log records personal data (IP address) governed by the Factory Owner's privacy statement. The following procedures apply regardless of the storage mechanism selected in OTD-07.

**Retention enforcement** — Log entries are retained for 2 years from the event timestamp per privacy statement §8.2.1. After the retention period, entries must be purged or marked as beyond use. Retention enforcement must be verified at least annually.

**Erasure requests** — Handled per privacy statement §12.1.5 using administrative "beyond use" marking. The log's write-once property means physical deletion may not be possible; the "beyond use" marking ensures the entry is excluded from any operational or audit access.

**Audit access** — Log data is infrastructure-level per FR-P16 and not accessible to the application's recommendation or comparison logic. Access to the log is restricted to the Human Maintainer for compliance verification purposes.

## Operational decisions

Operational decisions are tracked here. Architecture-scoped decisions are tracked in [`architecture.md`](architecture.md) §Open Technical Decisions.

| # | Decision | Notes |
|---|---|---|
| OTD-06 | APCu availability on shared hosting | Verify before implementation. File-based rate limiting is the fallback if APCu is unavailable. |
| OTD-07 | Acceptance log write-once implementation | Depends on hosting environment capabilities. Assess whether append-only file or database table is available. |

## Releases

Release workflow is based on the factory template (`Infra_-_Subscription_Factory/.github/workflows/release.yml`). The workflow has not yet been adopted in this repository.

Once adopted, the release pipeline operates as follows:

1. **Trigger**: manual dispatch on `main` or tag push (`v*`).
2. **Dependency audit**: verifies all pinned GitHub Actions are current.
3. **Version tag**: determines next SemVer tag from conventional commits (MAJOR on breaking changes, MINOR on `feat`, PATCH on `fix`/`refactor`/`docs`/etc.), pushes new tag.
4. **Release**: injects `BUILD_VERSION` placeholder, publishes GitHub release with build provenance, breaking changes documentation, and `AGENTS.md` as release asset.

Pre-conditions for adoption:

- `BUILD_VERSION` placeholder must exist in a source file (see AGENTS.md §Version traceability).
- Tag protection rules must be enabled for the `v*` pattern.
