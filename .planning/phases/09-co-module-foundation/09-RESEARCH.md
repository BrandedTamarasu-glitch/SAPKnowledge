# Phase 9: CO Module Foundation - Research

**Researched:** 2026-02-17
**Domain:** SAP ECC 6.0 Controlling (CO) module content authoring
**Confidence:** HIGH

## Summary

Phase 9 delivers complete CO reference content following the same structural patterns established in Phases 3 (FI), 5 (MM), and 7 (SD). The CO module is the fourth and final module foundation. All four deliverables (tcodes.md, master-data.md, config-spro.md, processes.md) follow locked formats from prior phases. The CLAUDE.md index already exists with the correct file structure and needs only a "Read When" update in Plan 04.

CO is organizationally centered on the Controlling Area (KOKRS), which spans one or more company codes. The module covers six major subareas: Cost Element Accounting (CO-OM-CEL), Cost Center Accounting (CO-OM-CCA), Internal Orders (CO-OM-OPA), Activity-Based Costing / Activity Types (CO-OM-ABC), Profit Center Accounting (EC-PCA), and Product Costing (CO-PC). Period-end processing -- allocation cycles (assessment/distribution), settlement, activity price calculation, and product cost runs -- is the most complex area and the central process flow.

CO has a unique characteristic compared to FI/MM/SD: it is heavily period-end oriented. While FI has daily postings and MM has transactional goods movements, CO's value-add comes primarily from period-end allocations, settlements, and cost analysis. The T-code count (50-80) is achievable but the distribution is skewed: CCA and Internal Orders have the most transactions; CO-PC has fewer but more complex ones; PCA in ECC 6 has a separate set of T-codes (KE5x series) that become obsolete in S/4HANA.

**Primary recommendation:** Author all four content files following FI/MM/SD patterns exactly. Organize T-codes and config by CO subarea (CCA, PCA, Internal Orders, CO-PC, Period-End), not by alphabetical grouping. Prioritize period-end processes (allocation cycles, settlement, product costing run) as the primary process flows since they are where consultants spend 80% of their CO time.

## Standard Stack

This phase produces markdown reference content, not software. The "stack" is the established content patterns from prior phases.

### Core Patterns (from Phases 3, 5, and 7)

| Pattern | Source | Purpose | Applies To |
|---------|--------|---------|------------|
| Frontmatter + workflow index + submodule sections | FI/MM/SD tcodes.md | T-code reference structure | CO tcodes.md |
| Single master-data.md with table-per-segment format | FI/MM/SD master-data.md | Master data reference | CO master-data.md |
| Narrative-plus-table with role annotations | FI/MM/SD processes.md | Business process flows | CO processes.md |
| SPRO step-by-step with IMG path + T-code | FI/MM/SD config-spro.md | Configuration reference | CO config-spro.md |
| CORRECTION note blocks | FI/MM master-data.md | Flag commonly-wrong field locations | CO master-data.md |
| S/4HANA callout at section header | All modules | Disambiguation without contamination | CO files (especially cost elements, PCA) |

### Validation Constraints

| Constraint | Source | Value |
|-----------|--------|-------|
| Token budget (tcodes) | validate.py | 5000 tokens (~20,000 chars) |
| Token budget (config-spro) | validate.py | 5000 tokens (~20,000 chars) |
| Token budget (processes) | validate.py | 4000 tokens (~16,000 chars) |
| Token budget (master-data) | validate.py | 4000 tokens (~16,000 chars) |
| Required frontmatter fields | validate.py | module, content_type, ecc_version, ehp_range, confidence, last_verified |
| Valid module value | validate.py | "co" |
| S/4HANA contamination check | validate.py | ACDOCA, Universal Journal = CRITICAL (allowed only in S/4HANA callout sections) |

**Token budget note:** CO config-spro.md may be large (controlling area setup, cost element categories, cost center hierarchies, allocation cycle config, settlement profiles, product costing config) but should be manageable within 5000 tokens since CO SPRO is more compact than SD's condition technique breadth.

