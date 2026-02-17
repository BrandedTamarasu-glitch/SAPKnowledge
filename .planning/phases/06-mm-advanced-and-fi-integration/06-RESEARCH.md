---
module: mm
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: "2026-02-17"
phase: 06-mm-advanced-and-fi-integration
created: 2026-02-17
---

# Phase 6: MM Advanced & FI Integration - Research

**Researched:** 2026-02-17
**Domain:** SAP ECC 6.0 Materials Management — OBYC account determination, MM decision trees, troubleshooting, MM-FI integration
**Confidence:** MEDIUM-HIGH (existing KB provides strong foundation; web searches verified OBYC keys, movement types, and period-end processes)

---

## Summary

Phase 6 layers four content types onto the Phase 5 MM foundation: (1) a deep OBYC account determination walkthrough with dual-axis navigation and 10+ worked examples, (2) procurement and inventory decision trees following the FI Phase 4 pattern, (3) symptom-first troubleshooting with SAP message IDs, and (4) the first complete cross-module integration documentation (MM-FI) in the knowledge base.

The OBYC content builds directly on the foundation already established in `modules/fi/account-determination.md` (Phase 4), which covers the determination path, BSX/WRX/PRD/GBB keys, and three worked examples (movement types 101, 261, 551). Phase 6 expands this with the MM-side perspective: valuation class setup (OMSK), movement type configuration (OMJJ), the complete OBYC debugging path, and additional worked examples for subcontracting (541), consignment (411K), stock transfers (301), returns (122), split valuation, revaluation (MR21/MR22), and price changes.

The decision trees cover both procurement decisions (valuation approach, release strategy, source determination, vendor evaluation) and inventory decisions (split valuation, batch management, serial numbers, consignment, special stocks, MRP type selection, lot sizing, tolerance keys). These follow the FI Phase 4 format: question-driven flow leading to recommendation with comparison table.

The MM-FI integration documentation populates the existing `modules/mm/integration.md` placeholder with a comprehensive integration point catalog and transaction traces answering "what happens in FI when I post MIGO 101?"

**Primary recommendation:** Structure OBYC content as dual-axis (by movement type AND by transaction key) with explicit cross-references. Follow FI Phase 4 fi-advanced.md as the direct template for decision trees and troubleshooting format. The integration.md file should use transaction-trace format showing the complete accounting flow for each key MM-FI touchpoint.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### OBYC Walkthrough Depth
- Dual-axis structure: organized by both movement types AND transaction keys, with cross-references between them
- Extended 10+ worked examples with full debit/credit GL account entries (GR to stock 101, GR to consumption 201, GI to cost center, invoice with PRD variance, stock transfer 301, subcontracting 541, split valuation, consignment, returns, scrapping, revaluation, price changes)
- Include valuation class setup guidance: OMSK valuation class design, OMJJ account category reference, and how they feed into OBYC
- Include full OBYC debugging path: simulation and account determination trace for diagnosing missing GL assignments

#### Decision Tree Topics
- Cover both procurement AND inventory decision trees
- Procurement trees: valuation approach (standard vs MAP), release strategy design, source determination, vendor evaluation setup
- Inventory trees: split valuation, batch management, serial numbers, consignment, special stock types
- Include MRP decision guidance: MRP type selection (PD vs VB vs VV), lot sizing procedures, planning strategy (MTS vs MTO)
- Include tolerance key decision guidance: which tolerance keys (PP, PE, BD, AN, etc.) for which business scenarios with recommended values
- Follow FI Phase 4 format: question-driven flow leading to recommendation, with comparison tables where relevant

#### Troubleshooting Format
- Symptom-first lookup organization: entries organized by what user sees (error messages, blocked documents, wrong postings)
- Target 10-12 entries (broader than FI's 7 due to MM's wider scope: purchasing, inventory, invoice verification, MRP)
- Include actual SAP message IDs (M7, ME class numbers) so users can search by exact error
- Self-contained entries: full diagnosis + resolution inline, no jumping to other files (match FI Phase 4 pattern)
- Include diagnostic T-codes (MB51, MBPM, MR11, OMJJ check) in each entry's resolution path

#### MM-FI Integration Scope
- Integration point catalog listing all MM-FI touchpoints (GR, GI, IV, GR/IR clearing, period-end) plus detailed transaction traces for key transactions
- Populate existing modules/mm/integration.md (not a new file)
- Transaction-trace format for key scenarios: "When you post MIGO 101, here's exactly what happens in FI"
- Full GR/IR clearing coverage: account setup, F.13 automatic clearing, MR11 maintenance/revaluation, period-end GR/IR analysis
- MM period-end FI impacts: material ledger actual costing run (CKMLCP), balance sheet revaluation (MR21/MR22), MMPV period close, and their FI postings

### Claude's Discretion
- Exact number of decision trees per category (procurement vs inventory)
- Which specific SAP message IDs to include in troubleshooting
- Level of detail in transaction trace diagrams
- Whether to create an mm-advanced.md file (like fi-advanced.md) or split decision trees and troubleshooting differently

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

---

## Section 1: OBYC Account Determination -- Verified Facts for Expanded Coverage

### 1.1 Existing Foundation (from Phase 4)

The knowledge base already contains in `modules/fi/account-determination.md`:
- Full determination path: Movement type -> OMJJ -> OBYC (transaction key + valuation class + modifier) -> GL account
- Transaction keys: BSX, WRX, PRD, GBB (with modifiers VBR, VNG, VAX, VAY, AUF, BSA, INV, ZOB)
- Three worked examples: movement type 101 (GR, standard and MAP), 261 (GI to production), 551 (scrapping)
- VKOA framework overview (scoped to Phase 8 for deep-dive)
- FI-only automatic postings: F.05/OBA1, OBXU/OBXI, clearing account mechanics

