---
module: co
content_type: tcodes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — Transaction Codes

> ECC 6.0 reference. T-codes listed work in both ECC 6.0 and S/4HANA via SAP GUI unless noted otherwise. Key S/4 differences: cost elements KA01/KA06 obsolete (GL accounts serve as cost elements); PCA separate ledger eliminated (data in ACDOCA); Material Ledger mandatory.

## Workflow Index

| Process Stage | T-code(s) | Subarea | Notes |
|---|---|---|---|
| Create primary cost element | KA01 | Cost Elements | Must match GL account number |
| Create secondary cost element | KA06 | Cost Elements | No GL counterpart (cat 21-43) |
| Display cost element | KA03 | Cost Elements | |
| Cost element report | KA23 | Cost Elements | |
| Create cost center | KS01 | CCA | Master record |
| Change/display cost center | KS02, KS03 | CCA | |
| Cost center group | KSH1/2/3 | CCA | Hierarchy maintenance |
| Cost center standard hierarchy | OKEON | CCA | Define top node |
| Cost center planning (primary costs) | KP06 | CCA | Plan data entry |
| Cost center plan overview | KP04 | CCA | |
| Activity price planning | KP26 | CCA / Activity Types | Plan rates |
| Create planning profile | KSPI | CCA | Combines layout + planner profile |
| Create internal order | KO01 | Internal Orders | Master record |
| Change/display internal order | KO02, KO03 | Internal Orders | |
| Internal order list | KOK2 | Internal Orders | Collective processing |
| Order group | KOH1/2/3 | Internal Orders | |
| Order settlement | KO88 | Internal Orders / Period-End | Period-end workhorse |
| Create activity type | KL01 | Activity Types | |
| Display activity type plan | KP27 | Activity Types | |
| Actual price calculation | KSII | Activity Types / Period-End | |
| Create profit center | KE51 | PCA | |
| Profit center hierarchy | KCH1/2/3 | PCA | |
| PC plan/actual report | KE5Z | PCA | |
| Create cost estimate | CK11N | Product Costing | Single material |
| Costing run | CK40N | Product Costing | Mass costing |
| Mark/release cost estimate | CK24 | Product Costing | TWO steps: mark then release |
| Material price analysis | CKM3 | Product Costing | |
| Create assessment cycle | KSU1 | Period-End | Allocation setup |
| Run assessment cycle | KSU5 | Period-End | Uses secondary CE (cat 42) |
| Create distribution cycle | KSV1 | Period-End | Allocation setup |
| Run distribution cycle | KSV5 | Period-End | Preserves original CEs |
| Repost CO line items | KB61 | Period-End | Before allocations |
| Overhead calculation | KGI2 | Period-End | |
| Settle production orders | CO88 | Period-End | PP/PI orders |
| CC actual line items | KSB1 | Reporting | Primary CC report |
| Order actual line items | KOB1 | Reporting | Primary IO report |
| CC plan/actual | S_ALR_87013611 | Reporting | |
| IO plan/actual | S_ALR_87013015 | Reporting | |
| CO-PA actual posting | KE21N | CO-PA (basic) | Phase 10 for deep coverage |
| CO-PA settlement | KE24 | CO-PA (basic) | Settle to profitability segment |

---

## Cost Element Accounting

> **S/4HANA CRITICAL:** In S/4HANA, cost elements are no longer separate master data. GL accounts automatically serve as cost elements. KA01 and KA06 are obsolete. The cost element category is maintained directly on the GL account master (FS00). This is one of the biggest S/4HANA changes affecting CO.

**Primary Cost Elements (category 1, 3, 4, 11, 12, 22):**
Primary cost elements MUST have a corresponding GL account in FI with the same number. The GL account must exist first (FS00), then the cost element is created (KA01). Category 1 = primary costs/revenue (most common); category 11 = revenue; category 12 = sales deduction.

### KA01 — Create Primary Cost Element

**Menu Path:** Accounting > Controlling > Cost Element Accounting > Master Data > Cost Element > Individual Processing > Create Primary
**Usage:** Creates a primary cost element in CSKA/CSKB. The cost element number MUST match an existing GL account. Select cost element category (1 = primary costs is default). Set validity dates.
**Gotcha:** CRITICAL — if the GL account does not exist, KA01 fails. Create the GL account in FS00 first, then the cost element in KA01. Many consultants forget this sequence.