## Architecture Patterns

### Recommended File Structure (CO Module)

All files already exist as stubs in `modules/co/`. Phase 9 populates four of them:

```
modules/co/
├── CLAUDE.md           # Already populated -- update File Index "Read When" guidance (Plan 04)
├── tcodes.md           # Phase 9: CO-01
├── master-data.md      # Phase 9: CO-02 (resequenced -- see note)
├── config-spro.md      # Phase 9: CO-03
├── processes.md        # Phase 9: CO-04
├── integration.md      # Phase 10 (deferred)
└── patterns.md         # Phase 12 (deferred)
```

### CO Subarea Organization

Use these subareas as the primary organizational axis in all four files:

| Subarea | SAP Component | Scope | T-code Prefix |
|---------|---------------|-------|---------------|
| Cost Element Accounting | CO-OM-CEL | Primary/secondary cost element master data | KA0x |
| Cost Center Accounting | CO-OM-CCA | Cost center master, planning, reporting, allocations | KS0x, KP0x, S_ALR_870xx |
| Internal Orders | CO-OM-OPA | Internal order master, budgeting, settlement | KO0x |
| Activity-Based Costing | CO-OM-ABC | Activity types, activity prices, activity allocation | KL0x, KP26/27 |
| Profit Center Accounting | EC-PCA | Profit center master, reporting, planning | KE5x |
| Product Costing | CO-PC | Cost estimates, costing runs, material cost analysis | CK11N, CK24, CK40N, KKBC_HOD |
| Period-End Closing | CO-OM (cross) | Assessment/distribution cycles, settlement, reposting | KSU5, KSV5, KO88, KB61 |
| CO Reporting | CO (cross) | Line item reports, plan/actual comparisons | KSB1, KOB1, S_ALR reports |

### Plan Sequence Recommendation

| Plan | Content | Rationale |
|------|---------|-----------|
| 09-01 | tcodes.md | T-code reference first (establishes the vocabulary) |
| 09-02 | master-data.md | Master data second (tables/fields needed for config and process context) |
| 09-03 | config-spro.md | Config third (references master data objects defined in 09-02) |
| 09-04 | processes.md + CLAUDE.md update | Processes last (ties T-codes + config + master data into business flows) |

This matches the established 4-plan structure from prior phases.

## CO T-Code Reference (50-80 Target)

### Recommended T-Code Distribution

| Subarea | Estimated Count | Key T-codes |
|---------|----------------|-------------|
| Cost Elements | 4-6 | KA01/02/03 (primary), KA06 (secondary), KA23 (cost element report) |
| Cost Center Accounting | 12-16 | KS01/02/03 (master), KSH1/2/3 (hierarchy), KP06/26 (planning), KSBT (CC group), S_ALR_87013611 (plan/actual) |
| Internal Orders | 10-14 | KO01/02/03/04 (master), KO12 (change master list), KOK2 (collective order), KO88 (settlement), KOB1 (line items), KOH1/2 (order group) |
| Activity Types | 4-6 | KL01/02/03 (master), KP26/27 (activity price planning), KPHR (price report) |
| Profit Center Accounting | 6-8 | KE51/52/53 (master), KCH1/2/3 (hierarchy), KE5Z (plan/actual), 1KE5 (profit center group) |
| Product Costing | 6-10 | CK11N (create estimate), CK24 (mark/release), CK40N (costing run), KKBC_HOD (cost object report), CK13N (display), CKM3 (material price analysis) |
| Period-End / Allocations | 8-12 | KSU5 (assessment cycle run), KSV5 (distribution cycle run), KSU1-3 (assessment create/change/display), KSV1-3 (distribution), KB61 (reposting), KO88 (settlement), KOAC (settlement-cost centers), KGI2 (actual overhead calculation) |
| Reporting | 6-8 | KSB1 (CC actual line items), KOB1 (order line items), S_ALR_87013611 (CC plan/actual), S_ALR_87013015 (IC orders actual), KSBL (CC summarization), KE5Z (PC plan/actual) |