Phase 6 does NOT duplicate this content. It adds the MM-side perspective and extended examples.

### 1.2 Additional Movement Type -> Transaction Key Mappings (Verified)

These are the additional worked examples required by CONTEXT.md decisions, beyond the three already in fi/account-determination.md:

**Movement Type 201 -- GI to Cost Center (Consumption)**
| Transaction Key | Dr/Cr | What It Posts | Modifier |
|----------------|-------|---------------|----------|
| GBB | Dr | Consumption expense (cost center) | VBR |
| BSX | Cr | Inventory / stock account | None |

Same keys as 261 (GI to production order) but the account assignment object is a cost center instead of a production order. GBB/VBR is the correct modifier for both.

Confidence: HIGH (consistent with existing KB and Phase 4 research)

**Movement Type 301 -- Plant-to-Plant Stock Transfer (One Step)**
| Transaction Key | Dr/Cr | What It Posts | Modifier |
|----------------|-------|---------------|----------|
| BSX | Dr | Inventory at receiving plant | None |
| BSX | Cr | Inventory at issuing plant | None |

Two BSX postings -- one at each plant's valuation area. If the two plants are in the same company code, a single FI document is created. If in different company codes, intercompany postings are generated. No GBB modifier needed because there is no consumption -- stock simply moves between plants.

For two-step transfers (303/305): Movement type 303 issues from source plant (BSX Cr + GBB Dr with stock-in-transit account), and 305 receives at destination plant (BSX Dr + GBB Cr clearing the transit account).

Confidence: MEDIUM-HIGH (training data verified against SAP Community discussions)

**Movement Type 541 -- Transfer to Subcontractor**
| Transaction Key | Dr/Cr | What It Posts | Modifier |
|----------------|-------|---------------|----------|
| No FI posting | -- | Stock reclassification only | -- |

Movement type 541 transfers stock from unrestricted to subcontracting stock (special stock O) at the same plant. This is a stock type change, NOT a valuation event. No accounting entries are generated at 541. The actual consumption posts when the finished goods are received back from the subcontractor via movement type 543 (automatic GI of components), which triggers GBB/VBO (consumption from vendor-managed/subcontracting stock) and BSX.

The subcontracting GR (movement type 101 against subcontracting PO) creates the standard BSX/WRX entries for the finished goods, and the simultaneous 543 consumes the components.

Confidence: MEDIUM (SAP Community source confirms no FI posting at 541; consumption at 543 triggers VBO)

**Movement Type 411K -- Consignment Withdrawal (Transfer to Own Stock)**
| Transaction Key | Dr/Cr | What It Posts | Modifier |
|----------------|-------|---------------|----------|
| BSX | Dr | Inventory (own stock) | None |
| KON | Cr | Consignment payables (vendor liability) | Has modifier |

When consignment stock (special stock K) is withdrawn into own stock, BSX debits inventory and KON creates a liability to the consignment vendor. KON is one of the three OBYC keys (with GBB and PRD) that supports account modifiers.

If the material has standard price (S) and the consignment price differs from standard price, transaction key AKO (expense/revenue from consignment) fires for the price difference.

Movement type 412K reverses the 411K posting (return from own stock to consignment).

Confidence: MEDIUM (SAP Community confirmed BSX + KON for consignment withdrawal)

**Movement Type 122 -- Return to Vendor**
| Transaction Key | Dr/Cr | What It Posts | Modifier |
|----------------|-------|---------------|----------|
| BSX | Cr | Inventory (reduces stock) | None |
| WRX | Dr | GR/IR clearing (reverses the original GR clearing) | None |
| PRD | Dr or Cr | Price difference (if S-price material) | Optional |

Movement type 122 mirrors 101 with opposite signs -- it is functionally equivalent to a GR reversal (102) but specifically designated as a return to vendor. The same OBYC transaction keys fire (BSX, WRX, PRD) with reversed debit/credit.

Important configuration note: When GR-Based Invoice Verification (LFM1-WEBRE) is active and the PO has already been invoiced, movement type 122 is blocked by default. Transaction OMBZ controls whether 122 is allowed despite existing invoices.

Confidence: MEDIUM (SAP Community confirmed; OMBZ configuration for returns with invoices verified)

**Split Valuation -- BSX with Different Valuation Types**

When split valuation is active for a material:
- The material has a valuation header and multiple valuation types (e.g., "Domestic" and "Imported")
- Each valuation type can have its own valuation class in MBEW
- OBYC determines the GL account based on the valuation class of the specific valuation type
- BSX can therefore post to different GL accounts for the same material depending on which valuation type is being received or issued

Configuration chain: OMWC (valuation category + valuation types) -> OMSK (account category reference per valuation type) -> OBYC (GL account per valuation class)

Confidence: MEDIUM (SAP Community confirmed split valuation uses valuation class per type in OBYC)

**MR21/MR22 -- Price Change / Revaluation**
| Transaction Key | Dr/Cr | What It Posts | Modifier |
|----------------|-------|---------------|----------|
| BSX | Dr or Cr | Stock account (value adjustment) | None |
| UMB | Cr or Dr | Revaluation account (offsetting entry) | Optional |

MR21 changes the standard price or MAP of a material. MR22 debits or credits a material's value without changing the price. Both use transaction key UMB for the offsetting entry to the revaluation/price change GL account.

UMB supports account modifiers via "reasons for price change" -- different reasons can route to different GL accounts. Configuration: OBYC -> UMB -> valuation class + optional modifier -> GL account.

Confidence: MEDIUM (SAP Note 2494660 and SAP Blog confirm UMB key and reason-based modifiers)

### 1.3 Valuation Class Setup Chain (OMSK / OMJJ / OBYC)

