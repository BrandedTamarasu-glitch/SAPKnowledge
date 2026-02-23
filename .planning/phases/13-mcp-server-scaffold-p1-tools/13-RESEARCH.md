# Phase 13: MCP Server Scaffold + P1 Tools - Research

**Researched:** 2026-02-23
**Domain:** Python FastMCP server, markdown section extraction, MCP stdio protocol
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Tool response shape**
- Format: plain markdown text (not structured JSON) — Claude renders naturally in conversation
- Size ceiling: tight — just the matching section (~300-500 tokens); no full file dumps
- Source attribution: always include a `Source:` line with the KB file path (e.g., `Source: modules/fi/tcodes.md`)
- `compare_ecc_s4`: return matching table rows as-is from the existing disambiguation table (no prose synthesis)

**KB extraction strategy**
- Parse at query time (no pre-indexing on startup) — read relevant file, walk markdown headers, return matching section
- KB root location: resolved via path relative to the server script (scripts/ → repo root two levels up) — no env var required
- T-code matching: normalize input to uppercase, match case-insensitively (handles 'migo', 'Migo', 'MIGO')
- Module matching: normalize to uppercase 2-letter abbreviation (MM/SD/FI/CO) — accept full names, abbreviations, any case

**Install & venv approach**
- Venv location: project-local `.venv/` at repo root (gitignored)
- Setup: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`
- `.mcp.json` uses absolute path to interpreter (e.g., `/home/corye/Claude/SAPKnowledge/.venv/bin/python`)
- Package pinning: exact version in requirements.txt (`fastmcp==X.Y.Z`) — researcher identifies current stable version
- Server code location: `scripts/` directory alongside `validate.py`

**Tool routing & edge cases**
- Tool descriptions: strict routing rules — written as LLM invocation conditions ("Use this tool ONLY when...") to pass the 10-query routing test in MCP Inspector
- T-code not found: return clear "not found" message with scope note
- Module not in KB (e.g., PM, QM): return clear error ("Only MM/SD/FI/CO are covered in this KB")
- Topic not matched for get_config_path / get_process_flow: attempt partial/fuzzy match on section headings; return closest section found (not a hard fail)

### Claude's Discretion
- Exact fuzzy matching algorithm for topic parameter (substring, normalized, or scored)
- Internal helper structure (single file vs. module split in scripts/)
- Exact FastMCP version to pin (researcher identifies at implementation time)
- Whether to add a `__main__` entry point or rely on `fastmcp run` invocation

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MCP-01 | Developer can install the MCP server using standard Python tooling (venv + pip install) | requirements.txt pattern, fastmcp==3.0.2, PyYAML>=6.0 already present |
| MCP-02 | MCP server runs via stdio transport registered at repo root (.mcp.json) for Claude Code + Claude Desktop | FastMCP 3.x mcp.run() with no args defaults to stdio; .mcp.json absolute path pattern confirmed |
| MCP-03 | User can look up any SAP T-code and get description, module, menu path, and usage context | `### TCODE` heading pattern confirmed consistent across all 4 modules (MM/SD/FI/CO) |
| MCP-04 | User can get an overview of available KB content for a specific module | modules/{module}/CLAUDE.md has content_type=index; file index table and key concepts always present |
| MCP-05 | User can retrieve SPRO/IMG configuration path and steps for a given module + topic | modules/{module}/config-spro.md; `### Step N: Description` + `**IMG Path:**` heading pattern |
| MCP-06 | User can retrieve a step-by-step process flow for a named SAP business process | modules/{module}/processes.md; `## N. Process Name` + summary table pattern |
| MCP-07 | User can compare ECC 6 vs S/4HANA behavior for a given topic or feature | .claude/rules/sap-disambiguation.md; 17-row markdown table; exact row extraction |
| MCP-09 | Each tool description is written as an invocation condition for reliable LLM routing | Determined by implementation; research confirms this is a FastMCP tool docstring |
| MCP-10 | Tool responses use section-level extraction (not full file content) to stay within context limits | Section extraction patterns documented in Code Examples section below |
</phase_requirements>

