# Technology Stack

**Project:** SAP ECC 6 Knowledge Base — MCP Server Layer
**Researched:** 2026-02-23
**Confidence:** HIGH (SDK version verified against npm registry; transport model verified against official MCP docs)

---

## Context

The knowledge base already exists as structured markdown files with YAML frontmatter in
`modules/{mm,sd,fi,co}/`. The task is to add an MCP server layer that exposes that content
to any MCP-capable client (Claude Code, Claude Desktop).

This stack document covers only the MCP server. The content layer stack (markdown conventions,
file organization) is covered separately.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Node.js | 22.x (LTS) | Runtime | Already installed on this machine (verified: v22.22.0). MCP SDK requires >=18. Node 22 is current LTS. No reason to use anything else on a machine that already has it. |
| TypeScript | 5.9.x | Language | Verified current: 5.9.3 on npm. The official MCP TypeScript SDK is typed end-to-end — the type system catches tool schema mistakes before runtime. Not optional for an MCP server; the SDK is built around TypeScript types. |
| @modelcontextprotocol/sdk | 1.27.0 | MCP server framework | Verified current: 1.27.0 published 2026-02-16. This is Anthropic's official SDK. It handles the JSON-RPC protocol, stdio/HTTP transports, tool registration, and lifecycle. Do not implement MCP protocol by hand. |
| zod | 4.3.6 | Input schema validation | Required peer dependency of the MCP SDK (accepts `^3.25 || ^4.0`). Zod 4 is stable as of 2026-01-22. Use for defining tool input schemas — the SDK converts Zod schemas to JSON Schema automatically. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| gray-matter | 4.0.3 | YAML frontmatter parsing | Required. Every KB file has YAML frontmatter (module, content_type, confidence, last_verified). gray-matter parses `---` frontmatter from markdown strings synchronously with zero setup. Use in the file-loading layer. |
| glob | 11.x | File discovery | Use `glob` (the npm package) for discovering KB files by pattern (`modules/**/*.md`). Built-in `fs.glob` works on Node 22 but the npm package has a simpler API and consistent behavior across environments. |
| tsx | 4.21.0 | Dev-time TypeScript execution | Run `src/index.ts` directly without a build step during development. Use `node --import tsx/esm` or `tsx watch` for rapid iteration. Do not use in production. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| tsc | TypeScript compilation for production | `target: ES2022`, `module: Node16`, `outDir: build/`. The official docs use exactly this tsconfig. |
| @types/node | 25.3.0 | Node.js type definitions | Required for fs, path, process types. Pin to match your Node version. |
| @modelcontextprotocol/inspector | latest | MCP server debugging | Official interactive test client. Run `npx @modelcontextprotocol/inspector node build/index.js` to test tool calls without Claude. Essential during development. |

---

## Installation

```bash
# Initialize project inside the KB repo
mkdir -p mcp-server/src
cd mcp-server

# Init package.json with ESM
npm init -y
# Then manually set "type": "module" in package.json

# Core dependencies
npm install @modelcontextprotocol/sdk zod gray-matter

# Dev dependencies
npm install -D typescript @types/node tsx

# Init tsconfig
npx tsc --init
# Then update to use Node16 module resolution (see tsconfig below)
```

### Required package.json shape

```json
{
  "type": "module",
  "bin": { "sap-kb-mcp": "./build/index.js" },
  "scripts": {
    "build": "tsc && chmod 755 build/index.js",
    "dev": "tsx watch src/index.ts",
    "start": "node build/index.js"
  },
  "files": ["build"]
}
```

### Required tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

Why `Node16` module resolution: the MCP SDK uses `.js` import extensions internally and
expects Node16 resolution. Using `bundler` or `NodeNext` also works, but `Node16` is what
the official quickstart uses and what has been verified to work.

---

## Transport: stdio, not HTTP

Use `StdioServerTransport` from `@modelcontextprotocol/sdk/server/stdio.js`.

**Why stdio:** Claude Code and Claude Desktop both launch MCP servers as child processes over
stdio. The KB server is a local read-only tool — it does not need network accessibility, auth,
or multi-client support. HTTP/SSE transport (also available in the SDK) adds complexity that
serves no purpose for this use case.

**Critical stdio rule:** Never write to stdout in stdio mode. `console.log()` corrupts the
JSON-RPC stream and breaks the server silently. Use `console.error()` for all logging — it
goes to stderr, which is safe.

---

## What to Expose: Tools vs Resources

The MCP SDK supports Tools, Resources, and Prompts. For a read-only KB:

**Use Tools** — not Resources. Here is why:

