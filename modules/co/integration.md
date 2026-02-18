---
module: co
content_type: integration
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — Integration Points

> ECC 6.0 reference. Documents every touchpoint where FI creates CO documents and where CO creates FI documents. CO-FI integration is bidirectional: FI->CO is automatic (via primary cost elements), CO->FI occurs only through external settlement (category 22) and reconciliation posting (KALC). For cost element mapping details, see `modules/co/co-advanced.md`. For OBYC (MM-FI) and VKOA (SD-FI) account determination, see `modules/fi/account-determination.md`. For S/4HANA differences, see the S/4HANA Differences section at the end.

---

## 1. CO-FI Integration Point Catalog

Every CO-related transaction organized by integration direction: which transactions create CO documents from FI, which create FI documents from CO, and which stay entirely within CO.

### Direction 1: FI -> CO (Automatic — Primary Cost Element Postings)

Every row in this table follows the same mechanism: the FI posting hits a P&L GL account that has a corresponding primary cost element (CSKB lookup), and the CO account assignment (cost center, order, WBS) determines where in CO the cost lands. The system performs this check at posting time — the CO document is created simultaneously with the FI document, not asynchronously. For the detailed 5-step flow, see `modules/co/co-advanced.md` Section 1b.

> **Key principle:** Balance sheet GL accounts (assets, liabilities, equity) do NOT have cost elements and therefore NEVER create CO documents. Only P&L accounts with a corresponding primary cost element trigger CO postings. This is why not every FI posting appears in CO.

| FI Transaction | FI T-Code | CO Impact | CO Tables Updated | Condition |
|---------------|-----------|-----------|-------------------|-----------|
| GL posting to P&L account | FB50, F-02 | CO document created; cost center/order debited | COBK, COEP, COSP | Primary CE must exist for the GL account |
| Vendor invoice (non-PO) | FB60 | CO document; expense on cost center | COBK, COEP, COSP | P&L GL account with primary CE + CO assignment |
| Vendor invoice (PO-based) | MIRO | CO document; expense or stock on CC/order | COBK, COEP, COSP | Account-assigned PO (K, F, P) |
| Goods issue to cost center | MIGO (201) | CO document; consumption on cost center | COBK, COEP, COSP | GBB/VBR posting has CE + CC assignment |
| Goods issue to production order | MIGO (261) | CO document; consumption on production order | COBK, COEP, COSP | GBB/VBR posting has CE + order assignment |
| Customer billing (revenue) | VF01 | CO document; revenue on profitability segment | COBK, COEP, COSP | Revenue CE exists; CO-PA active |
| PGI (COGS) | VL02N (601) | CO document; COGS on cost object | COBK, COEP, COSP | COGS CE exists |
| Depreciation run | AFAB | CO document; depreciation on cost center | COBK, COEP, COSP | Depreciation CE exists; asset has CC in ANLZ |
| Payroll posting | PC00_MXX_CALC | CO document; salary expense on cost center | COBK, COEP, COSP | Wage type mapped to CE + CC |

### Direction 2: CO -> FI (Settlement with External Receivers)

> **CRITICAL:** Only category 22 (external settlement) and KALC create FI documents from CO. All other CO transactions (assessment, distribution, activity allocation, internal settlement) stay within CO and never touch FI.

| CO Transaction | CO T-Code | FI Impact | FI Tables Updated | Condition |
|---------------|-----------|-----------|-------------------|-----------|
| Settle order to GL account | KO88 (KST receiver) | FI document created | BKPF, BSEG | Category 22 CE; receiver = GL account |
| Settle order to asset/AUC | KO88 (FXA receiver) | FI document (capitalization) | BKPF, BSEG, ANLA/ANLP | Category 22 CE; receiver = asset |
| Settle production order | CO88 | FI document (variance to P&L or inventory) | BKPF, BSEG | Settlement rule with FI receiver |
| Reconciliation posting | KALC | FI intercompany documents | BKPF, BSEG | Cross-CC CO postings exist in COFIT |

### Direction 3: CO Internal (No FI Impact)

