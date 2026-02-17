---
module: mm
content_type: tcodes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Materials Management — Transaction Codes

> ECC 6.0 reference. T-codes listed work in both ECC 6.0 and S/4HANA via SAP GUI. S/4HANA also offers equivalent Fiori apps. Key S/4 differences: MKPF/MSEG → MATDOC; vendor master XK01 → Business Partner (BP); MRP MD01 → MD01N (MRP Live).

## Workflow Index

| Process Stage | T-code(s) | Submodule | Notes |
|---|---|---|---|
| PR Creation | ME51N | Purchasing | |
| PR Change/Display | ME52N, ME53N | Purchasing | |
| PR to PO (Auto) | ME59N | Purchasing | Requires source list/info record |
| PO Creation | ME21N | Purchasing | |
| PO Change/Display | ME22N, ME23N | Purchasing | |
| PO Release (List) | ME28 | Purchasing | Collective — multiple POs |
| PO Release (Individual) | ME29N | Purchasing | Single PO |
| Vendor Master | XK01, XK02, XK03, MK01 | Purchasing | |
| Info Records | ME11, ME12, ME13 | Purchasing | |
| Source List | ME01, ME03 | Purchasing | |
| Contracts | ME31K, ME32K, ME33K | Purchasing | |
| Scheduling Agreements | ME31L, ME32L | Purchasing | |
| Purchasing Reports | ME2M, ME2N, ME2L, ME80 | Purchasing | |
| Goods Receipt (PO) | MIGO (A01) | Inventory Mgmt | Action = GR |
| Material Doc Change/Display | MIGO (A07), MIGO (A03) | Inventory Mgmt | |
| Transfer Posting | MB1B | Inventory Mgmt | |
| Other Goods Receipt | MB1C | Inventory Mgmt | Without PO reference |
| Physical Inventory | MI01, MI04, MI07 | Inventory Mgmt | |
| Stock Reports | MB51, MB52, MB54, MMBE, MB5B | Inventory Mgmt | |
| GR/IR Maintenance | MR11, MR11SHOW | Inventory Mgmt | |
| Invoice Entry | MIRO | LIV | |
| Invoice Park | MIR7 | LIV | |
| Invoice Display | MIR4 | LIV | |
| Invoice List/Overview | MIR5, MIR6 | LIV | |
| Fast Invoice Entry | MIRA | LIV | |
| Release Blocked Invoices | MRBR | LIV | |
| Cancel Invoice | MR8M | LIV | |
| ERS (Auto Invoice) | MRRL | LIV | |
| Subsequent Debit/Credit | MIRO variants | LIV | Use MIRO transaction type dropdown |
| Invoice Output | MR90 | LIV | |
| Invoice Revaluation | MRNB | LIV | |
| Invoice Background | MRM | LIV | |
| MRP Run (Plant) | MD01 | MRP | |
| MRP Run (Single-Multi) | MD02 | MRP | |
| MRP Run (Single) | MD03 | MRP | |
| Stock/Requirements (Live) | MD04 | MRP | Dynamic — real-time view |
| MRP List (Snapshot) | MD05 | MRP | Static — last run only |
| MRP Collective | MD06, MD07 | MRP | |
| Planned Orders | MD11, MD12 | MRP | |
| Planned Indep. Requirements | MD61 | MRP | |
| Payment | F110 | FI (cross-ref) | See FI processes.md |

---

## Purchasing

### ME51N — Create Purchase Requisition

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Requisition → Create
**Usage:** Primary PR entry point (Enjoy screen). Account assignment (CC/IO/WBS) set here drives CO postings downstream.
**Gotcha:** Account assignment entered on PR carries through to PO and GR — wrong CC here propagates through entire P2P chain.

### ME52N — Change Purchase Requisition

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Requisition → Change
**Usage:** Modify an existing PR — quantity, delivery date, account assignment, item text. Only possible before PO is created from the PR.

### ME53N — Display Purchase Requisition

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Requisition → Display
**Usage:** Read-only view of PR. Use to check approval status, source assignment, and whether PO has been created.

