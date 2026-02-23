# scripts/kb_reader.py
# KB file I/O and section extraction helpers for the SAP ECC 6 MCP server.
# Source patterns: scripts/validate.py (parse_frontmatter, KB_ROOT pattern)
# and KB structure inspection (heading formats confirmed across all modules).

import re
import yaml
from pathlib import Path

# KB root: scripts/ is one level below repo root
KB_ROOT = Path(__file__).resolve().parent.parent

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

VALID_MODULES = {"MM", "SD", "FI", "CO"}

# KB file path templates (format with module=lowercase module abbreviation)
TCODE_FILE = "modules/{module}/tcodes.md"
OVERVIEW_FILE = "modules/{module}/CLAUDE.md"
CONFIG_FILE = "modules/{module}/config-spro.md"
PROCESS_FILE = "modules/{module}/processes.md"
DISAMBIGUATION_FILE = ".claude/rules/sap-disambiguation.md"


def parse_frontmatter(filepath: Path) -> tuple[dict, str]:
    """Return (metadata_dict, body_str). Verbatim pattern from validate.py."""
    text = filepath.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    metadata = yaml.safe_load(match.group(1)) or {}
    return metadata, text[match.end():]


def normalize_module(raw: str) -> str | None:
    """
    Normalize user-supplied module name to 2-letter uppercase key.
    Accepts abbreviations (mm, FI), full names (Materials Management), any case.
    Returns None if the module is not in this KB.
    Per CONTEXT.md: normalize to MM/SD/FI/CO; reject PM, QM, etc.
    """
    upper = raw.strip().upper()
    if upper in VALID_MODULES:
        return upper
    name_map = {
        "MATERIALS MANAGEMENT": "MM",
        "SALES AND DISTRIBUTION": "SD",
        "SALES & DISTRIBUTION": "SD",
        "FINANCIAL ACCOUNTING": "FI",
        "FINANCE": "FI",
        "CONTROLLING": "CO",
        "COST ACCOUNTING": "CO",
    }
    return name_map.get(upper)


def get_file_body(template: str, module: str) -> tuple[str, str]:
    """
    Read a KB file using a path template and module abbreviation.
    Returns (body_text, relative_source_path).
    source_path is relative to KB_ROOT for use in Source: attribution lines.
    Per CONTEXT.md: module is already normalized (uppercase) before calling this.
    """
    rel_path = template.format(module=module.lower())
    full_path = KB_ROOT / rel_path
    _, body = parse_frontmatter(full_path)
    return body, rel_path


