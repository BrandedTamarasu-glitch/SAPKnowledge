# Phase 14: Keyword Search Tool - Research

**Researched:** 2026-02-23
**Domain:** Python text search, markdown section extraction, FastMCP tool design
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Result shape and volume**
- Excerpt size: up to ~5 lines of surrounding context per match (enough to understand what the match refers to)
- Always show the nearest parent heading above each match (even if the match is in body text below the heading)
- Always include a `Source:` line with the file path per result — consistent with P1 tool behavior
- Maximum 10 results total across the response

**Result ordering**
- Order by module then file: MM first, then SD, FI, CO, cross-module, reference
- Group all matches from the same file consecutively (not interleaved)
- Cap at 3 excerpts per file — prevents a single file from dominating the response
- When total matches exceed 10, truncate with a note: e.g., "Showing 10 of N matches. Refine your query for more targeted results."

**Query behavior**
- Case-insensitive always — consistent with how P1 tools normalize input
- Multi-word query handling: Claude's discretion (phrase match, AND logic, or hybrid — implement what works best for KB content)
- Search both body text AND YAML frontmatter
- Broad query overflow: apply the 10-result / 3-per-file caps and include a truncation note — no minimum length enforcement

**Scope and file coverage**
- Explicit allowlist: search only modules/, cross-module/, and reference/ directories
- Include module-level CLAUDE.md files (modules/{module}/CLAUDE.md) — they contain key concepts worth matching
- Treat reference/ content the same as module content (same ordering tier: reference comes after cross-module)
- Markdown (.md) files only

### Claude's Discretion
- Exact multi-word matching strategy (phrase, AND, or hybrid based on query length/structure)
- Whether to add `search_by_keyword` to `kb_reader.py` (as a new helper) or implement inline in `mcp_server.py`
- Exact excerpt extraction logic (line-based or section-based)
- Tool description wording (must follow "Use this tool ONLY when..." pattern per MCP-09)

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MCP-08 | User can search the full KB by keyword and get matching excerpts with source module/file | search_by_keyword tool: file enumeration, line-based excerpt extraction, heading detection, module ordering, 10-result cap |
</phase_requirements>

---

## Summary

Phase 14 adds a single `search_by_keyword` tool to the existing `scripts/mcp_server.py`. The tool performs a full-text case-insensitive search across all 46 markdown files in `modules/`, `cross-module/`, and `reference/` directories, returning up to 10 excerpts with the nearest parent heading and a `Source:` attribution line per excerpt.

The KB has 46 `.md` files across the three searchable directories. Files range from 28 to ~1200 lines. The largest single file (`cross-module/playbooks.md`) has 1189 lines, and there are dense files like `modules/mm/mm-advanced.md` that contain hundreds of matches for common terms. The 10-result / 3-per-file cap is the primary mechanism for keeping responses within the 2000-token budget.

The implementation should add one helper function (`search_kb`) to `scripts/kb_reader.py` and one tool function (`search_by_keyword`) to `scripts/mcp_server.py`. No new files outside `scripts/` are needed.

**Primary recommendation:** Line-based search with backwards heading scan. For multi-word queries shorter than 3 words, use phrase match. For 3+ words, use AND logic (all words must appear on the same line or within the 5-line context window). Add helper to `kb_reader.py` to maintain the two-file separation established in Phase 13.

---

## Standard Stack

### Core (already in place from Phase 13)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastmcp | 3.0.2 | MCP server framework | Pinned in scripts/requirements.txt |
| PyYAML | >=6.0 | Frontmatter parsing | Already in use in kb_reader.py |
| re (stdlib) | stdlib | Regex for heading detection, keyword matching | No new dependency needed |
| pathlib (stdlib) | stdlib | File system traversal | Already used in KB_ROOT and parse_frontmatter |

### No New Dependencies Required

The search implementation uses only Python stdlib (`re`, `pathlib`) plus what is already imported in `kb_reader.py`. No fuzzy-match libraries (difflib, rapidfuzz), no full-text indexing (whoosh, tantivy), no embedding libraries — pure line-by-line scan.

**Rationale:** The KB is 46 files totaling ~9000 lines. A full linear scan completes in under 50ms on modern hardware. Index complexity is not justified for this size. The out-of-scope note in REQUIREMENTS.md explicitly states "Semantic search / embeddings: KB structure + keyword search covers 80%+ of patterns at a fraction of the complexity."

