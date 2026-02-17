---
module: sd
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# SAP Sales & Distribution (SD)

> ECC 6.0 reference. For S/4HANA differences, see individual file sections. Key S/4 changes: customer master XD01/VD01 → Business Partner (BP); output determination NACE → BRF+; credit management FD32 → FSCM/UKM; material docs MKPF/MSEG → MATDOC.

## When to Use This Module

- Sales order processing, quotations, contracts, and scheduling agreements
- Delivery processing, shipping, picking, packing, and transportation
- Billing, invoicing, credit/debit memos, and revenue recognition
- Pricing (condition technique), output determination, credit management

## File Index

| File | Contains | Read When |
|------|----------|-----------|
| @tcodes.md | ~75 T-codes (Sales/Shipping/Billing/Pricing/Output/Credit/Returns/Rebates) with menu paths, usage, gotchas | Finding the right T-code; looking up menu path; understanding VA01 document type variants or condition technique T-codes |
| @config-spro.md | SPRO/IMG configuration for Enterprise Structure, Document Types, Pricing, Copy Control, Delivery, Billing, Output, Credit | Configuring SD settings; need SPRO path for pricing procedure (OVKK), item category determination (OVLP), copy control (VTAA/VTLA/VTFL/VTAF), or output (NACE) |
| @processes.md | Business process flows: standard O2C, returns, credit/debit memos, cash sales, rush orders, consignment, third-party | Understanding end-to-end order-to-cash process; document flow (VBAK→LIKP→VBRK); mapping transactions to roles; ATP and credit check logic |
| @master-data.md | Master data: customer master (KNA1/KNB1/KNVV), condition records (KONH/KONP), output determination, material sales views (MVKE) | Looking up table fields; finding which table holds a field; CORRECTION blocks for KTGRD, KTGRM, DWERK field locations; pricing condition types |
| @sd-advanced.md | VKOA account determination walkthrough (dual-axis, 8+ worked examples, pricing-to-VKOA chain, debugging path), 12 decision trees (pricing procedure, access sequence, copy control, partner determination, ATP, credit management), 12 troubleshooting entries (symptom-first, SAP message IDs) | Making SD configuration choices; diagnosing VA01/VF01/VL01N errors; tracing billing to GL account; understanding VKOA setup for SD |
| @integration.md | SD-FI integration: point catalog (14 touchpoints), transaction traces (VF01 billing-to-FI, PGI COGS), revenue recognition basics, period-end (rebate settlement/revenue accruals/VF04) | Tracing what happens in FI when SD posts; VF01 billing trace; PGI COGS trace; period-end SD-FI sequence |
| @patterns.md | Solution design patterns | Designing SD solutions for complex scenarios (Phase 12) |

## Key Concepts

- **Sales Area** — Sales Org + Distribution Channel + Division; key organizational unit for all SD data
- **Customer Master** — KNA1 (general) + KNB1 (company code) + KNVV (sales area); S/4: Business Partner
- **Condition Technique** — 4-layer model: condition table → access sequence → condition type → procedure; drives pricing, output, account determination
- **Copy Control** — VTAA/VTLA/VTFL/VTAF; governs data flow between order → delivery → billing with requirements and data transfer routines
- **Document Flow** — VBAK/VBAP → LIKP/LIPS → VBRK/VBRP → BKPF/BSEG; traceable via VBFA table
- **Item Category Determination** — 4-key lookup: doc type + MTPOS + usage + higher-level item cat → OVLP
