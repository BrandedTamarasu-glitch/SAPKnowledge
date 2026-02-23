# Architecture Research

**Domain:** MCP Server over a flat-file markdown knowledge base (SAP ECC 6.0)
**Researched:** 2026-02-23
**Confidence:** HIGH

> This file supersedes the v1.0 ARCHITECTURE.md (flat-file KB architecture). v1.1 adds an MCP server layer on top of the existing KB. The flat-file KB structure documented in v1.0 is unchanged and remains the source of truth.

---

## Standard Architecture

### System Overview

```
+---------------------------------------------------------------------+
|                         MCP Client Layer                             |
|   +------------------+          +------------------------------+    |
|   |   Claude Code    |          |   Claude Desktop             |    |
|   |  (.mcp.json or   |          |  (claude_desktop_config.json)|    |
|   |   mcpServers)    |          |                              |    |
|   +--------+---------+          +--------------+---------------+    |
+------------|-----------------------------------------|---------------+
             |  stdio (JSON-RPC 2.0)                   |  stdio (JSON-RPC 2.0)
             v                                         v
+---------------------------------------------------------------------+
|                       MCP Server Process                             |
|                    scripts/mcp_server.py                             |
|                                                                      |
|   +--------------------------------------------------------------+  |
|   |  FastMCP instance -- tool registry, request dispatch         |  |
|   +--------------------------------------------------------------+  |
|                                                                      |
|   +--------------+  +--------------+  +--------------+             |
|   |  search_kb   |  |  get_content |  | lookup_tcode |             |
|   |  @mcp.tool() |  |  @mcp.tool() |  |  @mcp.tool() |             |
|   +------+-------+  +------+-------+  +------+-------+             |
|          |                 |                  |                      |
|   +------+-----------------+------------------+---------------+     |
|   |         kb_reader.py -- KB I/O utilities                  |     |
|   |  parse_frontmatter()  |  read_file()  |  list_kb_files()  |     |
|   +------------------------------------------------------------+     |
+-----------------------------+---------------------------------------+
                              |  os.path / open() -- on-demand file I/O
                              v
+---------------------------------------------------------------------+
|                       KB File System (disk)                          |
|                                                                      |
|  modules/mm/       modules/sd/       modules/fi/       modules/co/  |
|  +- tcodes.md      +- tcodes.md      +- tcodes.md      +- tcodes.md |
|  +- processes.md   +- processes.md   +- processes.md   +- processes  |
|  +- integration.md +- integration.md +- integration.md +- integrat. |
|  +- mm-advanced.md +- sd-advanced.md +- fi-advanced.md +- co-adv.md |
|  +- ...            +- ...            +- ...            +- ...       |
|                                                                      |
|  cross-module/                   reference/                         |
|  +- record-to-report.md          +- movement-types.md               |
|  +- mm-sd-integration.md         +- document-types.md               |
|  +- checklists.md                +- ...                             |
|  +- playbooks.md                                                     |
|  +- design-patterns.md                                               |
+---------------------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `scripts/mcp_server.py` | MCP server entry point; registers tools; runs stdio transport loop | Python, `FastMCP` class, `@mcp.tool()` decorators, `mcp.run(transport="stdio")` |
| `scripts/kb_reader.py` | KB I/O layer; parses YAML frontmatter; enumerates KB files; reads bodies | Python, PyYAML (already a dependency); logic extracted from `validate.py` |
| `search_kb` tool | Full-text keyword search across all KB files; returns ranked excerpts | Iterates all KB files, searches body text, returns (file, module, content_type, excerpt, confidence) per match |
| `get_content` tool | Retrieves the full body of one file by module + content_type | Single targeted file read via frontmatter-index lookup |
| `lookup_tcode` tool | Finds the definition and context of a specific SAP transaction code | Searches tcodes.md and advanced files for the T-code string with 3-line context window |
| `list_modules` tool | Returns the inventory of all KB files with module, content_type, and confidence | Reads frontmatter from all KB files without loading their bodies |
| KB files (disk) | Source of truth for all SAP ECC 6.0 knowledge | Flat markdown with YAML frontmatter; read-only at runtime; never modified by the server |

---

## Recommended Project Structure

```
SAPKnowledge/
+-- scripts/
|   +-- mcp_server.py        # MCP server entry point -- FastMCP, tool definitions
|   +-- kb_reader.py         # KB I/O utilities -- parse_frontmatter, read_file, list_kb_files
|   +-- validate.py          # Existing validation script (unchanged; share parse_frontmatter with kb_reader)
|   +-- requirements.txt     # Add mcp>=1.2.0 alongside existing PyYAML>=6.0
+-- modules/
|   +-- mm/                  # MM module KB files (unchanged)
|   +-- sd/                  # SD module KB files (unchanged)
|   +-- fi/                  # FI module KB files (unchanged)
|   +-- co/                  # CO module KB files (unchanged)
+-- cross-module/            # Cross-module KB files (unchanged)
+-- reference/               # Reference lookup tables (unchanged)
+-- .mcp.json                # Claude Code MCP registration (new file, committed to repo)
+-- .planning/               # Planning and research (unchanged)
```

### Structure Rationale

- **`scripts/mcp_server.py` in `scripts/`:** Keeps the server alongside the existing `validate.py`. No new top-level directories needed. Consistent with the existing scripts-for-tooling convention.
- **`scripts/kb_reader.py` as a separate module:** Isolates KB I/O from the MCP protocol layer. `validate.py` already parses frontmatter with PyYAML. `kb_reader.py` extracts and extends that logic so it is importable by the server without duplicating code or modifying the validator.
- **`.mcp.json` at repo root:** Claude Code looks for `.mcp.json` in the project root at session start. Committing it to the repo means every Claude Code session on this machine auto-discovers the server without any manual config step.
- **KB files untouched:** The server is read-only. No KB file is modified, renamed, or relocated at runtime.

---

## Architectural Patterns

### Pattern 1: On-Demand File Reads (No Indexing)

**What:** The server reads files from disk on every tool call. There is no in-memory index, SQLite database, or pre-built search structure. Each `search_kb` call opens and reads all ~35 KB files; each `get_content` call opens one file.

**When to use:** KB has ~35 files, each under 5,000 tokens, total on-disk size under 300KB. On-demand reads at this scale complete in under 100ms. No startup latency, no index maintenance, no stale data.

**Trade-offs:**
- Pro: Zero state management. Server restarts instantly. No cache invalidation when KB files are edited.
- Pro: Any KB file edit is reflected immediately in the next tool call.
- Con: Does not scale beyond ~500 files before search latency becomes noticeable. At that point, build a simple in-memory index at server startup.

**Example:**
```python
import os

