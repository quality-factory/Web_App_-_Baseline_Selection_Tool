#!/bin/sh
# Basic secrets detection hook.
# Implements SubscriptionFactory.md §Commit-Time Enforcement Requirements, req 4.
#
# Scans staged files for common secret patterns. This is a baseline scanner;
# repos MAY replace it with a more sophisticated tool (e.g., detect-secrets,
# gitleaks) by vendoring that tool into vendor/hooks/.
#
# Detected patterns: API keys, tokens, passwords, private keys, connection strings.

# Get list of staged files (only added/modified, skip deleted).
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [ -z "$STAGED" ]; then
    exit 0
fi

HITFILE=$(mktemp 2>/dev/null || echo "/tmp/detect-secrets-$$")
: > "$HITFILE"

echo "$STAGED" | while IFS= read -r file; do
    [ -n "$file" ] || continue
    # Skip binary files.
    if file "$file" 2>/dev/null | grep -q "binary"; then
        continue
    fi

    # Skip files that don't exist (deleted in working tree but staged).
    [ -f "$file" ] || continue

    # Pattern list: each pattern on its own grep -E call for clarity.
    # Private keys
    if grep -lnE "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----" "$file" > /dev/null 2>&1; then
        echo "BLOCKED: possible private key detected in $file" >&2
        echo "hit" >> "$HITFILE"
    fi

    # High-entropy tokens and API keys (common formats).
    if grep -lnE "(AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})" "$file" > /dev/null 2>&1; then
        echo "BLOCKED: possible API key or token detected in $file" >&2
        echo "hit" >> "$HITFILE"
    fi

    # Password assignments (common patterns).
    if grep -lnEi "(password|passwd|pwd|secret|token|api_key|apikey|access_key)\s*[:=]\s*['\"][^'\"]{8,}['\"]" "$file" > /dev/null 2>&1; then
        echo "WARNING: possible hardcoded credential in $file" >&2
        echo "hit" >> "$HITFILE"
    fi

    # Connection strings with embedded credentials.
    if grep -lnEi "(Server=|Data Source=|mongodb(\+srv)?://|postgres(ql)?://|mysql://)[^;]*Password=" "$file" > /dev/null 2>&1; then
        echo "BLOCKED: possible connection string with credentials in $file" >&2
        echo "hit" >> "$HITFILE"
    fi
done

FOUND=0
if [ -s "$HITFILE" ]; then
    FOUND=1
fi
rm -f "$HITFILE"

if [ "$FOUND" -ne 0 ]; then
    echo "" >&2
    echo "  Secrets scanning detected potential secrets in staged files." >&2
    echo "  Review the flagged files. If these are false positives," >&2
    echo "  document the exception and use: git commit --no-verify" >&2
    exit 1
fi

exit 0
