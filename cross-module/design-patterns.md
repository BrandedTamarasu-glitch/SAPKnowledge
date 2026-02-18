---
module: cross-module
content_type: patterns
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-18
related_modules: [mm, sd, fi, co]
---

# Cross-Module Solution Design Patterns

> ECC 6.0 reference. Twelve named patterns covering the most common cross-module business requirements in SAP ECC 6. Each pattern maps a business requirement to the SAP approach, summarizes configuration, defines master data, and provides testing steps. Patterns sit above individual module decision trees — they answer "which approach do I use?" and then point to module files for the "how do I configure it?" detail. For complete implementation walkthroughs of process and configuration scenarios, see `cross-module/playbooks.md`.

## How to Use This File

1. Identify the business requirement your project must satisfy
2. Find the matching pattern (or the closest one)
3. Read the SAP approach, when-to-use guidance, and configuration summary
4. Follow cross-references to `cross-module/playbooks.md` for full implementation walkthroughs
5. Follow cross-references to module decision trees (mm-advanced.md, co-advanced.md, sd-advanced.md) for config-level choices

---

## Pattern 1: Make-to-Stock Production with Standard Costing

**Business requirement:** Manufacture standard products in advance of customer demand. Products are stocked in inventory and shipped from available stock when sales orders arrive. Management needs product cost visibility and manufacturing variance analysis.

**SAP ECC 6 approach:** Use make-to-stock (MTS) planning with standard price control (S) on the material master. CO-PC creates standard cost estimates (CK11N/CK24) that set the material's standard price. Production orders collect actual costs; CO88 settles the variance between standard and actual cost at period-end.

**When to use:** Products with predictable demand; manufacturing to replenish safety stock or satisfy planned independent requirements (MD61); management requires monthly variance analysis by product.

**When NOT to use:** Custom or engineer-to-order products (use Pattern 2); high-mix/low-volume where standard cost loses relevance; pure trading (no manufacturing).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | Set price control = S on material master | MM02 → Accounting 1 view → MBEW-VPRSV = S |
| CO-PC | Define costing variant for standard cost | OKKN — costing variant settings |
| CO-PC | Create and release standard cost estimate | CK11N (create) → CK24 (mark then release) |
| CO (CCA) | Define overhead costing sheet | SPRO → Controlling → Product Cost Controlling → Basic Settings → Overhead → Define Costing Sheets |
| CO (CCA) | Configure actual overhead calculation | KGI2 — applies overhead at period-end |
| MM/PP | MRP settings for production | MARC-DISMM = PD (MRP-based planning) |

### Master Data Setup

- **Material master (MRP 1/2 view):** Procurement type F or X (in-house production), lot size, planned delivery time
- **Material master (Accounting 1 view):** Price control S, standard price updated after CK24 release
- **Bill of Materials:** Component structure for BOM explosion in CK11N (via CS01/CS02)
- **Routing (if PP active):** Operations, work centers, standard values for activity allocation
- **Cost estimate (CK11N):** Explodes BOM + routing; must be marked and released via CK24 before standard price updates MBEW-STPRS
- **Production order type:** Controls settlement profile — settlement to material/stock (category 22 CE) via CO88

### Testing Steps

1. Create cost estimate: CK11N → select costing variant → execute → review cost component split (material + labor + overhead)
2. Mark and release: CK24 → verify MM03 Accounting 1 view shows new standard price in MBEW-STPRS
3. Post goods issue for production: MIGO movement 261 → verify GBB/VBR posting at standard price
4. Post goods receipt for production order: MIGO movement 101 → verify BSX inventory posting at standard price + PRD variance posting (if actual differs)
5. Run period-end settlement: CO88 → verify variance posting (Dr Variance / Cr Production Order) in FBL3N for the variance GL account

**See also:** `modules/co/processes.md` Section 3 (Product Costing Run). `modules/co/co-advanced.md` DT 8 for make-to-stock vs make-to-order decision tree.

---

## Pattern 2: Engineer-to-Order with Project Cost Collection

**Business requirement:** Manufacture or deliver custom products/services for specific customer orders. Each project has unique costs that must be tracked individually, reported to the customer, and settled when complete. Costs may be capitalized as assets or billed to the customer.

**SAP ECC 6 approach:** Use internal orders (KO01) as cost collectors for the customer project, or WBS elements if PS (Project System) is active. All costs (materials, labor, services) are posted to the internal order. At project completion, costs are settled to the final receiver: GL account (expense), customer project, or fixed asset.

**When to use:** Customer-specific projects where costs must be tracked per project; capital investment projects where construction costs will be capitalized; repair or service projects billed at cost-plus.

**When NOT to use:** Standard repetitive manufacturing (use Pattern 1); high-volume make-to-order where individual cost tracking would be impractical.

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| CO | Define internal order type | KOT2 — order type controls settlement profile, budgeting |
| CO | Define settlement profile | OKO7 — allowed receiver types (cost center, GL, asset, WBS) |
| CO | Define allocation structure | OKO6 — maps source CEs to settlement CEs |
| MM | Account-assigned purchase orders | ME21N — account assignment category F (order) or P (project) |
| FI | Configure AUC account (if capitalizing) | SPRO → FI-AA → Asset Classes → Define Asset Classes for AUC |
| CO | Default account assignment (OKB9) | OKB9 — fallback when order not entered manually |

