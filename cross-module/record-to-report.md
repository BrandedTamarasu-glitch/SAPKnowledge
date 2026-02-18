---
module: cross-module
content_type: e2e-process
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-18
related_modules:
  - fi
  - co
  - mm
  - sd
---

# Record-to-Report (R2R) -- End-to-End Process

> ECC 6.0. The R2R process is not a single document chain like P2P or O2C -- it is a **period-end orchestration** across all four modules with strict ordering dependencies. This document covers the complete cross-module close sequence. For S/4HANA differences, see the S/4HANA Differences section below.

## Prerequisites

Read these module files for full detail on individual module close steps:

- `modules/mm/integration.md` Section 5 -- Period-End MM-FI Sequence (8 steps: MIGO/MIRO completions, F.13, MR11, MMPV, CKMLCP)
- `modules/sd/integration.md` Section 5 -- Period-End SD-FI Sequence (7 steps: VF04, VBO1/VBOF, FBS1 accruals, rebate settlement)
- `modules/co/processes.md` Section 5 -- Period-End CO Closing Sequence (9 steps: KB61 through period lock)
- `modules/co/integration.md` Section 5 -- CO-FI Integration and timing diagram
- `modules/fi/processes.md` Section 2 -- Month-End Close (F.05, FBS1, F.13, AFAB, OB52)
- `modules/co/co-advanced.md` Section "Reconciliation Ledger" -- CO-FI reconciliation via KALC (COFIT/COFIS tables)

## Document Chain

R2R is a period-end sequence, not a single document flow. The orchestration moves through four module phases with strict ordering:

```
MM Cutoffs  ->  SD Cutoffs  ->  CO Allocations/Settlement  ->  FI Valuations/Close
 MMPV/CKMLCP    VF04/VBO1      KSU5/KSV5 -> KO88/CJ88        F.05/F.13/AFAB/OB52
 [MM]            [SD]           [CO]       [CO -> FI]          [FI]
```

## Ordering Dependencies

The ordering is not arbitrary -- each phase depends on the prior phase's output:

1. **MM must close before CO** -- CO needs all material cost variances, GR/IR clearing adjustments, and material ledger actual costs finalized. If CKMLCP runs after CO allocations, the actual material costs used in CO are incomplete.

2. **SD must close before CO** -- CO needs all revenue postings and COGS entries finalized. If billing (VF04) runs after CO settlement, revenue and cost-of-sales are not fully reflected in profitability analysis.

3. **CO must close before FI** -- CO settlement (KO88/CJ88) generates FI postings via category 22 cost elements. These postings must land in the GL before FI runs foreign currency revaluation, automatic clearing, and period close. If FI closes before CO settles, the GL is incomplete.

4. **FI closes last** -- FI period close (OB52) locks the posting periods. All upstream module postings must be complete, because once OB52 closes the period, no further postings are possible without reopening.

**Dependency diagram:**

```
MM Period-End (complete all goods movements, invoices, ML closing)
  |
  v
SD Period-End (complete all billing, rebate settlement, accruals)
  |
  v
CO Period-End (allocations, settlement -- generates FI postings)
  |
  v
FI Period-End (valuations, clearing, depreciation, close periods)
```

## Process Flow

### Phase 1: MM Period-End Cutoffs

Complete all MM transactions for the closing period and run MM-specific period-end activities.

| Step | Activity | T-code | Purpose |
|------|----------|--------|---------|
| 1 | Post all remaining goods movements and invoices | MIGO, MIRO | Complete all open receipts and invoices for the period |
| 2 | Run GR/IR automatic clearing | F.13 | Clear matched GR/IR pairs on the clearing account |
| 3 | Run GR/IR maintenance for one-sided items | MR11 | Write off residual unmatched GR/IR items (if appropriate) |
| 4 | Run price changes if needed | MR21, MR22 | Adjust standard prices or material values |
| 5 | Open the new MM period | MMRV/MMPV | MMPV opens the new MM period and closes the old; MMRV allows emergency posting to a closed period |
| 6 | Open the new FI period for account type M | OB52 | Allows FI documents from MM in the new period |
| 7 | Run Material Ledger actual costing (if ML active) | CKMLCP | Redistributes variance between inventory and COGS; creates postings in new period |
| 8 | Verify GR/IR clearing account status | MB5S | Confirm remaining open items are expected |

