---
module: mm
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# SAP Materials Management (MM)

> ECC 6.0 reference. For S/4HANA differences, see individual file sections. Key S/4 changes: MKPF/MSEG → MATDOC; vendor master → Business Partner (BP); MRP MD01 → MD01N (MRP Live); Material Ledger mandatory.

## When to Use This Module

- Procurement and purchasing (purchase requisitions, purchase orders, contracts, scheduling agreements)
- Inventory management (goods receipt, goods issue, stock transfers, physical inventory)
- Invoice verification and logistics invoice processing (MIRO, three-way match)
- Material requirements planning (MRP) — basic operations (deep MRP config deferred)

## File Index

| File | Contains | Read When |
|------|----------|-----------|
| @tcodes.md | ~67 T-codes (Purchasing/IM/LIV/MRP) with menu paths, usage, gotchas | Finding the right T-code; looking up menu path; understanding MIGO variants or ME-family scope |
| @config-spro.md | SPRO/IMG configuration for Enterprise Structure, Purchasing, IM, LIV, Valuation | Configuring MM settings; need SPRO path for tolerance keys (OMR6) or PO doc types (OMH6); valuation level setup |
| @processes.md | Business process flows: P2P (PR→PO→GR→MIRO→F110), outline agreements, physical inventory | Understanding end-to-end procurement process; three-way match logic; mapping transactions to roles |
| @master-data.md | Master data: material master (all views/tables), vendor (LFA1/LFB1/LFM1), info records (EINA/EINE), source lists (EORD) | Looking up table fields; finding which view/table holds a field; CORRECTION blocks for commonly-wrong field locations |
| @mm-advanced.md | OBYC account determination walkthrough (dual-axis, 10+ worked examples, debugging path), 12 decision trees (valuation, release strategy, MRP, split valuation, batch management), 12 troubleshooting entries (symptom-first, SAP message IDs) | Making MM configuration choices; diagnosing MIGO/MIRO errors; tracing movement type to GL account; understanding OBYC setup for MM |
| @integration.md | MM-FI integration: point catalog (20 touchpoints), transaction traces (MIGO 101, MIRO), GR/IR clearing (F.13/MR11), period-end (MMPV/CKMLCP/MR21) | Tracing what happens in FI when MM posts; GR/IR clearing troubleshooting; period-end MM-FI sequence |
| @patterns.md | Solution design patterns | Designing MM solutions for complex scenarios (Phase 12) |

## Key Concepts

- **Material Master** — Central data repository; views map to tables (MARA/MARC/MARD/MBEW)
- **Vendor Master** — LFA1 (general) + LFB1 (FI) + LFM1 (purchasing); S/4: Business Partner
- **Purchase Order** — Document type NB; three variants ME21N/22N/23N documented separately
- **Movement Types** — 101 (GR), 201 (GI to CC), 301 (plant transfer), 601 (GI for delivery)
- **Three-Way Match** — PO price/qty vs GR qty vs invoice; tolerance keys in OMR6; MRBR for blocked
- **Valuation** — Price control S (standard, PRD fires) vs V (moving average, BSX absorbs); OMWM = plant
