# Phase 14: Keyword Search Tool - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a single `search_by_keyword` tool to the existing MCP server (`scripts/mcp_server.py`). The tool searches the full KB (modules/, cross-module/, reference/ directories only) for a free-text keyword and returns matching excerpts with source attribution. This is the fallback tool when no P1 tool covers the user's query. No new files outside of scripts/ are created — the tool extends the existing server.

</domain>

<decisions>
## Implementation Decisions

### Result shape & volume
- Excerpt size: up to ~5 lines of surrounding context per match (enough to understand what the match refers to)
- Always show the nearest parent heading above each match (even if the match is in body text below the heading)
- Always include a `Source:` line with the file path per result — consistent with P1 tool behavior
- Maximum 10 results total across the response

### Result ordering
- Order by module then file: MM first, then SD, FI, CO, cross-module, reference
- Group all matches from the same file consecutively (not interleaved)
- Cap at 3 excerpts per file — prevents a single file from dominating the response
- When total matches exceed 10, truncate with a note: e.g., "Showing 10 of N matches. Refine your query for more targeted results."

### Query behavior
- Case-insensitive always — consistent with how P1 tools normalize input
- Multi-word query handling: Claude's discretion (phrase match, AND logic, or hybrid — implement what works best for KB content)
- Search both body text AND YAML frontmatter
- Broad query overflow: apply the 10-result / 3-per-file caps and include a truncation note — no minimum length enforcement

### Scope & file coverage
- Explicit allowlist: search only modules/, cross-module/, and reference/ directories
- Include module-level CLAUDE.md files (modules/{module}/CLAUDE.md) — they contain key concepts worth matching
- Treat reference/ content the same as module content (same ordering tier: reference comes after cross-module)
- Markdown (.md) files only

### Claude's Discretion
- Exact multi-word matching strategy (phrase, AND, or hybrid based on query length/structure)
- Whether to add `search_by_keyword` to `kb_reader.py` (as a new helper) or implement inline in `mcp_server.py`
- Exact excerpt extraction logic (line-based or section-based)
- Tool description wording (must follow "Use this tool ONLY when..." pattern per MCP-09)

</decisions>

<specifics>
## Specific Ideas

- The tool should be the "last resort" fallback — its description should signal to LLMs to use the specific P1 tools first (lookup_tcode, get_config_path, etc.), and only call search_by_keyword when no P1 tool covers the query
- Module order (MM → SD → FI → CO → cross-module → reference) matches the existing KB structure and how consultants think about the domain
- The 2000-token budget constraint is a hard ceiling — 10 results × 5-line excerpts + headings + Source lines should comfortably fit

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 14-keyword-search-tool*
*Context gathered: 2026-02-23*