### KA02 — Change Cost Element

**Menu Path:** Accounting > Controlling > Cost Element Accounting > Master Data > Cost Element > Individual Processing > Change
**Usage:** Change cost element attributes (description, validity dates). Category cannot be changed after creation.

### KA03 — Display Cost Element

**Menu Path:** Accounting > Controlling > Cost Element Accounting > Master Data > Cost Element > Individual Processing > Display
**Usage:** Read-only display of cost element master data including category, validity dates, and controlling area assignment.

**Secondary Cost Elements (category 21, 31, 41, 42, 43):**
Secondary cost elements exist ONLY in CO — they have NO corresponding GL account. Created via KA06. Category 21 = internal settlement; category 31 = order/project results analysis; category 41 = overhead rates; category 42 = assessment; category 43 = internal activity allocation.

### KA06 — Create Secondary Cost Element

**Menu Path:** Accounting > Controlling > Cost Element Accounting > Master Data > Cost Element > Individual Processing > Create Secondary
**Usage:** Creates a secondary cost element for CO-internal allocations. These have no GL account counterpart. Select the appropriate category: 42 for assessment cycles, 43 for activity allocation, 21 for internal order settlement.
**Gotcha:** If you accidentally create a primary CE (KA01) when you need a secondary (KA06), the system will demand a GL account number. Use KA06 for any CO-internal allocation cost element.

### KA23 — Cost Element Report

**Menu Path:** Accounting > Controlling > Cost Element Accounting > Information System > Reports > Cost Elements > Master Data Indexes > Cost Element Report
**Usage:** List cost elements by category, controlling area, or cost element group. Useful for auditing which cost elements exist and their categories.

---

## Cost Center Accounting

**Cost Center Master Data (3):**

### KS01 — Create Cost Center

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Cost Center > Individual Processing > Create
**Usage:** Creates cost center master record in CSKS/CSKT. Required fields: controlling area, cost center number, name, description, responsible person (VERAK), cost center category (KOSAR — e.g., H = overhead, F = production, V = sales), company code, profit center assignment, validity dates.
**Gotcha:** Every cost center MUST be assigned to the standard hierarchy (OKEON). If the hierarchy node is missing, KS01 may fail. Also: profit center assignment (CSKS-PRCTR) is critical for PCA reporting — costs posted to this CC automatically appear on the assigned profit center.

### KS02 — Change Cost Center

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Cost Center > Individual Processing > Change
**Usage:** Modify cost center master data including responsible person, category, profit center assignment, and validity dates.

### KS03 — Display Cost Center

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Cost Center > Individual Processing > Display
**Usage:** Read-only display of cost center master record. Shows all fields including hierarchy assignment and profit center.

**Cost Center Hierarchy (3):**

### KSH1 — Create Cost Center Group

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Cost Center Group > Create
**Usage:** Creates a cost center group (node in the hierarchy). Groups are used as sender/receiver in allocation cycles and for summary reporting. The standard hierarchy is the mandatory top-level structure; additional groups can be created for flexible reporting.

### KSH2 — Change Cost Center Group

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Cost Center Group > Change
**Usage:** Add or remove cost centers from a group, or restructure the group hierarchy.

### KSH3 — Display Cost Center Group

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Cost Center Group > Display
**Usage:** Read-only display of cost center group structure and member cost centers.

**Cost Center Planning (4):**

### KP06 — Change Cost Center Plan (Primary Costs)

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Planning > Cost Element/Activity Input Planning > Change
**Usage:** Primary planning transaction for cost centers. Enter planned costs by cost element, period, and version (version 0 = plan/actual integration). Uses planning layouts defined in OKP1.
**Gotcha:** The planning layout determines which fields are available for input. If a cost element is not in the layout, it cannot be planned.

### KP26 — Change Activity Type Plan (Cost Center)

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Planning > Activity Type/Price Planning > Change
**Usage:** Plan activity output quantities and activity prices per cost center. Sets the planned activity rate (fixed + variable) used for activity allocation.
**Gotcha:** Activity prices planned here are used by the system to value activity allocations at period-end. If no price is planned, activity allocations post at zero.