### ME59N — Automatic PR-to-PO Conversion

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Requisition → Follow-On Functions → Create PO Automatically
**Usage:** Mass-converts approved PRs to POs based on source determination. Runs for a plant/purchasing group/date range selection.
**Gotcha:** CRITICAL — ME59N is automatic CONVERSION (creates POs), NOT a display T-code. Requires source determination (source list or info record) to be configured. Without valid source, ME59N cannot convert.

### ME21N — Create Purchase Order

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → Create → Vendor/Supplying Plant Known
**Usage:** Primary PO creation (Enjoy screen). Document type NB = standard PO. Header has vendor, purchasing org, currency; items have material, quantity, delivery date, and account assignment.

### ME22N — Change Purchase Order

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → Change
**Usage:** Modify an existing PO — quantities, delivery dates, account assignment, item texts. Cannot change vendor or document type after save.

### ME23N — Display Purchase Order

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → Display
**Usage:** Most commonly used for PO status tracking and delivery monitoring. Shows GR status, invoice status, and open quantities for each item.

### ME28 — Release (Approve) Purchase Orders — Collective List

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → Release → Collective Release
**Usage:** Shows all POs pending release for a given release code; approve multiple POs at once.
**Gotcha:** ME28 = collective LIST of POs pending approval. ME29N = release a SPECIFIC PO by number.

### ME29N — Release (Approve) Purchase Order — Individual

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → Release → Individual Release
**Usage:** Release a specific PO by PO number. Shows the release strategy and release codes; approver clicks release button.

### XK01 — Create Vendor (Central — All Views)

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Vendor → Central → Create
**Usage:** Creates LFA1 (general) + LFB1 (company code) + LFM1 (purchasing org) in one transaction. Preferred in MM+FI environments where vendor needs both purchasing and payment views.

### XK02 — Change Vendor (Central)

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Vendor → Central → Change
**Usage:** Modify any vendor master view — general data, company code data, or purchasing data — in one session.

### XK03 — Display Vendor (Central)

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Vendor → Central → Display
**Usage:** Read-only view of all vendor master views. Use to check payment terms (LFB1), order acknowledgment settings (LFM1), or bank details.

### MK01 — Create Vendor (Purchasing View Only)

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Vendor → Purchasing → Create
**Usage:** Creates MM-only vendor without FI company code data. Use when FI team manages their own vendor accounting setup separately.
**Gotcha:** MK01 creates LFA1 + LFM1 but NOT LFB1 — vendor cannot receive payments until FI extends with FK01.

### ME11 — Create Purchasing Info Record

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Info Record → Create
**Usage:** Creates EINA/EINE record linking vendor + material + purchasing org with price, delivery time, and order unit. Foundation for source determination and price defaulting in POs.

### ME12 — Change Purchasing Info Record

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Info Record → Change
**Usage:** Update price conditions, delivery time, or order acknowledgment settings on an existing info record.

### ME13 — Display Purchasing Info Record

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Info Record → Display
**Usage:** Read-only view of info record. Shows effective price (after scales), validity dates, and purchasing org-specific conditions.

### ME31K — Create Contract

**Menu Path:** Logistics → Materials Management → Purchasing → Outline Agreement → Contract → Create
**Usage:** Creates quantity contract (type MK) or value contract (type WK) with a vendor for agreed terms over a validity period. Individual releases draw down against contract target quantity or value.

### ME32K — Change Contract

**Menu Path:** Logistics → Materials Management → Purchasing → Outline Agreement → Contract → Change
**Usage:** Modify contract terms, validity dates, or add new item lines. Use to update target quantities after renegotiation.

### ME33K — Display Contract

**Menu Path:** Logistics → Materials Management → Purchasing → Outline Agreement → Contract → Display
**Usage:** Read-only view of contract including release orders created against it and remaining open quantity/value.

### ME31L — Create Scheduling Agreement

**Menu Path:** Logistics → Materials Management → Purchasing → Outline Agreement → Scheduling Agreement → Create
**Usage:** Long-term agreement with delivery schedule lines; used for repetitive procurement. Forecast and firm delivery schedule lines replace individual POs.

### ME32L — Change Scheduling Agreement

**Menu Path:** Logistics → Materials Management → Purchasing → Outline Agreement → Scheduling Agreement → Change
**Usage:** Modify delivery schedule lines or agreement terms. Scheduling agreement changes trigger partner communications in JIT/EDI environments.

