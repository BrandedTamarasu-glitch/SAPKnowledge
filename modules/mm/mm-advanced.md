---
module: mm
content_type: decision-trees-and-troubleshooting
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Materials Management — OBYC Walkthrough, Decision Trees & Troubleshooting

> ECC 6.0 reference. OBYC account determination walkthrough covers the MM-side perspective on how movement types map to GL accounts. Decision trees guide MM configuration choices. Troubleshooting covers symptom-based diagnosis of common MM issues. For the OBYC framework and FI-side worked examples (movement types 101, 261, 551), see `modules/fi/account-determination.md`.

---

## 1. OBYC Account Determination — MM Perspective

The OBYC framework — the determination path from movement type through OMJJ to transaction key + valuation class to GL account — is documented in `modules/fi/account-determination.md`. This section adds the MM-side perspective:

- **Dual-axis navigation** — reference tables organized by transaction key AND by movement type, with cross-references between the two axes
- **Valuation class setup chain** — the complete configuration chain from OMWM through OMSK, OMJJ, OMWN to OBYC
- **Extended worked examples** — 7 additional Dr/Cr examples beyond the 3 in the FI file (10+ total)
- **OBYC debugging path** — 5-step diagnostic procedure for account determination errors

---

### 1a. Dual-Axis Reference — By Transaction Key

This table lists all OBYC transaction keys relevant to MM, what they post, and which movement types trigger them. Use this when you know the transaction key from an error message and need to understand its scope.

| Transaction Key | What It Posts | Supports Account Modifier? | Triggered By (Common Movement Types) |
|----------------|---------------|---------------------------|--------------------------------------|
| BSX | Inventory / stock account | No | 101, 102, 122, 201, 261, 301, 411K, 551, 561, 601, 701/702, MR21/MR22 |
| WRX | GR/IR clearing account | No | 101, 102, 122, MIRO |
| PRD | Price difference | Yes (optional modifier) | 101 (S-price only), 122 (S-price only), MIRO |
| GBB | Offsetting entry (consumption, scrapping, initial load, etc.) | Yes (VBR, VNG, VAX, VAY, AUF, BSA, INV, VBO, ZOB) | 201, 261, 301 two-step, 501, 551, 561, 601, 701/702 |
| KON | Consignment payables | Yes (has modifier) | 411K, 412K |
| AKO | Expense/revenue from consignment price difference | No | 411K (S-price materials with price diff) |
| UMB | Revaluation / price change account | Yes (optional reason-based modifier) | MR21, MR22 |

**Key notes:**

- **BSX and WRX do NOT use account modifiers.** They determine the GL account from the valuation class alone.
- **GBB is the most complex key** — it has 9 account modifiers, each routing to a different GL account depending on the business context. Getting the modifier wrong is the most common OBYC configuration error.
- **GBB modifier VBO** = consumption from subcontracting stock. It fires at movement type 543, NOT at 541. Movement type 541 has no FI posting.
- **PRD fires ONLY for standard price (S) materials.** For moving average price (V) materials, BSX absorbs the variance — no PRD posting occurs.

---

### 1b. Dual-Axis Reference — By Movement Type

This table is organized by movement type, showing which transaction keys fire and whether an FI posting occurs. Use this when you know the movement type and need to trace the GL postings.

