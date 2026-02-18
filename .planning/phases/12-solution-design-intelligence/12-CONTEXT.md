# Phase 12: Solution Design Intelligence - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Layer solution design patterns, scenario playbooks, and operational checklists on top of the complete module and integration foundation. This is the capstone phase — transforms the knowledge base from reference material into actionable implementation guidance.

</domain>

<decisions>
## Implementation Decisions

### Design Pattern Depth
- Implementation guide format: business requirement → recommended approach → T-codes to configure → master data setup → testing steps (cookbook style)
- Focus on cross-module scenarios (requirements that span MM/SD/FI/CO), not single-module config dilemmas
- Build on existing module decision trees: design patterns are the higher-level "when to use what" layer, pointing to module decision trees for config-level choices
- Target 10-15 patterns covering the most common cross-module business requirements

### Scenario Playbook Scope
- All eight scenarios from roadmap: consignment, intercompany sales, third-party processing, subcontracting, split valuation, special procurement, batch management, serial numbers
- Playbooks are deep-dive implementation walkthroughs: full config steps, master data setup, cross-module perspective
- Each playbook includes 2-3 test scenarios showing how to verify the config works (e.g., "Create consignment fill order with VA01, verify stock at customer site with MB52")
- Playbooks are the definitive deep-dive for their scenario; existing module mentions (SD processes.md, MM processes.md) become brief introductions pointing to the playbook
- Playbooks differ from design patterns: patterns give overview + decision, playbooks give full implementation walkthrough

### Operational Checklists
- Checklists are the actionable operator version of the R2R E2E flow from Phase 11 (different audience: operator vs architect)
- Cover both month-end and year-end close (year-end adds fiscal year rollover, balance carryforward, depreciation close)
- Include relative timing guidance using business days (Day 1, Day 2, Day 3) — sequence and relative timing are universal even though actual dates vary
- Markdown checkbox format: `- [ ] Step 1: Run MMPV (T-code) — close MM posting period`

### File Organization
- All content lives in cross-module/ alongside the E2E files from Phase 11
- Design patterns: single file cross-module/design-patterns.md with all 10-15 patterns as sections
- Playbooks: single file cross-module/playbooks.md with all 8 scenarios as sections (grouped: 4 process + 4 config)
- Checklists: separate from R2R (different audience); location in cross-module/
- Full navigation update: routing table rows for design patterns, playbooks, and checklists; cross-module/CLAUDE.md index updated

### Claude's Discretion
- Exact selection of which 10-15 design patterns to include
- How to structure each playbook section internally (step ordering, level of config detail)
- Whether checklists are one file (month-end + year-end) or two separate files
- How much to expand existing module process file references vs keeping playbooks self-contained
- Whether to update existing module process files to point to playbooks

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches matching the patterns established in Phases 3-11.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 12-solution-design-intelligence*
*Context gathered: 2026-02-18*
