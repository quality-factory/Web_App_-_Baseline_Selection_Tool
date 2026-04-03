"""Ensure every text file ends with exactly one newline.

Uses binary I/O to avoid CRLF conversion on Windows — the root cause of the
infinite re-trigger loop when bash echo + core.autocrlf=true interact.

Exit codes:
    0  All files already ended with a newline (no changes).
    1  One or more files were fixed (pre-commit will abort the commit so
       the user can review and re-stage).
"""
import sys


def main() -> int:
    fixed = False
    for path in sys.argv[1:]:
        with open(path, "rb") as fh:
            content = fh.read()
        if not content:
            continue
        if not content.endswith(b"\n"):
            with open(path, "ab") as fh:
                fh.write(b"\n")
            print(f"Fixing {path}")
            fixed = True
    return 1 if fixed else 0


if __name__ == "__main__":
    sys.exit(main())
