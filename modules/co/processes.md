---
module: co
content_type: processes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — Business Processes

> ECC 6.0 reference. Each process documented as numbered narrative followed by summary table (Step | Activity | T-code | Role | Output). Roles: CO Accountant, CO Manager, Cost Accountant, Product Cost Analyst. CO processes are predominantly period-end oriented — allocations, settlements, and costing runs happen monthly, not daily.

## CO Process Overview

Unlike FI (daily postings) or MM/SD (transactional), CO's primary value is in **period-end processing**. The core CO cycle:

1. **During the period:** Costs flow automatically from FI → CO via cost elements and account assignments
2. **At period-end:** CO redistributes costs via allocations, settles orders, runs product costing, and closes the period
3. **Reporting:** Plan/actual comparisons, variance analysis, cost transparency

---

## 1. Period-End Cost Allocation (Assessment / Distribution)

Cost allocation redistributes costs from sender cost centers (typically overhead departments like IT, HR, Facilities) to receiver objects (production cost centers, internal orders, WBS elements).

### CRITICAL DISTINCTION — Assessment vs Distribution

| Aspect | Assessment (KSU5) | Distribution (KSV5) |
|--------|--------------------|----------------------|
| Cost element on receiver | **Secondary CE (category 42)** — single "overhead assessed" element | **Original cost elements preserved** — receiver sees sender's cost breakdown |
| Cost transparency | Lost — receiver cannot see what the original costs were | Maintained — full drill-down to original costs |
| Which costs can be allocated | Primary AND secondary cost elements | **Primary cost elements ONLY** — secondary CEs cannot be distributed |
| Typical use | Administrative overhead (IT, HR allocations where detail is not needed) | Production overhead (where management wants to see cost composition) |
| Performance | Faster (fewer CO line items created) | Slower (one line item per original cost element) |

### Narrative

**Step 1 — Review Actual Costs on Sender Cost Centers** (CO Accountant)
Before running allocations, review the actual costs posted to sender cost centers during the period using KSB1 (actual line items). Verify completeness — are all vendor invoices posted? Are all accruals booked?

**Step 2 — Verify Allocation Cycle Configuration** (CO Accountant)
Review the assessment cycle (KSU2) or distribution cycle (KSV2). Check:
- Segments: sender cost centers/groups, receiver cost centers/orders, allocation basis
- Secondary cost element (for assessment): must exist (KA06, category 42)
- Allocation basis: percentages current? Statistical key figures (KB31N) entered for the period?

**Step 3 — Run Allocation Cycle in Test Mode** (CO Accountant)
Execute the cycle in test mode:
- Assessment: KSU5 with "Test Run" checkbox
- Distribution: KSV5 with "Test Run" checkbox
Review the test results: sender debits, receiver credits, allocation amounts. Verify the allocation basis produced expected distribution.

**Step 4 — Review Test Results** (CO Manager)
CO Manager reviews the test run output. Check:
- Are sender cost centers being fully allocated (zero balance after allocation)?
- Are receiver amounts reasonable?
- Any errors (unassigned senders, missing statistical key figure values)?

**Step 5 — Execute Allocation Cycle Live** (CO Accountant)
Run KSU5 or KSV5 without the test run flag. The system creates CO documents:
- Assessment: Dr Receiver (with secondary CE cat 42) / Cr Sender (with secondary CE cat 42)
- Distribution: Dr Receiver (with original CEs) / Cr Sender (with original CEs)

**Step 6 — Verify Results on Receiver Objects** (CO Accountant)
Confirm allocations posted correctly: KSB1 for receiver cost centers, KOB1 for receiver internal orders. Verify sender cost centers have expected remaining balance (typically zero for fully allocated CCs).

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Review sender actual costs | KSB1 | CO Accountant | Verified completeness of sender costs |
| 2 | Verify cycle configuration | KSU2/KSV2 | CO Accountant | Confirmed senders, receivers, basis |
| 3 | Run cycle in test mode | KSU5/KSV5 (test) | CO Accountant | Test results for review |
| 4 | Review test results | KSU5/KSV5 output | CO Manager | Approved allocation amounts |
| 5 | Execute cycle live | KSU5/KSV5 | CO Accountant | CO documents posted |
| 6 | Verify receiver results | KSB1/KOB1 | CO Accountant | Confirmed amounts on receivers |

---

## 2. Internal Order Settlement

Internal orders collect costs for a specific purpose (marketing campaign, repair project, capital investment). At period-end, these costs are settled (transferred) to permanent receivers.

### Narrative

**Step 1 — Review Actual Costs on the Order** (Cost Accountant)
Use KOB1 to review all actual costs posted to the order during the period. Verify completeness.

**Step 2 — Verify Settlement Rule** (Cost Accountant)
Open the order in KO02, navigate to the Settlement Rule. Verify:
- Receiver type and receiver object are correct (cost center, GL account, asset, WBS, CO-PA segment)
- Settlement percentage (typically 100% to one receiver, or split across multiple)
- Settlement cost element (secondary CE, category 21 for internal settlement or 22 for external)