---

## Summary

Phase 13 builds a Python FastMCP 3.x server in `scripts/` that exposes five read-only tools for querying the SAP ECC 6 KB. The server is a thin parse-at-query-time layer over the existing markdown KB — it reads files on demand, extracts the matching section by walking markdown headers, and returns plain text with a `Source:` attribution line.

FastMCP 3.0.2 (current stable as of 2026-02-23) is the correct pinned version. The framework's `@mcp.tool` decorator (without parentheses in v3) exposes Python functions as MCP tools. `mcp.run()` with no arguments defaults to stdio transport, which is what Claude Code and Claude Desktop expect.

The existing `scripts/validate.py` already contains the exact `parse_frontmatter()` function and `REPO_ROOT` path pattern needed. The KB has a consistent `### TCODE — Description` heading structure across all four tcodes.md files, and the disambiguation table in `.claude/rules/sap-disambiguation.md` has 17 data rows ready for direct row-level extraction.

**Primary recommendation:** Two-file layout (`scripts/mcp_server.py` + `scripts/kb_reader.py`) with `mcp_server.py` containing tool definitions and `kb_reader.py` containing all file I/O and extraction helpers. Pin `fastmcp==3.0.2` in `scripts/requirements.txt`.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastmcp | 3.0.2 | MCP server framework — exposes Python functions as MCP tools via stdio | Official Python MCP framework; `@mcp.tool` decorator, `mcp.run()` for stdio |
| PyYAML | >=6.0 | Parse YAML frontmatter from KB files | Already in requirements.txt; used by validate.py |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pathlib (stdlib) | stdlib | Path resolution for KB root, file discovery | Use instead of os.path throughout |
| re (stdlib) | stdlib | Frontmatter regex, section heading extraction | Already used in validate.py |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| fastmcp 3.0.2 | mcp (official Python SDK) | fastmcp is the higher-level framework; mcp SDK is lower-level and requires more boilerplate |
| fastmcp 3.0.2 | fastmcp 2.x | v3 is current stable; v2 decorator syntax differs (see pitfalls) |
| parse-at-query-time | pre-index on startup | Pre-indexing adds startup cost and memory; parse-at-query-time is simpler and KB is small enough |

**Installation:**
```bash
# Add to scripts/requirements.txt:
fastmcp==3.0.2
PyYAML>=6.0

# Install:
python -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

---

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── mcp_server.py    # FastMCP instance + @mcp.tool decorated functions (tool I/O only)
├── kb_reader.py     # All file I/O, section extraction, normalization helpers
├── requirements.txt # fastmcp==3.0.2 + PyYAML>=6.0
└── validate.py      # Existing validation script (unchanged)

.venv/               # Project-local venv at repo root (gitignored)
.mcp.json            # Absolute path to .venv/bin/python + scripts/mcp_server.py
```

### Pattern 1: FastMCP Server Setup (v3 syntax)

**What:** Declare FastMCP instance, apply `@mcp.tool` decorator to each tool function, call `mcp.run()` in `__main__` block.

**When to use:** This is the only correct pattern for FastMCP 3.x.

```python
# Source: https://gofastmcp.com/deployment/running-server.md
from fastmcp import FastMCP

mcp = FastMCP("SAP ECC 6 Knowledge Base")

@mcp.tool
def lookup_tcode(tcode: str) -> str:
    """Use this tool ONLY when the user asks about a specific SAP transaction code..."""
    ...

if __name__ == "__main__":
    mcp.run()
```

**Key v3 behaviors (verified):**
- `@mcp.tool` without parentheses is the v3 decorator syntax
- `mcp.run()` with no arguments defaults to stdio transport
- The decorated function's original behavior is preserved (v3 change from v2)
- Transport configuration (`host`, `port`) goes in `mcp.run()`, not in `FastMCP()` constructor

