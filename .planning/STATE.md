# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-16)

**Core value:** When someone asks Claude "how do I do X in SAP," it gives the correct ECC 6 answer — right transaction, right config path, right module interactions.
**Current focus:** Phase 6 in progress — MM Advanced & FI Integration (plan 2 of 3 complete).

## Current Position

Phase: 6 of 12 (MM Advanced & FI Integration)
Plan: 2 of 3 in Phase 6
Status: 06-01 complete, 06-02 complete (integration.md MM-FI reference); 06-03 pending
Last activity: 2026-02-17 — Completed 06-02-PLAN.md (MM-FI integration: 20-transaction catalog, MIGO 101 trace, GR/IR clearing, period-end)

Progress: [██████░░░░] 47%

(18 known plans have SUMMARY.md)

## Performance Metrics

**Velocity:**
- Total plans completed: 18 (4 Phase 1 + 2 Phase 2 + 4 Phase 3 + 2 Phase 4 + 4 Phase 5 + 2 Phase 6)
- Average duration: ~2min
- Total execution time: ~0.6 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-repository-foundation | 4 | ~12min | ~3min |
| 02-core-reference-framework | 2 | ~5min | ~2.5min |
| 03-fi-module-foundation | 4 (complete) | ~9min | ~2.3min |
| 04-fi-advanced-and-integration-prep | 2 (complete) | ~6min | ~3min |
| 05-mm-module-foundation | 4 (complete) | ~8min | ~2min |
| 06-mm-advanced-and-fi-integration | 2 of 3 | ~9min | ~4.5min |

**Recent Trend:**
- Last 5 plans: 04-02 (3min), 05-01..04 (parallel wave), 06-01 (4min), 06-02 (5min)
- Trend: Stable ~2-5min per content-writing plan

*Updated after each plan completion*

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

### Pending Todos

None yet.

### Blockers/Concerns

- Subagent directory permission issue: agents spawned from ~/Claude/General cannot write to ~/Claude/SAPKnowledge. Workaround: execute plans directly from orchestrator level.

## Session Continuity

Last session: 2026-02-17
Stopped at: Completed 06-02-PLAN.md (MM-FI integration: 20-transaction catalog, MIGO 101 trace, MIRO trace, GR/IR clearing, period-end). Phase 6 plan 2 of 3 done.
Resume file: None
