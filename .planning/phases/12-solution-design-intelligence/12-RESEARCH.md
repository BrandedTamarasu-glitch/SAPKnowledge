# Phase 12: Solution Design Intelligence - Research

**Researched:** 2026-02-18
**Domain:** SAP ECC 6.0 Knowledge Base content authoring — solution design patterns, scenario playbooks, and operational checklists
**Confidence:** HIGH (primary source is the existing knowledge base itself; all content is first-party)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Design Pattern Depth**
- Implementation guide format: business requirement → recommended approach → T-codes to configure → master data setup → testing steps (cookbook style)
- Focus on cross-module scenarios (requirements that span MM/SD/FI/CO), not single-module config dilemmas
- Build on existing module decision trees: design patterns are the higher-level "when to use what" layer, pointing to module decision trees for config-level choices
- Target 10-15 patterns covering the most common cross-module business requirements

**Scenario Playbook Scope**
- All eight scenarios from roadmap: consignment, intercompany sales, third-party processing, subcontracting, split valuation, special procurement, batch management, serial numbers
- Playbooks are deep-dive implementation walkthroughs: full config steps, master data setup, cross-module perspective
- Each playbook includes 2-3 test scenarios showing how to verify the config works (e.g., "Create consignment fill order with VA01, verify stock at customer site with MB52")
- Playbooks are the definitive deep-dive for their scenario; existing module mentions (SD processes.md, MM processes.md) become brief introductions pointing to the playbook
- Playbooks differ from design patterns: patterns give overview + decision, playbooks give full implementation walkthrough

**Operational Checklists**
- Checklists are the actionable operator version of the R2R E2E flow from Phase 11 (different audience: operator vs architect)
- Cover both month-end and year-end close (year-end adds fiscal year rollover, balance carryforward, depreciation close)
- Include relative timing guidance using business days (Day 1, Day 2, Day 3) — sequence and relative timing are universal even though actual dates vary
- Markdown checkbox format: `- [ ] Step 1: Run MMPV (T-code) — close MM posting period`

**File Organization**
- All content lives in cross-module/ alongside the E2E files from Phase 11
- Design patterns: single file cross-module/design-patterns.md with all 10-15 patterns as sections
- Playbooks: single file cross-module/playbooks.md with all 8 scenarios as sections (grouped: 4 process + 4 config)
- Checklists: separate from R2R (different audience); location in cross-module/
- Full navigation update: routing table rows for design patterns, playbooks, and checklists; cross-module/CLAUDE.md index updated

### Claude's Discretion

- Exact selection of which 10-15 design patterns to include
- How to structure each playbook section internally (step ordering, level of config detail)
- Whether checklists are one file (month-end + year-end) or two separate files
- How much to expand existing module process file references vs keeping playbooks self-contained
- Whether to update existing module process files to point to playbooks

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SOLN-01 | Solution design patterns: cross-module implementation guides (business requirement → SAP ECC 6 approach → T-codes → master data → testing) | Pattern catalog below identifies 12 specific patterns sourced from gaps in the existing knowledge base |
| SOLN-02 | Process scenario playbooks: consignment, intercompany sales, third-party processing, subcontracting | Deep coverage already exists in mm-sd-integration.md (foundation level); playbooks must add full config walkthroughs, master data, test scenarios |
| SOLN-03 | Config scenario playbooks: split valuation, special procurement, batch management, serial numbers | Decision trees already in mm-advanced.md; playbooks must synthesize into complete implementation walkthroughs with cross-module perspective |
| SOLN-04 | Operational checklists: month-end and year-end close with checkbox format and business-day timing | R2R file covers architect view; checklists must be operator-oriented (executable, T-code specific, timed) |
</phase_requirements>

---

## Summary

Phase 12 is a pure content authoring phase — there is no software to build, no libraries to install, no APIs to configure. The "research" domain is the existing SAP ECC 6.0 Knowledge Base itself, and the primary finding is a precise gap analysis: what is already documented in Phases 1-11 versus what Phase 12 must add.

