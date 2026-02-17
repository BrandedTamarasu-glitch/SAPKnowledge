# Phase 3: FI Module Foundation - Context

**Gathered:** 2026-02-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver complete FI reference covering T-codes, SPRO configuration paths, process maps, and master data — serving as the integration target for MM, SD, and CO in later phases. Covers GL, AP, AR, and Asset Accounting. Account determination logic, decision trees, and troubleshooting are Phase 4.

</domain>

<decisions>
## Implementation Decisions

### T-code Selection & Depth

- **Coverage distribution:** Balanced across GL / AP / AR / AA — roughly equal representation for each submodule
- **Detail per T-code:** Full detail — menu path + description + typical usage + common gotchas (not a slim lookup table)
- **Organization:** Submodule sections (GL / AP / AR / AA) with a workflow index at the top linking to each section
- **Reporting T-codes:** Include — FB03 (display document), FBL1N/FBL3N/FBL5N (line item reports), F.01, S_ALR series are heavily used daily and belong in the reference

### SPRO Configuration Path Format

- **Path presentation:** Full IMG path string first (e.g. `Financial Accounting (New) ▸ General Ledger Accounting ▸ ...`), then T-code shortcut in parentheses if one exists (e.g. `(OB13)`)
- **Config detail level:** Step-by-step — what to do in each screen and which key fields to set; not just path + description
- **Coverage areas (all four):**
  - GL configuration — chart of accounts, posting keys, document types, fiscal year variant, field status groups
  - AP/AR configuration — payment terms, tolerance groups, dunning procedures, payment run config (F110 setup)
  - Asset Accounting configuration — chart of depreciation, asset classes, depreciation keys, AA integration with GL
  - New GL configuration — parallel accounting, ledger groups, document splitting rules, segment reporting activation

### Process Flow Representation

- **Format:** Both — numbered workflow narrative explaining WHY each step, plus a summary transaction table at the end (Step | Activity | T-code | Role | Output)
- **Activities to cover (all four):**
  1. Daily GL posting cycle — FB50/FB60/FB70, document parking, clearing, reversal
  2. Month-end close — foreign currency revaluation (F.05), accruals (FBS1), GR/IR clearing (F.13), depreciation run (AFAB), period-end posting period close
  3. AP payment run — F110 payment proposal creation, editing, payment run execution, bank file, reconciliation
  4. Financial reporting — F.01 balance sheet, S_ALR reports, drill-to-document from report to FI posting
- **Role/persona:** Include role for every step (AP Accountant, GL Accountant, Finance Manager, System Administrator) — helps Claude answer authorization and ownership questions

### Master Data Depth

- **Format:** Same detailed field-table pattern as `reference/org-structure.md` — field | description | typical values per object; not a summary overview
- **Objects covered (all four):**
  - GL accounts: SKA1 (chart of accounts segment) + SKB1 (company code segment) — account type, recon account flag, posting control, tax relevance, field status group
  - Vendor master: LFA1 (general) + LFB1 (company code) + LFM1 (purchasing data) — payment terms, payment method, dunning procedure, recon account, GR-based IV flag, sort key
  - Customer master: KNA1 (general) + KNB1 (company code) + KNVV (sales area data) — payment terms, credit limit, recon account, dunning procedure, account assignment group
  - Asset master: ANLA (general) + ANLB (depreciation area data) — asset class, depreciation key, useful life, cost center assignment, capitalization date, deactivation date
- **S/4HANA callouts:** Only for vendor and customer master — one callout each flagging Business Partner (BP / BUT000) replacement. Skip S/4 callouts for GL accounts and asset master (no significant structural change).

### Claude's Discretion

- Exact number of T-codes per submodule within the 50-80 total target
- Which specific S_ALR report T-codes to include in the reporting section
- Ordering of SPRO entries within each config area
- Exact field selection for each master data object (keep to 8-12 key fields; exclude fields that are rarely configured)

</decisions>

<specifics>
## Specific Ideas

- F110 (payment run) is complex and commonly misunderstood — worth extra detail in both T-code section and process flow
- The workflow index at the top of the T-code file should map to process stages (posting → clearing → reporting) not just submodules, so Claude can answer "what T-code do I use to clear an open item?"
- Asset Accounting config is complex and often misconfigured — step-by-step SPRO detail here is especially valuable
- New GL document splitting is a frequent pain point — config steps should clarify what's required vs optional

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-fi-module-foundation*
*Context gathered: 2026-02-16*