### KP04 — Cost Center Plan Overview

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Planning > Planning Aids > Display Plan/Actual
**Usage:** Overview of planned vs actual costs for a cost center. Quick comparison without running a full report.

### KSPI — Create Planning Profile

**Menu Path:** SPRO > Controlling > Cost Center Accounting > Planning > Manual Planning > Define Planning Profiles
**Usage:** Combines planning layout with planner profile for streamlined planning sessions.

**Cost Center Reporting (3):**

### KSB1 — Cost Centers: Actual Line Items

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Information System > Reports > Line Items > Actual
**Usage:** The primary CO line item report for cost centers. Shows all actual postings by cost element, document number, posting date, amount. Equivalent of FBL3N for CO. Filter by cost center, cost center group, cost element, or period.
**Gotcha:** KSB1 shows CO document line items (COEP), not FI documents (BSEG). The CO document number differs from the FI document number.

### S_ALR_87013611 — Cost Centers: Actual/Plan/Variance

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Information System > Reports > Plan/Actual Comparisons > Cost Centers: Actual/Plan/Variance
**Usage:** The standard plan/actual comparison report for cost centers. Shows planned costs, actual costs, and variance by cost element. The most-used CO management report.
**Gotcha:** S_ALR report numbers vary by SAP release — verify the exact number via the menu path if the transaction code does not resolve.

### KSBL — Cost Center Summarization

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Information System > Reports > Summarization
**Usage:** Summarized cost center report showing totals by cost center group. Less detail than S_ALR_87013611 but useful for management overviews.

---

## Internal Orders

**Order Master Data (4):**

### KO01 — Create Internal Order

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Special Functions > Order > Create
**Usage:** Creates internal order master record in AUFK. Required: order type (AUART — defines number range, settlement profile, planning profile, budgeting), controlling area, company code. Optional but important: settlement rule (define receivers), responsible cost center, profit center.
**Gotcha:** The order type (configured in KOT2) controls nearly all order behavior — settlement profiles, planning profiles, budgeting, status management. Wrong order type = wrong behavior.

### KO02 — Change Internal Order

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Special Functions > Order > Change
**Usage:** Change order master data, maintain settlement rule (via Settlement Rule button), set status (released, technically complete, closed).

### KO03 — Display Internal Order

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Special Functions > Order > Display
**Usage:** Read-only display of internal order master data, status, and settlement rule.

### KO04 — Display Internal Order (Alternative)

**Usage:** Alternative display transaction for internal orders. Functionally similar to KO03.

**Order Collective Processing (2):**

### KOK2 — Internal Orders: Collective Change

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Special Functions > Collective Processing > Change
**Usage:** Mass change internal orders — update status, responsible person, or other master data fields across multiple orders simultaneously.

### KO12 — Change Order Master Data (List)

**Usage:** Change internal order master data in list format. Alternative to KOK2 for list-based processing.

**Order Groups (3):**

### KOH1 — Create Order Group

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Order Group > Create
**Usage:** Groups internal orders for reporting and settlement. Analogous to cost center groups (KSH1).

### KOH2 — Change Order Group

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Order Group > Change
**Usage:** Add or remove orders from a group.

### KOH3 — Display Order Group

**Menu Path:** Accounting > Controlling > Internal Orders > Master Data > Order Group > Display
**Usage:** Read-only display of order group structure and member orders.

**Order Reporting (2):**

### KOB1 — Internal Orders: Actual Line Items

**Menu Path:** Accounting > Controlling > Internal Orders > Information System > Reports > Line Items > Actual
**Usage:** Line item report for internal orders. Shows all actual postings by cost element. The primary report for reviewing costs collected on an order before settlement.

### S_ALR_87013015 — Internal Orders: Actual/Plan/Variance

**Menu Path:** Accounting > Controlling > Internal Orders > Information System > Reports > Plan/Actual Comparisons
**Usage:** Plan/actual comparison for internal orders. Shows planned costs, actual costs, and variance.

**Settlement:**

### KO88 — Settle Internal Order