> **CRITICAL:** MMPV and OB52 are independent controls. Opening the MM period via MMPV does NOT open the FI posting period. Both must be managed separately. See `modules/mm/integration.md` Section 5 for full detail.

**Handoff to SD:** Once all MM postings are complete and CKMLCP has finalized actual material costs, SD period-end can proceed.

---

### Phase 2: SD Period-End Cutoffs

Complete all SD billing and revenue-related activities for the closing period.

| Step | Activity | T-code | Purpose |
|------|----------|--------|---------|
| 1 | Process billing due list | VF04 | Create billing documents for all deliveries ready for invoicing |
| 2 | Settle rebate agreements (if applicable) | VBO1 / VBOF | Partial or final rebate settlement creates credit memos |
| 3 | Post revenue accruals for unbilled deliveries | FBS1 | Accrue revenue for goods shipped but not yet billed (Dr Unbilled Receivables / Cr Accrued Revenue) |
| 4 | Post COGS accruals for billed-not-shipped | FBS1 | Accrue COGS for billed items where PGI has not yet posted |
| 5 | Verify SD-FI document flow completeness | VF05, FBL5N | Confirm all billing documents created FI accounting documents |

> Rebate settlement (VBO1/VBOF) creates credit memos that flow to FI as customer open items. These must post before CO allocations to ensure complete revenue picture.

**Handoff to CO:** Once all SD billing and accruals are posted, all revenue and COGS are in the GL. CO can now run allocations and settlement knowing the complete cost and revenue picture.

---

### Phase 3: CO Allocations and Settlement

Execute CO period-end processing in the prescribed sequence. This phase generates FI postings via settlement.

| Step | Activity | T-code | Purpose | Dependencies |
|------|----------|--------|---------|--------------|
| 1 | Repost CO line items | KB61 | Correct mis-postings before allocations | Must run first |
| 2 | Calculate actual overhead | KGI2 | Apply overhead surcharges to orders/cost centers | After reposting |
| 3 | Run assessment cycles | KSU5 | Allocate overhead costs using secondary CE (cat 42) | After overhead calc |
| 4 | Run distribution cycles | KSV5 | Allocate costs preserving original cost elements | After overhead calc |
| 5 | Settle internal orders | KO88 | Transfer collected costs to permanent receivers | After allocations |
| 6 | Settle production orders (if PP active) | CO88 | Settle production order costs (after WIP/RA via KKAX) | After WIP calculation |
| 7 | Settle project orders (if PS active) | CJ88 | Settle WBS element costs to receivers | After allocations |
| 8 | Calculate actual activity prices | KSII | Determine actual cost rates for activity types | After all allocations/settlements |
| 9 | Execute transfer pricing (if configured) | 1KEG | Profit center transfer pricing | After all settlements |

> **CO -> FI handoff:** Settlement (KO88/CO88/CJ88) with category 22 cost elements creates FI documents. These are the CO postings that must land in the GL before FI closes. Internal settlement (category 21) stays within CO and has no FI impact.

> **Cross-company-code reconciliation:** If the controlling area spans multiple company codes, run KALC (reconciliation ledger posting) after all CO allocations to create the intercompany FI entries that balance cross-company-code cost flows. See `modules/co/co-advanced.md` Reconciliation Ledger section for the 3-step KALC process (COFIT/COFIS tables).

**Handoff to FI:** Once all CO settlements are posted and KALC has reconciled cross-CC flows, the GL contains the complete period picture. FI can now run final valuations and close.

---

### Phase 4: FI Period-End Close

Execute FI-specific period-end activities and lock the posting periods.

| Step | Activity | T-code | Purpose |
|------|----------|--------|---------|
| 1 | Foreign currency revaluation | F.05 (or FAGL_FC_VAL) | Revalue open items and GL balances in foreign currencies at closing rate |
| 2 | Post accruals and deferrals | FBS1 | Post recurring accruals (rent, insurance, etc.) not already handled by MM/SD accruals |
| 3 | Run automatic clearing (including GR/IR) | F.13 | Clear matched open items on clearing accounts; includes any residual GR/IR from MM |
| 4 | Run asset depreciation | AFAB | Post periodic depreciation for fixed assets (AJAB/AJRW for year-end) |
| 5 | Close posting periods | OB52 | Lock the closed period to prevent further postings |

