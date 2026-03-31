<!-- Audience: DevOps, maintainers -->
<!-- Scope: CI/CD, git hooks, version tagging, releases, incident response -->
<!-- Source: dissolved from technical-design-bst-v1.md (2026-03-31) -->

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

The acceptance event is logged in `index.php` when the user submits the GT&C agreement (from the website-layer popup). The log entry (see acceptance log schema in `docs/architecture.md`) is written server-side before the user is permitted to load the SPA. Log file is write-once/append-only where the hosting environment supports it.

## Operational decisions

| # | Decision | Notes |
|---|---|---|
| OTD-07 | APCu availability on shared hosting | Verify before implementation. File-based rate limiting is the fallback if APCu is unavailable. |
| OTD-08 | Acceptance log write-once implementation | Depends on hosting environment capabilities. Assess whether append-only file or database table is available. |

## Releases

<!-- Add release workflow documentation after first release. -->