The complete configuration chain for MM account determination:

```
1. OMWM -- Set valuation level (plant or company code)
           CRITICAL: Cannot change after materials are valued
           Standard: Valuation area = Plant

2. OMSK -- Define Account Category References
           Groups valuation classes into categories
           Assigned to material types (controls which val classes are allowed)

3. Material Type -> Account Category Reference -> Valuation Classes
           e.g., Material type ROH -> Acct Cat Ref 0001 -> Val classes 3000, 3010

4. OMJJ -- Movement Type Configuration
           Defines which transaction keys fire per movement type
           Read-only during normal operations; do not modify standard mvt types

5. OMWN -- Value String Assignment
           Maps movement types to value strings (grouping of transaction keys)
           Intermediary between OMJJ and OBYC

6. OBYC -- Account Determination
           Transaction key + Valuation class [+ Account modifier] -> GL account
           This is the final step that resolves to specific GL accounts
```

Key design principle: The valuation class in the material master (MBEW-BKLAS) is the primary driver. Two materials with different valuation classes will post to different GL accounts for the same movement type. This is how SAP separates raw materials from finished goods from spare parts in the GL.

### 1.4 OBYC Debugging Path (Verified)

When a goods movement fails with "account determination error" or posts to an unexpected GL account, the diagnostic path is:

**Step 1: Identify the transaction key**
- Read the error message -- it usually names the transaction key (e.g., "Account not defined for BSX")
- Or use OMJJ/OMWN to look up which keys fire for the movement type in question

**Step 2: Check OBYC configuration**
- T-code OBYC -> Enter the transaction key -> Check if an entry exists for:
  - Your chart of accounts
  - Your valuation grouping code (if multi-CC setup, see OMWD)
  - Your valuation class (from material master MBEW-BKLAS)
  - Your account modifier (for GBB, PRD, KON only)

**Step 3: Simulation via OMWB**
- T-code OMWB -> Enter material number -> Simulation -> Go to Report
- Shows which GL accounts would be determined for each transaction key
- Use before posting to verify the determination will succeed

**Step 4: Runtime trace via SE37**
- Debug function module MR_ACCOUNT_ASSIGNMENT
- Set breakpoint to see each OBYC lookup step
- Shows the exact selection criteria and result for each transaction key

**Step 5: SQL trace via ST05**
- Activate SQL trace before posting in MIGO
- Shows all table accesses against T030 (OBYC configuration table)
- Useful for identifying which table access failed

Confidence: MEDIUM (OMWB simulation confirmed by SAP Community; SE37/ST05 debugging approaches are standard SAP techniques)

---

## Section 2: MM Decision Trees -- Research Findings

### 2.1 Valuation Approach (Standard Price S vs Moving Average Price V)

**Key decision factors verified:**

| Factor | Standard Price (S) | Moving Average Price (V) |
|--------|-------------------|------------------------|
| Price variance visibility | PRD account shows all variances explicitly | Variances absorbed into stock value (BSX) |
| Price stability | Price fixed until cost estimate released | Price fluctuates with each receipt |
| Typical use | Manufactured goods, materials with stable costs | Traded goods, commodities, volatile-price materials |
| Production variance analysis | Required for standard costing in CO-PC | Not suitable for standard costing |
| Material Ledger interaction | ML can calculate actual cost alongside standard | ML tracks actual cost layers |
| Complexity | Higher (requires cost estimate maintenance via CK11N/CK24) | Lower (automatic) |

Confidence: HIGH (well-established SAP standard knowledge, consistent with existing KB content)

### 2.2 Release Strategy Design

**Configuration objects:**
- Release group (SPRO: MM -> Purchasing -> Purchase Order -> Release Procedure)
- Release code (approval code, assigned to users)
- Release indicator (status of the document -- released/not released)
- Release strategy (combination of release codes with sequence and prerequisites)
- Classification: characteristics (total value, material group, plant, purchasing group) drive which strategy applies

**Decision guidance for the tree:**
- Q1: How many approval levels? (1 = simple, 2-3 = standard, 4+ = complex)
- Q2: Are approval thresholds value-based, org-based, or both?
- Q3: Do PRs and POs need separate release strategies?

Confidence: MEDIUM (SAP Community blog on release strategy design confirmed; exact SPRO paths verified)

### 2.3 MRP Type Selection (PD vs VB vs VV)

**Verified decision criteria:**

| MRP Type | Full Name | Drives By | Best For |
|----------|-----------|-----------|----------|
| PD | MRP (deterministic) | Demand (sales orders, PIR, BOM explosion) | A-class materials, manufactured goods, materials with known demand |
| VB | Manual Reorder Point | Stock level vs reorder point | B/C-class materials, consumables, stable consumption |
| VV | Forecast-Based | Historical consumption forecast | Materials with predictable consumption patterns |
| VM | Automatic Reorder Point | System-calculated reorder point | Materials where system can reliably calculate safety stock |
| ND | No MRP | None -- excluded from planning | Non-stock materials, services |

**Important note on VV:** SAP has placed VV in "compatibility scope" for S/4HANA (supported until Dec 2025/2030 depending on version). For ECC 6.0 content this is still fully functional, but worth flagging as a future migration consideration.

Confidence: HIGH (SAP Community and SAP Learning confirmed; VV deprecation path verified)

### 2.4 Lot Sizing Procedures

**Key lot sizing options for decision tree:**

| Procedure | Code | Description | When to Use |
|-----------|------|-------------|-------------|
| Lot-for-lot | EX | Order exactly what's needed | Expensive materials, make-to-order |
| Fixed lot size | FX | Always order fixed quantity | Materials with setup cost constraints |
| Weekly lot size | WB | Consolidate weekly requirements | Medium-value materials with weekly delivery |
| Monthly lot size | MB | Consolidate monthly requirements | Low-value materials with monthly ordering |
| Period lot size | PB | Consolidate by configurable period | Flexible period consolidation |
| Optimum lot size | OP | Cost-optimized (carrying cost vs ordering cost) | When cost parameters are maintained |

