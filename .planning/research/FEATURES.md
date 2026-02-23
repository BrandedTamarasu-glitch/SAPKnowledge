# Feature Landscape — MCP Server Tools

**Domain:** MCP server exposing SAP ECC 6.0 Knowledge Base programmatic query interface
**Researched:** 2026-02-23
**Confidence:** HIGH (based on direct KB structure inspection + MCP protocol knowledge)

---

## Context

The KB already exists. It is ~35 structured markdown files organized as:

```
modules/{module}/          -- tcodes, config-spro, processes, master-data, advanced, integration, patterns
cross-module/              -- E2E process flows (P2P, O2C, R2R), checklists, playbooks, design-patterns
reference/                 -- movement-types, document-types, posting-keys, org-structure
.claude/rules/             -- routing, disambiguation, org-structure (always-loaded rules)
```

Every file has YAML frontmatter with `module`, `content_type`, `confidence`, and `last_verified`.

The MCP server wraps this KB. Its tools are the query interface. **The question is: what tools expose the right KB surfaces for programmatic use?**

Target clients: Claude Desktop, Claude Code, custom apps (e.g., a web tool for SAP consultants).

---

## Table Stakes

Features MCP clients assume exist. Missing = server is incomplete and Claude will use raw file reads instead.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **`lookup_tcode`** | "What does VA01 do?" is the single most common SAP query. Any SAP KB tool must answer this atomically without loading full module files. | LOW | Input: tcode string. Output: description, menu path, module, when-to-use, gotchas. Content lives in `modules/{module}/tcodes.md`. |
| **`get_process_flow`** | "Walk me through P2P" or "explain how billing works" — users need E2E flows. Without this, clients must load entire process files manually. | LOW | Input: process name (e.g., "P2P", "O2C", "R2R") or free text. Output: step-by-step flow with T-codes and module boundaries. Content in `cross-module/` and `modules/{module}/processes.md`. |
| **`search_by_keyword`** | Free-text search across the KB. Without this, clients must know which file contains the answer. MCP tools are not useful if the caller must pre-know the structure. | MEDIUM | Input: query string, optional module filter. Output: matching sections from relevant files ranked by relevance. Requires text matching across all content files. |
| **`get_module_overview`** | "What does the MM module cover?" — clients need orientation before diving deep. Without this, every module entry requires reading CLAUDE.md manually. | LOW | Input: module code (mm, sd, fi, co, cross-module, reference). Output: module scope, file index with one-liner descriptions, key concepts. Content from `modules/{module}/CLAUDE.md`. |
| **`get_config_path`** | "How do I configure tolerance keys in ECC 6?" — SPRO paths are the second most common query type after T-codes. | LOW | Input: feature or T-code name. Output: SPRO IMG path, T-code shortcut, what to configure, gotchas. Content from `modules/{module}/config-spro.md`. |
| **`get_integration_points`** | "What happens in FI when I post a GR?" — integration questions are the most error-prone without this KB. Without a dedicated tool, clients must navigate the full integration files. | MEDIUM | Input: source module, target module, optional transaction. Output: integration points catalog with OBYC/VKOA key info, FI document impact. Content from `modules/{module}/integration.md`. |

---

## Differentiators

