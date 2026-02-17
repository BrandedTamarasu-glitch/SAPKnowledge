---
module: fi
content_type: decision-trees-and-troubleshooting
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-16
---

# Financial Accounting — Decision Trees & Troubleshooting

> ECC 6.0 reference. Decision trees guide FI configuration choices during implementation. Troubleshooting covers implementation pitfalls (setup mistakes) and symptom-based diagnosis (production issues).

## Configuration Decision Trees

> Each decision tree has two parts: (1) Q&A routing — answer yes/no questions to reach the recommended approach, then (2) a comparison table explaining each approach with config implications and trade-offs.

---

### Decision Tree 1: New GL Ledger Strategy

**Q1: Is New GL activated in your system?**
- No → This is a Classic GL environment; New GL ledger strategy does not apply. Consider a migration project if needed.
- Yes → Continue to Q2.

**Q2: Do you need to report balance sheets by profit center or segment?**
- Yes → You need document splitting (see Decision Tree 3 for document splitting scope). Continue to Q3 regardless.
- No → Continue to Q3.

**Q3: Do you need to maintain parallel sets of financial statements under different accounting principles (e.g., IFRS + local GAAP)?**
- Yes → Use non-leading ledgers (Approach B below).
- No → Leading ledger only (Approach A below).

| Approach | When to Use | Config Path | Trade-offs |
|----------|-------------|-------------|------------|
| A: Leading ledger only (0L) | Single accounting principle; differences handled externally or are immaterial | Default — no additional config | Simplest; cannot carry parallel depreciation or different posting rules within SAP |
| B: Leading + non-leading ledger(s) | Material permanent differences between reporting frameworks (IFRS vs local GAAP) | SPRO → Financial Accounting (New) → General Ledger Accounting (New) → Ledgers → Ledger → Define and Activate Non-Leading Ledgers | Each non-leading ledger can have own fiscal year variant and posting period variant; more complex period-end close; asset depreciation areas must align to ledger assignments |

---

### Decision Tree 2: Parallel Accounting

**Q1: Do you report under multiple accounting principles (e.g., IFRS and local GAAP) with material differences?**
- No → Single-principle approach — use leading ledger only (Decision Tree 1, Approach A).
- Yes → Continue to Q2.

**Q2: Are the differences limited to depreciation/asset valuation, or do they extend to revenue recognition, provisions, and other areas?**
- Depreciation/asset valuation only → Consider separate depreciation areas in Asset Accounting (OAOB) without a non-leading ledger.
- Broader differences → Use non-leading ledgers (configure per Decision Tree 1, Approach B).

**CRITICAL CLARIFICATION:** Document splitting is NOT a parallel accounting approach. Document splitting enables segment-level and profit center-level balance sheet reporting within a single accounting principle. It does not carry parallel sets of accounting entries under different GAAP frameworks. The two decisions are:
1. **Parallel accounting** = Do I need multiple sets of books? (This decision tree)
2. **Document splitting** = Do I need balance sheets by profit center/segment? (Decision Tree 3)

These are related but distinct. A company may need both, one, or neither.

| Approach | When to Use | Config Implications | Trade-offs |
|----------|-------------|---------------------|------------|
| Single principle (leading ledger only) | Differences immaterial or handled outside SAP | No non-leading ledger config | Cannot produce parallel financials within SAP |
| Parallel depreciation areas only | Only asset valuation differs between standards | Additional depreciation areas in OAOB/AFAMA; no non-leading ledger needed | Simpler than full parallel; limited to AA differences |
| Full parallel ledgers | Broad differences across multiple areas (depreciation, provisions, revenue) | Non-leading ledger(s) per Decision Tree 1; ledger-specific posting rules; separate period-end per ledger | Most powerful; most complex — every period-end activity must consider all ledgers |

---

### Decision Tree 3: Document Splitting Scope

*(Linked from Decision Trees 1 and 2 — document splitting is about segment/profit center reporting, not parallel GAAP.)*

**Q1: Does your organization need to produce balance sheets by profit center, segment, or business area?**
- No → Document splitting not needed.
- Yes → Continue to Q2.

**Q2: Is document splitting already activated in this client?**
- Yes → Proceed to configure splitting characteristics and GL account classification.
- No → CRITICAL: Activation is client-wide and irreversible (all company codes affected). Plan carefully before activating.

**Q3: Which characteristics need zero-balance enforcement?**
- Typically profit center and segment. Each zero-balance characteristic requires a dedicated zero-balance clearing account.