The existing knowledge base has excellent breadth across all four modules (MM, SD, FI, CO) with detailed T-code references, SPRO configuration paths, process flows, and module-level decision trees. However, it has two structural gaps that Phase 12 fills:

1. **No synthesis layer.** The modules document individual capabilities in isolation. A consultant facing a business requirement like "we need consignment stock at customer sites" must mentally assemble the puzzle from SD processes.md (billing approach), mm-sd-integration.md (movement types), and mm-advanced.md (stock type management). The playbooks and design patterns eliminate this assembly burden by providing pre-synthesized, cross-module implementation guidance.

2. **No operator-facing checklists.** The record-to-report.md file documents the period-end sequence at the architect level (what steps exist, what they depend on, why the sequence matters). An operator running month-end close needs something different: a checkbox list with specific T-codes, ordered by business day, that can be executed without understanding the architecture behind it.

The patterns.md stub files in all four modules (`modules/mm/patterns.md`, `modules/sd/patterns.md`, `modules/fi/patterns.md`, `modules/co/patterns.md`) all say "To be populated in Phase X" — confirming this has been the intended capstone phase. The locked decision places all patterns in `cross-module/design-patterns.md` rather than module-level files, which is appropriate since the patterns are explicitly cross-module scenarios.

**Primary recommendation:** Write three new files in `cross-module/` (design-patterns.md, playbooks.md, and checklists.md or two checklist files), then update cross-module/CLAUDE.md and sap-routing.md navigation. The planner should structure this as four sequential tasks matching the four SOLN requirements.

---

## Content Gap Analysis (The Knowledge Base "Standard Stack")

Since this is a content authoring phase rather than software development, the "standard stack" is the established content patterns from Phases 1-11, and the "architecture" is the gap analysis between what exists and what Phase 12 must produce.

### What Already Exists (The Foundation)

| File | Coverage Relevant to Phase 12 |
|------|-------------------------------|
| `cross-module/mm-sd-integration.md` | Foundation-level coverage of consignment (movement types 631-634), third-party (TAS item cat, auto-PR), subcontracting (541/543), STOs, intercompany |
| `cross-module/record-to-report.md` | Full R2R period-end sequence — architect view; checklists will be the operator version |
| `modules/sd/processes.md` | Brief coverage: 4-scenario consignment table, 5-step third-party summary, standard O2C |
| `modules/mm/mm-advanced.md` | Decision trees 6-9: split valuation (OMWC), batch management (OISO), serial numbers, subcontracting/special stock |
| `modules/mm/processes.md` | Standard P2P, physical inventory; no consignment |
| `modules/fi/processes.md` | FI period-end close sequence, AR/AP processing |
| `modules/co/processes.md` | Full CO period-end sequence (9 steps with dependencies) |
| `modules/co/co-advanced.md` | CO-FI integration, reconciliation, 10 decision trees |

### What Phase 12 Must Add

| Deliverable | Gap Description | Depth Required |
|-------------|----------------|----------------|
| `cross-module/design-patterns.md` | No cross-module "when to use what" layer exists; module decision trees are config-level only | 10-15 patterns: business requirement → approach → T-codes → master data → testing |
| `cross-module/playbooks.md` | Existing coverage is introductory (brief tables, 4-6 steps); no full implementation walkthroughs | Deep-dive: full SPRO paths, master data setup across modules, 2-3 test scenarios per playbook |
| `cross-module/checklists.md` | R2R is architect view; no operator checklist exists | Checkbox format, business-day timing, T-codes, month-end and year-end |

### Existing Coverage Depth vs Playbook Requirement

