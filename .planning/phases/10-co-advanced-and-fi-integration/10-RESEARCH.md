---
module: co
content_type: research
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium-high
last_verified: "2026-02-17"
phase: 10-co-advanced-and-fi-integration
created: 2026-02-17
---

# Phase 10: CO Advanced & FI Integration - Research

**Researched:** 2026-02-17
**Domain:** SAP ECC 6.0 Controlling — cost element mapping, CO-FI reconciliation, decision trees, troubleshooting, CO-FI integration
**Confidence:** MEDIUM-HIGH (existing CO foundation from Phase 9 is strong; CO-FI integration mechanics are well-established SAP architecture)

---

## Summary

Phase 10 layers four content types onto the Phase 9 CO foundation, following the exact pattern established by Phase 6 (MM Advanced) and Phase 8 (SD Advanced): (1) a cost element mapping and CO-FI reconciliation walkthrough covering how primary cost elements map 1:1 to GL accounts, how secondary cost elements live CO-only, and how the reconciliation ledger tracks cross-company-code CO postings; (2) configuration decision trees for common CO scenarios (allocation cycle design, settlement rule configuration, transfer pricing, cost center hierarchy design); (3) symptom-first CO troubleshooting with SAP message IDs; and (4) complete CO-FI integration point documentation in integration.md.

Unlike MM (OBYC) and SD (VKOA), CO does not have a single "account determination" framework to walk through. Instead, the CO-FI relationship is fundamentally different: FI postings automatically create CO documents (real-time integration), and CO-internal postings (secondary cost elements) never touch FI at all. The "mapping walkthrough" for CO is therefore about understanding which FI postings flow to CO, which CO postings flow back to FI (settlement with category 22 cost elements), and how to reconcile the two ledgers.

The reconciliation ledger (tables COFIT/COFIS) is the ECC 6-specific mechanism for tracking CO postings that cross company code boundaries within a controlling area. When a cost center in company code 1000 assesses costs to a cost center in company code 2000, the reconciliation ledger records the intercompany entry so that FI can post the corresponding intercompany receivable/payable. This is eliminated in S/4HANA (Universal Journal handles it natively).

**Primary recommendation:** Structure the co-advanced.md file with: (1) Cost element mapping and CO-FI reconciliation walkthrough, (2) 10 decision trees covering allocation, settlement, hierarchy, and planning scenarios, (3) 10 troubleshooting entries covering period-end failures, allocation errors, settlement errors, and reconciliation issues. The integration.md should use the same integration point catalog + transaction trace format as MM and SD, answering "what happens in CO when I post FB50 to a P&L account?"

---

## Section 1: Cost Element Mapping and CO-FI Reconciliation -- Verified Facts

### 1.1 Existing Foundation (from Phase 9)

The knowledge base already contains in `modules/co/master-data.md` and `modules/co/tcodes.md`:
- Complete cost element category reference (primary 1,3,4,11,12,22 vs secondary 21,31,41,42,43)
- CSKA/CSKB table structure for cost elements
- KA01 (primary CE creation requires existing GL account) and KA06 (secondary CE, no GL account)
- CORRECTION block: secondary cost elements CANNOT have a GL account
- S/4HANA note: cost elements merged into GL accounts (FS00), KA01/KA06 obsolete

Phase 10 does NOT duplicate this master data content. It adds:
- The mapping walkthrough: how primary CEs link to GL accounts and how this link drives real-time CO postings
- CO-FI reconciliation: how to ensure CO totals match FI totals, the reconciliation ledger mechanism
- Tracing: "when I post to GL account 400000 in FB50, what happens in CO?"

Confidence: HIGH (builds directly on verified Phase 9 content)

### 1.2 CO-FI Real-Time Integration Mechanism

The most fundamental CO-FI integration concept: when an FI posting hits a P&L GL account that has a corresponding primary cost element, the system automatically creates a CO document.

**How it works:**

```
Step 1: User posts FI document (FB50, FB60, MIRO, VF01, etc.)
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
```

**Key principle:** Primary cost elements are the bridge between FI and CO. Every P&L posting that has a corresponding primary cost element automatically flows to CO. Balance sheet postings (asset accounts, liability accounts, equity) do NOT flow to CO because they have no cost element.

**Exception — Category 22 (External Settlement):** When an internal order settles to a GL account (KO88 with receiver type KST), a category 22 cost element is used. This is the ONLY direction where CO creates an FI posting. All other CO-internal transactions (assessment, distribution, activity allocation) stay within CO and never create FI documents.

Confidence: HIGH (fundamental SAP CO architecture, consistent with existing KB content in config-spro.md OKB9 section)

### 1.3 Primary Cost Element to GL Account Mapping

**The mapping rule is simple:** Primary cost element number = GL account number. They MUST be identical. The GL account must exist in FS00/SKA1/SKB1 BEFORE the cost element can be created in KA01.

**Mapping table by cost element category:**