**Menu Path:** Accounting > Controlling > Internal Orders > Period-End Closing > Single Functions > Settlement
**Usage:** THE period-end settlement transaction. Settles costs collected on internal orders to receivers defined in the settlement rule. Receiver types: GL account (FI posting), cost center, another internal order, asset under construction (AUC — for capital orders), WBS element (PS), profitability segment (CO-PA). Always run in test mode first (Test Run checkbox), review results, then execute live.
**Gotcha:** CRITICAL — if the settlement rule is missing on an order, KO88 skips it silently or produces an error. Verify settlement rules exist on all orders before period-end. Configure the settlement profile (OKO7) to require settlement rules at order creation.

---

## Activity Types

### KL01 — Create Activity Type

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Activity Type > Individual Processing > Create
**Usage:** Creates activity type master record in CSLA/CSLT. Activity types measure the output of cost centers (e.g., machine hours, labor hours). Required: controlling area, activity type key, name, activity unit (LEINH — e.g., H for hours), price indicator (TARKZ).
**Gotcha:** Activity types without planned prices (KP26) will allocate at zero — always plan activity prices before period-end.

### KL02 — Change Activity Type

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Activity Type > Individual Processing > Change
**Usage:** Modify activity type attributes including unit, price indicator, and validity dates.

### KL03 — Display Activity Type

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Master Data > Activity Type > Individual Processing > Display
**Usage:** Read-only display of activity type master data.

### KP27 — Display Activity Type Plan (Cost Center)

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Planning > Activity Type/Price Planning > Display
**Usage:** Display planned activity prices (complement to KP26 change mode). Shows fixed and variable price components per cost center per activity type.

### KSII — Actual Price Calculation

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Price Calculation
**Usage:** Calculates actual activity prices based on actual costs and actual activity quantities. Run at period-end to determine actual cost rates. Compares actual price to planned price for variance analysis.

---

## Profit Center Accounting

> **S/4HANA NOTE:** In S/4HANA, the separate PCA ledger (EC-PCA, tables GLPCA/GLPCT) is eliminated. PCA data is integrated into the Universal Journal (ACDOCA). KE5x T-codes still work but read from ACDOCA, not GLPCA. No reconciliation between FI and PCA is needed in S/4HANA.

### KE51 — Create Profit Center

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Master Data > Profit Center > Individual Processing > Create
**Usage:** Creates profit center master record in CEPC/CEPCT. Required: controlling area, profit center number, name, responsible person, company code, validity dates. Important field: SEGMENT (if segment reporting active under New GL).
**Gotcha:** In ECC 6, profit centers exist in a SEPARATE ledger from FI. All FI postings must carry a profit center (via substitution 1KEF or document splitting) or PCA reports will have gaps.

### KE52 — Change Profit Center

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Master Data > Profit Center > Individual Processing > Change
**Usage:** Modify profit center master data including responsible person, segment, and validity dates.

### KE53 — Display Profit Center

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Master Data > Profit Center > Individual Processing > Display
**Usage:** Read-only display of profit center master data.

### KCH1 — Create Profit Center Group

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Master Data > Profit Center Group > Create
**Usage:** Creates profit center hierarchy groups. The standard hierarchy is mandatory (defined in controlling area settings). Additional groups for flexible reporting.

### KCH2 — Change Profit Center Group

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Master Data > Profit Center Group > Change
**Usage:** Add or remove profit centers from a group.

### KCH3 — Display Profit Center Group

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Master Data > Profit Center Group > Display
**Usage:** Read-only display of profit center group structure.

### KE5Z — Profit Center: Actual/Plan/Variance

**Menu Path:** Accounting > Enterprise Controlling > Profit Center Accounting > Information System > Profit Center Reports > Plan/Actual Comparisons
**Usage:** The primary PCA management report. Shows planned and actual revenue/costs by profit center. Reads from GLPCA (ECC 6 separate ledger).
**Gotcha:** If KE5Z totals differ from FI reports (FAGLB03), the PCA separate ledger is out of sync — check that all FI postings carry profit center assignments.

---

## Product Costing

