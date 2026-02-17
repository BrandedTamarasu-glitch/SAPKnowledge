# Phase 5: MM Module Foundation — Research

**Researched:** 2026-02-16
**Domain:** SAP ECC 6.0 Materials Management (MM) — transactions, configuration, master data, procure-to-pay process
**Confidence:** HIGH (training-data knowledge cross-validated with SAP Community, guru99, official SAP documentation searches)

---

## Summary

This research answers the six planning questions for Phase 5 of the SAP MM Module Foundation. The domain is well-understood SAP ECC 6.0 MM — a stable, mature module with a settled T-code ecosystem and well-documented SPRO structure. The primary planning risk is accuracy traps (wrong field locations in material master, OLMR vs OMR6 confusion, OMBA misidentification) rather than coverage gaps.

The FI module (Phase 3) established format conventions that MM must follow exactly: workflow index table, submodule sections with ### headings, CORRECTION note blocks, narrative-plus-table in processes.md, single-file config-spro.md. These are not re-decisions — they are execution constraints.

The ~65 T-code target breaks cleanly across four families. The hardest planning task is selecting the right 25 purchasing T-codes — the ME-family is large and many codes are display-only variants or rarely-used specialty transactions. This research recommends the specific selections below.

**Primary recommendation:** Build all four files (tcodes.md, config-spro.md, processes.md, master-data.md) in parallel using the FI module as the direct format template. The CORRECTION blocks are the highest-value differentiator — the material master has more field-location traps than any other SAP object.

---

## T-Code Selections by Family

### Purchasing (~25 T-codes, ME-family)

These selections prioritize consultant daily use — transactions that appear in every implementation and every support engagement.

