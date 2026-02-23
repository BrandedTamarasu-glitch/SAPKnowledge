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
