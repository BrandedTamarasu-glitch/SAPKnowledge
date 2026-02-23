# Phase 13: MCP Server Scaffold + P1 Tools - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a Python FastMCP server (in scripts/) exposing five read-only tools that let MCP-capable clients (Claude Code, Claude Desktop) query the SAP ECC 6 KB with targeted, section-level responses. The KB markdown files are unchanged — the server is a thin query layer on top. New tools (search_by_keyword) and deployment docs are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Tool response shape
- Format: plain markdown text (not structured JSON) — Claude renders naturally in conversation
- Size ceiling: tight — just the matching section (~300–500 tokens); no full file dumps
- Source attribution: always include a `Source:` line with the KB file path (e.g., `Source: modules/fi/tcodes.md`)
- `compare_ecc_s4`: return matching table rows as-is from the existing disambiguation table (no prose synthesis)

### KB extraction strategy
- Parse at query time (no pre-indexing on startup) — read relevant file, walk markdown headers, return matching section
- KB root location: resolved via path relative to the server script (scripts/ → repo root two levels up) — no env var required
- T-code matching: normalize input to uppercase, match case-insensitively (handles 'migo', 'Migo', 'MIGO')
- Module matching: normalize to uppercase 2-letter abbreviation (MM/SD/FI/CO) — accept full names, abbreviations, any case

### Install & venv approach
- Venv location: project-local `.venv/` at repo root (gitignored)
- Setup: `python -m venv .venv && .venv/bin/pip install -r requirements.txt`
- `.mcp.json` uses absolute path to interpreter (e.g., `/home/corye/Claude/SAPKnowledge/.venv/bin/python`)
- Package pinning: exact version in requirements.txt (`fastmcp==X.Y.Z`) — researcher to identify current stable version
- Server code location: `scripts/` directory alongside `validate.py` (consistent with existing repo structure)

### Tool routing & edge cases
- Tool descriptions: strict routing rules — written as LLM invocation conditions ("Use this tool ONLY when...") to pass the 10-query routing test in MCP Inspector
- T-code not found: return clear "not found" message with scope note (e.g., "T-code XK99 not found. This KB covers MM/SD/FI/CO transactions.")
- Module not in KB (e.g., PM, QM): return clear error ("Only MM/SD/FI/CO are covered in this KB")
- Topic not matched for get_config_path / get_process_flow: attempt partial/fuzzy match on section headings; return closest section found (not a hard fail)

### Claude's Discretion
- Exact fuzzy matching algorithm for topic parameter (substring, normalized, or scored)
- Internal helper structure (single file vs. module split in scripts/)
- Exact FastMCP version to pin (researcher identifies at implementation time)
- Whether to add a `__main__` entry point or rely on `fastmcp run` invocation

</decisions>

<specifics>
## Specific Ideas

- The KB already has consistent `### TCODE` heading structure per T-code in tcodes.md files — extraction should leverage this pattern
- Tool description design: follow MCP-09 requirement that descriptions are LLM invocation conditions, not marketing copy
- STATE.md notes the venv strategy was a known blocker — the absolute-path + .venv/ at root decision resolves it

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 13-mcp-server-scaffold-p1-tools*
*Context gathered: 2026-02-23*