| Scenario | What Exists | What Playbook Adds |
|----------|-------------|-------------------|
| Consignment | mm-sd-integration.md: movement types 631-634, billing trigger; sd/processes.md: 4-scenario table | Full SPRO config (consignment info records, pricing), master data (special stock indicator, consignment partner functions), full SD billing configuration, inventory reporting (MB52 special stock), reconciliation process |
| Third-party | mm-sd-integration.md: TAS item cat, auto-PR, statistical GR; sd/processes.md: 5-step summary | Full item category config (TAS in SPRO), copy control requirements, vendor master (OA partner functions), statistical vs actual goods receipt decision, CO account assignment, billing document type |
| Subcontracting | mm-advanced.md: DT 9 (541/543 mechanics); mm-sd-integration.md: brief mention | Full BOM setup for subcontracting (MARC-SOBSL=30), purchase info records for subcontracting, 541 transfer to subcontractor + 543 component consumption, GR handling, settlement and CO perspective |
| Intercompany sales | mm-sd-integration.md: brief STO vs IC billing comparison | Full IC billing setup: partner functions, pricing procedure (IV), document flow (OR → NL → NLN → IV → RE → REBR), intercompany pricing, FI account determination (VKOA for IC revenue), CO-PA treatment |
| Split valuation | mm-advanced.md: DT 6 (OMWC config chain) | Cross-module: how split valuation affects OBYC (separate stock accounts per valuation type), production order integration, Material Ledger interaction, reporting implications (MB52 by valuation type) |
| Special procurement | mm-advanced.md: DT 9 partial | Complete special procurement keys (MARC-SOBSL): 10=production in another plant, 20=phantom assembly, 30=subcontracting, 40=stock transfer, 50=WM-managed; MRP interaction, account assignment |
| Batch management | mm-advanced.md: DT 7 (OISO activation, MARC-XCHPF) | Full config: batch classification (CT04 characteristics), batch search strategies (LS11), shelf life management (MHDRST), SD integration (batch split in delivery, picking), FI account determination for batch-specific pricing |
| Serial numbers | mm-advanced.md: DT 8 (OISO profile activation) | Serial number profiles (MARC-SERAIL via SPRO), equipment master (IE01 for assets), SD serialization (delivery serial numbers), FI asset integration, PM integration overview |

---

## Architecture Patterns

This section guides how the planner should structure the three deliverable files.

### Pattern 1: Design Patterns File Structure

**What:** `cross-module/design-patterns.md` contains 10-15 named patterns, each following the cookbook format specified in CONTEXT.md.

**Recommended pattern format:**
```markdown
## Pattern N: [Descriptive Business Name]

**Business requirement:** [What the business needs, in business terms]
**SAP ECC 6 approach:** [The recommended implementation approach, 1-2 sentences]
**When to use:** [Trigger conditions]
**When NOT to use:** [Alternative scenarios]

### Configuration Summary
| Module | Config Step | T-code / SPRO Path |
|--------|------------|-------------------|
| MM | ... | ... |
| SD | ... | ... |
| FI | ... | ... |

### Master Data Setup
[What master data must exist and how it interconnects]

### Testing Steps
1. [Test step with T-code]
2. [Verify result]

**See also:** [Cross-reference to playbook if deeper dive needed]
```

**Recommended 12 patterns (within the 10-15 range):**

| # | Pattern Name | Business Need | Modules |
|---|-------------|---------------|---------|
| 1 | Make-to-Stock Production with Standard Costing | Manufacture standard products for inventory | MM, CO (PP overview) |
| 2 | Engineer-to-Order with Project Cost Collection | Custom products with project-based cost tracking | MM, CO (internal orders / WBS) |
| 3 | Consignment Stock Management | Vendor-owned stock in your warehouse, or your stock at customer sites | MM, SD, FI |
| 4 | Third-Party Drop Shipment | Fulfill customer orders via direct vendor delivery | MM, SD, FI |
| 5 | Subcontracting (Toll Processing) | Send components to vendor for processing | MM, FI |
| 6 | Intercompany Sales / Stock Transfer | Transfer goods between company codes with legal billing | MM, SD, FI |
| 7 | Overhead Allocation to Products | Allocate overhead cost centers to product cost centers | CO (CCA, CK11N) |
| 8 | Investment Project Capitalization | Collect construction costs on internal orders and capitalize as assets | CO, FI (AM) |
| 9 | Batch-Managed Inventory with Shelf Life | Track inventory by batch with expiry dates | MM, SD |
| 10 | Serial Number Tracking to Asset Register | Track serialized equipment from goods receipt to fixed asset | MM, FI (AM) |
| 11 | Split Valuation for Multiple Stock Categories | Value same material differently by procurement type or origin | MM, FI |
| 12 | Customer Returns and Credit Processing | Handle returns with inspection, re-stocking, and credit note | MM, SD, FI |

