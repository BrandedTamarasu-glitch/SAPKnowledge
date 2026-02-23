---
phase: 14-keyword-search-tool
plan: "01"
subsystem: mcp-server
tags: [python, fastmcp, full-text-search, keyword-search, mcp-tool]

# Dependency graph
requires:
  - phase: 13-mcp-server
    provides: scripts/kb_reader.py (KB helpers), scripts/mcp_server.py (FastMCP server), .venv/ with fastmcp==3.0.2
provides:
  - search_kb() helper in kb_reader.py: full-text keyword search across 46 KB files
  - search_by_keyword() MCP tool in mcp_server.py: last-resort fallback search tool
  - _get_ordered_kb_files(), _nearest_heading(), _excerpt(), _matches_query() private helpers
affects: [15-deployment-docs, future phases using kb_reader search capability]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Allowlist scope pattern: _SEARCH_DIRS constant restricts search to modules/, cross-module/, reference/ only — never .planning/, .claude/, scripts/"
    - "Phrase/AND query routing: <=2 tokens use phrase match; 3+ tokens use AND logic"
    - "Module-priority ordering: MM -> SD -> FI -> CO -> cross-module -> reference (locked decision)"
    - "Return tuple pattern: search_kb returns (results, total_count) — mcp_server unpacks both"

key-files:
  created: []
  modified:
    - scripts/kb_reader.py
    - scripts/mcp_server.py

key-decisions:
  - "search_kb() returns tuple (list[dict], int) — both values used by mcp_server to show truncation note when total > cap"
  - "_HEADING_RE matches #{1,3} (not just ## and ###) — includes # Title headings as fallback for preamble matches"
  - "Stop scanning entirely after 10-result cap reached — simplified: no need to count tail matches once cap is full"
  - "Truncation note uses 'N+' suffix to signal count may be a lower bound (scanning stopped early)"
  - "Tool docstring follows MCP-09 'Use this tool ONLY when...' pattern with explicit P1 tool list for accurate LLM routing"

patterns-established:
  - "LLM invocation condition pattern: search_by_keyword docstring names all P1 tools explicitly so LLM knows when NOT to use it"
  - "Last-resort fallback: search_by_keyword is P2 tier — called only when no P1 tool matches the query"

requirements-completed: [MCP-08]

# Metrics
duration: 2min
completed: 2026-02-23
---

# Phase 14 Plan 01: Keyword Search Tool Summary

**Full-text keyword search across 46 KB files via search_kb() helper and search_by_keyword() MCP tool with heading context, source attribution, and phrase/AND query logic**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-23T16:44:23Z
- **Completed:** 2026-02-23T16:46:05Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added search_kb() to kb_reader.py: searches 46 KB files in module-priority order, returns up to 10 results with heading context and source paths
- Added search_by_keyword() MCP tool to mcp_server.py: last-resort fallback with LLM routing guidance, empty query guard, no-results message, truncation note
- Scope restriction verified: .planning/, .claude/, and scripts/ directories never searched (AST-verified zero print() calls in mcp_server.py)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add search_kb() helper to kb_reader.py** - `b087180` (feat)
2. **Task 2: Add search_by_keyword tool to mcp_server.py** - `0329ed1` (feat)

**Plan metadata:** (final metadata commit — see below)

## Files Created/Modified

- `scripts/kb_reader.py` - Added _SEARCH_DIRS, _HEADING_RE, _get_ordered_kb_files(), _nearest_heading(), _excerpt(), _matches_query(), search_kb()
- `scripts/mcp_server.py` - Added search_kb import, added search_by_keyword() @mcp.tool

## Decisions Made

- search_kb() returns (list, int) tuple so mcp_server can show truncation note when total > cap
- _HEADING_RE matches #{1,3} including # Title headings as fallback for content matched before first ## heading
- Stop scanning entirely after 10-result cap (simplified approach) — tail count would be inaccurate anyway; "N+" suffix signals lower bound
- Tool docstring explicitly names all 5 P1 tools so LLM knows precisely when NOT to use search_by_keyword

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MCP server now has 6 tools: 5 P1 (lookup_tcode, get_module_overview, get_config_path, get_process_flow, compare_ecc_s4) + 1 P2 (search_by_keyword)
- All MCP-01 through MCP-10 requirements met
- Ready for Phase 15 (deployment documentation)

---
*Phase: 14-keyword-search-tool*
*Completed: 2026-02-23*
