#!/usr/bin/env python3
"""Local CI simulation script for pre-push verification.

Replicates CI hard-gate lint and test steps locally.
Stdlib only — no third-party dependencies. Requires Python 3.11+.

Architecture: TD-085-ARCH v1.1
Issue: #85 / #145
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# TD-085-COMP-02: CheckRunner data model
# ---------------------------------------------------------------------------

@dataclass
class CheckDefinition:
    """Definition of a single check to execute."""

    name: str
    ci_step: str
    command: list[str]
    tool_name: str
    language: str
    gate: str = "hard"  # "hard" or "informational"
    file_args: bool = False
    per_file: bool = False  # True = run command once per file (e.g. php -l)
    file_pattern: str = ""
    exclude_patterns: list[str] = field(default_factory=lambda: ["vendor", ".git"])
    fallback: CheckDefinition | None = None


@dataclass
class CheckResult:
    """Result of executing a single check."""

    name: str
    ci_step: str
    language: str
    status: str  # "pass", "fail", "skip"
    gate: str
    output: str = ""
    duration: float = 0.0


# ---------------------------------------------------------------------------
# TD-085-COMP-01: LanguageDetector
# ---------------------------------------------------------------------------

LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py"],
    "powershell": [".ps1", ".psm1"],
    "php": [".php"],
}

EXCLUDE_DIRS = {"vendor", ".git"}


def detect_languages(root: Path) -> set[str]:
    """Scan repository for language file-extension markers.

    Returns set of detected language keys. Short-circuits per language
    once the first marker is found (mirrors CI's head -1 pattern).
    """
    found: set[str] = set()
    needed = set(LANGUAGE_EXTENSIONS.keys())

    try:
        import os
        for dirpath, dirnames, filenames in os.walk(root):
            if not needed:
                break
            # Prune excluded directories in-place to prevent recursion (TD-085-TC-06)
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for filename in filenames:
                suffix = os.path.splitext(filename)[1].lower()
                for lang in list(needed):
                    if suffix in LANGUAGE_EXTENSIONS[lang]:
                        found.add(lang)
                        needed.discard(lang)
                        break
                if not needed:
                    break
    except PermissionError as e:
        # TD-085-FM-04: partial results better than no results
        print(f"Warning: permission denied during scan: {e}", file=sys.stderr)

    return found


# ---------------------------------------------------------------------------
# TD-085-COMP-02: CheckRunner
# ---------------------------------------------------------------------------

def _discover_files(root: Path, pattern: str, exclude: list[str]) -> list[str]:
    """Discover files matching a glob pattern, excluding directories.

    Uses os.walk with in-place pruning for efficiency in large repos.
    """
    import fnmatch
    import os

    files = []
    exclude_set = set(exclude)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_set]
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                files.append(os.path.join(dirpath, filename))
    return files


def _run_per_file(definition: CheckDefinition, files: list[str], root: Path) -> CheckResult:
    """Run a command once per file, aggregating results.

    Used for tools like `php -l` that only accept one file argument.
    """
    start = time.monotonic()
    failures = []
    for filepath in files:
        cmd = list(definition.command) + [filepath]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=root, timeout=300,
            )
            if result.returncode != 0:
                failures.append(f"{filepath}: {(result.stdout + result.stderr).strip()}")
        except subprocess.TimeoutExpired:
            failures.append(f"{filepath}: timed out")
    duration = time.monotonic() - start
    status = "fail" if failures else "pass"
    output = "\n".join(failures) if failures else ""
    return CheckResult(
        name=definition.name,
        ci_step=definition.ci_step,
        language=definition.language,
        status=status,
        gate=definition.gate,
        output=output,
        duration=duration,
    )


def run_check(definition: CheckDefinition, root: Path) -> CheckResult:
    """Execute a check and return the result."""
    # Check tool availability
    if not shutil.which(definition.tool_name):
        if definition.fallback:
            return run_check(definition.fallback, root)
        return CheckResult(
            name=definition.name,
            ci_step=definition.ci_step,
            language=definition.language,
            status="skip",
            gate=definition.gate,
            output=f"Tool '{definition.tool_name}' not found — skipped.",
        )

    # Build command with file arguments if needed
    command = list(definition.command)
    if definition.file_args:
        files = _discover_files(root, definition.file_pattern, definition.exclude_patterns)
        if not files:
            return CheckResult(
                name=definition.name,
                ci_step=definition.ci_step,
                language=definition.language,
                status="skip",
                gate=definition.gate,
                output="No matching files found.",
            )
        if definition.per_file:
            # Run command once per file (e.g. php -l only accepts one file)
            return _run_per_file(definition, files, root)
        command.extend(files)

    # Execute (TD-085-FM-03: timeout at 300s)
    start = time.monotonic()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=root,
            timeout=300,
        )
        duration = time.monotonic() - start
        status = "pass" if result.returncode == 0 else "fail"

        # Informational gate: always pass (TD-085-COMP-03 PHP phpstan)
        if definition.gate == "informational" and status == "fail":
            status = "pass"

        output = (result.stdout + result.stderr).strip()
        return CheckResult(
            name=definition.name,
            ci_step=definition.ci_step,
            language=definition.language,
            status=status,
            gate=definition.gate,
            output=output,
            duration=duration,
        )
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return CheckResult(
            name=definition.name,
            ci_step=definition.ci_step,
            language=definition.language,
            status="fail",
            gate=definition.gate,
            output=f"Timed out after {int(duration)}s.",
            duration=duration,
        )


# ---------------------------------------------------------------------------
# TD-085-COMP-03: CheckRegistry
# ---------------------------------------------------------------------------

def _has_mypy_config(root: Path) -> bool:
    """Check if pyproject.toml contains [tool.mypy] section (TC-07)."""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return False
    try:
        import tomllib
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        return "mypy" in data.get("tool", {})
    except Exception:
        return False


def get_checks(language: str, root: Path | None = None) -> list[CheckDefinition]:
    """Return ordered check definitions for a language."""
    if root is None:
        root = Path(".")

    if language == "python":
        # Mypy conditional (TC-07)
        if _has_mypy_config(root):
            mypy_cmd = ["python", "-m", "mypy"]
        else:
            mypy_cmd = ["python", "-m", "mypy", "--ignore-missing-imports"]

        # Fallbacks
        pylint_fallback = CheckDefinition(
            name="Python lint (pylint)",
            ci_step="Python lint",
            command=["pylint"],
            tool_name="pylint",
            language="python",
            file_args=True,
            file_pattern="*.py",
            exclude_patterns=["vendor", ".git", "tests"],
        )
        unittest_fallback = CheckDefinition(
            name="Python tests (unittest)",
            ci_step="Python test",
            command=["python", "-m", "unittest", "discover", "-s", "tests"],
            tool_name="python",
            language="python",
        )

        return [
            CheckDefinition(
                name="Python compile check",
                ci_step="Python compile check",
                command=["python", "-m", "py_compile"],
                tool_name="python",
                language="python",
                file_args=True,
                file_pattern="*.py",
            ),
            CheckDefinition(
                name="Python lint (ruff)",
                ci_step="Python lint",
                command=["ruff", "check", ".", "--exclude", "vendor", "--exclude", ".git"],
                tool_name="ruff",
                language="python",
                fallback=pylint_fallback,
            ),
            CheckDefinition(
                name="Python type check (mypy)",
                ci_step="Python lint",
                command=mypy_cmd,
                tool_name="mypy",
                language="python",
            ),
            CheckDefinition(
                name="Python tests (pytest)",
                ci_step="Python test",
                command=["pytest"],
                tool_name="pytest",
                language="python",
                fallback=unittest_fallback,
            ),
        ]

    elif language == "powershell":
        # PSScriptAnalyzer settings conditional
        settings_flag = []
        if (root / ".PSScriptAnalyzerSettings.psd1").exists():
            settings_flag = ["-Settings", ".PSScriptAnalyzerSettings.psd1"]

        return [
            CheckDefinition(
                name="PSScriptAnalyzer",
                ci_step="Run PSScriptAnalyzer",
                command=["pwsh", "-Command",
                         f"Invoke-ScriptAnalyzer -Path . -Recurse {' '.join(settings_flag)}".strip()],
                tool_name="pwsh",
                language="powershell",
            ),
            CheckDefinition(
                name="Pester tests",
                ci_step="Run Pester tests",
                command=["pwsh", "-Command", "Invoke-Pester -Output Detailed"],
                tool_name="pwsh",
                language="powershell",
            ),
        ]

    elif language == "php":
        # PHP test fallback
        phpunit_fallback = CheckDefinition(
            name="PHP tests (vendor)",
            ci_step="Run PHP tests",
            command=["vendor/bin/phpunit"],
            tool_name="vendor/bin/phpunit",
            language="php",
        )

        return [
            CheckDefinition(
                name="PHP syntax check",
                ci_step="PHP syntax check",
                command=["php", "-l"],
                tool_name="php",
                language="php",
                file_args=True,
                per_file=True,  # php -l only accepts one file at a time
                file_pattern="*.php",
            ),
            CheckDefinition(
                name="PHP static analysis (phpstan)",
                ci_step="PHP lint",
                command=["phpstan", "analyse"],
                tool_name="phpstan",
                language="php",
                gate="informational",
            ),
            CheckDefinition(
                name="PHP tests (phpunit)",
                ci_step="Run PHP tests",
                command=["phpunit"],
                tool_name="phpunit",
                language="php",
                fallback=phpunit_fallback,
            ),
        ]

    return []


# ---------------------------------------------------------------------------
# TD-085-COMP-04: ResultReporter
# ---------------------------------------------------------------------------

# ANSI colour codes (TD-085-DD-05)
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

_STATUS_COLOURS = {
    "pass": _GREEN,
    "fail": _RED,
    "skip": _YELLOW,
}


def report_results(results: list[CheckResult], use_color: bool) -> int:
    """Print formatted results. Return 0 if all hard-gate checks pass, else 1."""

    def _c(code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if use_color else text

    def _tag(status: str) -> str:
        colour = _STATUS_COLOURS.get(status, "")
        return _c(colour, f"[{status.upper()}]")

    # Group by language
    by_lang: dict[str, list[CheckResult]] = {}
    for r in results:
        by_lang.setdefault(r.language, []).append(r)

    hard_failures = 0
    total = 0
    passed = 0

    for lang in sorted(by_lang):
        print(f"\n{_c(_BOLD, f'=== {lang.title()} ===')}")
        for r in by_lang[lang]:
            total += 1
            duration_str = f" ({r.duration:.1f}s)" if r.duration > 0 else ""
            ci_map = f"  [CI: {r.ci_step}]"
            print(f"  {_tag(r.status)} {r.name}{duration_str}{ci_map}")

            if r.status == "pass":
                passed += 1
            elif r.status == "fail":
                if r.gate == "hard":
                    hard_failures += 1
                # Print output on failure
                if r.output:
                    for line in r.output.splitlines()[:20]:
                        print(f"         {line}")
                    if len(r.output.splitlines()) > 20:
                        print(f"         ... ({len(r.output.splitlines()) - 20} more lines)")
            elif r.status == "skip":
                if r.output:
                    print(f"         {r.output}")

    # Summary
    print()
    if hard_failures == 0:
        print(_c(_GREEN, f"{passed}/{total} checks passed. Local CI simulation: PASS"))
    else:
        print(_c(_RED, f"{passed}/{total} checks passed ({hard_failures} hard-gate failure(s)). Local CI simulation: FAIL"))

    return 1 if hard_failures > 0 else 0


# ---------------------------------------------------------------------------
# TD-085-COMP-05: main()
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Local CI simulation — replicate CI lint and test steps locally.",
    )
    parser.add_argument(
        "--language",
        choices=["python", "powershell", "php"],
        help="Run checks for a specific language only.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output.",
    )
    args = parser.parse_args()

    use_color = sys.stdout.isatty() and not args.no_color
    root = Path(".")

    # Detect languages
    languages = detect_languages(root)
    if args.language:
        languages = languages & {args.language}

    if not languages:
        print("No language-specific checks applicable.")
        sys.exit(0)

    # Run checks
    results: list[CheckResult] = []
    for lang in sorted(languages):
        checks = get_checks(lang, root)
        for check_def in checks:
            result = run_check(check_def, root)
            results.append(result)

    # Report and exit
    exit_code = report_results(results, use_color)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