**Total estimated: 56-80 T-codes.** Target the middle range (60-70) for coverage depth without padding.

### Key T-codes Requiring Detailed Documentation

These deserve full treatment (menu path, usage context, gotchas) comparable to FB50, MIGO, and VA01 in prior modules:

- **KS01** -- Cost center creation (the CC master record)
- **KO01** -- Internal order creation (the IO master record)
- **CK11N** -- Create cost estimate (the central product costing transaction)
- **CK24** -- Mark and release cost estimate (updates standard price in MBEW)
- **KSU5/KSV5** -- Run assessment/distribution cycles (period-end workhorses)
- **KO88** -- Order settlement (moves costs from orders to receivers)
- **KP06** -- Cost center planning (plan data entry)

## CO Master Data Reference

### Core Master Data Objects

| Object | Primary Table | Text Table | Create T-code | Key Fields |
|--------|--------------|------------|---------------|------------|
| Cost Element (Primary) | CSKA | CSKB shares structure, CSKU for texts | KA01 | KSTAR (cost element), KOKRS (CA), KAINT (category) |
| Cost Element (Secondary) | CSKA | CSKU | KA06 | KSTAR, KOKRS, KAINT (categories 21-43) |
| Cost Center | CSKS | CSKT | KS01 | KOSTL, KOKRS, BUKRS, KOSAR (category), DATBI/DATAB (validity) |
| Internal Order | AUFK | AUFT for texts (custom) | KO01 | AUFNR (order number), AUART (order type), KOKRS, BUKRS |
| Activity Type | CSLA | CSLT | KL01 | LSTAR (activity type), KOKRS, DATBI/DATAB |
| Profit Center | CEPC | CEPCT | KE51 | PRCTR, KOKRS, DATBI/DATAB, SEGMENT |
| Statistical Key Figure | -- (T685B/SKF tables) | -- | KK01 | STAGR (stat key figure), KOKRS |

### Cost Element Categories (CRITICAL)

Cost element categories define the behavior of cost elements. This is the most commonly confused CO concept.

**Primary cost elements** (categories 1, 3, 4, 11, 12, 22):
- Must have a corresponding GL account in FI with the same number
- Created via KA01; the GL account must exist first in FS00
- Category 1 = primary costs/revenue (most common)
- Category 11 = revenue
- Category 12 = sales deduction
- Category 3 = accrual/deferral (FI posts to different account than CO)
- Category 4 = accrual/deferral (CO posts to different account than FI)
- Category 22 = external settlement

**Secondary cost elements** (categories 21, 31, 41, 42, 43):
- NO corresponding GL account -- exist only in CO
- Created via KA06
- Category 21 = internal settlement
- Category 31 = order/project results analysis
- Category 41 = overhead rates (for overhead calculation)
- Category 42 = assessment
- Category 43 = internal activity allocation

**CORRECTION note candidate:** Many consultants confuse the cost element number with the GL account number. In ECC 6, primary cost elements MUST match a GL account number, but they are separate master data objects (CSKA vs SKA1/SKB1). The cost element is created AFTER the GL account. Secondary cost elements have NO GL account counterpart.

> **S/4HANA CRITICAL difference:** In S/4HANA, cost elements are no longer separate master data. GL accounts automatically serve as cost elements. KA01/KA06 are obsolete. The cost element category is maintained directly on the GL account master (FS00). This is one of the biggest S/4HANA changes affecting CO.

### Key CO Master Data Tables