### Master Data Setup

- **Internal order (KO01):** Order type determines settlement profile and budgeting; assign to project cost center and profit center
- **Settlement rule (KO02):** Define receivers (cost center for expense, fixed asset for capitalization, GL account for project billing); percentage distribution
- **Purchase orders:** Use account assignment category F (internal order) — all costs post directly to the order via MIGO/MIRO
- **Material cost objects:** If materials are procured project-specifically, reference the order on the purchase requisition (ME51N → account assignment)

### Testing Steps

1. Create internal order: KO01 → release order for posting (status REL)
2. Post expense to order: FB50 with cost element and order → verify KOB1 shows the cost
3. Post project-specific purchase: ME21N with account assignment F + order number → MIGO + MIRO → verify KOB1
4. Run settlement (test mode): KO88 → test run → review settlement amounts and receivers
5. Execute settlement live: KO88 → verify FBL3N for GL receiver or AW01N for asset receiver

**See also:** `modules/co/processes.md` Section 2 (Internal Order Settlement). `modules/co/co-advanced.md` DT 4 for make-to-order vs internal order decision. `cross-module/playbooks.md` Playbook 8 (Investment Project Capitalization) for the AUC→asset settlement walkthrough.

---

## Pattern 3: Consignment Stock Management

**Business requirement:** Track inventory that remains vendor-owned while stored in your warehouse (vendor consignment), OR track your own inventory stored at customer sites with billing triggered only at actual consumption (customer consignment).

**SAP ECC 6 approach:** Use special stock indicator K (vendor consignment) or W (customer consignment). Vendor consignment: goods movements 101K (receive) / 201K (withdraw to own stock). Customer consignment: SD order types KB/KE/KR/KA with movements 631/632/633/634. Billing occurs ONLY at consignment issue (movement 633) — not at fill-up.

**When to use:** Vendor consignment — vendor retains ownership until you withdraw/consume the stock; useful for high-value or slow-moving items where inventory financing risk stays with the vendor. Customer consignment — you retain ownership until the customer reports consumption; common in automotive and retail supplier relationships.

**When NOT to use:** If ownership transfers immediately on goods receipt (standard PO), use standard MM procurement (Pattern 1 or standard P2P). If the customer always takes full delivery ownership, use standard O2C (no consignment needed).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | Consignment info record | ME11 — info category = Consignment; vendor + material + plant; consignment price per unit |
| SD | Item category determination for consignment | VOV7 + OVLP — item categories KB/KE/KR/KA |
| SD | Schedule line category for consignment movements | VOV6 — movement types 631/632/633/634 |
| SD | Copy control for consignment billing | VTFL — consignment issue delivery → billing type |
| FI | OBYC KON key for consignment payable | OBYC → KON — payable account for vendor consignment withdrawal (411K) |
| FI | VKOA for consignment issue billing | VKOA → ERL — revenue account for consignment issue (633) |

### Master Data Setup

- **Vendor consignment info record (ME11):** Info category = Consignment; unit price posted at withdrawal (201K/411K), NOT at receipt
- **Customer master (KNVV):** No special field; consignment behavior controlled by SD item categories (KB/KE/KR/KA)
- **Material master:** No special field needed for consignment — special stock type is controlled by movement type and info record
- **SD order types:** KB (fill-up), KE (issue), KR (pickup), KA (consignment returns) — must exist in VOV8

### Testing Steps

1. Vendor consignment GR: MIGO movement type 101, special stock indicator K → verify MB52 shows stock in "Vendor Consignment" column; FBL1N shows NO vendor liability posted yet
2. Consignment withdrawal: MIGO movement 201K → verify FBL1N shows vendor liability for the withdrawn quantity (KON posting)
3. Customer consignment fill-up: VA01 order type KB → VL01N → VL02N (PGI posts movement 631) → verify MB52 shows consignment stock at customer (special stock W)
4. Customer consignment issue: VA01 order type KE → delivery → PGI (movement 633) → VF01 → verify revenue posted via VKOA; MB52 shows consignment stock reduced

**See also:** `cross-module/playbooks.md` Playbook 1 for the complete implementation walkthrough. `cross-module/mm-sd-integration.md` Section Consignment for movement type detail. `modules/sd/processes.md` Section 6.

---

## Pattern 4: Third-Party Drop Shipment

**Business requirement:** Fulfill customer orders via direct vendor delivery to the customer. The company acts as the commercial intermediary — it takes the customer order and issues a purchase order to the vendor — but the vendor ships directly to the customer without the goods ever entering the company's warehouse.

**SAP ECC 6 approach:** Item category TAS in the sales order triggers automatic purchase requisition creation. The buyer converts the PR to a PO (ME21N) with the customer's ship-to address. The vendor ships directly. MIRO posts a statistical goods receipt (no physical inventory). VF01 creates the customer invoice. Two independent invoices: one for the vendor (MIRO) and one for the customer (VF01).

