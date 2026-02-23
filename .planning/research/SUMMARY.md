# Project Research Summary — v1.1: MCP Server Layer

**Project:** SAP ECC 6 Knowledge Base — MCP Server Layer
**Domain:** MCP server exposing a structured markdown knowledge base
**Researched:** 2026-02-23
**Synthesized:** 2026-02-23
**Confidence:** HIGH — all four research files grounded in official MCP documentation, live npm registry checks, direct file inspection of this repo, and runtime environment verification.

> This summary supersedes the v1.0 SUMMARY.md (content curation research). The v1.0 findings remain valid — this document covers v1.1 only: adding an MCP server layer on top of the existing KB. The existing flat-file KB structure and CLAUDE.md loading path are unchanged.

---

## Executive Summary

The SAP ECC 6.0 Knowledge Base already exists as ~35 curated markdown files with consistent YAML frontmatter (`module`, `content_type`, `confidence`, `last_verified`). The v1.1 milestone adds one thing: an MCP server layer that exposes the KB to Claude Code and Claude Desktop as callable tools, enabling the model to query the KB programmatically rather than relying on context-window file loading. This is a purely additive layer — the existing CLAUDE.md hierarchy and `.claude/rules/` routing continue to work unchanged. The MCP server reads from the same files; it never moves, transforms, or indexes them.

The recommended implementation is **Python + FastMCP**, chosen over TypeScript + Node.js because Python is already present in this repo (`scripts/validate.py`, `scripts/requirements.txt`, PyYAML already installed, Python 3.14.2 at `/usr/bin/python3`). The Python path requires two new files in `scripts/` and one added dependency, while TypeScript would require a new `mcp-server/` subdirectory, `package.json`, `tsconfig.json`, and a build step. Both SDK options are equally mature — the decision is purely about minimizing footprint in an existing codebase. The full conflict resolution is in the dedicated section below.

The MCP server should launch with five P1 tools covering the highest-frequency consultant query patterns: `lookup_tcode`, `get_module_overview`, `get_config_path`, `get_process_flow`, and `compare_ecc_s4`. These five tools have LOW implementation complexity (they map directly to existing, consistently-structured KB files) and cover T-code lookup, SPRO config, E2E process flows, and ECC/S4 disambiguation — the stated primary purpose of this KB. Four P2 tools follow post-validation. Three P3 tools are deferred to v2 due to higher parsing complexity and dependency on earlier tools being stable.

---

## Stack Conflict Resolution

**Conflict:** STACK.md recommends TypeScript + `@modelcontextprotocol/sdk` (Node.js 22). ARCHITECTURE.md recommends Python + FastMCP.

**Resolution: Use Python + FastMCP.**

| Factor | TypeScript + Node.js | Python + FastMCP | Decision |
|--------|---------------------|------------------|----------|
| Language already in repo | No — new language, new toolchain | Yes — `scripts/validate.py` is Python | Python wins |
| Runtime available | Node 22.22.0 installed | Python 3.14.2 at `/usr/bin/python3` | Tie |
| Existing KB I/O code | None | `validate.py` has `parse_frontmatter()` + YAML logic | Python wins |
| Dependency already installed | No PyYAML equivalent needed | PyYAML already in `scripts/requirements.txt` | Python wins |
| SDK maturity | `@modelcontextprotocol/sdk@1.27.0` (official, typed) | `mcp[cli]` / FastMCP (official Python SDK) | Tie |
| Type safety | Full TypeScript type system | Python type hints + runtime validation | TypeScript wins |
| Directory footprint | New `mcp-server/` dir, `package.json`, `tsconfig.json`, build step | Two files in `scripts/`, one line in `requirements.txt` | Python wins |
| Architecture research coverage | Not researched | Full architecture in ARCHITECTURE.md — diagrams, data flows, anti-patterns, all against Python path | Python wins |