| Table | Content | Key | Important Fields |
|-------|---------|-----|-----------------|
| CSKA | Cost element master (chart of accounts) | KTOPL + KSTAR | KAINT (category), KATYP (cost element type) |
| CSKB | Cost element master (controlling area) | KOKRS + KSTAR + DATBI | KATYP, BUKRS |
| CSKS | Cost center master | KOKRS + KOSTL + DATBI | KOSAR (category), BUKRS, VERAK (responsible), PRCTR (profit center) |
| CSKT | Cost center texts | KOKRS + KOSTL + DATBI + SPRAS | KTEXT, LTEXT |
| AUFK | Internal order master | AUFNR | AUART (type), KOKRS, BUKRS, KSTAR (settlement CE), PRCTR |
| CSLA | Activity type master | KOKRS + LSTAR + DATBI | LEINH (activity unit), TARKZ (price indicator) |
| CSLT | Activity type texts | KOKRS + LSTAR + DATBI + SPRAS | KTEXT, LTEXT |
| CEPC | Profit center master | KOKRS + PRCTR + DATBI | BUKRS, SEGMENT, VERAK |
| CEPCT | Profit center texts | KOKRS + PRCTR + DATBI + SPRAS | KTEXT, LTEXT |
| TKA01 | Controlling area master | KOKRS | KTOPL, KOINH (currency), BEZEI |
| COSS | CO totals (secondary) | KOKRS + LEDNR + OBJNR + GJAHR + ... | WRTTP (value type), WKG/WOG amounts |
| COSP | CO totals (primary) | KOKRS + LEDNR + OBJNR + GJAHR + ... | WRTTP, WKG/WOG amounts |
| COBK | CO document header | KOKRS + BESSION + BELNR | AWTYP (reference doc type) |
| COEP | CO document line items | KOKRS + BELNR + BUZESSION | OBJNR, KSTAR, WKG001-016 |

### Relationship Map

```
Controlling Area (TKA01)
├── Cost Elements (CSKA/CSKB)
│   ├── Primary (cat 1,3,4,11,12,22) ── maps 1:1 to GL account (SKA1)
│   └── Secondary (cat 21,31,41,42,43) ── CO-only, no GL
├── Cost Center Hierarchy (SETNODE/SETHEADER)
│   └── Cost Centers (CSKS) ── receives costs, performs allocations
│       └── Activity Types (CSLA) ── output measurement unit
├── Internal Orders (AUFK) ── collects costs for settlement
│   └── Settlement Rule (COBRB) ── defines receivers
├── Profit Center Hierarchy (SETNODE/SETHEADER)
│   └── Profit Centers (CEPC) ── internal P&L reporting unit
└── Operating Concern (TKA01-ERKRS) ── CO-PA link (Phase 10)
```

## CO SPRO Configuration Reference

### Critical IMG Paths by Subarea

#### Controlling Area Setup (Foundation)
1. **OKKP** -- Maintain Controlling Area (the central config transaction)
   - IMG: Controlling > Organization > Maintain Controlling Area
   - Sets: CA key, name, currency, chart of accounts, fiscal year variant, assignment control (1:1 or 1:many CC)
2. **OX19** -- Assign Company Code to Controlling Area
   - IMG: Enterprise Structure > Assignment > Controlling > Assign company code to controlling area
3. **OKEQ** -- Maintain CO Versions
   - IMG: Controlling > General Controlling > Organization > Maintain Versions
   - Version 0 = plan/actual integration; version 000 = plan only

#### Cost Element Configuration
4. **OKB9** -- Default account assignment (cost center for GL postings)
   - IMG: Controlling > Cost Element Accounting > Default Account Assignments
   - Maps GL accounts to default cost centers for automatic CO posting
5. **OKA2** -- Maintain cost element categories
   - Not typically customized; SAP-delivered categories suffice
6. **OKEON / KSH1** -- Maintain cost center standard hierarchy
   - IMG: Controlling > Cost Center Accounting > Master Data > Cost Center > Define Standard Hierarchy

#### Cost Center Configuration
7. **OKE5** -- Cost center categories
   - IMG: Controlling > Cost Center Accounting > Master Data > Cost Center > Define Cost Center Categories
