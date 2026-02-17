---
module: co
content_type: decision-trees-and-troubleshooting
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — Cost Element Mapping, Decision Trees & Troubleshooting

> ECC 6.0 reference. Cost element mapping walkthrough covers how primary cost elements bridge FI and CO, how secondary cost elements live CO-only, and how to reconcile CO totals with FI. Decision trees guide CO configuration choices. Troubleshooting covers symptom-based diagnosis of common CO issues. For cost element master data and category reference, see `modules/co/master-data.md`. For the OBYC (MM) and VKOA (SD) account determination frameworks, see `modules/fi/account-determination.md`.

---

## Cost Element Mapping and CO-FI Reconciliation

CO-FI integration is fundamentally different from the account determination frameworks in MM and SD:

- **OBYC (MM)** maps movement types to GL accounts — one direction: MM -> FI
- **VKOA (SD)** maps billing conditions to GL accounts — one direction: SD -> FI
- **CO-FI** is BIDIRECTIONAL: FI -> CO automatically via primary cost elements; CO -> FI only via category 22 external settlement

There is no single "account determination" transaction for CO. The integration is architectural, not configuration-based — it is built into the cost element master data and the controlling area assignment. Every P&L GL account that has a corresponding primary cost element automatically flows to CO on every posting. The only configuration decision is OKB9 (default account assignment), which sets the default CO receiver when the user does not enter one.

For the full cost element category table (all 11 categories with descriptions and examples), see `modules/co/master-data.md`. This section adds the **mapping walkthrough**: how each category drives data flow between CO and FI.

### Cost Element Mapping Table — All 11 Categories

| Category | Name | GL Account Required | Direction of Flow | FI Impact | CO Tables Updated |
|----------|------|--------------------|--------------------|-----------|-------------------|
| 1 | Primary costs/revenue | Yes (same number) | FI -> CO (automatic) | Every FI posting to this GL account creates a CO document | COBK, COEP, COSP |
| 3 | Accrual/deferral (FI side) | Yes | FI -> CO | FI accrual posts to this GL/CE; CO may have separate imputed cost via category 4 | COBK, COEP, COSP |
| 4 | Accrual/deferral (CO side) | Yes | CO accrual posting | CO imputed costs (calculated depreciation, calculated interest) | COBK, COEP, COSP |
| 11 | Revenue | Yes | FI -> CO | Revenue postings flow to CO (for cost-of-sales accounting / CO-PA) | COBK, COEP, COSP |
| 12 | Sales deduction | Yes | FI -> CO | Discount/rebate postings flow to CO | COBK, COEP, COSP |
| 22 | External settlement | Yes | CO -> FI | Settlement from order to GL account creates FI document | COBK, COEP, COSP + BKPF, BSEG |
| 21 | Internal settlement | No (CO-only) | CO internal | Settlement from order to cost center/order — no FI impact | COBK, COEP, COSS |
| 31 | Results analysis | No (CO-only) | CO internal | WIP and results analysis — no FI impact (unless posted to FI via RA) | COBK, COEP, COSS |
| 41 | Overhead rates | No (CO-only) | CO internal | Overhead surcharges from KGI2 — no FI impact | COBK, COEP, COSS |
| 42 | Assessment | No (CO-only) | CO internal | Assessment allocations from KSU5 — no FI impact | COBK, COEP, COSS |
| 43 | Activity allocation | No (CO-only) | CO internal | Activity allocations — no FI impact | COBK, COEP, COSS |

**How to read this table:**

- **Categories 1, 3, 4, 11, 12** (primary): These require a GL account with the same number. When FI posts to the GL account, CO automatically creates a corresponding document. Primary postings update COSP (primary totals table).
- **Category 22** (external settlement): The ONLY direction where CO creates an FI posting. When an internal order settles to a GL account (KO88 with receiver type KST), FI documents are created in BKPF/BSEG.
- **Categories 21, 31, 41, 42, 43** (secondary): CO-only. No GL account exists. These postings update COSS (secondary totals table) and never touch FI.