Gotcha: CRITICAL — if the settlement rule does not exist, KO88 will skip the order or error. The most common period-end CO failure is missing settlement rules. Run a mass check before settlement.

**Step 3 — Run Settlement in Test Mode** (Cost Accountant)
Execute KO88 with "Test Run" checkbox. Review:
- Which orders are being settled
- Settlement amounts per receiver
- Any orders with errors (missing rules, blocked status)

**Step 4 — Execute Settlement Live** (Cost Accountant)
Run KO88 without test flag. The system:
- Debits the receiver with the settled amount
- Credits the internal order
- Creates CO settlement document (and FI document if settling to GL account or asset)

**Step 5 — Verify Receiver Objects** (Cost Accountant)
Confirm settlement posted: KSB1 for cost center receivers, FBL3N for GL account receivers, AW01N for asset receivers.

**Step 6 — Set Technical Completion (if applicable)** (Cost Accountant)
If the order is finished (no more costs expected), set status TECO in KO02. This prevents further postings and signals the order is settled and done.

### Settlement Receiver Types

| Receiver Type | COBRB-KONTY | T-code to Verify | FI Document? |
|---------------|-------------|-------------------|-------------|
| Cost Center | CTR | KSB1 | No (CO-internal) |
| Internal Order | ORD | KOB1 | No (CO-internal) |
| GL Account | KST | FBL3N | Yes |
| Fixed Asset / AUC | FXA | AW01N / AS03 | Yes (capitalization) |
| WBS Element | PSP | CJ03 | No (CO-internal) |
| CO-PA Segment | RKS | KE24 | No (CO-internal) |

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Review order actual costs | KOB1 | Cost Accountant | Verified order costs complete |
| 2 | Verify settlement rule | KO02 | Cost Accountant | Confirmed receiver and percentage |
| 3 | Run settlement test | KO88 (test) | Cost Accountant | Test results for review |
| 4 | Execute settlement live | KO88 | Cost Accountant | Settlement documents posted |
| 5 | Verify receiver objects | KSB1/FBL3N/AW01N | Cost Accountant | Confirmed amounts on receivers |
| 6 | Set TECO (if done) | KO02 | Cost Accountant | Order closed for further postings |

---

## 3. Product Costing Run

Product costing determines the standard cost of manufactured or procured materials. The cost estimate explodes the BOM and routing to calculate material costs, activity costs, and overhead.

### Narrative

**Step 1 — Create Cost Estimate** (Product Cost Analyst)
Use CK11N for a single material or CK40N for mass costing. Select:
- Costing variant (configured in OKKN — defines valuation approach)
- Plant and material
- Costing date range

