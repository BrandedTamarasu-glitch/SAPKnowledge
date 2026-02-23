# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-23)

**Core value:** When someone asks Claude "how do I do X in SAP," it gives the correct ECC 6 answer — right transaction, right config path, right module interactions.
**Current focus:** v1.1 milestone — MCP Server. Phase 13 Plan 01 complete (kb_reader.py). Next: Phase 13 Plan 02 (mcp_server.py).

## Current Position

Phase: 13
Plan: 13-02 (next)
Status: Phase 13 Plan 01 complete — kb_reader.py extraction helpers created; fastmcp==3.0.2 pinned; .gitignore created.
Last activity: 2026-02-23 — Phase 13 Plan 01 executed (kb_reader.py + requirements.txt + .gitignore)

Progress: [██████████] 97%

(38 known plans have SUMMARY.md; Phase 13 Plans 02+ and Phases 14/15 pending)

## Performance Metrics

**Velocity:**
- Total plans completed: 36 (4 Phase 1 + 2 Phase 2 + 4 Phase 3 + 2 Phase 4 + 4 Phase 5 + 3 Phase 6 + 4 Phase 7 + 3 Phase 8 + 4 Phase 9 + 3 Phase 10 + 3 Phase 11)
- Average duration: ~2min
- Total execution time: ~0.7 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-repository-foundation | 4 | ~12min | ~3min |
| 02-core-reference-framework | 2 | ~5min | ~2.5min |
| 03-fi-module-foundation | 4 (complete) | ~9min | ~2.3min |
| 04-fi-advanced-and-integration-prep | 2 (complete) | ~6min | ~3min |
| 05-mm-module-foundation | 4 (complete) | ~8min | ~2min |
| 06-mm-advanced-and-fi-integration | 3 (complete) | ~14min | ~4.7min |
| 07-sd-module-foundation | 4 (complete) | ~11min | ~2.8min |
| 08-sd-advanced-and-fi-integration | 3 (complete) | ~10min | ~3.3min |
| 09-co-module-foundation | 4 (complete) | ~12min | ~3min |
| 10-co-advanced-and-fi-integration | 3 (complete) | ~12min | ~4min |

**Recent Trend:**
- Last 5 plans: 10-03 (5min), 11-01 (3min), 11-02 (3min), 11-03 (8min), 12-01 (5min)
- Trend: Stable ~2-8min per content-writing plan

