# Governance Change Proposal — SubscriptionFactory.md

**Status:** Applied — SubscriptionFactory.md v13.4.0
**Branch:** `governance-changes/gtc-information-asset`
**Proposed by:** Governance Proposer (automation agent)
**Requires:** Author → Validator → Human Maintainer approval
**Date:** 2026-03-31

---

## Evidence Basis

- BST Functional Design §12 identifies a pre-go-live gate requiring the GT&C to be published before the BST becomes publicly accessible.
- BST Functional Design §10.6 requires the GT&C to be reviewed for Dutch commercial law compliance before go-live.
- BST Functional Design FR-P15 requires a configurable footer link to the GT&C on every page of every subscription application.
- The GT&C is currently absent from the factory's Information Asset Inventory, meaning it has no formal status, no version tracking, and no go-live gate mechanism.

---

## Proposed Changes

### Change 1 — Add GT&C to Information Asset Inventory

**Section:** `§Information Asset Inventory`
**Type:** Addition

Add the following row to the Information Asset Inventory table:

| Information Asset | Category | Status at Go-Live | Purpose |
|---|---|---|---|
| Factory General Terms and Conditions (GT&C) | Governance artifact | **Work in progress — go-live gate** (see §Platform Security Baseline Requirements note below) | Contractual framework governing all subscription relationships; liability limitation; IP protection; acceptable use policy. Must be published at a stable URL and linked in all subscription application footers (FR-P15 of each application FD) before any application is made publicly accessible. |

### Change 2 — Add GT&C Go-Live Gate Policy

**Section:** `§Product Domain` (after §Experience Level Agreement)
**Type:** Addition

Add the following new policy section:

#### General Terms and Conditions (GT&C)

1. The Factory Owner MUST maintain a current, published version of the General Terms and Conditions (GT&C) governing all subscription relationships.

2. No factory-produced subscription application MAY be made publicly accessible until:
   (a) The GT&C is published at a stable, publicly accessible URL.
   (b) The GT&C liability limitation clause has been reviewed for compliance with Dutch commercial law (Boek 6 BW) by a person with sufficient legal literacy.
   (c) Every application UI includes a footer link to the live GT&C per FR-P15 of that application's functional design.
   (d) A GT&C acceptance mechanism is in place (at minimum: a website-layer agreement popup logging acceptance events server-side per the Factory Owner's privacy statement §8.2.1).

3. The GT&C MUST be versioned. A version identifier MUST be included in the document and referenced in all acceptance log entries.

4. Material changes to the GT&C MUST be communicated to active subscribers in accordance with the Factory Owner's privacy statement §3 (change communication policy), adapted for contractual rather than privacy changes.

5. The GT&C is a protected factory asset. Changes to the GT&C MUST be treated as governance changes requiring Human Maintainer approval.

### Change 3 — Add GT&C to Traceability Matrix

**Section:** `§Traceability Matrix`
**Type:** Addition

Add the following row:

| Policy | Authority Source | Governing Domain(s) | Capabilities | Value Streams | Initiatives |
|---|---|---|---|---|---|
| GT&C (go-live gate and maintenance) | L0: Strategic Intent; L1: #1 no implicit trust | Product; Organization | Subscription Value Management; Governance and Decision Authority | Onboarding; Servicing; Offboarding | IM-001; IM-008 (and all future product initiatives) |

### Change 4 — Add GT&C to Enforcement Classification Register

**Section:** `§Appendix: Enforcement Classification Register`
**Type:** Addition

| Section | Req # | Enforcement Class | Mechanism |
|---|---|---|---|
| GT&C (go-live gate) | 2 | HAB | Human Maintainer verifies GT&C is published, reviewed, and linked before approving go-live of any application |
| GT&C (versioning) | 3 | HAB | Human Maintainer verifies version identifier is present in GT&C document |
| GT&C (material change communication) | 4 | HAB | Human Maintainer verifies change communication is sent to active subscribers |

---

## Rationale

The GT&C is the primary mechanism protecting the Factory Owner from liability in commercial relationships. Its absence from the Information Asset Inventory means it has no formal governance status — it could be published, modified, or neglected without any factory-level tracking. Adding it as a named asset with a go-live gate condition closes this gap consistently with how other critical artifacts (XLA, Zero Trust Checklist, Enforcement Classification Register) are treated.

The go-live gate in Change 2 mirrors the pattern established in `laptop-initiation-guide.md` §Factory-readiness blockers, applying the same "must be resolved before operations begin" model to the commercial rather than the technical domain.

---

## Impact Assessment

- No existing requirements are removed or weakened.
- No enforcement class changes.
- Adds one HAB requirement per application at go-live: Human Maintainer verification that GT&C is live and linked.
- Compatible with current SubscriptionFactory.md v13.3.0.

---

*This proposal feeds the standard Author → Validator → Human Maintainer workflow.*
*Branch: `governance-changes/gtc-information-asset`*
