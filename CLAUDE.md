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
- `docs/architecture.md` — Design decisions, component design, data schemas
- `docs/operations.md` — Deployment pipeline, verification checklist, operational notes
- Hosting infrastructure: [Infra_-_Subscription_Factory#18](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/18)
- Privacy statement v2 trigger: [Infra_-_Subscription_Factory#19](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/19)
- GT&C governance change evidence: `Infra_-_Subscription_Factory/governance/governance-change-subscriptionfactory-gtc.md`
