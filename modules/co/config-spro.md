---
module: co
content_type: config-spro
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — SPRO/IMG Configuration

> ECC 6.0 reference. Configuration organized by dependency sequence — complete each section before moving to the next. T-code shortcuts shown where available (faster than navigating IMG tree).

## Configuration Dependency Sequence

```
1. Controlling Area + Company Code Assignment (foundation — everything depends on this)
2. CO Versions
3. Cost Element Configuration (default assignments, automatic creation)
4. Cost Center Accounting (hierarchy, categories, number ranges, planning)
5. Internal Order Configuration (types, number ranges, settlement profiles, allocation structures)
6. Activity Type Configuration (categories, price indicators)
7. Allocation Cycle Configuration (assessment and distribution setup)
8. Product Costing Configuration (costing variants, costing types, transfer control)
9. Profit Center Accounting Configuration (activation, substitution, control parameters)
```

> CRITICAL: Step 1 (Controlling Area) MUST be complete before any other CO configuration. The controlling area defines the chart of accounts, fiscal year variant, and currency that all CO objects inherit.

---

## 1. Controlling Area and Company Code Assignment

### Step 1.1: Maintain Controlling Area
**T-code:** OKKP
**IMG Path:** Controlling → Organization → Maintain Controlling Area
**Settings:**
- Controlling area key (4 chars, e.g., 1000)
- Name
- Currency type and currency (controlling area currency for all CO reporting)
- Chart of accounts (must match assigned company codes)
- Fiscal year variant (must match assigned company codes)
- Assignment control: company code assignment (all CCs under this CA must share same CoA and FY variant)
- CCA: activate/deactivate cost center accounting components

Gotcha: CRITICAL — all company codes assigned to this controlling area MUST use the same chart of accounts and fiscal year variant. If they don't match, the assignment (OX19) will fail.

### Step 1.2: Assign Company Code to Controlling Area
**T-code:** OX19
**IMG Path:** Enterprise Structure → Assignment → Controlling → Assign company code to controlling area
**Settings:**
- Map each company code to its controlling area
- The system verifies chart of accounts and fiscal year variant consistency

### Step 1.3: Maintain CO Versions
**T-code:** OKEQ
**IMG Path:** Controlling → General Controlling → Organization → Maintain Versions
**Settings:**
- Version 0: plan/actual integration (the primary version — always used for actual postings)
- Additional versions (001, 002...): planning scenarios only
- Settings per version: plan/actual flag, exchange rate type, value type

Gotcha: Version 0 is mandatory and used by all actual postings. Additional versions are for plan data only. Do not attempt to post actuals to a non-zero version.

---

## 2. Cost Element Configuration

### Step 2.1: Default Account Assignment
**T-code:** OKB9
**IMG Path:** Controlling → Cost Element Accounting → Default Account Assignments
**Settings:**
- Maps GL accounts to default cost objects (cost center, internal order)
- When an FI posting hits a P&L GL account with a corresponding cost element, the system needs a CO receiver
- OKB9 provides the default cost center when the user does not manually enter one

Gotcha: If OKB9 is not maintained and the user does not enter a cost center on the FI posting, the posting fails with "Enter a CO account assignment." This is the most common CO error for new implementations.

### Step 2.2: Automatic Creation of Primary Cost Elements
**T-code:** OKB3 (or use KA01 with batch input / RKAKEP01)
**IMG Path:** Controlling → Cost Element Accounting → Automatic Creation of Primary Cost Elements
**Usage:** Automatically creates primary cost elements for GL accounts that don't have them. Useful during initial implementation or when a new chart of accounts range is added. Select GL account range and cost element category 1 (or appropriate category).

### Step 2.3: Cost Element Group Maintenance
**T-code:** KAH1 / KAH2 / KAH3
**IMG Path:** Controlling → Cost Element Accounting → Master Data → Cost Element Group
**Usage:** Group cost elements for reporting and planning. Similar to cost center groups.

---

## 3. Cost Center Accounting Configuration

### Step 3.1: Define Standard Hierarchy
**T-code:** OKEON
**IMG Path:** Controlling → Cost Center Accounting → Master Data → Cost Center → Define Standard Hierarchy
**Settings:**
- Define the top node of the cost center hierarchy
- Every cost center must belong to this hierarchy
- Structure: root → area nodes → department nodes → individual cost centers

### Step 3.2: Cost Center Categories
**T-code:** OKE5
**IMG Path:** Controlling → Cost Center Accounting → Master Data → Cost Center → Define Cost Center Categories
**Settings:**
- SAP standard categories: H (overhead), F (production), V (sales), E (R&D), A (admin), L (logistics)
- Controls which activity types and business transactions are allowed on the cost center
- Custom categories possible but rarely needed