| Category | Name | GL Account Required | Direction of Flow | FI Impact |
|----------|------|--------------------|--------------------|-----------|
| 1 | Primary costs/revenue | Yes (same number) | FI → CO (automatic) | Every FI posting to this GL account creates a CO document |
| 3 | Accrual/deferral (FI side) | Yes | FI → CO | FI accrual posts to this GL/CE; CO may have separate imputed cost via cat 4 |
| 4 | Accrual/deferral (CO side) | Yes | CO accrual posting | CO imputed costs (calculated depreciation, calculated interest) |
| 11 | Revenue | Yes | FI → CO | Revenue postings flow to CO (for cost-of-sales accounting) |
| 12 | Sales deduction | Yes | FI → CO | Discount/rebate postings flow to CO |
| 22 | External settlement | Yes | CO → FI | Settlement from order to GL account creates FI document |
| 21 | Internal settlement | No (CO-only) | CO internal | Settlement from order to cost center/order — no FI impact |
| 31 | Results analysis | No (CO-only) | CO internal | WIP and results analysis — no FI impact (unless posted to FI via RA) |
| 41 | Overhead rates | No (CO-only) | CO internal | Overhead surcharges from KGI2 — no FI impact |
| 42 | Assessment | No (CO-only) | CO internal | Assessment allocations from KSU5 — no FI impact |
| 43 | Activity allocation | No (CO-only) | CO internal | Activity allocations — no FI impact |

**Critical insight for reconciliation:** Secondary cost elements (21, 31, 41, 42, 43) exist ONLY in CO. They appear in COSP/COSS totals tables but have no corresponding GL posting. This means CO totals for a cost center will always be HIGHER than the FI GL totals for the same cost center's expense accounts, because CO includes both primary postings (from FI) and secondary allocations (CO-internal). This is not an error — it is by design.

Confidence: HIGH (verified against existing master-data.md cost element category table)

### 1.4 Reconciliation Ledger (COFIT/COFIS)

**What it is:** The reconciliation ledger is an ECC 6-specific mechanism that tracks CO postings crossing company code boundaries within a single controlling area. In ECC 6, a controlling area can span multiple company codes (OKKP configuration). When CO allocates costs from a cost center in company code 1000 to a cost center in company code 2000, the CO posting is complete — but FI needs an intercompany receivable/payable to balance the books.

**How it works:**

```
Step 1: CO posting crosses company code boundary
        Example: Assessment cycle allocates from CC 1000 (in CC 1000) to CC 2000 (in CC 2000)
        CO documents posted in COEP — CO is balanced

Step 2: Reconciliation ledger records the cross-CC posting
        Tables: COFIT (CO-FI reconciliation totals), COFIS (CO-FI reconciliation single records)
        Records: sending company code, receiving company code, amount, cost element

Step 3: Periodic reconciliation posting
        T-code: KALC (reconciliation posting for CO)
        What it does: reads COFIT/COFIS and creates FI intercompany documents
        Dr Intercompany Receivable (in sending CC)
        Cr Intercompany Payable (in receiving CC)
        This brings FI back into balance with CO for cross-CC allocations
```

**When reconciliation is needed:**
- Controlling area spans multiple company codes (1:many CA:CC relationship)
- CO allocations (assessment, distribution, activity allocation, settlement) cross company code boundaries
- If all CO objects are in the same company code, reconciliation ledger postings are zero

**Configuration:**
- OKKP: Controlling area must have "Cross-Company-Code Cost Accounting" indicator active
- KALC: Reconciliation posting run (can be scheduled as period-end job)
- The reconciliation GL accounts (intercompany receivable/payable) are configured in OKKP or in the cross-company-code configuration

**T-codes for reconciliation:**
- KALC — Execute reconciliation posting
- KAL1 — Display reconciliation ledger
- KAL2 — Reconciliation ledger report

**S/4HANA note:** The reconciliation ledger is ELIMINATED in S/4HANA. The Universal Journal (ACDOCA) records all CO postings with full FI account assignment, so cross-company-code CO postings automatically create the intercompany FI entries. KALC is no longer needed. Additionally, S/4HANA strongly recommends 1:1 controlling area to company code, further reducing cross-CC scenarios.

Confidence: MEDIUM-HIGH (reconciliation ledger concept is well-established; COFIT/COFIS table names and KALC T-code are standard; specific configuration details within OKKP may need validation)

### 1.5 CO-FI Reconciliation Walkthrough: "How Cost Center Postings Reconcile with FI"

This is a specific success criterion from the phase description. The walkthrough traces the full reconciliation path:

**Scenario:** User wants to verify that cost center 1000 shows the same total costs in CO reports (KSB1/S_ALR_87013611) as in FI reports (FBL3N/FAGLB03).

**Step 1: Understand what CO sees vs what FI sees**
- FI (FAGLB03 for the GL accounts): Shows only PRIMARY postings — actual FI document amounts posted to expense GL accounts. These are category 1/3/4/11/12 cost element postings.
- CO (KSB1 for the cost center): Shows primary postings PLUS secondary allocations (categories 21,31,41,42,43). The CO total is >= the FI total.

**Step 2: Reconcile primary postings**
- Run KSB1 for the cost center, filter by primary cost elements only (categories 1, 3, 4, 11, 12)
- Run FBL3N or FAGLB03 for the corresponding GL accounts in the same period
- These totals MUST match. If they don't:
  - Check if all FI postings carry a cost center assignment (OKB9 defaults, manual entry)
  - Check if some FI postings went to a different cost center (posting error)
  - Check if PCA substitution rules (1KEF) are redirecting profit center assignments

**Step 3: Identify secondary postings (CO-only)**
- Run KSB1 for the cost center, filter by secondary cost elements (categories 21, 31, 41, 42, 43)
- These postings have NO FI counterpart — they exist only in CO
- They represent allocations received from other CO objects (assessment, distribution, activity allocation)
- The total of primary + secondary = full cost center costs in CO