**When to use:** Vendor has product the company doesn't stock; customer needs fast delivery from vendor location; company margin on pass-through sales; drop-ship programs.

**When NOT to use:** If the company physically handles or inspects the goods before delivery (use standard O2C + P2P). If the vendor cannot ship directly to the customer's address.

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| SD | Item category TAS configuration | VOV7 — billing relevance B (order-related), no delivery |
| SD | Item category determination for TAS | OVLP — sales doc type + item category group BANS → TAS |
| MM | Auto PR from sales order | Triggered automatically when TAS item category is saved |
| MM | Purchase order with customer ship-to | ME21N — delivery address tab shows customer address (from VBKD) |
| FI | Statistical GR (MIRO without physical stock) | MIRO — GR-based IV still required; no physical inventory movement |
| FI | Customer billing (VF01) | Order-related billing — VTAF copy control |

### Master Data Setup

- **Material master (MVKE-MTPOS):** Item category group BANS (third-party) → triggers TAS item category determination
- **Vendor master (LFM1):** Standard vendor — no special setup for third-party; delivery address comes from the sales order ship-to
- **Customer master (KNVP):** Ship-to address automatically transferred to PO delivery address via VBKD-KUNNR
- **Purchasing info record:** Optional but recommended to default vendor price and lead time on the auto-created PR

### Testing Steps

1. Create sales order: VA01 OR → material with BANS item category group → verify TAS item category proposed; save → verify PR created automatically (ME53N)
2. Convert PR to PO: ME21N referencing the auto-created PR → verify delivery address on PO = customer ship-to address
3. Post vendor invoice (statistical): MIRO → select "Statistical" GR if required → verify no physical inventory movement in MMBE; vendor open item in FBL1N
4. Create customer invoice: VF01 from the sales order → verify customer open item in FBL5N; no delivery document in document flow
5. Verify two-invoice separation: MIRO vendor invoice (cost) and VF01 customer invoice (revenue) are independent FI documents; margin = revenue - vendor cost

**See also:** `cross-module/playbooks.md` Playbook 3 for the complete implementation walkthrough. `modules/sd/processes.md` Section 7. `cross-module/mm-sd-integration.md` Section Third-Party Processing.

---

## Pattern 5: Subcontracting (Toll Processing)

**Business requirement:** Send raw material components to a vendor (subcontractor) for processing into a finished or semi-finished product, then receive the processed goods back. The company owns the components throughout; the vendor provides the processing service.

**SAP ECC 6 approach:** Use subcontracting PO type (item category L in ME21N) with special procurement key 30 (MARC-SOBSL) on the material master. Components are transferred to the subcontractor via movement type 541 (no FI posting — stock reclassification only). Finished goods receipt (MIGO movement 101 against subcontracting PO) simultaneously posts movement type 543 (component consumption from subcontracting stock) automatically.

**When to use:** Heat treatment, surface coating, packaging, assembly by a specialized vendor; company provides the base material and controls the BOM.

**When NOT to use:** If the vendor provides both material and labor (buy the finished product outright — use standard PO). If the company has in-house capacity for the processing step (use production order).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | Subcontracting BOM | CS01 — component list for the finished/processed material |
| MM | Special procurement key on material | MM02 → MRP 2 view → MARC-SOBSL = 30 |
| MM | Subcontracting PO item category | ME21N — item category L automatically triggers BOM explosion |
| MM | Component transfer | MIGO movement 541 — no FI posting |
| MM | GR for finished goods (with auto-543) | MIGO movement 101 against subcontracting PO |
| FI | OBYC GBB/VBO for 543 posting | OBYC → GBB → VBO — component consumption account |

### Master Data Setup

- **Material master (MRP 2 view):** MARC-SOBSL = 30 (subcontracting); MARC-BESKZ = F or X (in-house or both) — tells MRP to generate subcontracting PRs
- **BOM (CS01):** Lists components to be provided to the subcontractor; BOM usage = 1 (production) or as configured; components are sent via movement 541
- **Subcontracting info record (ME11):** Info category = Subcontracting; vendor + service material + plant; processing price per unit (service fee only — NOT material cost)
- **Vendor master:** Standard vendor; subcontracting requires no special vendor flag

### Testing Steps

1. Transfer components to subcontractor: MIGO → movement type 541 → material = component, special stock O → verify MMBE shows stock "With Subcontractor" for the vendor; verify NO FI document created (541 has no FI posting)
2. Receive processed goods: MIGO → GR against subcontracting PO → movement 101 → verify: (a) finished goods stock increased in MMBE, (b) movement 543 auto-posted for component consumption, (c) FI document shows BSX (finished goods) + WRX (GR/IR for service fee) + GBB/VBO (component consumption)
3. Post subcontractor invoice: MIRO against the subcontracting PO → verify only the processing fee is invoiced (not the component value)
4. Verify component consumption: MB51 → movement type 543 → confirm components were consumed in correct quantity; GBB/VBO posting visible in FBL3N

