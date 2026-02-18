---
module: cross-module
content_type: checklists
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

# Period-End Close Checklists

> ECC 6.0 operator-facing reference. Checkbox format with specific T-codes and business-day timing. Every step names the exact transaction code. For the architectural view of why this ordering matters, see `cross-module/record-to-report.md`. For S/4HANA differences, see the S/4HANA Differences section at the end.

---

## Month-End Close Checklist

> Cross-module ordering is mandatory: MM must close before CO, and CO must close before FI. Running steps out of order causes allocation amounts to be incorrect or settlements to fail. See `cross-module/record-to-report.md` for the dependency explanation.

### Day -5 to Day -3 (Pre-Close Preparation)

- [ ] Review all open purchase orders for goods received but not yet posted (ME2M) -- confirm all GRs are posted before cutoff
- [ ] Post all remaining goods receipts and returns (MIGO) -- confirm MIGO entry complete for the period
- [ ] Post all remaining goods issues and internal transfers (MIGO) -- confirm no pending 201/261/301 movements
- [ ] Confirm vendor invoices received -- post or park pending invoices (MIRO) -- verify MIRO completeness via MR11 preview
- [ ] Plan accruals for expenses incurred but not yet invoiced (FBS1) -- reversing accrual postings to be reversed on Day 1 of next period
- [ ] Check for negative stock by material and storage location (MMBE) -- negative stock prevents period close in some configurations
- [ ] Review billing due list and trigger billing for all deliveries ready for invoicing (VF04) -- confirm all period-end billing is complete
- [ ] Verify all SD deliveries have PGI posted -- no open deliveries with unpaid goods issue (VL06G) -- confirm goods issue status

---

### Day 1 (MM Period-End)

> MM must close first. All goods movements and invoice verifications for the closing period must be complete before running MMPV.

- [ ] Run GR/IR automatic clearing to match open GR/IR pairs (F.13) -- clears matched GR/IR open items on the WRX clearing account
- [ ] Run GR/IR maintenance for one-sided items that cannot be automatically cleared (MR11) -- review and write off residual unmatched items only if appropriate; requires authorization
- [ ] Verify GR/IR clearing account balance -- confirm remaining open items are expected timing differences (MB5S) -- run GR/IR balance list
- [ ] Close the MM posting period for the closing month (MMPV) -- opens the new MM period and prevents further goods movements in the closed period
- [ ] Open the new FI posting period for account type M (materials management) (OB52) -- MMPV alone does NOT open FI; both must be maintained separately
- [ ] Run Material Ledger actual costing close (CKMLCP) -- only if Material Ledger is activated for the plant; redistributes price variances between inventory and COGS; run after MMPV

---

### Day 1-2 (FI Period-End)

> FI accruals and valuations must be complete before CO period-end starts. CO allocations use GL balances at time of execution -- FI postings after CO allocations will not be included.

- [ ] Post foreign currency revaluation for open items and GL balances at the closing exchange rate (F.05 or FAGL_FC_VAL) -- use FAGL_FC_VAL if New GL is active
- [ ] Post period-end accruals and deferrals not already handled by MM/SD (FBS1) -- recurring accruals for rent, insurance, and other overhead; set reversal date to first day of next period
- [ ] Run depreciation posting for the closing period (AFAB) -- posts depreciation for all asset classes; verify no errors in AFAB log before proceeding
- [ ] Clear open items on AR sub-ledger (F-32) -- clear customer open items where payment is received; confirm FBL5N open items are current
- [ ] Clear open items on AP sub-ledger (F-44) -- clear vendor open items where payment is posted; confirm FBL1N open items are current
- [ ] Verify GL balances are complete and reasonable (FAGLB03) -- spot check key expense and revenue accounts before CO period-end starts

---

### Day 2-3 (CO Period-End)

> CO period-end must run in the sequence below. Each step depends on the prior step's output. Do NOT reorder.