| Approach | When to Use | Config Path | Trade-offs |
|----------|-------------|-------------|------------|
| No document splitting | No sub-entity balance sheet requirement | No action needed | Cannot report balance sheet by profit center or segment |
| Splitting on segment only | Segment reporting required (IFRS 8 / ASC 280) | Activate splitting → define segment as characteristic → classify GL accounts and document types | Simpler; fewer zero-balance clearing entries |
| Splitting on segment + profit center | Both segment and profit center balance sheets needed | Both characteristics active; both need zero-balance clearing accounts | More comprehensive; more clearing account postings; more complex troubleshooting (see Troubleshooting section) |

---

### Decision Tree 4: Reconciliation Account Assignment

**Q1: Do all vendors (or customers) in a company code post to the same reconciliation GL account?**
- Yes → Single recon account is sufficient.
- No → Continue to Q2.

**Q2: Do you need separate GL balances for categories of vendors/customers (e.g., domestic vs intercompany vs employee)?**
- Yes → Use multiple reconciliation accounts.
- No → A single recon account may still be sufficient; evaluate reporting requirements.

*Note: Reconciliation account assignment is per vendor/customer master record (LFB1.AKONT for vendors, KNB1.AKONT for customers). It is NOT configured via a mapping table — each master record individually points to its recon GL account.*

| Approach | When to Use | Config Implications | Trade-offs |
|----------|-------------|---------------------|------------|
| Single recon account per company code | Small vendor/customer base; no need for AP/AR sub-classification on balance sheet | One GL account (e.g., 160000 for AP) flagged as reconciliation in FS00 | Simplest; all vendors appear under one balance sheet line |
| Multiple recon accounts by type | Need to separate domestic (160000), intercompany (161000), employee (162000) on balance sheet | Multiple GL accounts, each flagged as reconciliation (SKB1.XINTIT); assigned per vendor master (LFB1.AKONT) | Better reporting granularity; requires discipline in master data maintenance; changing a vendor's recon account requires clearing all open items first |

---

### Decision Tree 5: Payment Terms Design

**Q1: How many distinct payment term combinations exist across your vendor and customer base?**
- Fewer than 10 → SAP-delivered terms may suffice. Evaluate before creating custom terms.
- 10 or more → Create custom Z-terms.

**Q2: Do any payment terms require installment payments (split into multiple due dates)?**
- Yes → Configure installment payment terms (multi-line payment terms in OBB8).
- No → Standard single-line terms.

**Q3: What is the baseline date for due date calculation?**
- Document date (most common), posting date, or fixed day of month. Set per payment term in OBB8.

| Approach | When to Use | Config Path (OBB8) | Trade-offs |
|----------|-------------|---------------------|------------|
| SAP standard terms (0001, 0002, etc.) | Fewer than 10 combinations; standard net 30/60/90 patterns | Use delivered terms; modify descriptions if needed | Risk of overloading SAP defaults; may conflict with SAP upgrade deliveries |
| Custom Z-terms (Z001, Z030, etc.) | Many combinations; company-specific discount tiers | Create new entries in OBB8 with Z prefix; assign baseline date type | Clear separation from SAP defaults; more maintenance |
| Installment terms | Split payments (e.g., 50% on delivery, 50% in 30 days) | Multi-line configuration per term in OBB8; each line = installment with percentage and days | Installment line items appear separately in F110 proposal; more complex payment processing |

---

### Decision Tree 6: Tolerance Group Design

**Q1: Do all users have the same posting amount limits?**
- Yes → Configure the blank (default) tolerance group only.
- No → Continue to Q2.

**Q2: How many tiers of posting authority exist?**
- Typically 2-3: junior accountant, senior accountant, manager.

**Q3: Do you need separate tolerance limits for AP invoice approval vs general GL posting?**
- Yes → Configure OBA3 (GL/vendor tolerance) and OBA4 (customer tolerance) separately.
- No → Consistent limits across both.

| Approach | When to Use | Config Path | Trade-offs |
|----------|-------------|-------------|------------|
| Default group only (blank key) | All users same authority | OBA3/OBA4 → blank key → set limits | Simplest; no user assignment needed (blank = everyone) |
| 2-3 groups by authority level | Different posting limits by role | OBA3/OBA4 → create groups (e.g., JR, SR, MGR) → set limits per group → assign users via OB57 | Good balance of control vs maintenance |
| Many groups (5+) | Complex approval structures | Same config path; more groups | High maintenance; user changes require OB57 updates; consider using SAP workflow instead for complex approvals |