Features that make this server meaningfully better than "just reading files." These are where programmatic access pays off versus raw file loading.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **`lookup_movement_type`** | Movement types (101, 201, 261, 541, 601, etc.) are the backbone of MM operations. Each has specific FI posting logic (OBYC keys, Dr/Cr patterns). Atomic lookup beats loading the full advanced file. | LOW | Input: movement type number. Output: description, use case, OBYC transaction keys triggered, FI posting impact, common gotchas. Content from `modules/mm/mm-advanced.md` and `reference/movement-types.md` (when populated). |
| **`get_account_determination`** | OBYC/VKOA walkthroughs are the hardest SAP topic. Structured tool output (which key fires → which account → what modifier) is more useful than raw markdown. A tool can return structured JSON that clients use in different ways. | MEDIUM | Input: scenario (e.g., "MIGO 101 standard price material") or transaction key (e.g., "GBB"). Output: determination chain, account modifiers, Dr/Cr, worked example, debugging steps. Content from `modules/mm/mm-advanced.md` and `modules/fi/account-determination.md`. |
| **`get_period_end_checklist`** | Period-end close is operational, time-pressured work. A tool that returns a structured checklist (with T-codes, timing, dependencies) is more useful than reading the markdown. Callers can filter by module phase (MM, SD, CO, FI) or close type (month-end, year-end). | LOW | Input: close_type (month_end, year_end), optional phase (mm, sd, co, fi). Output: ordered checklist items with T-codes, business-day timing, dependency warnings. Content from `cross-module/checklists.md`. |
| **`get_scenario_playbook`** | Consignment, intercompany, third-party, subcontracting, split valuation, batch, serial — these 8 playbooks are the KB's highest-value content. A named lookup is far more useful than searching for the right file. | LOW | Input: scenario name. Output: full playbook — business context, config steps, master data, process flow table, test scenarios, cross-module perspective, pitfalls. Content from `cross-module/playbooks.md`. |
| **`resolve_routing`** | Replicates the `.claude/rules/sap-routing.md` logic as a tool. Given a natural language query, returns which module file(s) to read. Useful for orchestrator-style clients that want to plan their KB reads before executing them. | MEDIUM | Input: natural language query. Output: module code, recommended files, rationale. Uses keyword matching against routing table. Reduces wasted tool calls for clients that must pre-plan. |
| **`get_decision_tree`** | Decision trees exist in mm-advanced, co-advanced, sd-advanced, fi-advanced. Each answers "which approach should I use for X?" Structured tool output (Q&A chain + comparison table + trade-offs) is more useful than raw markdown. | MEDIUM | Input: domain (e.g., "valuation approach", "lot sizing", "release strategy"). Output: questions, answers, recommendation, comparison table. Content from `{module}-advanced.md` files. |
| **`compare_ecc_s4`** | The primary pain point driving this KB. A dedicated tool that returns ECC 6 vs S/4HANA differences for a specific topic prevents hallucinated S/4 answers. | LOW | Input: topic (e.g., "vendor master", "material documents", "cost elements"). Output: ECC 6 behavior, S/4HANA change, impact on workflows. Content from `modules/{module}/CLAUDE.md` headers and `.claude/rules/sap-disambiguation.md`. |

---

## Anti-Features

Features that seem valuable but create complexity or undermine the KB's purpose.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Full-text semantic search / embeddings** | "Find everything related to three-way match" — natural language similarity search sounds powerful. | Requires vector DB, embedding model, index maintenance. The KB has clean structure (routing rules, module indexes) that makes keyword search + structured routing ~80% as effective at 5% of the complexity. Semantic search adds infra to solve a problem that structured routing already handles. | Use `search_by_keyword` with good keyword extraction + `resolve_routing` to narrow to the right files first. This covers 95% of real queries. |
| **Write / update KB content tools** | "Let me correct this T-code description via MCP" — mutations sound useful for maintenance. | MCP read-only is the right model for a reference KB. Write tools turn an authoritative reference into a mutable store, requiring validation, versioning, and conflict resolution. Also creates security risk if clients can modify the KB through the MCP server. | Keep KB as git-managed files. Updates go through normal git workflow. The MCP server is read-only. |
| **Real-time SAP system connection** | "Connect to my SAP system and pull the actual config" — would give live data. | Completely out of scope. Different security model (SAP credentials), different architecture (RFC connection), different use case (live system inspection vs reference KB). | Explicitly document this as out of scope. The KB is a reference, not a live SAP connector. |
| **Chat/conversation management tools** | "Remember my previous questions about MM" — stateful session management. | MCP servers are stateless by design. Adding session state requires a database, session ID management, and expiry logic. The MCP protocol is built for stateless tool calls. Conversation memory is the client's (Claude's) responsibility, not the server's. | Let Claude's context window handle conversation state. The server returns structured data; Claude manages the conversation. |
| **Exhaustive field-level documentation tools** | "Give me every field in BSEG" — table schema lookup. | SE11 (SAP data dictionary) already does this. Reproducing it in the KB adds maintenance burden without adding value. The KB's value is in the logic (why field X matters, when field Y is used), not in schema enumeration. | Document key fields that drive business logic in `master-data.md` files, accessible via `search_by_keyword`. Do not create a dedicated table schema tool. |
| **Multi-language support** | SAP is global; German T-code descriptions would help German-language users. | KB content is English-only. Adding i18n requires parallel content maintenance for every file. The target audience (Claude, Claude Code) handles language bridging natively. | Accept English-only. The KB's precision matters more than language coverage for the initial milestone. |
| **Batch / bulk query tools** | "Give me all T-codes for all modules" — dump everything. | Produces large output that fills Claude's context window without helping. The value of structured tools is targeted retrieval, not dumps. Bulk responses defeat the purpose of the MCP interface. | Keep tools targeted. If a client needs bulk data, it should make multiple targeted tool calls, not one bulk call. |