> **CRITICAL RECONCILIATION INSIGHT:** Secondary cost elements (categories 21, 31, 41, 42, 43) exist ONLY in CO. They appear in COSP/COSS totals tables but have no corresponding GL posting. This means CO totals for a cost center will always be HIGHER than the FI GL totals for the same cost center's expense accounts, because CO includes both primary postings (from FI) and secondary allocations (CO-internal). **This is not an error — it is by design.** Only primary cost element totals should match between CO and FI.

---

### CO-FI Real-Time Integration Flow

What happens when an FI posting hits a P&L account with a corresponding cost element — the complete 5-step process that executes in real time during every FI document posting:

```
Step 1: User posts FI document (FB50, FB60, MIRO, VF01, AFAB, etc.)
        Document includes a P&L GL account (e.g., 400000 Salaries)

Step 2: System checks — does a primary cost element exist with the same number?
        Lookup: CSKB where KSTAR = GL account number and KOKRS = controlling area
        If YES → CO posting is created automatically
        If NO → No CO posting (GL account is FI-only, e.g., balance sheet accounts)

Step 3: System requires a CO account assignment object
        The CO receiver must be specified: cost center, internal order, WBS element, etc.
        If OKB9 default exists for this GL account → system uses the default
        If OKB9 has no default AND user did not enter one → posting FAILS with
        "Enter a CO account assignment" (this is the most common CO error)

Step 4: CO document created
        COBK header + COEP line items
        The CO document number is DIFFERENT from the FI document number
        COEP-BELNR references the FI document for traceability
        COSP totals table updated (primary postings go to COSP)

Step 5: If the CO object (cost center, order) has a profit center assignment
        PCA separate ledger (GLPCA) is also updated
        This creates the ECC 6-specific PCA data flow
        If the CO object has NO profit center → GLPCA is NOT updated → PCA gap
```

**Worked example:**

A user posts an FI invoice (FB60) for office supplies, GL account 472000, amount 500 EUR, cost center 4100:

1. FI document created in BKPF/BSEG (e.g., doc 1900000100)
2. System finds CSKB entry: KSTAR = 472000, KOKRS = 1000, KATYP = 1 (primary) — YES, cost element exists
3. Cost center 4100 is entered on the invoice line — CO account assignment satisfied (no OKB9 lookup needed)
4. CO document created: COBK/COEP with reference to FI doc 1900000100. COSP updated for cost center 4100, cost element 472000, period posting amount 500 EUR
5. Cost center 4100 has profit center 1010 assigned (CSKS-PRCTR) — GLPCA updated with 500 EUR for profit center 1010

**What triggers Step 2 failure (no CO posting):**
- GL account is a balance sheet account (asset, liability, equity) — no cost element exists
- GL account is a P&L account but no one created the cost element via KA01
- Cost element validity dates do not cover the posting date

**What triggers Step 3 failure (posting error):**
- No OKB9 default for this GL account AND user left cost center blank
- Error message: "Enter a CO account assignment" — the #1 most common CO error in new implementations
- Resolution: either maintain OKB9 default or train users to enter cost center/order on every P&L posting

> **Key principle:** Primary cost elements are the bridge between FI and CO. Every P&L posting that has a corresponding primary cost element automatically flows to CO. Balance sheet postings (asset accounts, liability accounts, equity) do NOT flow to CO because they have no cost element.

> **Exception — Category 22 (External Settlement):** When an internal order settles to a GL account (KO88 with receiver type KST), a category 22 cost element is used. This is the ONLY direction where CO creates an FI posting. All other CO-internal transactions (assessment, distribution, activity allocation) stay within CO and never create FI documents.

---

### CO-FI Reconciliation Walkthrough

This section answers the question: "How do cost center postings reconcile with FI?"

**Scenario:** User wants to verify that cost center 1000 shows the same total costs in CO reports (KSB1 / S_ALR_87013611) as in FI reports (FBL3N / FAGLB03).

