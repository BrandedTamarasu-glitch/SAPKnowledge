---
phase: 02-core-reference-framework
plan: 01
subsystem: reference
tags: [sap, ecc6, org-structure, company-code, plant, controlling-area, profit-center, segment]

# Dependency graph
requires:
  - phase: 01-repository-foundation
    provides: Reference directory structure, CLAUDE.md index files, always-loaded rules files
provides:
  - Comprehensive org structure reference for all 16 ECC 6.0 org units (reference/org-structure.md)
  - Field tables, T-codes, creation/display transactions for every org unit
  - Assignment Rules table with cardinality and T-codes for all org unit relationships
  - Cross-Module Consequences table explaining downstream FI impact of each org assignment
  - Consolidated S/4HANA Differences Summary table at org-structure level
  - Updated reference index (reference/CLAUDE.md) with org-structure.md entry
  - Cross-reference from always-loaded sap-org-structure.md rules file
affects:
  - 03-fi-module (uses org structure context for company code, chart of accounts, fiscal year variant)
  - 04-mm-module (plant, storage location, purchasing org/group)
  - 05-sd-module (sales org, distribution channel, division, sales area)
  - 06-co-module (controlling area, cost center, profit center, segment)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reference files use YAML frontmatter with module/content_type/ecc_version/confidence/last_verified"
    - "Org unit subsections follow table-first pattern: fields table, then Table/Create/Display bold line, then configured-here/common-pattern/cross-module-impact"
    - "S/4HANA callouts as blockquotes only where significant differences exist (omitted for unchanged org units)"
    - "Consolidated S/4HANA summary table at document end for quick comparison"

key-files:
  created:
    - reference/org-structure.md
  modified:
    - reference/CLAUDE.md
    - .claude/rules/sap-org-structure.md

key-decisions:
  - "Segment org unit carries CRITICAL ECC 6 NOTE about requiring New GL + document splitting — important disambiguation since S/4HANA makes this automatic"
  - "Sales Area documented as special non-table subsection (not a separate DB table, it is a combination key) to prevent confusion"
  - "Purchasing Org three-assignment-mode pattern documented inline to capture common implementation question"

patterns-established:
  - "Org unit reference pattern: field table → Table/T-codes → configured-here → common pattern → cross-module impact → optional S/4 callout"
  - "Cross-reference at bottom of rules files pointing to comprehensive reference doc"

# Metrics
duration: 2min
completed: 2026-02-16
---

# Phase 2 Plan 01: Org Structure Reference Summary

**16 ECC 6.0 org units documented with field tables, T-codes, cardinality rules, cross-module FI consequences, inline S/4HANA callouts, and consolidated S/4 differences summary — reference/org-structure.md is 18,276 characters**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-17T01:41:29Z
- **Completed:** 2026-02-17T01:43:30Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created reference/org-structure.md with all 16 org units (12 core + 4 extended), each with field table, table name, create/display T-codes, configured-here details, common pattern, and cross-module impact
- Added Assignment Rules table covering all 12 org unit relationships with From/To/Cardinality/T-Code columns
- Added Cross-Module Consequences table explaining downstream FI impact for each key assignment
- Inline S/4HANA callouts for Company Code, Controlling Area, Profit Center, Business Area, Segment, and Functional Area
- Consolidated S/4HANA Differences Summary table at document end
- Updated reference/CLAUDE.md File Index and When to Use section
- Added cross-reference line to .claude/rules/sap-org-structure.md pointing to comprehensive reference

## Task Commits

Each task was committed atomically:

1. **Task 1: Create reference/org-structure.md** - `208b996` (feat)
2. **Task 2: Update reference index and rules cross-ref** - `153b70b` (feat)

**Plan metadata:** (this commit — docs: complete plan)

## Files Created/Modified

- `reference/org-structure.md` — Comprehensive 16-org-unit reference, 18,276 chars, all field tables, T-codes, cardinality, S/4 callouts
- `reference/CLAUDE.md` — Added org-structure.md to File Index table and When to Use bullet list
- `.claude/rules/sap-org-structure.md` — Added cross-reference to reference/org-structure.md at end of file

## Decisions Made

- Sales Area documented as a special non-table subsection (it is a combination key VKORG+VTWEG+SPART, not an independent org unit with its own master data table) — prevents common confusion
- Segment org unit includes a "CRITICAL ECC 6 NOTE" highlighting the New GL + document splitting prerequisite, because this is a frequent source of mistakes when migrating from Classic GL
- Purchasing Org documents all three assignment modes (CC-specific, cross-plant, cross-CC) inline, as this pattern answers a very common implementation question

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- reference/org-structure.md is the foundational org structure document for Phases 3-12
- All module content in MM/SD/FI/CO can reference org units by linking to this file
- Phase 3 (FI module) can immediately reference company code, chart of accounts, fiscal year variant details
- Phase 4 (MM module) can immediately reference plant, storage location, purchasing org/group details
- No blockers or concerns

---
*Phase: 02-core-reference-framework*
*Completed: 2026-02-16*