> **Year-end additional steps:** At fiscal year-end, additional steps include balance carry-forward (FAGLGVTR or F.16), annual asset closing (AJAB/AJRW), and financial statement preparation. These extend Phase 4 but do not change the cross-module ordering.

> See `modules/fi/processes.md` Section 2 for the full FI Month-End Close narrative.

---

## Reconciliation

After all four phases complete, verify cross-module consistency:

### CO-FI Reconciliation

- **Primary cost elements:** Run KSB1 (CO line items) filtered by primary cost elements only (categories 1, 3, 4, 11, 12) and compare against FBL3N/FAGLB03 for the same GL accounts. These totals MUST match. Differences indicate missing cost elements or wrong cost center assignments.

- **Secondary cost elements:** CO totals (KSB1 all CEs) will always be HIGHER than FI totals because secondary CEs (categories 21, 31, 41, 42, 43) exist only in CO. This is expected -- not an error.

- **Reconciliation ledger (if cross-company-code):** Run KAL1 to display COFIT/COFIS entries. Verify KALC reconciliation postings created the correct intercompany FI documents.

See `modules/co/co-advanced.md` CO-FI Reconciliation Walkthrough for the full 5-step reconciliation process.

### PCA-FI Reconciliation

- Compare KE5Z (PCA report, reads GLPCA) against FAGLB03 (FI report, reads FAGLFLEXT). If totals differ, some FI postings lack profit center assignments. Check CSKS-PRCTR on cost centers, 1KEF substitution rules, and document splitting configuration.

### MM-FI Reconciliation

- Run MB5S (GR/IR balance list) to verify remaining open items on the GR/IR clearing account are expected timing differences, not errors.

---

## Cross-Module Troubleshooting

Common R2R period-end issues that span module boundaries.

| Issue | Root Cause | Resolution |
|-------|-----------|------------|
| CO settlement (KO88) fails with "posting period not open" | FI posting period for the target GL account is closed in OB52, but CO settlement needs to post | Open the required posting period in OB52 (account type S for GL, or + for all); verify both old and new periods are open during close window |
| CKMLCP actual costing errors prevent MM close | Material ledger closing has errors (missing prices, unfinished transactions in closed period) | Review CKMLCP error log; post or reverse open MIGO/MIRO documents for the period; rerun CKMLCP |
| CO allocations include incomplete cost picture | MM or SD period-end ran after CO allocations, adding costs that were not included | Rerun CO allocations (KSU5/KSV5 can be reversed and re-executed); enforce strict phase ordering |
| GR/IR account balance does not reconcile after F.13 | One-sided items (GR without invoice, or invoice without GR) remain after automatic clearing | Run MR11 for genuine one-sided items; run MB5S to identify remaining open items; see `modules/mm/integration.md` Section 4 |
| KE5Z (PCA) differs from FAGLB03 (FI) | FI postings missing profit center assignment -- PCA separate ledger incomplete | Check cost center profit center assignments (CSKS-PRCTR); verify 1KEF substitution rules; run 1KEK for retroactive PCA transfer |

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on R2R Flow |
|----------------|----------------|-------------------|
| Material Ledger optional (CKMLCP only if activated) | Material Ledger mandatory | CKMLCP always required in Phase 1; actual costing always available |
| PCA separate ledger (GLPCA) requires reconciliation with FI | Universal Journal (ACDOCA) eliminates separate PCA ledger | PCA-FI reconciliation step eliminated; KE5Z reads from ACDOCA |
| Reconciliation ledger (COFIT/COFIS, KALC) for cross-CC CO | Eliminated -- ACDOCA handles cross-CC natively | KALC step eliminated from Phase 3; intercompany postings automatic |
| CO documents in COBK/COEP | CO data in ACDOCA | Same T-codes; different storage; no functional change to period-end sequence |
| Separate FI and CO period locks | Unified period management | Fewer period control points; same sequential close logic |
| Classic GL or New GL | Universal Journal only | All module postings go to ACDOCA; simpler reconciliation |
| Period-end still sequential (MM -> SD -> CO -> FI) | Same ordering required | Cross-module dependencies unchanged; fewer reconciliation steps needed |