### CK11N — Create Material Cost Estimate

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Product Cost Planning > Material Costing > Cost Estimate with Quantity Structure > Create
**Usage:** THE central product costing transaction. Creates a cost estimate for a material by exploding the BOM and routing (if PP active) or using the costing structure. Costing variant (configured in OKKN) controls valuation: which prices to use, which BOM to explode, which routing.
**Gotcha:** CK11N creates the estimate but does NOT update the material master standard price. You must use CK24 to mark and release.

### CK13N — Display Material Cost Estimate

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Product Cost Planning > Material Costing > Cost Estimate with Quantity Structure > Display
**Usage:** Display existing cost estimate with itemization (cost component split, BOM explosion detail).

### CK24 — Mark/Release Standard Price

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Product Cost Planning > Material Costing > Price Update
**Usage:** TWO-STEP process for updating material master standard price:
1. **Mark** — Sets the cost estimate as the "future standard price." Visible in material master Costing 2 view but NOT yet operative. MBEW-ZPLP1 is updated (future price) but MBEW-STPRS (current standard price) is NOT changed.
2. **Release** — Activates the marked price as the new standard price. MBEW-STPRS is updated. This is the operative price used for inventory valuation.
**Gotcha:** CRITICAL — mark alone does NOT update the standard price. Many users forget the release step. Always verify MBEW-STPRS via MM03 > Accounting 1 after release. Between mark and release, the future price differs from the operative price.

### CK40N — Costing Run

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Product Cost Planning > Material Costing > Cost Estimate with Quantity Structure > Costing Run
**Usage:** Mass costing run. Creates, marks, and releases cost estimates for multiple materials in one execution. Steps: selection > costing > analysis > marking > release. Each step can be run independently.
**Gotcha:** CK40N can be scheduled as a background job for periodic standard cost revaluation.

### CKM3 — Material Price Analysis

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Actual Costing/Material Ledger > Information System > Detailed Reports > Material Price Analysis
**Usage:** Analyze material cost components, price differences, and exchange rate differences. Shows the multilevel price determination if Material Ledger is active.
**Gotcha:** In ECC 6, Material Ledger is optional (activated per plant). In S/4HANA, Material Ledger is mandatory.

### CKM3N — Material Price Analysis (New)

**Usage:** Enhanced version of CKM3 with improved navigation. Available in later EHP levels.

### KKBC_HOD — Product Cost: Cost Object Hierarchy Report

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Cost Object Controlling > Product Cost by Order > Information System > Reports
**Usage:** Report on costs collected on production orders or cost objects. Shows actual vs planned costs with variance categories.

### CK44 — Overhead Calculation: Cost Estimate

**Usage:** Apply overhead rates to cost estimates. Used when overhead surcharges are part of the costing model.

---

## Period-End Closing / Allocations

> Period-end processing is where CO delivers its primary value. The recommended sequence: repost (KB61) > overhead calc (KGI2) > assessment/distribution (KSU5/KSV5) > settlement (KO88/CO88) > actual price calc (KSII) > lock period.

### KB61 — Reposting of CO Line Items

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Actual Postings > Repostings of Line Items
**Usage:** Transfers individual CO line items from one cost object to another. Used to correct mis-postings before running allocations.
**Gotcha:** Run repostings BEFORE allocation cycles — once costs are allocated, reposting the original item creates confusion.

### KGI2 — Actual Overhead Calculation

**Menu Path:** Accounting > Controlling > Internal Orders > Period-End Closing > Single Functions > Overhead Calculation
**Usage:** Applies overhead rates (costing sheet) to actual costs on internal orders or cost centers. Creates overhead surcharge postings using secondary cost element (category 41). Run before settlement so overhead is included in settled amounts.

**Assessment Cycles:**

> **CRITICAL DISTINCTION — Assessment vs Distribution:**
> - **Assessment (KSU5):** Allocates costs using a SECONDARY cost element (category 42). The original cost elements on the sender are REPLACED by a single assessment cost element on the receiver. The receiver sees "Overhead Assessed" — the original cost detail is lost.
> - **Distribution (KSV5):** Allocates costs preserving the ORIGINAL cost elements. The receiver sees the same cost elements as the sender. Full cost transparency is maintained.
> Assessment is simpler (one CE on receiver); distribution provides better cost visibility. Most implementations use assessment for administrative overhead and distribution when cost element transparency is required.