| Movement Type | Description | Transaction Keys | FI Posting? | Notes |
|---------------|-------------|-----------------|-------------|-------|
| 101 | GR against PO | BSX (Dr), WRX (Cr), PRD (Dr/Cr for S-price) | Yes | See `fi/account-determination.md` for full worked example |
| 102 | GR reversal | Same as 101, reversed Dr/Cr | Yes | Opposite signs of 101 |
| 122 | Return to vendor | BSX (Cr), WRX (Dr), PRD (Dr/Cr for S-price) | Yes | Mirrors 101 reversed; OMBZ controls blocking when invoiced |
| 201 | GI to cost center | GBB/VBR (Dr), BSX (Cr) | Yes | Cost center receives consumption posting |
| 261 | GI to production order | GBB/VBR (Dr), BSX (Cr) | Yes | See `fi/account-determination.md` for full worked example |
| 262 | GI reversal (production) | Same as 261, reversed | Yes | Opposite signs of 261 |
| 301 | Plant-to-plant transfer (one step) | BSX (Dr at receiving), BSX (Cr at issuing) | Yes | Same CC = one FI doc; different CC = intercompany |
| 303/305 | Plant-to-plant transfer (two step) | 303: BSX Cr + GBB Dr (transit); 305: BSX Dr + GBB Cr (transit) | Yes | Uses stock-in-transit account via GBB |
| 311 | Storage location transfer | None | No | Same valuation area — no value change |
| 411K | Consignment withdrawal | BSX (Dr), KON (Cr), AKO (Dr/Cr if S-price diff) | Yes | Converts vendor consignment (K) to own stock |
| 412K | Consignment return | Reverse of 411K | Yes | Returns own stock to consignment |
| 501 | GR without PO | BSX (Dr), GBB (Cr) | Yes | Found stock |
| 541 | Transfer to subcontractor | **NONE** | **No** | **Stock reclassification only** (unrestricted to subcontracting stock O). NO FI posting. |
| 543 | GI for subcontracting (auto at GR) | GBB/VBO (Dr), BSX (Cr) | Yes | Component consumption at subcontractor GR. Fires automatically when 101 posts against subcontracting PO. |
| 551 | Scrapping | GBB/VNG (Dr), BSX (Cr) | Yes | See `fi/account-determination.md` for full worked example |
| 561 | Initial stock load | BSX (Dr), GBB/BSA (Cr) | Yes | Balance sheet opening |
| 601 | GI for delivery (SD) | GBB/VAX or VAY (Dr), BSX (Cr) | Yes | VAX = no CO acct assignment; VAY = with CO acct assignment |
| 701/702 | Inventory differences | BSX (Dr/Cr), GBB/INV (Cr/Dr) | Yes | Physical inventory adjustments |
| MR21 | Price change | BSX (Dr/Cr), UMB (Cr/Dr) | Yes | Changes standard price or MAP |
| MR22 | Debit/credit material value | BSX (Dr/Cr), UMB (Cr/Dr) | Yes | Adjusts value without changing price |

---

### 1c. Valuation Class Setup Chain

The valuation class (MBEW-BKLAS) is the primary driver in OBYC account determination. Two materials with different valuation classes post to different GL accounts for the same movement type. This is how SAP separates raw materials from finished goods from spare parts in the general ledger.

The complete configuration chain that feeds into OBYC:

```
Step 1: OMWM — Set valuation level (plant or company code)
        CRITICAL: Cannot change after any material is valued
        Standard: Valuation area = Plant

Step 2: OMSK — Define Account Category References
        Groups valuation classes into categories
        Assigned to material types (controls which valuation classes are allowed)
        Example: Material type ROH -> Account Category Reference 0001 -> Valuation classes 3000, 3010

Step 3: Material Type -> Account Category Reference -> Valuation Classes
        The material type determines which valuation classes can be assigned to a material
        Valuation class is stored in MBEW-BKLAS (Accounting 1 view of material master)

Step 4: OMJJ — Movement Type Configuration
        Defines which transaction keys fire per movement type
        Read-only during normal operations; do NOT modify standard movement types

Step 5: OMWN — Value String Assignment
        Maps movement types to value strings (grouping of transaction keys)
        Intermediary between OMJJ and OBYC

Step 6: OBYC — Account Determination
        Transaction key + Chart of accounts + Valuation class [+ Account modifier] -> GL account
        This is the final step that resolves to specific GL accounts
```

**Split valuation note:** When split valuation is active (OMWC), each valuation type can have its own valuation class, so BSX can post to different GL accounts for the same material depending on which valuation type is being received or issued. Configuration chain: OMWC (valuation category + types) -> OMSK (account category reference per type) -> OBYC (GL per valuation class).

---

### 1d. Worked Examples — Extended

> `modules/fi/account-determination.md` already has full worked examples for movement types 101 (standard price and MAP), 261 (GI to production order), and 551 (scrapping). Those are NOT duplicated here. The examples below extend the total to 10+ across both files.

> **Note:** Account numbers in all examples are representative examples. Your implementation will have different GL accounts based on your chart of accounts and OBYC configuration. The determination logic is what matters.

---