### Pattern 2: Playbooks File Structure

**What:** `cross-module/playbooks.md` contains all 8 scenarios in two groups, each as a major section with consistent internal structure.

**Recommended section format:**
```markdown
## Playbook N: [Scenario Name]

> [1-sentence positioning: what business problem this solves and what distinguishes it from standard flow]

### Business Context
[When to use this process; what distinguishes it from the standard flow it replaces]

### Prerequisites
- [System requirement]
- [Master data that must exist first]

### Configuration Walkthrough

#### Step 1: [Module] — [Config Area]
**T-code / SPRO path:** ...
**Settings:** ...
**Gotcha:** ...

#### Step 2: ...

### Master Data Setup
[What master data objects must be created and how they link across modules]

### Process Flow
[Step-by-step transaction sequence for the end-to-end scenario]

### Test Scenarios

**Test 1: [Name]**
1. [Execute T-code with specific values]
2. [Verify result using T-code]
3. [Check cross-module result]

**Test 2: ...**

### Cross-Module Perspective
[FI account assignment, CO object assignment, key integration touchpoints]

### Common Pitfalls
- [Pitfall]: [Resolution]
```

**File grouping:**
```
## Process Playbooks
  Playbook 1: Consignment Stock
  Playbook 2: Intercompany Sales
  Playbook 3: Third-Party Drop Shipment
  Playbook 4: Subcontracting (Toll Processing)

## Configuration Playbooks
  Playbook 5: Split Valuation
  Playbook 6: Special Procurement Keys
  Playbook 7: Batch Management
  Playbook 8: Serial Number Management
```

### Pattern 3: Checklists File Structure

**Recommendation:** One file (`cross-module/checklists.md`) with two major sections — month-end and year-end. Year-end = month-end steps + additional year-end-only steps. This is preferable to two files because most steps are shared; duplication would create maintenance problems.

**Recommended checklist format:**
```markdown
## Month-End Close Checklist

> Use this checklist on the last business day of each period. Complete each module's steps before moving to the next module's steps. CO period-end cannot start until MM and FI period-end are complete.

### Day -5 to Day -3 (Pre-Close Preparation)
- [ ] Verify all goods receipts for the period are posted (MIGO)
- [ ] Verify all vendor invoices for the period are posted or accrued (MIRO / FBS1)
...

### Day 1 (MM Period-End)
- [ ] Run MMPV — close current MM posting period
...

### Day 2 (FI Period-End)
- [ ] Run F.05 — foreign currency revaluation
...

### Day 3 (CO Period-End)
- [ ] Run KB61 — repost any CO mis-postings
- [ ] Run KGI2 — calculate actual overhead
- [ ] Run KSU5 — execute assessment cycles
- [ ] Run KSV5 — execute distribution cycles
- [ ] Run KO88 — settle internal orders (test mode first, then live)
- [ ] Run CO88 — settle production orders (if PP active)
- [ ] Run KSII — calculate actual activity prices
- [ ] Run KALC — reconciliation posting (if multi-company-code CA)
...
```

**Business-day timing structure (month-end):**

| Timing | Module | Key Steps |
|--------|--------|-----------|
| Day -5 to -3 | All | Pre-close: verify completeness, post accruals, resolve open items |
| Day 1 | MM | MMPV period close; CKMLCP Material Ledger (if active) |
| Day 1-2 | FI | F.05 revaluation; AFAB depreciation; FBS1 accruals; clear open items |
| Day 2-3 | CO | KB61 → KGI2 → KSU5/KSV5 → KO88/CO88 → KSII → KALC → lock |
| Day 3-4 | All | Verification reports; management reporting; period lock confirmation |

**Year-end additions to month-end:**

