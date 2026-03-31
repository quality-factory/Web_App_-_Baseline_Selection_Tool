# Sovereignty Classification — Baseline Selection Tool (BST)

**Status:** Complete
**Classification:** INTERNAL — the Factory Owner does not publicly disclose service providers for security reasons. This document must not be shared externally.
**Factory alignment:** SubscriptionFactory.md v13.3.0 §Operational Constraints #5
**Date:** 2026-03-31

---

## Classification Taxonomy

Per §Operational Constraints item 5, each service is classified as:

- **(a) Replaceable** — a sovereignty-compliant alternative exists and can be adopted without factory redesign
- **(b) Tolerable with exit strategy** — no sovereign equivalent at comparable capability; documented exit strategy required
- **(c) No sovereignty risk** — fully open-source, locally installable, not subject to foreign-jurisdiction compelled access
- **(d) Blocking** — unmitigated sovereignty risk; MUST NOT be used

---

## BST Infrastructure Components

| Component | Provider | Country of incorporation | Classification | Exit strategy | Notes |
|---|---|---|---|---|---|
| Shared web hosting | Hosting.nl | Netherlands (NL) | **(a) Replaceable** | Migration to any Dutch or EU-hosted provider (e.g. TransIP, Antagonist, Hostnet, Antagonist) requires file transfer and DNS change only; no factory or application redesign required | Dutch incorporation; subject to Dutch/EU law; no US parent entity; no CLOUD Act exposure; supervised by Autoriteit Persoonsgegevens; GDPR compliance by jurisdiction |
| GitHub (source control) | Microsoft | USA | **(b) Tolerable with exit strategy** | Git is distributed; complete local copy on factory laptop at all times; migration to any Git-compatible host (GitLab, Forgejo, Gitea, Codeberg) requires no factory redesign; CI workflow definitions are portable YAML requiring syntax translation only | US CLOUD Act applies to Microsoft; EU data residency available but does not fully mitigate; accepted on same basis as factory's existing GitHub usage |
| GitHub Actions (CI) | Microsoft | USA | **(b) Tolerable with exit strategy** | Workflow definitions portable to GitLab CI, Forgejo Actions, Woodpecker CI, or equivalent; no architectural change required | Must review sovereignty classification on any platform migration initiative per TD §11.1 |
| Alpine.js (frontend) | Community (OSS) | N/A | **(c) No sovereignty risk** | MIT licence; bundled locally; no CDN dependency; no runtime external calls | |
| Python (curation pipeline) | PSF | USA (PSF incorporated) | **(c) No sovereignty risk** | Open-source; locally installed; no external runtime dependency | |

---

## Sovereignty Assessment — Hosting.nl

**Jurisdiction:** Netherlands. EU member state. Subject to GDPR (Regulation 2016/679), supervised by the Autoriteit Persoonsgegevens (AP). Dutch civil and commercial law applies.

**Compelled access risk:** Low. No US CLOUD Act exposure. No known US parent company, US ownership, or US-jurisdiction infrastructure dependency. Dutch law does not require hosting providers to grant foreign government access without Dutch judicial process.

**Data residency:** Netherlands. The GT&C acceptance log (IP addresses, timestamps — personal data per privacy statement §8.2.1) is stored on Dutch infrastructure. This is the most favourable possible residency outcome under the factory's sovereignty posture.

**Conclusion:** Hosting.nl satisfies the factory's sovereignty requirements. Classification (a) is applied because equivalent Dutch and EU-hosted alternatives exist, not because Hosting.nl is deficient. No exit strategy documentation is required for class (a).

**Future subdomain migration:** The BST is currently deployed at `qualityfactory.com/my/bst/`. The `/my/` prefix mirrors the future subdomain name, making migration a clean promotion — the prefix is absorbed by the subdomain and tool paths remain unchanged (`qualityfactory.com/my/bst/` → `my.qualityfactory.com/bst/`). Future tools follow the same pattern. Hosting.nl has confirmed the required DNS records:
- A-record: `my.qualityfactory.com → 37.46.140.10`
- AAAA-record: `my.qualityfactory.com → 2a01:518:1:1041::10`

These records are filed here for future reference. Migration requires DNS record creation by Hosting.nl, a Plesk subdomain with dedicated document root, and footer/GT&C link URL updates. No application code changes are required.

---

## Cost Register Entry

| Service | Monthly cost | Purpose | Sovereignty class | Exit strategy required |
|---|---|---|---|---|
| Shared web hosting — Hosting.nl | Existing subscription (BST added to existing plan; no incremental cost anticipated) | Hosts BST web application, GT&C acceptance log, robots.txt | (a) Replaceable | No |
| GitHub (BST repository) | Included in existing $4 USD/month GitHub Team plan | Source control and CI for BST | (b) | Documented above |

*Cost Register must be updated if a dedicated BST hosting plan is created or if the BST hosting incurs incremental cost.*

