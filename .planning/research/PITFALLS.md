# Pitfalls Research

**Domain:** Adding MCP Server Layer to an Existing Markdown Knowledge Base
**Researched:** 2026-02-23
**Confidence:** HIGH (critical pitfalls verified against official MCP protocol documentation)

---

## Context

This document covers pitfalls specific to the milestone of **adding an MCP server programmatic interface on top of the existing SAP ECC 6 markdown knowledge base**. It does not repeat content-quality pitfalls from the prior PITFALLS.md (ECC/S4 contamination, context overflow, etc.) — those remain valid and are assumed addressed.

The key constraint this milestone works around: the existing KB is optimized for Claude Code's native file-loading system (CLAUDE.md hierarchy, `.claude/rules/`, `@import` chains). The MCP layer must expose the same content through a different access path without breaking the existing access path or duplicating content.

---

## Critical Pitfalls

### Pitfall 1: Tool Descriptions That Don't Match How Users Actually Query

**What goes wrong:**
Tool descriptions are written from the server author's perspective ("queries the SAP ECC 6 knowledge base for module content") instead of from the LLM's perspective when routing a user query. The LLM reads tool descriptions to decide which tool to invoke. If the description doesn't match the surface form of real queries, the LLM either picks the wrong tool or calls none at all and falls back to training data.

**Why it happens:**
Server authors write descriptions to explain what the tool does technically, not to act as routing signals. Generic descriptions like "search SAP knowledge" don't signal to the model when to use `search_sap_module` vs `get_sap_tcode` vs `lookup_sap_config` — or whether any tool is appropriate at all.

**How to avoid:**
Write tool descriptions as if they are the first sentence the LLM will read when deciding whether to invoke the tool. Include:
- The query pattern the tool handles ("Use this when the user asks about a specific T-code, transaction, or menu path")
- The module scope covered ("Covers MM, SD, FI, CO modules in SAP ECC 6.0 only")
- What it does NOT handle ("Does not cover S/4HANA — for ECC 6 only")

Test each tool description against 10 realistic user queries and verify the LLM routes them correctly using MCP Inspector before considering the tool design complete.

**Warning signs:**
- Tool description reads like a README section, not an invocation condition
- Multiple tools with overlapping descriptions (LLM will pick arbitrarily)
- No mention of what query types the tool is designed for
- Description omits the ECC 6 scope boundary

**Phase to address:**
Tool design phase (before any implementation). Description quality cannot be retrofitted without changing the tool's surface area.

---

### Pitfall 2: Returning Full File Content Instead of Relevant Excerpts

**What goes wrong:**
A tool fetches and returns entire markdown files (e.g., the full `modules/mm/tcodes.md` at 3000+ tokens) when the user asked about one T-code. The MCP tool response floods the LLM's context with irrelevant content, which both wastes context budget and degrades response quality via the lost-in-the-middle effect.

**Why it happens:**
The simplest implementation of a "read knowledge base file" tool is `read_file(path)` → return full content. This works in demos but fails in practice. The existing KB was designed for progressive loading by a routing layer (CLAUDE.md hierarchy). Bypassing that routing and dumping raw file content through MCP loses the curation that makes the KB useful.

**How to avoid:**
Tools must return targeted content, not full files. Strategies:
- Parse the markdown into sections (by `##` headings) and return only the matching section
- For T-code lookups: parse the T-code table and return the single matching row plus its context paragraph
- For process queries: return the specific process section plus the integration points section
- Cap tool response at 2000 tokens; if more is needed, return a summary with an offer to provide details

The MCP tool response is context that the LLM receives — treat it with the same token discipline as the files themselves.

**Warning signs:**
- Tool response size regularly exceeds 1500 tokens
- Tool response includes table-of-contents, frontmatter, and metadata sections that weren't asked for
- Users report that the LLM's answers are correct but verbose, with irrelevant module details included

**Phase to address:**
Tool implementation phase. Design the content extraction logic before writing any tool handler.

---

### Pitfall 3: STDIO stdout Contamination Crashing the Server