### KSU1 — Create Assessment Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Assessment > Create
**Usage:** Define assessment cycle: name, allocation segments (sender CC/group, receiver CC/orders/WBS, allocation basis: fixed percentages, fixed amounts, statistical key figures, or variable portions).

### KSU2 — Change Assessment Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Assessment > Change
**Usage:** Modify existing assessment cycle segments, senders, receivers, or allocation basis.

### KSU3 — Display Assessment Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Assessment > Display
**Usage:** Read-only display of assessment cycle configuration.

### KSU5 — Run Assessment Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Assessment > Execute
**Usage:** Executes assessment allocation. Run in test mode first (Test Run flag), review results, then execute live. The system posts to the receiver using the secondary cost element (category 42) defined in the cycle.
**Gotcha:** If the assessment cycle has no valid segments or senders have zero balance, the run produces no postings — check sender balances first (KSB1).

### KSV1 — Create Distribution Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Distribution > Create
**Usage:** Define distribution cycle: same structure as assessment (senders, receivers, allocation basis) but preserves original cost elements on the receiver.

### KSV2 — Change Distribution Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Distribution > Change
**Usage:** Modify existing distribution cycle configuration.

### KSV3 — Display Distribution Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Distribution > Display
**Usage:** Read-only display of distribution cycle configuration.

### KSV5 — Run Distribution Cycle

**Menu Path:** Accounting > Controlling > Cost Center Accounting > Period-End Closing > Single Functions > Allocations > Distribution > Execute
**Usage:** Executes distribution allocation. Same execution process as KSU5 (test first, then live) but preserves original cost elements on the receiver.
**Gotcha:** Distribution can only allocate primary cost elements — secondary cost elements cannot be distributed (they must be assessed).

### CO88 — Settle Production Order

**Menu Path:** Accounting > Controlling > Product Cost Controlling > Cost Object Controlling > Product Cost by Order > Period-End Closing > Single Functions > Settlement
**Usage:** Settles production order costs to receivers. Similar to KO88 but for production/process orders (PP/PI). Run after variance calculation.

---

## Reporting (Cross-Subarea)

### KSB1 — Cost Centers: Actual Line Items
(Primary entry in CCA section above — cross-listed here as the most-used CO report.)

### KOB1 — Internal Orders: Actual Line Items
(Primary entry in Internal Orders section above — cross-listed here.)

### S_ALR_87013611 — Cost Centers: Actual/Plan/Variance
(Primary entry in CCA section above — cross-listed here.)

### S_ALR_87013015 — Internal Orders: Actual/Plan/Variance
(Primary entry in Internal Orders section above — cross-listed here.)

### KE5Z — Profit Center: Actual/Plan/Variance
(Primary entry in PCA section above — cross-listed here.)

### KKBC_HOD — Product Cost: Cost Object Report
(Primary entry in Product Costing section above — cross-listed here.)

---

## CO-PA (Basic)

> Deep CO-PA (Profitability Analysis) coverage is deferred to Phase 10. These are the minimum T-codes for CO-PA awareness.

### KE21N — Create CO-PA Actual Posting

**Menu Path:** Accounting > Controlling > Profitability Analysis > Actual Postings > Create Transfer Posting
**Usage:** Manual posting to a profitability segment. Used for adjustments or allocations directly into CO-PA.

### KE24 — Settlement to CO-PA

**Usage:** Settle costs from internal orders or cost centers to profitability segments. The receiver in the settlement rule is a CO-PA segment.

---

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|--------|
| Cost elements: KA01 (primary), KA06 (secondary) — separate master data in CSKA/CSKB | GL accounts serve as cost elements; category maintained on GL master (FS00) | KA01/KA06 obsolete; no separate cost element creation needed |
| PCA: separate ledger (EC-PCA), tables GLPCA/GLPCT | Universal Journal (ACDOCA); PCA integrated | KE5x T-codes still work; no FI-PCA reconciliation needed |
| Material Ledger: optional (activated per plant) | Material Ledger mandatory | Actual costing always available; CKM3 always populated |
| CO documents: COBK/COEP tables | CO data in ACDOCA | Technical change; T-codes still work |
| Controlling Area: can span multiple company codes freely | 1:1 CA to company code strongly recommended | Cross-CC controlling still possible but discouraged |
