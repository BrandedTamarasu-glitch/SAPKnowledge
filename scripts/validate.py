#!/usr/bin/env python3
"""SAP ECC 6 Knowledge Base validation script.

Checks markdown content files for:
1. YAML frontmatter presence and required fields (CRITICAL)
2. Frontmatter value validation (CRITICAL)
3. S/4HANA contamination detection (CRITICAL/WARNING)
4. Token budget enforcement (WARNING)
5. Cross-reference integrity (WARNING)

Usage: python validate.py [--strict] [path...]
  --strict: Treat warnings as errors (exit 2)
  path...:  Files or directories to check (default: modules/, cross-module/, reference/)
Exit codes: 0 = pass, 1 = critical errors, 2 = warnings (with --strict)

Dependencies: PyYAML (system package python-yaml)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

# --- Constants ---

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS = [
    "module", "content_type", "ecc_version", "ehp_range",
    "confidence", "last_verified",
]

VALID_MODULES = {"fi", "mm", "sd", "co", "cross-module", "reference"}
VALID_CONTENT_TYPES = {
    "index", "tcodes", "config-spro", "processes", "master-data",
    "integration", "patterns", "e2e-process", "lookup-table",
    "account-determination", "decision-trees-and-troubleshooting",
}
VALID_CONFIDENCE = {"high", "medium", "low"}

# S/4HANA contamination patterns
S4_CRITICAL = [
    (r"\bUniversal Journal\b", "Universal Journal"),
    (r"\bACDOCA\b", "ACDOCA"),
    (r"\bMATDOC\b", "MATDOC"),
    (r"\bSimplified Data Model\b", "Simplified Data Model"),
]
S4_WARNING = [
    (r"\bBusiness Partner\b", "Business Partner"),
    (r"\bCDS Views?\b", "CDS Views"),
    (r"\bEmbedded Analytics\b", "Embedded Analytics"),
    (r"\bFiori Launchpad\b", "Fiori Launchpad"),
    (r"\bManage\s+\w+(?:\s+\w+)?\b", "Manage [X] (Fiori app name)"),
    (r"\bBP\s+transaction\b", "BP transaction"),
]

# Token budgets by content_type (characters // 4)
TOKEN_BUDGETS = {
    "index": 600,
    "tcodes": 5000,
    "config-spro": 5000,
    "processes": 4000,
    "master-data": 4000,
    "patterns": 4000,
    "integration": 5000,
    "e2e-process": 5000,
    "lookup-table": 5000,
    "account-determination": 5000,
    "decision-trees-and-troubleshooting": 5000,
}

RULES_TOKEN_CAP = 1500

DEFAULT_DIRS = ["modules", "cross-module", "reference"]

# --- Color output ---

USE_COLOR = sys.stdout.isatty()


def red(text):
    return f"\033[91m{text}\033[0m" if USE_COLOR else text


def yellow(text):
    return f"\033[93m{text}\033[0m" if USE_COLOR else text


def green(text):
    return f"\033[92m{text}\033[0m" if USE_COLOR else text


# --- Frontmatter parser ---

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_frontmatter(filepath):
    """Parse YAML frontmatter and body from a markdown file.

    Returns (metadata_dict, body_str). metadata is {} if no frontmatter found.
    """
    text = Path(filepath).read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw_yaml = match.group(1)
    body = text[match.end():]
    try:
        metadata = yaml.safe_load(raw_yaml)
    except yaml.YAMLError:
        metadata = None
    if not isinstance(metadata, dict):
        metadata = {}
    return metadata, body


# --- Helpers ---


def estimate_tokens(text):
    return len(text) // 4


def strip_fenced_blocks(content):
    """Remove fenced code blocks from content for scanning."""
    return re.sub(r"```[\s\S]*?```", "", content)


def strip_s4_callouts(content):
    """Remove intentional S/4HANA disambiguation callouts from scanning.

    Strips:
    - Blockquote lines containing S/4HANA (> ... S/4HANA ...)
    - The entire 'S/4HANA Differences' section at the end of files
      (standard disambiguation section per KB conventions)
    """
    # Strip blockquote callouts
    result = re.sub(
        r'^>.*?S/4HANA.*$', '', content, flags=re.MULTILINE
    )
    # Strip the S/4HANA Differences section (always at end of file)
    result = re.sub(
        r'^##\s+\d*\.?\s*S/4HANA Differences.*',
        '', result, flags=re.MULTILINE | re.DOTALL
    )
    return result


def relative_path(filepath):
    """Return path relative to repo root for display."""
    try:
        return str(Path(filepath).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(filepath)


# --- Check functions ---


def check_frontmatter_presence(filepath, metadata):
    """Check 1: Frontmatter presence and required fields."""
    errors = []
    if not metadata:
        errors.append(("CRITICAL", filepath, "No YAML frontmatter found"))
        return errors

    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append((
                "CRITICAL", filepath,
                f"Missing required frontmatter field: {field}"
            ))
    return errors


def check_frontmatter_values(filepath, metadata):
    """Check 2: Frontmatter value validation."""
    errors = []
    if not metadata:
        return errors

    module = metadata.get("module")
    if module and str(module) not in VALID_MODULES:
        errors.append((
            "CRITICAL", filepath,
            f"Invalid module: '{module}' (expected one of: {', '.join(sorted(VALID_MODULES))})"
        ))

    content_type = metadata.get("content_type")
    if content_type and str(content_type) not in VALID_CONTENT_TYPES:
        errors.append((
            "CRITICAL", filepath,
            f"Invalid content_type: '{content_type}' (expected one of: {', '.join(sorted(VALID_CONTENT_TYPES))})"
        ))

    ecc_version = metadata.get("ecc_version")
    if ecc_version and str(ecc_version) != "6.0":
        errors.append((
            "CRITICAL", filepath,
            f"Invalid ecc_version: '{ecc_version}' (expected '6.0')"
        ))

    ehp_range = metadata.get("ehp_range")
    if ehp_range and not re.match(r"^\d(-\d)?$", str(ehp_range)):
        errors.append((
            "CRITICAL", filepath,
            f"Invalid ehp_range: '{ehp_range}' (expected pattern like '0-8' or '6')"
        ))

    confidence = metadata.get("confidence")
    if confidence and str(confidence) not in VALID_CONFIDENCE:
        errors.append((
            "CRITICAL", filepath,
            f"Invalid confidence: '{confidence}' (expected one of: {', '.join(sorted(VALID_CONFIDENCE))})"
        ))

    last_verified = metadata.get("last_verified")
    if last_verified:
        date_str = str(last_verified)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append((
                "CRITICAL", filepath,
                f"Invalid last_verified: '{date_str}' (expected YYYY-MM-DD)"
            ))

    return errors


def check_s4_contamination(filepath, body):
    """Check 3: S/4HANA contamination detection."""
    errors = []
    if not body:
        return errors

    # Strip fenced code blocks and S/4 callouts before scanning
    scannable = strip_s4_callouts(strip_fenced_blocks(body))
    lines = scannable.split("\n")

    for line_num, line in enumerate(lines, 1):
        for pattern, name in S4_CRITICAL:
            if re.search(pattern, line, re.IGNORECASE):
                errors.append((
                    "CRITICAL", filepath,
                    f'S/4HANA contamination: "{name}" (line {line_num})'
                ))

        for pattern, name in S4_WARNING:
            if re.search(pattern, line, re.IGNORECASE):
                errors.append((
                    "WARNING", filepath,
                    f'Possible S/4HANA reference: "{name}" (line {line_num})'
                ))

    return errors


def check_token_budget(filepath, metadata, full_text):
    """Check 4: Token budget enforcement."""
    errors = []
    content_type = metadata.get("content_type") if metadata else None
    if not content_type:
        return errors

    tokens = estimate_tokens(full_text)
    cap = TOKEN_BUDGETS.get(str(content_type))

    if cap and tokens > cap:
        errors.append((
            "WARNING", filepath,
            f"Token budget exceeded: {tokens} tokens (cap: {cap})"
        ))

    return errors


def check_cross_references(filepath, body):
    """Check 5: Cross-reference integrity."""
    errors = []
    if not body:
        return errors

    file_dir = Path(filepath).resolve().parent
    refs = re.findall(r"@([\w./-]+\.md)", body)

    for ref in refs:
        ref_path = (file_dir / ref).resolve()
        if not ref_path.exists():
            errors.append((
                "WARNING", filepath,
                f"Broken reference: @{ref} (file not found)"
            ))

    return errors


def check_rules_token_budget():
    """Check combined token budget for .claude/rules/ files."""
    errors = []
    rules_dir = REPO_ROOT / ".claude" / "rules"
    if not rules_dir.exists():
        return errors

    total_tokens = 0
    for md_file in rules_dir.glob("*.md"):
        content = md_file.read_text()
        total_tokens += estimate_tokens(content)

    if total_tokens > RULES_TOKEN_CAP:
        errors.append((
            "WARNING", str(rules_dir),
            f"Combined rules token budget exceeded: {total_tokens} tokens (cap: {RULES_TOKEN_CAP})"
        ))

    return errors


# --- Main ---


def collect_files(paths):
    """Collect all .md files from given paths."""
    files = []
    for p in paths:
        path = REPO_ROOT / p if not Path(p).is_absolute() else Path(p)
        if path.is_file() and path.suffix == ".md":
            files.append(str(path.resolve()))
        elif path.is_dir():
            for md in sorted(path.rglob("*.md")):
                files.append(str(md.resolve()))
    return files


def validate_file(filepath):
    """Run all checks on a single file."""
    errors = []
    try:
        full_text = Path(filepath).read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(filepath)
    except Exception as e:
        errors.append(("CRITICAL", filepath, f"Failed to parse file: {e}"))
        return errors

    errors.extend(check_frontmatter_presence(filepath, metadata))
    errors.extend(check_frontmatter_values(filepath, metadata))
    errors.extend(check_s4_contamination(filepath, body))
    errors.extend(check_token_budget(filepath, metadata, full_text))
    errors.extend(check_cross_references(filepath, body))
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate SAP ECC 6 Knowledge Base content files"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as errors (exit 2)"
    )
    parser.add_argument(
        "paths", nargs="*", default=DEFAULT_DIRS,
        help="Files or directories to check"
    )
    args = parser.parse_args()

    files = collect_files(args.paths)
    if not files:
        print("No .md files found to validate.")
        return 0

    all_errors = []
    for f in files:
        all_errors.extend(validate_file(f))

    # Also check rules token budget
    all_errors.extend(check_rules_token_budget())

    critical_count = sum(1 for e in all_errors if e[0] == "CRITICAL")
    warning_count = sum(1 for e in all_errors if e[0] == "WARNING")
    passed_count = len(files) - len(set(e[1] for e in all_errors))

    for level, filepath, message in all_errors:
        display_path = relative_path(filepath)
        if level == "CRITICAL":
            print(f"{red('CRITICAL')}: {display_path} - {message}")
        else:
            print(f"{yellow('WARNING')}:  {display_path} - {message}")

    print()
    summary_parts = []
    if critical_count:
        summary_parts.append(red(f"{critical_count} critical"))
    if warning_count:
        summary_parts.append(yellow(f"{warning_count} warnings"))
    if passed_count > 0:
        summary_parts.append(green(f"{passed_count} passed"))
    print(f"Results: {', '.join(summary_parts)}")

    if critical_count > 0:
        return 1
    if warning_count > 0 and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