Confidence: HIGH (standard SAP MRP lot sizing; consistent with material master MRP 1 view field MARC-DISLS)

### 2.5 Split Valuation Decision

**When split valuation is needed:**
- Same material number with different origins requiring different prices (domestic vs imported)
- Same material with different quality grades requiring separate valuation
- Production vs purchased stock valued differently
- Batch-specific valuation requirements

**Configuration path:** OMWC (valuation category + types) -> OMSK (account category reference per type) -> material master (activate split valuation indicator)

**Key trade-offs:**
- Adds complexity to goods movements (must specify valuation type)
- Each valuation type can have its own price control (S or V)
- Separate stock quantities and values per type
- More OBYC entries needed (one per valuation class per type)

Confidence: MEDIUM (SAP Community and SAP Help confirmed; OMWC configuration path verified)

### 2.6 Tolerance Key Decision Guidance

**Recommended tolerance keys by business scenario:**

| Scenario | Key Tolerance Keys | Recommended Values |
|----------|-------------------|-------------------|
| Standard procurement | BD (auto-post small diff), PP (price), DQ (quantity) | BD: $5-10 absolute; PP: 2-5%; DQ: 5-10% |
| High-value procurement | PP, DQ, AN, AP | Tighter: PP 1-2%; DQ 2-5% |
| Service procurement | AN (no order ref), PP | AN: higher absolute; PP: wider % |
| Consignment/VMI | VP (MAP variance), PP | VP: 5-10% to absorb price fluctuations |
| Blanket POs | LA (blanket amount), LD (time limit), PS (estimated price) | LA/LD per business policy |

The CONTEXT.md mentions "PE" as a tolerance key -- this is not a standard SAP tolerance key. The 15 standard keys are: AN, AP, BD, BR, BW, DQ, DW, KW, LA, LD, PC, PP, PS, ST, VP. The planner should use PP (price variance) where the user may have intended PE.

Confidence: HIGH (all 15 tolerance keys verified in Phase 5 research and existing config-spro.md)

---

## Section 3: Troubleshooting -- SAP Message IDs and Diagnostic Patterns

### 3.1 Message Class Reference

Key SAP message classes for MM troubleshooting:

| Class | Area | Description |
|-------|------|-------------|
| M7 | Inventory Management | Goods movements, physical inventory |
| M8 | Invoice Verification / Valuation | MIRO, LIV, tolerances |
| ME | Purchasing | POs, PRs, contracts |
| M3 | Material Master | Master data maintenance |
| F5 | FI Document Posting | Account determination failures |

### 3.2 Recommended Troubleshooting Entries (10-12 Target)

Based on research, here are the highest-value troubleshooting entries organized by symptom category:

**Purchasing (2-3 entries):**
1. **PO cannot be saved / "Account determination error"** -- Missing OBYC configuration for the valuation class + transaction key combination. Diagnostic: Check OMWB simulation; verify material master MBEW-BKLAS.
   - Message: F5 class errors or "Account not defined for transaction key BSX/GBB/WRX"

2. **ME59N fails to convert PR to PO** -- No valid source determination. Diagnostic: Check ME03 (source list), ME13 (info record), OMGM (source list requirement).
   - No specific error class -- ME59N simply skips items without valid sources

3. **PO release strategy not triggering / wrong approver** -- Classification mismatch between PO characteristics and release strategy conditions. Diagnostic: Check release strategy in ME28/ME29N; verify characteristic values match strategy conditions.

**Inventory Management (3-4 entries):**
4. **M7 021 "Deficit of GR quantity"** -- Attempting GR reversal (102) or return (122) when insufficient stock exists, or when invoice already posted for the PO and GR-based IV is active. Diagnostic: Check MB51 for stock movements; check OMBZ if returns with invoices are needed.

5. **M7 090 "Accounting data not yet maintained for material"** -- Material master Accounting 1 view not extended to the posting plant. Diagnostic: Check MM03 Accounting 1 view; extend via MM01 if needed.

6. **Wrong GL account on goods movement** -- OBYC configuration has incorrect valuation class mapping. Diagnostic: OMWB simulation, check MBEW-BKLAS, verify OBYC entry for the transaction key.

7. **Posting period not open for materials (M7 053)** -- MMPV has not opened the current period, or OB52 account type M is closed. Diagnostic: Check OMSY (MM period), OB52 (FI posting periods for type M).

**Invoice Verification (3-4 entries):**
8. **MIRO invoice blocked (M8 tolerance messages)** -- Tolerance exceeded. M8 082 = price too high; M8 084 = price too low; M8 504 = quantity too high. Diagnostic: Check OMR6 tolerance limits; check MRBR for blocking reason; verify PO terms in ME23N and GR quantities in MB51.

9. **MIRO "No GR exists" despite goods receipt posted** -- GR-Based Invoice Verification (WEBRE) active but GR posted to wrong PO line or movement type. Diagnostic: Check EKBE (PO history) for the GR; verify LFM1-WEBRE; check that MIGO used correct PO number.

10. **GR/IR account balance growing / never clears** -- GR/IR clearing account not set as open-item managed in FS00, or F.13 not running. Diagnostic: Check FS00 OI indicator; run F.13 in test mode; use MR11 for one-sided items.

11. **MIRO price variance posting to wrong account** -- PRD account misconfigured in OBYC for the material's valuation class. Diagnostic: Check MBEW-VPRSV (must be S for PRD to fire); check OBYC PRD entry.