---

## Technical Environment — Hosting.nl

The following technical characteristics of the hosting environment are derived from the server configuration file provided by the Factory Owner. They are recorded here because they affect BST deployment decisions.

**Environment:**
- Web server: LiteSpeed (Apache-compatible; `<IfModule LiteSpeed>` applies only to LiteSpeed-specific caching; standard Apache directives work normally)
- OS: Ubuntu 24.04.2+ LTS
- PHP: 8.4.5+ via CGI/FPM (not mod_php)
- Management: Plesk (customer-level access — no server-level configuration)
- Loaded modules: `mod_auth_basic`, `mod_expires`, `mod_headers`, `mod_mime`, `mod_rewrite`

**Key constraints and implications for BST:**

1. **PHP CGI/FPM:** `php_admin_flag` and `php_value` directives are ignored in `.htaccess`. PHP configuration must be done via Plesk or `.user.ini` / `php.ini`. This affects OTD-07 (APCu availability for rate limiting) — APCu availability must be verified through Plesk, not `.htaccess`.

2. **`.json` files are blocked globally:** The existing `.htaccess` contains a `FilesMatch` rule that denies access to all `.json` files sitewide. `data/baselines.json` is therefore already blocked from direct browser access regardless of the BST's own `.htaccess` rules. This is a beneficial side-effect for FR-P09 (knowledge base not bulk-downloadable), but it must be confirmed in deployment verification — the `api/baselines.php` PHP endpoint reads the file server-side (PHP file I/O is unaffected by `FilesMatch`) and serves content via HTTP response. **No additional `.htaccess` rule is needed to block direct JSON access; the global rule already covers it.**

3. **Security headers are set globally:** The existing `.htaccess` sets `X-Frame-Options "SAMEORIGIN"` globally. The BST TD specifies `X-Frame-Options "DENY"`. When both the global `.htaccess` and BST PHP code attempt to set the same header, LiteSpeed/Apache behaviour under `Header always set` may produce duplicate header values rather than an override. **The webmaster must add a path-specific `Header always set X-Frame-Options "DENY"` override for the BST path in the global `.htaccess` — or the BST PHP must use `header_remove()` before setting its own value.** This is a deployment-time conflict that must be resolved before go-live.

4. **HTTP Basic Auth is available:** `mod_auth_basic` is loaded. The webmaster CR (BST-WM-001 Change 1) can be implemented via `.htaccess` + `.htpasswd` on the BST path without Plesk server-level access. Standard implementation.

5. **WordPress multisite rewrite rules:** The existing `.htaccess` contains WordPress multisite rewrite rules that pass all requests to `index.php` unless the request targets an existing file or directory (`RewriteCond %{REQUEST_FILENAME} -f`). BST PHP files (`index.php`, `api/baselines.php`) are real files on the filesystem and will be served directly, bypassing the WordPress rewrite chain. **The BST does not need to be a WordPress plugin.** It operates as a standalone PHP application within the same hosting environment.

6. **Footer links and GT&C popup (webmaster CR):** The existing site is a WordPress multisite. Adding footer links and a popup via raw PHP or `.htaccess` would conflict with WordPress page rendering. The correct implementation is via the active WordPress theme or a lightweight WordPress plugin — not via `.htaccess` injection. **The webmaster CR (BST-WM-001) must be updated to reflect this: Changes 2 and 3 are WordPress theme/plugin implementations, not `.htaccess` implementations.** Change 1 (HTTP Basic Auth on the BST path) remains an `.htaccess` implementation and is unaffected.

---

## Validator Findings — Impact on Other Artefacts

The technical environment revealed by the hosting configuration requires the following corrections in existing artefacts:

| Finding | Affected artefact | Action required |
|---|---|---|
| X-Frame-Options conflict: global SAMEORIGIN vs BST DENY | TD §10.4, webmaster CR BST-WM-001 | Add path-specific header override for BST path to global .htaccess, or use PHP `header_remove()` before setting BST header |
| .json globally blocked — no additional BST rule needed | TD §10.1 repository structure, TD §11.2 deployment pipeline | Remove `.htaccess` deny rule for `/data/` from BST deployment instructions; global rule already covers it. Verify in deployment checklist. |
| PHP CGI/FPM — APCu config via Plesk not .htaccess | TD §10.5, OTD-07 | APCu availability must be verified and configured via Plesk; document in operations guide |
| WordPress multisite context — footer and popup via theme/plugin | Webmaster CR BST-WM-001 Changes 2 and 3 | Revise CR: Change 2 (footer links) and Change 3 (popup) are WordPress theme or plugin implementations, not .htaccess implementations |

---

*This document is INTERNAL. Do not share externally.*
*Record Hosting.nl classification in Cost Register.*
*Address Validator findings before Author Phase 1 spec begins.*