**Purchase Requisition (4 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME51N | Create Purchase Requisition | Enjoy screen; primary entry point |
| ME52N | Change Purchase Requisition | Enjoy screen; edit quantities, dates, account assignment |
| ME53N | Display Purchase Requisition | Read-only view; commonly used for status checking |
| ME59N | Convert PR to PO automatically | Auto-convert approved PRs to POs; source determination required |

**Purchase Order — Core Create/Change/Display (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME21N | Create Purchase Order | Enjoy screen; primary PO creation entry point |
| ME22N | Change Purchase Order | Change header, line items, delivery dates post-creation |
| ME23N | Display Purchase Order | Read-only; most commonly used for PO status tracking |

**Purchase Order — Release (2 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME28 | Release (Approve) Purchase Orders — List | Collective release; see all POs pending approval for a release code |
| ME29N | Release (Approve) Purchase Order — Individual | Release a specific PO; standard approver workflow entry point |

**Vendor Master (4 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| XK01 | Create Vendor (Central — all views) | LFA1 + LFB1 + LFM1 in one transaction; preferred in MM+FI |
| XK02 | Change Vendor (Central) | All views; purchasing org view editable |
| XK03 | Display Vendor (Central) | Read-only all views |
| MK01 | Create Vendor (Purchasing View Only) | MM-only vendor without FI company code data |

**Purchasing Info Records (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME11 | Create Purchasing Info Record | EINA/EINE tables; vendor+material+purchasing org price and delivery |
| ME12 | Change Purchasing Info Record | Update price, validity dates, order unit |
| ME13 | Display Purchasing Info Record | Read-only; verify current pricing before PO creation |

**Outline Agreements — Contracts (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME31K | Create Contract | Quantity contract (MK) or value contract (WK) |
| ME32K | Change Contract | |
| ME33K | Display Contract | |

**Outline Agreements — Scheduling Agreements (2 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME31L | Create Scheduling Agreement | Delivery schedule lines against a long-term agreement |
| ME32L | Change Scheduling Agreement | |

**Source List (2 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME01 | Maintain Source List | EORD table; authorized vendors per material per plant |
| ME03 | Display Source List | |

**Reporting — Purchasing (4 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| ME2M | Purchase Orders by Material | Filter by material number; shows all POs for a material |
| ME2N | Purchase Orders by PO Number | Filter by PO number range; standard PO lookup |
| ME2L | Purchase Orders by Vendor | Filter by vendor; all open POs for a supplier |
| ME80 | Purchasing Reporting General | Flexible report combining PR, PO, outline agreements; configurable output |

**Total: 27 purchasing T-codes** (slightly above 25 — trimming optional: ME33K or ME32L can be dropped if strict 25 is required; recommend keeping all for completeness).

---

### Inventory Management (~15 T-codes, MB-family + MIGO)

**Goods Movement — MIGO variants (3 slots — document separately per CONTEXT.md decision):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MIGO (A01 GR) | Goods Receipt against PO | Action = Goods Receipt, Reference = Purchase Order; posts MT 101 |
| MIGO (A07 Change) | Change Material Document | Correct header data on existing document |
| MIGO (A03 Display) | Display Material Document | Read material document; view posting details |

**Physical Inventory (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MI01 | Create Physical Inventory Document | Block stock for count |
| MI04 | Enter Inventory Count | Post count results |
| MI07 | Post Inventory Differences | Generate difference document; updates stock |

**Goods Transfer and Other Postings (2 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MB1B | Transfer Posting | Classic screen for stock transfers between plants/storage locations/special stocks |
| MB1C | Enter Other Goods Receipt | Receipts without reference (MT 501/561) |

**Reporting — Inventory Management (5 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MB51 | Material Document List | List all material documents by selection criteria; primary IM audit tool |
| MB52 | Warehouse Stocks of Material | Current stock by storage location; includes special stocks (consignment, quality) |
| MB54 | Consignment Stocks at Customer | Special stock display |
| MMBE | Stock Overview | Multi-level stock display: client → plant → storage location → batch |
| MB5B | Stocks for Posting Date | Historical stock position at a specific date |

**GR/IR Account Maintenance (2 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MR11 | GR/IR Account Maintenance | Clear one-sided GR/IR open items; deferred delivery or invoices |
| MR11SHOW | Display GR/IR Clearing Documents | Review past MR11 postings |

**Total: 15 IM T-codes** (MIGO counted as three due to documented-separately rule).

---

### Invoice Verification (~15 T-codes, MIR/MIRO-family)

**Core Invoice Posting (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MIRO | Enter Invoice (Logistics Invoice Verification) | PO-based invoice entry; three-way match against PO and GR |
| MIR7 | Park Incoming Invoice | Park LIV invoice for later posting; no FI doc number until posted |
| MIR4 | Display Incoming Invoice | Read-only display of invoice document |

**Invoice List and Change (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MIR5 | Display List of Invoice Documents | Search LIV invoices by various criteria |
| MIR6 | Invoice Overview | Summary view of invoices grouped by PO or vendor |
| MIRA | Fast Invoice Entry | Multiple invoice lines from a list; for high-volume processing |

**Invoice Release and Hold (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MRBR | Release Blocked Invoices | Review and release invoices blocked by tolerance excess |
| MR8M | Cancel Invoice Document | Reversal of a posted MIRO invoice |
| MRRL | Evaluated Receipt Settlement | ERS — automatic invoice creation from GR for ERS-enabled vendors |

**Subsequent Debit/Credit and Variances (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MIRO (Subsequent Debit) | Post Subsequent Debit | Price increase after original invoice is paid |
| MIRO (Credit Memo) | Enter Credit Memo | Credit from vendor; references original PO or delivery |
| MIR9 | Display Parked Invoice (Enjoy) | Display parked LIV documents |

**Account Statement and Reconciliation (3 slots):**
| T-code | Description | Notes |
|--------|-------------|-------|
| MR90 | Messages for Invoice Documents | Output (print) invoice verification documents |
| MRNB | Revaluation with Actual Costs | Revalue GRs with actual invoice costs for price corrections |
| MRM | Invoice Verification in Background | Background processing for EDI/automatic invoice posting |

**Total: 15 IV T-codes** (some MIRO variants counted as separate per document-separately rule).

---

### MRP/Planning (~10 T-codes, MD-family)

| T-code | Description | Notes |
|--------|-------------|-------|
| MD01 | MRP Run — Total Planning (Plant Level) | Batch MRP for entire plant; run in background during off-hours |
| MD02 | MRP Run — Single Item, Multi-Level | Explodes full BOM; plans all dependent materials |
| MD03 | MRP Run — Single Item, Single Level | Plans one material only; no BOM explosion |
| MD04 | Stock/Requirements List | Dynamic real-time view of stock, requirements, and planned receipts; primary MRP results view |
| MD05 | MRP List | Snapshot of last MRP run results (static, unlike MD04) |
| MD06 | Collective Display MRP List | Multiple materials at once; planner workload view |
| MD07 | Stock/Requirements List (Collective) | Multiple materials collective view |
| MD11 | Create Planned Order | Manual planned order creation |
| MD12 | Change Planned Order | Convert/change planned order before MRP converts it to PO/PR |
| MD61 | Create Planned Independent Requirements | Manual demand input for make-to-stock planning |

**Total: 10 MRP/planning T-codes.**

**Grand Total: ~67 T-codes** (within the ~65 target with small overage on purchasing side; planner can trim 2-3 display-only variants if strict 65 is required).

---

## Commonly-Wrong Field Locations in Material Master (CORRECTION Blocks)

These are the highest-priority CORRECTION blocks for master-data.md and anywhere material master views are discussed. Confidence: HIGH based on SAP Community discussions and training data.

### CORRECTION 1: Valuation Class is in Accounting 1 view, NOT Basic Data or Purchasing

**Wrong claim:** "Valuation class is maintained in the Basic Data view or Purchasing view."
**Correct:** Valuation class (BKLAS) is in the **Accounting 1 view** (MBEW table). It is the critical field linking the material to OBYC account determination. Many consultants look for it in Basic Data 1 because "it seems like a general attribute" — it is not general. It is plant-and-valuation-area-specific, stored in MBEW.

**Field:** MBEW-BKLAS (Valuation Class)
**View:** Accounting 1
**Table:** MBEW (Material Valuation)
**Key:** MANDT + MATNR + BWKEY (valuation area = plant in standard config)

### CORRECTION 2: Price Control (S/V) is in Accounting 1 view, NOT MRP or Purchasing

**Wrong claim:** "The price control field (standard vs moving average) is in the MRP view or Purchasing view."
**Correct:** Price control indicator (VPRSV) is in the **Accounting 1 view** (MBEW table). It controls whether the material uses Standard Price (S) or Moving Average Price (V). It is NOT in MRP 1-4 views and NOT in the Purchasing view.

**Field:** MBEW-VPRSV (Price Control Indicator: S = Standard, V = Moving Average)
**View:** Accounting 1
**Table:** MBEW

**Critical implication:** When consultants look for price control during an OBYC troubleshooting session, they often look in MRP or Purchasing views first. Always check Accounting 1.

### CORRECTION 3: Reorder Point and MRP Type are in MRP 1 view, NOT Basic Data

**Wrong claim:** "Reorder point quantity is in Basic Data because it seems like a general stock parameter."
**Correct:** Reorder point (MINBE) and MRP Type (DISMM — e.g., VB = manual reorder point, ND = no MRP) are in the **MRP 1 view** (MARC table, plant-specific). Basic Data 1/2 contains only client-level data (description, base UoM, material type) — no planning parameters.

**Fields in MRP 1:**
- MARC-DISMM (MRP Type)
- MARC-MINBE (Reorder Point)
- MARC-DZEIT (In-house production time)
- MARC-PLIFZ (Planned Delivery Time)

### CORRECTION 4: Purchasing Group is in the Purchasing view (MARC), NOT Vendor Master

**Wrong claim:** "The purchasing group field is in the vendor master — it controls which buyer handles the vendor."
**Correct:** Purchasing group (EKGRP) in MIRO/PO context comes from the **Purchasing view of the material master** (MARC-EKGRP). The vendor master has a purchasing organization (LFM1) but does NOT have a purchasing group field. The purchasing group is a material+plant-level assignment controlling which buyer handles procurement for that material.

### CORRECTION 5: GR-Based Invoice Verification flag is in the Vendor Purchasing View (LFM1), NOT the PO

**Wrong claim:** "GR-based IV is controlled at the PO document type or company code level."
**Correct:** GR-Based Invoice Verification indicator (WEBRE) is a field in **LFM1** (Vendor Purchasing Organization Data). When WEBRE = X on the vendor master, MIRO will require a GR to exist before the invoice can be posted. This flag can also appear at the individual PO line level (item WEPOS indicator), but the default comes from LFM1.

**Field:** LFM1-WEBRE (GR-Based Invoice Verification)
**View:** Vendor Purchasing View (XK01/XK02 → Purchasing Data tab)

### CORRECTION 6: Standard Price is in Accounting 1, NOT the Costing view for ECC materials

**Wrong claim:** "The standard price value is maintained in the Costing 1 view."
**Correct:** For ECC 6.0, the **current standard price** actually used for inventory valuation is stored in **MBEW-STPRS** (Standard Price) and **MBEW-VERPR** (Moving Average Price). The Costing views (Costing 1, Costing 2) hold cost estimates from CO-PC — a cost estimate must be marked and released before it updates the Accounting 1 standard price. Reading Accounting 1 shows the operative price. Costing views show the planned/estimated cost before release.

### CORRECTION 7: Plant Data / Storage 1 view: Batch management flag is here, NOT Basic Data

**Wrong claim:** "Batch management is configured at the material type level in Basic Data."
**Correct:** The batch management indicator (MARA-XCHPF or MARC-XCHPF) can be plant-specific — the relevant control for plant-level batch management is in the **Plant Data / Storage 1 view** (MARC table). The material type can mandate batches at client level, but the per-plant activation is in the storage view.

---

## Key SAP Accuracy Traps in MM Content

These are the MM equivalents of the cash discount / OBB8 trap in FI — places where well-intentioned SAP documentation consistently gets it wrong.

### Trap 1: OMBA is NOT for Purchase Order document types

**The trap:** Content claiming "configure PO document types in OMBA."
**Reality:** OMBA = "Number Assignment for Accounting Documents" — it is an FI transaction for accounting document number ranges, not purchasing. PO document types are configured via: SPRO → MM → Purchasing → Purchase Order → Define Document Types (T-code: OMH6 or via the SPRO tree). Number ranges for purchasing documents use separate T-codes per document category (OMLF for purchase requisitions, OMH7 for POs, etc.).

**Confidence:** HIGH (confirmed via SAP T-code search — OMBA description is explicitly "Number Assgmt. for Accounting Docs").

### Trap 2: OLMR is the IMG node root, NOT a standalone T-code for tolerance configuration

**The trap:** Content saying "configure LIV tolerances using T-code OLMR."
**Reality:** OLMR is the SAP IMG customizing node for Logistics Invoice Verification — it opens the IMG subtree, not a configuration screen. The actual T-code for setting tolerance limits is **OMR6** (Set Tolerance Limits). Vendor-specific tolerance groups are in **OMRX**.

**SPRO path:** Materials Management ▸ Logistics Invoice Verification ▸ Invoice Block ▸ Set Tolerance Limits (OMR6)

### Trap 3: PRD (price difference) fires for Standard Price (S) materials only — confirmed critical for MM-FI integration content

**The trap:** Saying "MIRO posts a price difference to PRD account for all materials."
**Reality:** PRD fires on GR (MIGO movement 101) ONLY for standard price (S) materials. For moving average price (V) materials, the stock account (BSX) absorbs the full PO price — no PRD posting occurs. This was already documented in the FI knowledge base (modules/fi/account-determination.md) and must be consistently stated in MM content.

### Trap 4: ME59N is automatic PR-to-PO conversion, NOT a display T-code

**The trap:** Conflating ME59N with ME53N (display PR) because both end in 9N.
**Reality:** ME59N = "Automatically Generate Purchase Orders from Purchase Requisitions." It requires that source determination (info record or source list) is configured and assigned. ME53N = Display PR. These are completely different functions.

### Trap 5: MIRO credit memo vs FB65 — wrong T-code for PO-based credit

**The trap:** Using FB65 (FI vendor credit memo) for a credit memo from a vendor that references a purchase order.
**Reality:** PO-based credit memos must be entered in **MIRO** using transaction type "Credit Memo" (not FB65). Using FB65 for a PO-based credit bypasses the three-way match, does not update MM logistics tables (EKBE, RSEG), and creates reconciliation problems between MM and FI. This is the MM equivalent of the MIRO vs FB60 distinction documented in FI tcodes.md.

### Trap 6: MD04 vs MD05 — live vs static MRP results

**The trap:** Using MD05 to check "current" MRP status, expecting real-time information.
**Reality:** MD05 (MRP List) is a SNAPSHOT taken at the time of the last MRP run and does NOT update when stock movements or new requirements are created. MD04 (Stock/Requirements List) is the DYNAMIC view that updates in real time. For monitoring purposes, always use MD04. MD05 is useful for investigating what MRP saw at a specific run point.

### Trap 7: Valuation Area = Company Code vs Plant (default)

**The trap:** Assuming valuation area is at company code level.
**Reality:** In standard ECC 6.0 implementations, valuation area equals PLANT (OMWM setting). This means material valuations (prices, stock values) are maintained per plant, not per company code. A material in Plant 1000 and Plant 2000 (same company code) can have different standard prices and moving average prices. The OMWM setting cannot be changed after materials have been valued — set correctly at go-live.

---

## SPRO Transaction Codes and IMG Paths — All 4 Config Areas

### Area 1: Enterprise Structure

**Plant Parameters (OMSY)**
- **T-code:** OMSY
- **IMG Path:** Logistics — General ▸ Material Master ▸ Basic Settings ▸ Maintain Company Codes for Materials Management
- **What to configure:** Activate company code for MM, set the current period (important for period-end), fiscal year variant

**Storage Location Setup**
- **T-code:** OMB2 (GI), OMB3 (GR) — controls automatic storage location creation
- **IMG Path (OMB2):** Materials Management ▸ Inventory Management and Physical Inventory ▸ Goods Issue / Transfer Postings ▸ Create Storage Location Automatically
- **IMG Path (OMB3):** Materials Management ▸ Inventory Management and Physical Inventory ▸ Goods Receipt ▸ Create Storage Location Automatically
- **What to configure:** Whether storage locations should be created automatically when a goods movement references a non-existing storage location

**Enterprise Structure — Plant Definition**
- **T-code:** OX10 (Define Plant)
- **IMG Path:** Enterprise Structure ▸ Definition ▸ Logistics — General ▸ Define, Copy, Delete, Check Plant
- **Assignment to Company Code:** OX18 (Assign Plant to Company Code)
- **Assignment of Purchasing Org to Plant:** OX17
- **Assignment of Purchasing Org to Company Code:** OX01

### Area 2: Purchasing Configuration

**Purchasing Document Types**
- **T-code:** OMH6 (Define PO Document Types) — NOT OMBA
- **IMG Path:** Materials Management ▸ Purchasing ▸ Purchase Order ▸ Define Document Types
- **What to configure:** PO document types (NB = standard PO, FO = framework order/blanket PO, ZNB = custom), number range assignment, field selection key

**Number Ranges for Purchasing Documents**
- **T-code:** OMH7 (Number Ranges for PO), OMLF (PR number ranges)
- **IMG Path:** Materials Management ▸ Purchasing ▸ Purchase Order ▸ Define Number Ranges

**Screen Layout Rules — Purchase Orders**
- **T-code:** OMF4 (for PO header), OMEC (for PO item)
- **IMG Path:** Materials Management ▸ Purchasing ▸ Purchase Order ▸ Define Screen Layout at Document Level (OMF4)
- **What to configure:** Which fields are required/optional/hidden/display-only at the PO header and item level

**Tolerance Keys for Purchasing**
- **Note:** Purchasing-side tolerances (for PO approval) are different from LIV invoice tolerances. Purchasing tolerances for release strategies are configured within the release strategy config (OME4/OMGS).

**Source Determination / Source List**
- **T-code:** OMGM (Activate source list requirement per plant)
- **IMG Path:** Materials Management ▸ Purchasing ▸ Source Determination ▸ Define Source List Requirement

### Area 3: Inventory Management

**Movement Type Configuration**
- **T-code:** OMJJ
- **IMG Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Movement Types ▸ Copy, Change Movement Types
- **What to configure:** For each movement type — allowed transaction types, field selection, OMJJ defines which OBYC transaction keys fire. Standard movement types (101 GR, 102 GR reversal, 201 GI to cost center, 261 GI to production order, 301 plant transfer, 311 SLoc transfer, 551 scrapping, 601 GI to delivery) should not be modified — copy and create custom types only.

**GR/GI Document Settings**
- **T-code:** OMGN (Set tolerance for under/over delivery at GR)
- **IMG Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Goods Receipt ▸ Set Tolerance Limits

**Number Ranges for Material Documents**
- **T-code:** OMBT
- **IMG Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Number Assignment ▸ Define Number Assignment for Material and Physical Inventory Documents
- **What to configure:** Number range intervals for material document numbers (MKPF/MSEG table key)

**Physical Inventory Settings**
- **T-code:** OMIE (Counting document), OMII (Difference document)
- **IMG Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Physical Inventory ▸ Number Assignment

### Area 4: Invoice Verification / LIV

**OLMR — LIV IMG Node (root)**
- OLMR opens the LIV customizing section; use specific sub-T-codes below

**Tolerance Limits**
- **T-code:** OMR6
- **IMG Path:** Materials Management ▸ Logistics Invoice Verification ▸ Invoice Block ▸ Set Tolerance Limits
- **What to configure:** Upper and lower tolerance limits (absolute and percentage) for each tolerance key, per company code

**Complete Tolerance Key Reference:**
| Key | What It Checks |
|-----|---------------|
| BD | Small differences — auto-post difference to tolerance GL account instead of blocking |
| DQ | Quantity variance: invoice quantity exceeds PO/GR quantity |
| DW | Quantity variance when GR quantity is zero (GR not yet done) |
| PP | Price variance: invoice price deviates from PO price |
| PS | Price variance against estimated price (blanket POs) |
| ST | Schedule variance: invoice date vs PO delivery date |
| VP | Moving average price variance: invoice price would cause MAP variance beyond limit |
| AN | Amount for item WITHOUT order reference |
| AP | Amount for item WITH order reference |
| BR | OPUn variance — invoice before GR (quantity unit variance) |
| BW | OPUn variance — GR before invoice |
| KW | Variance from condition value |
| LA | Amount of blanket purchase order |
| LD | Blanket PO time limit exceeded |
| PC | Price variance: contract |

**Key behavioral difference:** BD tolerance posts small differences automatically (no blocking even if exceeded). All other keys BLOCK the invoice if the upper limit is exceeded. The user must release blocked invoices via MRBR.

**Vendor-Level Tolerance Groups**
- **T-code:** OMRX (Define Tolerance Groups for Employees/Vendors)
- **What to configure:** If different vendors need different tolerance limits, create tolerance groups and assign to vendor master

**GR-Based Invoice Verification Setting**
- Default comes from LFM1-WEBRE on vendor master (per vendor, per purchasing org)
- Can also be set at the PO item level (EKPO-WEPOS)
- Company code default: SPRO ▸ LIV ▸ Incoming Invoice ▸ Set Check for Duplicate Invoices

**Invoice Blocking Reasons**
- **T-code:** OMR4 (Define Blocking Reasons for Invoices)
- **IMG Path:** Materials Management ▸ Logistics Invoice Verification ▸ Invoice Block ▸ Define Blocking Reasons

**Valuation / Price Control Basics**
- **T-code:** OMWM (Valuation Area = Plant or Company Code — set at implementation start)
- **IMG Path:** Materials Management ▸ Valuation and Account Assignment ▸ Determine Valuation Level
- **Critical:** Once set to plant-level (standard), this cannot be changed after materials are valued. Plan this at project start.
- **Account Category Reference:** OMSK (Define Account Category References) — groups valuation classes for OBYC account determination (Phase 6 detail)

---

## Critical Process Steps in Procure-to-Pay (with Role Annotations)

The P2P narrative needs role annotations at the points where the process touches multiple roles or crosses module boundaries. Key annotation points:

### Step 1: Purchase Requisition Creation (ME51N)
- **Role:** Requester / Materials Planner
- **Cross-reference:** PR account assignment (cost center CC, internal order IO, project WBS) drives CO postings. Wrong account assignment here propagates through the entire P2P chain.
- **Annotation flag:** PR can be created manually or generated automatically by MRP run (MD01/MD02) as a planned order converted to PR.

### Step 2: PR Release / Approval (ME28, ME29N)
- **Role:** Purchasing Manager / Budget Owner
- **Annotation flag:** Release strategy is characteristic-based (configured in Phase 6). Brief concept only here — the key T-codes ME28 (collective release) and ME29N (individual) are the day-to-day operations.
- **CORRECTION note:** ME28 shows a LIST of POs pending release; ME29N is for releasing a SPECIFIC PO. Do not confuse with ME28N which is a separate variant.

### Step 3: PR to PO Conversion (ME21N manual or ME59N automatic)
- **Role:** Buyer / Purchasing Agent
- **Annotation flag:** ME59N requires source determination (source list or info record) to be in place. Without a valid source, ME59N cannot convert automatically.
- **Sourcing logic:** System checks source list (EORD) → then purchasing info record (EINE/EINA) → then outline agreement. First valid source wins.

### Step 4: Goods Receipt (MIGO — Action 01, Reference Purchase Order)
- **Role:** Warehouse / Receiving Team
- **FI Impact:** Posting creates FI document via OBYC: BSX (Dr inventory) and WRX (Cr GR/IR clearing). For standard price materials, PRD may also fire.
- **Annotation flag:** Movement type 101 = GR against PO (creates planned receipt → actual stock). GR quantity tolerance (under/over delivery) controlled by OMGN.
- **Cross-reference:** GR posts to MKPF (document header) and MSEG (line items) in ECC 6. The GR-based invoice verification flag (LFM1-WEBRE) means MIRO cannot be posted until at least one GR exists.

### Step 5: Invoice Verification (MIRO)
- **Role:** Accounts Payable Accountant
- **Three-way match logic:** MIRO reads the PO (price/quantity terms) and the GR documents (confirmed quantity). The system calculates variances against each tolerance key. If within tolerance, auto-posts. If outside tolerance, blocks.
- **FI Impact:** MIRO debits GR/IR clearing (WRX — offsetting the GR posting) and credits Vendor (sub-ledger, reconciliation account). Creates FI document automatically.
- **Annotation flag:** MIRO is the MM-FI handoff point. AP accountants see this in both module contexts. Emphasize that MIRO (not FB60) is required for PO-based invoices.

### Step 6: Invoice Release if Blocked (MRBR)
- **Role:** Accounts Payable Accountant / Finance Manager
- **Process:** Check blocking reason, verify with requestor/buyer/vendor as appropriate, release in MRBR.

### Step 7: Payment (F110 Automatic Payment Program)
- **Role:** Accounts Payable Accountant
- **Cross-reference:** F110 is documented in FI processes.md. The MM P2P process.md should cross-reference it rather than duplicate. The P2P narrative should show the handoff: once MIRO posts and clears the GR/IR, the vendor open item appears in FBL1N and is picked up by F110.

---

## ECC 6 vs S/4HANA Disambiguation Notes for MM

These are the MM-specific differences that must be flagged in the documentation. Confidence: HIGH (confirmed by SAP community posts and official SAP S/4HANA documentation).

### 1. Material Document Tables: MKPF/MSEG → MATDOC (single table)

| ECC 6 | S/4HANA | Impact |
|-------|---------|--------|
| Material documents stored in MKPF (header) + MSEG (line items) — two-table structure | Single table MATDOC replaces both MKPF and MSEG | Queries/reports using SE16 on MKPF/MSEG work in ECC; in S/4HANA, query MATDOC instead |

**Flag this** wherever MKPF/MSEG are mentioned in queries, SE16 lookups, or ABAP context.

### 2. Material Ledger: Optional → Mandatory

| ECC 6 | S/4HANA | Impact |
|-------|---------|--------|
| Material Ledger (ML) is optional — activated per plant via configuration | Material Ledger is mandatory in all S/4HANA systems (since S/4HANA 1511) | In ECC, moving average price (V) without ML is common; in S/4HANA, ML always runs alongside |

**Flag this** in the price control (S/V) discussion and the valuation section.

### 3. Vendor Master: LFA1/LFB1/LFM1 → Business Partner (BP) / BUT000

| ECC 6 | S/4HANA | Impact |
|-------|---------|--------|
| Vendor master uses XK01/FK01/MK01; tables LFA1, LFB1, LFM1 | Business Partner model (transaction BP); table BUT000 with role-based extensions | XK01/FK01 are obsolete in S/4HANA; vendor + customer are managed as unified Business Partner |

**Flag this** in the vendor master section — this is the biggest structural change in master data.

### 4. MRP: Classic MRP (MD01/MD02) → MRP Live (pMRP / MD01N)

| ECC 6 | S/4HANA | Impact |
|-------|---------|--------|
| MRP runs as batch job in off-peak hours via MD01/MD02 | MRP Live runs in real-time via MD01N (single transaction replacing MD01/MD02/MD03) | In S/4HANA, MD01N does not create an MRP list (MD05 irrelevant); always use MD04 for results |

**Flag this** in the MRP T-code section and MRP 1 view discussion.

### 5. Stock Reporting: MMBE same UI, but table source differs

| ECC 6 | S/4HANA | Impact |
|-------|---------|--------|
| MMBE reads from MARD, MCHB, MKPF-derived views | MMBE in S/4HANA reads from MATDOC-derived views (ACDOCA for values) | MMBE UI is familiar but underlying table is different; custom ABAP reading MARD directly may need rework |

### 6. Purchasing: No major T-code changes — ME21N/ME22N/ME23N remain primary

The core purchasing T-codes (ME21N, ME22N, ME23N, MIGO, MIRO) are the same in S/4HANA with SAP GUI. The primary change is the Fiori app layer — S/4HANA offers Fiori apps for purchasing that provide the same function with modern UI. The ECC T-codes still work in S/4HANA with SAP GUI.

**Flag this** once, at the top of tcodes.md: "T-codes listed work in both ECC 6.0 and S/4HANA via SAP GUI. S/4HANA also offers equivalent Fiori apps."

---

## Architecture Patterns for MM Files

Following FI module conventions exactly (no deviation):

### tcodes.md Structure
```
--- frontmatter ---
# Materials Management — Transaction Codes
> ECC 6.0 reference note

## Workflow Index
| Process Stage | T-code(s) | Submodule | Notes |

---
## Purchasing (ME-family)
### ME51N — Create Purchase Requisition
### ME52N — Change Purchase Requisition
... (each T-code = own ### section)

## Inventory Management (MB-family / MIGO)
### MIGO — Goods Movements (Enjoy Transaction)
...

## Logistics Invoice Verification (LIV)
### MIRO — Enter Invoice (Logistics Invoice Verification)
...

## Material Requirements Planning (MD-family)
### MD01 — MRP Run (Total Planning)
...

## Master Data — Purchasing
### XK01 — Create Vendor Master (Central)
...
### ME11 — Create Purchasing Info Record
...
```

### master-data.md Structure (single file per CONTEXT.md decision)
```
## Material Master
### MARA — General Material Data (Client Level)
### MARC — Plant Data (Plant Level)
### MARD — Storage Location Data
### MBEW — Material Valuation (Accounting 1/2 views)
[CORRECTION blocks within each section]

## Vendor Master
### LFA1 — General Data
### LFB1 — Company Code Data (FI)
### LFM1 — Purchasing Organization Data (MM-emphasis)

## Purchasing Info Records
### EINA — Info Record Header
### EINE — Info Record Purchasing Organization Data

## Source Lists
### EORD — Source List
```

### config-spro.md Structure
```
## Enterprise Structure
## Purchasing Configuration
## Inventory Management Configuration
## Logistics Invoice Verification (LIV) Configuration
## Valuation Basics
```

### processes.md Structure (narrative + table, role annotations)
```
## Procure-to-Pay (Standard PO Process)
[Narrative with step-by-step role-annotated text]
[Summary table: Step | Activity | T-code | Role | Output]

## Procure-to-Pay (Direct Procurement — PR to PO)
## Invoice Verification and Three-Way Match
## Physical Inventory Process
```

---

## Common Pitfalls for Phase 5 Content Creation

### Pitfall 1: Using OMBA for Purchasing Document Types

**What goes wrong:** Writers document OMBA as "Define Purchasing Document Types."
**Why it happens:** OMBA appears in MM config searches because it is in the MM area; the description "Number Assignment for Accounting Docs" sounds like it could be purchasing.
**How to avoid:** OMBA is an FI transaction for accounting document number ranges. Use OMH6 for PO document types. Verify every SPRO T-code claim.

### Pitfall 2: Collapsing MIGO Variants

**What goes wrong:** Documenting MIGO as a single entry instead of separate display/create/change entries.
**Why it happens:** MIGO is one T-code that handles multiple actions.
**How to avoid:** CONTEXT.md explicitly states: document MIGO create/change/display separately. Follow the same rule for ME21N/ME22N/ME23N.

### Pitfall 3: Missing the GR/IR Clearing Account Open Item Requirement

**What goes wrong:** Documenting the GR/IR clearing account without noting the open item management requirement.
**Why it happens:** This is a FI-side requirement that MM writers often skip.
**How to avoid:** The GR/IR clearing account (WRX OBYC key) MUST be flagged as open item managed in FS00. Without this, F.13 cannot clear GR/IR items. Cross-reference FI config-spro.md Pitfall 7.

### Pitfall 4: Omitting the PRD Distinction for Standard vs Moving Average Price

**What goes wrong:** Saying "MIGO GR posts BSX and WRX" without noting that PRD only fires for standard price materials.
**Why it happens:** Simplified explanations omit the condition.
**How to avoid:** Always state: "PRD fires only when material has price control S (standard price). For price control V (moving average), BSX absorbs the full PO price — no PRD posting." This was established in Phase 3 (FI account-determination.md) and must be consistent in Phase 5.

### Pitfall 5: Documenting LFM1 Without the Purchasing View Emphasis

**What goes wrong:** Treating LFM1 as a brief addendum to LFA1/LFB1 with minimal field coverage.
**Why it happens:** FI-oriented writers emphasize LFA1/LFB1 (FI-relevant fields) and skip LFM1 details.
**How to avoid:** CONTEXT.md specifies "purchasing view emphasis: LFM1 fields." Key LFM1 fields to cover: WAERS (PO currency), WEBRE (GR-based IV), ZTERM (purchasing payment terms), INCO1/INCO2 (incoterms), MINBW (minimum order value), MWSKZ (tax indicator), VERKF (sales contact person), TELF1 (phone).

---

## Open Questions

1. **OMF4 vs OMEC exact scope:** Both are screen layout T-codes for purchasing documents. Research suggests OMF4 applies at the document level and OMEC at the item level, but exact distinguishing scope was not fully verified. Planner should confirm via SAP Help before documenting config step.
   - What we know: Both are valid MM SPRO T-codes for PO screen layout
   - What's unclear: Exact scope boundary between the two
   - Recommendation: Document both with a note that OMF4 = header-level, OMEC = item-level field selection (standard SAP knowledge)

2. **ME35 vs ME29N for contract release:** Contracts (ME31K) released via ME35; individual PO release via ME29N. The distinction between agreement release (ME35) and PO release (ME29N) should be documented clearly in the T-code section.
   - Recommendation: Include ME35 in the outline agreements T-code listing

3. **Number of IV tolerance keys in scope:** The full list has 15 keys (AN, AP, BD, BR, BW, DQ, DW, KW, LA, LD, PC, PP, PS, ST, VP). CONTEXT.md mentions BD/DQ/PP/ST/VP as examples. Document all 15 with the five mentioned getting extra attention as the most-used.

---

## Sources

### Primary (HIGH confidence — verified in FI module and training data)
- modules/fi/account-determination.md — PRD behavior for standard vs moving average confirmed
- modules/fi/master-data.md — LFA1/LFB1/LFM1 fields verified against ABAP dictionary
- modules/fi/tcodes.md — MIRO entry confirming MIRO vs FB60 for PO-based invoices
- modules/fi/config-spro.md — GR/IR account OI management requirement (Pitfall 7)
- .claude/rules/sap-disambiguation.md — ECC vs S/4HANA MM table differences (MKPF/MSEG vs MATDOC, ML mandatory, vendor BP)

### Secondary (MEDIUM confidence — SAP Community and search-verified)
- SAP Community: Invoice Tolerance Keys insight (all 15 keys confirmed: AN, AP, BD, BR, BW, DQ, DW, KW, LA, LD, PC, PP, PS, ST, VP)
- SAP Community/guru99: OMR6 confirmed as tolerance limit T-code (OLMR = node only)
- SAP Community: MD04 (live) vs MD05 (static MRP list snapshot) distinction
- SAP Community: ME28 (collective release) vs ME29N (individual release PO) confirmed
- SAP Community: MKPF/MSEG → MATDOC S/4HANA change confirmed
- SAP Community: Material Ledger mandatory in S/4HANA since 1511 confirmed

### Tertiary (LOW confidence — training data only, not independently verified)
- OMF4 vs OMEC exact scope distinction — standard knowledge but not independently confirmed in this session
- OMBT as number ranges for material documents — high probability correct but not independently confirmed

---

## Metadata

**Confidence breakdown:**
- T-code selections: HIGH — well-established SAP ECC 6.0 standard; cross-validated with multiple sources
- Material master CORRECTION blocks: HIGH — field-to-table mappings are dictionary-level facts
- SPRO paths and T-codes: MEDIUM-HIGH — core T-codes confirmed; some details (OMF4 vs OMEC) flagged LOW
- Process flow: HIGH — P2P is the most-documented SAP process; role assignments are standard
- ECC vs S/4 differences: HIGH — confirmed against sap-disambiguation.md and search results

**Research date:** 2026-02-16
**Valid until:** Stable — ECC 6.0 MM is a mature, unchanging platform. Review only if S/4HANA content scope changes.
