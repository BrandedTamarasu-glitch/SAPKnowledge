---
phase: 03-fi-module-foundation
plan: 01
subsystem: fi-tcodes
tags: [sap, ecc6, fi, general-ledger, accounts-payable, accounts-receivable, asset-accounting, tcodes, transaction-codes]

# Dependency graph
requires:
  - phase: 01-repository-foundation
    provides: repository structure and CLAUDE.md routing files
  - phase: 02-core-reference-framework
    provides: org structure reference and disambiguation rules
provides:
  - 65 verified FI T-codes with menu paths, usage guidance, and gotcha warnings
  - Workflow index mapping 35 process stages to T-codes
  - New GL vs Classic GL bifurcation documented (FS10N/GLT0 vs FAGLB03/FAGLFLEXT)
  - S_ALR report number corrections (87012284=Financial Statements, 87012082=Vendor Balances)
  - F110 APP full 7-step execution sequence
  - AA year-end lifecycle order dependency (AFAB → AJRW → AJAB)
affects: [04-fi-advanced, 05-mm-foundation, 07-sd-foundation, cross-module]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "T-code reference format: frontmatter + workflow index table + submodule sections with ### headings"
    - "Each T-code entry: Menu Path + Usage (1-2 sentences) + Gotcha (where significant)"
    - "Critical corrections called out with CRITICAL prefix in Gotcha fields"
    - "Cross-references between related T-codes (FS10N ↔ FAGLB03, F-41 ↔ F-27)"

key-files:
  created: [modules/fi/tcodes.md]
  modified: []

key-decisions:
  - "Workflow index uses 35-row table format covering all FI process stages, not a prose index"
  - "FS10N labeled as 'Classic GL' despite menu saying '(New)' — important disambiguation for New GL environments"
  - "S_ALR corrections embedded in both the workflow index and the individual T-code Gotcha fields for maximum discoverability"
  - "F110 APP sequence documented inline in the T-code entry rather than a separate process file"
  - "AA year-end order (AFAB → AJRW → AJAB) repeated in all three T-code entries and cross-referenced"

patterns-established:
  - "Module T-code files: YAML frontmatter + workflow index + submodule sections"
  - "Gotcha fields use CRITICAL prefix for the most dangerous/common errors"
  - "Cross-references via 'See also:' in Gotcha fields link related T-codes bidirectionally"

# Metrics
duration: 3min
completed: 2026-02-16
---

# Phase 3 Plan 01: FI T-Code Reference Summary

**65 verified FI T-codes across GL/AP/AR/AA/Reporting with workflow index, New GL bifurcation, and S_ALR identification corrections**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-17T02:26:07Z
- **Completed:** 2026-02-17T02:29:27Z
- **Tasks:** 2 completed
- **Files modified:** 1

## Accomplishments

- Created authoritative FI T-code reference with 65 verified entries covering GL (20), AP (15), AR (13), Asset Accounting (12), and Reporting (5)
- Built 35-row workflow index mapping process stages to T-codes with submodule labels, enabling process-based lookup
- Documented the New GL vs Classic GL bifurcation: FS10N reads GLT0 (may be empty in New GL environments) vs FAGLB03 reads FAGLFLEXT (correct for New GL-active systems)
- Corrected the most dangerous S_ALR misidentification: S_ALR_87012284 = Financial Statements (Balance Sheet/P&L), NOT vendor balances; vendor balances = S_ALR_87012082
- Documented F110 APP with full 7-step execution sequence (FBZP → parameters → proposal → edit → payment run → DME → FBL1N reconcile)
- Documented AA year-end order dependency in all three relevant entries: AFAB must complete before AJAB, with AJRW in between

## Task Commits

1. **Task 1: Frontmatter, workflow index, and GL section (20 T-codes)** — included in `09e12ef` (feat)
2. **Task 2: AP, AR, Asset Accounting, and period-end sections (45 T-codes)** — `09e12ef` (feat: combined commit as specified in plan)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `modules/fi/tcodes.md` — 641 lines; complete FI T-code reference with YAML frontmatter, workflow index, and five submodule sections

## Decisions Made

- Workflow index uses a 35-row table format rather than a prose index, enabling fast scan by process stage
- FS10N labeled as "Classic GL" in both the workflow index and its section heading despite the SAP menu path containing "(New)" — this "(New)" refers to the old "new Enjoy screen" naming convention from the early 2000s, not New GL; users consistently confuse this
- S_ALR corrections appear in three places: workflow index, S_ALR_87012082 Gotcha, and S_ALR_87012284 Gotcha — belt-and-suspenders approach given how frequently these are confused
- F110 APP sequence documented inline in the T-code entry rather than deferring to a separate process file, since the sequence is the most common F110 question
- AJRW Gotcha documents all three-step order dependency even though AJRW is only the middle step, so each AA year-end T-code entry is self-contained

## Deviations from Plan

None — plan executed exactly as written. All 65 T-codes documented per the plan specifications with all required corrections applied.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- modules/fi/tcodes.md is ready for use as the primary FI T-code lookup reference
- The FS10N vs FAGLB03 and S_ALR identification corrections are embedded and will prevent the most common FI query errors
- Next plans in Phase 3 should populate config-spro.md, processes.md, master-data.md, and integration.md to complete the FI module foundation
- Phase 4 (FI Advanced) can reference this file's T-codes for deeper process flow documentation

---
*Phase: 03-fi-module-foundation*
*Completed: 2026-02-16*