*Updated after each plan completion*
| Phase 12-solution-design-intelligence P01 | 5 | 1 tasks | 1 files |
| Phase 12 P02 | 15 | 2 tasks | 2 files |
| Phase 13-mcp-server P01 | 2 | 2 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Markdown files over MCP server (simpler, no infrastructure, portable)
- Prioritize MM/SD/FI/CO for v1 (core logistics and finance modules)
- ECC 6 only, S/4 disambiguation (prevents mixing up ECC and S/4 behavior)
- Public sources only (keeps knowledge base shareable)
- Routing table uses CLAUDE.md entry points per module, not individual content files (01-01)
- Combined rules token budget ~809 of 1500 limit, leaving headroom (01-01)
- Org structure uses ASCII tree diagram for compact visual hierarchy (01-01)
- Used PyYAML directly instead of python-frontmatter (pip unavailable on system) (01-03)
- Subagents cannot write to SAPKnowledge from General working directory — execute plans from orchestrator (01-02, 01-03, 01-04)
- Disambiguation table rows added at end of table when domain-specific rows are added; cross-reference links to detail files (02-02)
- Token budget after phase 2 expansion: ~975 tokens of 1500 limit (02-02)
- Sales Area documented as special non-table subsection (not a separate DB entity) to prevent confusion (02-01)
- Segment org unit carries CRITICAL ECC 6 NOTE about New GL prerequisite — important disambiguation (02-01)
- Purchasing Org three-assignment-mode pattern documented inline (02-01)
- T-code reference format: frontmatter + workflow index table + submodule sections with ### headings (03-01)
- FS10N labeled as "Classic GL" despite menu saying "(New)" — important disambiguation for New GL environments (03-01)
- S_ALR corrections embedded in workflow index + two T-code Gotcha fields for maximum discoverability (03-01)
- F110 APP 7-step sequence documented inline in T-code entry, not deferred to process file (03-01)
- CRITICAL prefix used in Gotcha fields for the most dangerous errors (03-01)
- master-data.md written as single file (not split by object) for single-lookup master data reference (03-02)
- CORRECTION note blocks used for commonly-wrong field locations (AKONT, FDGRV, KVGR1-5, KOSTL) — field-location errors are #1 source of bad SAP content (03-02)
- S/4HANA Business Partner callout placed once at customer master section header, covers both vendor+customer (03-02)
- config-spro.md written as single file covering all four FI config areas — single-lookup SPRO reference (03-03)
- AA config order (EC08→OAOB→OAOA→AO90→AFAMA) documented at section header with CRITICAL warning — most dangerous FI config mistake (03-03)
- FBZP 5 sub-areas under one step (not 5 steps) — reflects how consultants describe FBZP in practice (03-03)
- Document splitting client-level warning uses CRITICAL callout; per-CC deactivation path included (03-03)
- processes.md uses narrative-plus-table format with role annotations at each step (03-04)
- Cross-references embedded inline: FBZP→config-spro.md, S_ALR confusion warning, AFAB→AJAB dependency (03-04)
- CLAUDE.md File Index updated to specific Read When guidance (not generic) for all four Phase 3 files (03-04)
- account-determination.md: cash discount config = OBXU/OBXI (NOT OBB8); OBB8 = payment terms only (04-01)
- PRD fires for movement type 101 on standard price (S) materials only; MAP (V) absorbs variance into BSX (04-01)
- VKOA section scoped to framework intro; Phase 8 (SD Advanced) owns the full VKOA deep-dive (04-01)
- GR/IR clearing account OI indicator = required for F.13 automatic clearing — documented as critical implementation pitfall (04-01)
- CRITICAL CLARIFICATION: document splitting is NOT parallel accounting — must be preserved in all future FI content (04-02)
- Troubleshooting entries are self-contained (full resolution path inline) to avoid requiring multiple file lookups (04-02)
- Decision trees include config implications inline, not just pointers to config-spro.md (04-02)
- validate.py updated to accept decision-trees-and-troubleshooting and account-determination content types (06-01)
- validate.py: S/4HANA Differences section now stripped from contamination scan — prevents false positives on intentional disambiguation content (06-02)
- validate.py: integration content type token budget raised from 3000 to 5000 — comprehensive integration docs need more space (06-02)
- Token budget warnings accepted for mm-advanced.md (12524 tokens vs 5000 cap) — file intentionally covers OBYC + decision trees + troubleshooting; splitting would reduce usability (06-03)
- Customer master self-contained (all three levels KNA1/KNB1/KNVV) with SD emphasis on KNVV — matches FI master-data.md pattern (07-02)
- S/4HANA Business Partner callout placed once at customer master section header, not per-field (07-02)
- 4 CORRECTION blocks for field-location errors: KVGR1-5, KTGRD, KTGRM, DWERK (07-02)
- Condition technique documented once in Pricing section, referenced by Output Determination and Text Determination — avoids duplication (07-03)
- Credit management kept at foundation level (5-step brief) with explicit deferral to Phase 8 (07-03)
- VKOA revenue account determination kept as brief framework entry point, deferring deep-dive to Phase 8 (07-03)
- Token budget warning accepted for SD tcodes.md (7100 tokens vs 5000 cap) — comprehensive reference with condition technique overview; same pattern as mm-advanced.md (07-01)
- Batch Determination included at foundation level (VLBR, MBC1, CL20N) — batch traceability is daily-use (07-01)
- Credit/debit memo sections expanded with summary tables for self-contained reference (07-04)
- Cash sales documented as 5-step automatic process (order+delivery+PGI+billing+FI simultaneous) (07-04)
- CLAUDE.md token budget slightly over (720 vs 600 cap) — accepted for comprehensive File Index guidance across 4 content files (07-04)
- VKOA content placed in sd-advanced.md (not fi/account-determination.md) to keep SD perspective separate from FI framework (08-01)
- EVV documented with both VKOA and OBXI paths since implementation choice varies (08-01)
- Intercompany billing kept at foundation level with explicit Phase 12 deferral for deep IV/PI/PD config (08-01)
- VKOA vs OBYC independence documented as CRITICAL DISTINCTION -- prevents the #1 SD-FI confusion (08-02)
- Pro forma billing (F5/F8) explicitly marked as No FI posting in integration catalog (08-02)
- Period-end sequence as 7-step table paralleling MM-FI period-end format (08-02)
- Revenue recognition kept at moderate depth; complex POC deferred to Phase 12 (08-02)
- Token budget warnings accepted for sd-advanced.md (13459 tokens vs 5000 cap) -- file covers VKOA + decision trees + troubleshooting; same pattern as mm-advanced.md (08-03)
- CLAUDE.md token budget slightly over (872 vs 600 cap) -- accepted for comprehensive File Index with 6 content file rows (08-03)
- content_type set to config-spro (not config) to match validate.py expected types (09-03)
- [Phase 09]: Token budget warning accepted for CO tcodes.md (7600 tokens vs 5000 cap) -- comprehensive reference with 8 subareas; same pattern as SD tcodes.md
- [Phase 09]: CO-PA limited to 2 T-codes (KE21N, KE24) with explicit Phase 10 deferral
- [Phase 09]: Token budget warnings accepted for processes.md (4029 vs 4000 cap) and CLAUDE.md (755 vs 600 cap) -- comprehensive process documentation
- [Phase 09]: PCA Separate Ledger Key Concept rephrased to avoid S/4HANA contamination trigger in CLAUDE.md index
- [Phase 10]: Worked examples (FB50 trace, reconciliation table with amounts) included to make abstract CO-FI flows concrete
- [Phase 10]: OKC1 added as KALC configuration prerequisite for reconciliation posting accounts
- [Phase 10]: Token budget warnings accepted for co-advanced.md (11248 tokens vs 5000 cap) -- file covers CE mapping + decision trees + troubleshooting; same pattern as mm-advanced.md and sd-advanced.md
- [Phase 10]: CLAUDE.md token budget slightly over (931 vs 600 cap) -- accepted for comprehensive File Index with 7 content file rows
- [Phase 11]: Consignment and STO each get own ## section -- distinct movement types justify separate sections per Claude's discretion
- [Phase 11]: ATP section explains integration mechanics (checking group + checking rule + what MM provides), defers SPRO-level OVZ2 config to modules/sd/config-spro.md
- [Phase 11]: Returns section provides full reverse trace with every document and module handoff per locked decision
- [Phase 11]: Used e2e-process content_type (not end-to-end-process) to match validate.py expected types
- [Phase 11]: Cross-references use consistent See modules/xx/file.md Section X format per RESEARCH.md and CONTEXT.md requirements
- [Phase 11]: R2R documented as period-end orchestration (not linear document flow) across all 4 modules with strict ordering: MM -> SD -> CO -> FI
- [Phase 12-solution-design-intelligence]: Token budget warning accepted for design-patterns.md (11501 tokens vs 4000 cap) — same pattern as mm-advanced.md, sd-advanced.md, co-advanced.md
- [Phase 12-solution-design-intelligence]: content_type set to 'patterns' (not 'design-patterns') to match validate.py expected types
- [Phase 12]: Playbooks use cross-reference synthesis pattern — point to module files for config detail, add cross-module FI/CO perspective and test scenarios unavailable in single module files
- [Phase 12]: validate.py updated to accept playbooks and checklists content types — pre-registering checklists prevents blocking issue in Plan 03
- [v1.1 Roadmap]: MCP server implemented as Python + FastMCP (not TypeScript) — Python already in repo (validate.py), PyYAML installed, two new files in scripts/ vs new directory + build step for TypeScript
- [v1.1 Roadmap]: Phase 13 groups all P1 tools (MCP-01/02/03/04/05/06/07/09/10) — shared infrastructure, all LOW complexity, no benefit to splitting
- [v1.1 Roadmap]: MCP-08 (search_by_keyword) deferred to Phase 14 — P2 tool, add after observing P1 tool gaps
- [v1.1 Roadmap]: MCP-11 (deployment docs) is Phase 15 — final deliverable, depends on server being complete and validated
- [v1.1 Roadmap]: MCP server is read-only — never moves, renames, or transforms KB files; native CLAUDE.md loading path unchanged
- [v1.1 Roadmap]: Tool descriptions must be written as LLM invocation conditions (MCP-09); section-level extraction enforced, no full file dumps (MCP-10)
- [Phase 13-01]: fastmcp==3.0.2 pinned at exact version (not >=) — floor-only spec insufficient for production
- [Phase 13-01]: normalize_module returns None (not raises) for out-of-KB modules — enables clean user-facing error messages in mcp_server.py
- [Phase 13-01]: MIGO first-match strategy — first occurrence in MM tcodes.md is Goods Receipt, correct for most common query

### Pending Todos

- Execute Phase 13 Plan 02 (mcp_server.py with all 5 P1 tools)

### Blockers/Concerns

- Subagent directory permission issue: agents spawned from ~/Claude/General cannot write to ~/Claude/SAPKnowledge. Workaround: execute plans directly from orchestrator level.

## Session Continuity

Last session: 2026-02-23
Stopped at: Completed 13-mcp-server-scaffold-p1-tools/13-01-PLAN.md (kb_reader.py, requirements.txt, .gitignore)
Resume file: None