### Pattern 2: KB Root Resolution

**What:** Resolve the KB root from the server script location without env vars.

**When to use:** Always — this is the locked decision from CONTEXT.md.

```python
# Source: scripts/validate.py (exact pattern used by existing validate.py)
from pathlib import Path

# scripts/mcp_server.py is in scripts/, KB root is one level up
KB_ROOT = Path(__file__).resolve().parent.parent
```

### Pattern 3: Frontmatter Parsing

**What:** Parse YAML frontmatter from KB files using the exact pattern already in `validate.py`.

**When to use:** kb_reader.py should replicate or import this pattern.

```python
# Source: scripts/validate.py (verbatim)
import re
import yaml
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

def parse_frontmatter(filepath):
    text = Path(filepath).read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw_yaml = match.group(1)
    body = text[match.end():]
    metadata = yaml.safe_load(raw_yaml)
    return metadata or {}, body
```

### Pattern 4: T-code Section Extraction

**What:** Locate a T-code section in a tcodes.md file by matching the `### TCODE` heading and returning through the next `###` heading.

**When to use:** `lookup_tcode` tool.

```python
# Source: KB inspection — all 4 modules confirmed with this heading structure
import re

def extract_tcode_section(body: str, tcode: str) -> str | None:
    """Extract a single ### TCODE section from tcodes.md body."""
    normalized = tcode.upper()
    # Heading format: ### ME21N — Create Purchase Order
    pattern = re.compile(
        r"(^### " + re.escape(normalized) + r"\b.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else None
```

**KB heading structure (confirmed across all 4 tcodes.md files):**
```
### ME21N — Create Purchase Order
**Menu Path:** Logistics → ...
**Usage:** ...
**Gotcha:** ...
```

### Pattern 5: Module File Routing

**What:** Map tool parameters to the correct KB file for each tool.

**When to use:** All five tools need this routing table.

```python
# Source: KB structure inspection — all paths confirmed
VALID_MODULES = {"MM", "SD", "FI", "CO"}

MODULE_FILES = {
    "tcodes":    "modules/{module}/tcodes.md",
    "overview":  "modules/{module}/CLAUDE.md",
    "config":    "modules/{module}/config-spro.md",
    "processes": "modules/{module}/processes.md",
}
DISAMBIGUATION_FILE = ".claude/rules/sap-disambiguation.md"

def normalize_module(raw: str) -> str | None:
    """Normalize 'mm', 'materials management', 'MM' -> 'MM'. Returns None if unknown."""
    upper = raw.strip().upper()
    # Direct match
    if upper in VALID_MODULES:
        return upper
    # Full-name variants
    name_map = {
        "MATERIALS MANAGEMENT": "MM",
        "SALES AND DISTRIBUTION": "SD",
        "SALES & DISTRIBUTION": "SD",
        "FINANCIAL ACCOUNTING": "FI",
        "FINANCE": "FI",
        "CONTROLLING": "CO",
    }
    return name_map.get(upper)
```

### Pattern 6: Section Extraction for config-spro.md and processes.md

**What:** Find the best-matching section in config-spro.md or processes.md by fuzzy topic matching on headings.

**When to use:** `get_config_path` and `get_process_flow` tools.

```python
# Source: KB inspection — config-spro.md uses ### Step N: Topic, processes.md uses ## N. Topic
def find_section_by_topic(body: str, topic: str) -> str | None:
    """
    Find the best-matching section by case-insensitive substring match on headings.
    Returns the section text from the matching heading to the next same-level heading.
    """
    topic_lower = topic.lower()
    # Split into sections on ## or ### headings
    sections = re.split(r"(?=^#{2,3} )", body, flags=re.MULTILINE)
    best = None
    for section in sections:
        heading_match = re.match(r"^#{2,3} (.+)", section)
        if heading_match and topic_lower in heading_match.group(1).lower():
            best = section.strip()
            break  # First substring match wins
    return best
```

