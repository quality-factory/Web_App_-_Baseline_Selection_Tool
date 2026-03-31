# Change Request — Website Webmaster

**Reference:** BST-WM-001 rev.3
**Requestor:** Factory Owner / Human Maintainer
**Priority:** Required before BST go-live
**Date:** 2026-03-31
**Status:** **Superseded** — all changes generalized to cover all factory web apps under `/my/` and tracked in [Infra_-_Subscription_Factory#18](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/18). This file is retained as the original design rationale and technical detail reference.

---

## Context

The Baseline Selection Tool (BST) will be deployed as a standalone PHP application at `httpdocs/my/bst/` within the existing `httpdocs/` root (accessible at `qualityfactory.com/my/bst/`). The `/my/` prefix mirrors the future subdomain name `my.qualityfactory.com`, making eventual migration a clean promotion. Because the WordPress multisite maps multiple domains to the same web root, the `/my/` directory must explicitly restrict access to `qualityfactory.com` only. Placing the restriction at `/my/` rather than `/my/bst/` covers all future tools deployed under this prefix in one rule. Four changes are required before go-live.

---

## Change 1a — Domain Restriction on BST Path (Permanent)

**Scope:** `httpdocs/my/` directory `.htaccess` — covers the BST and all future tools deployed under this prefix.
**Duration:** Permanent — this rule stays in place indefinitely, including after the GT&C is published and Change 1b is removed.

**What to implement:**

Create a `.htaccess` file in `httpdocs/my/` (not in `httpdocs/my/bst/` — placing it one level up means all future tools under `/my/` are automatically covered by a single rule). This must be the **first rule block** in that file.

```apache
# Block access from all domains except qualityfactory.com
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{HTTP_HOST} !^(www\.)?qualityfactory\.com$ [NC]
    RewriteRule ^ - [F,L]
</IfModule>
```

**Why first:** If HTTP Basic Auth (Change 1b) is evaluated before this rule, browsers on other mapped domains would receive an auth prompt rather than a clean 403. The domain restriction must fire first.

**Verification:** After deployment, access `qualityfactory.com/my/bst/` from a browser using a different mapped domain. It must return 403 Forbidden. Access from `https://www.qualityfactory.com/my/bst/` must work normally.

---

## Change 1b — HTTP Basic Auth on BST Path (Temporary)

**Scope:** `httpdocs/my/bst/` directory `.htaccess` (appended after Change 1a, or in a separate `.htaccess` in the BST subdirectory)
**Duration:** Temporary — remove when the GT&C is published and Change 3 is live and confirmed working.

**What to implement:**

Append to the BST directory `.htaccess`, after the Change 1a block:

```apache
# Temporary access gate while GT&C is in preparation
AuthType Basic
AuthName "Restricted"
AuthUserFile /path/to/.htpasswd
Require valid-user
```

Create the `.htpasswd` file using `htpasswd -c /path/to/.htpasswd username`. Store the file **outside the web root**.

**Credential management:** The Factory Owner will supply the username and password via a secure channel — not by email. The credential must not be stored in any version-controlled file.

**Removal trigger:** Remove this block (and the `.htpasswd` file) when both of the following are confirmed:
1. The GT&C is published at a stable URL.
2. Change 3 (popup + server-side logging) is live and the acceptance log is receiving entries.

---

## Change 2 — GT&C and Privacy Statement Links in Website Footer

**Scope:** Sitewide WordPress footer — all pages on `qualityfactory.com`.
**Implementation:** WordPress theme or plugin (theme footer template, child theme, Customizer widget area, or lightweight custom plugin — whichever fits the active theme setup).
**Duration:** Permanent.

**What to implement:**

Add two links to the website footer:

1. **Algemene Voorwaarden** (Dutch) / **Terms and Conditions** (English) — linking to the GT&C URL.
2. **Privacyverklaring** (Dutch) / **Privacy Statement** (English) — linking to the privacy statement URL.

**Requirements:**
- Both URLs stored as configurable values (e.g. WordPress Customizer option or plugin setting) — not hardcoded — so they can be updated without a code change when documents change.
- Links visible on all pages without scrolling.
- Standard navigation — no `target="_blank"`.
- If a privacy statement link already exists in the footer, verify it and add the GT&C link alongside it.

**Factory Owner will supply:** GT&C URL (once published) and privacy statement URL.

---

## Change 3 — GT&C Agreement Popup with Server-Side Logging

**Scope:** `qualityfactory.com` only, or targeted to the BST path — Factory Owner to confirm before implementation.
**Implementation:** WordPress theme function or custom plugin with server-side logging (see §3c below).
**Duration:** Permanent (popup may evolve; logging remains).
**Priority:** Required before removing Change 1b.

### 3a — Popup display

- **Trigger:** On first visit, or after cookie expiry (see §3b).
- **Content:** *"To use this tool, you must agree to our [General Terms and Conditions]. Do you agree?"* — the bracketed phrase is a link to the GT&C URL (Change 2).
- **Actions:**
  - **Yes / Agree:** Sets cookie (§3b), triggers server-side log entry (§3c), grants access.
  - **No / Decline:** Shows *"Access requires agreement to our Terms and Conditions."* No cookie set; no log entry written.
- **Blocking:** The popup must prevent interaction with page content until the user chooses. A semi-transparent overlay is sufficient.

### 3b — Cookie

| Property | Value |
|---|---|
| Name | `gtc_accepted` (or equivalent) |
| Value | GT&C version identifier (e.g. `v1.0`) |
| Expiry | 30 days from acceptance |
| Scope | Domain root |

When the GT&C version identifier changes, cookies containing the old version value are treated as not accepted and the popup re-appears. This is implemented by comparing the cookie value to the current configured version identifier.

### 3c — Server-side acceptance logging

**This is a legal requirement** (proof of GT&C acceptance per the Factory Owner's privacy statement §8.2.1). Standard cookie consent plugins that only set cookies are insufficient — a server-side log entry must be written on each acceptance.

**Log entry fields:**

| Field | Value |
|---|---|
| Timestamp | Server-side ISO8601 datetime |
| IP address | Visitor's IP address |
| GT&C version | Current configured version identifier |
| Action | `accepted` |
| User agent hash | SHA-256 hash of HTTP User-Agent string (not the raw string) |

**Storage:** Dedicated append-only log file outside the web root, or a dedicated WordPress custom database table. Not publicly accessible. Retained for 2 years (privacy statement §8.2.1). Included in the existing backup schedule.

**Implementation note:** Most cookie consent plugins only set cookies and do not write server-side records. If no existing plugin supports this requirement, a small custom plugin or `functions.php` addition is the correct path.

### 3d — Configurable values (WordPress options)

Store the following as WordPress options — not hardcoded:
- GT&C URL
- GT&C version identifier (e.g. `v1.0`)
- Popup scope (sitewide or BST-path-only)

**Factory Owner will supply:** GT&C URL, initial version identifier, and preferred popup scope.

---

## Change 4 — X-Frame-Options Override for BST Path

**Superseded.** This change has been generalized to cover all factory web apps under `/my/` and is now tracked in [Infra_-_Subscription_Factory#18](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/18) (Change 4). The X-Frame-Options DENY header is set once in `httpdocs/my/.htaccess`, not per-app.

---

## Future Migration Note — Subdomain

When the factory grows to the point where a subdomain is warranted, the path structure maps cleanly — the `/my/` prefix is absorbed by the subdomain and all tool paths remain unchanged:

- Current: `qualityfactory.com/my/bst/` → After migration: `my.qualityfactory.com/bst/`
- Future tools follow the same pattern: `qualityfactory.com/my/[tool]/` → `my.qualityfactory.com/[tool]/`

Hosting.nl has confirmed the required DNS records:

- **A-record:** `my.qualityfactory.com → 37.46.140.10`
- **AAAA-record:** `my.qualityfactory.com → 2a01:518:1:1041::10`

Migration requires DNS record creation by Hosting.nl, a Plesk subdomain with dedicated document root, and updating footer/GT&C link URLs. No application code changes are required. Changes 1a and 4 become unnecessary in the subdomain architecture since the subdomain has its own isolated document root.

---

## Summary

| # | Change | Layer | When needed | Duration |
|---|---|---|---|---|
| 1a | Domain restriction on `httpdocs/my/` — blocks all mapped domains except qualityfactory.com | `httpdocs/my/.htaccess` | Immediately | Permanent |
| 1b | HTTP Basic Auth on `httpdocs/my/bst/` | `httpdocs/my/bst/.htaccess` | Immediately | Temporary — remove when GT&C + popup are live |
| 2 | GT&C + privacy statement links in footer | WordPress theme/plugin | Before BST go-live | Permanent |
| 3 | GT&C agree popup with server-side logging | WordPress theme/plugin | Before removing 1b | Permanent |
| 4 | ~~X-Frame-Options DENY override for BST path~~ | — | — | **Superseded** by [Infra_-_Subscription_Factory#18](https://github.com/quality-factory/Infra_-_Subscription_Factory/issues/18) Change 4 (general `/my/` rule) |

---

## Information Factory Owner Will Supply

- HTTP Basic Auth credential via secure channel — not email (Change 1b)
- GT&C URL once published (Changes 2, 3)
- Privacy statement URL if not already in footer (Change 2)
- GT&C version identifier string e.g. `v1.0` (Change 3)
- Preferred popup scope: sitewide or `/my/` path only (Change 3)

---

*Please confirm receipt and expected implementation timeline.*
*For questions: contact the Factory Owner via the usual channel.*