8. **OKEX** -- Number ranges for cost centers
9. **OKP1** -- Cost center planning layouts
   - IMG: Controlling > Cost Center Accounting > Planning > Manual Planning > Define Planning Layouts
10. **KSPI** -- Create planning profiles (combines layout + planner profile)

#### Internal Order Configuration
11. **KOT2** -- Define order types
    - IMG: Controlling > Internal Orders > Order Master Data > Define Order Types
    - Controls number ranges, settlement profiles, planning profiles, budgeting profiles
12. **OKOS** -- Number ranges for internal orders
13. **OKO7** -- Settlement profiles
    - IMG: Controlling > Internal Orders > Actual Postings > Settlement > Maintain Settlement Profiles
    - Defines: allowed receivers, settlement cost element, distribution rule, residual handling
14. **OKO6** -- Allocation structures (for settlement)
    - IMG: Controlling > Internal Orders > Actual Postings > Settlement > Maintain Allocation Structures
    - Maps source cost elements to settlement cost elements

#### Activity Type / Activity-Based Costing
15. **OKL1** -- Activity type categories
16. **KP26/KP27** -- Activity price planning (primary/secondary)
    - Plan activity rates: fixed + variable per activity type per cost center

#### Assessment / Distribution Cycles
17. **KSU1/KSU2/KSU3** -- Create/change/display assessment cycles
    - Sender: cost center(s) or cost center group
    - Receiver: cost centers, internal orders, WBS elements
    - Allocation basis: fixed percentages, fixed amounts, statistical key figures, variable portions
18. **KSV1/KSV2/KSV3** -- Create/change/display distribution cycles
    - Same structure as assessment but uses ORIGINAL cost elements (preserves cost transparency)
    - Assessment uses a SECONDARY cost element (category 42) -- loses original cost element identity

#### Product Costing Configuration
19. **OKKN** -- Costing variants
    - IMG: Controlling > Product Cost Controlling > Product Cost Planning > Material Cost Estimate > Define Costing Variants
    - Combines: costing type, valuation variant, date control, quantity structure control
20. **OKP0** -- Costing types
21. **OK17** -- Transfer control (which value from cost estimate updates material master price)

#### Profit Center Accounting Configuration
22. **OKEQ** -- Activate PCA components
    - IMG: Controlling > Profit Center Accounting > Basic Settings > Controlling Area Settings
23. **1KEF** -- Maintain PCA substitution rules (auto-assign profit center)
24. **3KE5** -- Set control parameters for PCA actual postings

### Config Organization Recommendation

Organize config-spro.md by the following sections in this order:
1. Controlling Area and Company Code Assignment (foundation)
2. Cost Element Configuration
3. Cost Center Accounting Configuration (hierarchy, categories, planning)
4. Internal Order Configuration (types, settlement, allocation structures)
5. Activity Type Configuration
6. Allocation Cycle Configuration (assessment and distribution)
7. Product Costing Configuration (costing variants, costing runs)
8. Profit Center Accounting Configuration

This follows the natural config dependency sequence: CA first, then cost elements (needed by everything), then the objects that use them.

## CO Business Processes

### Key Business Processes to Document

| Process | Priority | Complexity | Key T-codes |
|---------|----------|------------|-------------|
| Period-End Cost Allocation (Assessment/Distribution) | HIGH | HIGH | KSU5, KSV5, KSU1-3, KSV1-3 |
| Internal Order Settlement | HIGH | HIGH | KO88, KO02 (settlement rule), OKO7 |
| Product Costing Run | HIGH | HIGH | CK11N, CK24, CK40N |
| Cost Center Planning | MEDIUM | MEDIUM | KP06, KP26, KSPI |
| Activity Price Calculation | MEDIUM | HIGH | KSPI, KP26, KSII |
| Period-End CO Closing | HIGH | MEDIUM | CO88, COGI, KSU5/KSV5, KO88 (sequence) |