### ME01 — Maintain Source List

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Source List → Maintain
**Usage:** Maintains EORD table — defines authorized vendors per material per plant. Required for ME59N automatic PO creation and for procurement via fixed source.

### ME03 — Display Source List

**Menu Path:** Logistics → Materials Management → Purchasing → Master Data → Source List → Display
**Usage:** Read-only view of source list entries for a material/plant combination. Shows validity dates and whether source is fixed.

### ME2M — Purchase Orders by Material

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → List Displays → By Material
**Usage:** Filter all POs by material number; shows open quantities and delivery status. Use for material shortage analysis and expediting.

### ME2N — Purchase Orders by PO Number

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → List Displays → By PO Number
**Usage:** Standard PO lookup by number range. Use when you have a PO number range and need a status list.

### ME2L — Purchase Orders by Vendor

**Menu Path:** Logistics → Materials Management → Purchasing → Purchase Order → List Displays → By Vendor
**Usage:** All open POs for a specific supplier; used for vendor performance review and spend analysis.

### ME80 — Purchasing Reporting (General)

**Menu Path:** Logistics → Materials Management → Purchasing → General Evaluation → Purchasing Reporting
**Usage:** Flexible report combining PR, PO, and outline agreement data with configurable output layout. Best single report for cross-document purchasing analysis.

---

## Inventory Management

### MIGO — Goods Receipt (Create)

**Menu Path:** Logistics → Materials Management → Inventory Management → Goods Movement → Goods Receipt
**Usage:** Action = A01 (Goods Receipt), Reference = Purchase Order. Posts movement type 101 (GR against PO). Creates MKPF header + MSEG line items. FI posting: BSX (Dr inventory) + WRX (Cr GR/IR clearing). For standard price (S) materials, PRD may fire for price differences.
**Gotcha:** MIGO is a single T-code serving multiple functions — always verify the Action dropdown (A01=GR, A07=Change, A03=Display). S/4HANA note: MKPF/MSEG replaced by single MATDOC table.

### MIGO — Change Material Document

**Menu Path:** Logistics → Materials Management → Inventory Management → Goods Movement → Goods Receipt (then set Action = A07)
**Usage:** Correct header data on existing material document. Cannot change quantities or amounts — use reversal (movement type 102) and re-post instead.

### MIGO — Display Material Document

**Menu Path:** Logistics → Materials Management → Inventory Management → Goods Movement → Goods Receipt (then set Action = A03)
**Usage:** Read-only view of material document and associated FI document. Use to confirm FI posting details and movement type applied.

### MI01 — Create Physical Inventory Document

**Menu Path:** Logistics → Materials Management → Physical Inventory → Physical Inventory Document → Create
**Usage:** Creates count document blocking stock for counting. Specify plant, storage location, and posting date. Materials are listed for physical count entry.

### MI04 — Enter Inventory Count

**Menu Path:** Logistics → Materials Management → Physical Inventory → Inventory Count → Enter
**Usage:** Post actual count results against the physical inventory document. Enter counted quantities; system calculates difference to book stock.

### MI07 — Post Inventory Differences

**Menu Path:** Logistics → Materials Management → Physical Inventory → Difference → Post
**Usage:** Generates difference posting document; updates stock quantities. FI posting adjusts inventory account. Run after MI04 count entry and difference review.

### MB1B — Transfer Posting

**Menu Path:** Logistics → Materials Management → Inventory Management → Goods Movement → Transfer Posting
**Usage:** Stock transfers between plants (movement type 301/303), storage locations (311/313), or special stock types. Classic screen — MIGO can also handle transfers via movement type selection.

### MB1C — Enter Other Goods Receipt

**Menu Path:** Logistics → Materials Management → Inventory Management → Goods Movement → Goods Receipt → Other
**Usage:** Receipts without PO reference — initial stock load (561), found stock (501), production receipt without order. Classic screen; use when no reference document exists.

### MB51 — Material Document List

**Menu Path:** Logistics → Materials Management → Inventory Management → Environment → List Displays → Material Documents
**Usage:** Primary audit tool — list all material documents by material, plant, movement type, date range. Reads MKPF/MSEG. Use to trace all inventory movements for a material.

### MB52 — Warehouse Stocks of Material