**Step 4: Cross-company-code reconciliation (if applicable)**
- If the controlling area spans multiple company codes:
  - Run KAL1 to check the reconciliation ledger for cross-CC postings
  - Run KALC if reconciliation postings are pending
  - Verify intercompany receivables/payables in FI match the COFIT totals

**Step 5: PCA reconciliation**
- Compare KE5Z (PCA report, reads GLPCA) totals with FAGLB03 (FI report, reads FAGLFLEXT)
- If PCA totals differ from FI: some FI postings lack profit center assignment
  - Check document splitting configuration (New GL)
  - Check 1KEF substitution rules
  - Check that every cost center has a profit center assigned (CSKS-PRCTR)

Confidence: HIGH (standard SAP reconciliation approach, consistent with existing KB content)

---

## Section 2: CO Decision Trees -- Research Findings

### 2.1 Recommended Decision Trees (10 Trees)

Based on the requirements (CO-06: allocation cycles, settlement rules, transfer pricing) and the pattern from Phase 6 (12 trees) and Phase 8 (12 trees), the CO module warrants 10 decision trees. CO has fewer configuration decision points than MM or SD because CO configuration is more formulaic (allocation cycles have a fixed structure, settlement rules have a fixed structure).

**Allocation Trees (3):**
1. Assessment vs Distribution — when to use each, design principles
2. Allocation Basis Selection — fixed percentages vs statistical key figures vs variable portions
3. Iterative vs Non-Iterative Allocation — circular allocation handling

**Settlement Trees (2):**
4. Settlement Rule Design — receiver types, single vs split settlement, settlement cost elements
5. Order Type Configuration — overhead vs investment vs accrual, settlement profile selection

**Hierarchy and Organization Trees (2):**
6. Cost Center Hierarchy Design — standard hierarchy structure, grouping principles, reporting implications
7. Controlling Area to Company Code Relationship — 1:1 vs 1:many, cross-CC implications, reconciliation ledger

**Planning Trees (2):**
8. Activity Price Determination — plan price manual vs automatic, price indicator selection
9. CO Version Strategy — version 0 (plan/actual) vs additional versions for scenario planning

**Transfer Pricing (1):**
10. Transfer Pricing Approach — PCA transfer pricing methods (1KEG), when to use, ECC 6-specific considerations

Confidence: HIGH (these cover the major CO configuration decision areas from config-spro.md and processes.md)

### 2.2 Assessment vs Distribution (Tree 1)

This is the most important CO decision tree — already documented at process level in processes.md but needs decision-tree format.

**Key decision factors:**

| Factor | Assessment (KSU5) | Distribution (KSV5) |
|--------|-------------------|---------------------|
| Cost element on receiver | Secondary CE (category 42) — single "overhead assessed" element | Original primary CEs preserved |
| Cost transparency | Lost on receiver side | Maintained — full drill-down |
| Which CEs can be allocated | Primary AND secondary | Primary ONLY |
| Performance | Faster (fewer line items) | Slower (one item per original CE) |
| Typical use | Administrative overhead (IT, HR, Facilities) | Production overhead where cost breakdown matters |
| Reporting impact | Receiver sees one line "Assessed Overhead" | Receiver sees original cost element breakdown |

**Decision Q&A:**
- Q1: Does the receiver need to see the original cost element breakdown?
  - Yes → Distribution (KSV5)
  - No → Assessment (KSU5) is simpler
- Q2: Do you need to allocate secondary cost elements (from prior allocations)?
  - Yes → Assessment only (distribution cannot handle secondary CEs)
  - No → Either works
- Q3: Is performance a concern (high-volume allocations)?
  - Yes → Assessment creates fewer CO documents
  - No → Choose based on reporting needs

Confidence: HIGH (verified against existing processes.md and tcodes.md)

### 2.3 Settlement Rule Design (Tree 4)

**Key decision factors:**

| Receiver Type | COBRB-KONTY | When to Use | Creates FI Document? |
|---------------|-------------|-------------|---------------------|
| Cost Center | CTR | Redistribute costs to operational CCs | No (CO-internal) |
| Internal Order | ORD | Chain settlement (order to order) | No (CO-internal) |
| GL Account | KST | Close order to P&L/BS account | Yes (category 22 CE) |
| Fixed Asset / AUC | FXA | Capitalize investment order | Yes (creates asset posting) |
| WBS Element | PSP | Project system integration | No (CO-internal) |
| CO-PA Segment | RKS | Profitability analysis | No (CO-internal) |

**Decision Q&A:**
- Q1: Is this an overhead order (costs to be redistributed)?
  - Yes → Settle to cost center (CTR) or GL account (KST)
- Q2: Is this an investment/capital order (costs to be capitalized)?
  - Yes → Settle to fixed asset/AUC (FXA)
- Q3: Should settlement create an FI document?
  - Yes → Use receiver type KST (GL account) or FXA (asset)
  - No → Use CTR, ORD, PSP, or RKS

**Settlement cost element selection:**
- Internal settlement (to CO receivers): Use category 21 secondary CE
- External settlement (to FI receivers): Use category 22 primary CE (must have corresponding GL account)
- The allocation structure (OKO6) maps source CEs to settlement CEs

Confidence: HIGH (verified against existing tcodes.md KO88 section and config-spro.md OKO7/OKO6)

### 2.4 Transfer Pricing (Tree 10)

**ECC 6-specific PCA transfer pricing:**