KB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIRS = ["modules", "cross-module", "reference"]

def list_kb_files() -> list[str]:
    """Return absolute paths of all .md files under content directories."""
    paths = []
    for d in CONTENT_DIRS:
        base = os.path.join(KB_ROOT, d)
        for root, _, files in os.walk(base):
            for f in files:
                if f.endswith(".md"):
                    paths.append(os.path.join(root, f))
    return paths
```

---

### Pattern 2: Frontmatter-Filtered Retrieval

**What:** Every KB file has a YAML frontmatter block with `module`, `content_type`, `confidence`, and `last_verified` fields. The server parses this block without reading the entire file body to support `list_modules` and to route `get_content` requests.

**When to use:** Any time the tool input includes a `module` or `content_type` parameter. Filtering by frontmatter lets the server answer "give me the MM processes file" without full-text searching the body.

**Trade-offs:**
- Pro: Low-cost targeted retrieval. Parse frontmatter of all 35 files, skip body reads for non-matching files.
- Pro: `confidence: low` files can be flagged in tool responses, alerting the model to verify content.
- Con: Requires consistent frontmatter across all KB files. The existing `validate.py` enforces this via CI.

**Example:**
```python
import yaml

def parse_frontmatter(filepath: str) -> tuple[dict, str]:
    """Return (metadata_dict, body_str) from a KB markdown file with YAML frontmatter."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    meta = yaml.safe_load(content[3:end])
    body = content[end + 3:].lstrip("\n")
    return meta or {}, body
```

This is the same logic already in `validate.py`. `kb_reader.py` is the authoritative home; `validate.py` should import it.

---

### Pattern 3: Tools as the Primary MCP Primitive

**What:** The server exposes all KB access as MCP Tools (`@mcp.tool()`). Tools are model-invocable — Claude decides when to call them. This contrasts with MCP Resources (app-controlled, passive) or Prompts (user-invoked templates).

**When to use:** The primary consumer is Claude (the model). The model needs to decide whether to query the KB, which query to issue, and how to use the result. Tools enable that autonomy.

**Trade-offs:**
- Pro: Claude can chain tool calls. `list_modules` to find the right file, then `get_content` to read it.
- Pro: Tool input/output is typed JSON, making responses predictable and parseable.
- Con: Every KB access incurs a round-trip tool call. Acceptable for a local stdio server where round-trips are sub-millisecond.

**Example:**
```python
from mcp.server.fastmcp import FastMCP
from kb_reader import parse_frontmatter, list_kb_files

mcp = FastMCP("SAP ECC 6.0 Knowledge Base")

@mcp.tool()
def get_content(module: str, content_type: str) -> str:
    """Return the full body of a KB file by module and content_type.

    Args:
        module: One of mm, sd, fi, co, cross-module, reference
        content_type: e.g. processes, tcodes, integration, config-spro
    """
    for path in list_kb_files():
        meta, body = parse_frontmatter(path)
        if meta.get("module") == module and meta.get("content_type") == content_type:
            confidence = meta.get("confidence", "unknown")
            return f"[Confidence: {confidence}]\n\n{body}"
    return f"No KB file found for module={module}, content_type={content_type}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## Data Flow

### Request Flow: search_kb

```
Claude decides to query KB for "how does GR/IR clearing work"
    |
    | tools/call {"name": "search_kb", "arguments": {"query": "GR/IR clearing"}}
    | (JSON-RPC 2.0 over stdin pipe)
    v
mcp_server.py -- FastMCP dispatches to search_kb handler
    |
    v
kb_reader.list_kb_files() --> [~35 absolute paths]
    |
    v
For each path:
    kb_reader.parse_frontmatter(path) --> (meta, body)
    body.lower().find(query.lower()) --> match? extract 3-line excerpt
    |
    v
Ranked list of (file_path, module, content_type, excerpt, confidence)
    |
    v
Serialize to JSON string --> write to stdout (JSON-RPC 2.0 response)
    |
Claude receives tool result, calls get_content for the best match
```

### Request Flow: get_content

```
Claude calls get_content(module="mm", content_type="integration")
    |
    v
kb_reader.list_kb_files() --> iterate until frontmatter matches
    |
    v
parse_frontmatter(matching_path) --> (meta, body)
Prepend "[Confidence: high]" header
Return full body (~2,000-8,000 tokens)
    |
    v
stdout --> Claude reads full file content and answers the user
```

### Request Flow: lookup_tcode

```
Claude calls lookup_tcode(tcode="MMPV")
    |
    v
kb_reader.list_kb_files()
--> filter to files where content_type in ("tcodes", "processes", "integration", "checklists")
    |
    v
For each candidate file:
    search body text for "\bMMPV\b" with 3-line context window
    |
    v
Return all matches: [{source_file, module, context_lines}]
    Multiple files may reference the same T-code (e.g., MMPV appears in
    mm/integration.md AND cross-module/checklists.md)
```

### Key Data Flows

1. **Frontmatter-first filtering:** For `get_content` and `list_modules`, frontmatter is parsed across all files but body text is read only for matching files. This minimizes I/O for targeted retrieval.
2. **Full-scan for search:** `search_kb` reads all file bodies. Acceptable at ~35 files (~200ms worst case). If KB grows to hundreds of files, pre-compute an in-memory index at startup.
3. **Confidence surfacing:** Every response includes the `confidence` field from frontmatter. This lets Claude tell the user when content is `low` confidence and needs external verification.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Current (~35 files, 1 local user) | On-demand reads. No indexing. No caching. Single Python process over stdio. |
| Medium (~200 files, 1 local user) | Add in-memory index built at server startup: dict mapping (module, content_type) to path; simple inverted index of lowercase tokens to [paths]. Startup cost ~50ms. |
| Large (~500+ files, multiple concurrent users) | Switch from stdio to HTTP/SSE transport. Add sqlite FTS5 search index. Use async I/O. Consider separate search worker. |

### Scaling Priorities

1. **First bottleneck:** `search_kb` latency grows linearly with file count. Fix: build an inverted token index at startup, invalidate entries when files are modified (use file mtime comparison on each request or inotify).
2. **Second bottleneck:** Multiple concurrent users. The stdio transport is inherently single-client. Fix: switch to HTTP/SSE transport and a basic process pool or async handler.

For v1.1 (single local user, ~35 files), neither bottleneck applies. Do not pre-optimize.

---

## Anti-Patterns

### Anti-Pattern 1: Writing to stdout in the server process

**What people do:** Use `print()` for debug messages or status output while running the stdio MCP transport.

**Why it's wrong:** The MCP stdio transport uses stdout as the exclusive JSON-RPC communication channel. Any non-JSON content written to stdout corrupts the protocol stream, causing the client to fail with a silent parse error that is difficult to diagnose.

**Do this instead:** Use `sys.stderr` for all logging. In development, redirect stderr to a file: `python3 mcp_server.py 2>>server.log`. The MCP SDK also provides a structured `send_log_message` facility for surfacing logs through the protocol itself.

---

### Anti-Pattern 2: Module-level side effects (indexing at import time)

**What people do:** Build a search index or read KB files at module import time: `INDEX = build_index()` at the top of `mcp_server.py`.

**Why it's wrong:** MCP clients may import the server module to introspect its tools without starting the full server runtime. Module-level I/O causes errors when `KB_ROOT` is unset, the working directory is wrong, or files are missing. It also prevents unit testing without a full KB on disk.

**Do this instead:** Initialize lazily inside tool handlers or in an explicit startup hook. Keep module-level code to constant definitions and function declarations.

---

### Anti-Pattern 3: Exposing `.claude/rules/` files as MCP content

**What people do:** Walk the entire repo directory tree and expose every `.md` file as a retrievable document.

**Why it's wrong:** The `.claude/rules/` files (sap-routing.md, sap-disambiguation.md, etc.) are Claude Code session context files that define how the current session behaves. They are not SAP knowledge content. Exposing them through MCP would confuse the model about the boundary between configuration and content, and risks the model applying routing rules as factual SAP content.

**Do this instead:** Scope KB file discovery explicitly to `modules/`, `cross-module/`, and `reference/`. Use an explicit whitelist in `list_kb_files()`. Never walk `.claude/`, `.planning/`, or `scripts/`.

---

### Anti-Pattern 4: Returning full file bodies from search_kb

**What people do:** For every file that contains the search query, return the entire file body in the `search_kb` result.

**Why it's wrong:** KB files are 2,000-8,000 tokens each. Returning 10 full files from a search call consumes 20,000-80,000 tokens in a single tool response. This saturates the context window and forces Claude to process far more text than needed to decide which file to retrieve next.

**Do this instead:** `search_kb` returns summaries: file path, module, content_type, confidence, and a 3-5 line excerpt around each match. Claude then calls `get_content` for the one or two specific files it needs. This is the standard search-then-retrieve pattern used by Context7 and similar KB tools.

---

## Integration Points

### Deployment Configuration

| Client | Config File | Example Entry | Notes |
|--------|-------------|---------------|-------|
| Claude Code | `.mcp.json` at repo root | `{"sap-kb": {"command": "python3", "args": ["/abs/path/scripts/mcp_server.py"]}}` | Committed to repo; auto-discovered at session start |
| Claude Desktop | `~/.config/Claude/claude_desktop_config.json` | `{"mcpServers": {"sap-kb": {"command": "python3", "args": ["/abs/path/scripts/mcp_server.py"]}}}` | Not committed; user-configured per machine |

Both clients launch the server as a child process over stdio. No port, no network, no daemon process to manage.

**Observed `.mcp.json` format from context7 on this machine:**
```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```
The SAP KB server uses `python3` + absolute path instead of `npx`, but the format is identical.

### New vs. Existing Files

| File | Status | Notes |
|------|--------|-------|
| `scripts/mcp_server.py` | New | MCP server entry point; tool definitions; `mcp.run(transport="stdio")` |
| `scripts/kb_reader.py` | New | KB I/O utilities; `parse_frontmatter`, `read_file`, `list_kb_files` |
| `scripts/requirements.txt` | Modified | Add `mcp>=1.2.0` (or `mcp[cli]`) to existing `PyYAML>=6.0` |
| `.mcp.json` | New | Claude Code MCP registration at repo root |
| `scripts/validate.py` | Unchanged | Existing validator; refactor to import `parse_frontmatter` from `kb_reader.py` |
| All KB `.md` files | Unchanged | Read-only at runtime; server never modifies KB content |

### Reuse from validate.py

`validate.py` already implements the exact frontmatter parsing logic the server needs:
- `parse_frontmatter(filepath)` — splits `---` YAML block from body, returns both
- `VALID_MODULES` set: `{"fi", "mm", "sd", "co", "cross-module", "reference"}`
- `VALID_CONTENT_TYPES` set (12 valid values including processes, tcodes, integration, config-spro, etc.)
- `VALID_CONFIDENCE` set: `{"high", "medium", "low"}`

Recommended refactor: move this logic into `kb_reader.py`, then have both `validate.py` and `mcp_server.py` import from `kb_reader.py`. This avoids duplicate code without breaking the existing validation CI.

### Python Environment

- Python 3.14.2 at `/usr/bin/python3` (confirmed by `python3 --version`)
- `PyYAML>=6.0` already installed (in `scripts/requirements.txt`)
- `mcp` package not yet installed — must be added before v1.1 development begins
- No virtual environment exists currently — create one at `scripts/venv/` or install with `pip install --user mcp`

---

## Sources

- MCP specification (Tools): https://modelcontextprotocol.io/specification/2025-11-25/server/tools (HIGH confidence — official spec, fetched 2026-02-23)
- MCP specification (Resources): https://modelcontextprotocol.io/specification/2025-11-25/server/resources (HIGH confidence — official spec, fetched 2026-02-23)
- MCP Python quickstart: https://modelcontextprotocol.io/quickstart/server (HIGH confidence — official guide, fetched 2026-02-23)
- MCP local deployment guide: https://modelcontextprotocol.io/docs/develop/connect-local-servers (HIGH confidence — official guide, fetched 2026-02-23)
- Claude Code MCP registration format: `/home/corye/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/context7/.mcp.json` (HIGH confidence — live config on this machine)
- KB file structure: surveyed from `/home/corye/Claude/SAPKnowledge/` (HIGH confidence — actual files)
- `validate.py` frontmatter parsing logic: read from `/home/corye/Claude/SAPKnowledge/scripts/validate.py` (HIGH confidence — actual file)
- Python version: `python3 --version` = 3.14.2 (HIGH confidence — runtime check)

---
*Architecture research for: MCP server over SAP ECC 6.0 flat-file knowledge base*
*Researched: 2026-02-23*