**See also:** `cross-module/playbooks.md` Playbook 4 for the complete implementation walkthrough. `modules/mm/mm-advanced.md` DT 9 for subcontracting decision tree. `cross-module/mm-sd-integration.md` Section Subcontracting.

---

## Pattern 6: Intercompany Sales / Stock Transfer

**Business requirement:** Transfer goods or deliver to customers across company code boundaries within the same corporate group. Each company code must record independent revenue, cost, and payables/receivables. Legal billing between group entities is required.

**SAP ECC 6 approach:** Use Stock Transport Orders (PO type UB, ME21N) for plant-to-plant transfers. For cross-company-code STOs with SD delivery, the supplying plant ships via an SD delivery document and intercompany billing creates an invoice between the two company codes. For intercompany customer sales (order in one company, deliver from another), configure intercompany billing with document types IV (intercompany invoice) and settings in VKOA.

**When to use:** Manufacturing in one company code, selling in another; shared distribution center model; transfer pricing between group entities required for compliance.

**When NOT to use:** Intra-company transfers within the same company code (use plant-to-plant STO without intercompany billing). Non-legal entities without transfer pricing requirements.

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | STO purchase order type UB | ME21N → document type UB |
| SD | Intercompany billing type IV | VOFA — billing type IV for intercompany invoice |
| SD | VKOA for intercompany revenue (PI account key) | VKOA → PI — intercompany revenue GL account in supplying CC |
| FI | Intercompany payable/receivable accounts | SPRO → FI → Accounts Receivable/Payable → Business Transactions → Intercompany |
| SD | Copy control for STO delivery → intercompany billing | VTFL — STO delivery type NL → billing type IV |
| CO | KALC for cross-company-code CO allocations | OKKP — controlling area spans both company codes; KALC creates FI intercompany entries |

### Master Data Setup