---

### Decision Tree 7: Asset Class Strategy

**Q1: How many distinct types of fixed assets does the organization own?**
- Count major categories: buildings, vehicles, machinery, IT equipment, furniture, leasehold improvements, etc.

**Q2: Do different asset types require different GL accounts (balance sheet and depreciation expense)?**
- Yes → Each GL grouping needs its own account determination key, and likely its own asset class.
- No → Broader classes may suffice.

**Q3: Do different asset types have different default useful lives?**
- Yes → Separate classes help prevent errors (users inherit correct defaults from class).
- No → Broader asset classes remain an option.

| Approach | When to Use | Config Path | Trade-offs |
|----------|-------------|-------------|------------|
| Broad (3-5 classes) | Small organization; few asset types; similar useful lives | OAOA → create classes → AO90 → assign GL accounts per class | Simpler AO90 and OAOA maintenance; fewer number ranges; risk of wrong defaults if asset types vary |
| Granular (10-20 classes) | Large organization; many asset types; different useful lives and GL accounts per type | Same path; more classes, more AO90 entries, more number ranges (OAOA) | Correct defaults reduce user error; better reporting granularity; more config to maintain |
| Very granular (20+) | Detailed regulatory reporting requirements; asset register used for insurance or tax | Same path; extensive setup | Maximum control; significant initial and ongoing maintenance |

---

## Implementation Pitfalls

> Organized by setup mistake. These are errors made during implementation that cause problems later. Avoid these during initial configuration.

### Pitfall 1: New GL vs Classic GL Transaction Confusion

**Mistake:** Using FS10N (reads GLT0 table) as the primary balance display in a New GL environment.

**Why it fails:** When New GL is active, GLT0 is not updated for most accounts. FS10N shows zero balances on accounts that have active postings. The consultant sees zeroes and assumes postings are missing — leading to incorrect diagnosis and potential duplicate entries.

**Prevention:** Use FAGLB03 (reads FAGLFLEXT) as the primary balance display in New GL environments. Use FAGLL03 instead of FBL3N when profit center or segment line-item detail is needed. FS10N should only be used in Classic GL environments.

**Cross-reference:** See tcodes.md — FS10N and FAGLB03 entries for detailed T-code guidance.

---

### Pitfall 2: Document Splitting Activation Without Complete Configuration

**Mistake:** Activating document splitting (client-level, irreversible) without completing all four downstream configuration steps.

**Why it fails:** Missing any of these steps causes posting errors:
1. Zero-balance clearing account not defined → GLT2201 error "Balancing field not filled"
2. GL accounts not classified (item category assignment missing) → system cannot determine how to split
3. Document types not classified (business transaction/variant missing) → splitting rules not applied
4. Zero-value base lines in source document → division by zero in proportional allocation (SAP Note 3035677)

**Prevention:** Complete ALL four steps before activating: (1) Define zero-balance clearing account, (2) Classify GL accounts for splitting, (3) Classify document types for splitting, (4) Test with representative documents in sandbox.

**Cross-reference:** See config-spro.md — New GL Configuration Steps 4-7 for the full SPRO paths.

---

### Pitfall 3: Asset Accounting Year-End Sequence Errors

**Mistake:** Running AJAB (year-end close) before AFAB (depreciation) is 100% complete, or before AJRW (fiscal year change) has opened the new year.

**Why it fails:** AJAB checks that all depreciation is posted. If AFAB has unposted items or error assets, AJAB fails with "depreciation not complete." If AJRW has not run, AJAB cannot close the old year because the new year is not open to receive carry-forward values.

**Prevention:** Mandatory sequence: AFAB (all periods, all assets — no errors) → AJRW (opens new year) → AJAB (closes old year). Run AFAB in test mode first. Fix error assets before live run. Check AW01N per asset if depreciation amounts look wrong.

**Cross-reference:** See tcodes.md — AFAB, AJRW, AJAB entries; see processes.md — Month-End Close step 4.

---

### Pitfall 4: F110 Automatic Payment Program Misconfiguration

**Mistake:** Incomplete FBZP configuration causing F110 proposals to miss items or fail bank selection.

**Why it fails:** F110 depends on FBZP for: (1) which company codes can pay, (2) which payment methods exist, (3) which bank accounts are available with how much money, (4) ranking order for bank selection. Missing any area causes silent failures — items are excluded without obvious error.