#### Example 1: Movement Type 201 — GI to Cost Center (Consumption)

Scenario: Issue 50 units of raw material (valuation class 3000, standard price 20 EUR/unit) to cost center 1000.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 400100 (Consumption Expense — representative example) | 1,000.00 | Dr | GBB/VBR: valuation class 3000 + modifier VBR -> GL 400100 |
| 140000 (Inventory — representative example) | 1,000.00 | Cr | BSX: valuation class 3000 -> GL 140000 |

Note: Same OBYC keys as movement type 261 (GI to production order). The difference is the account assignment object: cost center (201) vs production order (261). Both use GBB/VBR.

---

#### Example 2: Movement Type 301 — Plant-to-Plant Transfer (One Step)

Scenario: Transfer 100 units of finished goods (valuation class 7920, standard price 50 EUR/unit) from Plant 1000 to Plant 2000. Both plants in same company code.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140200 (Inventory Plant 2000 — representative example) | 5,000.00 | Dr | BSX: valuation class 7920 at Plant 2000 -> GL 140200 |
| 140100 (Inventory Plant 1000 — representative example) | 5,000.00 | Cr | BSX: valuation class 7920 at Plant 1000 -> GL 140100 |

Note: Two BSX postings — one per plant's valuation area. Same GL account if both plants share the same OBYC configuration; different GL accounts if plant-specific valuation grouping codes are used (OMWD). Different company codes generate intercompany postings.

---

#### Example 3: Movement Type 411K — Consignment Withdrawal

Scenario: Withdraw 200 units of consignment raw material (valuation class 3000, consignment price 15 EUR/unit, standard price 18 EUR/unit) from vendor consignment stock to own stock.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Inventory — representative example) | 3,600.00 | Dr | BSX: at standard price (18 x 200) |
| 195000 (Consignment Payables — representative example) | 3,000.00 | Cr | KON: at consignment price (15 x 200) |
| 310000 (Consignment Price Difference — representative example) | 600.00 | Cr | AKO: price difference (18 - 15) x 200 — fires because material is S-price and consignment price differs from standard |

Note: KON creates a liability to the consignment vendor. AKO fires only for S-price materials when consignment price differs from standard price. For MAP materials, BSX absorbs the consignment price directly.

---

#### Example 4: Movement Type 541/543 — Subcontracting

Scenario: Transfer 500 units of raw material (valuation class 3000, MAP 12 EUR/unit) to subcontractor. Later, receive 100 finished goods (valuation class 7920, PO price 25 EUR/unit) from subcontractor.

**Step 1 — Movement type 541 (Transfer to subcontractor):**

**NO FI POSTING.** Stock reclassified from unrestricted to subcontracting stock (special stock O) at the same plant. This is a stock type change, not a valuation event.

**Step 2 — Movement type 101 (GR against subcontracting PO) + automatic 543 (component consumption):**

GR for finished goods (101):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Finished Goods Inventory — representative example) | 2,500.00 | Dr | BSX: valuation class 7920 -> GL 140000 |
| 191100 (GR/IR Clearing — representative example) | 2,500.00 | Cr | WRX: valuation class 7920 -> GL 191100 |

Simultaneous component consumption (543):

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 400200 (Subcontracting Consumption — representative example) | 6,000.00 | Dr | GBB/VBO: valuation class 3000 + modifier VBO -> GL 400200 |
| 140000 (Raw Material Inventory — representative example) | 6,000.00 | Cr | BSX: valuation class 3000 -> GL 140000 (500 units x 12 EUR) |

Note: The 543 fires automatically when the GR (101) is posted against a subcontracting PO. The system issues the components from subcontracting stock. GBB modifier VBO is specific to subcontracting consumption.

---

#### Example 5: Movement Type 122 — Return to Vendor

Scenario: Return 20 units of raw material (valuation class 3000, standard price 100 EUR, PO price 105 EUR) to vendor.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Inventory — representative example) | 2,000.00 | Cr | BSX: reduces stock at standard price |
| 191100 (GR/IR Clearing — representative example) | 2,100.00 | Dr | WRX: reverses GR/IR at PO price |
| 310000 (Price Difference — representative example) | 100.00 | Cr | PRD: price variance (standard vs PO) |

