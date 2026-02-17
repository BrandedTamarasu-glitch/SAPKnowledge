# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-16)

**Core value:** When someone asks Claude "how do I do X in SAP," it gives the correct ECC 6 answer — right transaction, right config path, right module interactions.
**Current focus:** Phase 3 - FI Module Foundation

## Current Position

Phase: 3 of 12 (FI Module Foundation) — In progress
Plan: 2 of 4 in Phase 3
Status: 03-01 (FI T-codes) and 03-02 (FI master data) complete; 03-03 and 03-04 remaining
Last activity: 2026-02-17 — Completed 03-02-PLAN.md (FI master data: 11 table segments, 4 field-location corrections)

Progress: [███░░░░░░░] 25%

(3 of 12 phases partially complete; 8 known plans have SUMMARY.md)

## Performance Metrics

**Velocity:**
- Total plans completed: 8 (4 Phase 1 + 2 Phase 2 + 2 Phase 3)
- Average duration: ~2min
- Total execution time: ~0.4 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-repository-foundation | 4 | ~12min | ~3min |
| 02-core-reference-framework | 2 | ~5min | ~2.5min |
| 03-fi-module-foundation | 2 (of 4) | ~5min | ~2.5min |

**Recent Trend:**
- Last 5 plans: 02-02 (1min), 02-01 rerun (2min), 03-01 (3min), 03-02 (2min)
- Trend: Stable ~2-3min per content-writing plan

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

### Pending Todos

None yet.

### Blockers/Concerns

- Subagent directory permission issue: agents spawned from ~/Claude/General cannot write to ~/Claude/SAPKnowledge. Workaround: execute plans directly from orchestrator level.

## Session Continuity

Last session: 2026-02-17
Stopped at: Completed 03-02-PLAN.md (FI master data reference, 11 table segments). Phase 3 plan 2 of 4 done.
Resume file: None
