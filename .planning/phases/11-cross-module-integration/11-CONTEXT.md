# Phase 11: Cross-Module Integration - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Complete integration coverage with MM-SD touchpoints and deliver end-to-end process flows (Procure-to-Pay, Order-to-Cash, Record-to-Report) spanning multiple modules. Also create cross-module/CLAUDE.md index and update routing table.

</domain>

<decisions>
## Implementation Decisions

### E2E Flow Depth
- Step-by-step with every T-code in sequence — consultant implementation guide level
- Focus on integration handoffs between modules (complement existing module process files, don't re-document)
- ASCII document chain at the top of each E2E flow showing the document creation sequence (e.g., PO → GR mat doc → IR doc → FI invoice → payment doc)
- Record-to-Report covers full cross-module period-end close: MM cutoffs → SD cutoffs → CO allocations/settlement → FI close, with ordering dependencies

### MM-SD Integration Scope
- Core three: availability check (ATP), goods issue for delivery, returns
- Extended: consignment (fills/returns), stock transport orders, third-party processing, subcontracting (SD order triggers MM procurement)
- Lives in cross-module/mm-sd-integration.md (new file, not in module integration.md files)
- ATP: include different check types (stock check, planned receipts, delivery scheduling) and how SD triggers each
- Returns: full reverse trace (SD return order → return delivery → GR back to stock → credit memo) showing every document and module handoff

### Cross-Reference Strategy
- Inline brief + pointer: one-line summary of the step inline, then "See modules/xx/file.md Section X for full detail"
- Each E2E file includes a Prerequisites reading list at the top (which module files to read for full detail)
- Update sap-routing.md with rows for E2E process queries (e.g., "full P2P flow" → cross-module/)
- Create cross-module/CLAUDE.md as index file (same format as module CLAUDE.md files)
- Add "See Also" cross-references to existing module integration.md files pointing to new E2E and MM-SD content

### File Organization
- One file per E2E process: cross-module/procure-to-pay.md, cross-module/order-to-cash.md, cross-module/record-to-report.md
- Replace existing Phase 1 template files in-place (same filenames, overwrite with full content)
- MM-SD integration lives in cross-module/mm-sd-integration.md (flat, alongside E2E files)
- cross-module/CLAUDE.md follows same format as module CLAUDE.md files (frontmatter + File Index table with Read When guidance)

### Claude's Discretion
- Exact ASCII document chain diagram style
- How much ATP configuration detail to include vs keeping it integration-focused
- Whether consignment and STO get their own sections or are subsections of the main MM-SD flow
- Level of detail in period-end ordering dependencies for R2R

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches matching the patterns established in Phases 3-10.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 11-cross-module-integration*
*Context gathered: 2026-02-17*