Resources require the client to browse and fetch specific URIs. Tools let the LLM
decide what to retrieve based on a query. For a KB lookup pattern ("find everything
about MIRO" or "what movement types affect the GR/IR account"), tools with query
parameters are a much better fit than resource browsing.

Recommended tools:

| Tool | Input Schema | What It Does |
|------|-------------|--------------|
| `search_kb` | `query: string, module?: "mm"\|"sd"\|"fi"\|"co"` | Glob all KB files, parse frontmatter, return files whose content matches the query |
| `get_file` | `path: string` | Return the full content of a specific KB file by relative path |
| `list_files` | `module?: string, content_type?: string` | Return a list of all KB files with their frontmatter metadata |

Three tools is the right scope for a first implementation. Do not build more until these
are working and the query patterns are understood.

---

## Claude Code / Claude Desktop Configuration

After `npm run build`, register the server in Claude Code by adding to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server/build/index.js"]
    }
  }
}
```

Or with the dev runner (no build step required):

```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "npx",
      "args": ["tsx", "/absolute/path/to/mcp-server/src/index.ts"]
    }
  }
}
```

The npx/tsx form is convenient for development but starts slower. Use the compiled form
for daily use.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| TypeScript + Node.js | Python + `mcp[cli]` (FastMCP) | Python if the team has no Node.js experience. Python FastMCP has the nicest API (`@mcp.tool()` decorator). But the TypeScript SDK is equally mature, this machine already has Node 22, and TypeScript types provide better correctness guarantees for schema definitions. |
| stdio transport | HTTP/SSE transport | HTTP when the server needs to be shared across machines or accessed by multiple clients simultaneously. Not needed for a local KB server. |
| Three focused tools | Single `query` tool | A single flexible tool is simpler to implement but harder for the LLM to use correctly. Separate tools with specific input schemas give the LLM clearer affordances. |
| zod | Raw JSON Schema objects | Raw JSON Schema works but is verbose and lacks runtime validation. Zod gives type-safe schema definitions that are automatically converted to JSON Schema by the SDK. |
| gray-matter | Manual YAML parsing | gray-matter is the standard choice, well-tested, handles edge cases in YAML frontmatter. Manual parsing risks breaking on multi-line values or special characters. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Vector database (Chroma, Pinecone, etc.) | Massive over-engineering for ~50 curated markdown files. Adds infrastructure, index maintenance, and semantic drift. | File system + string search. The KB is small enough that full-file reads are fast. |
| LangChain / LlamaIndex | Framework overhead for a job that is 50 lines of TypeScript. These frameworks add abstraction layers that make debugging harder. | Direct SDK usage: `McpServer.registerTool()` + `gray-matter` + `fs.readFile()`. |
| `console.log()` in stdio mode | Writes to stdout, corrupts the JSON-RPC stream, breaks the server with no obvious error. | `console.error()` for all debug output in stdio servers. |
| Third-party MCP framework wrappers | The official SDK is already high-level enough. Wrappers add an extra dependency layer on a rapidly evolving protocol. | `@modelcontextprotocol/sdk` directly. |
| Embedding models at query time | Unnecessary for a structured KB. The KB files have clear module/content_type metadata in frontmatter. | Filter by frontmatter fields + string search on content. |
| HTTP server for local deployment | Adds auth concerns, port management, and startup ordering issues. | stdio transport: the MCP client spawns the server as a subprocess, no port needed. |

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `@modelcontextprotocol/sdk@1.27.0` | `zod@^3.25 \|\| ^4.0` | Both are peer deps. Use zod@4 (4.3.6) — it is the current stable release. |
| `@modelcontextprotocol/sdk@1.27.0` | `node>=18` | Tested on Node 22. No compatibility issues. |
| `typescript@5.9.3` | `@types/node@25.3.0` | Verified compatible. Both are current as of 2026-02-23. |
| `gray-matter@4.0.3` | Node 22, ESM | Works in ESM with `import matter from 'gray-matter'`. No named-export issues. |
| `tsx@4.21.0` | TypeScript 5.x, Node 22 | Used for dev only. Compatible. |

---

## Sources

- npm registry: `@modelcontextprotocol/sdk` — version 1.27.0 (published 2026-02-16), engines, peer dependencies (HIGH confidence — direct registry query)
- npm registry: `zod` — version 4.3.6 (published 2026-01-22) (HIGH confidence)
- npm registry: `typescript` — version 5.9.3 (HIGH confidence)
- npm registry: `gray-matter` — version 4.0.3 (HIGH confidence)
- npm registry: `tsx` — version 4.21.0 (HIGH confidence)
- npm registry: `@types/node` — version 25.3.0 (HIGH confidence)
- `https://modelcontextprotocol.io/docs/develop/build-server` — Official MCP quickstart (TypeScript tab): transport selection, tsconfig shape, tool registration API, stdio logging rules (HIGH confidence — fetched 2026-02-23)
- Local KB inspection: `modules/mm/CLAUDE.md`, `modules/mm/tcodes.md` — confirmed YAML frontmatter structure (module, content_type, confidence, last_verified) (HIGH confidence)

---

*Stack research for: SAP ECC 6 Knowledge Base MCP Server*
*Researched: 2026-02-23*