The system explodes the BOM, values each component (using the costing variant's valuation), and calculates activity costs from routings. Output: itemized cost estimate with cost component split.

**Step 2 — Review Cost Estimate** (Product Cost Analyst)
Review the cost estimate in CK13N. Check:
- Cost component split (material, labor, overhead, subcontracting)
- BOM explosion completeness (all components resolved)
- Any error messages (missing prices, missing BOM, missing routing)

**Step 3 — Mark the Cost Estimate** (Product Cost Analyst)
Run CK24 → Mark. This sets the cost estimate as the "future standard price."
- MBEW-ZPLP1 (future planned price) is updated
- MBEW-STPRS (current standard price) is NOT changed
- The future price is visible in MM03 → Costing 2 view

> The marked price is a staging step. Production and inventory valuation continue to use the current standard price until release.

**Step 4 — Release the Cost Estimate** (Product Cost Analyst / CO Manager)
Run CK24 → Release. This activates the marked price as the new standard price.
- MBEW-STPRS (standard price) is updated to the marked value
- MBEW-PEINH (price unit) may also change
- All future goods movements are valued at the new standard price

Gotcha: CRITICAL — mark alone does NOT update the standard price. You MUST release. Many implementations have a two-step approval: Product Cost Analyst marks, CO Manager releases. If CK24 release appears to succeed but MM03 shows the old price, check transfer control configuration (OK17).

**Step 5 — Verify Standard Price Update** (Product Cost Analyst)
Check MM03 → Accounting 1 view:
- MBEW-STPRS should show the new standard price
- MBEW-VPRSV should show "S" (standard price control)
- Compare with CK13N cost estimate total

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Create cost estimate | CK11N / CK40N | Product Cost Analyst | Cost estimate with component split |
| 2 | Review cost estimate | CK13N | Product Cost Analyst | Verified BOM/routing/prices |
| 3 | Mark cost estimate | CK24 (mark) | Product Cost Analyst | Future price set (MBEW-ZPLP1) |
| 4 | Release cost estimate | CK24 (release) | CO Manager | Standard price updated (MBEW-STPRS) |
| 5 | Verify price update | MM03 | Product Cost Analyst | Confirmed new standard price |

> **S/4HANA Note:** In S/4HANA, Material Ledger is mandatory. Actual costing runs (CKMLCP) determine actual prices monthly. The CK11N/CK24 process still exists for standard cost estimates but actual costing provides a more accurate alternative.

---

## 4. Cost Center Planning

Cost center planning establishes the budget baseline for plan/actual comparison reporting. Planning is typically done annually with monthly distribution.

### Narrative

**Step 1 — Define Planning Framework** (CO Manager)
Set up for the planning cycle:
- Confirm planning version (version 0 for integrated plan/actual, or separate version)
- Confirm planning layout (OKP1) includes required cost elements
- Confirm planning profile (KSPI) is assigned

**Step 2 — Plan Primary Costs** (Cost Accountant)
Enter planned costs in KP06:
- Select cost center, version, period range, fiscal year
- Enter planned amounts by cost element (salaries, rent, supplies, etc.)
- Distribution options: equal distribution across periods, specific period amounts, or reference to prior year actuals

**Step 3 — Plan Activity Output** (Cost Accountant)
Enter planned activity quantities in KP26:
- Select cost center, activity type, version, fiscal year
- Enter planned activity quantity (e.g., 2000 machine hours)
- Enter planned activity price (fixed + variable per unit) or let the system calculate from planned costs / planned activity quantity

**Step 4 — Plan Statistical Key Figures** (Cost Accountant)
If allocation cycles use statistical key figures as allocation basis, enter planned values in KB31N. Example: planned headcount per cost center for HR cost allocation.

**Step 5 — Review Plan Data** (CO Manager)
Review plan using S_ALR_87013611 (plan/actual comparison — plan column shows entered values, actual is zero at start of year). Verify plan totals are reasonable and consistent with business expectations.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Define planning framework | OKP1/KSPI | CO Manager | Planning layouts and profiles ready |
| 2 | Plan primary costs | KP06 | Cost Accountant | Planned costs by CE and period |
| 3 | Plan activity output/prices | KP26 | Cost Accountant | Planned activity rates |
| 4 | Plan statistical key figures | KB31N | Cost Accountant | Planned allocation bases |
| 5 | Review plan data | S_ALR_87013611 | CO Manager | Verified plan totals |

---

## 5. Period-End CO Closing Sequence

This is the recommended sequence for the complete CO period-end close. Steps must be executed in order — each depends on the prior step's output.

> **Cross-reference:** FI period-end close is documented in `modules/fi/processes.md`. MM period-end close (MMPV, CKMI) is in `modules/mm/processes.md`. CO period-end typically runs AFTER FI and MM period-end to capture all postings.

### Sequence

| Step | Activity | T-code | Purpose | Dependencies |
|------|----------|--------|---------|--------------|
| 1 | Repost CO line items | KB61 | Correct mis-postings (move costs between CO objects) | Before any allocations — must run first |
| 2 | Calculate actual overhead | KGI2 | Apply overhead surcharges to orders/cost centers based on costing sheets | After reposting — overhead calculated on corrected balances |
| 3 | Run assessment cycles | KSU5 | Allocate overhead CC costs to receivers using secondary CE (cat 42) | After overhead calc — includes overhead in allocation |
| 4 | Run distribution cycles | KSV5 | Allocate costs preserving original CEs | After overhead calc — same dependency as assessment |
| 5 | Settle internal orders | KO88 | Move collected costs from orders to permanent receivers | After allocations — includes allocated costs in settlement |
| 6 | Settle production orders | CO88 | Move production order costs to receivers (if PP active) | After WIP/RA calculation (step 6a) |
| 6a | WIP/Results analysis | KKAX/KKA2 | Calculate work-in-process for open production orders (if PP active) | Before production order settlement |
| 7 | Calculate actual activity prices | KSII | Determine actual cost rates for activity types | After all allocations and settlements |
| 8 | Transfer pricing (PCA) | 1KEG | Execute profit center transfer pricing (if configured) | After all settlements |
| 9 | Lock CO period | OKP1 / COPI | Prevent further postings to the closed period | After all postings complete |

### Key Rules

1. **Reposting (KB61) MUST run first** — allocations and settlements use the balances at execution time. Reposting after allocation creates double-counting.
2. **Overhead (KGI2) before allocations** — overhead surcharges should be included in the allocated amounts.
3. **Allocations (KSU5/KSV5) before settlement (KO88)** — if a cost center receives allocated costs and those costs should be on an internal order, the allocation must run first so the costs are available for settlement.
4. **Settlement (KO88/CO88) after allocations** — settlement captures the final cost picture including all allocations.
5. **Actual price calculation (KSII) last** — uses final actual costs and actual activity quantities to determine actual activity rates. This is a reporting/analysis step, not a cost movement.

### Timing Relative to FI/MM

```
FI Period-End (month-end close, accruals, reclassifications)
    → MM Period-End (MMPV material price changes, CKMI ML closing)
        → CO Period-End (this sequence: repost → allocate → settle → close)
```

CO period-end depends on FI and MM being complete. All FI postings with CO account assignments must be posted before CO allocations run, or the allocations will miss those costs.

---