**Menu Path:** Logistics → Materials Management → Inventory Management → Environment → Stock → Warehouse Stocks
**Usage:** Current stock by storage location; includes unrestricted, quality inspection, and blocked stock. Run for a plant or set of plants and materials.

### MB54 — Consignment Stocks at Customer

**Menu Path:** Logistics → Materials Management → Inventory Management → Environment → Stock → Consignment Stocks at Customer
**Usage:** Special stock display for consignment materials held at customer locations (special stock indicator W).

### MMBE — Stock Overview

**Menu Path:** Logistics → Materials Management → Inventory Management → Environment → Stock → Stock Overview
**Usage:** Multi-level stock display: client → company code → plant → storage location → batch. Best single-screen stock view. S/4HANA note: same UI but reads from MATDOC-derived views instead of MARD.

### MB5B — Stocks for Posting Date

**Menu Path:** Logistics → Materials Management → Inventory Management → Environment → Stock → Stocks on Posting Date
**Usage:** Historical stock position at a specific past date — answers "what was my stock on date X?" Essential for period-end reconciliation and audit.

### MR11 — GR/IR Account Maintenance

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → GR/IR Account Maintenance → Maintain
**Usage:** Clears one-sided GR/IR open items — e.g., GR posted but invoice never received (or vice versa). Posts write-off or accrual to clear the hanging items.
**Gotcha:** Always run F.13 automatic clearing first (clears matched pairs); MR11 handles the residual unmatched items that F.13 cannot clear automatically.

### MR11SHOW — Display GR/IR Clearing Documents

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → GR/IR Account Maintenance → Display
**Usage:** Review past MR11 postings and their impact on the GR/IR account. Use for audit of period-end GR/IR clearing activity.

---

## Logistics Invoice Verification (LIV)

### MIRO — Enter Invoice (Logistics Invoice Verification)

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Document Entry → Enter Invoice
**Usage:** PO-based invoice entry with three-way match (PO price/qty vs GR qty vs invoice). Creates FI document automatically: debits GR/IR clearing (WRX), credits vendor account. Handles standard invoices, credit memos, subsequent debits/credits via transaction type dropdown.
**Gotcha:** CRITICAL — For PO-based credit memos, use MIRO transaction type "Credit Memo" — NOT FB65. Using FB65 bypasses MM three-way match, does not update EKBE/RSEG, and causes MM-FI reconciliation breaks.

### MIR7 — Park Incoming Invoice

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Document Entry → Park Invoice
**Usage:** Parks LIV invoice for later posting; no FI document number created until posted. Used for workflow-based invoice approval. Similar to FBV1 in FI.

### MIR4 — Display Incoming Invoice

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Display Incoming Invoice
**Usage:** Read-only display of posted or parked LIV document. Shows PO reference, GR reference, tolerance status, and FI document link.

### MIR5 — Display List of Invoice Documents

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Display List of Invoice Documents
**Usage:** Search LIV invoices by vendor, PO, posting date, or amount range. Use for invoice reconciliation and vendor statement matching.

### MIR6 — Invoice Overview

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Invoice Overview
**Usage:** Summary view of invoices grouped by PO or vendor; useful for reconciliation and checking invoice/GR balance.

### MIRA — Fast Invoice Entry

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Document Entry → Fast Invoice Entry
**Usage:** Multiple invoice lines from a list; designed for high-volume processing environments. Reduces screen navigation vs. MIRO for batch posting.

### MRBR — Release Blocked Invoices

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Release Blocked Invoices
**Usage:** Review and release invoices blocked due to tolerance exceedances. Shows blocking reason (price, quantity, date, amount) and allows release or manual correction.
**Gotcha:** BD tolerance auto-posts small differences — all OTHER tolerance keys (DQ/PP/ST/VP) BLOCK the invoice, requiring MRBR release.

### MR8M — Cancel Invoice Document

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Cancel Invoice Document
**Usage:** Reversal of a posted MIRO invoice. Creates reversal document in both MM (RSEG) and FI. Required before correcting a wrongly posted invoice.

### MRRL — Evaluated Receipt Settlement (ERS)

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Automatic Settlement → Evaluated Receipt Settlement
**Usage:** Automatic invoice creation from goods receipt for ERS-enabled vendors. Vendor must have ERS indicator set in LFM1 and must agree not to send invoices.