### Process 1: Period-End Cost Allocation (Assessment/Distribution)

**Narrative structure:**
1. Review actual costs posted to sender cost centers (KSB1)
2. Verify allocation cycle configuration (KSU2/KSV2 -- check segments and rules)
3. Run allocation cycle in test mode (KSU5/KSV5 with test flag)
4. Review test results
5. Run allocation cycle in live mode
6. Verify results on receiver objects (KSB1, KOB1)

**Roles:** CO Accountant, CO Manager

**Critical distinction:** Assessment (KSU5) uses a secondary cost element (category 42) -- the original cost element is lost. Distribution (KSV5) preserves original cost elements on the receiver. Most implementations use assessment for simplicity; distribution for cost transparency.

### Process 2: Internal Order Settlement

**Narrative structure:**
1. Verify actual costs on the order (KOB1)
2. Check/maintain settlement rule on the order (KO02 -> Settlement Rule)
3. Run settlement in test mode (KO88 with test flag)
4. Review test results (settlement document preview)
5. Execute settlement live
6. Verify receiver objects received the settled amounts
7. Set technical completion on the order if done (KO02 status TECO)

**Settlement receivers:** GL account (FI), cost center, another internal order, asset under construction (AUC), profitability segment (CO-PA), WBS element (PS)

### Process 3: Product Costing Run

**Narrative structure:**
1. Create cost estimate (CK11N) or run costing run (CK40N)
2. Review cost estimate results
3. Mark the cost estimate (CK24 -- marks as future standard price)
4. Release the cost estimate (CK24 -- updates MBEW-STPRS, the standard price)
5. Verify material master standard price updated (MM03 Accounting 1)

**Key concept:** CK11N creates a single material cost estimate. CK40N runs a mass costing. CK24 has TWO steps: mark (sets future price) and release (activates the price). Between mark and release, the new price is visible but not yet operative.

### Process 4: Period-End CO Closing Sequence

This is the recommended sequence for CO period-end closing:

| Step | Activity | T-code | Dependencies |
|------|----------|--------|-------------|
| 1 | Repost CO line items (if needed) | KB61 | Before allocations |
| 2 | Calculate actual overhead rates | KGI2 | Before settlement |
| 3 | Run assessment cycles | KSU5 | After overhead calc |
| 4 | Run distribution cycles | KSV5 | After overhead calc |
| 5 | Settle internal orders | KO88 | After allocations |
| 6 | Settle production orders (if PP active) | CO88 | After allocations |
| 7 | Calculate WIP/results analysis (if PP active) | KKAX/KKA2 | Before settlement |
| 8 | Run profit center transfer pricing (if active) | 1KEG | After settlements |
| 9 | Lock CO period | OKP1 or via COPI | After all postings |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cost element category descriptions | Custom text | SAP standard categories (1,3,4,11,12,21,31,41,42,43,22) | Categories are fixed SAP logic; custom descriptions confuse users |
| Assessment vs distribution comparison | Freeform text | Structured comparison table with Dr/Cr examples | This is the #1 CO confusion point; needs precise worked examples |
| Settlement receiver types | Ad-hoc list | SAP settlement profile receiver type table (from OKO7) | Settlement profiles define allowed receivers; document what the system enforces |

## Common Pitfalls

### Pitfall 1: Cost Element Not Created Before GL Account Assignment

**What goes wrong:** A GL account is created in FS00 for a cost/revenue account but no corresponding cost element exists. FI postings to this account do not flow to CO. CO reports show incomplete costs.
**Why it happens:** Cost elements are separate master data from GL accounts in ECC 6. Creating a GL account does not auto-create the cost element.
**How to avoid:** After creating any P&L GL account in FS00, immediately create the primary cost element in KA01. Batch creation via KA01 or program RKAKEP01.
**Warning signs:** CO reports show lower totals than FI reports for the same period.

### Pitfall 2: Assessment vs Distribution Confusion