| Additional Step | T-code | Module | Timing |
|----------------|--------|--------|--------|
| Balance carryforward (GL) | FAGLGVTR | FI | After final CO period close |
| Balance carryforward (AR/AP) | F.07 / F.16 | FI-AR, FI-AP | After final CO close |
| Asset fiscal year close | AJAB | FI-AM | After depreciation fully posted |
| CO fiscal year close | OKP1 lock all periods | CO | After all CO period-end complete |
| Open new FI period (new FY) | OB52 | FI | New fiscal year period 1 |
| Open new MM period (new FY) | OMSY / MMPV | MM | New fiscal year period 1 |
| Copy planning version (if needed) | KP97 / KP98 | CO | New fiscal year planning |

---

## Don't Recreate What Exists

| Content Area | Don't Rewrite | Reference Instead |
|-------------|---------------|-----------------|
| Movement type details for consignment (631-634) | Covered in mm-sd-integration.md | Cross-reference with "See also: cross-module/mm-sd-integration.md" |
| Assessment vs distribution decision | Fully covered in co/processes.md + co/co-advanced.md DT 1 | Cross-reference |
| CK11N / CK24 product costing steps | Fully covered in co/processes.md Section 3 | Cross-reference |
| SPRO path for OMWC (split valuation) | Covered in mm/mm-advanced.md DT 6 | Cross-reference — playbook adds cross-module perspective |
| OKB9 default account assignment config | Covered in co/config-spro.md + co/co-advanced.md Symptom 1 | Cross-reference |
| Period-end CO sequence (9 steps) | Covered in co/processes.md Section 5 + co/integration.md Section 5 | Checklists reference, don't repeat explanation |

**Key principle for playbooks:** The playbook is a synthesis layer, not a duplication layer. Point to module files for config detail (e.g., "Configure the settlement profile per `modules/co/config-spro.md` Section 4.3"), but add the cross-module perspective and the test scenarios that don't exist anywhere else.

---

## Common Pitfalls (Content Authoring)

### Pitfall 1: Playbooks That Duplicate Module Content Instead of Synthesizing It

**What goes wrong:** The playbook writer copies T-code details and SPRO paths verbatim from module files, creating a longer file that adds no new value.

**How to avoid:** Each playbook section should answer questions the module files do NOT answer: "How does SD configuration interact with MM stock type management?" "What FI account determination is triggered when the consignment fill order is billed?" "How do I verify this works end-to-end?"

**The test:** If a section of a playbook could be found word-for-word in a module file, replace it with a cross-reference.

### Pitfall 2: Design Patterns Too Granular (Config-Level)

**What goes wrong:** Patterns become config how-to guides: "Pattern 7: How to configure settlement profiles in OKO7." This duplicates SPRO content.

**How to avoid:** Patterns must start with a business requirement (not a config task) and must span at least two modules. "A business requirement to capitalize internal project costs as fixed assets" is a pattern; "how to configure settlement profiles" is config documentation that already exists.

### Pitfall 3: Checklists Missing Actual T-Codes

**What goes wrong:** Checklist steps are written as vague descriptions: "- [ ] Close the MM period." The operator cannot execute this without looking up the T-code.

**How to avoid:** Every checklist step includes the T-code in parentheses or inline: "- [ ] Close MM posting period (MMPV)". This is the key difference between the checklist (operator) and R2R (architect). The format specified in CONTEXT.md demonstrates this: `- [ ] Step 1: Run MMPV (T-code) — close MM posting period`.

### Pitfall 4: Playbooks Without Test Scenarios

**What goes wrong:** The playbook documents config and master data but doesn't tell the consultant how to know if it works.

**How to avoid:** Every playbook must include 2-3 concrete test scenarios that are testable in a sandbox. Test scenarios should specify starting transaction, input values (or ranges), and verification transaction with expected result. Example: "Create consignment fill order: VA01, order type ZKOB (or KB), ship-to party with consignment handling. After saving, verify MB52 shows the material in special stock type K at the customer."

### Pitfall 5: Year-End Checklist Missing Balance Carryforward Steps

**What goes wrong:** Year-end checklist is just month-end with "also close asset fiscal year." The critical balance carryforward steps (FAGLGVTR, F.07, F.16) are omitted.

**How to avoid:** The research explicitly identifies these steps: FAGLGVTR (GL balance carryforward), F.07 (AR balance carryforward), F.16 (AP balance carryforward), AJAB (asset year close). All must appear in the year-end-specific section.