**Prevention:** Complete all 5 FBZP sub-areas before the first F110 run: All Company Codes, Paying Company Codes, Payment Methods in Country, Payment Methods in Company Code, Bank Determination. After each FBZP change, run F110 in proposal mode and review the payment log (Edit → Payment Run Log) to verify items are selected correctly.

**Cross-reference:** See config-spro.md — FBZP configuration; see processes.md — AP Payment Run; see tcodes.md — F110 entry.

---

### Pitfall 5: Posting Period Not Open for All Account Types

**Mistake:** Opening posting periods in OB52 for account type S (GL) but forgetting account type M (materials) or A (assets).

**Why it fails:** MIGO postings fail with "posting period not open" because account type M is closed even though S is open. Asset postings (AFAB, F-90) fail for the same reason with account type A. Users blame MIGO or AFAB when the root cause is OB52.

**Prevention:** When opening a new period, check ALL account types: S (GL), K (vendors), D (customers), A (assets), M (materials). The "+" wildcard row covers everything not explicitly listed, but explicit rows override it.

---

### Pitfall 6: Tolerance Group Mismatch

**Mistake:** Assigning a user to a tolerance group (OB57) with lower limits than their role requires, or not assigning them at all when the default (blank) group has restrictive limits.

**Why it fails:** Large invoices are blocked at posting time with a tolerance exceeded error. The user cannot post documents within their business authority.

**Prevention:** Document tolerance group assignments alongside user role assignments. Review OBA3/OBA4 limits when changing user responsibilities. Verify that the blank (default) tolerance group has appropriate limits before going live.

---

### Pitfall 7: GR/IR Account Not Set as Open-Item Managed

**Mistake:** Creating the GR/IR clearing account (e.g., 191100) without setting the open item management indicator in FS00.

**Why it fails:** F.13 automatic clearing requires open item management to match GR and IR postings. Without it, items post to the account but F.13 cannot clear them — the GR/IR balance grows indefinitely and never resolves.

**Prevention:** When creating the GR/IR clearing account in FS00, set Open Item Management = X and Line Item Display = X. This must be done BEFORE any postings; changing OI management on an account with existing postings requires clearing all items first.

---

## Troubleshooting — Symptom-Based Diagnosis

> Organized by what the consultant observes. Each entry: symptom → root cause → full resolution path. Self-contained — no need to cross-reference other files to fix the problem (though cross-references are provided for additional context).

### Symptom 1: FS10N Shows Zero Balances on Active Accounts

**Symptom:** FS10N displays zero balances for GL accounts that are known to have active postings (confirmed via FB03 or FBL3N).

**Root Cause:** FS10N reads the GLT0 table. In New GL environments, GLT0 is not updated — postings go to FAGLFLEXT instead. FS10N is looking at an empty or stale table.

**Resolution:**
1. Confirm New GL is active: check if FAGLB03 is available in the system (if it is, New GL is active)
2. Use FAGLB03 instead of FS10N for balance display — it reads FAGLFLEXT
3. For line items, use FAGLL03 instead of FBL3N when segment/profit center fields are needed
4. Note: Some systems auto-redirect FS10N to FAGLB03 via parameter FAGL_READ_GLT0_USER — check SU01 user parameters if behavior varies between users

---

### Symptom 2: GLT2201 Error — "Balancing Field Not Filled" During Document Posting

**Symptom:** Document posting fails with error GLT2201: "Balancing field 'Profit Center' in line item NNN not filled" (or 'Segment' instead of 'Profit Center').

**Root Cause:** Document splitting is active and requires zero balance per the named characteristic, but the posting line does not carry the required field value.

**Resolution:**
1. **Check zero-balance clearing account:** SPRO → Financial Accounting (New) → General Ledger Accounting (New) → Business Transactions → Document Splitting → Define Zero Balance Clearing Account. If missing, create one.
2. **Check GL account classification:** SPRO → Document Splitting → Classify G/L Accounts. The GL account on the failing line must be assigned an item category. If missing, assign one (01000 = balance sheet, 02000 = customer, 03000 = vendor, 04000 = cash).
3. **Check document type classification:** SPRO → Document Splitting → Classify Document Types. The document type must be assigned a business transaction and variant. If missing, assign one.
4. **Zero-value base lines:** If the error occurs on documents where proportional splitting has a zero-value base line (e.g., a zero-amount line item), this is a known SAP issue. Refer to SAP Note 3035677 for the correction program.

---