**What goes wrong:** Implementation uses assessment when the business needs cost element transparency on the receiver, or uses distribution when the business wants a single "overhead allocated" cost element.
**Why it happens:** Assessment (KSU5) replaces original cost elements with a single secondary cost element (category 42). Distribution (KSV5) preserves original cost elements. The names alone don't convey this critical difference.
**How to avoid:** Document the requirement explicitly: "Do we need to see the original cost element on the receiver?" If yes, use distribution. If no, use assessment.
**Warning signs:** Receiver cost center reports show unexpected cost elements.

### Pitfall 3: Settlement Rule Missing or Incomplete

**What goes wrong:** KO88 settlement fails with "No settlement rule exists" or settles to wrong receiver.
**Why it happens:** Settlement rules must be maintained individually on each internal order. New orders may not have the settlement rule populated, especially if the order type's settlement profile doesn't enforce mandatory rules.
**How to avoid:** Configure the settlement profile (OKO7) to require a settlement rule at order creation. Verify rules exist before running period-end settlement.
**Warning signs:** KO88 test run shows orders with errors or no settlement.

### Pitfall 4: CK24 Mark Without Release (Standard Price Not Updated)

**What goes wrong:** Cost estimate is created (CK11N) and marked (CK24 mark) but never released. The material master standard price (MBEW-STPRS) is not updated. Inventory valuation remains at the old price.
**Why it happens:** CK24 has two separate steps: mark and release. Mark sets the "future price" visible in the material master Costing view. Release actually updates MBEW-STPRS (the operative standard price). Many users forget the release step.
**How to avoid:** Always run CK24 with both mark AND release. Verify MBEW-STPRS via MM03 Accounting 1 after release.
**Warning signs:** Costing view shows a "future price" different from the standard price in Accounting 1.

### Pitfall 5: Controlling Area / Company Code Assignment Mismatch

**What goes wrong:** CO postings fail because the controlling area is not assigned to the company code, or CCs under the CA have different charts of accounts or fiscal year variants.
**Why it happens:** All company codes assigned to a controlling area MUST share the same chart of accounts and fiscal year variant. This is enforced at assignment time (OX19/OKKP) but can cause confusion in multi-CC environments.
**How to avoid:** Verify chart of accounts and fiscal year variant consistency before assigning CCs to CA.
**Warning signs:** Error messages at posting time referencing controlling area or company code mismatch.

### Pitfall 6: PCA Separate Ledger Not Reconciled (ECC 6 Specific)

**What goes wrong:** Profit center accounting reports (KE5Z) don't match FI reports because the PCA separate ledger (EC-PCA, tables GLPCA/GLPCT) is out of sync.
**Why it happens:** In ECC 6, PCA maintains a separate ledger. If postings are made in FI without a profit center assignment, PCA has gaps. Also, if adjustment postings are made in PCA but not reflected in FI.
**How to avoid:** Ensure all FI postings carry a profit center (via substitution rules 1KEF or document splitting). Run periodic reconciliation between FI and PCA.
**Warning signs:** KE5Z totals differ from FAGLB03 totals for the same accounts.

> **S/4HANA note:** This pitfall is eliminated in S/4HANA where PCA is integrated into the Universal Journal (ACDOCA). No separate PCA ledger, no reconciliation needed.

## Code Examples

Not applicable -- this phase produces SAP reference content in markdown format, not code.

## State of the Art

| Old Approach (ECC 6) | Current Approach (S/4HANA) | Impact on This Phase |
|----------------------|---------------------------|---------------------|
| Separate cost element master data (KA01/KA06, CSKA/CSKB) | GL accounts serve as cost elements; cost element category on GL master | Document ECC 6 approach; S/4HANA callout as major difference |
| PCA separate ledger (EC-PCA, GLPCA/GLPCT) | Universal Journal (ACDOCA), PCA integrated | Document ECC 6 PCA T-codes (KE5x); note S/4 deprecation |
| CO-PA costing-based and account-based (COPA tables) | Margin analysis replaces costing-based CO-PA | Mention briefly; Phase 10 territory |
| Material Ledger optional (CKMLCP) | Material Ledger mandatory | Note in product costing section |
| KE51/52/53 for profit center master | Same T-codes but data in ACDOCA | Document ECC 6 behavior |
| Separate CO document tables (COBK/COEP) | CO data in ACDOCA | Document ECC 6 tables |