Transfer pricing in ECC 6 PCA allows posting transfer prices between profit centers for internal goods/service transfers. This creates dual valuation: legal valuation in FI (at cost or market price) and management valuation in PCA (at transfer price).

- T-code: 1KEG (execute transfer pricing)
- Configuration: 3KEH (define transfer pricing methods)
- Methods: percentage markup, fixed price, standard cost + markup
- Posting: PCA separate ledger (GLPCA) is updated; FI is NOT affected

**Decision Q&A:**
- Q1: Do you need management reporting at profit centers with internal markup?
  - Yes → Configure PCA transfer pricing
  - No → Skip (most implementations skip this)
- Q2: Should transfer prices affect FI (legal books)?
  - No (standard ECC 6) → PCA transfer pricing is PCA-only
  - Yes → Use intercompany billing (SD) instead — not PCA transfer pricing

**S/4HANA note:** PCA transfer pricing via 1KEG is still available in S/4HANA but the separate PCA ledger is eliminated. Transfer pricing in S/4HANA uses the Universal Journal with additional valuation views.

Confidence: MEDIUM (PCA transfer pricing is a less commonly implemented feature; 1KEG and 3KEH T-codes are verified in existing processes.md period-end sequence)

### 2.5 Other Key Decision Areas

**Allocation Basis Selection (Tree 2):**
- Fixed percentages: simplest, used when allocation ratios are known and stable
- Fixed amounts: absolute values per receiver
- Statistical key figures (KB31N): data-driven allocation (headcount, square meters, machine hours)
- Variable portions: receiver's own values drive allocation (e.g., actual costs on receiver determine share)
- Trade-off: Fixed = predictable but static; SKF = accurate but requires maintaining SKF values each period

**Iterative vs Non-Iterative (Tree 3):**
- Non-iterative: standard; each cycle runs once; sender balance goes to zero
- Iterative: for circular allocations (A allocates to B, B allocates to A); system iterates until convergence
- When to use iterative: reciprocal service cost centers (IT charges HR, HR charges IT)
- Configuration: cycle header "Iterative" flag in KSU1/KSV1

**Cost Center Hierarchy Design (Tree 6):**
- Standard hierarchy (OKEON) is mandatory; all CCs must belong
- Structure typically mirrors org chart: Company > Division > Department > Team
- Additional groups (KSH1) for reporting flexibility
- Key decision: depth of hierarchy vs maintenance overhead

**Controlling Area to Company Code (Tree 7):**
- 1:1 (recommended, especially for S/4HANA readiness): simplest; no reconciliation ledger needed
- 1:many: one CA spans multiple CCs; allows cross-CC allocations; requires reconciliation ledger (KALC)
- Trade-off: 1:many enables cross-CC cost analysis but adds reconciliation complexity

Confidence: HIGH for trees 2, 3, 6; MEDIUM-HIGH for tree 7 (reconciliation ledger specifics)

---

## Section 3: Troubleshooting -- SAP Message IDs and Diagnostic Patterns

### 3.1 Message Class Reference for CO

Key SAP message classes for CO troubleshooting:

| Class | Area | Description |
|-------|------|-------------|
| KI | Cost Element / Cost Center | Cost element creation, cost center postings |
| KO | Internal Orders | Order creation, settlement, status |
| KD | Allocation / Distribution | Assessment and distribution cycle errors |
| KS | Cost Center Accounting | Cost center planning, reporting |
| KP | Planning | Cost center and activity planning |
| KW | Product Costing | CK11N, CK24, costing run errors |
| F5 | FI Document Posting | Account determination failures (shared with FI) |

### 3.2 Recommended Troubleshooting Entries (10 Target)

CO troubleshooting is heavily period-end focused, reflecting CO's nature as a period-end processing module.

**CO Account Assignment (2 entries):**

1. **"Enter a CO account assignment" when posting FI document** — P&L GL account has a corresponding primary cost element but no cost center/order is specified and OKB9 has no default.
   - Root cause: OKB9 default account assignment not maintained for this GL account/company code
   - Resolution: Check OKB9 for the GL account; add default cost center. Or enter cost center manually on FI posting.
   - This is the single most common CO error for new implementations.

2. **FI posting succeeds but cost center is wrong in CO** — OKB9 default assigns costs to a catch-all cost center instead of the correct operational CC.
   - Root cause: OKB9 has a blanket default; user relies on default instead of entering specific CC
   - Resolution: Review OKB9 defaults; use KB61 (reposting) to correct before period-end allocations; train users to enter correct CC

**Period-End Allocation (3 entries):**

3. **Assessment/distribution cycle runs but posts zero** — Sender cost centers have no balance for the cost elements included in the cycle.
   - Root cause: Sender values = zero (costs not yet posted, or wrong cost element range in cycle)
   - Resolution: KSB1 to verify sender balances; KSU2/KSV2 to check cycle sender values configuration; verify cost element groups in cycle match actual postings

4. **Assessment cycle error: "No valid segments found"** — Cycle has no active segments for the selected period/fiscal year.
   - Root cause: Cycle validity dates don't cover the execution period, or all segments are inactive
   - Resolution: KSU2 to check cycle validity dates and segment validity; ensure at least one segment is active for the period

5. **Distribution fails: "Secondary cost elements cannot be distributed"** — Attempting to distribute secondary CEs (categories 21-43) which is not allowed.
   - Root cause: Sender cost center has secondary CE balances from prior assessment; distribution can only handle primary CEs
   - Resolution: Use assessment (KSU5) for secondary CEs; or restructure allocation sequence so distribution runs before assessment