### Pattern 7: Disambiguation Table Row Extraction

**What:** Search the 17-row markdown table in `.claude/rules/sap-disambiguation.md` for rows matching the topic.

**When to use:** `compare_ecc_s4` tool.

```python
# Source: .claude/rules/sap-disambiguation.md inspection
# Table structure: | Area | ECC 6 (This KB) | S/4HANA (Not Covered) |
def extract_disambiguation_rows(body: str, topic: str) -> str | None:
    """Return matching table rows (header + matching data rows)."""
    topic_lower = topic.lower()
    lines = body.splitlines()
    header = None
    separator = None
    matching_rows = []
    for line in lines:
        if line.startswith("| Area "):
            header = line
        elif header and line.startswith("|---"):
            separator = line
        elif header and line.startswith("|") and topic_lower in line.lower():
            matching_rows.append(line)
    if not matching_rows:
        return None
    return "\n".join([header, separator] + matching_rows)
```

### Pattern 8: Tool Response Format

**What:** Every tool response ends with a `Source:` attribution line.

**When to use:** All five tools, always.

```python
# Source: CONTEXT.md locked decision
def format_response(content: str, source_path: str) -> str:
    """Append standard Source: attribution line to every tool response."""
    return f"{content}\n\nSource: {source_path}"
```

### Pattern 9: .mcp.json Registration

**What:** Register the server with Claude Code using absolute paths.

**When to use:** Install step for MCP-01 / MCP-02.

```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "/home/corye/Claude/SAPKnowledge/.venv/bin/python",
      "args": ["/home/corye/Claude/SAPKnowledge/scripts/mcp_server.py"]
    }
  }
}
```

Note: The absolute path to the Python interpreter MUST point to the `.venv/bin/python` at repo root, not the system Python. This is the locked decision from CONTEXT.md.

### Anti-Patterns to Avoid

- **Never write to stdout in a FastMCP server** — stdout is the MCP protocol wire. Use `sys.stderr` for any debug/logging output, never `print()`.
- **Never call `mcp.run()` at module level** — always guard with `if __name__ == "__main__":` block to prevent execution during import.
- **Never dump full file bodies** — every tool must extract the matching section only (MCP-10). Full tcodes.md files are 50-100KB+.
- **Do not use `@mcp.tool()` with parentheses** — FastMCP 3.x uses `@mcp.tool` (no parens). Parenthesized form has different semantics.
- **Do not put transport config in `FastMCP()` constructor** — v3 moved those params to `mcp.run()`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MCP protocol wire format | Custom JSON-RPC stdio handler | FastMCP 3.x `mcp.run()` | MCP protocol has complex framing, capability negotiation, error handling |
| YAML frontmatter parsing | Custom parser | `yaml.safe_load()` + FRONTMATTER_RE from validate.py | Edge cases in YAML (multi-line strings, special chars) |
| T-code section extraction | Full-file string search | `### TCODE\b` regex on extracted body | Heading structure is consistent; regex is sufficient and fast |

**Key insight:** The KB files are small (10-100KB each), consistently structured, and read-only. No caching, no indexing, no database needed. A direct read+regex approach is correct for this scale.

---

## Common Pitfalls

### Pitfall 1: stdout Contamination

**What goes wrong:** Any `print()` statement in the server (including import-time logging) writes to stdout and corrupts the MCP protocol stream. Claude Code shows connection errors or garbled responses.
**Why it happens:** The MCP stdio protocol uses stdout as the wire; Python's default print goes to stdout.
**How to avoid:** Use `sys.stderr` for all debug output. Never use `print()` in server code.
**Warning signs:** Claude Code shows "server disconnected" or "invalid JSON" immediately after connection.

### Pitfall 2: FastMCP v2 vs v3 Decorator Syntax