**Key S/4HANA callouts for CO files:**
1. **Cost elements:** KA01/KA06 obsolete; cost element category maintained on GL account master (FS00). This is the single biggest S/4 change for CO.
2. **PCA:** Separate PCA ledger eliminated; PCA integrated in Universal Journal. KE5x T-codes still work but data is in ACDOCA, not GLPCA.
3. **Material Ledger:** Mandatory in S/4HANA (optional in ECC 6). Actual costing always available.
4. **CO-PA:** Costing-based CO-PA replaced by margin analysis. Account-based remains.
5. **Controlling Area:** 1:1 with company code strongly recommended (cross-CC controlling still technically possible but discouraged).

## Open Questions

1. **co-advanced.md existence**
   - The file `modules/co/co-advanced.md` was referenced in the CLAUDE.md but does not exist on disk. Prior modules have `{module}-advanced.md` (fi-advanced.md, mm-advanced.md, sd-advanced.md) created in their "Advanced" phases (4, 6, 8). co-advanced.md is Phase 10 territory.
   - Recommendation: Ignore for Phase 9. Phase 10 (CO Advanced) will create co-advanced.md with decision trees, troubleshooting, and deep CO-PA/ML content.

2. **CO-PA scope boundary**
   - CO-PA (Profitability Analysis) is a major CO subarea. Phase 9 should mention it in T-codes (KE21N for actual posting, KE24 for settlement to CO-PA) but NOT attempt deep CO-PA coverage.
   - Recommendation: Include 2-4 basic CO-PA T-codes in tcodes.md with a note "Deep CO-PA coverage in Phase 10." Do not include CO-PA config in config-spro.md.

3. **Exact T-code count per subarea**
   - The distribution above totals 56-80. The actual count depends on how many reporting T-codes to include and whether to document S_ALR report variants individually.
   - Recommendation: Target 60-65 T-codes. Include key S_ALR reports but do not exhaustively list all CO report variants.

## Sources

### Primary (HIGH confidence)
- Existing knowledge base files: FI tcodes.md, FI master-data.md, FI config-spro.md, FI processes.md (format patterns)
- Existing knowledge base files: MM and SD equivalent files (format patterns)
- Existing knowledge base: reference/org-structure.md (controlling area, cost center, profit center definitions)
- Existing knowledge base: modules/co/CLAUDE.md (file structure and stubs)

### Secondary (MEDIUM confidence)
- SAP ECC 6.0 CO module structure from training data (CO subareas, T-codes, table names, SPRO paths)
- Cost element categories and their behavior are well-established SAP standard

### Tertiary (LOW confidence)
- Exact S_ALR report numbers for CO -- should be verified during authoring
- Some SPRO IMG path strings -- should be verified for exact wording during authoring

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- follows established 4-plan pattern from 3 prior modules
- Architecture: HIGH -- CO subarea organization is well-defined SAP standard
- T-code distribution: MEDIUM -- exact counts depend on authoring decisions (Claude's discretion)
- Master data tables: HIGH -- CSKS, AUFK, CSKA, CEPC, CSLA are verified standard SAP tables
- Config SPRO paths: MEDIUM -- IMG path strings should be verified during authoring; T-code shortcuts are reliable
- Pitfalls: HIGH -- these are well-known CO implementation issues
- S/4HANA differences: HIGH -- cost element integration and PCA integration are widely documented

**Research date:** 2026-02-17
**Valid until:** 2026-03-17 (stable domain -- SAP ECC 6.0 is not changing)