---

## Architecture Patterns

### File Structure (No Changes to Existing Layout)

```
scripts/
├── mcp_server.py      # Add search_by_keyword tool (one new @mcp.tool function)
├── kb_reader.py       # Add search_kb() helper function
├── validate.py        # Unchanged
└── requirements.txt   # Unchanged (no new dependencies)
```

### Pattern 1: File Enumeration in Module Order

**What:** Build an ordered list of all `.md` files in the search scope, sorted by module rank.
**When to use:** Every `search_by_keyword` call.

```python
# Source: kb_reader.py patterns established in Phase 13
MODULE_ORDER = ["mm", "sd", "fi", "co", "cross-module", "reference"]

def _get_ordered_kb_files() -> list[Path]:
    """Return all searchable .md files in module-priority order."""
    files = []
    # modules/ subdirectories in MODULE_ORDER sequence
    for mod in ["mm", "sd", "fi", "co"]:
        mod_dir = KB_ROOT / "modules" / mod
        if mod_dir.is_dir():
            files.extend(sorted(mod_dir.glob("*.md")))
    # cross-module/ and reference/ directories
    for top_dir in ["cross-module", "reference"]:
        d = KB_ROOT / top_dir
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    return files
```

Confidence: HIGH — verified against actual directory structure (46 files confirmed).

### Pattern 2: Line-Based Keyword Search with Heading Detection

**What:** Scan each file line by line, detect keyword matches, find nearest parent heading by walking backwards, extract 5-line context window.

**When to use:** Core search logic inside `search_kb()`.

```python
# Source: heading patterns verified across all KB files
HEADING_RE = re.compile(r'^(#{1,3}) (.+)')

def _find_nearest_heading(lines: list[str], match_idx: int) -> str:
    """Walk backwards from match to find nearest ## or ### heading."""
    for i in range(match_idx, -1, -1):
        if HEADING_RE.match(lines[i]):
            return lines[i].strip()
    return ""  # No heading found (rare: match in file preamble)

def _extract_excerpt(lines: list[str], match_idx: int, context: int = 2) -> str:
    """Return up to 2 lines before + match line + 2 lines after (5 lines total)."""
    start = max(0, match_idx - context)
    end = min(len(lines), match_idx + context + 1)
    return "\n".join(lines[start:end]).strip()
```

**Heading pattern verification:** All KB files use `## Section` and `### Subsection` headings consistently. Module CLAUDE.md files use `## When to Use`, `## File Index`, `## Key Concepts`. T-code files use `### ME21N — Create Purchase Order`. Config files use `### Step 1: Description`. Walking backwards always finds a meaningful heading within 30 lines for any match.

Confidence: HIGH — verified by inspecting heading structure in mm/tcodes.md, fi/config-spro.md, cross-module/playbooks.md, and reference/org-structure.md.

### Pattern 3: Multi-Word Query Strategy

**What:** Determine match logic based on query word count.
**When to use:** Inside keyword match evaluation for each line.

