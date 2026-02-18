---
phase: 12-solution-design-intelligence
plan: "02"
subsystem: content-knowledge-base
tags: [sap, ecc6, cross-module, playbooks, consignment, intercompany, third-party, subcontracting, split-valuation, batch-management, serial-numbers]

requires:
  - phase: 11-cross-module-integration
    provides: mm-sd-integration.md with consignment/third-party/subcontracting foundation; record-to-report.md
  - phase: 06-mm-advanced-and-fi-integration
    provides: mm-advanced.md decision trees 6-9 (split valuation, batch, serial, subcontracting)
  - phase: 08-sd-advanced-and-fi-integration
    provides: sd-advanced.md VKOA walkthrough, intercompany billing foundation

provides:
  - cross-module/playbooks.md with 8 complete scenario playbooks (4 process + 4 config)
  - Deep-dive implementation walkthroughs for consignment, intercompany, third-party, subcontracting
  - Deep-dive implementation walkthroughs for split valuation, special procurement keys, batch management, serial numbers
  - 2-3 concrete test scenarios per playbook with specific T-codes and expected results
  - Cross-module synthesis layer unavailable in individual module files

affects:
  - 12-03 (checklists plan — references playbooks as the definitive scenario reference)
  - Any user asking how to implement complex SAP ECC 6 scenarios end-to-end

tech-stack:
  added: []
  patterns:
    - "Playbooks as synthesis layer: reference module files for config detail, add cross-module perspective and test scenarios"
    - "Each playbook section answers questions module files do NOT answer: how modules interact, FI account flow, CO treatment, how to verify"

key-files:
  created:
    - cross-module/playbooks.md
  modified:
    - scripts/validate.py

key-decisions:
  - "Playbooks use cross-reference pattern — point to module files for config detail (OMWC config chain in mm-advanced.md DT 6), add cross-module synthesis not available there"
  - "All 8 playbooks written in single commit — Tasks 1 and 2 combined since Task 2 appended to file started in Task 1"
  - "validate.py updated to accept playbooks and checklists content types (Rule 2: missing critical functionality)"
  - "Intercompany billing covers full IV billing type config, partner functions PI, VKOA for IC revenue — completing the Phase 8 deferral"
  - "Special procurement key 20 (phantom) documented with MRP behavior for no procurement element generation"
  - "FI account flow documented for every movement type in each playbook (541 no FI = explicit, not missing)"

patterns-established:
  - "Playbook structure: Business Context → Prerequisites → Config Walkthrough (#### steps) → Master Data → Process Flow (table) → Test Scenarios → Cross-Module Perspective → Common Pitfalls"
  - "Test scenarios: specific T-codes, specific field values, expected results — not generic descriptions"
  - "Cross-Module Perspective: always covers FI account assignment, CO assignment, and integration cross-references to module files"

requirements-completed: [SOLN-02, SOLN-03]

duration: 15min
completed: 2026-02-18
---

# Phase 12 Plan 02: Cross-Module Scenario Playbooks Summary

**8 deep-dive ECC 6 scenario playbooks covering consignment (vendor+customer), intercompany IV billing, third-party TAS, subcontracting 541/543, split valuation OMWC, special procurement keys (10/20/30/40), batch management FEFO, and serial number OISO profiles — each with concrete test scenarios and cross-module FI/CO perspective**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-02-18T15:04:12Z
- **Completed:** 2026-02-18T15:19:00Z
- **Tasks:** 2 (both completed in single commit — Task 2 appended to same file)
- **Files modified:** 2

## Accomplishments

- Created `cross-module/playbooks.md` (1190 lines) with all 8 playbooks
- Each playbook covers: Business Context, Prerequisites, Config Walkthrough with SPRO paths and T-codes, Master Data Setup table, Process Flow table with movement types and FI impact, 2-3 Test Scenarios with specific commands and expected results, Cross-Module Perspective covering FI accounts and CO treatment, Common Pitfalls
- Added "playbooks" and "checklists" content types to validate.py — enables validation of Phase 12 Plan 03 (checklists) without a second code change
- Cross-module synthesis: playbooks reference module files for config detail (e.g., "See modules/mm/mm-advanced.md Decision Tree 6") and add the integration perspective that no single module file contains

## Task Commits

1. **Tasks 1 + 2: Create playbooks.md with all 8 playbooks** - `11a76e5` (feat)

**Plan metadata:** (created below)

## Files Created/Modified

- `cross-module/playbooks.md` — 8 scenario playbooks: Consignment Stock, Intercompany Sales, Third-Party Drop Shipment, Subcontracting, Split Valuation, Special Procurement Keys, Batch Management, Serial Number Management
- `scripts/validate.py` — Added "playbooks" and "checklists" to VALID_CONTENT_TYPES

## Decisions Made

- Used cross-reference pattern throughout: "Configure per modules/mm/mm-advanced.md DT 6" instead of duplicating OMWC walkthrough. Playbooks add what module files cannot: cross-module interaction, FI account flows, and test scenarios.
- validate.py updated to accept "playbooks" content type (Rule 2 auto-fix — missing critical functionality for validation to pass). Also pre-added "checklists" since Plan 03 will need it.
- Intercompany billing playbook completes the Phase 8 deferral: full IV billing type config, partner function PI, VKOA for IC revenue/expense in both company codes — unavailable in any single module file.
- Movement 541 (subcontracting) explicitly documented as having NO FI posting in the process flow table and Common Pitfalls — this is the most frequently misunderstood aspect of subcontracting.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added "checklists" to validate.py alongside "playbooks"**
- **Found during:** Task 1 (validate.py update for playbooks content type)
- **Issue:** Plan 03 (checklists.md) will need "checklists" content type — updating validate.py now prevents a blocking issue in Plan 03
- **Fix:** Added both "playbooks" and "checklists" to VALID_CONTENT_TYPES in validate.py
- **Files modified:** scripts/validate.py
- **Verification:** validate.py passes for playbooks.md; checklists type pre-registered
- **Committed in:** 11a76e5 (combined task commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Pre-registering checklists content type eliminates a future blocking issue. No scope creep.

## Issues Encountered

None — content creation proceeded smoothly using existing module files as reference material.

## Next Phase Readiness

- Plan 02 complete — playbooks.md is the definitive implementation reference for all 8 scenarios
- Plan 03 (operational checklists) can proceed: validate.py already updated, cross-module/CLAUDE.md and sap-routing.md navigation updates are planned in Plan 03

---
*Phase: 12-solution-design-intelligence*
*Completed: 2026-02-18*
