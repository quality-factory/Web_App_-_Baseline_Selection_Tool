#!/bin/sh
# Prepare-commit-msg hook: pre-fill conventional commit template.
# Reduces agent re-commit cycles by providing the expected format.
#
# Only pre-fills if the message file is empty or contains the default
# git template. Does not overwrite user-provided messages.

MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Do not modify messages from merge, squash, or commit --amend.
case "$COMMIT_SOURCE" in
    merge|squash|commit) exit 0 ;;
esac

# Only pre-fill if the first line is empty or starts with a comment.
FIRST_LINE=$(head -n 1 "$MSG_FILE" 2>/dev/null || echo "")
case "$FIRST_LINE" in
    "#"*|"")
        # Pre-fill with conventional commit template.
        TMPFILE=$(mktemp 2>/dev/null || echo "/tmp/prepare-commit-$$")
        {
            echo "type(scope): description"
            echo ""
            echo "# Types: feat, fix, refactor, test, ci, docs, chore"
            echo "# Format: type(scope): lowercase imperative description"
            echo "# Example: feat(auth): add token refresh mechanism"
            echo "#"
            # Preserve existing comments (e.g., git status output).
            tail -n +2 "$MSG_FILE" 2>/dev/null || true
        } > "$TMPFILE"
        mv "$TMPFILE" "$MSG_FILE"
        ;;
esac

exit 0