Note: Mirrors movement type 101 with opposite Dr/Cr. If GR-Based Invoice Verification (LFM1-WEBRE) is active and the PO is already invoiced, movement type 122 may be blocked. T-code OMBZ controls whether returns are allowed when invoices exist.

---

#### Example 6: Split Valuation — Same Material, Different GL Accounts

Scenario: Material "STEEL-001" has split valuation active (OMWC). Valuation type "Domestic" uses valuation class 3000 (GL 140000). Valuation type "Imported" uses valuation class 3010 (GL 140100). GR of 100 units against PO for "Imported" stock.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140100 (Imported Inventory — representative example) | 10,000.00 | Dr | BSX: valuation class **3010** (Imported type) -> GL 140100 |
| 191100 (GR/IR Clearing — representative example) | 10,000.00 | Cr | WRX: valuation class 3010 -> GL 191100 |

Note: The valuation class comes from the specific valuation type in MBEW, not the header material. Different valuation types can use different valuation classes, which map to different GL accounts in OBYC. Configuration chain: OMWC (valuation category + types) -> OMSK (account category reference per type) -> OBYC (GL per valuation class).

---

#### Example 7: MR21 — Price Change (Revaluation)

Scenario: Change standard price of raw material (valuation class 3000, current standard 100 EUR, new standard 110 EUR, stock quantity 500 units).

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Inventory — representative example) | 5,000.00 | Dr | BSX: stock value increase (10 EUR x 500 units) |
| 315000 (Revaluation Account — representative example) | 5,000.00 | Cr | UMB: offsetting revaluation entry |

Note: MR21 changes the material price; MR22 adjusts value without changing price. Both use UMB for the offsetting entry. UMB supports reason-based account modifiers — different "reasons for price change" can route to different GL accounts in OBYC.

---

#### Reversals — Abbreviated Treatment

Reversal movement types (102, 262, 412K) use the same OBYC transaction keys as their base movement types (101, 261, 411K) but post Dr/Cr in the opposite direction. No separate worked examples needed — apply the base example with reversed signs.

---

### 1e. OBYC Debugging Path

When a goods movement fails with an account determination error or posts to an unexpected GL account, follow this 5-step diagnostic path.

> **Quick check:** Most OBYC errors come from Step 2 — a missing entry for the valuation class + transaction key combination. Before running traces, always check OBYC directly for the transaction key and valuation class shown in the error message.

**Step 1: Identify the transaction key**

Read the error message — it usually names the transaction key (e.g., "Account not defined for transaction key BSX" or F5 class errors referencing a specific key). If the error message is unclear, use OMJJ or OMWN to look up which transaction keys fire for the movement type in question.

**Step 2: Check OBYC configuration**

T-code OBYC -> Enter the transaction key -> Verify that an entry exists for:
- Your chart of accounts
- Your valuation grouping code (if multi-company-code setup via OMWD)
- Your valuation class (from the material master, MBEW-BKLAS in the Accounting 1 view)
- Your account modifier (for GBB, PRD, KON only — check which modifier the movement type requires from the tables in sections 1a/1b above)

**Step 3: Simulation via OMWB**

T-code OMWB -> Enter material number -> Simulation -> Go to Report. This shows which GL accounts would be determined for each transaction key for the given material. Use before posting to verify the determination will succeed. If the simulation shows "no account found," the OBYC entry from Step 2 is missing or misconfigured.

**Step 4: Runtime trace via SE37**

Debug function module MR_ACCOUNT_ASSIGNMENT. Set a breakpoint and post the goods movement. The debugger shows the exact OBYC lookup steps: which selection criteria are used (chart of accounts, valuation grouping code, valuation class, modifier) and the result for each transaction key. Use when OMWB simulation succeeds but the actual posting fails — indicates a runtime condition (e.g., valuation grouping code mismatch).

**Step 5: SQL trace via ST05**

Activate SQL trace (ST05 -> Activate Trace) before posting in MIGO. Post the goods movement, then deactivate the trace. Display the trace and filter for table T030 (OBYC configuration table). The trace shows all table accesses against T030 and identifies which specific access returned no result. This is the most detailed diagnostic — use when Steps 2-4 do not identify the issue.

---

## 2. Configuration Decision Trees

