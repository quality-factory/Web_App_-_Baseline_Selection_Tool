# Action Plan — Baseline Selection Tool (BST) v1

**Date:** 2026-03-31

---

## Artefact Index

| File | Description |
|---|---|
| `functional-design-bst-v1.md` | Functional Design — what the BST does |
| `technical-design-bst-v1.md` | Technical Design — how it is built and deployed |
| `governance-change-subscriptionfactory-gtc.md` | Governance change proposal for SubscriptionFactory.md |
| `governance-change-privacystatement-v2.md` | Governance change proposal for privacy statement (v2 trigger) |
| `webmaster-change-request-bst-wm-001.md` | Change request for the website webmaster |
| `sovereignty-classification-bst.md` | Sovereignty classification — INTERNAL, do not share externally |
| `action-plan-bst-v1.md` | This document |

---

## Phase 1 — Approve artefacts (you)

| # | Action | Artefact |
|---|---|---|
| 1 | Review and approve the FD | `functional-design-bst-v1.md` |
| 2 | Review and approve the TD | `technical-design-bst-v1.md` |
| 3 | Process the SubscriptionFactory.md governance change via the factory's governance-change workflow | `governance-change-subscriptionfactory-gtc.md` |

---

## Phase 2 — Webmaster (parallel with Phase 1)

| # | Action | Artefact | Depends on |
|---|---|---|---|
| 4 | Send CR to webmaster | `webmaster-change-request-bst-wm-001.md` | — |
| 5 | Supply Basic Auth credential to webmaster via secure channel | — | Step 4 |
| 6 | Webmaster implements Change 1a (domain restriction on `/my/`), Change 1b (Basic Auth), and Change 4 (X-Frame-Options) | — | Step 5 |
| 7 | Webmaster implements Change 2 (footer links) | — | GT&C URL available (Phase 3) |
| 8 | Webmaster implements Change 3 (popup + acceptance log) | — | GT&C published (Phase 3) |

---

## Phase 3 — GT&C (parallel with Phases 1 and 2)

| # | Action | Depends on |
|---|---|---|
| 9 | Draft GT&C | — |
| 10 | Legal review — Dutch commercial law liability clause (Boek 6 BW) | Step 9 |
| 11 | Publish GT&C at stable URL | Step 10 |

---

## Phase 4 — Build the BST

| # | Action | Depends on |
|---|---|---|
| 12 | Run Clarifier — produce requirements artifact | Steps 1 and 2 |
| 13 | Author Phase 1 spec — Human Maintainer approves before implementation begins | Step 12 |
| 14 | Author Phase 2 — implementation | Step 13 |
| 15 | Validator sign-off | Step 14 |
| 16 | Merge and deploy to `qualityfactory.com/my/bst/` | Step 15 + Step 6 |

---

## Phase 5 — Go live

| # | Action | Depends on |
|---|---|---|
| 17 | Verify deployment checklist (TD §11.3) | Step 16 |
| 18 | Webmaster removes Basic Auth (Change 1b) | Steps 8 and 11 |
| 19 | BST is publicly accessible | Step 18 |

---

## Phase 6 — First use

| # | Action | Depends on |
|---|---|---|
| 20 | Use the BST to re-evaluate and select the factory's Ubuntu 24.04 baseline | Step 19 |
| 21 | Update `laptop-initiation-guide.md` with the selected and justified baseline | Step 20 |

---

## Deferred — no action needed now

| Item | Trigger |
|---|---|
| Privacy statement update for subscription app users (`governance-change-privacystatement-v2.md`) | When v2 per-user authentication is built |
| Subdomain migration to `my.qualityfactory.com` | When business growth warrants it |
