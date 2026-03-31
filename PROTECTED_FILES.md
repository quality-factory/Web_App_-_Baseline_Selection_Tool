# Protected Files

This file is the machine-readable inventory of protected files in this repository.
The pre-commit hook (`hooks/pre-commit`) reads the table below to warn developers
before committing changes to protected files. CI enforcement (`.github/workflows/ci.yml`)
reads the same table when a CI workflow is configured for this repository.

## Adding protected files

Add a row to the table below. CI and the pre-commit hook parse the `Path / glob` column
automatically — no per-repo CI customization is needed.

## Inventory

| Path / glob | Protection level | Normative reference |
|-------------|-----------------|---------------------|
| `AGENTS.md` | absolute | AGENTS.md — "Absolute protections" |
| `PROTECTED_FILES.md` | governance-change-only | SubscriptionFactory §Protected Files |
