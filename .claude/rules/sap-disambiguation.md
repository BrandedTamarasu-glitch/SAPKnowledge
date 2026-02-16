# ECC 6 vs S/4HANA — Quick Reference

This KB covers ECC 6. Use this table to avoid mixing up ECC and S/4 behavior.

| Area | ECC 6 (This KB) | S/4HANA (Not Covered) |
|---|---|---|
| Vendor master | XK01/FK01/MK01 — LFA1 table | Business Partner (BP) — BUT000 |
| Customer master | XD01/FD01/VD01 — KNA1 table | Business Partner (BP) — BUT000 |
| Material documents | MKPF/MSEG tables | MATDOC single table |
| Material Ledger | Optional (activate per plant) | Mandatory, always active |
| General Ledger | Classic GL or New GL (FAGL) | Universal Journal (ACDOCA) |
| Document splitting | Optional New GL feature | Mandatory |
| Cost of goods sold | COGS via OBYC/GBB | Real-time COGS split |
| Reporting | SAP Query, Report Painter, BW | Embedded Analytics, CDS views |
| UI | SAP GUI transactions | Fiori apps (GUI still works) |
| Credit management | FD32, classic credit mgmt | FSCM Credit Management |
| Output management | NACE condition-based output | BRF+ output management |
| MRP | MD01/MD02, classic MRP | MRP Live (pMRP) |

When answering ECC 6 questions, use the ECC 6 column. Flag S/4 differences only when the user asks or when it prevents a common mistake.
