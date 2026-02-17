---
module: mm
content_type: config-spro
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Materials Management — SPRO/IMG Configuration

> ECC 6.0 reference. Configuration paths verified against standard ECC 6.0 IMG. T-code shortcuts noted in parentheses where available. No MRP SPRO configuration in this file (deferred). OBYC account determination detail deferred to Phase 6.

## 1. Enterprise Structure

### Define Plant (OX10)

**SPRO Path:** Enterprise Structure ▸ Definition ▸ Logistics — General ▸ Define, Copy, Delete, Check Plant
**T-code:** OX10
**What to configure:** Define plants with plant code, name, address, and factory calendar. Each plant is assigned to exactly one company code.

### Assign Plant to Company Code (OX18)

**SPRO Path:** Enterprise Structure ▸ Assignment ▸ Logistics — General ▸ Assign Plant to Company Code
**T-code:** OX18
**What to configure:** Assigns each plant to its company code. This assignment is mandatory and determines which company code's fiscal year variant, currency, and chart of accounts govern the plant.

### Assign Purchasing Organization to Plant (OX17)

**SPRO Path:** Enterprise Structure ▸ Assignment ▸ Materials Management ▸ Assign Purchasing Organization to Plant
**T-code:** OX17
**What to configure:** Links purchasing organization to plant(s). A purchasing org can serve multiple plants (cross-plant purchasing) or be plant-specific.

### Assign Purchasing Organization to Company Code (OX01)

**SPRO Path:** Enterprise Structure ▸ Assignment ▸ Materials Management ▸ Assign Purchasing Organization to Company Code
**T-code:** OX01
**What to configure:** Links purchasing organization to company code. Required for vendor master data (LFM1 is per purchasing org + vendor).

### Activate MM for Company Code (OMSY)

**SPRO Path:** Logistics — General ▸ Material Master ▸ Basic Settings ▸ Maintain Company Codes for Materials Management
**T-code:** OMSY
**What to configure:** Activates company code for MM use — sets the current MM period and fiscal year variant. Must be done before any MM transactions can be posted in the company code.

### Automatic Storage Location Creation (OMB2 / OMB3)

**SPRO Path (OMB2 — GI):** Materials Management ▸ Inventory Management and Physical Inventory ▸ Goods Issue / Transfer Postings ▸ Create Storage Location Automatically
**SPRO Path (OMB3 — GR):** Materials Management ▸ Inventory Management and Physical Inventory ▸ Goods Receipt ▸ Create Storage Location Automatically
**T-codes:** OMB2 (goods issue), OMB3 (goods receipt)
**What to configure:** Whether storage locations are created automatically when a goods movement references a non-existing storage location. Typically disabled in production to maintain storage location discipline.

---

## 2. Purchasing Configuration

### Define Purchase Order Document Types (OMH6)

**SPRO Path:** Materials Management ▸ Purchasing ▸ Purchase Order ▸ Define Document Types
**T-code:** OMH6

> **CRITICAL:** OMBA is NOT for purchase order document types. OMBA = "Number Assignment for Accounting Documents" — an FI transaction for accounting document number ranges. For PO document types, use OMH6. This is one of the most common MM config navigation errors.

**What to configure:** PO document types control document behavior:
| Document Type | Description | Usage |
|---------------|-------------|-------|
| NB | Standard Purchase Order | Default for external procurement |
| FO | Framework Order | Blanket/umbrella PO with value limit |
| UB | Stock Transport Order | Inter-plant transfer via PO |
| ZNB | Custom PO type (example) | Copy NB for organization-specific rules |

Each document type defines: number range, item category default, field selection key, release procedure relevance.

### Number Ranges for Purchasing Documents (OMH7 / OMLF)

**SPRO Path (PO):** Materials Management ▸ Purchasing ▸ Purchase Order ▸ Define Number Ranges
**T-code:** OMH7 (purchase orders), OMLF (purchase requisitions)
**What to configure:** Internal (system-assigned) vs external (user-assigned) number ranges per document category. Standard: internal numbering for both POs and PRs.

### Screen Layout — Purchase Orders (OMF4 / OMEC)

**SPRO Path:** Materials Management ▸ Purchasing ▸ Purchase Order ▸ Define Screen Layout at Document Level
**T-codes:** OMF4 (document/header level), OMEC (item level)
**What to configure:** Which fields are required, optional, hidden, or display-only at the PO header and item level. Controls data entry enforcement — e.g., make "Agreement" field required, hide "Tracking Number."