### Step 3.3: Number Ranges for Cost Centers
**T-code:** OKEX
**IMG Path:** Controlling → Cost Center Accounting → Master Data → Cost Center → Define Number Ranges
**Settings:**
- Internal (system-assigned) or external (user-assigned) number ranges
- Define per controlling area

### Step 3.4: Planning Layouts
**T-code:** OKP1
**IMG Path:** Controlling → Cost Center Accounting → Planning → Manual Planning → Define Planning Layouts
**Settings:**
- Define which fields appear in cost center planning screens
- Row = cost elements (or cost element groups)
- Column = periods, plan/actual, versions
- Assign layouts to planning profiles (KSPI)

### Step 3.5: Planning Profiles
**T-code:** KSPI (create via SPRO or directly)
**IMG Path:** Controlling → Cost Center Accounting → Planning → Manual Planning → Define Planning Profiles
**Settings:**
- Combine planning layout + planner profile
- Assign to cost center type or user for streamlined planning sessions

---

## 4. Internal Order Configuration

### Step 4.1: Define Order Types
**T-code:** KOT2
**IMG Path:** Controlling → Internal Orders → Order Master Data → Define Order Types
**Settings:**
- Order type key (4 chars, e.g., 0100=overhead, 0200=investment, 0300=accrual)
- Number range assignment
- Settlement profile assignment (from OKO7) — CRITICAL: controls settlement behavior
- Planning profile assignment
- Budget profile assignment (if budgeting required)
- Status management profile
- Object class: overhead order vs investment order

Gotcha: The order type is the single most important internal order config element. It controls settlement behavior, budgeting, and planning. Get this wrong and you need to create new orders with the correct type.

### Step 4.2: Number Ranges for Internal Orders
**T-code:** OKOS (or KON1/KON2)
**IMG Path:** Controlling → Internal Orders → Order Master Data → Define Number Ranges
**Settings:**
- Separate ranges for different order types (overhead vs investment)
- Internal or external numbering

### Step 4.3: Settlement Profiles
**T-code:** OKO7
**IMG Path:** Controlling → Internal Orders → Actual Postings → Settlement → Maintain Settlement Profiles
**Settings:**
- Allowed receiver types: cost center (CTR), internal order (ORD), GL account (FXA for asset, KST for GL), WBS element (PSP), CO-PA segment (RKS)
- Default values for settlement: 100% to single receiver or split
- Settlement cost element (secondary CE, category 21 or 22)
- Allocation structure reference (from OKO6)
- Document type for settlement FI documents
- Validity: per order type assignment in KOT2

Gotcha: CRITICAL — if the settlement profile does not allow a receiver type, the user cannot define that receiver in the settlement rule. Plan receiver types carefully before go-live.

### Step 4.4: Allocation Structures
**T-code:** OKO6
**IMG Path:** Controlling → Internal Orders → Actual Postings → Settlement → Maintain Allocation Structures
**Settings:**
- Maps source cost elements to settlement cost elements
- Defines which cost elements from the order are settled and to which settlement CE
- Can settle all source CEs to one target CE, or map individually
- Referenced by settlement profile (OKO7)

---

## 5. Activity Type Configuration

### Step 5.1: Activity Type Categories
**T-code:** OKL1
**IMG Path:** Controlling → Cost Center Accounting → Master Data → Activity Type → Define Activity Type Categories
**Settings:**
- Category 1: manual entry, manual allocation (user posts activity quantities)
- Category 2: indirect determination, indirect allocation (system determines quantities)
- Category 3: manual entry, indirect allocation
- Category 4: indirect determination, manual allocation
- Most implementations use category 1 (manual/manual) for simplicity

### Step 5.2: Activity Price Planning
**T-code:** KP26 (change) / KP27 (display)
**IMG Path:** Via direct T-code (not typically configured in SPRO — uses CCA planning framework)
**Settings:**
- Plan activity rates per cost center per activity type per version per fiscal year
- Fixed price + variable price per activity unit
- The system uses: Total planned costs / planned activity quantity = planned activity price
- Or manually enter prices in KP26

Gotcha: If no activity price is planned (KP26) for an activity type used in allocations, the allocation posts at zero value. Always verify planned prices before period-end.

---

## 6. Allocation Cycle Configuration (Assessment and Distribution)

