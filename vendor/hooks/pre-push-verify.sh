#!/bin/sh
# Pre-push verification hook.
# Catches --no-verify bypasses before wasting CI minutes.
# Implements defense-in-depth: re-runs critical checks that could
# have been skipped at commit time.
#
# Checks: secrets scanning and protected-file detection.
# This hook MAY be slower than 5 seconds (pre-push is not subject
# to the commit-time 5-second rule).

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
VENDOR_HOOKS="$REPO_ROOT/vendor/hooks"
FAILED=0

echo "pre-push: running verification checks..." >&2

# Re-run secrets detection on commits being pushed.
# Git pre-push hook receives refs on stdin: <local ref> <local sha> <remote ref> <remote sha>
# Read each ref line and scan changed files.
while IFS=' ' read -r LOCAL_REF LOCAL_SHA REMOTE_REF REMOTE_SHA; do
    # Skip branch deletions.
    if [ "$LOCAL_SHA" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi

    # Determine diff range.
    if [ "$REMOTE_SHA" = "0000000000000000000000000000000000000000" ]; then
        # New branch — compare against default branch.
        RANGE="$(git merge-base HEAD origin/main 2>/dev/null || echo HEAD~10)..${LOCAL_SHA}"
    else
        RANGE="${REMOTE_SHA}..${LOCAL_SHA}"
    fi

    CHANGED_FILES=$(git diff --name-only "$RANGE" 2>/dev/null || echo "")
    while IFS= read -r file; do
        [ -n "$file" ] && [ -f "$file" ] || continue
        if grep -lqE "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}" "$file" 2>/dev/null; then
            echo "BLOCKED: possible secret detected in $file (pre-push check)" >&2
            FAILED=1
        fi
    done <<EOF_FILES
$CHANGED_FILES
EOF_FILES
done

# Re-run protected-file detection.
if [ -x "$VENDOR_HOOKS/protected-file-check.sh" ]; then
    PRE_PUSH_HOOK=1 "$VENDOR_HOOKS/protected-file-check.sh"
fi

if [ "$FAILED" -ne 0 ]; then
    echo "" >&2
    echo "  Pre-push verification failed. Resolve the issues above." >&2
    echo "  This check exists to catch --no-verify bypasses." >&2
    exit 1
fi

echo "pre-push: all verification checks passed." >&2
exit 0
