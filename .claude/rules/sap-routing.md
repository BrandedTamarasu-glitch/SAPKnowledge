# SAP ECC 6 — Module Routing

When asked about SAP ECC 6, use this table to find the right files.

## Module Routing

| Topic Keywords | Module | Entry Point |
|---|---|---|
| Procurement, purchasing, POs, vendors, invoices | MM | `modules/mm/CLAUDE.md` |
| Inventory, goods movements, MIGO, stock | MM | `modules/mm/CLAUDE.md` |
| Sales orders, deliveries, billing, pricing | SD | `modules/sd/CLAUDE.md` |
| General ledger, AP, AR, assets, bank accounting | FI | `modules/fi/CLAUDE.md` |
| Cost centers, internal orders, profit centers, allocations | CO | `modules/co/CLAUDE.md` |
| Account determination, OBYC, VKOA | Integration | `cross-module/` + module `integration.md` |
| E2E processes (P2P, O2C, R2R) | Cross-module | `cross-module/` |
| Period-end close, month-end, year-end, R2R sequence | Cross-module | `cross-module/CLAUDE.md` |
| Availability check, ATP, goods issue for delivery, MM-SD | Cross-module | `cross-module/CLAUDE.md` |
| Solution design patterns, choosing SAP approach for business requirement | Cross-module | `cross-module/design-patterns.md` |
| Scenario playbooks: consignment, intercompany, third-party, subcontracting, split valuation, batch, serial | Cross-module | `cross-module/playbooks.md` |
| Month-end close checklist, year-end close checklist, period-end operator steps, T-codes for close | Cross-module | `cross-module/checklists.md` |
| Movement types, document types, posting keys | Reference | `reference/` |

## How to Use

1. Identify the module from the user's question using the table above
2. Read the module's `CLAUDE.md` for file orientation
3. Read specific content files listed in that CLAUDE.md

**ECC 6.0 only.** S/4HANA mentions are for disambiguation, not primary reference.