> Each decision tree has two parts: (1) Q&A routing — answer questions to reach the recommended approach, then (2) a comparison table with config implications and trade-offs. Decision trees include config paths inline (not just pointers to config-spro.md).

---

### Decision Tree 1: Valuation Approach — Standard Price (S) vs Moving Average Price (V)

**Q1: Is this a manufactured material with a production cost estimate (CK11N/CK24)?**
- Yes → Use Standard Price (S) — required for standard costing variance analysis in CO-PC.
- No → Continue to Q2.

**Q2: Is this a traded/purchased material with volatile prices (commodities, spot-market items)?**
- Yes → Moving Average Price (V) is typically better — stock value tracks actual purchase cost automatically.
- No → Continue to Q3.

**Q3: Is Material Ledger active for this plant?**
- Yes → ML can calculate actual costs on top of standard price, giving benefits of both.
- No → The choice between S and V determines how variance appears (PRD account vs absorbed into BSX).

| Approach | When to Use | Config Implications | Trade-offs |
|----------|------------|---------------------|------------|
| Standard Price (S) | Manufactured goods; materials with cost estimates; need variance visibility | Cost estimate required (CK11N/CK24); PRD fires on GR/MIRO when actual differs from standard; periodic price release via MR21 | Price variances visible in PRD account; requires cost estimate maintenance; inventory valued at predetermined price |
| Moving Average Price (V) | Traded goods; volatile-price materials; simpler operations | No cost estimate needed; BSX absorbs all price fluctuations; MAP updates automatically with each receipt | No separate variance visibility; inventory value fluctuates with purchases; negative stock can distort MAP |
| Standard + Material Ledger | Best of both — standard for planning, actual for reporting | ML activation per plant (CKMLCP required at period-end); additional complexity | Most comprehensive; requires period-end CKMLCP run; ML is optional in ECC 6, mandatory in S/4HANA |

---

### Decision Tree 2: Release Strategy Design

**Q1: How many approval levels are needed?**
- 1 level → Simple release.
- 2-3 levels → Standard release strategy.
- 4+ levels → Consider SAP workflow instead.

**Q2: Are approval thresholds value-based, org-based (plant/purchasing group), or both?**
- Value-based → Use total value characteristic.
- Org-based → Use plant + purchasing group characteristics.
- Both → Combine characteristics in classification.

**Q3: Do PRs and POs need separate release strategies?**
- Yes → Configure separate release groups for PRs (M) and POs (B).
- No → One release group may suffice.

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Simple (1 level, value-based) | Small org; single approver above threshold | SPRO -> MM -> Purchasing -> PO -> Release Procedure; 1 release code, 1 strategy with value characteristic | Fastest setup; limited control; no multi-level approval |
| Standard (2-3 levels, value + org) | Medium org; escalating approval by PO value | Same SPRO path; multiple release codes in sequence; classification with value ranges + org characteristics | Good balance of control and complexity; covers most business scenarios |
| Complex (4+ levels or conditional) | Large org; matrix approval; conditional routing | Consider SAP Business Workflow (SWU3) instead of pure release strategy | Classification-based strategies become difficult to maintain beyond 3-4 levels; workflow provides more flexibility |

---

### Decision Tree 3: Source Determination

**Q1: Do you need to enforce specific approved vendors per material/plant?**
- Yes → Activate source list (OMGM) and use ME01 to maintain EORD entries.
- No → Skip source list.

**Q2: Do you want ME59N (automatic PR-to-PO conversion) to work?**
- Yes → Either source list with valid entries OR purchasing info records (EINE/EINA) must exist for the material+vendor combination.
- No → Source determination is informational only.

**Q3: Do you have outline agreements (contracts/scheduling agreements) that should be the preferred source?**
- Yes → Link the agreement to the source list entry and set the "fixed source" indicator.
- No → Standard source determination is sufficient.

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No source list (info records only) | Small vendor base; flexible sourcing | No OMGM activation; ME59N uses info records | Simplest; any vendor with an info record can be used; no vendor restriction enforcement |
| Source list without fixed source | Approved vendor enforcement; multiple valid sources per material | OMGM activation per plant/material type; ME01 source list maintenance | Restricts purchasing to approved vendors; ME59N picks best source; maintenance overhead for source list entries |
| Source list with fixed source + agreement | Preferred vendor enforcement; agreement-based purchasing | Source list entry linked to contract/SA; fixed source indicator set | Maximum control; guaranteed agreement usage; highest maintenance — source list entries must be kept current with agreement validity |

