---
phase: 04-fi-advanced-and-integration-prep
plan: 01
subsystem: fi-account-determination
tags: [sap, fi, mm, sd, OBYC, VKOA, account-determination, BSX, WRX, GBB, KOFI]

# Dependency graph
requires:
  - phase: 03-fi-module-foundation
    provides: FI master data, T-codes, SPRO config, and process flows that this file extends
provides:
  - OBYC framework with full determination path (movement type -> OMJJ -> transaction key -> valuation class -> GL)
  - MM GR worked example for movement type 101 (BSX/WRX/PRD with Dr/Cr table)
  - MM GI worked examples for movement types 261 and 551 (GBB modifier system)
  - VKOA framework introduction for KOFI access sequence and key fields
  - FI-only auto posting config (F.05/OBA1 KDB/KDF, OBXU/OBXI cash discount, clearing accounts)
affects:
  - 06-mm-advanced
  - 08-sd-advanced
  - cross-module

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Account determination files use worked Dr/Cr journal entry tables with representative account numbers labeled as examples"
    - "CORRECTION note blocks used for commonly-wrong config paths (OBXU/OBXI vs OBB8)"
    - "Scope boundary notes used to defer deep-dives to the owning phase"

key-files:
  created:
    - modules/fi/account-determination.md
  modified: []

key-decisions:
  - "account-determination.md: cash discount GL accounts = OBXU/OBXI (NOT OBB8); OBB8 is payment terms only"
  - "GBB account modifiers documented in full table (AUF, BSA, INV, VAX, VAY, VBR, VNG) with movement type cross-reference"
  - "PRD behavior for MAP vs standard price materials called out explicitly — most common MM-FI account determination question"
  - "VKOA section scoped to framework only; full VKOA deep-dive deferred to Phase 8 (SD Advanced)"
  - "Cleared GR/IR account OI indicator requirement called out as critical implementation pitfall"

patterns-established:
  - "Account number examples always labeled as 'representative example' to prevent confusion with real chart of accounts"
  - "Both diagnostic path and setup path documented for each config area (OBYC, VKOA)"

# Metrics
duration: 3min
completed: 2026-02-17
---

# Phase 4 Plan 01: Account Determination Summary

**OBYC/VKOA/FI-only automatic posting reference with full MM GR/GI worked examples, GBB modifier table, KOFI 5-level access sequence, and OBXU/OBXI cash discount correction**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-02-17T03:17:17Z
- **Completed:** 2026-02-17T03:19:51Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created 372-line account determination reference covering the full MM-FI integration backbone
- OBYC determination path documented with worked Dr/Cr journal entries for GR (101) and GI (261, 551)
- GBB account modifier table with all 7 modifiers (AUF/BSA/INV/VAX/VAY/VBR/VNG) and movement type references
- VKOA framework introduced with KOFI 5-level access sequence and key fields (KTGRD, material AAG, account keys)
- FI-only automatic postings: F.05/OBA1 (KDB/KDF), OBXU/OBXI (cash discount), and clearing account mechanics

## Task Commits

Each task was committed atomically:

1. **Task 1: Write account-determination.md** - `e3dc55c` (feat)

## Files Created/Modified

- `modules/fi/account-determination.md` — Comprehensive account determination reference: OBYC framework, MM GR/GI walkthroughs, VKOA framework, FI-only auto postings (372 lines)

## Decisions Made

- Cash discount GL account config = OBXU (AP) and OBXI (AR), NOT OBB8. OBB8 is payment terms only. CORRECTION block added.
- GBB modifier table includes all 7 standard modifiers with representative movement types — supports both consultant lookup and learner understanding
- PRD firing condition (standard price S only, not MAP V) documented explicitly — this is the most common MM-FI account determination question
- VKOA scoped to framework introduction only; Phase 8 owns the deep-dive (condition tables, AAG config, billing examples)
- Clearing account OI indicator requirement flagged as critical implementation pitfall

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Account determination backbone complete for Phase 4 FI context
- Plan 04-02 can proceed (next plan in phase 4)
- Phase 6 (MM Advanced) and Phase 8 (SD Advanced) have the OBYC/VKOA framework ready to reference
- VKOA deep-dive is deferred to Phase 8 per scope boundary documented in the file

---
*Phase: 04-fi-advanced-and-integration-prep*
*Completed: 2026-02-17*
