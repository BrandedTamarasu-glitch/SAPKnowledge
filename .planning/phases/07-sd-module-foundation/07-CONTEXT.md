---
module: sd
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: "2026-02-17"
phase: 07-sd-module-foundation
created: 2026-02-17
status: final
areas_discussed: T-code coverage scope, Master data structure, Order-to-cash process depth, SPRO configuration scope
---

# Phase 7: SD Module Foundation - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver complete SD reference covering transactions, configuration, processes, and master data for order-to-cash. This is the third of four module foundations (after FI and MM), following the same structural patterns established in Phases 3 and 5.

</domain>

<decisions>
## Implementation Decisions

### T-code Coverage Scope
- Full breadth across all SD submodules: Sales (VA01-VA03), Shipping/Delivery (VL01N-VL06), Billing (VF01-VF04), Pricing (VK11-VK13), Output Determination (VV31-VV33, NACE), Credit Management (FD32, VKM1-VKM5), Returns, Rebates (VBO1-VBO3), Foreign Trade, Batch Determination
- Target 65-80 T-codes (upper range due to SD's broader submodule coverage)
- Follow the same format as FI and MM: frontmatter + workflow index table + ### submodule sections
- Pricing T-codes should include condition technique detail inline (access sequences, condition tables, V/06)

### Master Data Structure
- Single file (master-data.md) consistent with FI and MM pattern
- Full customer master: all three levels (general KNA1, company code KNB1, sales area KNVV) with SD emphasis — self-contained, not just SD views
- Include condition records (pricing master data) in detail: KONH/KONP tables, condition types (PR00, K004, K005, MWST), access sequences, validity periods
- Include output determination master data: output types, condition records for output (print, EDI, email), partner-based output determination

### Order-to-Cash Process Depth
- Full variant coverage: standard O2C, returns (RMA), credit/debit memos, cash sales, rush orders, consignment (fill-up/issue/pickup/return), third-party processing
- Include document flow diagrams showing the complete document chain: inquiry -> quotation -> order -> delivery -> PGI -> billing doc -> FI doc with table references (VBAK/VBAP -> LIKP/LIPS -> VBRK/VBRP)
- Include availability check (ATP) and credit check as inline process steps — they happen automatically during order entry
- Follow the same narrative-plus-table format with role annotations used in FI and MM processes

### SPRO Configuration Scope
- Full breadth: enterprise structure (sales org, distribution channel, division), sales document types, item categories, schedule line categories, delivery types, billing types, pricing procedure assignment (OVKK), condition types, access sequences, output determination (NACE), partner determination, copy control, text determination, incompletion procedures, availability check, credit management config
- Full copy control documentation: VTAA (order to order), VTLA (order to delivery), VTFL (delivery to billing), VTAF (billing to order) with key fields at header + item level, requirements, data transfer routines
- Item category determination logic: document the 4-key determination in OVLP/VOV4 (sales doc type + item category group + usage + higher-level item) and how each key contributes
- Single file (config-spro.md) consistent with FI and MM pattern

### Claude's Discretion
- Exact T-code count within the 65-80 range
- How deep to go on foreign trade and rebate T-codes (foundation level is fine)
- Whether to include incomplete document flow variants (e.g., inquiry and quotation are optional)
- Level of detail on credit management config vs deferring deep credit to Phase 8
- How to handle the large volume of SD config in a single file (section organization)

</decisions>

<specifics>
## Specific Ideas

- SD follows the same structural patterns as FI (Phase 3) and MM (Phase 5) — consistency across all four modules is important
- Document flow is central to SD in a way it isn't for FI or MM — the process file should make the document chain very clear
- Customer master content should be self-contained (all three levels) even though FI already covers customer master — SD consultants need the full picture in one place
- Pricing condition technique is foundational enough to include inline in T-codes and master data, not defer entirely to Phase 8

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-sd-module-foundation*
*Context gathered: 2026-02-17*