**What goes wrong:**
Any `console.log()`, `print()`, or standard output write in a STDIO-transport MCP server corrupts the JSON-RPC message stream. The protocol uses stdout exclusively for JSON-RPC communication. A single debug log line written to stdout during startup or tool execution renders the server non-functional — the client receives malformed JSON and drops the connection.

**Why it happens:**
This is the single most common mistake in MCP server implementations, documented explicitly across all language SDKs (Python, TypeScript, Java, Kotlin, Rust, C#). Developers habitually add debug logging to stdout during development and forget to remove it. In STDIO transport, there is no way to recover from this — the entire JSON-RPC framing breaks.

**How to avoid:**
From the first line of server code, configure all logging to stderr or a log file. Never stdout.

```python
# Python — WRONG
print("Server starting...")  # corrupts JSON-RPC stream

# Python — CORRECT
import sys
print("Server starting...", file=sys.stderr)

# Or use logging module (writes to stderr by default)
import logging
logging.info("Server starting...")
```

```typescript
// TypeScript — WRONG
console.log("Server starting...");

// TypeScript — CORRECT
console.error("Server starting...");
```

Enforce this with a linter rule or pre-commit hook that fails if stdout write calls appear in server code outside of the MCP SDK's transport layer.

**Warning signs:**
- MCP server starts but the client reports "connection failed" or "malformed response"
- Server works in HTTP transport mode but not STDIO
- Debug output visible intermixed with JSON in server logs
- Any `console.log` / `print` / `System.out.println` / `println!` in server code

**Phase to address:**
Server scaffolding phase (first implementation). Add the linter rule before writing any tool code.

---

### Pitfall 4: Tool Granularity Mismatch — Too Coarse OR Too Fine

**What goes wrong:**
**Too coarse:** A single `search_sap` tool that accepts any query string forces the LLM to decide what to look for and how to phrase the query for maximum recall — the LLM is now doing retrieval work it isn't optimized for. Results are inconsistent.

**Too fine:** 40+ tools (one per file, one per module section, one per T-code lookup type) overwhelms the LLM's tool selection. The LLM either picks the wrong tool from a long list or hallucinates a tool name. Research and documentation confirm LLMs struggle when presented with more than ~15-20 tools simultaneously.

**Why it happens:**
Authors either model the tool surface after the file structure (too fine) or try to create one universal tool that mirrors "search anything" (too coarse). Neither maps to how users actually query — which is by topic category (T-codes, config paths, process flows, integration points, troubleshooting).

**How to avoid:**
Design 4-8 tools mapped to query intent categories that exist in this KB:
- `get_tcode_info` — for "what does T-code X do" or "what T-code do I use for Y"
- `get_spro_config_path` — for "how do I configure X in SPRO/IMG"
- `get_process_flow` — for "what's the process for X" or "how does P2P work"
- `get_integration_points` — for "how does MM post to FI" / "what happens in FI when..."
- `get_master_data_info` — for "what fields are in the material master / vendor master"
- `search_module` — fallback for general queries within a specified module

Each tool maps to a distinct question type. This keeps the tool list small enough for reliable LLM routing while keeping tools targeted enough for high-quality responses.

**Warning signs:**
- Tool list has more than 20 entries
- Multiple tools with nearly identical descriptions
- A single tool accepts a free-text query with no constraints on what it returns
- Users report the LLM frequently picks the wrong tool or calls no tool

**Phase to address:**
Tool design phase. Enumerate the 10 most common question patterns against this KB first, then design tools to cover those patterns.

---

### Pitfall 5: Breaking the Existing CLAUDE.md File-Loading Path

**What goes wrong:**
The MCP server is implemented in a way that changes, moves, or interferes with the existing `.claude/rules/` files, `CLAUDE.md` hierarchy, or file paths that the native Claude Code loading system relies on. The MCP layer is supposed to be additive — a new access path — but the implementation accidentally breaks the existing access path that current users depend on.

**Why it happens:**
The server needs to know where the KB files are. Developers hardcode absolute paths, restructure the directory layout to fit the server's expectations, or rename files to something the server can index more easily. Any of these breaks the `@import` references and `.claude/rules/` routing that the existing CLAUDE.md hierarchy uses.

**How to avoid:**
The MCP server must treat the KB directory as read-only from its perspective. The server reads files; it never moves, renames, or restructures them. Configuration paths in the server point to the existing directory layout, not a copy or transformation of it.

Concrete rules:
- Server config takes a `KB_ROOT` path; all file reads are relative to this root
- No preprocessing step that generates a new file layout
- No `index.json` or `embeddings.db` that replaces or supplements the existing `CLAUDE.md` routing
- The `scripts/validate.py` and `.claude/rules/` files remain untouched
- Test both access paths independently after any server change

**Warning signs:**
- Server implementation includes a "build step" that copies or transforms KB files
- Any PR that modifies files in `.claude/rules/` or `CLAUDE.md` files as part of the MCP work
- Absolute paths hardcoded in server config
- The server's file discovery logic reimplements what CLAUDE.md hierarchy already does

**Phase to address:**
Server design phase. Establish the "server is read-only consumer of existing layout" constraint before any code is written.

---

### Pitfall 6: Capability Declaration Mismatch at Protocol Initialization

**What goes wrong:**
The server claims capabilities it doesn't implement (e.g., declares `resources` support but never implements `resources/list` or `resources/read`), or doesn't declare capabilities it does implement (e.g., exposes tools but omits `tools` from the capability object). The MCP protocol requires capability negotiation during initialization — the client uses declared capabilities to decide what to call. Mismatches cause silent failures or confusing "method not found" errors.

**Why it happens:**
Capability declaration is done once during server initialization and is easy to copy from an example without matching it to the actual implementation. The protocol is permissive enough that some clients won't fail loudly — they'll just never call capabilities that weren't declared, silently degrading functionality.

**How to avoid:**
Capabilities declared in the `initialize` response MUST exactly match what the server handles. Use this checklist:
- Implementing tools? → declare `"tools": {}` (add `"listChanged": true` only if you support notifications)
- Implementing resources? → declare `"resources": {}` and implement both `resources/list` and `resources/read`
- Implementing prompts? → declare `"prompts": {}` and implement `prompts/list` and `prompts/get`

For a markdown KB server, the minimal correct declaration is likely:
```json
{
  "capabilities": {
    "tools": {}
  }
}
```

Do not declare `resources` or `prompts` unless fully implemented. Verify with MCP Inspector after every server change.

**Warning signs:**
- Client connects but some tools/resources never get called even for relevant queries
- "Method not found" errors in server logs for operations the client tries to call
- Server declares `listChanged: true` but never sends notifications when files change
- Capability object copied from a different server's example code without review

**Phase to address:**
Server scaffolding phase. Verify capability declaration matches implementation before adding any tool code.

---

### Pitfall 7: Confusing Tools, Resources, and Prompts — Using the Wrong Primitive

**What goes wrong:**
The SAP KB content gets implemented as MCP tools when it should be resources (or vice versa), creating poor UX and misaligned protocol semantics. Specifically: exposing every KB file as a separate MCP tool ("tool: read_mm_tcodes", "tool: read_fi_processes") rather than as resources, or trying to implement query capabilities as resources when they require tool-level execution.

**Why it happens:**
The three MCP primitives have distinct semantics that aren't obvious from a quick read:
- **Tools** are model-invoked, action-oriented, take arguments, do computation (query a KB, look up a T-code)
- **Resources** are application-driven, data-oriented, expose URI-addressable content (a KB file at `sap://mm/tcodes`)
- **Prompts** are user-initiated templates that structure LLM interactions

Most KB server use cases fit tools (query and retrieve relevant content). Exposing raw files as resources works but requires the client to have resource-reading UI — Claude Code supports this, but the LLM won't automatically use resources the way it uses tools.

**How to avoid:**
For this KB, implement **tools for all query operations** (where the LLM decides when and what to query) and optionally expose **resources for direct file access** (where a human explicitly wants to read a specific file). Do not implement prompts unless you are building reusable query templates for common SAP workflows.

Decision table:
- "User asks what T-code to use for X" → tool
- "User wants to read the full MM tcodes.md file" → resource (or tool with a file path argument)
- "User wants a structured template for 'design a P2P process'" → prompt (optional)

**Warning signs:**
- All KB content exposed only as resources with no tools — LLM won't automatically query the KB
- 50+ resources declared (one per file) with no tools — client can't present these usefully
- Tools that take no arguments and just return static file content — these are resources, not tools

**Phase to address:**
Tool design phase. Clarify the primitive mapping before writing any handler code.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Returning full file content from every tool | Simpler implementation, no parsing code | Context flooding, poor answer quality, high token cost per query | Never — always extract relevant sections |
| Hardcoded file paths in server config | Faster setup, no config needed | Breaks when KB moves or is used on different machines | Never in production; acceptable in local dev with clear documentation |
| Single `search_sap` tool with free-text query | Minimal tool surface, easy to explain | LLM must figure out how to query effectively; inconsistent results | Only if you add substantial query routing logic inside the tool |
| Skipping MCP Inspector testing during dev | Faster iteration | Capability mismatches, stdout contamination go undetected until deployment | Never — Inspector testing costs 30 minutes and catches critical issues |
| Copying tool descriptions from another server's README | Faster authoring | Descriptions don't match this KB's actual content; LLM routing fails | Never — descriptions must match this KB's query patterns |
| Building an indexing/embedding layer before validating simple file reads | Feels more "production-ready" | Adds infrastructure complexity before knowing if simpler approach is sufficient | Defer until simple file reads are proven insufficient |

---

## Integration Gotchas

Common mistakes when connecting the MCP server to the existing markdown KB.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| KB file discovery | Traversing the directory tree with a generic glob and treating all `.md` files as KB content | Respect the existing structure: use the CLAUDE.md files as indexes, read the `## Files` sections, mirror the routing logic already defined in `.claude/rules/sap-routing.md` |
| YAML frontmatter | Ignoring frontmatter when returning content, stripping it from responses | Read `confidence:` and `last_verified:` fields from frontmatter; include confidence level in tool responses so LLM can caveat low-confidence answers |
| Cross-file references | Not following `@import` chains and `related:` frontmatter when a query spans multiple files | When a query hits a file with `related:` references, fetch and include the related section if it's directly relevant (but cap total response tokens) |
| Markdown tables | Returning markdown table syntax as raw text assuming the client will render it | For STDIO/Claude Code clients, raw markdown table syntax is fine — Claude renders it. For other clients, test whether markdown is rendered or shown as syntax |
| File encoding | Assuming all files are ASCII | Files may contain SAP-specific characters (umlauts in German module names, special symbols in T-code descriptions). Use UTF-8 throughout |
| Validation scripts | MCP server breaking when `scripts/validate.py` runs and modifies files | Server should never write to the KB directory; validate scripts are fine to run concurrently |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Reading all KB files into memory at startup | Slow server start, high memory usage | Load files on demand when a tool is called, not at initialization | At 50+ files, startup takes several seconds; at 200+ files, memory pressure on constrained systems |
| No response caching for repeated identical queries | Same file read from disk on every "what is T-code ME21N" query | Cache file content in memory with a simple dict; invalidate on file change detection | Noticeable at 10+ queries/minute in shared-use deployments |
| Synchronous file I/O in async tool handlers | Tool calls block the event loop; other requests queue up | Use async file I/O (`asyncio` in Python, async/await in TypeScript) for all file reads | Becomes problematic with concurrent users; immediate issue if any file read is slow |
| Building a vector search index on every startup | 30-60 second startup delay before server is usable | Build index once, persist to disk, reload on startup | On every restart; prohibitive in development where restarts are frequent |

Note: for individual-developer use of this KB, all four traps are tolerable at current KB size (~50 files). These become real concerns only for org-wide deployment with concurrent users.

---

## Security Mistakes

Domain-specific security issues for a local markdown KB server.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Accepting arbitrary file path arguments in tools (e.g., `get_file(path: str)`) | Path traversal attack — caller can read any file on the system with `../../etc/passwd` | Validate all paths against `KB_ROOT`; reject any path that resolves outside `KB_ROOT`; use `os.path.realpath()` comparison, not string prefix matching |
| Writing stdout from STDIO server (even accidentally) | Corrupts JSON-RPC stream; attacker who controls tool input might inject content | Never write to stdout; all logging to stderr; tool response content is only what the server explicitly constructs |
| Exposing the server on a TCP port without authentication | Any process on the local machine can call the server | For individual use: STDIO transport only (no TCP). For shared use: Streamable HTTP with authentication token |
| Not validating tool input schema before execution | Malformed input causes unhandled exceptions that leak stack traces | Use the SDK's schema validation; reject malformed arguments with a protocol-level error response, not an uncaught exception |

Note: this KB contains only ECC 6 reference documentation — no credentials, no internal system data, no PII. Security risk is low for a local single-user deployment. Risks increase for org-wide shared deployments.

---

## UX Pitfalls

Common user experience mistakes that prevent adoption.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Server not available in Claude Code because config JSON has a syntax error | Users who can't debug JSON silently never get MCP working; they assume it "doesn't work" | Provide a tested, copy-pasteable config snippet in the README; include a validation step in the setup instructions |
| Server crashes silently — user sees "tool failed" with no explanation | Users stop trusting the tool; fall back to asking Claude without MCP | Tool execution errors must return `isError: true` with a descriptive message, not crash the server. Catch all exceptions in tool handlers |
| Server works in dev but fails after restart because absolute paths changed | Users in different environments (different home directories, Windows vs Linux paths) can't reproduce a working setup | Use environment variables or a config file for `KB_ROOT`; document the setup clearly; test on a clean machine |
| All KB queries return the same generic "I found this in the SAP knowledge base" prefix | Users can't tell which file the content came from; can't verify or dig deeper | Include the source file path and frontmatter confidence in every tool response. Example: `[Source: modules/mm/tcodes.md | Confidence: HIGH | Verified: 2026-02-17]` |
| Tool called but returns an error when the KB has relevant content | Erodes trust rapidly — users conclude the tool doesn't know SAP | Log all tool calls and misses; audit the 10 most-missed queries and improve tool descriptions or content coverage accordingly |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Server starts without errors:** Verify startup doesn't write to stdout. Run `python server.py 2>/dev/null | head -5` and confirm the first 5 lines are valid JSON-RPC initialization, not log output.
- [ ] **All declared capabilities are implemented:** Use MCP Inspector to call `tools/list`, `resources/list`, `prompts/list` — every declared capability must return a valid response, not "method not found."
- [ ] **Tool descriptions are tested, not assumed:** Run 10 realistic SAP queries through an LLM with the tool list and confirm the correct tool is selected each time before shipping.
- [ ] **Tool responses are bounded:** Check that no tool response exceeds 2000 tokens under normal usage. Log response sizes in development.
- [ ] **Path traversal is blocked:** Attempt `../../../etc/passwd` as a file path argument. Server must return an error, not file contents.
- [ ] **Existing CLAUDE.md path still works:** After adding MCP, verify that using Claude Code natively (without MCP) still loads the KB correctly via the CLAUDE.md hierarchy.
- [ ] **Error handling returns `isError: true`:** Introduce a deliberate error (request a non-existent T-code) and verify the tool response uses `isError: true` with a helpful message, not an unhandled exception.
- [ ] **Server restarts cleanly:** Kill and restart the server 3 times and confirm it reconnects without residual state issues.

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| stdout contamination discovered in production | LOW | Add `file=sys.stderr` to all print calls; restart server. 30 minutes. |
| Tool descriptions cause wrong tool selection | MEDIUM | Rewrite descriptions iteratively using MCP Inspector to test each revision. 2-4 hours for thorough testing. |
| Full file content flooding responses | MEDIUM | Implement section extraction in tool handlers; add token cap guard. 4-8 hours if file structure is consistent. |
| Existing CLAUDE.md hierarchy broken by server changes | HIGH | Do not modify KB files during server development. If already broken: git diff to identify changed files, revert to last good state, then redo server changes without touching KB files. Hours to days depending on extent. |
| Too many tools causing LLM routing failures | MEDIUM | Consolidate tools: combine tools with overlapping patterns into one with a `query_type` enum parameter. 4-8 hours plus re-testing. |
| Server fails across environments due to hardcoded paths | LOW | Replace hardcoded paths with environment variable `SAP_KB_ROOT`; add to setup documentation. 1-2 hours. |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Tool descriptions don't match query patterns | Phase 1: Tool design | Test 10 real queries through the tool list before any implementation begins |
| Full file content flooding | Phase 2: Tool implementation | Check response token sizes for the 5 largest KB files; all must return targeted excerpts |
| STDIO stdout contamination | Phase 1: Server scaffolding | Run linter check for stdout write calls; test with MCP Inspector before writing any tool handler |
| Tool granularity mismatch | Phase 1: Tool design | Design tool list on paper first; validate against common query patterns before coding |
| Breaking existing CLAUDE.md path | Phase 1: Architecture constraint | Establish "server is read-only" rule; verify native loading still works after every PR |
| Capability declaration mismatch | Phase 1: Server scaffolding | MCP Inspector test of `initialize` handshake and capability-matching tool calls |
| Wrong primitive (tool vs resource vs prompt) | Phase 1: Tool design | Classify each planned server operation using the primitive decision table above before coding |
| Path traversal in file tools | Phase 2: Tool implementation | Automated test: attempt path traversal in each tool that accepts a path argument |
| Server config friction blocking adoption | Phase 3: Deployment | Write setup docs with copy-pasteable config; test on a clean machine before releasing |

---

## Org-Wide vs Individual Deployment Pitfalls

Most pitfalls above apply to both deployment scopes. These are specific to org-wide deployment.

**Org-wide only:**

- **Shared server concurrency:** A single STDIO server serves one client. For org-wide shared access, use Streamable HTTP transport. Do not use STDIO for multi-user. This requires authentication (bearer token minimum), rate limiting, and session management.

- **Stale content in shared cache:** If the shared server caches file content and one user updates a KB file, other users see stale content until the cache invalidates. Use file modification time (`mtime`) as cache invalidation signal, or disable caching for small KBs.

- **Scope creep under org pressure:** Org deployments attract "can you also add X" requests that belong in the KB content layer, not the MCP tool layer. "Add a tool that answers SAP payroll questions" is a content gap, not a tool design problem. Push content additions back to the KB files; the tools should remain stable query interfaces.

---

## Sources

- [MCP Official Documentation — Tools](https://modelcontextprotocol.io/docs/concepts/tools) — Tool definition, input schema, error handling, security requirements (HIGH confidence, official spec)
- [MCP Official Documentation — Resources](https://modelcontextprotocol.io/docs/concepts/resources) — Resource URI conventions, annotation semantics, binary vs text content (HIGH confidence, official spec)
- [MCP Official Documentation — Prompts](https://modelcontextprotocol.io/docs/concepts/prompts) — Prompt primitives, when to use vs tools/resources (HIGH confidence, official spec)
- [MCP Official Documentation — Architecture](https://modelcontextprotocol.io/docs/concepts/architecture) — STDIO vs Streamable HTTP transport, capability negotiation, lifecycle (HIGH confidence, official spec)
- [MCP Build-a-Server Tutorial](https://modelcontextprotocol.io/docs/develop/build-server.md) — Stdout contamination warning explicitly documented for Python, TypeScript, Java, Kotlin, Rust, C# (HIGH confidence, official)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices.md) — Path traversal risks, token passthrough anti-pattern, scope minimization, session hijacking (HIGH confidence, official)
- [Lost in the Middle: How Language Models Use Long Contexts — Liu et al., 2024](https://arxiv.org/abs/2307.03172) — Context window token flooding degradation (HIGH confidence, peer-reviewed)
- Existing `.planning/research/PITFALLS.md` in this repository — Prior KB content pitfalls (context for what is already addressed vs new concerns)

---

*Pitfalls research for: MCP server layer over SAP ECC 6 markdown knowledge base*
*Researched: 2026-02-23*