---

### Decision Tree 4: Vendor Evaluation Setup

**Q1: Does the business need to score and rank vendors systematically?**
- No → Skip vendor evaluation — informal tracking is sufficient.
- Yes → Continue to Q2.

**Q2: Which evaluation criteria matter most?**
- Standard SAP criteria: delivery (on-time performance), price (price level vs market), quality (reject rate), service (response time). Activate the criteria that align with business priorities.

**Q3: Should evaluation update automatically from PO/GR/QM data?**
- Yes → Configure automatic evaluation.
- No → Manual scores via ME62/ME63.

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No vendor evaluation | Small vendor base; informal relationship management | No config needed | No systematic scoring; no data-driven vendor comparisons |
| Manual evaluation only | Need scoring but limited transaction volume for automatic | ME61 (maintain criteria weights); ME62/ME63 (manual scoring) | Simple setup; requires discipline to update scores; subjective |
| Automatic evaluation | High transaction volume; objective scoring needed | SPRO -> MM -> Purchasing -> Vendor Evaluation -> Configure criteria + automatic weighting; requires GR/QM data flow | Objective, data-driven; requires proper GR posting discipline (on-time flags); more config complexity |

---

### Decision Tree 5: Tolerance Key Selection

**Q1: What type of procurement are you configuring tolerances for?**
- Standard procurement, high-value procurement, service procurement, or consignment/VMI? Each needs different key focus.

**Q2: Should small price differences auto-post or block for review?**
- Auto-post → Configure BD tolerance.
- Block → Focus on PP tolerance.
- Most implementations use BOTH (BD for tiny differences, PP for larger ones).

**Q3: Do you need quantity-based blocking?**
- Yes → Configure DQ tolerance.
- If GR quantity = 0 scenarios are common, also configure DW.

Recommended tolerance keys by scenario:

| Scenario | Key Tolerance Keys | Recommended Starting Values | Config T-code |
|----------|-------------------|----------------------------|---------------|
| Standard procurement | BD, PP, DQ | BD: $5-10 absolute; PP: 2-5%; DQ: 5-10% | OMR6 |
| High-value procurement | PP, DQ, AN, AP | PP: 1-2%; DQ: 2-5%; AN/AP: tighter absolute | OMR6 |
| Service procurement | AN, PP | AN: higher absolute (services vary); PP: wider % | OMR6 |
| Consignment/VMI | VP, PP | VP: 5-10% (absorb price fluctuations); PP: standard | OMR6 |
| Blanket POs | LA, LD, PS | LA/LD: per business policy; PS: estimated price % | OMR6 |

> **IMPORTANT:** There is no standard SAP tolerance key "PE." The 15 standard keys are: AN, AP, BD, BR, BW, DQ, DW, KW, LA, LD, PC, PP, PS, ST, VP. Use PP (price variance) for price tolerance. See `modules/mm/config-spro.md` for the complete 15-key reference.

---

### Decision Tree 6: Split Valuation

**Q1: Do you need to value the same material at different prices based on origin, quality, or source?**
- No → Standard single valuation is sufficient.
- Yes → Continue to Q2.

**Q2: What characteristic differentiates the valuation?**
- Origin (domestic vs imported), quality grade, production vs purchased. This becomes the "valuation category" in OMWC.

**Q3: Do the different categories need different GL accounts?**
- Yes → Configure different valuation classes per valuation type, leading to different OBYC -> GL mappings.
- No → Split valuation still tracks separate stock quantities, but GL posting is the same.

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No split valuation | One price per material per plant is sufficient | Default — no config | Simplest; cannot distinguish origin/quality in valuation |
| Split valuation (2-3 types) | Domestic vs imported; different prices per origin | OMWC (define categories + types) -> OMSK (account category ref per type) -> material master (activate split valuation) -> OBYC (GL per valuation class) | Moderate complexity; must specify valuation type on every goods movement; separate stock quantities per type |
| Batch-specific valuation | Each batch valued at actual receipt price | Different mechanism: batch management + batch valuation indicator | Per-batch actual cost; high complexity; typically used with Material Ledger for proper costing |