- [ ] Repost any CO line item mis-assignments from the period (KB61) -- move costs from catch-all cost centers to the correct CO objects; run BEFORE any allocations
- [ ] Calculate actual overhead on internal orders and cost centers (KGI2) -- applies overhead surcharges defined in the costing sheet; run after reposting so overhead is calculated on corrected balances
- [ ] Run assessment cycles in TEST mode, review results, then execute LIVE (KSU5) -- allocates overhead cost center costs to receivers using secondary cost element (category 42); verify sender balances and receiver amounts in test output before live run
- [ ] Run distribution cycles in TEST mode, review results, then execute LIVE (KSV5) -- distributes costs preserving original cost elements; run after assessment; note: distribution cannot process secondary cost elements
- [ ] Settle internal orders in TEST mode, review results, then execute LIVE (KO88) -- transfers costs from internal orders to permanent receivers per settlement rules; verify settlement rules exist on all open orders before live run
- [ ] Calculate work-in-process for open production orders (KKAX or KKA2) -- required BEFORE production order settlement if PP is active; calculates WIP for orders not yet delivered
- [ ] Settle production orders in TEST mode, review results, then execute LIVE (CO88) -- only if PP is active; run after WIP calculation (KKAX/KKA2)
- [ ] Calculate actual activity prices from period-end actual costs and quantities (KSII) -- determines actual cost rates for activity types; run after all allocations and settlements are complete
- [ ] Execute profit center transfer pricing if configured (1KEG) -- only if PCA transfer pricing is active; run after all settlements
- [ ] Run reconciliation ledger posting for cross-company-code CO allocations (KALC) -- only if controlling area spans multiple company codes; creates FI intercompany documents for cross-CC cost flows; run after all settlements, before period lock
- [ ] Lock the CO period to prevent further postings (OKP1) -- set the posting period status to locked for CO; verify all CO postings are complete before locking

---

### Day 3-4 (Verification and Reporting)

- [ ] Run cost center plan/actual comparison and review variances (S_ALR_87013611) -- primary management report; identify cost centers with significant variance from plan
- [ ] Review CO actual line items for catch-all cost centers to confirm no residual mis-postings remain (KSB1) -- filter by catch-all cost center number; repost any remaining items found
- [ ] Reconcile PCA report against FI general ledger -- compare KE5Z (PCA actuals, reads GLPCA) with FAGLB03 (FI actuals) -- totals should match for primary cost elements; differences indicate missing profit center assignments on FI postings
- [ ] Verify GR/IR clearing account status after all clearing runs (MB5S) -- confirm remaining open items are genuine timing differences, not errors
- [ ] Lock the FI posting period for the closed month to prevent further postings (OB52) -- set posting period to closed for account type + (all); this is the final step; verify all upstream postings are complete before locking
- [ ] Distribute period-end management reports to stakeholders -- confirm S_ALR_87013611 and KE5Z output is delivered

---

## Year-End Close Checklist

> Year-end close = complete the Month-End Close Checklist above for fiscal period 12, then execute the additional steps below. The additional steps perform fiscal year rollover and prepare the new fiscal year for posting.

**Prerequisite:** All Month-End steps for period 12 must be complete and verified before proceeding with year-end-only steps.

---

### Year-End-Only Steps

