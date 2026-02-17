---
module: co
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# SAP Controlling (CO)

> ECC 6.0 reference. For S/4HANA differences, see individual file sections. Key S/4 changes: cost elements KA01/KA06 obsolete (GL accounts serve as cost elements); PCA separate ledger eliminated (data in ACDOCA); Material Ledger mandatory.

## When to Use This Module

- Cost center accounting, internal orders, and activity-based costing
- Profit center accounting and profitability analysis
- Product costing, cost allocation, and settlement
- Period-end closing: assessment, distribution, overhead, settlement

## File Index

| File | Contains | Read When |
|------|----------|-----------|
| @tcodes.md | ~63 T-codes (Cost Elements/CCA/Internal Orders/Activity Types/PCA/Product Costing/Period-End/Reporting) with menu paths, usage, gotchas | Finding the right CO T-code; looking up menu path; understanding assessment (KSU5) vs distribution (KSV5); CK24 mark/release process |
| @master-data.md | Master data: cost elements (CSKA/CSKB), cost centers (CSKS), internal orders (AUFK), activity types (CSLA), profit centers (CEPC), CO tables (COSP/COSS/COBK/COEP) | Looking up CO table names; finding which table holds a field; cost element category reference (1-43); CORRECTION blocks for common misconceptions; settlement rule table (COBRB) |
| @config-spro.md | SPRO/IMG configuration for CA setup, cost elements, CCA, internal orders, activity types, allocation cycles, product costing, PCA | Configuring CO settings; need SPRO path for controlling area (OKKP), order types (KOT2), settlement profiles (OKO7), costing variants (OKKN), PCA substitution (1KEF) |
| @processes.md | Business process flows: period-end allocation, internal order settlement, product costing run, cost center planning, period-end closing sequence | Understanding CO period-end process; assessment vs distribution decision; settlement process; CK24 mark/release; period-end sequence and timing |
| @integration.md | Cross-module integration points (CO-FI, CO-MM, CO-SD) | Understanding cost element mapping, CO-FI reconciliation (Phase 10) |
| @patterns.md | Solution design patterns | Designing CO solutions for complex scenarios (Phase 12) |

## Key Concepts

- **Controlling Area (KOKRS)** — organizational unit spanning one or more company codes; all CO objects belong to a controlling area
- **Cost Elements** — primary (categories 1,3,4,11,12,22 — match GL accounts) vs secondary (categories 21,31,41,42,43 — CO-only)
- **Assessment vs Distribution** — assessment uses secondary CE (cat 42, loses original CEs); distribution preserves original CEs
- **Settlement** — transfers costs from internal orders to receivers (CC, GL, asset, WBS, CO-PA) via settlement rules (COBRB)
- **CK24 Mark/Release** — two-step process: mark sets future price, release updates MBEW-STPRS (standard price)
- **PCA Separate Ledger** — ECC 6 only: GLPCA/GLPCT tables store profit center actuals separately from FI