### MIRO (Subsequent Debit) — Post Subsequent Debit

**Menu Path:** Same as MIRO; select transaction type "Subsequent Debit" in dropdown
**Usage:** Price increase from vendor after original invoice is already paid. Posts additional charge against the PO referencing original GR. Debits inventory or price difference account.

### MIRO (Credit Memo) — Enter Credit Memo

**Menu Path:** Same as MIRO; select transaction type "Credit Memo" in dropdown
**Usage:** Credit from vendor referencing original PO. Reverses or reduces original invoice value against PO.
**Gotcha:** Always use MIRO Credit Memo for PO-based credits, never FB65. FB65 does not reference PO/GR and breaks MM-FI reconciliation. See MIRO main entry.

### MIR9 — Display Parked Invoice Documents

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Display Parked Invoice Documents
**Usage:** View parked LIV documents created via MIR7. Shows parked documents awaiting posting or approval.

### MR90 — Messages for Invoice Documents

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Messages for Invoice Documents
**Usage:** Output (print/fax/email) invoice verification documents. Controls output determination for LIV.

### MRNB — Revaluation with Actual Costs

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Further Processing → Revaluate GR for Order Price
**Usage:** Revalue goods receipts with actual invoice costs when price corrections are needed. Used in ERS scenarios and actual costing environments.

### MRM — Invoice Verification in Background

**Menu Path:** Logistics → Materials Management → Logistics Invoice Verification → Automatic Settlement → Invoice Verification in Background
**Usage:** Background processing for EDI/automatic invoice posting; scheduled as batch job. Processes invoice IDocs without manual MIRO entry.

---

## Material Requirements Planning (MRP)

### MD01 — MRP Run — Total Planning (Plant Level)

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Planning → Total Planning → Online
**Usage:** Batch MRP for entire plant; generates planned orders and purchase requisitions based on demand. Run in background during off-hours for production systems.
**Gotcha:** S/4HANA note: replaced by MD01N (MRP Live/pMRP) which runs in real-time without batch jobs.

### MD02 — MRP Run — Single Item, Multi-Level

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Planning → Single Item, Multi-Level
**Usage:** Plans one material and explodes full BOM; plans all dependent materials recursively. Use for targeted replanning that must ripple through BOM levels.

### MD03 — MRP Run — Single Item, Single Level

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Planning → Single Item, Single-Level
**Usage:** Plans one material only without BOM explosion. Used for quick replanning of a specific purchased material with no sub-components.

### MD04 — Stock/Requirements List

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Evaluations → Stock/Requirements List
**Usage:** Dynamic real-time view of stock, requirements, and planned receipts. Primary MRP results view — updates immediately when stock movements or new requirements occur.
**Gotcha:** CRITICAL — MD04 is LIVE (updates in real time). MD05 is a SNAPSHOT from the last MRP run. For current status, always use MD04. MD05 is useful only for investigating what MRP saw at a specific run point.

### MD05 — MRP List

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Evaluations → MRP List
**Usage:** Static snapshot of last MRP run results. Does NOT update when stock movements or new requirements are created after the run. Use only to compare current MD04 against last MRP run baseline.

### MD06 — Collective Display MRP List

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Evaluations → Collective Display MRP List
**Usage:** Multiple materials MRP list view; planner workload overview. Shows exception messages across many materials for planner action.

### MD07 — Stock/Requirements List (Collective)

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Evaluations → Stock/Requirements List (Collective)
**Usage:** Multiple materials in collective view — dynamic (like MD04 but for many materials at once). Use for planner workbench or material shortage review.

### MD11 — Create Planned Order

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Planned Orders → Create
**Usage:** Manual planned order creation; bypasses MRP automation for specific demand situations where MRP has not generated a planned order.

### MD12 — Change Planned Order

**Menu Path:** Logistics → Materials Management → Material Requirements Planning → Planned Orders → Change
**Usage:** Convert or modify planned order before MRP converts it to purchase requisition or production order. Use to adjust quantity or dates.

### MD61 — Create Planned Independent Requirements

**Menu Path:** Logistics → Production Planning → Demand Management → Planned Independent Requirements → Create
**Usage:** Manual demand input for make-to-stock (MTS) planning; drives MRP net requirements calculation. Enter forecast quantities by period for demand-managed materials.