- **Customer master for supplying company:** The supplying plant must have an "internal customer" master record for the ordering company code to enable SD billing (VKOA lookup uses this customer's KTGRD)
- **Vendor master for ordering company:** The ordering company must have an "internal vendor" master for the supplying company (enables MIRO for the intercompany invoice)
- **Material master:** Same material number in both plants; price control may differ per plant
- **Transfer price configuration:** Intercompany price must be agreed and configured in VKOA (PI account key in pricing procedure for intercompany scenario)

### Testing Steps

1. Create STO: ME21N → document type UB → receiving plant orders from supplying plant
2. Supplying plant ships: VL01N (NL delivery type) → VL02N (PGI with movement 641) → verify goods in transit between company codes
3. Receiving plant GR: MIGO → movement 101 against STO → verify stock in receiving plant (movement 101) + stock reduction in supplying plant (movement 641)
4. Intercompany billing: VF01 → billing type IV → verify FI document in supplying company code: Dr Intercompany Receivable / Cr Intercompany Revenue (PI account key)
5. Ordering company posts AP: MIRO against the intercompany PO → verify Intercompany Payable in ordering CC; verify intercompany balance nets to zero across both company codes

**See also:** `cross-module/playbooks.md` Playbook 2 for the complete intercompany sales/STO implementation walkthrough. `cross-module/mm-sd-integration.md` Section Stock Transport Orders. `modules/sd/sd-advanced.md` Example 8 (intercompany billing FI posting).

---

## Pattern 7: Overhead Allocation to Products

**Business requirement:** Allocate overhead costs (IT, HR, Facilities) from administrative cost centers to product cost centers or directly to production orders. Management requires full-absorption costing to understand true product cost including indirect costs.

**SAP ECC 6 approach:** Two mechanisms serve different needs. For standard product costing: configure an overhead costing sheet (SPRO → Costing Sheets) that applies percentage surcharges to direct costs during CK11N cost estimation and KGI2 actual overhead calculation. For period-end redistribution of actual overhead: configure assessment cycles (KSU5) or distribution cycles (KSV5) to reallocate overhead cost centers to receivers.

**When to use:** Any time you need to see indirect cost in product cost estimates or in cost center/order actuals; required for standard costing environments; required when management wants to see fully burdened product cost.

**When NOT to use:** If management wants to see direct costs only (marginal costing approach); if overhead allocation distorts product cost comparisons (use contribution margin reporting via CO-PA instead).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| CO | Define overhead costing sheet (for product costing) | SPRO → CO → Product Cost Controlling → Basic Settings → Overhead → Define Costing Sheets |
| CO | Define assessment cycle (for CC-to-CC allocation) | KSU1 — senders, receivers, secondary CE (cat 42), allocation basis |
| CO | Define distribution cycle (for CE-preserving allocation) | KSV1 — same structure as assessment but preserves original CEs |
| CO | Enter statistical key figures for allocation basis | KB31N — headcount, square meters, machine hours per cost center per period |
| CO | Run assessment or distribution at period-end | KSU5 / KSV5 — test mode first, then live |
| CO | Overhead calculation on production orders | KGI2 — applies costing sheet surcharges to actual order costs |

### Master Data Setup

- **Overhead costing sheet:** Defines which base cost elements receive overhead, the rate or percentage, and the credit cost center (where the overhead "flows from" in CO)
- **Assessment cycle:** Defines sender cost centers (overhead departments), receivers (production cost centers or orders), allocation basis (statistical key figures, fixed percentages, or variable portions based on receiver activity)
- **Secondary cost element (category 42):** Required for assessment — created via KA06 — appears on the receiver as "overhead assessed" replacing original cost element detail
- **Statistical key figures (KK01, KB31N):** Non-monetary allocation bases (headcount, square meters) entered monthly for each cost center

### Testing Steps

1. Verify overhead on cost estimate: CK11N → inspect itemization → overhead line should show surcharge calculated from costing sheet; if missing, check costing sheet assignment (OKKN → costing variant → valuation variant → costing sheet)
2. Enter statistical key figures: KB31N → headcount or m² per cost center per period
3. Run assessment cycle (test): KSU5 → test mode → review sender credits and receiver debits; verify allocation basis distributes as expected
4. Execute assessment live: KSU5 → live → verify KSB1 on receiving cost centers shows secondary CE (category 42) overhead line
5. Run overhead calculation on orders: KGI2 → verify KOB1 on production orders shows overhead surcharge (secondary CE category 41)

**See also:** `modules/co/processes.md` Section 1 (Period-End Cost Allocation). `modules/co/co-advanced.md` DT 1 (Assessment vs Distribution decision tree). `modules/co/config-spro.md` Section 6 (Allocation Cycle Configuration).

---

## Pattern 8: Investment Project Capitalization

**Business requirement:** Collect costs for a capital investment project (construction, equipment installation, IT system build) and at completion capitalize those costs as a fixed asset. All spending must be tracked on the project, subject to budget monitoring, and converted to an Asset Under Construction (AUC) then to a final asset when complete.

**SAP ECC 6 approach:** Use an internal order of type Investment (KOT2 order class = investment order). Costs accumulate on the order during the project. Periodic settlement via KO88 moves costs to an Asset Under Construction (AUC) in FI-AM. At project completion, a final settlement moves AUC to the final fixed asset (AIAB/AIBU for asset retirement from AUC).

**When to use:** Any capital expenditure project where CAPEX must be tracked separately from OPEX; construction-in-progress accounting; IT system development costs to be capitalized per accounting policy.

**When NOT to use:** Operating expense projects that will never be capitalized (use a standard overhead internal order with cost center receiver). Projects managed in PS/Project System (use WBS elements and CJ88 instead of KO88).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| CO | Define investment order type | KOT2 — object class = INVEST (investment); settlement profile allows FXA (asset) receiver |
| CO | Configure AUC asset class | SPRO → FI → Asset Accounting → Asset Classes → Define Asset Classes → include AUC class |
| FI-AM | Create AUC asset master | AS01 — asset class = AUC (depreciation area: no depreciation during construction) |
| CO | Define settlement profile allowing AUC | OKO7 — receiver type FXA allowed; category 22 CE for external settlement |
| CO | Periodic settlement to AUC | KO88 — receiver = AUC asset number; creates FI capitalization document |
| FI-AM | Final capitalization from AUC to asset | AIAB (transfer from AUC) + AIBU (final settlement) |

### Master Data Setup

- **Internal order (KO01):** Order type = investment order type; profit center assigned; budget can be managed via SPRO budget profile assigned to order type
- **AUC asset master (AS01):** Asset class = AUC; no depreciation start date (AUC is construction-in-progress); company code + cost center (ANLZ table)
- **Settlement rule (KO02):** Receiver type FXA (fixed asset); receiver = AUC asset number; category 22 cost element for the FI capitalization entry
- **Final asset master (AS01):** Created at completion; asset class with appropriate depreciation key; AIAB/AIBU links the final capitalization from AUC

### Testing Steps

1. Post project cost: FB50 or MIRO with account assignment to the investment order → verify KOB1 shows cost on order; verify budget check not exceeded (if budgeting active)
2. Periodic settlement to AUC: KO88 → receiver = AUC asset → verify AW01N (asset explorer) shows capitalization posting on the AUC; FBL3N shows capitalization entry
3. Repeat steps 1-2 over project duration as costs accumulate
4. Final capitalization: AIAB → settle AUC to final asset → AIBU → verify final asset in AS03 shows asset value; AUC is reduced to zero; depreciation starts in the final asset's depreciation key
5. Verify CO settlement: KOB1 → order shows total costs settled; order status should reflect completion (TECO after final settlement)

**See also:** `modules/co/processes.md` Section 2 (Internal Order Settlement). `modules/co/co-advanced.md` DT 4 (settlement receiver type decision). `cross-module/playbooks.md` Playbook 8 (Investment Project Capitalization full walkthrough).

---

## Pattern 9: Batch-Managed Inventory with Shelf Life

**Business requirement:** Track inventory by production batch with expiry dates or best-before dates. Deliveries must use the oldest or soonest-expiring batches first (FEFO — First Expired First Out). Regulatory or quality requirements mandate traceability from vendor receipt to customer delivery.

**SAP ECC 6 approach:** Activate batch management per material (MARC-XCHPF) in the Plant Data/Storage 1 view. Configure batch classification with shelf life characteristics (CT04). Set minimum remaining shelf life and total shelf life on the material master (Plant Data/Storage view — MARC-MHDLP/MHDLV). In SD, configure batch determination (FEFO sort rule) to automatically select the soonest-expiring batch at delivery creation.

**When to use:** Food, pharmaceutical, chemical industries with expiry dates; any material requiring lot traceability; industries with regulatory recall requirements; quality management requiring batch-specific test results.

**When NOT to use:** Materials where all units are interchangeable and lot traceability is not required (standard non-batch materials). Commodity materials where FEFO provides no business value.

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | Activate batch management per material/plant | MM02 → Plant Data/Storage 1 → MARC-XCHPF = X |
| MM/QM | Define batch classification characteristics | CT04 — shelf life characteristics (MHDRST = date of manufacture, VFDAT = expiry date) |
| MM | Set shelf life parameters on material | MM02 → Plant Data/Storage 2 → minimum remaining shelf life (MHDLP), total shelf life (MHDLV) |
| SD | Activate batch determination for movement type | SPRO → Logistics Execution → Shipping → Picking → Batch Determination → Activate |
| SD | Define batch search strategy (FEFO) | MBC1 — search strategy type + FEFO sort rule by expiry date |
| SD | Assign batch search strategy to condition record | VK11 using batch search strategy condition type |

### Master Data Setup

- **Material master (Plant Data/Storage 1):** MARC-XCHPF = X activates batch requirement; all goods movements for this material/plant now require a batch number
- **Material master (Plant Data/Storage 2):** Minimum remaining shelf life = minimum days a batch must have remaining when issued to customer; total shelf life = maximum days from manufacture
- **Batch master (MSC1N):** Created automatically at GR or manually before GR; stores batch-specific data including expiry date (VFDAT), manufacturing date, and classification characteristics
- **Batch classification:** Characteristics (CT04) linked to class (CL01) linked to batch → enables search by expiry date in FEFO batch determination

### Testing Steps

1. Post GR with batch: MIGO movement 101 → enter batch number → enter expiry date on batch tab → verify MMBE shows stock with batch number
2. Check batch information: MSC3N (display batch master) → verify expiry date and classification data stored correctly; MB52 shows batch-specific stock
3. Create delivery (batch determination): VL01N from sales order → in delivery, batch determination automatically proposes soonest-expiring batch (if FEFO active) → verify VLBR shows batch in delivery
4. Verify shelf life check: delivery should warn or block if batch expiry is within the minimum remaining shelf life configured for the material
5. Verify traceability: VLBR → enter batch number → system shows all deliveries where that batch was used

**See also:** `cross-module/playbooks.md` Playbook 7 (Batch Management complete walkthrough). `modules/mm/mm-advanced.md` DT 7 (batch management decision tree). `modules/sd/tcodes.md` (VLBR, MBC1, CL20N entries).

---

## Pattern 10: Serial Number Tracking to Asset Register

**Business requirement:** Track individual serialized equipment from vendor goods receipt through customer delivery and, for equipment kept in-house, link the serial number to a fixed asset record. Quality and warranty tracking requires individual unit history. Assets require serial number identification for physical audit.

**SAP ECC 6 approach:** Define a serial number profile (SPRO → MM → Logistics → Serial Numbers → Define Serial Number Profiles) and assign it to the material master (MARC-SERAIL field in Plant Data/Storage 1 view). The profile controls at which transactions serial numbers must be entered (GR, GI, delivery). For in-house equipment: create equipment master records (IE01 in PM module) that link to fixed assets (ANLZ-ILOAN).

**When to use:** High-value individual units requiring warranty tracking; equipment where asset management requires serial number identification; regulated industries requiring individual unit traceability (medical devices, aerospace, defense); equipment with maintenance histories.

**When NOT to use:** Low-value consumables where individual unit tracking adds no value. Bulk materials (liquids, powder) where lot tracking (batches — Pattern 9) is more appropriate than serialization.

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | Define serial number profile | SPRO → Plant Maintenance → Technical Objects → Serial Number Management → Define Serial Number Profiles |
| MM | Assign serial number profile to material | MM02 → Plant Data/Storage 1 → MARC-SERAIL = serial number profile |
| SD | Activate serial numbers for SD deliveries | Serial number profile setting: serialization procedure for goods issue (VL02N) |
| PM | Create equipment master | IE01 — equipment master with serial number; links to asset if capitalized |
| FI-AM | Link equipment to fixed asset | AS02 or within IE01 → enter asset number in equipment master → ANLZ-ILOAN |
| FI-AM | Asset sub-number for individual unit tracking | AS11 — create sub-number per serial number if each unit is a separate asset |

### Master Data Setup

- **Serial number profile (SPRO):** Defines at which logistics transactions serial numbers are required/optional; profiles control whether serial number must match between GR and GI
- **Material master (MARC-SERAIL):** Serial number profile assigned at plant level; once assigned and goods movements exist, changing the profile is restricted
- **Equipment master (IE01):** PM equipment record stores maintenance history, serial number, manufacturer data; ANLZ table links to fixed asset when the equipment is capitalized
- **Fixed asset master (AS01/AS11):** If each serialized unit is a separate asset, create sub-numbers (AS11) for tracking individual unit depreciation and book value

### Testing Steps

1. Post GR with serial number: MIGO movement 101 → serial number entry required → enter unique serial number → verify IQ01/IQ03 shows serial number with equipment master created
2. Check equipment-asset link: IE02 → equipment master → look for asset reference in the structure/organization data (ANLZ-ILOAN); if capital equipment, link should exist
3. Customer delivery with serial number: VL01N + VL02N → serial number required at PGI → enter serial number → verify serial number removed from plant inventory
4. Asset verification: AS03 → individual asset or sub-number → asset value should reflect the specific unit; compare with physical audit results
5. Warranty/maintenance history: IQ03 → serial number → maintenance orders, notification history; confirms end-to-end traceability

**See also:** `cross-module/playbooks.md` Playbook 8 (Serial Number Management complete walkthrough). `modules/mm/mm-advanced.md` DT 8 (serial number decision tree).

---

## Pattern 11: Split Valuation for Multiple Stock Categories

**Business requirement:** Value the same material differently based on procurement type (in-house vs. purchased) or origin (domestic vs. imported), while keeping it as a single material number. Financial reporting requires visibility into different cost layers within the same material.

**SAP ECC 6 approach:** Activate split valuation at the client level (OMWC) and define valuation categories and valuation types. Each valuation type gets its own accounting 1 data (price, valuation class, stock account). The same material number has multiple valuation types (e.g., "IN-HOUSE" and "PURCHASED") each with different GL accounts in OBYC via separate valuation classes.

**When to use:** Material produced internally has different standard cost than the same material purchased externally; material valued differently by country of origin for customs or transfer pricing; gold or precious metal inventory valued by quality grade.

**When NOT to use:** If all stock of the material should be valued at the same price (use standard material master accounting — no split valuation needed). If different materials should be used instead of different valuation types (e.g., truly different specifications warrant different material numbers).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| MM | Activate split valuation at client level | OMWC — activate split valuation globally (CRITICAL: cannot deactivate after use) |
| MM | Define valuation category | OMWC — valuation category key (e.g., "H" for origin) |
| MM | Define valuation types | OMWC — valuation types per category (e.g., "DOMESTIC" and "IMPORT") |
| MM | Assign valuation types to material per plant | MM02 → Accounting 1 → select valuation type; SAP creates separate MBEW record per valuation type |
| FI | OBYC entries per valuation class | OBYC → BSX and other keys — separate GL accounts per valuation type's valuation class |
| CO | Standard cost per valuation type | CK11N must be run separately for each valuation type that uses standard price (S) |

### Master Data Setup

- **Valuation category (OMWC):** High-level grouping (e.g., "H" = by origin); assigned to material type or plant
- **Valuation types (OMWC):** Specific values within the category (e.g., "DOMESTIC", "IMPORT"); each becomes a separate MBEW record (material + plant + valuation type)
- **Material master per valuation type:** Accounting 1 view maintained separately for each valuation type — different valuation class, different price, different price control (can mix S and V)
- **OBYC per valuation class:** Each valuation type's valuation class must have OBYC entries for BSX (stock account) — different GL accounts enable separate reporting by valuation type

### Testing Steps

1. Verify split valuation activation: OMWC → confirm valuation category and types exist; check material master has valuation type field visible in Accounting 1
2. Post GR specifying valuation type: MIGO movement 101 → on batch tab or header, specify valuation type (e.g., "DOMESTIC") → verify MBEW record shows stock for that specific valuation type
3. Verify separate GL posting: FBL3N → confirm inventory GL account corresponds to the valuation class for the selected valuation type (not the same account as the other valuation type)
4. Check split valuation stock: MB52 → shows stock quantities per valuation type within the same material + plant
5. Run product cost estimate per type: CK11N → for each valuation type separately → verify different standard prices can be maintained

**See also:** `cross-module/playbooks.md` Playbook 5 (Split Valuation complete walkthrough). `modules/mm/mm-advanced.md` DT 6 (split valuation configuration decision tree with SPRO detail). `modules/fi/account-determination.md` for OBYC BSX configuration.

---

## Pattern 12: Customer Returns and Credit Processing

**Business requirement:** Handle customer returns of previously sold goods: receive the returned goods back into inventory (or to inspection/scrapping), issue a credit note to the customer for the returned amount, and update financial records to reverse the original revenue and COGS.

**SAP ECC 6 approach:** Use SD document type RE (returns order) in VA01, which triggers return delivery type LR. Goods receipt from the customer posts movement type 651 (returns from customer). Billing type RE (returns credit) creates the credit memo in VF01, reversing the original revenue posting via VKOA. COGS is reversed via OBYC at goods receipt (651 posting). The complete reverse trace: RE order → LR delivery → GR 651 → credit memo RE → FI reversal.

**When to use:** Customer returns goods that were previously billed; warranty claims; quality complaints where the customer receives credit; end-of-season returns in retail.

**When NOT to use:** Consignment pickups (use consignment KR order type — Pattern 3). Goods never shipped to the customer (cancel the billing document instead with VF11). Internal material movements that don't involve customers.

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|-------------|-------------------|
| SD | Returns order type RE configuration | VOV8 — document type RE; delivery type LR; billing type RE |
| SD | Item category REN for returns | VOV7 — billing relevance allows credit memo; negative billing |
| SD | Copy control for returns order to credit memo | VTAA (RE → credit memo request) or VTAF (billing → credit memo) |
| SD | Return delivery type LR | OVLK — movement type 651 at goods receipt |
| FI | VKOA for credit memo (ERL reversal) | VKOA → same ERL account key; credit memo reverses via billing type RE |
| FI | OBYC for returns GR (BSX/GBB reversal) | Movement type 651 → BSX (Dr inventory) + GBB (Cr — reverses COGS) |

### Master Data Setup

- **Customer master (KNVV):** Standard customer; returns are processed using the same sales area data as the original sale
- **Material master (Accounting 1):** No special setup; returns GR (651) uses the same BSX/GBB OBYC keys as the original GI (601), but reverses the Dr/Cr
- **Returns order reason:** VA01 RE → enter return reason (configured in SPRO → SD → Sales → Define Order Reasons); used for quality analysis reporting
- **Credit memo approval:** VOV8 can configure billing block on RE orders requiring sales manager approval before credit memo is issued (VA02 to release block)

### Testing Steps

1. Create returns order: VA01 document type RE → reference original billing document or order → item category REN proposed → verify correct return quantity and reason
2. Create return delivery: VL01N referencing returns order → delivery type LR; goods not yet received
3. Post customer GR: VL02N → "Post Goods Receipt" → movement type 651 → verify MMBE stock increased; FBL3N shows: Dr Inventory (BSX) / Cr COGS reversal (GBB)
4. Create credit memo: VF01 → billing type RE → verify FI document: Dr Revenue (ERL) / Cr Customer → customer open item is a credit in FBL5N
5. Reconcile document flow: VF03 → Environment → Document Flow → complete chain: RE order → LR delivery → material document (651) → credit memo → FI document; all documents linked

**See also:** `cross-module/mm-sd-integration.md` Section Returns for the cross-module document flow. `modules/sd/processes.md` Section 2 (Returns). `modules/sd/sd-advanced.md` troubleshooting for returns-related errors.

---

## S/4HANA Differences

The following ECC 6 behaviors relevant to these patterns differ in S/4HANA. Patterns above document ECC 6 behavior only; this section is for disambiguation.

| Pattern | ECC 6 Behavior | S/4HANA Change |
|---------|----------------|----------------|
| Pattern 1 (MTS/Standard Costing) | Material Ledger optional; standard price only if activated | Material Ledger mandatory; actual costing always available; CKMLCP required monthly |
| Pattern 2 (Engineer-to-Order) | Internal orders with separate CE master data (KA01) | GL accounts serve as cost elements; KA01 obsolete; same settlement logic |
| Pattern 3 (Consignment) | Material documents in MKPF/MSEG; movement types 101K/201K/631-634 unchanged | Same movement types; MATDOC replaces MKPF/MSEG; consignment business process unchanged |
| Pattern 4 (Third-Party) | TAS item category; statistical GR; two independent invoices | Same item category and process; Fiori apps available for PO approval; core unchanged |
| Pattern 5 (Subcontracting) | 541/543 movement types; BOM explosion in subcontracting PO | Same movement types; MATDOC replaces MKPF/MSEG; process unchanged |
| Pattern 6 (Intercompany) | Reconciliation ledger (COFIT/COFIS) for cross-CC CO; KALC creates intercompany FI entries | Reconciliation ledger eliminated; ACDOCA handles cross-CC natively; KALC no longer needed |
| Pattern 7 (Overhead Allocation) | KSU5/KSV5 assessment/distribution; secondary CEs in CO only | Same process; secondary CEs still exist; CO data in ACDOCA instead of COBK/COEP |
| Pattern 8 (Investment Capitalization) | Internal order → AUC → asset; KO88 + AIAB/AIBU | Same investment order logic; ACDOCA replaces COBK/COEP; asset accounting unchanged |
| Pattern 9 (Batch Management) | Batch master in MCH1/MCHA; FEFO in batch determination | Same batch management logic; batch data in MATDOC instead of MKPF/MSEG |
| Pattern 10 (Serial Numbers) | Serial number in EQUI/EQUZ; equipment-asset link via ANLZ-ILOAN | Same serial number process; technical object tables unchanged |
| Pattern 11 (Split Valuation) | Separate MBEW record per valuation type; OMWC activation | Same split valuation logic; MATDOC replaces MKPF/MSEG; ML always active affects costing |
| Pattern 12 (Returns/Credit) | Returns via RE/LR/651; MKPF/MSEG for returns GR | Same document flow; MATDOC replaces MKPF/MSEG; customer master → Business Partner |