### Step 6.1: Assessment Cycles
**T-code:** KSU1 (create) / KSU2 (change) / KSU3 (display)
**IMG Path:** Controlling → Cost Center Accounting → Period-End Closing → Single Functions → Allocations → Assessment
**Settings per segment:**
- **Sender:** Cost center or cost center group
- **Sender values:** All costs, specific cost elements, or cost element groups
- **Receiver:** Cost centers, internal orders, WBS elements, or combinations
- **Allocation basis:** Fixed percentages, fixed amounts, statistical key figures (from KB31N), variable portions (receiver's own values)
- **Secondary cost element:** Category 42 CE used for assessment posting on receiver
- **Cycle settings:** Iterative (for circular allocations), non-iterative, test/live run control

> Assessment replaces original cost elements with the secondary CE (category 42) on the receiver. The sender's detailed cost breakdown is lost on the receiver side.

### Step 6.2: Distribution Cycles
**T-code:** KSV1 (create) / KSV2 (change) / KSV3 (display)
**IMG Path:** Controlling → Cost Center Accounting → Period-End Closing → Single Functions → Allocations → Distribution
**Settings:** Same segment structure as assessment (sender, receiver, basis) but:
- NO secondary cost element needed — original cost elements are preserved on the receiver
- Only PRIMARY cost elements can be distributed (secondary CEs must use assessment)

> Distribution preserves original cost elements on the receiver, providing full cost transparency. Choose distribution when management needs to see the source cost breakdown on the receiving object.

### Step 6.3: Statistical Key Figure Configuration
**T-code:** KK01 (create) / KB31N (enter values)
**IMG Path:** Controlling → Cost Center Accounting → Master Data → Statistical Key Figures
**Usage:** Define key figures used as allocation bases. Enter actual values per cost center per period via KB31N. Assessment/distribution cycles reference these values for allocation calculation.

---

## 7. Product Costing Configuration

### Step 7.1: Costing Variants
**T-code:** OKKN
**IMG Path:** Controlling → Product Cost Controlling → Product Cost Planning → Material Cost Estimate → Define Costing Variants
**Settings:**
- Costing variant = the central config element for product costing
- Combines: costing type (OKP0), valuation variant, date control, quantity structure control
- Costing type determines which BOM and routing to use
- Valuation variant determines which prices to use (standard price, planned price, current price)
- Date control determines which date drives BOM explosion and price lookup

### Step 7.2: Costing Types
**T-code:** OKP0 (or via OKKN)
**IMG Path:** Controlling → Product Cost Controlling → Product Cost Planning → Material Cost Estimate → Define Costing Types
**Settings:**
- Defines the purpose of the cost estimate (standard cost, current cost, modified standard cost)
- Controls which BOM usage and routing usage to apply
- Controls whether the estimate can update the material master price

### Step 7.3: Transfer Control
**T-code:** OK17
**IMG Path:** Controlling → Product Cost Controlling → Product Cost Planning → Material Cost Estimate → Define Transfer Control
**Settings:**
- Controls which value from the cost estimate updates the material master price (MBEW-STPRS or MBEW-VERPR)
- Maps costing variant + valuation variant + cost component to material master price field
- This is the link between CK24 (mark/release) and the actual standard price update

Gotcha: If transfer control is not configured correctly, CK24 release appears to succeed but the material master price is not updated. Always verify MBEW-STPRS via MM03 after release.

### Step 7.4: Overhead Costing Sheets
**T-code:** KZS2 (or via SPRO)
**IMG Path:** Controlling → Product Cost Controlling → Product Cost Planning → Basic Settings → Overhead → Define Costing Sheets
**Settings:**
- Costing sheets define overhead surcharges applied to cost estimates
- Structure: base (which costs to apply overhead to) → overhead rate (percentage or fixed) → credit key (which CC receives the credit)
- Used by CK11N during cost estimation and KGI2 during actual overhead calculation

---

## 8. Profit Center Accounting Configuration

### Step 8.1: Activate PCA Components
**T-code:** OKEQ (PCA tab within CO version maintenance)
**IMG Path:** Controlling → Profit Center Accounting → Basic Settings → Controlling Area Settings
**Settings:**
- Activate profit center accounting for the controlling area
- Set PCA as active for plan and/or actual data

### Step 8.2: Maintain PCA Substitution Rules
**T-code:** 1KEF
**IMG Path:** Controlling → Profit Center Accounting → Assignments of Account Assignment Objects to Profit Centers → Define Substitution
**Settings:**
- Rule-based automatic assignment of profit centers to FI postings
- Conditions: based on GL account, cost center, material, business area, etc.
- Action: substitute profit center field
- Ensures PCA ledger (GLPCA) captures all FI postings with a profit center

Gotcha: If substitution rules are incomplete and document splitting is not active, FI postings without a profit center will not appear in PCA reports — creating reconciliation gaps between FI and PCA.

### Step 8.3: Control Parameters for PCA Actual Postings
**T-code:** 3KE5
**IMG Path:** Controlling → Profit Center Accounting → Basic Settings → Controlling Area Settings → Control Parameters for Actual Postings
**Settings:**
- Control which postings are transferred to PCA
- Transaction-based or document-based transfer
- Settings for balance carry-forward and profit center currency

> **S/4HANA NOTE:** Sections 8.1-8.3 are largely eliminated in S/4HANA. PCA is integrated into the Universal Journal. No separate activation, substitution rules, or control parameters are needed for basic PCA functionality. Profit center is simply a field on the journal entry.
