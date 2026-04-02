#!/bin/sh
# Suppression directive detection hook.
# Implements SubscriptionFactory.md §Commit-Time Enforcement Requirements, req 10.
#
# Scans staged files for inline lint/type suppression directives.
# New suppressions MUST NOT be introduced; existing ones MUST be tracked.

# Get list of staged files (only added/modified).
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [ -z "$STAGED" ]; then
    exit 0
fi

# Get only the added lines (lines starting with +, excluding +++ header).
ADDED_LINES=$(git diff --cached --unified=0 --diff-filter=ACM 2>/dev/null \
    | grep '^+[^+]' \
    | grep -v '^+++' || true)

if [ -z "$ADDED_LINES" ]; then
    exit 0
fi

FOUND=0

# Python suppressions.
if echo "$ADDED_LINES" | grep -qE '# (noqa|type:\s*ignore|pylint:\s*disable|pragma:\s*no\s*cover)'; then
    echo "WARNING: Python suppression directive detected in staged changes." >&2
    echo "$ADDED_LINES" | grep -nE '# (noqa|type:\s*ignore|pylint:\s*disable|pragma:\s*no\s*cover)' >&2
    FOUND=1
fi

# TypeScript/JavaScript suppressions.
if echo "$ADDED_LINES" | grep -qE '(//\s*@ts-ignore|//\s*@ts-expect-error|//\s*eslint-disable|/\*\s*eslint-disable)'; then
    echo "WARNING: TypeScript/JavaScript suppression directive detected." >&2
    FOUND=1
fi

# PHP suppressions.
if echo "$ADDED_LINES" | grep -qE '(@phpstan-ignore|@psalm-suppress|@codingStandardsIgnore)'; then
    echo "WARNING: PHP suppression directive detected." >&2
    FOUND=1
fi

# PowerShell suppressions.
if echo "$ADDED_LINES" | grep -qE '\[Diagnostics\.CodeAnalysis\.SuppressMessage'; then
    echo "WARNING: PowerShell suppression directive detected." >&2
    FOUND=1
fi

if [ "$FOUND" -ne 0 ]; then
    echo "" >&2
    echo "  New suppression directives are not permitted (commit-time req 10)." >&2
    echo "  Fix the root cause instead of suppressing the warning." >&2
    echo "  If suppression is unavoidable, get HM approval and document in PR." >&2
    # Informational level: warn but do not block.
    # Change to 'exit 1' when promoted to hard gate.
fi

exit 0