**Step 1: Understand What CO Sees vs What FI Sees**

- **FI (FAGLB03 for the GL accounts):** Shows only PRIMARY postings — actual FI document amounts posted to expense GL accounts. These are category 1, 3, 4, 11, 12 cost element postings.
- **CO (KSB1 for the cost center):** Shows primary postings PLUS secondary allocations (categories 21, 31, 41, 42, 43). The CO total is always >= the FI total.

The difference between CO and FI totals = the sum of all secondary cost element postings on that cost center. This difference is expected and correct.

**Worked example:** Cost center 1000 in period 01/2026:

| Source | Cost Element | Category | Amount | Appears in FI? | Appears in CO? |
|--------|-------------|----------|--------|----------------|----------------|
| Salaries posting (FB50) | 400000 | 1 (primary) | 80,000 | YES (FAGLB03) | YES (KSB1) |
| Office supplies (MIRO) | 472000 | 1 (primary) | 5,000 | YES | YES |
| IT assessment received (KSU5) | 690100 | 42 (assessment) | 12,000 | NO | YES |
| Facility overhead received (KGI2) | 691000 | 41 (overhead) | 3,000 | NO | YES |
| **FI total** | | | **85,000** | | |
| **CO total** | | | **100,000** | | |

The 15,000 difference (100,000 - 85,000) is the sum of secondary CE postings (12,000 + 3,000). This is correct — the secondary postings represent allocations that exist only in CO.

**Step 2: Reconcile Primary Postings**

- Run KSB1 for the cost center, filter by primary cost elements only (categories 1, 3, 4, 11, 12)
- Run FBL3N or FAGLB03 for the corresponding GL accounts in the same period
- These totals MUST match. If they do not:
  - Check if all FI postings carry a cost center assignment (OKB9 defaults, manual entry)
  - Check if some FI postings went to a different cost center (posting error)
  - Check if PCA substitution rules (1KEF) are redirecting profit center assignments
  - Check if FI postings to P&L accounts are missing cost elements (KA01 not created for that GL account)

**Step 3: Identify Secondary Postings (CO-Only)**

- Run KSB1 for the cost center, filter by secondary cost elements (categories 21, 31, 41, 42, 43)
- These postings have NO FI counterpart — they exist only in CO
- They represent allocations received from other CO objects:
  - Category 42: Assessment allocations (from KSU5)
  - Category 43: Activity allocations
  - Category 41: Overhead surcharges (from KGI2)
  - Category 21: Internal order settlements (from KO88 with CO receiver)
  - Category 31: Results analysis / WIP postings
- The total of primary + secondary = full cost center costs in CO

**Step 4: Cross-Company-Code Reconciliation (If Applicable)**

If the controlling area spans multiple company codes (OKKP configuration):
- Run KAL1 to display the reconciliation ledger for cross-company-code postings
- Run KALC if reconciliation postings are pending — this creates the FI intercompany entries
- Verify intercompany receivables/payables in FI match the COFIT totals
- See the Reconciliation Ledger section below for the full 3-step process

**Step 5: PCA Reconciliation**

- Compare KE5Z (PCA report, reads GLPCA) totals with FAGLB03 (FI report, reads FAGLFLEXT)
- If PCA totals differ from FI: some FI postings lack profit center assignment
  - Check document splitting configuration (New GL) — is profit center derived for all line items?
  - Check 1KEF substitution rules — are all GL accounts covered?
  - Check that every cost center has a profit center assigned (CSKS-PRCTR)
  - Check for balance sheet items without profit center derivation (common gap in New GL)

### Reconciliation Quick Reference

