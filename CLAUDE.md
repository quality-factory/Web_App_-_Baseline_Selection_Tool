# CLAUDE.md

This file provides concise instructions to Claude Code when working in this repository.

## Mandatory pre-work

@AGENTS.md

## Build, lint, and test commands

This is a PHP + JavaScript web application with a Python curation pipeline.

### Presentation subsystem (PHP + Alpine.js)

- Deployed to shared hosting (LiteSpeed on Ubuntu 24.04, Plesk-managed) via Plesk webhook on `deploy` branch merge
- No local build step for the presentation layer
- Hosting environment reference: `Infra_-_Subscription_Factory/reference/htaccess`

### Curation pipeline (Python)

- Runs locally on the factory laptop
- No external service dependencies at runtime

## Project overview

**Baseline Selection Tool (BST)** is a web application that helps security practitioners systematically choose hardening baselines for their workstation environments. The tool delivers a curated knowledge base through a browser-based comparison and recommendation interface.

### Key design documents

- `docs/functional-design-v1.md` — What the system does (technology-agnostic)
- `docs/technical-design-v1.md` — How it is built and deployed
- `docs/sovereignty-classification.md` — INTERNAL; infrastructure sovereignty assessment
- `docs/governance-change-privacystatement-v2.md` — Deferred v2 privacy statement trigger
- Hosting infrastructure changes: [Infra_-_Subscription_Factory#18](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/18)
- `governance/governance-change-subscriptionfactory-gtc.md` — Applied GT&C governance change (SubscriptionFactory.md v13.4.0)
