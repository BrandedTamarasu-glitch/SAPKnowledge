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