| What to Compare | CO Source | FI Source | Should Match? | If Not |
|----------------|-----------|-----------|---------------|--------|
| Primary costs only | KSB1 (filter primary CEs) | FBL3N / FAGLB03 | YES — must match exactly | Missing cost elements, wrong CC assignment, missing OKB9 |
| Total costs | KSB1 (all CEs) | FBL3N / FAGLB03 | NO — CO >= FI | Expected: secondary CEs are CO-only |
| PCA vs FI | KE5Z (GLPCA) | FAGLB03 (FAGLFLEXT) | YES — should match | Missing profit center on FI postings |
| Cross-CC | KAL1 (COFIT) | FI intercompany accounts | YES — after KALC run | Pending reconciliation postings |

---

### Reconciliation Ledger (COFIT/COFIS) — ECC 6 Specific

**What it is:** The reconciliation ledger tracks CO postings that cross company code boundaries within a single controlling area. In ECC 6, a controlling area can span multiple company codes (OKKP configuration). When CO allocates costs from a cost center in company code 1000 to a cost center in company code 2000, FI needs an intercompany entry to balance the books.

**How it works (3-step process):**

```
Step 1: CO posting crosses company code boundary
        Example: Assessment cycle allocates from CC 1000 (company code 1000)
                 to CC 2000 (company code 2000)
        CO documents posted in COEP — CO is balanced

Step 2: Reconciliation ledger records the cross-CC posting
        Tables: COFIT (totals), COFIS (single records)
        Records: sending company code, receiving company code, amount, cost element

Step 3: Periodic reconciliation posting
        T-code: KALC
        Creates FI intercompany documents:
          Dr Intercompany Receivable (sending company code)
          Cr Intercompany Payable (receiving company code)
        The FI documents balance the cross-CC cost flow in the general ledger
```

**When reconciliation is needed:**

- Controlling area spans multiple company codes (1:many CA:CC relationship in OKKP)
- CO allocations (assessment, distribution, activity allocation) cross company code boundaries
- If all CO objects are in the same company code, reconciliation ledger postings are zero — KALC produces no output

**When reconciliation is NOT needed:**

- 1:1 controlling area to company code — no cross-CC scenario possible
- CO allocations stay within one company code — no intercompany impact
- Settlement to GL account (category 22) — this already creates FI documents directly

**Key T-codes:**

| T-code | Purpose | When to Run |
|--------|---------|-------------|
| KALC | Execute reconciliation posting | Period-end, after all CO allocations complete |
| KAL1 | Display reconciliation ledger | Anytime — review cross-CC CO postings |
| KAL2 | Reconciliation ledger report | Anytime — detailed reconciliation analysis |

**Tables:**

| Table | Content | Key Fields |
|-------|---------|------------|
| COFIT | Reconciliation ledger totals | KOKRS, GJAHR, PERIO, BUKRS (sender), BUKRS_R (receiver) |
| COFIS | Reconciliation ledger single records | KOKRS, BELNR, BUZEI |

**Worked example:** Assessment cycle allocates 10,000 EUR from CC 1000 (company code 1000) to CC 5000 (company code 2000):

1. CO posting: Dr CC 5000 / Cr CC 1000 (CE cat 42) — CO documents in COEP
2. COFIT records: sender CC = 1000, receiver CC = 2000, amount = 10,000 EUR
3. KALC run creates FI documents:
   - In company code 1000: Dr Intercompany Receivable from 2000, amount 10,000
   - In company code 2000: Cr Intercompany Payable to 1000, amount 10,000
4. After KALC: both company codes are balanced in FI, matching the CO allocation

**Period-end timing:** KALC should run after all CO allocations (KSU5, KSV5) and settlements (KO88, CO88) are complete but before the CO period is locked. See `modules/co/processes.md` for the full period-end sequence.

**Configuration prerequisite:** The intercompany GL accounts used by KALC (receivable and payable) must be configured in OKC1 (or SPRO > Controlling > Organization > Define Reconciliation Posting Accounts). Without this configuration, KALC will error.

