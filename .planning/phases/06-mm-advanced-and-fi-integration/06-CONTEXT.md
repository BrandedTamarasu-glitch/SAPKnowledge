---
module: mm
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: "2026-02-17"
phase: 06-mm-advanced-and-fi-integration
created: 2026-02-17
status: final
areas_discussed: OBYC walkthrough depth, Decision tree topics, Troubleshooting format, MM-FI integration scope
---

# Phase 6: MM Advanced & FI Integration - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Document OBYC account determination with full worked examples, MM decision trees for procurement and inventory scenarios, MM troubleshooting with symptom-first lookup, and complete MM-FI integration point coverage. This phase makes MM-FI the first fully documented cross-module integration in the knowledge base.

</domain>

<decisions>
## Implementation Decisions

### OBYC Walkthrough Depth
- Dual-axis structure: organized by both movement types AND transaction keys, with cross-references between them
- Extended 10+ worked examples with full debit/credit GL account entries (GR to stock 101, GR to consumption 201, GI to cost center, invoice with PRD variance, stock transfer 301, subcontracting 541, split valuation, consignment, returns, scrapping, revaluation, price changes)
- Include valuation class setup guidance: OMSK valuation class design, OMJJ account category reference, and how they feed into OBYC
- Include full OBYC debugging path: simulation and account determination trace for diagnosing missing GL assignments

### Decision Tree Topics
- Cover both procurement AND inventory decision trees
- Procurement trees: valuation approach (standard vs MAP), release strategy design, source determination, vendor evaluation setup
- Inventory trees: split valuation, batch management, serial numbers, consignment, special stock types
- Include MRP decision guidance: MRP type selection (PD vs VB vs VV), lot sizing procedures, planning strategy (MTS vs MTO)
- Include tolerance key decision guidance: which tolerance keys (PP, PE, BD, AN, etc.) for which business scenarios with recommended values
- Follow FI Phase 4 format: question-driven flow leading to recommendation, with comparison tables where relevant

### Troubleshooting Format
- Symptom-first lookup organization: entries organized by what user sees (error messages, blocked documents, wrong postings)
- Target 10-12 entries (broader than FI's 7 due to MM's wider scope: purchasing, inventory, invoice verification, MRP)
- Include actual SAP message IDs (M7, ME class numbers) so users can search by exact error
- Self-contained entries: full diagnosis + resolution inline, no jumping to other files (match FI Phase 4 pattern)
- Include diagnostic T-codes (MB51, MBPM, MR11, OMJJ check) in each entry's resolution path

### MM-FI Integration Scope
- Integration point catalog listing all MM-FI touchpoints (GR, GI, IV, GR/IR clearing, period-end) plus detailed transaction traces for key transactions
- Populate existing modules/mm/integration.md (not a new file)
- Transaction-trace format for key scenarios: "When you post MIGO 101, here's exactly what happens in FI"
- Full GR/IR clearing coverage: account setup, F.13 automatic clearing, MR11 maintenance/revaluation, period-end GR/IR analysis
- MM period-end FI impacts: material ledger actual costing run (CKMLCP), balance sheet revaluation (MR21/MR22), MMPV period close, and their FI postings

### Claude's Discretion
- Exact number of decision trees per category (procurement vs inventory)
- Which specific SAP message IDs to include in troubleshooting
- Level of detail in transaction trace diagrams
- Whether to create an mm-advanced.md file (like fi-advanced.md) or split decision trees and troubleshooting differently

</decisions>

<specifics>
## Specific Ideas

- OBYC should be navigable from either direction: "I have movement type 101, what posts?" AND "What does transaction key BSX control?"
- Follow the established Phase 4 pattern for decision trees and troubleshooting (fi-advanced.md is the template)
- GR/IR clearing account is a critical integration pitfall already noted in Phase 4 (OI indicator required for F.13) — build on that foundation
- The "what happens in FI when I post MIGO with movement type 101" question from the success criteria should be directly answerable

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-mm-advanced-and-fi-integration*
*Context gathered: 2026-02-17*