**MRP (1-2 entries):**
12. **MRP not generating planned orders / PRs** -- MRP type ND (no planning) set in material master, or procurement type mismatch. Diagnostic: Check MARC-DISMM (MRP type), MARC-BESKZ (procurement type), MARC-DISPO (MRP controller); verify MD04 shows requirements.

Confidence: MEDIUM (message IDs M7 021, M7 090, M8 082/084/504 verified via SAP Datasheet and SAP Community; resolution paths are standard diagnostic procedures)

### 3.3 Key Diagnostic T-Codes for Resolution Paths

| T-Code | Purpose | Use In Troubleshooting |
|--------|---------|----------------------|
| MB51 | Material document list | Trace all movements for a material/plant |
| OMWB | Account determination simulation | Verify GL account before posting |
| OMJJ | Movement type config display | Check which OBYC keys fire for a movement type |
| OBYC | Account determination config | Verify GL account assignments |
| OMR6 | Tolerance limits | Check tolerance configuration |
| MRBR | Release blocked invoices | Identify blocking reason |
| MR11 | GR/IR account maintenance | Clear one-sided GR/IR items |
| EKBE | PO history | Verify GR and IR postings against a PO |
| OMSY | MM period display | Check current MM posting period |
| OMCQ | Message configuration | Change M7 message severity (warning vs error) |

---

## Section 4: MM-FI Integration Points -- Verified Facts

### 4.1 Integration Point Catalog

Every MM transaction that creates an FI document:

| MM Transaction | Movement Type(s) | FI Document Created | OBYC Keys | Key Tables Updated |
|---------------|------------------|--------------------|-----------|--------------------|
| MIGO (GR against PO) | 101 | Yes -- BSX Dr, WRX Cr, PRD Dr (S-price) | BSX, WRX, PRD | MKPF, MSEG, EKBE, BSEG, BKPF |
| MIGO (GR reversal) | 102 | Yes -- reverse of 101 | BSX, WRX, PRD | Same as 101 |
| MIGO (GI to cost center) | 201 | Yes -- GBB/VBR Dr, BSX Cr | GBB, BSX | MKPF, MSEG, BSEG, BKPF |
| MIGO (GI to production) | 261 | Yes -- GBB/VBR Dr, BSX Cr | GBB, BSX | MKPF, MSEG, BSEG, BKPF |
| MIGO (scrapping) | 551 | Yes -- GBB/VNG Dr, BSX Cr | GBB, BSX | MKPF, MSEG, BSEG, BKPF |
| MIGO (plant transfer) | 301 | Yes -- BSX Dr (recv), BSX Cr (issue) | BSX | MKPF, MSEG, BSEG, BKPF |
| MIGO (return to vendor) | 122 | Yes -- reverse of 101 pattern | BSX, WRX, PRD | MKPF, MSEG, EKBE, BSEG, BKPF |
| MIGO (initial stock load) | 561 | Yes -- BSX Dr, GBB/BSA Cr | BSX, GBB | MKPF, MSEG, BSEG, BKPF |
| MIGO (consignment withdrawal) | 411K | Yes -- BSX Dr, KON Cr | BSX, KON | MKPF, MSEG, BSEG, BKPF |
| MIGO (GI for delivery) | 601 | Yes -- GBB/VAX Dr, BSX Cr | GBB, BSX | MKPF, MSEG, LIPS, BSEG, BKPF |
| MIRO (invoice) | -- | Yes -- WRX Dr, Vendor Cr | -- | RSEG, EKBE, BSEG, BKPF |
| MIRO (credit memo) | -- | Yes -- Vendor Dr, WRX Cr | -- | RSEG, EKBE, BSEG, BKPF |
| MI07 (inventory diff) | 701/702 | Yes -- BSX / INV account | BSX, GBB/INV | MKPF, MSEG, BSEG, BKPF |
| MR21 (price change) | -- | Yes -- BSX Dr/Cr, UMB Cr/Dr | BSX, UMB | CKMI1, BSEG, BKPF |
| MR22 (debit/credit) | -- | Yes -- BSX Dr/Cr, UMB Cr/Dr | BSX, UMB | CKMI1, BSEG, BKPF |
| MR11 (GR/IR maint) | -- | Yes -- WRX offset entry | -- | BSEG, BKPF |
| SLoc transfer | 311 | No FI posting | -- | MKPF, MSEG only |

### 4.2 Transaction Trace: "What happens in FI when I post MIGO 101?"

This is the specific success criterion from the phase description. The trace format:

**Trigger:** User posts MIGO with Action = Goods Receipt, Reference = Purchase Order, Movement Type = 101

**Step 1: Material Document Creation**
- System creates MKPF header (material doc number, posting date, movement type)
- System creates MSEG line items (material, plant, storage location, quantity, amount)
- PO history updated in EKBE (GR record linked to PO line)

**Step 2: Account Determination (OBYC)**
- System reads MBEW-BKLAS (valuation class) for the material at this plant
- System reads MBEW-VPRSV (price control: S or V)
- For each transaction key triggered by movement type 101:
  - BSX: Chart of accounts + valuation class -> inventory GL account
  - WRX: Chart of accounts + valuation class -> GR/IR clearing GL account
  - PRD (only if S-price and PO price differs from standard): Chart of accounts + valuation class -> price difference GL account

**Step 3: FI Document Creation**
- System creates BKPF header (FI doc number, same posting date as material doc)
- System creates BSEG line items:
  - Line 1: BSX -> Dr inventory GL account (at standard price for S, at PO price for V)
  - Line 2: WRX -> Cr GR/IR clearing GL account (at PO price -- always)
  - Line 3 (if applicable): PRD -> Dr or Cr price difference (PO price minus standard price)
