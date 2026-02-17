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
