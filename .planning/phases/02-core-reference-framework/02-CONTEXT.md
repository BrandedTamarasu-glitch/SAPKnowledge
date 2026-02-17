# Phase 2: Core Reference Framework - Context

**Gathered:** 2026-02-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Create always-available org structure and disambiguation framework that all module content references. Delivers two foundational documents: (1) a comprehensive org structure reference covering all org units with full field detail, and (2) an expanded ECC 6 vs S/4HANA disambiguation framework with inline callouts and summary table. Content writing is in scope — implementation decisions (format, depth, coverage) are settled here.

</domain>

<decisions>
## Implementation Decisions

### Org Structure Depth

- **Full field explanations** per org unit — every configurable field with description and typical values
- **Include common patterns** — typical 1:many relationship examples with rationale (e.g., "most companies use 1 company code per country for tax reporting")
- **Include cardinality rules** — explicit 1:1, 1:many, many:many notation for each relationship
- **Include SAP table names** — the primary table storing each org unit (e.g., Company Code → T001, Plant → T001W)
- **Include creation T-codes** — document the T-codes used to create and display each org unit (e.g., OX02 for company code)
- **Explain level-specific config** — what is configured AT each org level (e.g., "fiscal year variant defined at company code level, not client level")
- **Include cross-module assignment consequences** — downstream financial impact of org assignments (e.g., "Sales Org links to Company Code, so SD billing postings flow to FI under that company code")

### S/4 Disambiguation Format

- **Both inline callouts AND summary table** — `> S/4HANA: [difference]` blockquotes within each org unit section, PLUS a consolidated table at the end for scanning all differences at once
- **Always flag significant differences** — proactively surface ECC vs S/4 differences wherever they occur, don't wait for user to ask
- **Expand sap-disambiguation.md** — add org-structure-specific rows for units that behave differently (Business Partner replaces vendor/customer masters, etc.)
- **Blockquote style:** `> S/4HANA: [difference]` — consistent with existing sap-disambiguation.md style

### Coverage Boundaries

**Core org units (in scope):**
- Client, Company Code, Plant, Storage Location
- Sales Organization, Distribution Channel, Division (= Sales Area)
- Purchasing Organization, Purchasing Group
- Controlling Area, Cost Center, Profit Center

**Extended units (also in scope for Phase 2):**
- Business Area — optional cross-company reporting unit, frequently misunderstood
- Profit Center — CO-based reporting unit alongside cost centers
- Segment — IFRS 8 reporting segments (New GL feature, note ECC 6 constraint)
- Functional Area — cost of sales accounting (document even if niche)

### Content Format

- **ASCII tree for hierarchy + tables for details** — tree diagram shows structure/relationships, then a markdown table per org unit with: field name, description, typical values, SAP table, creation T-code, S/4 differences
- **Single comprehensive file** — one `reference/org-structure.md` (not split by domain) for simple loading and reference
- **Explicit cross-references** — use "See `modules/fi/tcodes.md`" style links pointing forward to module content added in Phases 3-10
- **Confidence: high** — org structure is stable ECC 6 content, mark as `confidence: high` in frontmatter, verified against SAP Help Portal

### Claude's Discretion

- Exact table column order and visual formatting within markdown constraints
- How to handle org units with no S/4 differences (omit callout vs explicit "no change in S/4")
- Token budget optimization — if the full org-structure.md exceeds the file size budget from Phase 1 validation, Claude can decide how to split or summarize

</decisions>

<specifics>
## Specific Ideas

- The existing `sap-org-structure.md` (Phase 1) already has the ASCII hierarchy tree — Phase 2 should build on/extend it, not duplicate it
- Table format should mirror how SAP consultants actually reference this content — field name | description | typical value | table is the standard pattern
- The disambiguation callouts should be specific, not vague (e.g., "> S/4HANA: Vendor master replaced by Business Partner (BP) — use transaction BP, stored in BUT000" not "> S/4HANA: Uses Business Partner")

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-core-reference-framework*
*Context gathered: 2026-02-16*