**Settlement (2 entries):**

6. **KO88 settlement skips orders or produces "No settlement rule" error** — Missing settlement rule on the internal order.
   - Root cause: Settlement rule not maintained on the order (COBRB table empty for this order)
   - Resolution: KO02 -> Settlement Rule button -> define receiver, percentage, settlement CE; configure OKO7 settlement profile to REQUIRE settlement rule at order creation (preventive)

7. **KO88 settlement fails: "Receiver not valid" or "Settlement cost element not found"** — Settlement rule points to an invalid receiver or the allocation structure (OKO6) doesn't map the source CEs.
   - Root cause: Receiver deleted/closed, or allocation structure missing mapping for the cost elements on the order
   - Resolution: Check KO03 settlement rule for receiver validity; check OKO6 allocation structure referenced by the settlement profile (OKO7); verify category 21/22 CE exists

**Product Costing (1 entry):**

8. **CK24 mark/release appears to succeed but standard price not updated** — Transfer control (OK17) not configured correctly for the costing variant.
   - Root cause: OK17 transfer control missing or wrong mapping between costing variant and MBEW price field
   - Resolution: Check OK17 for the costing variant used in CK11N; verify the transfer control maps to MBEW-STPRS; verify via MM03 Accounting 1 view after release

**Reconciliation (2 entries):**

9. **KE5Z (PCA report) totals differ from FAGLB03 (FI report)** — FI postings missing profit center assignment.
   - Root cause: Some FI postings do not carry a profit center; PCA separate ledger (GLPCA) is incomplete
   - Resolution: Check if all cost centers have CSKS-PRCTR assigned; check 1KEF substitution rules; check document splitting configuration for New GL; run 1KEK (PCA data transfer) if needed for historical correction

10. **CO totals (COSP/COSS) higher than FI totals for same cost center** — This is expected behavior, not an error. Secondary allocations in CO have no FI counterpart.
    - Root cause: User expects CO and FI to match exactly; doesn't understand secondary CE concept
    - Resolution: Explain that CO = primary (from FI) + secondary (CO-only); filter KSB1 by primary CEs only to reconcile against FI; secondary CEs are the difference

Confidence: MEDIUM-HIGH (troubleshooting patterns are standard CO support knowledge; specific message IDs need validation against SAP Datasheet but patterns are correct)

### 3.3 Key Diagnostic T-Codes for CO Troubleshooting

| T-Code | Purpose | Use In Troubleshooting |
|--------|---------|----------------------|
| KSB1 | Cost center actual line items | Primary CO report; verify what costs posted and from which FI document |
| KOB1 | Internal order actual line items | Verify order costs before settlement |
| KA03 | Display cost element | Check if CE exists, category, validity dates |
| OKB9 | Default account assignment | Verify/fix default CO assignments for GL accounts |
| KSU2/KSV2 | Change assessment/distribution cycle | Check cycle configuration, segments, validity |
| KO02 | Change internal order | Maintain settlement rule, check status |
| OKO7 | Settlement profiles | Check allowed receiver types, settlement CE |
| OKO6 | Allocation structures | Check source-to-settlement CE mapping |
| OK17 | Transfer control | Verify costing variant to price field mapping |
| KAL1 | Display reconciliation ledger | Check cross-CC CO postings |
| KALC | Reconciliation posting | Execute cross-CC FI reconciliation |

---

## Section 4: CO-FI Integration Points -- Verified Facts

### 4.1 CO-FI Integration Point Catalog

Every scenario where CO and FI interact, documenting the direction of flow and the tables involved:

**Direction 1: FI → CO (Automatic — Primary Cost Element Postings)**

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

**Direction 2: CO → FI (Settlement with External Receivers)**

| CO Transaction | CO T-Code | FI Impact | FI Tables Updated | Condition |
|---------------|-----------|-----------|-------------------|-----------|
| Settle order to GL account | KO88 (KST receiver) | FI document created | BKPF, BSEG | Category 22 CE; receiver = GL account |
| Settle order to asset/AUC | KO88 (FXA receiver) | FI document (capitalization) | BKPF, BSEG, ANLA/ANLP | Category 22 CE; receiver = asset |
| Settle production order | CO88 | FI document (variance to P&L or inventory) | BKPF, BSEG | Settlement rule with FI receiver |
| Reconciliation posting | KALC | FI intercompany documents | BKPF, BSEG | Cross-CC CO postings exist in COFIT |

**Direction 3: CO Internal (No FI Impact)**

| CO Transaction | CO T-Code | CO Tables Updated | FI Impact |
|---------------|-----------|-------------------|-----------|
| Assessment | KSU5 | COBK, COEP, COSS (secondary) | NONE — stays in CO |
| Distribution | KSV5 | COBK, COEP, COSP (primary CEs preserved) | NONE — stays in CO |
| Activity allocation | KB21N | COBK, COEP, COSS | NONE — stays in CO |
| Overhead calculation | KGI2 | COBK, COEP, COSS | NONE — stays in CO |
| Reposting | KB61 | COBK, COEP | NONE — stays in CO |
| Actual price calculation | KSII | Recalculates prices; may adjust COSS | NONE — stays in CO |
| Settle order to cost center | KO88 (CTR receiver) | COBK, COEP, COSS | NONE — stays in CO |
| Settle order to CO-PA | KO88 (RKS receiver) | COBK, COEP, CO-PA tables | NONE — stays in CO |

