---
module: sd
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: "2026-02-17"
phase: 08-sd-advanced-and-fi-integration
created: 2026-02-17
status: final
areas_discussed: VKOA walkthrough depth, Decision trees scope, Troubleshooting format, SD-FI integration scope
---

# Phase 8: SD Advanced & FI Integration - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Document VKOA account determination, SD decision trees (including pricing foundations), troubleshooting, and complete SD-FI integration point. This mirrors Phase 6 (MM Advanced & FI Integration) structurally, applied to the SD module. The VKOA framework intro from Phase 4 (fi/account-determination.md) gets its full deep-dive here.

</domain>

<decisions>
## Implementation Decisions

### VKOA Walkthrough Depth
- Dual-axis approach like OBYC: by account key (ERL, ERS, EVV, ERF, ERU, MWS) AND by condition type (PR00, MWST, KF00, K004, K005, RA00)
- Cross-reference to fi/account-determination.md VKOA intro section — extend, don't duplicate the framework
- 8-10 worked billing-to-GL examples covering: standard revenue (ERL), sales deductions (ERS), cash discount (EVV), freight revenue (ERF), tax (MWS), credit memo, rebate accrual, intercompany
- Full pricing-to-VKOA chain: pricing procedure → condition type → account key assignment (V/08) → VKOA lookup → GL account. Show how condition type config feeds VKOA determination.
- Full VKOA debugging path: VF03 billing analysis → VKOA simulation → check account key assignment → verify GL account → common failure points

### Decision Trees Scope
- 12 decision trees (matching Phase 6 MM count for consistency)
- Multiple pricing-related trees (~3-4): pricing procedure design (which condition types to include), access sequence strategy, condition exclusion groups, pricing determination assignment (OVKK)
- Dedicated copy control decision tree: when to use requirements, data transfer routines, copy control at header vs item, common scenarios (VTAA/VTLA/VTFL/VTAF)
- Remaining trees cover: partner determination, availability check, output determination, credit management, item category determination, and other key SD config decisions
- Q&A routing format with comparison tables and config implications inline (same format as Phase 6)

### Troubleshooting Format
- 12 troubleshooting entries (matching Phase 6 MM count)
- Include SAP message IDs (V1/V2/VF/VK class) where applicable
- Dedicated entries for SD-specific pain points: incompletion procedure issues, delivery blocks, billing blocks, credit blocks — these are daily SD support topics
- Each entry self-contained with full resolution path inline (same pattern as Phase 6 — no cross-file lookups needed)
- Diagnostic T-codes referenced inline (VF03, VA03, VL03N, V/08, VKOA, etc.)

### SD-FI Integration Scope
- Full VF01 billing-to-FI trace: billing doc (VBRK/VBRP) → VKOA determination → FI document (BKPF/BSEG) → revenue/COGS/tax postings → customer open item. Show tables and fields at each step.
- Full SD-FI integration point catalog (like the 20-entry MM-FI catalog): all SD-FI touchpoints with billing types, VKOA keys, document types, GL impact, plus special scenarios (rebate accruals, intercompany, returns)
- Moderate depth on revenue recognition: basic revenue posting via VKOA (ERL), deferred revenue setup, milestone billing basics, relationship between billing plan types and revenue timing. Defer complex revenue recognition (POC) to Phase 12.
- SD period-end FI impacts: rebate settlement (VBO1/VBOF), revenue accruals, billing due list cleanup (VF04), credit management reset, and their FI posting impacts

### Claude's Discretion
- Exact distribution of the 12 decision trees across SD subdomains (beyond the specified pricing and copy control trees)
- Level of detail on intercompany billing in VKOA examples (foundation vs deep-dive)
- Whether to include a separate "common VKOA misconfigurations" section or fold into troubleshooting
- How to organize the sd-advanced.md file sections (VKOA first vs decision trees first)

</decisions>

<specifics>
## Specific Ideas

- Phase 6 (MM Advanced) set the structural pattern: sd-advanced.md (VKOA walkthrough + decision trees + troubleshooting) and integration.md (SD-FI integration). Follow the same pattern for consistency.
- The pricing-to-VKOA chain is uniquely important in SD — it's the #1 question SD consultants ask about account determination ("how does my pricing procedure end up in FI?")
- Credit management was kept at foundation level in Phase 7 (config-spro.md). Phase 8 decision trees should fill in the design guidance that was deferred.
- The VKOA framework intro already exists in fi/account-determination.md from Phase 4 — the Phase 8 content extends this, not replaces it.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-sd-advanced-and-fi-integration*
*Context gathered: 2026-02-17*