> **S/4HANA Differences:** The reconciliation ledger is ELIMINATED in S/4HANA. The Universal Journal (ACDOCA) records all CO postings with full FI account assignment, so cross-company-code CO postings automatically create intercompany FI entries in real time. KALC is no longer needed. Additionally, S/4HANA strongly recommends 1:1 controlling area to company code, further reducing cross-CC scenarios. COFIT and COFIS tables are not used in S/4HANA.

---

## Configuration Decision Trees

> Each decision tree has two parts: (1) Q&A routing — answer questions to reach the recommended approach, then (2) a comparison table with config implications and trade-offs. Decision trees include config paths inline (not just pointers to config-spro.md). CO has 10 decision trees (fewer than MM/SD) because CO configuration patterns are more formulaic.

### Decision Tree 1: Assessment vs Distribution

**Q&A Routing:**

- **Q1:** Does the receiver need to see the original cost element breakdown? -> **Yes:** Distribution (KSV5). **No:** Assessment (KSU5) is simpler.
- **Q2:** Do you need to allocate secondary cost elements (from prior allocations)? -> **Yes:** Assessment only — distribution cannot handle secondary CEs. **No:** Either works.
- **Q3:** Is performance a concern (high-volume allocations with many cost elements)? -> **Yes:** Assessment creates fewer CO documents (one per receiver, single CE). **No:** Choose based on reporting needs.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Assessment (KSU5) | Administrative overhead (IT, HR, Facilities); receiver doesn't need cost breakdown; secondary CEs need to be allocated | KSU1: create cycle with secondary CE (cat 42); define senders, receivers, basis | Simpler; fewer CO docs; original CE detail LOST on receiver side — receiver sees one line "Overhead Assessed" |
| Distribution (KSV5) | Production overhead where cost transparency matters; management wants to see sender's cost composition on receiver | KSV1: create cycle; NO secondary CE needed — original CEs preserved | Full cost visibility; more CO line items (one per original CE); CANNOT handle secondary CEs — only primary |
| Assessment then Distribution (chained) | Some senders have secondary CEs (from prior assessment), others have only primary | Run KSU5 first (handles secondary CEs), then KSV5 (distributes remaining primary CEs) | Most flexible; higher complexity; sequence matters — distribution must run AFTER assessment |

Cross-reference: See `modules/co/processes.md` Section 1 for the assessment vs distribution process walkthrough.

### Decision Tree 2: Allocation Basis Selection

**Q&A Routing:**

- **Q1:** Are allocation ratios known and stable across periods? -> **Yes:** Fixed percentages (simplest). **No:** Use data-driven allocation.
- **Q2:** Is the allocation basis a non-monetary measure (headcount, square meters, machine hours)? -> **Yes:** Statistical key figures (KB31N). **No:** Use receiver's own cost values.
- **Q3:** How frequently does the allocation basis change? -> **Rarely:** Fixed values are fine. **Monthly:** Statistical key figures require monthly entry. Consider fixed values with periodic review.

**Comparison Table:**