### 4.2 Transaction Trace: "What Happens in CO When I Post FB50 to a P&L Account?"

This is the core CO-FI integration trace, answering the fundamental question.

**Trigger:** GL Accountant posts FB50 with a P&L GL account (e.g., 400000 Salaries) and enters cost center 1000.

**Step 1: FI Document Creation**
- BKPF header created with document number, posting date, document type SA
- BSEG line items: Dr 400000 (expense), Cr 113100 (bank/clearing)
- FI document is complete and posted

**Step 2: Cost Element Check**
- System reads CSKB for KSTAR = 400000 in the controlling area
- If found (primary CE, category 1): proceed to Step 3
- If NOT found: no CO posting — the GL account is FI-only (balance sheet or unmapped P&L)

**Step 3: CO Account Assignment Validation**
- System checks: does the FI document line item have a CO account assignment?
  - Cost center (KOSTL) → post to cost center
  - Internal order (AUFNR) → post to order
  - WBS element (PS_PSP_PNR) → post to project
- If no CO assignment AND no OKB9 default: posting FAILS — "Enter a CO account assignment"
- If OKB9 default exists: system uses the default cost center

**Step 4: CO Document Creation**
- COBK header: CO document number (different from FI doc), posting date, controlling area
- COEP line item: KSTAR (cost element = 400000), OBJNR (CO object = cost center 1000), WKGBTR (amount in CC currency), BELNR (reference to FI document number)
- COSP updated: period total for cost element 400000 on cost center 1000 incremented

**Step 5: PCA Update (if active)**
- System reads CSKS-PRCTR for cost center 1000 → finds profit center PC-1000
- GLPCA (PCA actual line items) updated with the posting amount under profit center PC-1000
- This is how PCA captures FI postings: via the cost center → profit center assignment chain

**Step 6: Verification**
- FI: FBL3N or FAGLB03 shows the GL posting to account 400000
- CO: KSB1 shows the CO line item on cost center 1000 for cost element 400000
- PCA: KE5Z shows the amount under profit center PC-1000
- All three reports show the SAME amount for this posting (primary CE flow)

Confidence: HIGH (standard CO-FI integration flow, consistent with existing KB)

### 4.3 Transaction Trace: "What Happens When KO88 Settles an Order to a GL Account?"

**Trigger:** Cost Accountant runs KO88 for internal order 800001 with settlement rule: 100% to GL account 490000 (expense clearing).

**Step 1: Read Order Costs**
- System reads COEP for order 800001: total actual costs (sum of all primary + secondary postings)
- Example: 50,000 EUR total costs collected on the order

**Step 2: Read Settlement Rule**
- COBRB: receiver type KST (GL account), receiver = 490000, percentage = 100%
- Settlement cost element: category 22 CE (e.g., 690000 "Settlement to GL")

**Step 3: CO Document Creation (Settlement)**
- COBK/COEP: Credit order 800001 by 50,000 EUR (using settlement CE 690000)
- Order balance reduced to zero (fully settled)

**Step 4: FI Document Creation (External Settlement)**
- Because receiver type = KST (GL account), settlement creates an FI document
- BKPF header: document type SA, posting date = settlement period
- BSEG: Dr 490000 (expense clearing GL account) 50,000 EUR
- BSEG: Cr varies — depends on allocation structure (OKO6) mapping

**Step 5: Verification**
- KOB1: Order 800001 shows settlement credit line
- FBL3N: GL account 490000 shows the settlement debit
- KO03: Order status may be set to TECO (technically complete) after settlement

Confidence: HIGH (standard KO88 settlement mechanics, verified against existing tcodes.md and processes.md)

### 4.4 Period-End CO-FI Timing

```
FI Period-End (F.05 FX revaluation, FBS1 accruals, AFAB depreciation)
    → MM Period-End (MMPV, CKMLCP)
        → CO Period-End (KB61 → KGI2 → KSU5/KSV5 → KO88/CO88 → KSII → KALC → lock period)
```

**Key timing dependencies:**
1. All FI postings must complete before CO period-end — CO allocations use the balances at execution time
2. MM period-end (inventory adjustments, material ledger closing) must complete because they generate FI postings that flow to CO
3. CO period-end runs LAST: repost → allocate → settle → actual prices → reconciliation → close
4. KALC (reconciliation posting) runs after all CO allocations and settlements but before period lock

This timing is already documented in processes.md Section 5 but the integration.md should cross-reference it explicitly.

Confidence: HIGH (verified against existing processes.md period-end sequence)

---

## Section 5: File Structure Decisions

### 5.1 Recommendation: Create co-advanced.md (Parallel to mm-advanced.md and sd-advanced.md)

**Recommendation:** YES, create `modules/co/co-advanced.md` to hold the cost element mapping walkthrough, decision trees, and troubleshooting, paralleling the MM and SD module structure.

**Rationale:**
- Maintains structural consistency across all four modules (fi-advanced.md, mm-advanced.md, sd-advanced.md, co-advanced.md)
- The CO CLAUDE.md file index already references integration.md and patterns.md; adding co-advanced.md is the natural extension
- Cost element mapping, decision trees, and troubleshooting are module-internal concerns

**File allocation:**

