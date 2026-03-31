# Governance Change Proposal — Privacy Statement (Privacyverklaring)

**Status:** Work in progress — v2 trigger, not v1 requirement
**Proposed by:** Governance Proposer (automation agent)
**Requires:** Factory Owner review and approval (privacy statement is not a SubscriptionFactory.md governance artifact; changes are at Factory Owner discretion)
**Date:** 2026-03-31

---

## Evidence Basis

- The current privacy statement (v5.2) adequately covers BST v1. Specifically:
  - Website visitors (including BST users in v1) are covered by the "Websitebezoekers" category in §8.2.1.
  - GT&C acceptance logging is covered by the "Logs" row in §8.2.1 (user actions, IP addresses, timestamps; Art. 6(1)(f) AVG; 2-year retention).
  - Write-once log handling is established in §10.1.1 and §12.1.5.
- **No amendment is required for v1.**

- For v2 (multi-tenant SaaS), the BST introduces a new category of data subject not currently covered: **subscription application users with accounts**. These users will have: account credentials, usage history per session, per-user GT&C acceptance records with verified identity, and potentially saved comparisons or environment profiles. None of these are covered by the current "Websitebezoekers" category.

---

## Proposed Change — For v2 (deferred)

**Section:** `§8.2.1 Verwerkingsactiviteiten`
**Type:** Addition (deferred to v2)
**Trigger:** Before any subscription application introduces per-user accounts or stores user-generated content.

Add a new row to the processing activities table:

| Subcategorie betrokkene | Categorie gegevens | Specifieke gegevens | Verwerkingsactiviteit | Bewaartermijn | Verwerkingsdoel | Primaire rechtsgrond |
|---|---|---|---|---|---|---|
| **Gebruikers van abonnementsapplicaties** | Account- en gebruiksgegevens | Gebruikersnaam, gehashte inloggegevens, sessiemetadata, GT&C-acceptatierecords (versie, tijdstempel, IP-adres), opgeslagen vergelijkingen of profielen (indien van toepassing) | Authenticatie, autorisatie, sessiebeheer, vastleggen GT&C-acceptatie, opslaan gebruikersvoorkeuren | Account: duur abonnement + 7 jaar; Acceptatielogs: 2 jaar; Sessiegegevens: sessieduur | Uitvoering abonnementsovereenkomst; juridische zekerheid (bewijs GT&C-acceptatie) | Art. 6(1)(b) AVG — uitvoering overeenkomst |

**Additionally**, extend the "Logs" row to explicitly reference subscription application user actions alongside website visitor actions, for clarity.

---

## Rationale

The privacy statement is transparent and detailed. Adding subscription app users as an explicit category when v2 is introduced prevents a situation where these users are processed under "Websitebezoekers" — which is technically defensible but creates an implicit rather than explicit basis that may draw scrutiny from the Autoriteit Persoonsgegevens.

The per-user GT&C acceptance log in v2 processes a richer data set than the v1 IP-based log: it includes verified user identity. This strengthens forensic quality but also increases the personal data processing scope, warranting an explicit privacy statement entry.

---

## v1 Action Required

**None.** The current privacy statement (v5.2) is adequate for v1. This proposal is filed now so it is not forgotten when v2 development begins.

**Trigger condition for activation:** When the Author begins the v2 per-user authentication feature, the Governance Proposer MUST raise this proposal for Human Maintainer review before go-live of that feature.

---

## Impact Assessment — v2

- Adds one new subcategory of data subject to §8.2.1.
- No existing rows modified.
- No change to legal bases in use.
- Consistent with the privacy statement's existing layered approach and B2B focus.
- The Factory Owner MUST perform a Legitimate Interest Assessment (LIA) if any processing in the new row relies on Art. 6(1)(f) rather than Art. 6(1)(b).

---

*This is a v2 deferred proposal. File alongside the BST governance artefacts for traceability.*
*Not a SubscriptionFactory.md governance change — requires Factory Owner direct approval.*