| CO Transaction | CO T-Code | CO Tables Updated | FI Impact |
|---------------|-----------|-------------------|-----------|
| Assessment | KSU5 | COBK, COEP, COSS (secondary CE cat 42) | NONE — stays in CO |
| Distribution | KSV5 | COBK, COEP, COSP (primary CEs preserved) | NONE — stays in CO |
| Activity allocation | KB21N | COBK, COEP, COSS (secondary CE cat 43) | NONE — stays in CO |
| Overhead calculation | KGI2 | COBK, COEP, COSS (secondary CE cat 41) | NONE — stays in CO |
| Reposting | KB61 | COBK, COEP | NONE — stays in CO |
| Actual price calculation | KSII | Recalculates prices; may adjust COSS | NONE — stays in CO |
| Settle order to cost center | KO88 (CTR receiver) | COBK, COEP, COSS (secondary CE cat 21) | NONE — stays in CO |
| Settle order to CO-PA | KO88 (RKS receiver) | COBK, COEP, CO-PA tables | NONE — stays in CO |

Direction 3 transactions are the reason CO totals exceed FI totals. Every assessment, distribution, and activity allocation creates CO documents with secondary cost elements that have no FI counterpart. This is by design — secondary cost elements enable CO to track cost flows (who allocated what to whom) without creating redundant FI entries that would inflate the general ledger.

**Key distinction — Distribution preserves CEs, Assessment replaces them:**
- Distribution (KSV5) updates COSP (primary totals) because it preserves the original primary cost elements on the receiver. The receiver sees the same cost elements as the sender.
- Assessment (KSU5) updates COSS (secondary totals) because it uses a secondary cost element (category 42) that replaces the original cost elements. The receiver sees a single "overhead assessed" element.

See `modules/co/co-advanced.md` Section 1c for the reconciliation walkthrough.

---

## 2. Transaction Trace — "What Happens in CO When I Post FB50 to a P&L Account?"

This is the core CO-FI integration trace. It answers the single most common CO integration question: "I posted a GL expense — what happened in CO?"

**Trigger:** GL Accountant posts FB50 with a P&L GL account (e.g., 400000 Salaries) and enters cost center 1000.

> This trace also applies to FB60 (vendor invoice without PO), MIRO (PO-based invoice with account assignment), VF01 (billing with revenue CE), AFAB (depreciation run), and any other transaction that posts to a P&L GL account with a corresponding primary cost element. The mechanism is identical — only the FI document type and source transaction differ.

### Step 1: FI Document Creation

- BKPF header created with document number, posting date, document type SA
- BSEG line items: Dr 400000 (expense), Cr 113100 (bank/clearing)
- The user entered cost center 1000 on the expense line item (BSEG-KOSTL = 1000)
- FI document is complete and posted

### Step 2: Cost Element Check

- System reads CSKB for KSTAR = 400000 in the controlling area
- If found (primary CE, category 1): proceed to Step 3
- If NOT found: no CO posting — the GL account is FI-only (balance sheet or unmapped P&L)

### Step 3: CO Account Assignment Validation

- System checks: does the FI document line item have a CO account assignment?
  - Cost center (KOSTL) -> post to cost center
  - Internal order (AUFNR) -> post to order
  - WBS element (PS_PSP_PNR) -> post to project
- If no CO assignment AND no OKB9 default: posting FAILS — "Enter a CO account assignment"
- If OKB9 default exists: system uses the default cost center

### Step 4: CO Document Creation

- COBK header: CO document number (different from FI doc), posting date, controlling area
- COEP line item: KSTAR (cost element = 400000), OBJNR (CO object = cost center 1000), WKGBTR (amount), BELNR (reference to FI document number)
- COSP updated: period total for cost element 400000 on cost center 1000 incremented

### Step 5: PCA Update (If Active)

- System reads CSKS-PRCTR for cost center 1000 -> finds profit center assignment
- GLPCA (PCA actual line items) updated with the posting amount under the profit center
- This is how PCA captures FI postings: via the cost center -> profit center assignment chain

### Step 6: Verification

- FI: FBL3N or FAGLB03 shows the GL posting to account 400000
- CO: KSB1 shows the CO line item on cost center 1000 for cost element 400000
- PCA: KE5Z shows the amount under the assigned profit center
- All three reports show the SAME amount for this primary CE posting

