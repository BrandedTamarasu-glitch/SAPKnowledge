---
module: fi
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# SAP Financial Accounting (FI)

> ECC 6.0 reference. For S/4HANA differences, see individual file sections.

## When to Use This Module

- General ledger posting, account balances, and financial statements
- Accounts payable (vendor invoices, payments) and accounts receivable (customer invoices, receipts)
- Asset accounting, financial close, and period-end activities

## File Index

| File | Contains | Read When |
|------|----------|-----------|
| @tcodes.md | 65 T-codes (GL/AP/AR/AA) with menu paths, usage, gotchas | Finding the right T-code; looking up menu path; understanding when to use Enjoy vs classic screen |
| @config-spro.md | SPRO/IMG configuration paths for GL, AP/AR, Asset Accounting, New GL | Configuring FI settings; need step-by-step SPRO guidance |
| @processes.md | Business process flows: GL posting, month-end close, F110 payment run, financial reporting | Understanding end-to-end process sequence; mapping transactions to roles |
| @master-data.md | Master data: GL accounts (SKA1+SKB1), vendor (LFA1+LFB1+LFM1), customer (KNA1+KNB1+KNVV), asset (ANLA+ANLB+ANLZ) | Looking up table fields; field-level master data questions; table key structures |
| @account-determination.md | Account determination: OBYC framework (MM GR/GI), VKOA framework (SD revenue), FI-only auto postings (F.05 FX, OBXU/OBXI cash discount) | Understanding automatic GL postings; tracing movement type to GL account; account determination setup or diagnosis |
| @fi-advanced.md | 7 decision trees (New GL, parallel accounting, document splitting, recon accounts, payment terms, tolerances, asset classes) + troubleshooting (pitfalls and symptoms) | Making FI configuration choices during implementation; diagnosing FI posting errors; resolving F110, document splitting, AA year-end issues |
| @integration.md | Cross-module integration points (MM-FI, SD-FI) | Understanding automatic account postings from MM/SD to FI (Phase 4+) |
| @patterns.md | Solution design patterns | Designing FI solutions for common business scenarios (Phase 12) |

## Key Concepts

- Chart of Accounts
- Company Code
- Fiscal Year Variant
- Document Types
- Posting Keys