---

### Decision Tree 7: Batch Management

**Q1: Does the business need to track individual batches (lots) for materials?**
- No → Skip batch management.
- Yes → Continue to Q2.

**Q2: Is batch tracking needed for traceability (recall capability) or valuation (different cost per batch)?**
- Traceability → Activate batch management indicator.
- Valuation → Also consider batch-specific valuation (see Decision Tree 6).

**Q3: Where should the batch number be unique?**
- Per material (standard), per plant, or per material + plant. Configure batch level (OMCT) accordingly.

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No batch management | No traceability requirement; homogeneous materials | Default | Simplest; no batch number entry on movements |
| Batch management (traceability only) | Recall capability; lot tracking; shelf life | MARC-XCHPF = X per plant + material type config | Batch number required on all movements; batch master data (MSC1N) needed; batch determination rules optional |
| Batch management + batch valuation | Per-batch costing; different prices per lot | Batch management + split valuation indicator on batch level | Most complex; each batch has own price; requires discipline in receiving and issuing |

---

### Decision Tree 8: Serial Number Management

**Q1: Do you need to track individual serialized units?**
- No → Skip serial numbers.
- Yes → Continue to Q2.

**Q2: At which transactions should serial numbers be captured?**
- GR only, GI only, or both? This determines the serial number profile (OISO).

**Q3: Is this for warranty tracking, asset management, or regulatory compliance?**
- Warranty → Capture at GR + sales delivery.
- Asset → Link serial number to FI asset master (ANLSE).
- Regulatory → Full lifecycle tracking.

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No serial numbers | No unit-level tracking needed | Default | Simplest; fastest goods movements |
| Serial number profile (GR/GI) | Track which serial numbers are in stock or issued | OISO (define profile) -> material master (assign profile in Plant Data/Storage view) | Serial number entry required at configured transactions; not full lifecycle unless combined with equipment |
| Serial numbers + equipment link | Full lifecycle tracking with maintenance history | Serial profile + PM equipment master link | Maximum traceability; highest data entry overhead; typically combined with PM module |

---

### Decision Tree 9: Consignment and Special Stock Types

**Q1: Does the vendor retain ownership of stock stored at your plant?**
- Yes → Vendor consignment (special stock K).
- No → Standard stock.

**Q2: Do you provide materials to a subcontractor for processing?**
- Yes → Subcontracting stock (special stock O) with movement type 541/543.
- No → Continue to Q3.

**Q3: Is stock stored at a third-party location but owned by your company?**
- Yes → Consider pipeline stock (special stock type varies by scenario).
- No → Standard stock is sufficient.

| Special Stock Type | Indicator | When to Use | Key Movement Types | FI Impact |
|-------------------|-----------|-------------|-------------------|-----------|
| Standard stock | None | Company-owned, in own warehouse | 101, 201, 261 | Standard BSX/WRX/GBB |
| Vendor consignment | K | Vendor-owned, in your warehouse; pay on consumption | 411K (withdraw), 412K (return) | KON creates vendor liability at consumption; no FI at receipt |
| Subcontracting | O | Your materials at vendor for processing | 541 (transfer out — NO FI), 543 (consume at GR — GBB/VBO) | 541 = no FI posting; FI fires at GR + auto-543 |
| Project stock | Q | Stock assigned to WBS element | 101 with account assignment P | BSX posts to project-specific inventory account |

---

### Decision Tree 10: MRP Type Selection

**Q1: Does this material have deterministic demand (sales orders, planned independent requirements, BOM explosions)?**
- Yes → MRP type PD.
- No → Continue to Q2.

**Q2: Is this a consumable with relatively stable usage?**
- Yes → Reorder point planning (VB manual or VM automatic). If stable + seasonal, forecast-based (VV).
- No → Continue to Q3.

**Q3: Should this material be excluded from MRP entirely?**
- Yes → MRP type ND (no planning).
- No → Evaluate demand patterns and choose PD or VB based on predictability.