- [ ] Confirm depreciation for all periods (01-12) of the closing fiscal year is posted completely (AFAB) -- run AFAB in test mode for each period where depreciation may be missing; do not proceed to AJAB until depreciation is fully posted for all 12 periods
- [ ] Run asset fiscal year close (AJAB) -- closes the fixed assets subledger for the fiscal year; posts final depreciation and prepares assets for the new fiscal year; CRITICAL: AJAB is irreversible in many configurations -- verify depreciation is complete before running; once AJAB runs, no further depreciation changes are possible for the closed year
- [ ] Carry forward GL balances from the closing year to the new fiscal year (FAGLGVTR for New GL, or F.16 for classic GL) -- posts opening balances for balance sheet accounts in the new fiscal year; P&L accounts are zeroed out against the retained earnings account
- [ ] Carry forward AR open items and customer balances to the new fiscal year (F.07) -- transfers customer open items; must run before customer statements for the new year
- [ ] Carry forward AP open items and vendor balances to the new fiscal year (F.16) -- transfers vendor open items to the new fiscal year; F.16 handles both GL carryforward (classic GL) and AP carryforward
- [ ] Lock all CO periods for the closed fiscal year (OKP1) -- set all 12 periods of the closed year to locked status; prevents any further CO postings to the closed year
- [ ] Open the new FI posting period for the new fiscal year (OB52) -- set posting period status to open for all required account types (A, D, K, M, S) for the new fiscal year periods
- [ ] Open the new MM period for the first period of the new fiscal year (MMPV) -- allows goods movements in the new fiscal year; run after OB52 opens the FI period
- [ ] Copy CO planning data from the closed year to the new fiscal year if needed (KP97 for primary cost plan copy, KP98 for activity type plan copy) -- optional but commonly used to seed new fiscal year planning from prior year actuals or plan; run before the first planning cycle of the new year

---

### Year-End Verification

- [ ] Verify new fiscal year opening balances in FAGLB03 -- confirm balance sheet accounts carry forward correctly; confirm P&L accounts start at zero
- [ ] Verify AR balance carryforward -- compare FBL5N open items in new year against expected customer balances
- [ ] Verify AP balance carryforward -- compare FBL1N open items in new year against expected vendor balances
- [ ] Verify asset opening values in the new fiscal year (AW01N or AS03) -- confirm asset net book values match closing values from prior year
- [ ] Confirm new fiscal year CO periods are open for planning and actual postings (OKP1) -- verify period status is not locked for periods 01-12 of the new year

---

## Cross-References

- **Architecture and dependency explanation:** `cross-module/record-to-report.md` -- why this ordering is mandatory, what each module handoff means, and cross-module reconciliation
- **CO period-end detailed sequence:** `modules/co/processes.md` Section 5 -- 9-step sequence with dependency rules
- **FI period-end narrative:** `modules/fi/processes.md` Section 2 -- FI month-end close process
- **MM period-end narrative:** `modules/mm/integration.md` Section 5 -- 8-step MM-FI close sequence
- **GR/IR clearing detail:** `modules/mm/integration.md` Section 4 -- F.13/MR11/MB5S detail
- **CO-FI reconciliation:** `modules/co/co-advanced.md` Section "CO-FI Reconciliation Walkthrough" -- 5-step reconciliation process

---

## S/4HANA Differences

| ECC 6 Step | S/4HANA Change | Checklist Impact |
|------------|----------------|-----------------|
| F.05 foreign currency revaluation | FAGL_FC_VAL is the standard transaction; F.05 still available | Use FAGL_FC_VAL in S/4HANA; same timing in close sequence |
| Material Ledger (CKMLCP) optional -- only if ML activated | Material Ledger mandatory for all plants | CKMLCP is always required in S/4HANA; cannot skip |
| KALC reconciliation ledger posting for cross-CC CO | Eliminated -- Universal Journal handles cross-CC natively | Remove KALC step from S/4HANA checklist; intercompany postings are automatic |
| KE5Z vs FAGLB03 PCA-FI reconciliation step | PCA in ACDOCA -- no separate PCA ledger (GLPCA eliminated) | PCA-FI reconciliation step is eliminated in S/4HANA; KE5Z reads ACDOCA directly |
| FAGLGVTR for New GL balance carryforward | Same transaction | No change |
| F.16 for classic GL carryforward | Classic GL not available in S/4HANA | Use FAGLGVTR only in S/4HANA; F.16 for classic GL is N/A |
| OB52 period locking | Same transaction | No change |
| MMPV MM period management | Same transaction | No change |
| AJAB asset fiscal year close | Same transaction | No change |