| Content | File | Rationale |
|---------|------|-----------|
| Cost element mapping walkthrough (CE types, CO-FI flow, reconciliation walkthrough) | modules/co/co-advanced.md (Section 1) | CO-internal concern; the "account determination equivalent" for CO |
| Decision trees (10 trees: allocation, settlement, hierarchy, planning, transfer pricing) | modules/co/co-advanced.md (Section 2) | Parallel to mm-advanced.md Section 2 |
| Troubleshooting (10 entries, symptom-first) | modules/co/co-advanced.md (Section 3) | Parallel to mm-advanced.md Section 3 |
| CO-FI integration point catalog + transaction traces | modules/co/integration.md | This IS integration — belongs in the integration file |
| FB50-to-CO trace and KO88-to-FI trace | modules/co/integration.md | Primary CO-FI handoff documentation |
| Period-end CO-FI timing | modules/co/integration.md | Cross-module timing reference |
| Reconciliation ledger (KALC/COFIT) | modules/co/integration.md | Cross-module reconciliation topic |

### 5.2 Recommendation: Cost Element Mapping First in co-advanced.md

**Recommendation:** Cost element mapping walkthrough first (Section 1), then decision trees (Section 2), then troubleshooting (Section 3).

**Rationale:** Mirrors mm-advanced.md and sd-advanced.md structure (OBYC/VKOA first, decision trees second, troubleshooting third). The cost element mapping is CO's equivalent of OBYC/VKOA — the foundational "how does account determination work" content.

### 5.3 Decision Tree Count: 10 (Not 12)

**Recommendation:** 10 decision trees instead of 12, reflecting CO's narrower configuration decision space compared to MM and SD. CO has fewer distinct "should I use A or B?" decisions because CO configuration patterns are more formulaic.

---

## Section 6: Existing Content Dependencies and Cross-References

### 6.1 Content Already in Knowledge Base That Phase 10 Builds On

| File | What It Contains | How Phase 10 Uses It |
|------|-----------------|---------------------|
| co/master-data.md | Cost element categories (1-43), CSKA/CSKB tables, cost center (CSKS), COSP/COSS totals | Phase 10 REFERENCES this (does not duplicate); adds the mapping walkthrough explaining the CO-FI flow |
| co/tcodes.md | KA01/KA06, KS01, KO88, KSU5, KSV5, KSII, KB61, KGI2 | Phase 10 REFERENCES these in decision trees and troubleshooting |
| co/config-spro.md | OKKP, OKB9, OKO7, OKO6, KSU1, KSV1, OKKN | Phase 10 decision trees provide DESIGN GUIDANCE for the config documented here |
| co/processes.md | Period-end sequence, assessment vs distribution, product costing run | Phase 10 troubleshooting covers FAILURES in these processes |
| fi/account-determination.md | OBYC framework; no CO-specific account determination content | Phase 10 is CO's equivalent — explains the CO-FI flow (not OBYC-based but CE-based) |
| fi/fi-advanced.md | Decision tree and troubleshooting format template | Phase 10 FOLLOWS this format exactly |
| mm/mm-advanced.md | Structural template (OBYC walkthrough + 12 trees + 12 troubleshooting) | Phase 10 FOLLOWS this structure (CE mapping + 10 trees + 10 troubleshooting) |
| mm/integration.md | MM-FI integration point catalog format | Phase 10 FOLLOWS this format for CO-FI catalog |

### 6.2 Prior Decisions That Constrain Phase 10

From Phase 9:
- Cost element categories documented with specific numbers (1,3,4,11,12,22 primary; 21,31,41,42,43 secondary) — must be consistent
- Assessment vs distribution distinction documented in processes.md — Phase 10 decision tree must not contradict
- CK24 two-step (mark then release) documented — troubleshooting entry must be consistent
- Period-end sequence: KB61→KGI2→KSU5→KSV5→KO88→CO88→KSII — troubleshooting must reference this exact sequence
- PCA separate ledger (GLPCA/GLPCT) documented as ECC 6 specific — reconciliation walkthrough must use these tables
- CO-PA deferred to Phase 10 for deeper coverage — Phase 10 should add KOFK and CO-PA basic integration

### 6.3 Files to Be Modified/Created

| File | Action | Content |
|------|--------|---------|
| modules/co/co-advanced.md | CREATE | CE mapping walkthrough + 10 decision trees + 10 troubleshooting entries |
| modules/co/integration.md | REPLACE placeholder | CO-FI integration point catalog + transaction traces + reconciliation + period-end timing |
| modules/co/CLAUDE.md | UPDATE | Add co-advanced.md and update integration.md entries in File Index |

---

## Common Pitfalls for Content Authors

### Pitfall 1: Treating CO-FI Like OBYC or VKOA
**What goes wrong:** Trying to frame CO-FI integration as a single "account determination" lookup like OBYC (movement type → GL account) or VKOA (billing → GL account)
**Correct approach:** CO-FI integration is fundamentally different — it is bidirectional (FI→CO via primary CEs; CO→FI only via category 22 settlement). The walkthrough should explain the flow, not a lookup table.

### Pitfall 2: Saying CO and FI Totals Should Match
**What goes wrong:** Documenting that KSB1 totals should equal FBL3N totals for the same cost center
**Correct fact:** CO totals = primary (from FI) + secondary (CO-only). CO will ALWAYS show higher totals than FI for any cost center that receives allocations. Only primary CE totals should match.

### Pitfall 3: Ignoring the OKB9 Error as the #1 Issue
**What goes wrong:** Burying the "Enter a CO account assignment" error in the middle of troubleshooting
**Correct approach:** This is the single most common CO error. It should be troubleshooting entry #1 with prominent coverage.