| MRP Type | Full Name | Driven By | Best For | Config Field |
|----------|-----------|-----------|----------|--------------|
| PD | MRP (deterministic) | Sales orders, PIR, BOM explosion | A-class materials; manufactured goods; known demand | MARC-DISMM = PD |
| VB | Manual Reorder Point | Stock level vs manually set reorder point | B/C-class materials; consumables; stable consumption | MARC-DISMM = VB; set MARC-MINBE |
| VM | Automatic Reorder Point | System-calculated reorder point from consumption history | Materials where system can reliably forecast safety stock | MARC-DISMM = VM |
| VV | Forecast-Based | Historical consumption forecast | Predictable consumption patterns; seasonal materials | MARC-DISMM = VV |
| ND | No MRP | None — excluded from planning | Non-stock materials; services; one-time purchases | MARC-DISMM = ND |

> ECC 6 note: VV (forecast-based) is in "compatibility scope" for S/4HANA. Still fully functional in ECC 6.0 but flagged for future migration consideration.

---

### Decision Tree 11: Lot Sizing Procedure

**Q1: Should each procurement cover exactly one requirement (no consolidation)?**
- Yes → Lot-for-lot (EX).
- No → Continue to Q2.

**Q2: Does the business order in fixed quantities (e.g., pallet loads, container sizes)?**
- Yes → Fixed lot size (FX).
- No → Continue to Q3.

**Q3: Should requirements be consolidated by time period?**
- Weekly (WB), monthly (MB), or configurable period (PB)?

| Procedure | Code | When to Use | Config Field | Trade-offs |
|-----------|------|-------------|--------------|------------|
| Lot-for-lot | EX | Expensive materials; make-to-order; minimize inventory | MARC-DISLS = EX | No inventory buildup; more frequent orders; higher ordering cost |
| Fixed lot size | FX | Standard order quantities; pallet/container logic | MARC-DISLS = FX; MARC-BSTFE (fixed lot size qty) | Consistent order size; may over-purchase for small requirements |
| Weekly lot size | WB | Medium-value materials with weekly delivery rhythm | MARC-DISLS = WB | Reduces order frequency; one week of inventory exposure |
| Monthly lot size | MB | Low-value materials with monthly ordering | MARC-DISLS = MB | Fewest orders; highest inventory investment per cycle |
| Period lot size | PB | Flexible consolidation period | MARC-DISLS = PB; MARC-FXHOR (planning time fence) | Most flexible; requires period definition |
| Optimum lot size | OP | Cost-optimized (carrying cost vs ordering cost) | MARC-DISLS = OP; requires cost parameters in MRP 2 | Cost-optimal; requires accurate carrying cost and ordering cost parameters |

---

### Decision Tree 12: Planning Strategy — MTS vs MTO

**Q1: Are finished goods produced to stock for general demand (forecast-driven)?**
- Yes → Make-to-Stock (MTS).
- No → Continue to Q2.

**Q2: Are finished goods produced only when a specific sales order exists?**
- Yes → Make-to-Order (MTO).
- No → Consider hybrid strategy.

**Q3: Should finished goods carry individual customer assignment through production?**
- Yes → Strategy 20 (MTO with individual requirements).
- No but still triggered by sales orders → Strategy 50 (MTO without individual requirements — planning strategy).

| Strategy | Strategy Group | When to Use | Key Config | Trade-offs |
|----------|---------------|-------------|------------|------------|
| MTS — Strategy 10 | Net requirements planning | Standard MTS with consumption of PIR by sales orders | Strategy group 10 in material master MRP 3 view; PIR via MD61 | Smooth production; inventory risk; sales orders consume forecast |
| MTS — Strategy 40 | Planning with final assembly | Forecast for components, assemble on sales order | Strategy group 40; combination of PIR + sales order-driven assembly | Reduces FG inventory; components planned to forecast; assembly to order |
| MTO — Strategy 20 | Make-to-Order (individual) | Customer-specific production; each SO creates individual planned order | Strategy group 20; individual customer stock | Full traceability to customer order; no shared stock; highest complexity |
| MTO — Strategy 50 | Make-to-Order (planning) | SO-driven but no individual stock segment | Strategy group 50; planned orders linked to sales order but stock is shared | Simpler than 20; SO triggers production; stock fungible once produced |