### Symptom 3: AJAB Fails With "Depreciation Not Complete"

**Symptom:** Asset year-end closing (AJAB) fails with message "Depreciation posting not complete for fiscal year YYYY."

**Root Cause:** AFAB has not been run for all periods, or error assets exist with unposted depreciation.

**Resolution:**
1. Run AFAB in test mode for the fiscal year to identify any unposted depreciation or error assets
2. Fix error assets: Check AW01N (Asset Explorer) for each error asset — compare planned vs posted depreciation
3. Re-run AFAB in live mode to post remaining depreciation
4. Verify AJRW has been executed (opens the new year) — AJAB will also fail if AJRW has not run
5. Check if ASKBN (Post Periodic Asset Value Postings) is required in your configuration
6. After all depreciation is posted and AJRW is done, retry AJAB

---

### Symptom 4: F110 Payment Proposal Does Not Pick Up Vendor Items

**Symptom:** F110 proposal run completes but specific vendor invoices that should be due for payment are not included in the proposal.

**Root Cause (check in this order):**
1. **Payment block on invoice:** Check FB03 → line item → payment block field. If set, item is excluded.
2. **Vendor master posting block or deletion flag:** Check FK03 or XK03 → SPERR (central block) and LFB1.ZAHLS. Any block excludes the vendor.
3. **Invoice not yet due:** Check FBL1N → net due date. If the due date is after the F110 "next payment date" parameter, the item is not picked up.
4. **Payment method missing on vendor master:** LFB1.ZWELS must include at least one payment method matching the F110 run parameters.
5. **Missing bank details on vendor master:** For bank transfer methods, vendor must have bank details in LFA1 bank data.
6. **Amount below minimum threshold:** FBZP → Paying Company Codes → minimum payment amount. Items below this are excluded silently.

**Resolution:**
1. Check the F110 payment log: Edit → Payment Run Log. The log shows exact exclusion reasons with SAP message codes for each skipped item.
2. Address the specific exclusion cause from the list above.
3. Delete the current proposal, fix the issue, and re-run the proposal.

---

### Symptom 5: F110 Bank Account Not Selected

**Symptom:** F110 payment run fails or selects the wrong bank account for outgoing payments.

**Root Cause:**
1. FBZP bank determination missing: No bank determination entry for the payment method + currency combination.
2. Available amount exhausted: FBZP bank determination has an available amount that has been fully consumed by prior payments.
3. Ranking order incorrect: Multiple bank accounts configured but ranking sends payments to the wrong bank.
4. Currency mismatch: Payment currency does not match any configured bank account currency.

**Resolution:**
1. Check FBZP → Bank Determination → verify entries exist for the payment method and currency
2. Check available amounts — reset or increase if needed (FBZP → Bank Determination → Available Amounts)
3. Review ranking order — adjust to prioritize the correct bank
4. For currency issues, add the payment currency to the bank master data or configure currency conversion

---

### Symptom 6: FBL1N Shows Vendor Items But F110 Does Not Pick Them Up

**Symptom:** FBL1N shows open items for a vendor that appear to be due, but F110 proposal excludes them.

**Root Cause:** Usually a mismatch between F110 parameter criteria and item attributes:
1. **Company code mismatch:** F110 parameters specify a different company code than where items reside
2. **Payment method filter:** F110 parameters restrict to a payment method not assigned on the vendor master
3. **Vendor number range filter:** F110 parameters exclude the vendor's number range
4. **Items posted after proposal:** Items posted after proposal generation are not included (by design)

**Resolution:**
1. Compare F110 Parameters tab criteria (company codes, payment methods, vendor ranges, next payment date) against the vendor master and open item attributes in FBL1N
2. Widen F110 criteria or update the vendor master to match

---

### Symptom 7: Balance Sheet Does Not Balance in F.01

**Symptom:** F.01 or S_ALR_87012284 financial statement output shows an out-of-balance condition (assets do not equal liabilities + equity).

**Root Cause:** The Financial Statement Version (FSV, configured in OB58) has unassigned GL accounts. Any GL account with a balance not assigned to a node in the FSV is excluded from output, causing an imbalance.

**Resolution:**
1. Run F.01 and check the "Not Assigned" node in the FSV tree — this shows which accounts have balances but no FSV assignment
2. Open OB58 → edit the FSV → assign the missing accounts to the correct balance sheet or P&L nodes
3. Re-run F.01 to verify the statement now balances
4. As a preventive measure: run the FSV assignment check whenever new GL accounts are created