### Pitfall 4: Confusing Category 21 and 22 Settlement
**What goes wrong:** Saying all settlement creates FI documents
**Correct fact:** Only category 22 (external settlement) creates FI documents. Category 21 (internal settlement) is CO-only. The settlement profile (OKO7) and receiver type determine which is used.

### Pitfall 5: Omitting the Reconciliation Ledger
**What goes wrong:** Not documenting KALC/COFIT for cross-company-code scenarios
**Correct approach:** The reconciliation ledger is a critical ECC 6-specific concept that does not exist in S/4HANA. It must be documented with the appropriate S/4HANA disambiguation.

### Pitfall 6: Documenting Transfer Pricing as Standard Practice
**What goes wrong:** Presenting PCA transfer pricing (1KEG) as a common implementation pattern
**Correct approach:** Most ECC 6 implementations do NOT use PCA transfer pricing. The decision tree should clearly state this is optional and uncommon, with guidance on when it IS appropriate.

---

## Open Questions

1. **Exact COFIT/COFIS table structure and key fields**
   - What we know: COFIT is the reconciliation ledger totals table; COFIS is the single records table; KALC reads and posts from these
   - What's unclear: Exact key field structure and which fields drive the intercompany posting generation
   - Recommendation: Document at the conceptual level (what the reconciliation ledger does, when to run KALC); note exact table fields as LOW confidence

2. **KALC configuration prerequisites**
   - What we know: KALC requires cross-company-code indicator in OKKP; reconciliation GL accounts must be defined
   - What's unclear: Exact SPRO path for defining reconciliation GL accounts for cross-CC postings
   - Recommendation: Document KALC as a period-end step; reference OKKP for the activation; flag detailed configuration as needing validation

3. **CO-PA Integration Depth for Phase 10**
   - What we know: Phase 9 deferred CO-PA deep coverage to Phase 10; KOFK (CO-PA account determination) exists
   - What's unclear: How deep to go — should Phase 10 cover KOFK configuration, CO-PA operating concern setup, value fields/characteristics?
   - Recommendation: Cover KOFK at the same level as KOFI in fi/account-determination.md (framework + key concepts); defer CO-PA operating concern configuration to Phase 12 (solution patterns)

4. **Exact SAP message IDs for CO troubleshooting entries**
   - What we know: KI, KO, KD, KS message classes are correct; specific numbers need verification
   - What's unclear: Exact message numbers for each troubleshooting scenario
   - Recommendation: Document the message CLASS and symptom; include specific numbers where verified; the pattern is more important than the exact number

---

## Sources

### Primary (HIGH confidence -- existing knowledge base, verified in prior phases)
- modules/co/master-data.md -- cost element categories, CSKA/CSKB, cost center CSKS, COSP/COSS tables
- modules/co/tcodes.md -- 63 T-codes with usage and gotchas
- modules/co/config-spro.md -- OKKP, OKB9, OKO7, OKO6, allocation cycles, product costing
- modules/co/processes.md -- period-end sequence, assessment vs distribution, product costing run
- modules/fi/account-determination.md -- OBYC and VKOA frameworks, account determination principles
- modules/mm/mm-advanced.md -- structural template for advanced module content
- modules/sd/sd-advanced.md -- structural template for advanced module content (via Phase 8 research)
- modules/mm/integration.md -- structural template for integration point catalog
- modules/sd/integration.md -- structural template for integration point catalog (via Phase 8 research)

### Secondary (MEDIUM confidence -- SAP standard architecture, cross-verified with existing KB)
- CO-FI real-time integration mechanism (primary CE = GL account, automatic CO document creation)
- OKB9 default account assignment as the #1 CO error prevention mechanism
- Reconciliation ledger concept (COFIT/COFIS, KALC T-code)
- Settlement receiver types and FI document creation rules (category 22 for external, 21 for internal)
- PCA separate ledger (GLPCA) reconciliation with FI (KE5Z vs FAGLB03)

### Tertiary (LOW confidence -- training data, needs validation)
- Exact COFIT/COFIS table key fields and structure
- KALC configuration prerequisites and reconciliation GL account SPRO path
- Specific SAP message IDs (KI xxx, KO xxx numbers) for troubleshooting scenarios
- PCA transfer pricing (1KEG/3KEH) detailed configuration mechanics

---

## Metadata

**Confidence breakdown:**
- Cost element mapping (CE types, categories, GL account relationship): HIGH -- verified against existing master-data.md
- CO-FI real-time integration (automatic CO document from FI posting): HIGH -- fundamental SAP architecture
- Reconciliation ledger (COFIT/COFIS, KALC): MEDIUM-HIGH -- concept verified; table details need validation
- Decision tree topics: HIGH -- covers standard CO configuration areas from config-spro.md
- Troubleshooting patterns: MEDIUM-HIGH -- symptom patterns standard; specific message IDs need validation
- CO-FI integration points: HIGH -- consistent with existing KB processes.md and config-spro.md
- FB50-to-CO trace: HIGH -- standard CO-FI integration flow
- KO88-to-FI trace: HIGH -- standard settlement mechanics
- Transfer pricing (1KEG): MEDIUM -- less commonly implemented feature
- Period-end timing: HIGH -- verified against existing processes.md

**Research date:** 2026-02-17
**Valid until:** Stable -- ECC 6.0 CO-FI integration patterns do not change. Review only if knowledge base scope extends to deep CO-PA (operating concern configuration) or Material Ledger CO integration.