### Pitfall 6: Navigation Not Updated

**What goes wrong:** The new files exist but sap-routing.md and cross-module/CLAUDE.md don't reference them, making them invisible to users.

**How to avoid:** The last task in the plan should update both navigation files. This is a locked decision in CONTEXT.md and must not be omitted.

---

## Code Examples

These are the key content patterns that Phase 12 must follow.

### Example 1: Design Pattern Entry (cross-module/design-patterns.md)

```markdown
## Pattern 3: Consignment Stock Management

**Business requirement:** Track inventory that remains vendor-owned while stored in your warehouse (vendor consignment), OR track your own inventory stored at customer sites (customer consignment) with billing triggered at actual consumption.

**SAP ECC 6 approach:** Use special stock indicator K (vendor consignment) or W (customer consignment). Goods movements 101K/201K for vendor consignment; 631/632/633/634 for customer consignment. Billing in SD is triggered by movement type 633 (issue from consignment).

**When to use:** Vendor consignment — vendor retains ownership until you withdraw/consume the stock. Customer consignment — you retain ownership until the customer reports consumption.

**When NOT to use:** If ownership transfers immediately on goods receipt (standard PO), use standard MM procurement (no special stock indicator needed).

### Configuration Summary

| Module | Config Step | T-code / SPRO Path |
|--------|------------|-------------------|
| MM | Consignment info record | ME11/ME12 (info record with consignment price) |
| MM | Allow consignment stock in plant | OMSY / plant parameters |
| SD | Billing document for consignment issue | VOFA (billing type for consignment) |
| SD | Item category determination for consignment | VOV4 (item categories KB, KE, KA, KR) |
| FI | GR/IR account for consignment liability | OBYC (transaction WRX) |

### Master Data Setup
- Vendor master: no special setup needed; consignment controlled by info record type
- Consignment info record (ME11): vendor + material + plant, info category = "Consignment," price per unit
- Customer master for customer consignment: standard; consignment behavior controlled by SD item categories
- Material master: no special field needed for consignment in MM; SD requires special stock flag if customer consignment

### Testing Steps
1. Vendor consignment GR: MIGO movement type 101, special stock = K; verify MB52 shows stock in "Vendor Consignment" column
2. Consignment withdrawal: MIGO movement type 201K; verify vendor liability posting in FBL1N
3. Customer consignment: VA01 with consignment fill-up order; verify MB52 shows stock at customer site

**See also:** `cross-module/playbooks.md` Playbook 1 for the complete implementation walkthrough with full SPRO paths.
```

### Example 2: Playbook Section (cross-module/playbooks.md)

```markdown
## Playbook 1: Consignment Stock

> Consignment enables two distinct business models: vendor-managed inventory in your warehouse (vendor consignment) and your inventory at customer sites billed at consumption (customer consignment). Both use special stock type K but with opposite ownership direction.

### Business Context
Standard procurement transfers ownership at goods receipt. Standard sales transfers ownership at delivery. Consignment defers ownership transfer to a later point (withdrawal for vendor consignment; consumption confirmation for customer consignment).

### Prerequisites
- MM module active with plant and storage location configured
- For customer consignment: SD module active, sales organization and distribution channel assigned

### Configuration Walkthrough

#### Step 1: MM — Consignment Info Record (Vendor Consignment Only)
**T-code:** ME11
**Settings:** Info category = Consignment; vendor + material + purchasing org + plant; enter consignment price per unit (the price paid when you withdraw from consignment)
**Gotcha:** The consignment info record price is used for liability posting when stock is withdrawn (201K), not at goods receipt. At GR (101K), no vendor liability is created — the vendor owns the stock.

#### Step 2: SD — Item Category Configuration (Customer Consignment)
**SPRO Path:** Sales and Distribution → Sales → Sales Documents → Sales Item → Define Item Categories
**Item categories for customer consignment:**
- KB (Consignment Fill-Up): sends stock to customer site; no billing at this point
- KE (Consignment Issue): customer reports consumption; triggers billing
- KA (Consignment Pick-Up): retrieves unsold stock from customer; no billing
- KR (Consignment Returns): customer returns damaged goods; credit memo
...

### Test Scenarios

**Test 1: Vendor Consignment — Receive and Withdraw**
1. Create consignment PO: ME21N with consignment info record (system defaults consignment PO type)
2. Post GR: MIGO movement 101K — verify MB52 shows stock in "Vendor" special stock column; FBL1N shows NO vendor liability posted
3. Withdraw from consignment: MIGO movement 201K — verify FBL1N shows vendor liability for the withdrawn quantity

**Test 2: Customer Consignment — Send and Bill**
1. Create consignment fill-up order: VA01, order type ZKOB; complete delivery (VL01N), GI posts movement 631
2. Verify MB52: material shows in "Customer" special stock at ship-to party — not in your unrestricted stock
3. Create consignment issue (consumption confirmed): VA01, order type ZKOR; delivery posts movement 633; verify billing document created in VF01 for the consumed quantity
```

