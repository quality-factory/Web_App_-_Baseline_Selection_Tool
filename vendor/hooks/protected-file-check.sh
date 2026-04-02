#!/bin/sh
# Protected-file change detection hook.
# Implements SubscriptionFactory.md §Commit-Time Enforcement Requirements, req 5.
#
# Reads PROTECTED_FILES.md and warns when protected files are staged.
# Warning-only at pre-commit stage; CI is the blocking gate.
# Re-used at pre-push stage to catch --no-verify bypasses.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
PROTECTED_FILE="$REPO_ROOT/PROTECTED_FILES.md"

if [ ! -f "$PROTECTED_FILE" ]; then
    exit 0
fi

# Parse protected paths from the table (lines matching '| `<path>` |').
PROTECTED_PATHS=$(sed -n 's/^| `\([^`]*\)` |.*/\1/p' "$PROTECTED_FILE" 2>/dev/null || true)

if [ -z "$PROTECTED_PATHS" ]; then
    exit 0
fi

# Determine which files to check based on hook stage.
# pre-commit: staged files; pre-push: commits not yet on remote.
if [ -n "$PRE_PUSH_HOOK" ]; then
    # Called from pre-push: check commits being pushed.
    CHANGED=$(git diff --name-only "origin/$(git rev-parse --abbrev-ref HEAD)..HEAD" 2>/dev/null || echo "")
else
    # Called from pre-commit: check staged files.
    CHANGED=$(git diff --cached --name-only 2>/dev/null || echo "")
fi

if [ -z "$CHANGED" ]; then
    exit 0
fi

HITS=""
TMPFILE=$(mktemp 2>/dev/null || echo "/tmp/protected-check-$$")
echo "$PROTECTED_PATHS" > "$TMPFILE"
while IFS= read -r ppath; do
    [ -z "$ppath" ] && continue
    if echo "$CHANGED" | grep -qF "$ppath"; then
        HITS="$HITS  - $ppath
"
    fi
done < "$TMPFILE"
rm -f "$TMPFILE"

if [ -n "$HITS" ]; then
    echo "WARNING: the following protected files are staged for commit:" >&2
    printf '%s' "$HITS" >&2
    echo "" >&2
    echo "  These files are governance-controlled. CI will block this change" >&2
    echo "  unless the branch is named governance-changes/*." >&2
    echo "  See PROTECTED_FILES.md for details." >&2
    echo "" >&2
fi

exit 0