def extract_tcode_section(body: str, tcode: str) -> str | None:
    """
    Extract a single ### TCODE section from a tcodes.md body.
    Per RESEARCH.md: heading format is '### ME21N — Create Purchase Order'.
    Normalizes tcode to uppercase before matching (CONTEXT.md locked decision).
    Uses DOTALL + MULTILINE + lookahead to avoid bleeding into next section.
    MIGO appears multiple times — returns the first match (Goods Receipt), which
    is correct for the most common query (per RESEARCH.md MIGO special case note).
    """
    normalized = tcode.strip().upper()
    pattern = re.compile(
        r"(^### " + re.escape(normalized) + r"\b.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else None


def find_section_by_topic(body: str, topic: str) -> str | None:
    """
    Fuzzy section match for config-spro.md and processes.md.
    Case-insensitive substring match on ## or ### heading text.
    Returns the first matching section (heading through next same-level heading).
    Per CONTEXT.md: attempt partial/fuzzy match; return closest found, not hard fail.
    Per RESEARCH.md: config-spro.md uses '### Step N: Title'; processes.md uses '## N. Process'.
    """
    topic_lower = topic.lower()
    sections = re.split(r"(?=^#{2,3} )", body, flags=re.MULTILINE)
    for section in sections:
        m = re.match(r"^#{2,3} (.+)", section)
        if m and topic_lower in m.group(1).lower():
            return section.strip()
    return None


def extract_disambiguation_rows(body: str, topic: str) -> str | None:
    """
    Extract matching rows from the ECC 6 vs S/4HANA disambiguation table.
    Per CONTEXT.md: return matching table rows as-is (no prose synthesis).
    Per RESEARCH.md: table header is '| Area | ECC 6 (This KB) | S/4HANA (Not Covered) |'.
    Returns header row + separator + all matching data rows, or None if no match.
    """
    topic_lower = topic.lower()
    lines = body.splitlines()
    header, separator, matching = None, None, []
    for line in lines:
        if line.startswith("| Area "):
            header = line
        elif header and separator is None and line.startswith("|---"):
            separator = line
        elif header and line.startswith("|") and topic_lower in line.lower():
            matching.append(line)
    if not matching:
        return None
    return "\n".join([header, separator] + matching)


# Search scope allowlist: modules/, cross-module/, reference/ ONLY
# Order: MM -> SD -> FI -> CO -> cross-module -> reference (locked decision)
_SEARCH_DIRS = [
    ("mm", "modules/mm"),
    ("sd", "modules/sd"),
    ("fi", "modules/fi"),
    ("co", "modules/co"),
    ("cross-module", "cross-module"),
    ("reference", "reference"),
]

_HEADING_RE = re.compile(r"^#{1,3} ")


def _get_ordered_kb_files() -> list[Path]:
    """Return all .md files in module-priority order (allowlisted dirs only)."""
    files = []
    for _mod, rel_dir in _SEARCH_DIRS:
        d = KB_ROOT / rel_dir
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    return files


def _nearest_heading(lines: list[str], idx: int) -> str:
    """Walk backwards from idx to find nearest #{1,3} heading line."""
    for i in range(idx, -1, -1):
        if _HEADING_RE.match(lines[i]):
            return lines[i].strip()
    return ""


def _excerpt(lines: list[str], idx: int, context: int = 2) -> str:
    """Return up to context lines before + match line + context lines after."""
    start = max(0, idx - context)
    end = min(len(lines), idx + context + 1)
    return "\n".join(lines[start:end]).strip()


def _matches_query(line: str, tokens: list[str], phrase: bool) -> bool:
    """Case-insensitive match: phrase for <=2 tokens, AND logic for 3+."""
    lower = line.lower()
    if phrase:
        return " ".join(tokens) in lower
    return all(t in lower for t in tokens)


def search_kb(
    query: str, max_results: int = 10, max_per_file: int = 3
) -> tuple[list[dict], int]:
    """
    Search all KB files for query string.

    Returns:
        (results, total_match_count)
        results: list of {"source": rel_path, "heading": str, "excerpt": str}
        total_match_count: total lines matched (may be undercount if capped early)

    Scope: modules/, cross-module/, reference/ only — never .planning/, .claude/, scripts/.
    Ordering: MM -> SD -> FI -> CO -> cross-module -> reference (locked decision).
    Multi-word: phrase match for 1-2 tokens, AND logic for 3+ (Claude's discretion per CONTEXT.md).
    """
    tokens = query.strip().lower().split()
    if not tokens:
        return [], 0

    is_phrase = len(tokens) <= 2
    results: list[dict] = []
    total_count = 0

    for filepath in _get_ordered_kb_files():
        try:
            text = filepath.read_text(encoding="utf-8")
        except OSError:
            continue

        lines = text.splitlines()
        rel_path = str(filepath.relative_to(KB_ROOT))
        file_hits = 0

        for i, line in enumerate(lines):
            if _matches_query(line, tokens, is_phrase):
                total_count += 1
                if file_hits < max_per_file and len(results) < max_results:
                    results.append({
                        "source": rel_path,
                        "heading": _nearest_heading(lines, i),
                        "excerpt": _excerpt(lines, i),
                    })
                    file_hits += 1

        # Stop collecting after cap (simplified: stop scanning entirely)
        if len(results) >= max_results:
            break

    return results, total_count