### Example 3: Checklist Entry (cross-module/checklists.md)

```markdown
## Month-End Close Checklist

### Day -3 (Pre-Close Preparation — MM)
- [ ] Verify all goods receipts for the period are posted (MIGO or ME2M list)
- [ ] Verify all goods issues and transfers are posted (MIGO)
- [ ] Confirm with AP that all vendor invoices for the period are posted or an accrual is planned (MIRO / FBS1)
- [ ] Run MMBE — check for any negative stock that would prevent period close

### Day 1 (MM Period-End)
- [ ] Run MMPV — advance MM period (closes the current period to MM postings)
- [ ] If Material Ledger active: run CKMLCP — actual costing close for the period

### Day 1-2 (FI Period-End)
- [ ] Run AFAB — execute depreciation for the period (verify depreciation area parameters)
- [ ] Post period-end accruals: FBS1 (reversing accruals for expenses not yet invoiced)
- [ ] Run F.05 — foreign currency revaluation (if multi-currency)
- [ ] Clear open items: F-32 (AR), F-44 (AP) — clear matched items to clean aging reports
- [ ] Run FAGLB03 — verify GL balances before CO allocations begin

### Day 2-3 (CO Period-End)
- [ ] Run KB61 — repost any CO line item mis-assignments identified during the period
- [ ] Run KGI2 — calculate actual overhead (applies overhead surcharges to orders)
- [ ] Run KSU5 — execute assessment cycles in TEST MODE first; review results; then execute LIVE
- [ ] Run KSV5 — execute distribution cycles in TEST MODE first; review results; then execute LIVE
- [ ] Run KO88 — settle internal orders in TEST MODE first; review for missing settlement rules; then execute LIVE
- [ ] Run CO88 — settle production orders (if PP module active)
- [ ] Run KSII — calculate actual activity prices
- [ ] Run KALC — reconciliation posting for cross-company-code CO allocations (if multi-CC controlling area)
- [ ] Lock CO period: OKP1 — set period status to "2 - Locked for all users"

### Day 3-4 (Verification and Reporting)
- [ ] Run S_ALR_87013611 — verify cost center plan/actual comparison; investigate significant variances
- [ ] Run KSB1 — verify catch-all cost centers have zero or minimal balance (all costs allocated)
- [ ] Run KE5Z — verify PCA totals match FI (FAGLB03); investigate any gap (missing profit center assignments)
- [ ] Distribute management reports to cost center owners
```

---

## Navigation Updates Required

The plan must include a task to update navigation. These are the exact changes required:

### cross-module/CLAUDE.md — Add 3 rows to the File Index table

Current table has 4 files: procure-to-pay.md, order-to-cash.md, record-to-report.md, mm-sd-integration.md.

Add:
```markdown
| @design-patterns.md | 12 cross-module solution design patterns (business requirement → SAP approach → T-codes → master data → testing) | Designing a solution for a complex cross-module business requirement; choosing between approaches |
| @playbooks.md | 8 scenario playbooks: consignment, intercompany, third-party, subcontracting, split valuation, special procurement, batch management, serial numbers | Implementing a specific complex scenario end-to-end; full config + master data + test scenarios |
| @checklists.md | Month-end and year-end close checklists (operator-facing; checkbox format; business-day timing; specific T-codes) | Running period-end close; knowing the sequence and T-codes for each close step |
```

