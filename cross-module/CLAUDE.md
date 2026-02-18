---
module: cross-module
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Cross-Module Processes

> End-to-end business processes spanning multiple SAP ECC 6.0 modules.

## When to Use

- Questions about end-to-end process flows (P2P, O2C, R2R)
- Understanding how transactions in one module trigger actions in another
- Tracing document flow across module boundaries
- Designing a solution for a complex cross-module business requirement
- Implementing a specific complex scenario end-to-end
- Running period-end close — knowing the sequence and T-codes for each close step

## File Index

| File | Contains | Read When |
|------|----------|-----------|
| @procure-to-pay.md | P2P process flow (MM + FI) | Procurement through payment questions |
| @order-to-cash.md | O2C process flow (SD + FI + MM) | Sales through revenue recognition questions |
| @record-to-report.md | R2R period-end close (MM + SD + CO + FI) | Period-end close sequence, month-end ordering, cross-module reconciliation |
| @mm-sd-integration.md | MM-SD integration points (ATP, PGI, returns, consignment, STO) | MM-SD interaction questions, availability check, goods issue for delivery |
| @design-patterns.md | 12 cross-module solution design patterns (business requirement -> SAP approach -> T-codes -> master data -> testing) | Designing a solution for a complex cross-module business requirement; choosing between approaches |
| @playbooks.md | 8 scenario playbooks: consignment, intercompany, third-party, subcontracting, split valuation, special procurement, batch management, serial numbers | Implementing a specific complex scenario end-to-end; full config + master data + test scenarios |
| @checklists.md | Month-end and year-end close checklists (operator-facing; checkbox format; business-day timing; specific T-codes) | Running period-end close; knowing the sequence and T-codes for each close step |
