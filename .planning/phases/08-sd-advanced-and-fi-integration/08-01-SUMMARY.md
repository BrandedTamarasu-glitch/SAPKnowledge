---
phase: 08-sd-advanced-and-fi-integration
plan: 01
subsystem: sd-vkoa-walkthrough
tags: [vkoa, account-determination, billing, revenue, erl, ers, evv, erf, mws, pricing-procedure]

# Dependency graph
requires:
  - phase: 04-fi-advanced-and-integration-prep
    provides: VKOA framework in fi/account-determination.md (KOFI access sequence, key fields, account keys)
  - phase: 07-sd-module-foundation
    provides: SD master data (KTGRD/KTGRM field locations), config-spro (pricing condition technique), processes (O2C flow)
provides:
  - VKOA dual-axis reference (by account key and by condition type)
  - Pricing-to-VKOA chain (V/09 -> V/08 -> OVKK -> VF01 -> KOFI -> GL)
  - 8 worked billing-to-GL examples with Dr/Cr entries
  - VKOA 5-step debugging path
  - EVV cash discount timing documentation (payment clearing, not billing) with OBXI alternative
  - KTGRD/KTGRM blank as #1/#2 VKOA failure causes
affects: [08-03-decision-trees, cross-module]

# Tech tracking
tech-stack:
  added: []
  patterns: [dual-axis-reference, worked-example-format, debugging-path-format]

key-files:
  created: [modules/sd/sd-advanced.md]
  modified: []

key-decisions:
  - "VKOA content placed in sd-advanced.md (not fi/account-determination.md) to keep SD perspective separate from FI framework"
  - "EVV documented with both VKOA and OBXI paths since implementations vary"
  - "Intercompany billing kept at foundation level with Phase 12 deferral for deep IV/PI/PD config"

patterns-established:
  - "Dual-axis reference: same data organized by two different keys (account key AND condition type) with cross-references"
  - "Worked examples use consistent format: scenario, Dr/Cr table, representative example labels, source column explaining determination"

# Metrics
duration: 2min
completed: 2026-02-17
---

# Phase 8 Plan 01: SD Advanced — VKOA Walkthrough Summary

**VKOA account determination walkthrough with dual-axis reference (6 account keys, 8 condition types), pricing-to-VKOA chain, 8 worked billing-to-GL examples, and 5-step debugging path**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-17T18:25:27Z
- **Completed:** 2026-02-17T18:28:12Z
- **Tasks:** 1
- **Files created:** 1

## Accomplishments
- Created modules/sd/sd-advanced.md (304 lines) with complete VKOA walkthrough from SD perspective
- Dual-axis reference tables: by account key (ERL/ERS/EVV/ERF/ERU/MWS) and by condition type (PR00/K004/K005/KF00/MWST/RA00)
- Complete pricing-to-VKOA chain: V/09 -> V/08 -> OVKK -> VF01 -> KOFI access sequence -> GL account
- 8 worked billing-to-GL examples with full Dr/Cr entries and representative example account numbers
- EVV cash discount correctly documented as posting at payment clearing time with OBXI alternative path
- KTGRD blank = #1 VKOA failure, KTGRM blank = #2, documented as CRITICAL
- 5-step VKOA debugging path: VF03 -> VKOA simulation -> account key check -> KTGRD/KTGRM -> common failures
- Cross-references fi/account-determination.md for framework (no duplication)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create sd-advanced.md with VKOA account determination walkthrough** - `66c4ebd` (feat)

## Files Created/Modified
- `modules/sd/sd-advanced.md` - VKOA walkthrough with dual-axis reference, pricing-to-VKOA chain, 8 worked examples, debugging path

## Decisions Made
- VKOA content placed in sd-advanced.md to keep SD perspective separate from FI framework in account-determination.md
- EVV documented with both VKOA and OBXI paths since implementation choice varies
- Intercompany billing kept at foundation level with explicit deferral to Phase 12 for deep IV/PI/PD configuration

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- sd-advanced.md ready to receive decision trees and troubleshooting content in Plan 03
- VKOA walkthrough provides the worked examples that Plan 02 (SD-FI integration) can reference

---
*Phase: 08-sd-advanced-and-fi-integration*
*Completed: 2026-02-17*