### Source List Requirement (OMGM)

**SPRO Path:** Materials Management ▸ Purchasing ▸ Source Determination ▸ Define Source List Requirement
**T-code:** OMGM
**What to configure:** Activate source list requirement per plant per material type. When active, ME59N (automatic PR-to-PO conversion) requires a valid source list entry (EORD) for the material+plant. Without source list activation, ME59N may use info records as fallback.

---

## 3. Inventory Management Configuration

### Movement Type Configuration (OMJJ)

**SPRO Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Movement Types ▸ Copy, Change Movement Types
**T-code:** OMJJ
**What to configure:** Movement types control how goods movements are processed and which OBYC transaction keys fire. Standard movement types should NOT be modified — copy and create custom movement types instead.

Key standard movement types (do not modify — copy for customization):
| Movement Type | Description | OBYC Keys |
|---------------|-------------|-----------|
| 101 | GR against PO | BSX, WRX (PRD for S-price materials) |
| 102 | GR reversal (against PO) | Reverse of 101 |
| 201 | GI to cost center | BSX, GBB (cost center posting) |
| 261 | GI to production order | BSX, GBB |
| 301 | Plant-to-plant transfer (one step) | BSX both plants |
| 303 | Plant-to-plant transfer (two step — issue) | BSX, GBB |
| 305 | Plant-to-plant transfer (two step — receipt) | BSX, GBB |
| 311 | Storage location transfer | No FI posting (same valuation area) |
| 501 | GR without PO (found stock) | BSX, GBB |
| 551 | Scrapping | BSX, GBB |
| 561 | Initial stock load | BSX, GBB |
| 601 | GI for delivery (SD) | BSX, GBB |

### GR Tolerance Limits (OMGN)

**SPRO Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Goods Receipt ▸ Set Tolerance Limits
**T-code:** OMGN
**What to configure:** Under-delivery and over-delivery tolerance percentages for goods receipt against PO. Controls whether system accepts GR quantity that deviates from PO quantity.

### Number Ranges for Material Documents (OMBT)

**SPRO Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Number Assignment ▸ Define Number Assignment for Material and Physical Inventory Documents
**T-code:** OMBT
**What to configure:** Number range intervals for material document numbers (MKPF/MSEG table key). Standard: internal numbering, single number range for all material documents.

### Physical Inventory Number Ranges (OMIE / OMII)

**SPRO Path:** Materials Management ▸ Inventory Management and Physical Inventory ▸ Physical Inventory ▸ Number Assignment
**T-codes:** OMIE (physical inventory documents), OMII (difference posting documents)
**What to configure:** Number ranges for physical inventory count documents and difference posting documents.

---

## 4. Logistics Invoice Verification (LIV) Configuration

> **CRITICAL:** OLMR is the SAP IMG customizing node for LIV — it opens the IMG subtree, NOT a configuration screen. Do not document OLMR as a standalone T-code for tolerance configuration. Use the specific T-codes below (OMR6, OMRX, OMR4).

### Set Tolerance Limits (OMR6)

**SPRO Path:** Materials Management ▸ Logistics Invoice Verification ▸ Invoice Block ▸ Set Tolerance Limits
**T-code:** OMR6
**What to configure:** Upper and lower tolerance limits (absolute amount and percentage) for each tolerance key, per company code.

**Complete Tolerance Key Reference (all 15 keys):**

| Key | What It Checks | Behavior When Exceeded |
|-----|----------------|------------------------|
| **BD** | **Small differences — auto-post** | **UNIQUE: Auto-posts difference to tolerance GL account. Does NOT block.** |
| DQ | Quantity variance: invoice qty > PO/GR qty | BLOCKS invoice → MRBR release required |
| DW | Quantity variance when GR qty is zero | BLOCKS invoice → MRBR release required |
| PP | Price variance: invoice price vs PO price | BLOCKS invoice → MRBR release required |
| PS | Price variance: estimated price (blanket POs) | BLOCKS invoice → MRBR release required |
| ST | Schedule variance: invoice date vs PO delivery date | BLOCKS invoice → MRBR release required |
| VP | Moving average price variance | BLOCKS invoice → MRBR release required |
| AN | Amount for item WITHOUT order reference | BLOCKS invoice → MRBR release required |
| AP | Amount for item WITH order reference | BLOCKS invoice → MRBR release required |
| BR | Order price unit variance — invoice before GR | BLOCKS invoice → MRBR release required |
| BW | Order price unit variance — GR before invoice | BLOCKS invoice → MRBR release required |
| KW | Variance from condition value | BLOCKS invoice → MRBR release required |
| LA | Amount of blanket purchase order | BLOCKS invoice → MRBR release required |
| LD | Blanket PO time limit exceeded | BLOCKS invoice → MRBR release required |
| PC | Price variance: contract price | BLOCKS invoice → MRBR release required |