- Document balances: Dr total = Cr total

**Step 4: Open Item on GR/IR Account**
- The WRX posting creates an open item on the GR/IR clearing account
- This open item persists until MIRO posts the vendor invoice
- F.13 automatic clearing matches the GR posting against the MIRO posting

**Step 5: CO Posting (if account-assigned PO)**
- If the PO has account assignment (K = cost center, F = order, P = project), the GBB posting also creates a CO document
- Cost center or order receives the actual cost posting

### 4.3 GR/IR Clearing -- Complete Coverage

**Account Setup:**
- GR/IR clearing account (e.g., 191100) must be:
  - Flagged as "Open Item Managed" (OI indicator) in FS00 -- CRITICAL
  - Flagged as "Line Item Display" in FS00
  - These flags MUST be set BEFORE any postings; changing after postings requires clearing all items first
- OBYC WRX must point to this account for each relevant valuation class

**Clearing Sequence (period-end):**

1. **F.13 Automatic Clearing** -- runs first
   - Matches GR and IR postings on the GR/IR account by assignment field (typically PO number + PO line)
   - Clears matched pairs automatically
   - Items that match in both quantity and amount are cleared
   - Run in test mode first; review results before live execution

2. **MR11 GR/IR Account Maintenance** -- handles residuals
   - For items where GR was posted but invoice never arrived (or vice versa)
   - MR11 writes off the one-sided balance to a configured offset account
   - Best practice: Only use MR11 when you are certain no more invoices or GRs will arrive
   - MR11 posts accounting documents that clear the hanging items

3. **MR11SHOW** -- review past MR11 postings for audit

**Common problems:**
- OI indicator missing -> F.13 cannot clear -> balance grows (already documented in fi-advanced.md Pitfall 7)
- MR11 used too aggressively -> legitimate open items written off prematurely
- F.13 criteria mismatch -> items not matched despite matching amounts (check F.13 clearing criteria configuration in OB74)

Confidence: HIGH (SAP Note 2050268 on MR11/F.13 process confirmed; consistent with existing KB)

### 4.4 MM Period-End FI Impacts

**MMPV -- MM Period Close**
- T-code: MMPV (program RMMMPERI)
- What it does: Opens the new MM period and automatically closes the previous period
- FI impact: Controls which MM posting period is allowed for goods movements. The FI posting date on MM-generated FI documents is NOT controlled by MMPV -- it uses the FI posting period from OB52. This disconnect is a common source of confusion.
- Configuration: OMSY stores the current MM period per company code (table MARV)
- MMRV allows posting to a previously closed MM period (emergency override)

**CKMLCP -- Material Ledger Actual Costing Run (if ML is active)**
- T-code: CKMLCP
- What it does: Calculates actual costs for the period, determines price differences, and distributes variances between inventory and COGS
- FI impact: Creates FI documents that redistribute variance:
  - Portion consumed (e.g., COGS) -> posted to P&L accounts
  - Portion remaining in inventory -> adjusts BS inventory accounts
- OBYC transaction keys: Uses specific ML-related keys for the revaluation postings
- Sequence: CKMLCP runs AFTER all goods movements and invoices for the period are posted, and AFTER the new period is opened (because the "post closing" step reverses entries with a posting date in the new period)
- ECC 6.0 note: Material Ledger is optional in ECC 6. Only relevant if ML is activated for the plant.

**MR21/MR22 -- Balance Sheet Revaluation**
- MR21: Changes the material price (standard price or MAP)
- MR22: Debits or credits the material value without changing the price
- FI impact: Creates FI documents using BSX (stock adjustment) and UMB (revaluation account)
- Period-end use: MR21 used to release a new standard price from a cost estimate; MR22 used for manual value adjustments

Confidence: MEDIUM (CKMLCP FI posting mechanics confirmed via SAP Blog and SAP Community; MMPV/OB52 disconnect verified)

---

## Section 5: File Structure Decisions (Claude's Discretion)

### 5.1 Recommendation: Create mm-advanced.md (Parallel to fi-advanced.md)

**Recommendation:** YES, create `modules/mm/mm-advanced.md` to hold decision trees and troubleshooting, paralleling the FI module structure.

**Rationale:**
- Maintains structural consistency with FI module (fi-advanced.md exists with same content types)
- Keeps integration.md focused on cross-module integration points (not decision trees)
- The MM CLAUDE.md file index already references integration.md and patterns.md; adding mm-advanced.md is a natural extension
- Decision trees and troubleshooting are module-internal concerns, not integration topics

**File allocation:**
| Content | File | Rationale |
|---------|------|-----------|
| OBYC walkthrough (dual-axis, worked examples, debugging) | modules/mm/mm-advanced.md (Section 1) | Account determination is MM-internal config; the fi/account-determination.md already has the FI-side framework -- mm-advanced adds the MM perspective |
| Decision trees (procurement + inventory) | modules/mm/mm-advanced.md (Section 2) | Parallel to fi-advanced.md decision trees |
| Troubleshooting (symptom-first, 10-12 entries) | modules/mm/mm-advanced.md (Section 3) | Parallel to fi-advanced.md troubleshooting |
| MM-FI integration point catalog + transaction traces | modules/mm/integration.md | This IS integration -- belongs in the integration file |
| GR/IR clearing complete coverage | modules/mm/integration.md | GR/IR clearing is fundamentally an MM-FI integration topic |
| Period-end FI impacts | modules/mm/integration.md | Period-end activities are MM-FI boundary processes |

### 5.2 Recommended Decision Tree Count

**Procurement decision trees (5):**
1. Valuation approach: Standard Price (S) vs Moving Average Price (V)
2. Release strategy design: approval levels, thresholds, org structure
3. Source determination: source list vs info record vs outline agreement
4. Vendor evaluation setup: when to activate, which criteria
5. Tolerance key selection: which keys for which business scenarios

