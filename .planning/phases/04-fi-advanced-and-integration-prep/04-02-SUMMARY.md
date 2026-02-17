---
phase: 04-fi-advanced-and-integration-prep
plan: 02
subsystem: fi-decision-trees-troubleshooting
tags: [sap, fi, ecc6, new-gl, parallel-accounting, document-splitting, asset-accounting, f110, troubleshooting, decision-trees]

# Dependency graph
requires:
  - phase: 03-fi-module-foundation
    provides: tcodes.md, config-spro.md, processes.md, master-data.md — all cross-referenced in the troubleshooting section
  - phase: 04-fi-advanced-and-integration-prep
    provides: plan 01 (account-determination.md) — added to CLAUDE.md File Index in this plan

provides:
  - 7 FI configuration decision trees with Q&A routing and comparison tables
  - CRITICAL clarification that document splitting is not parallel accounting
  - 7 implementation pitfalls with prevention guidance
  - 7 troubleshooting symptoms with self-contained resolution paths
  - CLAUDE.md File Index updated with both Phase 4 files

affects: [05-mm-foundation, cross-module]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Decision tree format: Q&A routing (yes/no questions) + comparison table (Approach/When to Use/Config/Trade-offs)"
    - "Troubleshooting split into two audiences: pitfalls (implementors) and symptoms (support consultants)"
    - "CRITICAL CLARIFICATION pattern for the most dangerous conceptual errors (doc splitting != parallel accounting)"

key-files:
  created: [modules/fi/fi-advanced.md]
  modified: [modules/fi/CLAUDE.md]

key-decisions:
  - "Document splitting is NOT a parallel accounting approach — this CRITICAL CLARIFICATION is in Decision Tree 2 and must be preserved in all future FI content"
  - "Troubleshooting entries are self-contained (full resolution path inline) to avoid requiring multiple file lookups"
  - "Cross-references to tcodes.md, config-spro.md, and processes.md embedded where relevant but not required to resolve the issue"
  - "Each decision tree includes config implications inline (not just pointers to config-spro.md)"

patterns-established:
  - "Decision tree self-containment: config path included per approach, not deferred to config-spro.md"
  - "Symptom diagnosis format: Root Cause ordered check list (check in this order) ensures correct diagnostic sequence"

# Metrics
duration: 3min
completed: 2026-02-17
---

# Phase 4 Plan 02: FI Decision Trees & Troubleshooting Summary

**7 FI configuration decision trees (Q&A + comparison tables) and 14-entry dual-audience troubleshooting guide covering New GL, parallel accounting, document splitting, asset year-end, and F110 payment issues.**

## Performance

- **Duration:** 3min
- **Started:** 2026-02-17T03:20:36Z
- **Completed:** 2026-02-17T03:23:35Z
- **Tasks:** 2 completed
- **Files modified:** 2

## Accomplishments

- Created modules/fi/fi-advanced.md (367 lines) with 7 decision trees, each having Q&A routing + comparison table
- Embedded CRITICAL CLARIFICATION that document splitting is NOT a parallel accounting approach in Decision Tree 2 — one of the most commonly confused FI concepts
- Wrote 7 implementation pitfalls (Mistake/Why it fails/Prevention/Cross-reference) and 7 troubleshooting symptoms (Symptom/Root Cause/Resolution), all self-contained
- Updated CLAUDE.md File Index with correct Read When guidance for both account-determination.md and fi-advanced.md

## Task Commits

Each task was committed atomically:

1. **Task 1: Write fi-advanced.md (decision trees section)** — not committed separately per plan instructions (Tasks 1+2 committed together)
2. **Task 2: Append troubleshooting, update CLAUDE.md, commit** — `2235122` (feat)

**Plan metadata:** committed with task 2

## Files Created/Modified

- `modules/fi/fi-advanced.md` — 7 decision trees + 7 pitfalls + 7 symptoms (367 lines, YAML frontmatter with all 6 required fields)
- `modules/fi/CLAUDE.md` — File Index updated with account-determination.md and fi-advanced.md rows

## Decisions Made

1. **Document splitting distinction:** CRITICAL CLARIFICATION that document splitting is NOT parallel accounting placed prominently in Decision Tree 2. This is the #1 conceptual error in FI configuration and must survive in all future documentation.

2. **Self-contained troubleshooting:** Each entry includes the full resolution path inline. Cross-references to tcodes.md and config-spro.md are provided for additional context but are not required to resolve the issue.

3. **Tasks 1+2 committed together:** Per plan instructions, Task 1 (decision trees) was not committed separately — both tasks were committed in a single atomic commit once the full file was written and CLAUDE.md was updated.

## Deviations from Plan

None — plan executed exactly as written.

## Next Phase Readiness

- modules/fi/fi-advanced.md is complete and indexed in CLAUDE.md
- Phase 4 is now complete (both 04-01 account-determination.md and 04-02 fi-advanced.md delivered)
- Phase 5 (MM Foundation) can proceed without dependencies on Phase 4