> **KEY BEHAVIORAL DIFFERENCE:** BD is the ONLY tolerance key that auto-posts differences (small price variances posted to a tolerance GL account without blocking). ALL other 14 keys BLOCK the invoice when the tolerance limit is exceeded. Blocked invoices must be released via MRBR.

**Commonly configured keys (most implementations focus on these 5):**
- **BD** — Small differences (set absolute amount, e.g., $5.00; auto-posts below this)
- **DQ** — Quantity variance (set percentage, e.g., 5%)
- **PP** — Price variance (set percentage, e.g., 2% and absolute, e.g., $10.00)
- **ST** — Schedule variance (set number of days)
- **VP** — Moving average price variance (percentage)

### Define Tolerance Groups (OMRX)

**SPRO Path:** Materials Management ▸ Logistics Invoice Verification ▸ Invoice Block ▸ Set Tolerance Limits (then navigate to tolerance groups)
**T-code:** OMRX
**What to configure:** If different vendors or users need different tolerance limits, create tolerance groups and assign to vendor master (LFB1-TOGRU) or user profile.

### Define Blocking Reasons (OMR4)

**SPRO Path:** Materials Management ▸ Logistics Invoice Verification ▸ Invoice Block ▸ Define Blocking Reasons
**T-code:** OMR4
**What to configure:** Custom blocking reasons beyond the automatic tolerance-based blocks. Manual blocks can be set during MIRO entry for management review.

### GR-Based Invoice Verification

**Configuration level:** Vendor master field LFM1-WEBRE (per vendor + purchasing org), overridable at PO item level (EKPO-WEPOS).
**What it controls:** When WEBRE = X, MIRO requires at least one goods receipt (MIGO) to exist for the PO line before the invoice can be posted. This is the three-way match prerequisite.
**Company code default:** SPRO ▸ LIV ▸ Incoming Invoice ▸ Set Check for Duplicate Invoices (includes IV verification defaults).

---

## 5. Valuation Basics

### Determine Valuation Level (OMWM)

**SPRO Path:** Materials Management ▸ Valuation and Account Assignment ▸ Determine Valuation Level
**T-code:** OMWM

> **CRITICAL:** The valuation level setting (plant vs company code) CANNOT be changed after any material has been valued. This must be set correctly before go-live. Standard setting: valuation area = plant.

**What to configure:** Whether material valuations (prices, stock values) are maintained at plant level or company code level.
- **Plant level (standard):** Each plant has independent prices. Material in Plant 1000 and Plant 2000 (same company code) can have different standard/moving average prices.
- **Company code level (rare):** All plants in a company code share one price. Almost never used in modern implementations.

### Price Control: Standard (S) vs Moving Average (V)

**Configured at:** Material master Accounting 1 view (MBEW-VPRSV), not SPRO. Set per material.
- **S (Standard Price):** Inventory valued at predetermined price (MBEW-STPRS). Price differences between PO/invoice and standard price post to PRD account (OBYC). Cost variances are visible.
- **V (Moving Average Price):** Inventory valued at weighted average of all receipts (MBEW-VERPR). Each GR/invoice updates the MAP. BSX absorbs the full value — no PRD posting. Variances absorbed into stock value.

> S/4HANA note: Material Ledger is optional in ECC 6 but mandatory in S/4HANA. In S/4HANA, even MAP materials maintain actual cost layers through the mandatory Material Ledger.

### Account Category Reference (OMSK)

**SPRO Path:** Materials Management ▸ Valuation and Account Assignment ▸ Account Determination ▸ Account Determination Without Wizard ▸ Define Valuation Classes
**T-code:** OMSK (overview), OMW0 (account determination — Phase 6 detail)
**What to configure:** Account category references group valuation classes. The valuation class (MBEW-BKLAS) assigned to a material determines which GL accounts are hit in OBYC for each movement type. Full OBYC walkthrough deferred to Phase 6.