**TypeScript is the better choice when:** no existing Python codebase, team prioritizes end-to-end type safety, or tool input schemas are complex enough that the TypeScript type system catches real bugs at author time. For this project, TypeScript adds setup overhead without meaningful benefit given the existing Python foundation.

**Concrete decision:** Implement `scripts/mcp_server.py` (FastMCP entry point) + `scripts/kb_reader.py` (KB I/O utilities) + `mcp>=1.2.0` added to `scripts/requirements.txt`. The TypeScript option is documented in STACK.md and remains valid if language preferences change.

---

## Key Findings

### From STACK.md

- **stdio transport is correct** for a local single-user deployment. No port, no auth, no daemon. The MCP client spawns the server as a child process. Use `mcp.run(transport="stdio")`.
- **Never write to stdout in stdio mode.** `print()` or any stdout write corrupts the JSON-RPC message stream. All logging must go to `sys.stderr`. This is the most commonly violated rule across all MCP SDK implementations (Python, TypeScript, Java, Kotlin, Rust, C#).
- **Tools, not Resources.** For a KB query pattern where the LLM decides what to retrieve and when, Tools (`@mcp.tool()`) are the correct primitive. Resources require the client to browse specific URIs — wrong for this use case.
- **Three tools in STACK.md (`search_kb`, `get_file`, `list_files`)** are a viable minimum. FEATURES.md expands this to 5 P1 tools with better query-intent targeting against specific KB content types. Use FEATURES.md's tool design.
- **Avoid:** vector databases, LangChain/LlamaIndex, HTTP transport for local use, embedding models at query time. The KB is ~35 files; file system + string search is sufficient and completes in under 200ms.
- **TypeScript alternative documented:** `@modelcontextprotocol/sdk@1.27.0`, zod 4.3.6, Node16 module resolution, `console.error()` for logging. All versions verified against npm registry 2026-02-23. If TypeScript is chosen, STACK.md provides complete setup instructions.

### From FEATURES.md

- **5 P1 tools (launch with all five)** — all have LOW implementation complexity and cover the highest-frequency query types:
  - `lookup_tcode` — most common SAP query; parses `modules/{module}/tcodes.md` by H3 heading
  - `get_module_overview` — orientation tool; reads `modules/{module}/CLAUDE.md` file index
  - `get_config_path` — SPRO/IMG config paths; parses `modules/{module}/config-spro.md`
  - `get_process_flow` — P2P/O2C/R2R and module-level steps; reads `cross-module/` and `modules/{module}/processes.md`
  - `compare_ecc_s4` — primary KB purpose; reads `.claude/rules/sap-disambiguation.md` + module S/4HANA Differences sections
- **4 P2 tools (add after observing Phase 1 gaps):** `search_by_keyword`, `lookup_movement_type`, `get_integration_points`, `get_period_end_checklist`
- **3 P3 tools (v2+):** `get_account_determination` (high parse complexity across two files), `get_scenario_playbook` (depends on all P1/P2 tools being correct), `get_decision_tree`
- **Anti-features confirmed:** no write tools, no semantic search, no live SAP RFC connection, no session state, no bulk content dump tools
- **KB structure enables direct parsing without a custom index:** Consistent YAML frontmatter for module/content_type routing. `tcodes.md` uses H3 headings per T-code. `config-spro.md` uses H2/H3 with structured SPRO Path sub-fields. `checklists.md` uses checkbox format. All P1 tools implementable with frontmatter filtering + section-level string parsing.

### From ARCHITECTURE.md

- **Two new files, no new directories:** `scripts/mcp_server.py` (FastMCP, tool definitions, `mcp.run(transport="stdio")`) and `scripts/kb_reader.py` (`parse_frontmatter`, `read_file`, `list_kb_files`). Everything else unchanged.
- **`validate.py` refactor:** `validate.py` already implements the exact `parse_frontmatter()` logic the server needs plus `VALID_MODULES`, `VALID_CONTENT_TYPES`, and `VALID_CONFIDENCE` constants. Move this into `kb_reader.py`; have both `validate.py` and `mcp_server.py` import from it. No code duplication, no changes to the validation CI.
- **`.mcp.json` at repo root:** Claude Code auto-discovers this at session start. Commit it. Format: `{"sap-kb": {"command": "python3", "args": ["/abs/path/scripts/mcp_server.py"]}}`. Verified against live `context7` `.mcp.json` on this machine.
- **On-demand file reads, no indexing:** At ~35 files, full-scan `search_kb` completes in under 200ms. No startup index, no stale data, no cache invalidation. Build in-memory index only if KB grows past ~200 files.
- **Content scope boundary:** `list_kb_files()` must explicitly whitelist `modules/`, `cross-module/`, `reference/`. Never walk `.claude/`, `.planning/`, or `scripts/`. Exposing `.claude/rules/` files as KB content would confuse the model — those are session configuration, not SAP knowledge.
- **Search-then-retrieve pattern:** `search_kb` returns excerpts (3-5 lines around each match + file path + module + confidence). Claude then calls `get_content` for the one or two specific files it needs. This is how Context7 and similar KB tools work. Never return full file bodies from a search call.

### From PITFALLS.md

**Top 5 critical pitfalls with prevention strategies:**

1. **Tool descriptions don't match LLM query routing.** Write descriptions as invocation conditions, not README sections. Include: the query pattern the tool handles, ECC 6 scope, what it does NOT cover. Test against 10 realistic queries using MCP Inspector before shipping.

2. **Full file content flooding tool responses.** Parse into sections; return targeted excerpts capped at 2000 tokens. The "lost in the middle" effect degrades answer quality when tool responses contain large amounts of irrelevant context. Never return full file bodies from `search_kb`.

3. **stdout contamination crashing the server silently.** Any `print()` / stdout write in stdio mode corrupts the JSON-RPC stream with no obvious error. Use `sys.stderr` for all logging from the first line of server code. Verify with `python mcp_server.py 2>/dev/null | head -5` — first lines must be valid JSON-RPC initialization.

4. **Tool granularity mismatch.** 4-8 tools is the sweet spot. Above 20 tools, LLM routing degrades. Below 4 (single `search_sap` approach), query quality is inconsistent. The 5 P1 tools sit comfortably in range.

5. **Breaking the existing CLAUDE.md loading path.** The MCP server is a read-only consumer. It never moves, renames, or transforms KB files. Verify both access paths (MCP tools and native file loading) independently after every server change.

**Additional notable pitfalls:** capability declaration must exactly match implementation (declare only `tools: {}`); validate all file path arguments against `KB_ROOT` to block path traversal (`os.path.realpath()` comparison, not string prefix); use `isError: true` in tool responses for errors, not unhandled exceptions.

---

## Implications for Roadmap

### Suggested Phase Structure

**Phase 1: Server Scaffold + All P1 Tools**

Build the minimal working server and deliver all 5 P1 tools together. Splitting P1 tools across phases adds no value — they share the same infrastructure (`kb_reader.py`, FastMCP setup, `.mcp.json`) and all have LOW implementation complexity.

Delivers: Working MCP server auto-discovered by Claude Code. All five highest-frequency query patterns covered. ECC/S4 disambiguation available as a tool call.

Features: `lookup_tcode`, `get_module_overview`, `get_config_path`, `get_process_flow`, `compare_ecc_s4`

Pitfalls to address in this phase:
- stdout contamination (enforce `sys.stderr` from line one; add linter/pre-commit check)
- Capability declaration mismatch (MCP Inspector test of `initialize` handshake before writing any tool code)
- Breaking existing CLAUDE.md path (establish "server is read-only" constraint before writing code)
- Tool descriptions written from technical perspective rather than LLM routing perspective (write descriptions first, test against 10 real queries before implementing handlers)
- Wrong primitive (Tools vs Resources): all query operations are Tools; do not expose files as Resources

Research flag: **Standard patterns — no phase research needed.** The FastMCP decorator pattern is well-documented. The KB file structure is fully known. Follow ARCHITECTURE.md directly.

---

**Phase 2: Validated P2 Tool Expansion**

Add P2 tools after observing real usage patterns from Phase 1. `search_by_keyword` is the most important addition — it serves as the fallback for queries the five P1 tools don't match. `get_integration_points` addresses cross-module posting questions (the second most common gap after T-code lookup). `lookup_movement_type` and `get_period_end_checklist` address operational MM/close queries.

Delivers: Full-text search fallback. Movement type + OBYC key data. Cross-module integration point catalog. Period-end close checklist for operational use.

Features: `search_by_keyword`, `lookup_movement_type`, `get_integration_points`, `get_period_end_checklist`

Pitfalls to address:
- Adding tools before Phase 1 gap patterns are visible (define a clear trigger: specific query types missed, not a calendar date)
- `search_by_keyword` returning full file bodies (enforce excerpt-only output; add response token size check)
- Total tool count: P1 (5) + P2 (4) = 9 tools — well within the safe range

Research flag: **Needs phase research for `get_integration_points`.** The `modules/{module}/integration.md` file structure and the `cross-module/mm-sd-integration.md` format should be reviewed before implementation to map the actual table structure to the tool's output schema. Read those files during phase planning.

---

**Phase 3: High-Value Synthesis Tools (v2)**

Defer until Phase 2 tools are stable and validated. These tools synthesize content from multiple KB files and have HIGH implementation complexity. `get_scenario_playbook` is the highest-value P3 tool (8 named playbooks: consignment, intercompany, third-party, subcontracting, split valuation, batch, serial) but depends on `lookup_tcode`, `get_process_flow`, and `get_integration_points` all being accurate and stable.

Delivers: Complete cross-module scenario walkthroughs. OBYC account determination decision chains. Decision trees for solutioning.

Features: `get_account_determination`, `get_scenario_playbook`, `get_decision_tree`, `resolve_routing`

Pitfalls to address:
- Building `get_account_determination` before `get_integration_points` data model is validated (these share OBYC key data)
- `get_scenario_playbook` token flooding — playbooks are large; must return structured sections, not full playbook body
- `get_decision_tree` requires parsing structured Q&A chains from `{module}-advanced.md` files; design the parser before the tool handler

Research flag: **Needs phase research for `get_account_determination`.** The OBYC decision chain spans `modules/mm/mm-advanced.md` and `modules/fi/account-determination.md`. The data model (movement type → valuation class → transaction key → account modifier → G/L account) must be designed before implementation. Run `/gsd:research-phase` for this tool specifically.

---

### Cross-Phase Constraints

- **Read-only invariant:** Every phase must preserve the existing CLAUDE.md file-loading path. Verify native loading still works after each phase delivery.
- **Tool count ceiling:** Stay below 15 tools total through Phase 2. If approaching 15, consolidate before adding more.
- **Response token budget:** All tools must return targeted excerpts, not full file bodies. Establish and enforce this in Phase 1 before it becomes a habit. Cap at 2000 tokens per tool response.
- **MCP Inspector gate:** No phase is done until all tools in that phase pass MCP Inspector testing with 10 representative queries each.
- **Path traversal protection:** Any tool accepting a file path argument must validate it against `KB_ROOT` using `os.path.realpath()`. Add this before Phase 1 ships.

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|------------|-------|
| Stack (Python + FastMCP) | HIGH | Python 3.14.2 runtime verified, PyYAML already installed, `validate.py` existing codebase inspected. FastMCP is official Python SDK. |
| Stack (TypeScript fallback) | HIGH | STACK.md verified all package versions against npm registry as of 2026-02-23. |
| Features (P1 tool set) | HIGH | Based on direct inspection of all 35 KB files. All P1 tools map to existing, consistently-structured KB files. Parsing approach is straightforward. |
| Features (P2 tool set) | MEDIUM | Reasonable inferences from KB structure. `get_integration_points` parsing complexity may vary once integration.md files are reviewed in detail. |
| Features (P3 tool set) | MEDIUM | Deferred for good reason — `get_account_determination` spans two files with complex logic. Estimate may shift after Phase 2 data model work. |
| Architecture patterns | HIGH | Verified against official MCP protocol docs, live inspection of `validate.py`, live `.mcp.json` format from context7 plugin on this machine. |
| Pitfalls | HIGH | Grounded in official MCP documentation (stdout contamination documented across all six language SDKs). Lost-in-the-middle effect grounded in Liu et al. 2024. |

**Overall confidence:** HIGH. All four research files converged on consistent recommendations. The Python vs TypeScript conflict was the only real disagreement, and it resolves clearly in favor of Python given the existing codebase.

---

## Gaps to Address During Planning

1. **`mcp` Python package version:** ARCHITECTURE.md recommends `mcp>=1.2.0`. Verify the exact current version on PyPI before writing `requirements.txt`. Pin the version explicitly — do not use a floor-only spec in production.

2. **Virtual environment decision:** No venv exists currently for the `scripts/` Python tools. Decide before Phase 1: `pip install --user mcp` vs `scripts/venv/` vs project-root `venv/`. This affects the absolute path in `.mcp.json` and the setup instructions.

3. **`get_process_flow` input normalization:** The tool accepts free-text aliases ("procure to pay") or codes ("P2P"). The mapping from aliases to actual file paths in `cross-module/` must be defined during Phase 1 planning. Check the actual file names before assuming the routing table.

4. **Phase 2 trigger definition:** The roadmap says "add P2 tools after observing Phase 1 gaps." This must be made concrete — specific query types that miss the P1 tools, or a defined number of sessions. Without a defined trigger, Phase 2 risks being delayed indefinitely or rushed too early.

5. **`compare_ecc_s4` topic coverage:** The tool accepts a `topic` string. The full list of topics covered by `.claude/rules/sap-disambiguation.md` and the "S/4HANA Differences" sections across all module files should be enumerated before implementation, to define what input values the tool handles and how to respond gracefully to unrecognized topics.

---

## Sources (Aggregated from Research Files)

### HIGH Confidence (verified sources)

- npm registry: `@modelcontextprotocol/sdk@1.27.0`, `zod@4.3.6`, `typescript@5.9.3`, `gray-matter@4.0.3`, `tsx@4.21.0`, `@types/node@25.3.0` — verified 2026-02-23
- https://modelcontextprotocol.io/docs/develop/build-server — Official MCP quickstart, TypeScript and Python paths
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools — MCP Tools specification
- https://modelcontextprotocol.io/specification/2025-11-25/server/resources — MCP Resources specification
- https://modelcontextprotocol.io/quickstart/server — Python FastMCP quickstart
- https://modelcontextprotocol.io/docs/develop/connect-local-servers — Local deployment, stdio transport
- https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices.md — Path traversal, scope minimization
- `/home/corye/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/context7/.mcp.json` — Live `.mcp.json` format reference on this machine
- `scripts/validate.py` — Existing frontmatter parsing, `VALID_MODULES`/`VALID_CONTENT_TYPES`/`VALID_CONFIDENCE` constants
- All 35 KB markdown files — Direct inspection for structure, frontmatter schema, content type consistency
- `python3 --version` — Runtime check confirming Python 3.14.2 at `/usr/bin/python3`
- Liu et al. 2024, "Lost in the Middle: How Language Models Use Long Contexts" — Context flooding degradation (peer-reviewed)
- MCP Build-a-Server Tutorial — stdout contamination warning explicitly documented for Python, TypeScript, Java, Kotlin, Rust, C#

---

*Research synthesis for: SAP ECC 6.0 Knowledge Base — MCP Server Layer (v1.1)*
*Synthesized: 2026-02-23*
*Ready for roadmap: Yes*