---

## Feature Dependencies

```
resolve_routing
    └──enables──> search_by_keyword (routing narrows search scope)
    └──enables──> get_module_overview (routing identifies the module)

get_module_overview
    └──required by──> lookup_tcode (module context needed to locate T-code)
    └──required by──> get_config_path (module scopes SPRO paths)

lookup_tcode
    └──enhances──> get_process_flow (process steps reference T-codes)
    └──enhances──> get_integration_points (integration points reference T-codes)

get_process_flow
    └──required by──> get_integration_points (integration needs process context)
    └──enhances──> get_period_end_checklist (checklist is a process flow variant)

lookup_movement_type
    └──required by──> get_account_determination (movement type drives OBYC key selection)
    └──enhances──> get_integration_points (movement types appear in integration point catalog)

get_account_determination
    └──enhances──> get_integration_points (account determination is the FI side of integration)

compare_ecc_s4
    └──crosscuts──> all tools (disambiguation applies to every topic)

get_scenario_playbook
    └──depends on──> lookup_tcode + get_process_flow + get_integration_points + get_account_determination
    (playbooks synthesize all content types into a single scenario answer)
```

### Dependency Notes

- **`resolve_routing` enables `search_by_keyword`:** Routing first narrows the search to the right module file(s), making keyword search faster and more precise. Without routing, search must scan all files.
- **`lookup_movement_type` required by `get_account_determination`:** Account determination (OBYC) is triggered by movement type. The movement type determines which transaction keys fire, which determines the GL accounts. The two tools must be consistent in their data model.
- **`compare_ecc_s4` crosscuts all tools:** Every tool should accept an optional `include_s4_differences` flag that appends the disambiguation section to the response. This is not a separate query; it is an optional enrichment on any existing tool.
- **`get_scenario_playbook` is the synthesis tool:** It calls the same underlying data as the other tools but returns a complete cross-module answer. It is high-value but depends on all other content being correct. Build it last.

---

## MVP Definition

### Launch With (v1)

Minimum viable MCP server — covers the most common query patterns.

- [ ] **`lookup_tcode`** — handles "What does X T-code do?" which is the highest-frequency SAP query type
- [ ] **`get_module_overview`** — orientation tool; needed before any other tool can be used intelligently
- [ ] **`get_config_path`** — handles "How do I configure X?" which is the second-highest-frequency query type
- [ ] **`get_process_flow`** — handles P2P / O2C / R2R / module-level process questions; extremely high value for consultants
- [ ] **`compare_ecc_s4`** — the primary pain point; must be in v1 because it is the stated purpose of the KB

### Add After Validation (v1.x)

Tools to add once core is working and real usage patterns are visible.

- [ ] **`search_by_keyword`** — add when users are asking questions the five v1 tools cannot answer; requires knowing what queries miss
- [ ] **`lookup_movement_type`** — add when MM inventory questions become a visible gap; medium frequency
- [ ] **`get_integration_points`** — add when cross-module posting questions appear frequently; high value but overlaps with `get_process_flow`
- [ ] **`get_period_end_checklist`** — add when operational close questions appear; very targeted use case

### Future Consideration (v2+)

- [ ] **`get_account_determination`** — high implementation complexity (OBYC decision logic); defer until core tools are stable and the data model is validated
- [ ] **`get_scenario_playbook`** — highest value but depends on all other tools being correct; build last
- [ ] **`get_decision_tree`** — high value for solutioning but requires parsing structured decision tree content; defer until content is fully indexed
- [ ] **`resolve_routing`** — add if clients need pre-planning capability; not needed if clients use `search_by_keyword` directly

---

## Feature Prioritization Matrix