### sap-routing.md — Add 3 rows to the Module Routing table

```markdown
| Solution design patterns, choosing approach for business requirement | Cross-module | `cross-module/design-patterns.md` |
| Scenario playbooks: consignment, intercompany, third-party, subcontracting, split valuation, batch, serial | Cross-module | `cross-module/playbooks.md` |
| Month-end close, year-end close checklists, period-end steps | Cross-module | `cross-module/checklists.md` |
```

---

## Open Questions

1. **Stub patterns.md files in module directories**
   - What we know: All four modules have `patterns.md` stubs created as placeholders
   - What's unclear: Should Phase 12 populate these stubs (pointing to design-patterns.md) or leave them as-is?
   - Recommendation: Update the stubs with a single-sentence redirect: "Solution design patterns for cross-module CO scenarios are documented in `cross-module/design-patterns.md`." This is low-effort and makes navigation consistent. Mark as Claude's discretion in the plan.

2. **Whether to update existing module process files to point to playbooks**
   - What we know: CONTEXT.md identifies this as Claude's discretion
   - What's unclear: The locked decision says "Playbooks are the definitive deep-dive for their scenario; existing module mentions (SD processes.md, MM processes.md) become brief introductions pointing to the playbook"
   - Recommendation: Yes, update the brief existing coverage in sd/processes.md (consignment and third-party sections) to add a "See also: cross-module/playbooks.md Playbook N for the complete implementation walkthrough." This is a minor edit, not a rewrite. MM files need less attention since mm-sd-integration.md already has the cross-reference language.

3. **One vs two checklist files**
   - What we know: CONTEXT.md leaves this to Claude's discretion
   - Recommendation: One file (`cross-module/checklists.md`) with two sections (month-end and year-end). Rationale: the year-end section is month-end plus additional steps; keeping them in one file prevents drift between the shared steps and makes the relationship explicit. If the file becomes very long (>300 lines), split.

---

## Sources

### Primary (HIGH confidence)

All findings derive from reading the existing knowledge base files directly — first-party sources with no staleness risk.

- `cross-module/mm-sd-integration.md` — consignment movement types, third-party flow, subcontracting, intercompany; read in full
- `cross-module/record-to-report.md` — R2R period-end sequence; basis for checklist timing
- `cross-module/CLAUDE.md` — current file index; navigation update scope confirmed
- `modules/sd/processes.md` — existing consignment and third-party coverage depth assessed
- `modules/mm/mm-advanced.md` — DTs 6-9 confirmed (split valuation, batch, serial, subcontracting)
- `modules/co/processes.md` — period-end 9-step sequence; basis for CO section of checklist
- `modules/co/co-advanced.md` — CO-FI integration, reconciliation; confirms cross-module synthesis needed
- `modules/co/integration.md` — CO period-end timing and dependencies
- `modules/fi/processes.md` — FI period-end steps for checklist Day 1-2
- `.planning/phases/12-solution-design-intelligence/12-CONTEXT.md` — locked decisions and discretion areas

### Secondary (MEDIUM confidence)

- `modules/mm/patterns.md`, `modules/sd/patterns.md`, `modules/fi/patterns.md`, `modules/co/patterns.md` — all confirmed as stubs (no content, placeholders for this phase)

---

## Metadata

**Confidence breakdown:**
- Pattern catalog (12 patterns): HIGH — derived from gaps in existing content; each pattern verified against what's already documented
- Playbook gap analysis: HIGH — based on direct comparison of existing coverage depth vs required playbook depth
- Checklist timing/steps: HIGH — sourced directly from co/processes.md (9-step sequence), fi/processes.md, and co/integration.md
- Navigation update scope: HIGH — confirmed by reading current cross-module/CLAUDE.md and sap-routing.md

**Research date:** 2026-02-18
**Valid until:** N/A — based on internal knowledge base content, not external library versions; valid as long as the knowledge base files are unchanged