**Inventory decision trees (5):**
6. Split valuation: when needed, configuration implications
7. Batch management: when to activate, per-plant vs per-material-type
8. Serial number management: profile selection, when to track
9. Consignment and special stock: vendor consignment, subcontracting, pipeline
10. MRP type selection: PD vs VB vs VV vs ND

**MRP decision trees (2):**
11. Lot sizing procedure: EX vs FX vs WB vs MB vs optimum
12. Planning strategy: MTS (strategy 10/40) vs MTO (strategy 20/50)

**Total: 12 decision trees** (significantly more than FI's 7, reflecting MM's broader scope). This can be trimmed to 10 by combining serial numbers into batch management and combining lot sizing into MRP type selection.

### 5.3 Recommended Troubleshooting Count

12 entries as detailed in Section 3.2, covering all four MM submodules (purchasing, inventory, invoice verification, MRP).

---

## Section 6: Existing Content Dependencies and Cross-References

### 6.1 Content Already in Knowledge Base That Phase 6 Builds On

| File | What It Contains | How Phase 6 Uses It |
|------|-----------------|---------------------|
| fi/account-determination.md | OBYC framework, BSX/WRX/PRD/GBB keys, 3 worked examples, VKOA overview | Phase 6 REFERENCES this (does not duplicate); adds MM-side perspective and additional examples |
| fi/fi-advanced.md | 7 decision trees + 7 troubleshooting entries | Phase 6 FOLLOWS this format exactly for mm-advanced.md |
| mm/config-spro.md | OMJJ, OMR6, OMWM, OMSK basics | Phase 6 EXPANDS the OMSK and OMJJ sections with deeper account determination detail |
| mm/processes.md | P2P process with FI posting notes at GR and MIRO | Phase 6 integration.md provides the DETAILED traces that processes.md references |
| mm/master-data.md | MBEW-BKLAS, MBEW-VPRSV, LFM1-WEBRE | Phase 6 REFERENCES these fields in OBYC context |
| fi/fi-advanced.md Pitfall 7 | GR/IR account OI indicator requirement | Phase 6 BUILDS ON this in the GR/IR clearing section |

### 6.2 Prior Decisions That Constrain Phase 6

From Phase 4 (04-01):
- Cash discount config = OBXU/OBXI (NOT OBB8) -- referenced in OBYC context
- PRD fires for movement type 101 on S-price materials only; MAP absorbs into BSX -- must be consistent
- GR/IR clearing account OI indicator = required for F.13 -- built into integration.md GR/IR section
- Troubleshooting entries are self-contained (no jumping to other files)

From Phase 4 (04-02):
- Decision trees include config implications inline, not just pointers to config-spro.md

---

## Common Pitfalls for Content Authors

### Pitfall 1: Duplicating fi/account-determination.md Content
**What goes wrong:** Writing the OBYC framework explanation again in mm-advanced.md
**Prevention:** mm-advanced.md should reference fi/account-determination.md for the framework and focus on the MM-specific perspective: valuation class setup, additional worked examples, and the debugging path

### Pitfall 2: Confusing Movement Type 541 as Having FI Postings
**What goes wrong:** Writing that 541 (transfer to subcontractor) creates an FI document
**Correct fact:** 541 is a stock type reclassification only -- no FI posting. The FI posting happens at GR (101 for finished goods) when movement type 543 simultaneously consumes components (GBB/VBO)

### Pitfall 3: Missing the MMPV/OB52 Disconnect
**What goes wrong:** Saying MMPV controls FI posting periods for MM documents
**Correct fact:** MMPV controls the MM period (which goods movement period is allowed). The FI posting date on MM-generated FI documents is controlled by OB52 (FI posting periods, account type M). These are separate controls.

### Pitfall 4: Treating KON as a Simple Credit Posting
**What goes wrong:** Documenting consignment withdrawal as just "BSX Dr, KON Cr" without noting AKO for price differences
**Correct fact:** For S-price materials with consignment price different from standard, AKO (expense/revenue from consignment) also fires. KON also supports account modifiers.

### Pitfall 5: Using Nonexistent Tolerance Key "PE"
**What goes wrong:** Including PE as a tolerance key in the decision tree
**Correct fact:** There is no standard SAP tolerance key "PE." The 15 keys are: AN, AP, BD, BR, BW, DQ, DW, KW, LA, LD, PC, PP, PS, ST, VP. Use PP (price variance) where PE was intended.

### Pitfall 6: Ignoring the CKMLCP New Period Requirement
**What goes wrong:** Running CKMLCP before opening the new MM/FI period
**Correct fact:** CKMLCP "post closing" step creates reversal entries with a posting date in the new period. Both the new MM period (MMPV) and FI period (OB52) must be open before CKMLCP can complete.

---

## Open Questions

1. **Exact OBYC transaction keys for CKMLCP revaluation postings**
   - What we know: CKMLCP redistributes variance between inventory and COGS accounts via FI documents
   - What's unclear: The specific OBYC transaction keys used by ML for the closing entries (LKW, PKD, etc. are ML-specific keys not fully documented in the existing KB)
   - Recommendation: Document the CKMLCP process flow and FI impact at a conceptual level; note that ML-specific OBYC keys exist but detailed ML configuration is beyond Phase 6 scope (ECC 6 ML is optional)

2. **OMWB simulation availability across all ECC 6 enhancement packs**
   - What we know: OMWB simulation is referenced in SAP Community as a standard diagnostic tool
   - What's unclear: Whether OMWB simulation is available in base ECC 6.0 or requires a specific EhP
   - Recommendation: Document it as a diagnostic approach; note that SE37 debugging of MR_ACCOUNT_ASSIGNMENT is the universal fallback