| Basis Type | When to Use | Config (Cycle Segment) | Trade-offs |
|------------|------------|------------------------|------------|
| Fixed percentages | Known, stable ratios (e.g., 60/40 split between two departments) | Segment: allocation type = fixed percentages; enter % per receiver | Simplest; no maintenance; inaccurate if actual ratios change |
| Fixed amounts | Absolute allocation per receiver (e.g., fixed monthly charge) | Segment: allocation type = fixed amounts; enter EUR per receiver | Predictable cost allocation; not responsive to volume changes |
| Statistical key figures (KB31N) | Data-driven allocation (headcount, sq meters, machine hours) | Segment: allocation type = posted amounts with SKF; enter values via KB31N | Most accurate; requires monthly SKF entry (KB31N); more maintenance |
| Variable portions (receiver's own values) | Receiver's actual costs determine share of allocation | Segment: allocation type = variable portions; system reads receiver balances | Fully dynamic; no separate data entry; circular dependency risk if receivers also send |

### Decision Tree 3: Iterative vs Non-Iterative Allocation

**Q&A Routing:**

- **Q1:** Do any sender cost centers also receive allocations from other senders? -> **No:** Non-iterative (standard). **Yes:** Continue.
- **Q2:** Is this a reciprocal service situation (A allocates to B, B allocates to A)? -> **Yes:** Iterative allocation needed. **No:** Reorder cycles so senders run before receivers — non-iterative may work.
- **Q3:** How many cost centers are involved in circular allocations? -> **2-3:** Iterative is manageable. **5+:** Consider simplifying the allocation model or consolidating service cost centers.

**Comparison Table:**

| Approach | When to Use | Config | Trade-offs |
|----------|------------|--------|------------|
| Non-iterative (standard) | No circular allocations; each cycle runs once; sender balance goes to zero | Default — no special config | Simplest; fastest; sender balance fully allocated in one pass |
| Iterative | Reciprocal services (IT charges HR, HR charges IT); circular dependency | Cycle header: Iterative flag = X in KSU1/KSV1; system iterates until convergence (delta < threshold) | Handles circular allocations correctly; slower execution; must define convergence threshold; limited to ~50 iterations in standard SAP |
| Simplify (avoid iteration) | Complex circular allocations making iteration slow or hard to audit | Restructure CC hierarchy: merge reciprocal CCs or designate one as "primary sender" | Avoids iteration complexity; may sacrifice some allocation accuracy; simpler to audit |

### Decision Tree 4: Settlement Rule Design

**Q&A Routing:**

- **Q1:** Does the order collect costs that should be redistributed to operational cost centers? -> **Yes:** Settle to cost center (CTR) — CO-internal, no FI document.
- **Q2:** Does the order collect costs that should be capitalized as an asset? -> **Yes:** Settle to fixed asset or AUC (FXA) — creates FI document (capitalization).
- **Q3:** Should settlement create an FI document (post to a GL account)? -> **Yes:** Use receiver type KST (GL account) with category 22 CE. **No:** Use CTR, ORD, PSP, or RKS (all CO-internal).

**Comparison Table:**

| Receiver Type | COBRB-KONTY | When to Use | Creates FI Document? | Settlement CE |
|---------------|-------------|-------------|---------------------|---------------|
| Cost Center | CTR | Redistribute overhead costs to operational CCs | No (CO-internal) | Category 21 (internal) |
| Internal Order | ORD | Chain settlement (order to order) | No (CO-internal) | Category 21 |
| GL Account | KST | Close order to P&L/BS account; need FI visibility | Yes — category 22 CE creates FI doc | Category 22 (external) |
| Fixed Asset / AUC | FXA | Capitalize investment order costs as fixed asset | Yes — creates asset posting | Category 22 |
| WBS Element | PSP | Project system integration | No (CO-internal) | Category 21 |
| CO-PA Segment | RKS | Profitability analysis allocation | No (CO-internal) | Category 21 |

> **CRITICAL:** Category 21 (internal settlement) vs category 22 (external settlement) is the key distinction. Only category 22 creates FI documents. The settlement profile (OKO7) controls which receiver types are allowed, and the allocation structure (OKO6) maps source CEs to settlement CEs. See `modules/co/config-spro.md` Section 4.

### Decision Tree 5: Order Type Configuration

**Q&A Routing:**

- **Q1:** What is the purpose of this order type? -> **Overhead tracking:** standard overhead order. **Capital investment:** investment order (settlement to asset). **Accrual:** accrual order (periodic offsetting).
- **Q2:** Does the order need budgeting (commitment management)? -> **Yes:** Configure budget profile in the order type (KOT2). **No:** Skip budgeting.
- **Q3:** Should settlement rules be mandatory at order creation? -> **Yes (recommended):** Configure settlement profile (OKO7) to require settlement rule. **No:** Settlement rules can be added later, but risk missing them at period-end.

**Comparison Table:**

| Order Type Pattern | Example AUART | Settlement Profile | Budget Profile | Use Case |
|-------------------|---------------|-------------------|----------------|----------|
| Overhead order | 0100 | Allows CTR, KST receivers; settlement optional | None | Marketing campaigns, repairs, temporary cost collection |
| Investment order | 0200 | Requires FXA receiver; settlement mandatory | Budget profile active | Capital projects; costs capitalized as fixed asset at settlement |
| Accrual order | 0300 | Specific accrual settlement profile | None | Periodic accruals with offsetting entries |
| Statistical order (reporting only) | 0400 | No settlement — order is statistical (costs posted in parallel, not instead of) | None | Track costs for reporting without moving them; actual costs remain on the cost center |

### Decision Tree 6: Cost Center Hierarchy Design

**Q&A Routing:**

- **Q1:** What organizational structure should the hierarchy mirror? -> Typically: Company > Division/Business Unit > Department > Team/Function. The standard hierarchy (OKEON) must contain ALL cost centers.
- **Q2:** How deep should the hierarchy go? -> 3-4 levels is standard. More than 5 levels = maintenance overhead and reporting complexity.
- **Q3:** Do you need alternative groupings for reporting beyond the standard hierarchy? -> **Yes:** Create additional cost center groups (KSH1) for cross-departmental reporting. **No:** Standard hierarchy is sufficient.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| Flat hierarchy (2-3 levels) | Small organization; few cost centers (<100) | OKEON: root > department > cost centers | Simplest maintenance; limited drill-down in reports |
| Standard hierarchy (3-4 levels) | Medium-to-large org; clear departmental structure | OKEON: root > division > department > team > cost centers | Good balance of detail and maintainability; covers most reporting needs |
| Deep hierarchy (5+ levels) with groups | Large org; need multiple reporting dimensions | OKEON: deep standard hierarchy + KSH1 alternative groups | Maximum reporting flexibility; high maintenance; must keep KSH1 groups in sync |

### Decision Tree 7: Controlling Area to Company Code Relationship

**Q&A Routing:**

- **Q1:** Does the business need cross-company-code cost allocations in CO? -> **No:** Use 1:1 CA to CC (recommended, simpler, S/4HANA ready). **Yes:** Continue.
- **Q2:** Do all company codes share the same chart of accounts and fiscal year variant? -> **No:** Cannot share a controlling area — 1:1 is mandatory. **Yes:** 1:many is possible.
- **Q3:** Is S/4HANA migration planned within 3-5 years? -> **Yes:** Use 1:1 even if cross-CC allocation is desired (reduces migration complexity). **No:** 1:many is acceptable if cross-CC allocation is genuinely needed.

**Comparison Table:**

| Relationship | When to Use | Config Path | Trade-offs |
|-------------|------------|-------------|------------|
| 1:1 (recommended) | Single company code; or S/4HANA migration planned; no cross-CC allocation needed | OKKP: one CA per CC; OX19: one CC assigned | Simplest; no reconciliation ledger needed; S/4HANA ready; cannot allocate costs across company codes in CO |
| 1:many | Cross-company-code cost allocations required; shared chart of accounts and FY variant | OKKP: one CA spanning multiple CCs; OX19: multiple CCs assigned; cross-CC indicator active | Enables cross-CC allocations; requires reconciliation ledger (KALC); adds period-end complexity; S/4HANA migration is harder |

> **S/4HANA readiness:** S/4HANA strongly recommends 1:1. If you implement 1:many in ECC 6, plan for migration effort to split the controlling area or reorganize company codes.

### Decision Tree 8: Activity Price Determination

**Q&A Routing:**

- **Q1:** Can the cost center manager reliably estimate activity prices for the fiscal year? -> **Yes:** Manual price entry (KP26) with price indicator 2. **No:** Continue.
- **Q2:** Should the system calculate planned prices from planned costs and planned activity quantities? -> **Yes:** Automatic price (price indicator 1). The system divides total planned CC costs by planned activity output.
- **Q3:** Should actual prices replace planned prices for allocation valuation? -> **Yes:** Use price indicator 3 (target = actual). Run KSII at period-end to calculate actual rates.

**Comparison Table:**

| Price Indicator (CSLA-TARKZ) | Name | When to Use | Config | Trade-offs |
|------------------------------|------|-------------|--------|------------|
| 1 | Plan price automatic | System calculates from planned costs / planned activity | KP06 (plan costs) + KP26 (plan activity qty); system computes price | No manual price entry; accurate if plan costs and quantities are reliable; recalculates when plan data changes |
| 2 | Plan price manual | Manager sets activity rate directly | KP26: enter fixed + variable price per unit | Full control; commonly used; requires manager judgment; may not reflect actual cost structure |
| 3 | Target = actual | Actual costs determine activity price retroactively | KSII at period-end calculates actual price | Most accurate for cost reporting; introduces variance between plan and actual rates; actual price only known at period-end |

### Decision Tree 9: CO Version Strategy

**Q&A Routing:**

- **Q1:** Do you need only one plan for comparison against actuals? -> **Yes:** Use version 0 only (plan/actual integration version). This covers 90% of implementations.
- **Q2:** Do you need scenario planning (best case, worst case, budget vs forecast)? -> **Yes:** Create additional versions (001, 002, etc.) for scenarios. These hold plan data only — actuals always post to version 0.
- **Q3:** How many planning scenarios does management need? -> **1-2 scenarios:** manageable. **3+:** consider whether the complexity provides enough value.

**Comparison Table:**

| Strategy | When to Use | Config (OKEQ) | Trade-offs |
|----------|------------|----------------|------------|
| Version 0 only | Single plan vs actual comparison; budget = plan | OKEQ: version 0 configured for plan and actual | Simplest; one plan to maintain; covers most reporting needs; no scenario analysis |
| Version 0 + 1 (budget + forecast) | Separate budget (annual, locked) and forecast (rolling, updated) | OKEQ: version 0 = budget, version 001 = rolling forecast | Common pattern; two plans to maintain; enables budget-vs-forecast-vs-actual three-way comparison |
| Version 0 + multiple (scenarios) | Complex planning with what-if analysis | OKEQ: version 0 + 001-00N per scenario | Maximum planning flexibility; high maintenance; each version requires full planning data entry |

### Decision Tree 10: Transfer Pricing Approach

**Q&A Routing:**

- **Q1:** Does the business need management reporting at profit centers with internal markup for goods/services transferred between profit centers? -> **No:** Skip PCA transfer pricing — most implementations do not use it. **Yes:** Continue.
- **Q2:** Should transfer prices affect FI (legal books)? -> **No (standard ECC 6):** PCA transfer pricing updates GLPCA only, not FI. **Yes:** Use intercompany billing (SD module) instead — not PCA transfer pricing.
- **Q3:** What transfer pricing method? -> Percentage markup on cost, fixed price per unit, or standard cost + markup. Configure in 3KEH.

**Comparison Table:**

| Approach | When to Use | Config Path | Trade-offs |
|----------|------------|-------------|------------|
| No transfer pricing | Most implementations; no internal markup needed for management reporting | No config needed | Simplest; profit centers show costs at actual; no dual valuation |
| PCA transfer pricing (1KEG) | Need profit center reports showing internal margin; dual valuation (legal vs management) | 3KEH: define methods; 1KEG: execute transfer pricing; GLPCA updated | PCA-only (does not affect FI); enables profit center P&L with internal margin; adds period-end step; uncommon — most implementations skip this |
| Intercompany billing (SD) | Transfer prices must appear in FI (legal books); intercompany invoices required | SD intercompany billing (IV/PI/PD condition types); creates FI documents | FI-visible; legally recognized; much more complex; requires SD master data and billing |

> **S/4HANA Note:** PCA transfer pricing via 1KEG still works in S/4HANA, but the PCA separate ledger is eliminated. Transfer pricing uses the Universal Journal with additional valuation views.