**What goes wrong:** Using `@mcp.tool()` (with parentheses) — in v3 this creates a decorator factory, not a direct decorator. The function is not registered as a tool.
**Why it happens:** v2 used `@mcp.tool()` (parens). v3 uses `@mcp.tool` (no parens).
**How to avoid:** Always use `@mcp.tool` without parentheses in FastMCP 3.x.
**Warning signs:** MCP Inspector shows zero tools after server starts.

### Pitfall 3: FastMCP Constructor vs run() Transport Config

**What goes wrong:** Passing `host=`, `port=`, `debug=` to `FastMCP()` constructor — these are silently ignored in v3. The server may not start on the intended port/transport.
**Why it happens:** v2 accepted transport config in the constructor; v3 moved it to `mcp.run()`.
**How to avoid:** All transport config goes in `mcp.run(transport="stdio")` or `mcp.run()`.
**Warning signs:** For stdio use, this pitfall is irrelevant since stdio is the default.

### Pitfall 4: T-code Heading Boundary Mismatch

**What goes wrong:** Section extraction regex captures too little (misses the content) or too much (bleeds into the next T-code's section).
**Why it happens:** The regex must match from `### TCODE` to the next `###` (or end of file), but lookahead must be exact.
**How to avoid:** Use `re.DOTALL | re.MULTILINE` and a lookahead `(?=^### |\Z)` with multiline mode. Test with MIGO (appears multiple times in tcodes.md as `### MIGO — Goods Receipt`, `### MIGO — Change Material Document`, etc.) — each is a separate section.
**Warning signs:** `lookup_tcode("MIGO")` returns more than one section or truncates the content.

### Pitfall 5: Module Name Normalization Edge Cases

**What goes wrong:** User passes "Materials Management" or "financial" and the tool returns "module not found" even though the KB has that module.
**Why it happens:** Simple uppercase comparison misses full-name variants.
**How to avoid:** Implement the `normalize_module()` function shown in Pattern 5 with a name_map for common variants.
**Warning signs:** `get_module_overview("materials management")` fails with module-not-found error.

### Pitfall 6: KB Root Wrong When Server Invoked from Different Working Directory

**What goes wrong:** KB files not found at startup; relative paths resolve incorrectly.
**Why it happens:** Using `os.getcwd()` instead of `Path(__file__).resolve()` — the cwd depends on how the server is launched, but `__file__` is always the script location.
**How to avoid:** Always use `KB_ROOT = Path(__file__).resolve().parent.parent` (from validate.py pattern). Never use relative paths or `os.getcwd()`.
**Warning signs:** `lookup_tcode()` returns file-not-found errors for valid T-codes.

---

## Code Examples

Verified patterns from existing codebase and FastMCP 3.x official docs:

### Complete KB Reader Skeleton

```python
# scripts/kb_reader.py
# Source: derived from scripts/validate.py patterns + KB structure inspection

import re
import yaml
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo root

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

VALID_MODULES = {"MM", "SD", "FI", "CO"}

# KB file mapping per tool type
TCODE_FILE = "modules/{module}/tcodes.md"
OVERVIEW_FILE = "modules/{module}/CLAUDE.md"
CONFIG_FILE = "modules/{module}/config-spro.md"
PROCESS_FILE = "modules/{module}/processes.md"
DISAMBIGUATION_FILE = ".claude/rules/sap-disambiguation.md"


def parse_frontmatter(filepath: Path) -> tuple[dict, str]:
    """Return (metadata_dict, body_str). Verbatim from validate.py."""
    text = filepath.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    metadata = yaml.safe_load(match.group(1)) or {}
    return metadata, text[match.end():]


def normalize_module(raw: str) -> str | None:
    """Normalize user-supplied module name to 2-letter uppercase key."""
    upper = raw.strip().upper()
    if upper in VALID_MODULES:
        return upper
    name_map = {
        "MATERIALS MANAGEMENT": "MM",
        "SALES AND DISTRIBUTION": "SD", "SALES & DISTRIBUTION": "SD",
        "FINANCIAL ACCOUNTING": "FI", "FINANCE": "FI",
        "CONTROLLING": "CO",
    }
    return name_map.get(upper)


def get_file_body(template: str, module: str) -> tuple[str, str]:
    """
    Read a KB file and return (body, source_path).
    source_path is relative to KB_ROOT for display in Source: line.
    """
    rel_path = template.format(module=module.lower())
    full_path = KB_ROOT / rel_path
    _, body = parse_frontmatter(full_path)
    return body, rel_path


def extract_tcode_section(body: str, tcode: str) -> str | None:
    """Extract single ### TCODE section from tcodes.md body."""
    pattern = re.compile(
        r"(^### " + re.escape(tcode.upper()) + r"\b.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else None


def find_section_by_topic(body: str, topic: str) -> str | None:
    """
    Fuzzy section match: case-insensitive substring on heading text.
    Returns first matching section from ## or ### heading to next same-level heading.
    """
    topic_lower = topic.lower()
    sections = re.split(r"(?=^#{2,3} )", body, flags=re.MULTILINE)
    for section in sections:
        m = re.match(r"^#{2,3} (.+)", section)
        if m and topic_lower in m.group(1).lower():
            return section.strip()
    return None


def extract_disambiguation_rows(body: str, topic: str) -> str | None:
    """Return header row + matching data rows from disambiguation table."""
    topic_lower = topic.lower()
    lines = body.splitlines()
    header, separator, matching = None, None, []
    for line in lines:
        if line.startswith("| Area "):
            header = line
        elif header and not separator and line.startswith("|---"):
            separator = line
        elif header and line.startswith("|") and topic_lower in line.lower():
            matching.append(line)
    if not matching:
        return None
    return "\n".join([header, separator] + matching)
```

### Complete MCP Server Skeleton

```python
# scripts/mcp_server.py
# Source: FastMCP 3.x docs (gofastmcp.com/deployment/running-server.md)

from fastmcp import FastMCP
import sys
from kb_reader import (
    normalize_module, get_file_body, TCODE_FILE, OVERVIEW_FILE,
    CONFIG_FILE, PROCESS_FILE, DISAMBIGUATION_FILE, KB_ROOT,
    extract_tcode_section, find_section_by_topic,
    extract_disambiguation_rows, parse_frontmatter,
)
from pathlib import Path

mcp = FastMCP("SAP ECC 6 Knowledge Base")


@mcp.tool
def lookup_tcode(tcode: str) -> str:
    """Use this tool ONLY when the user asks about a specific SAP transaction
    code by name (e.g., 'ME21N', 'MIGO', 'VF01'). Do not use for general
    questions about SAP processes or configuration."""
    normalized = tcode.strip().upper()
    for module in ["MM", "SD", "FI", "CO"]:
        body, source = get_file_body(TCODE_FILE, module)
        section = extract_tcode_section(body, normalized)
        if section:
            return f"{section}\n\nSource: {source}"
    return (
        f"T-code {normalized} not found in this KB. "
        f"This KB covers MM, SD, FI, and CO transactions only."
    )


@mcp.tool
def get_module_overview(module: str) -> str:
    """Use this tool ONLY when the user asks what topics or files are available
    for a specific SAP module (MM, SD, FI, or CO), or asks for a module
    orientation. Do not use for specific T-code or config lookups."""
    mod = normalize_module(module)
    if not mod:
        return f"Module '{module}' not found. Only MM, SD, FI, and CO are covered."
    body, source = get_file_body(OVERVIEW_FILE, mod)
    return f"{body.strip()}\n\nSource: {source}"


@mcp.tool
def get_config_path(module: str, topic: str) -> str:
    """Use this tool ONLY when the user asks for SPRO/IMG configuration steps,
    configuration paths, or how to configure a specific SAP setting. Requires
    both a module (MM/SD/FI/CO) and a topic (e.g., 'tolerance keys', 'order types')."""
    mod = normalize_module(module)
    if not mod:
        return f"Module '{module}' not found. Only MM, SD, FI, and CO are covered."
    body, source = get_file_body(CONFIG_FILE, mod)
    section = find_section_by_topic(body, topic)
    if section:
        return f"{section}\n\nSource: {source}"
    return (
        f"No exact match for topic '{topic}' in {mod} configuration. "
        f"Try rephrasing or check Source: {source} for the full configuration reference."
    )


@mcp.tool
def get_process_flow(module: str, process: str) -> str:
    """Use this tool ONLY when the user asks about a step-by-step SAP business
    process flow (e.g., 'procure-to-pay', 'order settlement', 'period-end close').
    Requires both a module and a process name."""
    mod = normalize_module(module)
    if not mod:
        return f"Module '{module}' not found. Only MM, SD, FI, and CO are covered."
    body, source = get_file_body(PROCESS_FILE, mod)
    section = find_section_by_topic(body, process)
    if section:
        return f"{section}\n\nSource: {source}"
    return (
        f"No exact match for process '{process}' in {mod}. "
        f"Try rephrasing or check Source: {source} for the full process reference."
    )


@mcp.tool
def compare_ecc_s4(topic: str) -> str:
    """Use this tool ONLY when the user explicitly asks about differences between
    SAP ECC 6 and S/4HANA for a specific topic. Do not use for general ECC 6
    questions — this tool only returns comparison data."""
    source = ".claude/rules/sap-disambiguation.md"
    _, body = parse_frontmatter(KB_ROOT / source)
    rows = extract_disambiguation_rows(body, topic)
    if rows:
        return f"{rows}\n\nSource: {source}"
    return (
        f"No comparison data found for topic '{topic}'. "
        f"Available topics include: vendor master, customer master, material documents, "
        f"material ledger, general ledger, cost elements, profit center accounting, MRP, "
        f"controlling area, and more. "
        f"Source: {source}"
    )


if __name__ == "__main__":
    mcp.run()
```

---

## KB Content Map (for Implementer Reference)

### T-code Heading Structure (all 4 modules — HIGH confidence)

All tcodes.md files use:
```
### TCODE — Short Description

**Menu Path:** ...
**Usage:** ...
**Gotcha:** ...   (optional — only when there is a notable pitfall)
```

Counts: MM ~67, SD ~75, FI ~65, CO ~63 T-codes.

### MIGO Special Case

MIGO appears three times in `modules/mm/tcodes.md`:
- `### MIGO — Goods Receipt (Create)` (action A01)
- `### MIGO — Change Material Document` (action A07)
- `### MIGO — Display Material Document` (action A03)

The first match for `### MIGO\b` will return the "Goods Receipt" section, which is correct for the most common MIGO query. This is acceptable behavior.

### config-spro.md Heading Structure

```
## N. Topic Name

### Step N: Specific Step Title
**T-code:** ...
**IMG Path:** ...
**Settings:** ...
Gotcha: ...
```

Fuzzy match on `### Step N: Title` by topic substring is the right approach.

### processes.md Heading Structure

```
## N. Process Name

### Narrative
...step-by-step text...

### Summary Table
| Step | Activity | T-code | Role | Output |
```

Fuzzy match on `## N. Process Name` by topic substring is the right approach.

### Disambiguation Table (`.claude/rules/sap-disambiguation.md`)

17 data rows. Header: `| Area | ECC 6 (This KB) | S/4HANA (Not Covered) |`

Topics in the table: vendor master, customer master, material documents, material ledger, general ledger, document splitting, cost of goods sold, reporting, UI, credit management, output management, MRP, controlling area, cost elements, profit center accounting, segment reporting, business area.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `FastMCP("server", host=..., port=...)` | `FastMCP("server")` + `mcp.run(transport=..., host=...)` | FastMCP 3.0 (Feb 2026) | Transport config in constructor is silently ignored |
| `@mcp.tool()` with parentheses (v2) | `@mcp.tool` without parentheses (v3) | FastMCP 3.0 (Feb 2026) | Parenthesized form creates a factory, not a registration |
| Tool returns `FunctionTool` object | Tool returns the original function | FastMCP 3.0 (Feb 2026) | Code that accessed `.name` or `.description` on the return value breaks |

**Deprecated/outdated:**
- FastMCP 2.x `@mcp.tool()` parenthesized syntax: deprecated, replaced by `@mcp.tool` in v3
- FastMCP constructor transport config (`host=`, `port=` in constructor): deprecated, moved to `mcp.run()` in v3

---

## Open Questions

1. **Python version compatibility**
   - What we know: FastMCP 3.x requires Python >=3.10. System Python is 3.14.2.
   - What's unclear: Whether `str | None` union syntax (Python 3.10+) works cleanly with the `.venv/` Python. It should since venv inherits from system Python 3.14.2.
   - Recommendation: Use `str | None` syntax freely — system Python 3.14.2 fully supports it.

2. **`fastmcp run` vs `__main__` entry point**
   - What we know: Both work for stdio. CONTEXT.md marks this as Claude's discretion.
   - What's unclear: `fastmcp run scripts/mcp_server.py` is a CLI alternative to `python scripts/mcp_server.py`.
   - Recommendation: Use `if __name__ == "__main__": mcp.run()` pattern for simplicity and consistency with validate.py style. This avoids a dependency on the `fastmcp` CLI being on PATH.

3. **Import path for kb_reader.py**
   - What we know: Both files are in `scripts/`. Python relative imports need the right `sys.path` setup.
   - What's unclear: Whether `from kb_reader import ...` works when invoked as `python scripts/mcp_server.py` (depends on whether `scripts/` is on `sys.path`).
   - Recommendation: Planner should add `sys.path.insert(0, str(Path(__file__).resolve().parent))` at the top of `mcp_server.py` to ensure `kb_reader` is importable regardless of invocation method.

---

## Sources

### Primary (HIGH confidence)
- `scripts/validate.py` — `parse_frontmatter()`, `REPO_ROOT`, `FRONTMATTER_RE` patterns (verbatim)
- `scripts/requirements.txt` — confirms PyYAML>=6.0 already present
- `modules/mm/tcodes.md`, `modules/sd/tcodes.md`, `modules/fi/tcodes.md`, `modules/co/tcodes.md` — `### TCODE` heading structure confirmed across all four
- `modules/{mm,sd,fi,co}/config-spro.md` — `### Step N: Title` + `**IMG Path:**` heading structure confirmed
- `modules/{mm,sd,fi,co}/processes.md` — `## N. Process Name` heading structure confirmed
- `.claude/rules/sap-disambiguation.md` — 17-row table structure confirmed
- `modules/{mm,sd,fi,co}/CLAUDE.md` — overview/index files confirmed (content_type=index)

### Secondary (MEDIUM confidence)
- https://pypi.org/project/fastmcp/ — FastMCP 3.0.2 current stable version, Python >=3.10 requirement
- https://gofastmcp.com/deployment/running-server.md — `mcp.run()` defaults to stdio, `__main__` best practice
- https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2.md — v2→v3 breaking changes: decorator syntax, constructor transport params

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — FastMCP 3.0.2 confirmed on PyPI; PyYAML already in repo
- Architecture: HIGH — two-file layout follows existing repo patterns; KB structure confirmed by direct inspection
- Pitfalls: HIGH — FastMCP v2/v3 diff verified from official upgrade docs; other pitfalls from direct KB inspection
- Code examples: HIGH — Pattern 2/3 are verbatim from existing validate.py; Patterns 1/4-9 verified against KB structure

**Research date:** 2026-02-23
**Valid until:** 2026-03-23 (FastMCP moves fast; recheck version before implementation if >2 weeks)