**What if the cost element does NOT exist?**
If GL account 400000 has no corresponding primary cost element in CSKB, the system behavior depends on the account type:
- If the GL account is a balance sheet account: posting succeeds with no CO document (this is normal)
- If the GL account is a P&L account without a cost element: posting succeeds but no CO document is created. The cost is "invisible" to CO — it appears in FI reports but not in KSB1 or any CO report. To fix, create the cost element via KA01.

**What if the user does NOT enter a cost center?**
- If OKB9 has a default for GL account 400000: system uses the default cost center automatically
- If OKB9 has no default: posting FAILS with message KI 235 "Enter a CO account assignment." This is the single most common CO error in new implementations. Resolution: either enter a cost center on the FI document or maintain a default in OKB9.

---

## 3. Transaction Trace — "What Happens When KO88 Settles an Order to a GL Account?"

This is the reverse direction trace — the only common scenario where CO creates an FI document (besides KALC).

**Trigger:** Cost Accountant runs KO88 for internal order 800001 with settlement rule: 100% to GL account 490000.

> This trace applies specifically to settlement with an external receiver (GL account or fixed asset). Settlement to internal receivers (cost center, internal order, WBS, CO-PA) follows the same Steps 1-3 but does NOT create an FI document — see Direction 3 in the catalog above.

### Step 1: Read Order Costs

- System reads COEP for order 800001: total actual costs (sum of primary + secondary postings)
- Example: 50,000 EUR total costs collected on the order

### Step 2: Read Settlement Rule

- COBRB: receiver type KST (GL account), receiver = 490000, percentage = 100%
- Settlement cost element: category 22 CE (e.g., 690000 "Settlement to GL")

### Step 3: CO Document Creation (Settlement)

- COBK/COEP: Credit order 800001 by 50,000 EUR (using settlement CE 690000)
- Order balance reduced to zero (fully settled)

### Step 4: FI Document Creation (External Settlement)

- Because receiver type = KST (GL account), settlement creates an FI document
- BKPF header: document type SA, posting date = settlement period
- BSEG: Dr 490000 (expense clearing GL account), Cr varies per allocation structure (OKO6)

### Step 5: Verification

- KOB1: Order 800001 shows settlement credit line (cost element 690000, credit 50,000 EUR)
- FBL3N: GL account 490000 shows the settlement debit (50,000 EUR)
- KO03: Order status may be TECO after settlement if the order is fully settled and no further postings are expected

**Why does settlement create an FI document?**
Because the receiver type is KST (GL account) or FXA (fixed asset), the settlement crosses the CO-FI boundary. The settlement cost element must be category 22 (external settlement) — this is the only category that creates FI documents from CO. If the receiver were CTR (cost center) or ORD (internal order), the settlement would stay within CO using a category 21 CE (internal settlement) and no FI document would be created.

**Common settlement error:** If the settlement cost element is not category 22 but the receiver is a GL account, KO88 fails with an error. The settlement profile (OKO7) must allow external settlement and must reference a category 22 CE in the allocation structure (OKO6).

Cross-reference: For settlement receiver types and FI document creation rules, see `modules/co/processes.md` Section 2.

---

## 4. Reconciliation Ledger in Integration Context

When CO allocations (KSU5, KSV5, KB21N) or settlements (KO88 with CTR receiver) cross company code boundaries within a controlling area, the reconciliation ledger (COFIT/COFIS) records the intercompany amounts. KALC creates the corresponding FI intercompany documents.

This is listed as Direction 2 entry #4 in the catalog above. The 3-step mechanism:

1. **CO posting crosses company code boundary** — e.g., assessment from CC in company code 1000 to CC in company code 2000. CO documents are posted and balanced within CO.
2. **Reconciliation ledger records the cross-CC amounts** — COFIT (totals) and COFIS (single records) capture sending company code, receiving company code, amount, and cost element.
3. **KALC creates FI intercompany documents** — Dr Intercompany Receivable (sending CC), Cr Intercompany Payable (receiving CC). This brings FI back into balance with CO.

**When reconciliation is needed:**
- Controlling area spans multiple company codes (1:many CA:CC, configured in OKKP)
- CO allocations or settlements cross company code boundaries
- If all CO objects are in the same company code, COFIT/COFIS are empty and KALC produces no postings

**Reconciliation T-codes:**
- KALC — Execute reconciliation posting (creates FI intercompany documents)
- KAL1 — Display reconciliation ledger entries
- KAL2 — Reconciliation ledger report (summary view)