3. **Vendor evaluation setup depth**
   - What we know: Vendor evaluation uses ME61/ME62/ME63 with automatic scoring based on delivery, price, quality, and service criteria
   - What's unclear: How deep to go in the decision tree -- vendor evaluation is a standalone feature that could justify its own content section
   - Recommendation: Keep the decision tree at the "when to activate and which criteria" level; detailed vendor evaluation config can be deferred to Phase 12 (solution patterns)

4. **Number of OBYC worked examples vs file length**
   - What we know: CONTEXT.md specifies 10+ examples
   - What's unclear: Whether all 10+ examples should be full Dr/Cr tables or whether some can be abbreviated (e.g., reversals)
   - Recommendation: Full Dr/Cr table for the 7 primary scenarios (101, 201, 301, 411K, 541/543, 122, MR21); abbreviated "same keys, opposite signs" treatment for reversal movements (102, 262, 412K)

---

## Sources

### Primary (HIGH confidence -- existing knowledge base, verified in prior phases)
- modules/fi/account-determination.md -- OBYC framework, BSX/WRX/PRD/GBB keys, worked examples
- modules/fi/fi-advanced.md -- decision tree and troubleshooting format template
- modules/mm/config-spro.md -- OMJJ, OMR6, OMWM, OMSK configuration
- modules/mm/processes.md -- P2P process with FI posting notes
- modules/mm/master-data.md -- MBEW-BKLAS, MBEW-VPRSV field locations
- .planning/phases/04-fi-advanced-and-integration-prep/04-RESEARCH.md -- Phase 4 OBYC research

### Secondary (MEDIUM confidence -- SAP Community, multiple sources agree)
- [SAP Community: OBYC GBB Transaction Keys](https://community.sap.com/t5/enterprise-resource-planning-q-a/obyc-gbb-transaction-keys/qaq-p/4495190) -- GBB modifier list including VBO for subcontracting
- [SAP Community: Movement Type 541](https://community.sap.com/t5/enterprise-resource-planning-q-a/movement-type-541/qaq-p/3002369) -- No FI posting at 541; consumption at 543
- [SAP Community: Account Determination for Consignment](https://answers.sap.com/questions/6072103/account-determination-for-consignment.html) -- KON and AKO keys for consignment
- [SAP Community: MRP Type PD vs VB](https://community.sap.com/t5/enterprise-resource-planning-q-a/difference-between-mrp-type-pd-and-vb/qaq-p/5055842) -- MRP type selection criteria
- [SAP Blog: Price Change Reasons MR21/MR22](https://blogs.sap.com/2015/01/10/price-change-reasons-with-different-account-determination-mr21mr22/) -- UMB transaction key with reason-based modifiers
- [SAP Note 2494660](https://userapps.support.sap.com/sap/support/knowledge/en/2494660) -- MR22/MR21 UMB and PRD reasons
- [SAP Community: OMWB Simulation](https://community.sap.com/t5/enterprise-resource-planning-q-a/omwb-simulation/qaq-p/6647231) -- OMWB as diagnostic tool
- [SAP Blog: Account Determination Debugging](https://blogs.sap.com/2014/04/28/account-determination-why-was-this-account-determined/) -- SE37 MR_ACCOUNT_ASSIGNMENT debugging
- [SAP Note 2050268](https://userapps.support.sap.com/sap/support/knowledge/en/2050268) -- MR11/F.13 GR/IR clearing process
- [SAP Community: M8 Messages for Invoices with Tolerances](https://blogs.sap.com/2014/01/07/m8-messages-for-incoming-invoices-with-tolerances/) -- M8 082, M8 084, M8 504 message IDs
- [SAP Datasheet: M7 Message Class](https://www.sapdatasheet.org/abap/msag/m7.html) -- M7 021, M7 090 message IDs
- [SAP Community: MMPV Period Close](https://community.sap.com/t5/enterprise-resource-planning-q-a/mmpv-material-management-period-closing/qaq-p/695582) -- MMPV/OB52 relationship
- [SAPinsider: MM and FI Period Close Disconnect](https://sapinsider.org/avoid-a-disconnect-between-your-mm-and-fi-period-closes/) -- MMPV vs OB52 independence
- [SAP Blog: Material Ledger Actual Costing](https://blogs.sap.com/2018/01/07/material-ledgers-actual-costing/) -- CKMLCP process and FI posting

### Tertiary (LOW confidence -- training data only, not independently verified)
- Exact CKMLCP OBYC transaction keys for ML revaluation entries (LKW, PKD, etc.)
- OMWB simulation availability across ECC 6.0 enhancement packs
- Movement type 161 (return delivery) as alternative to 122 for invoiced POs -- referenced but not fully verified

---

## Metadata

**Confidence breakdown:**
- OBYC worked examples (101, 201, 261, 551): HIGH -- existing KB verified
- OBYC worked examples (301, 541, 411K, 122, MR21): MEDIUM -- SAP Community verified
- Split valuation account determination: MEDIUM -- concept confirmed, detailed config paths need validation
- Decision tree topics: HIGH for valuation/MRP; MEDIUM for release strategy/vendor evaluation
- Troubleshooting message IDs: MEDIUM -- M7/M8 class IDs verified via SAP Datasheet
- MM-FI integration points: HIGH -- consistent with existing KB and Phase 4 research
- GR/IR clearing process: HIGH -- SAP Note 2050268 confirmed
- Period-end FI impacts: MEDIUM -- CKMLCP mechanics confirmed at conceptual level

**Research date:** 2026-02-17
**Valid until:** Stable -- ECC 6.0 MM account determination and integration patterns do not change. Review only if knowledge base scope extends to Material Ledger deep-dive.