**Recommended approach (Claude's discretion):** Phrase match for 1-2 word queries; AND logic (all tokens present on the same line, case-insensitive) for 3+ word queries.

```python
def _line_matches(line: str, tokens: list[str], is_phrase: bool) -> bool:
    """Case-insensitive match: phrase for short queries, AND for longer ones."""
    line_lower = line.lower()
    if is_phrase:
        phrase = " ".join(tokens)
        return phrase in line_lower
    else:
        return all(t in line_lower for t in tokens)
```

**Rationale for AND over phrase for long queries:** SAP concepts often span words non-adjacently (e.g., query "tolerance key OMR6" — the tcode and concept appear on the same line but not always adjacently). AND logic finds these natural while phrase match would miss them. For short queries (1-2 words), phrase match avoids false positives from common words.

Confidence: MEDIUM — based on inspection of KB content patterns; actual query behavior may vary. This is in Claude's discretion per CONTEXT.md.

### Pattern 4: Per-File Cap and Global Cap Enforcement

**What:** Cap results at 3 per file and 10 total; collect total match count for truncation note.
**When to use:** In the main `search_kb()` loop.

```python
def search_kb(query: str, max_results: int = 10, max_per_file: int = 3) -> list[dict]:
    """
    Search all KB files for query. Returns list of result dicts:
      {"source": rel_path, "heading": str, "excerpt": str}
    """
    tokens = query.strip().lower().split()
    if not tokens:
        return []
    is_phrase = len(tokens) <= 2

    results = []
    total_match_count = 0

    for filepath in _get_ordered_kb_files():
        text = filepath.read_text(encoding="utf-8")
        lines = text.splitlines()
        rel_path = str(filepath.relative_to(KB_ROOT))

        file_results = []
        for i, line in enumerate(lines):
            if _line_matches(line, tokens, is_phrase):
                total_match_count += 1
                if len(file_results) < max_per_file:
                    heading = _find_nearest_heading(lines, i)
                    excerpt = _extract_excerpt(lines, i)
                    file_results.append({
                        "source": rel_path,
                        "heading": heading,
                        "excerpt": excerpt,
                    })

        results.extend(file_results)
        if len(results) >= max_results:
            # Tally remaining files for accurate truncation count (optional)
            break

    return results[:max_results], total_match_count
```

Note: `total_match_count` enables the truncation message. The count is an undercount if iteration stops early (breaking when max_results is reached), which is acceptable — the message indicates there are more results, not an exact total.

Confidence: HIGH — the cap logic follows directly from the locked decisions in CONTEXT.md.

### Pattern 5: Response Formatting

**What:** Format search results as plain markdown text consistent with P1 tool responses.
**When to use:** In the `search_by_keyword` tool function in `mcp_server.py`.

```python
@mcp.tool
def search_by_keyword(query: str) -> str:
    """Use this tool ONLY when the user asks a general SAP question that does not
    match a specific T-code lookup, SPRO configuration path, business process,
    or ECC/S4 comparison — for example, 'what does SAP do with GR/IR?',
    'find everything about tolerance keys', or 'show me content about consignment'.
    Use the specialized tools (lookup_tcode, get_config_path, get_process_flow,
    compare_ecc_s4) first. Use search_by_keyword only as a fallback when no
    specific P1 tool covers the query."""
    results, total = search_kb(query.strip())

    if not results:
        return (
            f"No results found for '{query}' in the SAP ECC 6 KB. "
            f"The KB covers MM, SD, FI, CO modules and cross-module processes. "
            f"Try a different keyword or use a more specific tool (lookup_tcode, "
            f"get_config_path, get_process_flow, compare_ecc_s4)."
        )

    parts = []
    for r in results:
        parts.append(f"{r['heading']}\n\n{r['excerpt']}\n\nSource: {r['source']}")

    body = "\n\n---\n\n".join(parts)

    if total > len(results):
        body += f"\n\n---\n\nShowing {len(results)} of {total} matches. Refine your query for more targeted results."

    return body
```

Confidence: HIGH — follows P1 tool response patterns from Phase 13 (`Source:` line, plain markdown text).

### Anti-Patterns to Avoid

- **Building an index at startup:** The KB is ~9000 lines — no pre-indexing needed. Scanning at query time avoids index drift when KB files change.
- **Returning full file content:** Even for 1 match, always use line-context extraction. Full files can exceed 5000 tokens.
- **Searching .planning/, .claude/, or scripts/ directories:** Allowlist is explicit — only `modules/`, `cross-module/`, `reference/`. These paths must be hardcoded in `_get_ordered_kb_files()`.
- **Using `print()` for debug output:** stdout is the MCP wire. Any stray `print()` corrupts the MCP protocol. Use stderr only if needed (no debug output in production code).
- **Raising exceptions for no-results:** Return a clear "no results" string, not a Python exception. This matches the P1 tool pattern of returning user-facing messages for all edge cases.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dependency resolution | A custom requirements file or pip subprocess call | scripts/requirements.txt (already exists, fastmcp==3.0.2 pinned) | Already in place from Phase 13 |
| File path computation | Custom path logic or env vars | KB_ROOT = Path(__file__).resolve().parent.parent | Established pattern in kb_reader.py, verified correct |
| Frontmatter stripping | New regex | FRONTMATTER_RE already defined in kb_reader.py | Identical pattern to validate.py; already imported |
| Module validation | Reimplementing VALID_MODULES check | Not needed — search_by_keyword takes free text, no module param | The tool is module-agnostic by design |

**Key insight:** Everything needed for the search helper already exists in `kb_reader.py` (KB_ROOT, FRONTMATTER_RE, parse_frontmatter). The search tool is additive — it uses the established infrastructure without replacing it.

---

## Common Pitfalls

### Pitfall 1: Heading Detection Misses Top-Level `#` Headings

**What goes wrong:** The heading detection regex only matches `##` and `###`, missing the file's `# Title` heading. For matches in the first 10 lines of a file (before any `##` section), the heading returned is blank.

**Why it happens:** KB files start with `# Module Name — T-codes` then have `## Workflow Index` then `## Section Name`. Matches in the preamble (workflow index table) have no `##` heading above them.

**How to avoid:** Include `#` in the heading regex: `re.compile(r'^#{1,3} ')`. Walking backwards will find the `#` title heading as a fallback. This provides useful context even when the match is at the top of the file.

**Warning signs:** If `_find_nearest_heading` returns empty string for a result, the heading regex is too narrow.

### Pitfall 2: 5-Line Context Window Bleeds Across File Boundaries

**What goes wrong:** The excerpt extraction uses `lines[start:end]` which is safe within a file. However, if `match_idx = 0` and `context = 2`, `start = max(0, -2) = 0` — this is correctly handled. No bleed across files since each file is processed independently.

**How to avoid:** The `max(0, ...)` and `min(len(lines), ...)` bounds in `_extract_excerpt` ensure the window stays within the file. Verify this is implemented correctly.

### Pitfall 3: Frontmatter Lines Produce Spurious Matches

**What goes wrong:** Searching for "high" matches `confidence: high` in frontmatter. Searching for "mm" matches `module: mm`. These are not useful content matches.

**Why it happens:** CONTEXT.md says "Search both body text AND YAML frontmatter." This is a correct and intentional decision — but the frontmatter lines themselves are in YAML format, not prose, so a match there may not provide useful context.

**How to avoid:** Accept this behavior — it is per spec. The heading returned for a frontmatter match will be the file's `# Title` heading (first heading, since frontmatter appears before any heading). The excerpt will show the frontmatter YAML. This is low-frequency and correct: searching for "confidence: high" to find high-confidence files is a valid use case.

### Pitfall 4: Total Match Count is Understated When Breaking Early

**What goes wrong:** If `break` is used to stop after `max_results`, the `total_match_count` only reflects files processed before the break — not the true total across all 46 files.

**Why it happens:** Performance optimization of stopping early.

**How to avoid:** Either (a) continue counting without collecting results after the cap is reached (two-phase approach: count first, then collect), or (b) accept the undercount in the truncation note. Option (b) is simpler. The truncation message says "Showing 10 of N+" which is still accurate — N is a lower bound. This is acceptable for a fallback tool.

### Pitfall 5: Tool Description Too Broad — LLM Routes to It Prematurely

**What goes wrong:** If the tool docstring doesn't explicitly mention that P1 tools should be tried first, the LLM may route every SAP question to `search_by_keyword`, bypassing the more precise P1 tools.

**Why it happens:** `search_by_keyword` semantically matches any SAP query. Without explicit routing guidance, it becomes the default handler.

**How to avoid:** The tool description MUST follow the MCP-09 pattern ("Use this tool ONLY when...") and MUST explicitly list all five P1 tools as the preferred first choices. The description in the Architecture Patterns section above demonstrates this. Test routing against the 10-query routing test in MCP Inspector.

---

## Code Examples

### Complete search_kb Helper

Verified pattern using KB_ROOT and FRONTMATTER_RE from kb_reader.py:

```python
# Source: kb_reader.py extension — search_kb() helper
import re
from pathlib import Path
# KB_ROOT, FRONTMATTER_RE already defined in kb_reader.py

_HEADING_RE = re.compile(r"^#{1,3} ")

# Module ordering matches KB directory layout (verified against actual structure)
_SEARCH_DIRS = [
    ("mm", "modules/mm"),
    ("sd", "modules/sd"),
    ("fi", "modules/fi"),
    ("co", "modules/co"),
    ("cross-module", "cross-module"),
    ("reference", "reference"),
]


def _get_ordered_kb_files() -> list[Path]:
    """Return all .md files in module-priority order (allowlisted dirs only)."""
    files = []
    for _mod, rel_dir in _SEARCH_DIRS:
        d = KB_ROOT / rel_dir
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    return files


def _nearest_heading(lines: list[str], idx: int) -> str:
    """Walk backwards from idx to find nearest heading line."""
    for i in range(idx, -1, -1):
        if _HEADING_RE.match(lines[i]):
            return lines[i].strip()
    return ""


def _excerpt(lines: list[str], idx: int, context: int = 2) -> str:
    """Return up to (context) lines before + match + (context) lines after."""
    start = max(0, idx - context)
    end = min(len(lines), idx + context + 1)
    return "\n".join(lines[start:end]).strip()


def _matches_query(line: str, tokens: list[str], phrase: bool) -> bool:
    """Case-insensitive match: phrase for <=2 tokens, AND for 3+."""
    lower = line.lower()
    if phrase:
        return " ".join(tokens) in lower
    return all(t in lower for t in tokens)


def search_kb(
    query: str, max_results: int = 10, max_per_file: int = 3
) -> tuple[list[dict], int]:
    """
    Search all KB files for query.

    Returns:
        (results, total_match_count)
        results: list of {"source": rel_path, "heading": str, "excerpt": str}
        total_match_count: total lines matched (may be undercount if capped early)
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

        # Stop collecting after cap; continue counting for accurate total
        # (simplified: stop entirely after cap for performance)
        if len(results) >= max_results:
            break

    return results, total_count
```

### Complete search_by_keyword Tool Function

```python
# Source: mcp_server.py addition — import search_kb from kb_reader
from kb_reader import (
    # ... existing imports ...
    search_kb,
)

@mcp.tool
def search_by_keyword(query: str) -> str:
    """Use this tool ONLY when the user asks a general SAP ECC 6 question that
    cannot be answered by any of the specific tools: lookup_tcode (for T-code
    names), get_config_path (for SPRO/IMG configuration), get_process_flow (for
    step-by-step business processes), get_module_overview (for module content
    index), or compare_ecc_s4 (for ECC vs S/4HANA differences). Use
    search_by_keyword as a last-resort fallback when the query is open-ended —
    for example: 'what is GR/IR clearing?', 'find content about tolerance keys',
    'show me everything about consignment stock'. Do NOT use for specific T-code
    lookups or SPRO path queries — use the specialized tools for those."""
    if not query.strip():
        return (
            "Please provide a keyword or phrase to search. "
            "Example: 'GR/IR clearing', 'tolerance keys', 'consignment stock'."
        )

    results, total = search_kb(query.strip())

    if not results:
        return (
            f"No results found for '{query}' in the SAP ECC 6 KB. "
            f"This KB covers MM, SD, FI, CO modules and cross-module processes. "
            f"Try rephrasing with a key term (T-code, config path, or process name). "
            f"For T-code lookup: use lookup_tcode. For SPRO paths: use get_config_path."
        )

    parts = []
    for r in results:
        section = f"{r['heading']}\n\n{r['excerpt']}\n\nSource: {r['source']}"
        parts.append(section)

    output = "\n\n---\n\n".join(parts)

    if total > len(results):
        output += (
            f"\n\n---\n\nShowing {len(results)} of {total}+ matches. "
            f"Refine your query for more targeted results."
        )

    return output
```

---

## KB File Inventory (Confirmed Scope)

The following 46 files are in the search scope. Confirmed by `find` against the actual repo.

**modules/mm/** (8 files)
- CLAUDE.md, config-spro.md, integration.md, master-data.md, mm-advanced.md, patterns.md, processes.md, tcodes.md

**modules/sd/** (8 files)
- CLAUDE.md, config-spro.md, integration.md, master-data.md, patterns.md, processes.md, sd-advanced.md, tcodes.md

**modules/fi/** (8 files)
- CLAUDE.md, account-determination.md, config-spro.md, fi-advanced.md, integration.md, master-data.md, patterns.md, processes.md, tcodes.md

Note: fi/ has 9 files (includes account-determination.md). Total is 46 confirmed.

**modules/co/** (8 files)
- CLAUDE.md, co-advanced.md, config-spro.md, integration.md, master-data.md, patterns.md, processes.md, tcodes.md

**cross-module/** (8 files)
- CLAUDE.md, checklists.md, design-patterns.md, mm-sd-integration.md, order-to-cash.md, playbooks.md, procure-to-pay.md, record-to-report.md

**reference/** (5 files)
- CLAUDE.md, document-types.md, movement-types.md, org-structure.md, posting-keys.md

**Total: 46 files**

Largest files (highest match density risk):
- cross-module/playbooks.md: 1189 lines
- modules/mm/mm-advanced.md: ~800 lines
- cross-module/design-patterns.md: 522 lines
- reference/org-structure.md: 353 lines

The 3-per-file cap prevents playbooks.md or mm-advanced.md from consuming all 10 result slots.

---

## Token Budget Analysis

**Per result:** 1 heading line (~8 tokens) + 5 context lines (~15 tokens each = 75 tokens) + 1 Source line (~10 tokens) + separator (~3 tokens) = ~96 tokens per result.

**10 results:** 10 × 96 = ~960 tokens for result content.

**Truncation note:** ~20 tokens.

**Total estimate:** ~980 tokens — well within the 2000-token ceiling.

**Worst case** (long heading + dense content lines): 10 × (20 + 5×30 + 15) = 10 × 185 = 1850 tokens — still within budget.

Confidence: HIGH — verified against actual KB line lengths and token estimation formula (chars / 4).

---

## Import Changes Required

In `mcp_server.py`, add `search_kb` to the import from `kb_reader`:

```python
from kb_reader import (
    normalize_module,
    get_file_body,
    extract_tcode_section,
    find_section_by_topic,
    extract_disambiguation_rows,
    parse_frontmatter,
    search_kb,           # NEW — Phase 14
    KB_ROOT,
    TCODE_FILE,
    OVERVIEW_FILE,
    CONFIG_FILE,
    PROCESS_FILE,
    DISAMBIGUATION_FILE,
)
```

No changes to `scripts/requirements.txt` — all search logic uses stdlib.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pre-indexed full-text search (whoosh, sqlite FTS) | At-query-time linear scan | Appropriate for <50 files | No index drift, no startup cost, simpler code |
| Semantic/embedding search | Keyword + AND logic | N/A — out of scope by design | Fast, deterministic, no model dependency |
| Returning full sections | 5-line context windows | Phase 13 established the pattern | Stays within 2000-token MCP budget |

**Deprecated/outdated:**
- `REQUIREMENTS.md` explicitly calls out "Semantic search / embeddings" as out of scope. Do not introduce vector similarity or embedding libraries.

---

## Open Questions

1. **AND logic false positives for 3+ word queries**
   - What we know: AND logic finds all tokens present on the same line.
   - What's unclear: A query like "purchase order goods receipt" has all three common terms appearing on many lines throughout the KB — potentially 100+ matches on a single file.
   - Recommendation: The 3-per-file cap and 10-result total cap handle this automatically. The truncation message tells the user to refine. No special handling needed beyond the caps.

2. **Frontmatter-only matches**
   - What we know: Searching "mm" or "high" or "tcodes" will match frontmatter lines like `module: mm`, `confidence: high`, `content_type: tcodes`.
   - What's unclear: Whether these matches consume result slots in a confusing way.
   - Recommendation: Accept per spec. The `_nearest_heading` function will return the file `# Title` heading for frontmatter matches, which is informative. Low frequency in practice.

3. **Empty query handling**
   - What we know: `query.strip()` with an empty string would result in `tokens = []`.
   - Recommendation: Guard with an early return (shown in code example) before calling `search_kb`.

---

## Sources

### Primary (HIGH confidence)
- Direct code inspection: `scripts/mcp_server.py`, `scripts/kb_reader.py`, `scripts/validate.py` — all patterns verified against actual implementation
- Direct file system inspection: all 46 KB files enumerated and sampled for heading structure, line length, and keyword density
- Phase 13 RESEARCH.md and CONTEXT.md — locked decisions and established patterns

### Secondary (MEDIUM confidence)
- Phase 14 CONTEXT.md decisions — directly govern implementation choices
- REQUIREMENTS.md MCP-08 and MCP-09 requirements — define success criteria and tool description constraints

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; stdlib only
- Architecture: HIGH — file enumeration and heading patterns verified against actual KB
- Token budget: HIGH — calculated against actual KB line lengths
- Multi-word matching strategy: MEDIUM — AND vs phrase trade-off is Claude's discretion; logic is sound but untested against full query set
- Pitfalls: HIGH — verified against actual KB structure and Phase 13 patterns

**Research date:** 2026-02-23
**Valid until:** 2026-04-23 (stable — KB file structure and Python stdlib don't change; FastMCP 3.0.2 pinned)