| Tool | User Value | Implementation Cost | Priority |
|------|------------|---------------------|----------|
| `lookup_tcode` | HIGH | LOW | P1 |
| `get_module_overview` | HIGH | LOW | P1 |
| `get_config_path` | HIGH | LOW | P1 |
| `get_process_flow` | HIGH | LOW | P1 |
| `compare_ecc_s4` | HIGH | LOW | P1 |
| `search_by_keyword` | HIGH | MEDIUM | P2 |
| `lookup_movement_type` | MEDIUM | LOW | P2 |
| `get_integration_points` | HIGH | MEDIUM | P2 |
| `get_period_end_checklist` | MEDIUM | LOW | P2 |
| `get_account_determination` | HIGH | HIGH | P3 |
| `get_scenario_playbook` | HIGH | HIGH | P3 |
| `get_decision_tree` | MEDIUM | HIGH | P3 |
| `resolve_routing` | MEDIUM | MEDIUM | P3 |

**Priority key:**
- P1: Must have for v1 launch
- P2: Should have, add after validation
- P3: Nice to have, future consideration

---

## Tool Input/Output Specifications

### P1 Tools (v1 Launch)

#### `lookup_tcode`
```
Input:
  tcode: string                  -- e.g., "ME21N", "MIRO", "FB60"
  include_s4_differences: bool   -- optional, default false

Output:
  tcode: string
  description: string
  module: string                 -- "mm" | "sd" | "fi" | "co" | "cross"
  submodule: string              -- e.g., "Purchasing", "LIV", "AP"
  menu_path: string
  usage: string                  -- when to use this T-code
  gotchas: string[]              -- list of critical warnings
  related_tcodes: string[]       -- related T-codes (e.g., ME22N for change, ME23N for display)
  s4_difference: string | null   -- only if include_s4_differences=true
  confidence: string             -- from frontmatter
```

#### `get_module_overview`
```
Input:
  module: string                 -- "mm" | "sd" | "fi" | "co" | "cross-module" | "reference"

Output:
  module: string
  scope: string[]                -- bullet list of what this module covers
  file_index: object[]           -- [{file, contains, read_when}] from CLAUDE.md
  key_concepts: object[]         -- [{concept, description}]
  confidence: string
```

#### `get_config_path`
```
Input:
  topic: string                  -- e.g., "tolerance keys", "OMR6", "document splitting"
  module: string | null          -- optional module filter

Output:
  topic: string
  spro_path: string              -- full IMG navigation path
  tcode_shortcut: string | null  -- direct T-code if available
  what_to_configure: string      -- what the config controls
  gotchas: string[]
  prerequisites: string[]        -- what must be configured first
  confidence: string
```

#### `get_process_flow`
```
Input:
  process: string                -- "P2P" | "O2C" | "R2R" | "physical-inventory" |
                                 --  free-text like "procure to pay" | "billing"
  module: string | null          -- optional scope to single module

Output:
  process_name: string
  description: string
  steps: object[]                -- [{step_number, activity, tcode, role, output, module, integration_notes}]
  integration_handoffs: object[] -- [{from_module, to_module, trigger, document_created}]
  common_issues: object[]        -- [{issue, root_cause, resolution}]
  confidence: string
```

#### `compare_ecc_s4`
```
Input:
  topic: string                  -- e.g., "vendor master", "material documents", "cost elements",
                                 --  "profit center accounting", "account determination"

Output:
  topic: string
  ecc6_behavior: string
  s4hana_change: string
  impact_on_workflows: string
  disambiguation_note: string    -- when to use which version
  confidence: string
```

### P2 Tools (v1.x)

#### `search_by_keyword`
```
Input:
  query: string                  -- natural language or keywords
  module: string | null          -- optional filter
  content_type: string | null    -- optional: "tcode" | "config" | "process" | "master-data" | "troubleshooting"
  max_results: number            -- default 5

Output:
  results: object[]              -- [{file_path, section_heading, excerpt, relevance_note, confidence}]
  routing_hint: string           -- which module/file is most relevant
```

#### `lookup_movement_type`
```
Input:
  movement_type: string | number  -- e.g., "101", 201, "541"

Output:
  movement_type: string
  description: string
  typical_use_case: string
  fi_posting: bool               -- whether this movement type creates an FI document
  obyc_keys: object[]            -- [{key, account_modifier, dr_cr, description}]
  worked_example: string | null  -- representative Dr/Cr example
  reversal_movement_type: string | null
  gotchas: string[]
  confidence: string
```