**Key timing:** KALC runs after all CO allocations and settlements but before the CO period is locked. See Section 5 below.

For the complete reconciliation ledger mechanism (reconciliation walkthrough, configuration, activation in OKKP), see `modules/co/co-advanced.md` Section 1d.

---

## 5. Period-End CO-FI Timing

CO period-end depends on FI and MM period-end being complete. The cross-module sequence:

```
FI Period-End (F.05 FX revaluation, FBS1 accruals, AFAB depreciation)
    -> MM Period-End (MMPV, CKMLCP if ML active)
        -> CO Period-End (KB61 -> KGI2 -> KSU5/KSV5 -> KO88/CO88 -> KSII -> KALC -> lock period)
```

### Key Timing Dependencies

1. **All FI postings must complete before CO period-end** — CO allocations use the balances at execution time. FI postings with CO account assignments (depreciation via AFAB, accruals via FBS1) must be posted before CO allocations run, or the allocations will miss those costs.

2. **MM period-end must complete before CO period-end** — inventory adjustments and Material Ledger closing (CKMLCP) generate FI postings that flow to CO. If MM period-end runs after CO allocations, the allocated amounts will not include MM adjustments.

3. **CO period-end runs LAST** — the internal sequence is: repost (KB61) -> overhead calc (KGI2) -> assessment/distribution (KSU5/KSV5) -> settlement (KO88/CO88) -> actual prices (KSII) -> reconciliation (KALC) -> lock period.

4. **KALC runs after all CO allocations and settlements but before period lock** — KALC must capture all cross-company-code CO postings from the current period. Running KALC before all settlements complete would miss settlement-related cross-CC entries.

### CO Period-End Sequence (Summary)

| Step | T-code | Purpose | Creates FI Document? |
|------|--------|---------|---------------------|
| 1 | KB61 | Repost CO line items (correct mis-postings) | No |
| 2 | KGI2 | Calculate actual overhead | No |
| 3 | KSU5 | Run assessment cycles | No |
| 4 | KSV5 | Run distribution cycles | No |
| 5 | KO88 | Settle internal orders | Only if receiver = GL or asset (cat 22) |
| 6 | CO88 | Settle production orders | Only if receiver = GL or asset |
| 7 | KSII | Calculate actual activity prices | No |
| 8 | KALC | Reconciliation posting (cross-CC) | Yes — intercompany FI documents |
| 9 | — | Lock CO period | No |

Cross-reference: For the detailed CO period-end sequence (9-step with dependencies), see `modules/co/processes.md` Section 5. For FI period-end close details, see `modules/fi/processes.md`. For MM period-end close (MMPV, CKMLCP), see `modules/mm/integration.md` Section 5.

---

## 6. S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on Integration |
|----------------|----------------|----------------------|
| Primary CE = GL account (same number, separate master data) | GL accounts serve as cost elements (no separate CSKA/CSKB) | Same FI->CO flow; KA01/KA06 obsolete |
| CO documents in COBK/COEP | CO data in Universal Journal (ACDOCA) | Same T-codes; different storage |
| PCA separate ledger (GLPCA) | PCA in ACDOCA | No FI-PCA reconciliation gap |
| Reconciliation ledger (COFIT/COFIS, KALC) | Eliminated — ACDOCA handles cross-CC natively | KALC no longer needed |
| Controlling Area can span many company codes | 1:1 CA to CC strongly recommended | Less cross-CC complexity |
| OKB9 default account assignment | Same OKB9 (still needed) | No change |
| Category 22 external settlement creates FI doc | Same mechanism | No change to settlement-FI flow |

> **Summary of S/4HANA impact on CO-FI integration:** The fundamental FI->CO real-time integration is unchanged — P&L postings still create CO documents via cost elements. The CO->FI direction (settlement with category 22) is also unchanged. The major eliminations are the reconciliation ledger (KALC) and the PCA separate ledger (GLPCA), both made unnecessary by the Universal Journal. For consultants migrating from ECC to S/4: the integration concepts transfer directly, but the reconciliation and PCA reconciliation steps disappear from period-end procedures.

---

## See Also

- `cross-module/record-to-report.md` -- Full R2R end-to-end flow with cross-module period-end ordering