#### `get_integration_points`
```
Input:
  source_module: string          -- "mm" | "sd" | "fi" | "co"
  target_module: string          -- "mm" | "sd" | "fi" | "co"
  transaction: string | null     -- optional: filter to specific T-code or process step

Output:
  integration_name: string
  touchpoints: object[]          -- [{mm_transaction, movement_type, fi_document_created,
                                 --   obyc_keys, key_tables_updated, notes}]
  transaction_trace: object | null  -- full step-by-step trace if transaction provided
  common_issues: object[]
  confidence: string
```

#### `get_period_end_checklist`
```
Input:
  close_type: string             -- "month_end" | "year_end"
  phase: string | null           -- "mm" | "sd" | "co" | "fi" | null (all phases)

Output:
  close_type: string
  phases: object[]               -- [{phase, timing, steps: [{checkbox, activity, tcode, purpose, dependencies}]}]
  critical_ordering: string      -- explanation of why phases must run in sequence
  s4_differences: string[]       -- year-end differences for S/4HANA environments
  confidence: string
```

---

## What the KB Structure Enables vs Requires

The KB structure directly shapes which tools are easy to implement:

| Tool | KB Surface | Implementation Notes |
|------|-----------|----------------------|
| `lookup_tcode` | `modules/{module}/tcodes.md` — structured sections with consistent H3 headings per T-code | Parse by H3 heading (T-code name). Each section has Menu Path, Usage, Gotcha sub-fields. High structure = easy parsing. |
| `get_module_overview` | `modules/{module}/CLAUDE.md` — frontmatter + File Index table + Key Concepts list | Read CLAUDE.md per module. File index is a markdown table. Structured enough to parse. |
| `get_config_path` | `modules/{module}/config-spro.md` — structured H2/H3 with SPRO Path, T-code, What to Configure | Parse by H3 heading (feature name). SPRO Path is consistently formatted. |
| `get_process_flow` | `modules/{module}/processes.md` + `cross-module/{process}.md` — narrative + Summary Table | Summary Table (Step/Activity/T-code/Role/Output) is the easiest surface. Narrative gives context. |
| `compare_ecc_s4` | `.claude/rules/sap-disambiguation.md` + S/4HANA Differences sections in each file | S/4HANA Differences tables appear at the end of most major files. Routing rule: check disambiguation.md first, then module file. |
| `search_by_keyword` | All files | Requires scanning all content. No pre-built index. Simple substring/regex matching is viable for v1. |
| `lookup_movement_type` | `modules/mm/mm-advanced.md` Section 1b | Movement type table is structured but embedded in a large file. Requires section-level parsing of mm-advanced.md. |
| `get_account_determination` | `modules/mm/mm-advanced.md` Sections 1a-1e + `modules/fi/account-determination.md` | Most complex parse — worked examples, debugging paths, and decision chains scattered across two files. |
| `get_period_end_checklist` | `cross-module/checklists.md` — checkbox format, explicit T-codes, business-day timing | Clean checkbox format is machine-readable. Phase structure matches the requested output. |
| `get_scenario_playbook` | `cross-module/playbooks.md` — 8 named playbooks with consistent structure | Parse by H2 heading (playbook name). Each playbook has consistent sections: Business Context, Config Walkthrough, Process Flow, Test Scenarios. |
| `get_integration_points` | `modules/{module}/integration.md` — integration point catalog tables | Catalog table format is structured. Transaction trace sections are narrative but contain structured data. |

---

## Sources

- Direct inspection of KB file structure and content (all 35 files read)
- MCP protocol design: stateless tool calls, structured input/output, read-only resource pattern
- SAP ECC 6.0 KB frontmatter schema: `module`, `content_type`, `confidence`, `last_verified`
- `.claude/rules/sap-routing.md` — routing table used as basis for `resolve_routing` tool design
- `cross-module/CLAUDE.md` and `modules/{module}/CLAUDE.md` — file index tables as tool output templates

---
*Feature research for: MCP server tools — SAP ECC 6.0 Knowledge Base*
*Researched: 2026-02-23*
