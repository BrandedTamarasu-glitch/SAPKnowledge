---
module: cross-module
content_type: playbooks
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-18
related_modules: [mm, sd, fi, co]
---

# Cross-Module Scenario Playbooks

> ECC 6.0 reference. Eight deep-dive implementation walkthroughs for complex SAP ECC 6 scenarios. Each playbook synthesizes cross-module configuration, master data, process flow, and test scenarios that cannot be found in any single module file. For S/4HANA differences, see the S/4HANA Differences section at the end.

## Prerequisites

Read these module files for config detail referenced in the playbooks:

- `modules/mm/mm-advanced.md` — OBYC account determination, decision trees (split valuation DT 6, batch DT 7, serial DT 8, subcontracting DT 9)
- `modules/sd/sd-advanced.md` — VKOA account determination, intercompany billing, decision trees
- `modules/mm/config-spro.md` — MM SPRO configuration paths
- `modules/sd/config-spro.md` — SD SPRO paths (VOFA, VOV7, copy control)
- `modules/co/co-advanced.md` — CO-FI integration, settlement rules
- `cross-module/mm-sd-integration.md` — Consignment movement types, third-party, subcontracting mechanics

---

## Process Playbooks

---

## Playbook 1: Consignment Stock

> Consignment enables two distinct business models — vendor-managed inventory in your warehouse (vendor consignment, special stock K) and your inventory at customer sites billed at consumption (customer consignment, special stock W) — each with opposite ownership direction but sharing the same special stock type indicator.

### Business Context

Standard procurement and sales transfer ownership immediately at goods receipt or delivery. Consignment defers the ownership transfer to a later event: withdrawal for vendor consignment, consumption confirmation for customer consignment. This is used when:

- **Vendor consignment:** Vendor wants to see usage patterns before invoicing; buyer wants to defer cash outflow until actual consumption.
- **Customer consignment:** Company wants goods physically at the customer site for immediate availability but retains ownership and recognizes revenue only at consumption.

The critical distinction from standard processes: no vendor liability at GR (vendor consignment), no billing at delivery (customer consignment). Both models use special stock indicator K but for opposite ownership roles.

### Prerequisites

- MM module active with plant and storage location configured (OX10, OX18)
- For vendor consignment: consignment info record (ME11) required
- For customer consignment: SD module active; consignment order types (KB, KE, KR, KA) configured in VOV8; item categories KBN, KEN, KRN, KAN assigned in OVLP
- OBYC transaction key KON configured (for vendor consignment withdrawal 411K)

### Configuration Walkthrough

#### Step 1: MM — Vendor Consignment Info Record

**T-code:** ME11
**Settings:** Info category = Consignment; vendor + material + purchasing org + plant; enter consignment price per unit (the price at which you pay the vendor when you withdraw stock). Leave standard price blank — consignment price is from the info record condition.
**Gotcha:** The consignment info record price is used for the vendor liability posting at consumption (411K or 201K withdrawal), NOT at goods receipt. At GR (101K), no vendor liability posts — the vendor owns the stock. If no consignment info record exists, movement type 411K will post the withdrawal at moving average price, not the agreed consignment price.

#### Step 2: SD — Consignment Order Types (Customer Consignment)

**SPRO Path:** Sales and Distribution → Sales → Sales Documents → Sales Document Header → Define Sales Document Types
**T-code:** VOV8
**Settings:** SAP delivers standard consignment order types KB (fill-up), KE (issue), KR (pick-up), KA (returns). Verify these are active. If your implementation uses custom types (ZKB, ZKE, etc.), confirm copy control and item category assignments are in place.
**Gotcha:** Billing type must be configured correctly for KE (consignment issue) only — KB, KR, and KA do not generate invoices.

#### Step 3: SD — Item Category Configuration

**SPRO Path:** Sales and Distribution → Sales → Sales Documents → Sales Document Item → Define Item Categories
**T-code:** VOV7
**Key item categories:**
- **KBN** (fill-up): special stock = W; billing relevance = blank (no billing); schedule line category with movement type 631
- **KEN** (issue): special stock = W; billing relevance = A (delivery-related); schedule line with movement type 633
- **KRN** (pick-up): special stock = W; billing relevance = blank; schedule line with movement type 632
- **KAN** (returns): special stock = W; schedule line with movement type 634
**Gotcha:** The schedule line category drives the movement type. If the wrong movement type fires (e.g., 601 instead of 631), standard stock is reduced instead of creating consignment stock — a critical error that will not show an error message.

#### Step 4: FI — OBYC Configuration for Vendor Consignment

**T-code:** OBYC
**Transaction key KON:** Consignment payables. Fires when movement type 411K posts vendor consignment withdrawal (converts consignment stock to own stock, creates vendor liability). Configure KON → GL account (vendor consignment payable) for each valuation class used on consignment materials.
**Transaction key AKO:** Expense/revenue from consignment price difference. Fires only for standard price (S) materials when the consignment info record price differs from the material standard price.
**Gotcha:** If KON is not configured in OBYC, movement type 411K fails with an account determination error. This is frequently overlooked during go-live configuration since KON is not tested in standard procurement scenarios.

#### Step 5: SD — Copy Control for Consignment Issue Billing

**T-code:** VTFL (delivery to billing copy control)
**Settings:** Verify that delivery type LF with billing type created for consignment issue (billing type F2 or custom) has the correct data transfer routine. The billing quantity source must be the delivered quantity.
**Gotcha:** Consignment billing uses delivery-related billing (movement 633 triggers the billing via delivery). If order-related billing is mistakenly configured, the consignment issue delivery cannot generate the billing document.

### Master Data Setup

| Object | What to Create | T-code | Cross-Module Link |
|--------|---------------|--------|-------------------|
| Consignment info record | Vendor + material + price per consignment unit | ME11 | Drives KON liability at withdrawal |
| Customer master | Standard KNVV; no special field for consignment | XD01 | Consignment controlled by SD doc type |
| Material master | No special field needed; pricing via info record (MM); item cat group = NORM in MVKE | MM01/MM02 | MVKE-KTGRM drives VKOA at billing |
| Consignment PO (vendor) | ME21N standard — system auto-proposes consignment PO based on info record | ME21N | No vendor liability until 411K |

### Process Flow

**Vendor Consignment:**

| Step | Activity | T-code | Movement Type | FI Impact |
|------|----------|--------|---------------|-----------|
| 1 | Create consignment PO | ME21N | — | None |
| 2 | Post GR of consignment stock | MIGO | 101K | BSX Dr inventory (at standard price); no vendor liability — KON does NOT fire |
| 3 | Withdraw from consignment (consume or move to own stock) | MIGO | 411K | KON Cr vendor liability; BSX Dr own stock; AKO for S-price difference |
| 4 | Return to vendor (if needed) | MIGO | 412K | Reverse of 411K |
| 5 | Vendor invoice based on 411K withdrawals | MIRO | — | Standard vendor invoice using consignment withdrawal quantities |

**Customer Consignment:**

| Step | Activity | T-code | Movement Type | FI/Revenue Impact |
|------|----------|--------|---------------|-------------------|
| 1 | Create fill-up order | VA01 (KB) | — | None |
| 2 | Create delivery and PGI | VL01N, VL02N | 631 | BSX Dr consignment-at-customer (W stock); BSX Cr unrestricted stock — no revenue |
| 3 | Customer confirms consumption | VA01 (KE) | — | None |
| 4 | Issue delivery and PGI | VL01N, VL02N | 633 | OBYC GBB Dr COGS; BSX Cr consignment stock — REVENUE recognition point |
| 5 | Create billing document | VF01/VF04 | — | VKOA Dr Customer, Cr Revenue |
| 6 | Retrieve unsold stock (pick-up) | VA01 (KR), VL02N | 632 | Stock returns to unrestricted; no billing |
| 7 | Customer returns issued goods | VA01 (KA), VL02N | 634 | Credit memo; VKOA revenue reversal |

### Test Scenarios

**Test 1: Vendor Consignment — Receive, Withdraw, Verify Liability**

1. Create consignment PO: ME21N, document type NB, item category K (Consignment). Enter vendor, material, quantity. Verify that a consignment info record (ME11) exists for vendor + material + purchasing org.
2. Post GR: MIGO, Action = Goods Receipt, reference = PO. Movement 101K. After posting, run MB52 — material should appear in the "Vendor Consignment" column (not Unrestricted). Run FBL1N for the vendor — NO open item should exist (vendor owns the stock).
3. Withdraw from consignment: MIGO, Movement Type = 411K (withdrawal from consignment). Enter material, quantity, plant. After posting, run FBL1N — a new open item should exist for the vendor (the consignment liability). Run MB52 — vendor consignment quantity decreases; own stock increases.
4. Post vendor invoice: MIRO referencing the consignment PO. Verify three-way match uses withdrawal quantity (411K document), not GR quantity (101K).

**Test 2: Customer Consignment — Fill-Up, Issue, Verify Revenue**

1. Create consignment fill-up order: VA01, order type KB. Enter sold-to party, material, quantity. Create delivery (VL01N) and post PGI (VL02N). Verify movement type 631 was posted. Run MB52 — material should show in "Customer" special stock W column for the ship-to party. Run FBL5N — NO customer open item (no billing at fill-up).
2. Create consignment issue order: VA01, order type KE. Create delivery and PGI. Verify movement type 633. Run MB52 — W stock decreases. Run VF04 billing due list — the KE delivery should appear as billable. Create billing document (VF01). Run FBL5N — customer open item (invoice) now exists. Verify revenue posted to correct GL via VKOA (FBL3N or BKPF/BSEG).

**Test 3: Consignment Inventory Reconciliation**

1. Run MB52 for the customer (select "Customer Consignment" stock): verify system shows the correct quantity at the customer site.
2. Run MB54: alternative consignment at customer report, shows special stock W per customer per material.
3. At period-end, the consignment stock at customer (W) remains on your balance sheet as inventory — verify that the inventory account balance includes consignment stock value.

### Cross-Module Perspective

**FI Account Assignment — Customer Consignment:**
- Fill-up (631): BSX → inventory reclassification between storage locations (from own plant to "at customer"). No revenue. No cost event. Material stays on company balance sheet.
- Issue (633): At PGI, OBYC GBB/VAX (or VAY) → COGS debit; BSX → inventory credit. At billing, VKOA ERL → revenue credit; customer reconciliation account → receivable debit.
- The timing gap between PGI (cost) and billing (revenue) creates a period-end issue if they fall in different periods. Accrue unbilled revenue at period-end via FBS1: Dr Unbilled Receivables / Cr Accrued Revenue. See `modules/sd/integration.md` Section 5b.

**CO Account Assignment:**
- Vendor consignment 411K withdrawal: no CO posting unless the material is issued to a cost object (201K consumption to cost center creates GBB/VBR cost center charge).
- Customer consignment 633 GI: if the sales order has a WBS element or internal order, VAY (instead of VAX) fires and the COGS posts to the CO object.

**Integration Cross-References:**
- Movement types 101K, 411K, 412K: `modules/mm/mm-advanced.md` Section 1b (By Movement Type table)
- Movement types 631-634: `cross-module/mm-sd-integration.md` Section Consignment
- KON and AKO account keys: `modules/mm/mm-advanced.md` Section 1a (By Transaction Key table)
- VKOA at billing: `modules/sd/sd-advanced.md` Section 1

### Common Pitfalls

- **No vendor liability at GR (expected behavior, not a bug):** Movement 101K for consignment GR does NOT post a vendor liability. Consultants expecting the WRX/vendor posting see a blank FBL1N and think the posting failed. The liability only appears when stock is withdrawn (411K).
- **Wrong billing document type for consignment issue:** If KE billing uses a pro forma billing type (F5/F8), no FI document posts. Check VOFA billing type configuration — pro forma indicator must be blank for consignment issue billing.
- **Consignment stock not visible in MB52:** Verify the plant and storage location filter in MB52. Customer consignment (W stock) requires "Special Stock = W" selection. Vendor consignment (K stock) requires the "Vendor Consignment" tab.
- **Consignment info record not found at 411K:** The withdrawal movement type 411K looks for the consignment info record for the vendor + material + plant combination. If the info record is for a different purchasing org or plant, the lookup fails and the withdrawal uses the material moving average price — creating valuation errors.

---

## Playbook 2: Intercompany Sales

> Intercompany sales (IC billing) handles goods flow between plants in different company codes, generating two legal billing documents: a customer invoice in the selling company code (order → delivery → F2 invoice) and an intercompany invoice from the delivering company code to the ordering company code (IV billing type), with FI postings in both company codes.

### Business Context

When a sales order is placed with a selling company (Company A, sales org 1000) but goods are delivered by a different company (Company B, plant 2000), two separate billing cycles must occur:

1. **Customer billing** (Company A → Customer): Standard F2 invoice at the customer price. Revenue posts in Company A's books.
2. **Intercompany billing** (Company B → Company A): IV invoice at the intercompany transfer price. Intercompany revenue posts in Company B; intercompany expense posts in Company A.

This creates a proper arm's length transaction between legal entities, required for consolidated financial reporting.

### Prerequisites

- Two company codes set up with separate FI books
- Delivering plant assigned to Company B, selling sales org assigned to Company A
- SD module active in both company codes
- Partner function PI (intercompany partner) configured in the selling company's document types

### Configuration Walkthrough

#### Step 1: SD — Partner Function PI (Intercompany)

**SPRO Path:** Sales and Distribution → Basic Functions → Partner Determination → Set Up Partner Determination → Partner Functions
**Settings:** Create or verify partner function PI (Ordering Company Code for Intercompany). This partner function links the ordering sales organization to the delivering plant's company code.

In the sales order, partner PI is automatically proposed based on the delivering plant. The PI partner drives which company code is billed via the IV billing type.

#### Step 2: SD — Intercompany Billing Type IV

**T-code:** VOFA
**SPRO Path:** Sales and Distribution → Billing → Billing Documents → Define Billing Types
**Settings:** Billing type IV (intercompany billing). Key fields: transaction group = 7 (intercompany billing), document type = intercompany, account determination procedure (links to VKOA for IC revenue).

The IV billing type must be assigned to the delivery type in copy control (VTFL) so that when a delivery from Plant 2000 is billed, the system generates both F2 (to customer) and IV (to ordering CC).

#### Step 3: SD — Copy Control for Intercompany (VTFL)

**T-code:** VTFL (delivery to billing copy control)
**Settings:** For the delivery type (e.g., LF from Plant 2000 in Company B), configure:
- Billing type F2: copied to Company A sales order (standard customer billing)
- Billing type IV: copied to Company B intercompany billing

The system determines which billing type to use based on whether the delivering plant and ordering sales organization belong to different company codes.

#### Step 4: SD — Intercompany Pricing Procedure

**T-code:** V/09 (pricing procedures), OVKK (determination)
**Settings:** Create a separate pricing procedure for intercompany pricing (e.g., ZICP00). This procedure contains the intercompany price condition type (e.g., PI01 = intercompany price, typically a fixed amount or percentage of customer price). The IC pricing procedure is assigned in OVKK for the delivering sales organization.

The intercompany price should reflect the transfer price agreed between the two companies (cost + markup, or cost price, per transfer pricing policy).

#### Step 5: FI — VKOA for Intercompany Revenue

**T-code:** VKOA
**Settings:** Configure account determination for the IV billing type in the delivering company code. The account key (e.g., ERL) must map to an intercompany revenue GL account (e.g., IC Revenue 8XXXXX) rather than the standard external revenue account.

The ordering company code also needs VKOA configured: the PI partner's billing creates an intercompany expense posting (Dr IC Expense, Cr IC Payable) in Company A's books.

**Gotcha:** VKOA determination uses the delivering sales organization (Company B's sales org). If Company B does not have its own sales organization for IC billing, a separate SD sales area must be created for the delivering entity. See `modules/sd/sd-advanced.md` Section 1 for full VKOA chain.

#### Step 6: SD/FI — Partner and Customer Master for IC Billing

**T-code:** XD01 (Customer Creation)
**Settings:** The delivering company code (Company B) must be set up as a customer in the ordering company code (Company A) for the IC payable/receivable clearing. Similarly, the ordering company code must be set up as a customer in the delivering company code.

These IC customer/vendor pairings ensure that the IV billing creates proper open items for intercompany clearing at period-end.

### Master Data Setup

| Object | In Which Company | What to Configure | T-code |
|--------|-----------------|-------------------|--------|
| IC customer master (Company B as customer in Company A) | Company A (ordering CC) | KNA1 + KNB1; reconciliation account = IC Receivable | XD01 |
| IC customer master (Company A as customer in Company B) | Company B (delivering CC) | KNA1 + KNB1; reconciliation account = IC Receivable | XD01 |
| Delivering plant | Company B | Plant 2000 assigned to Company B via OX18 | OX18 |
| Intercompany condition records | Company B sales org | PI01 price condition for the transfer price | VK11 |
| Partner function PI | Selling sales org | Assigned to Company A's order types | VOV8/VOFA |

### Process Flow

| Step | Activity | T-code | Company | Document Created |
|------|----------|--------|---------|-----------------|
| 1 | Customer places order | VA01 | Company A (ordering) | Sales order VBAK — delivering plant 2000 (Company B) |
| 2 | Delivery created from Plant 2000 | VL01N | Company B (delivering) | Delivery LIKP from Plant 2000 |
| 3 | Goods issue from Plant 2000 | VL02N | Company B | Material doc (601); FI in Company B: Dr COGS, Cr Inventory |
| 4 | Customer billing (F2) | VF01 | Company A | F2 invoice VBRK; FI in Company A: Dr Customer, Cr Revenue (at customer price) |
| 5 | Intercompany billing (IV) | VF01 | Company B → Company A | IV invoice VBRK; FI in Company B: Dr IC Receivable, Cr IC Revenue (at transfer price); FI in Company A: Dr IC Expense, Cr IC Payable |
| 6 | IC settlement at period-end | F-32/F.13 | Both | IC receivable/payable cleared |

> **Key insight:** The IV billing (Step 5) creates FI documents in BOTH company codes simultaneously. Company B's books show intercompany revenue; Company A's books show intercompany expense. The net effect on the consolidated group is zero — both cancel on consolidation.

### Test Scenarios

**Test 1: End-to-End Intercompany Sales Order**

1. Create sales order: VA01, order type OR, sales org = Company A's sales org. Enter material and specify Plant 2000 (Company B) as the delivering plant. Verify that partner function PI is automatically determined from the delivering plant's company code assignment.
2. Create delivery: VL01N from the sales order. Verify shipping point resolves to a Plant 2000 shipping point. Post PGI (VL02N, movement type 601). Verify FI document in Company B: Dr COGS / Cr Inventory.
3. Create customer billing: VF04 or VF01 from the delivery. Billing type F2. Verify FI document in Company A: Dr Customer / Cr Revenue at customer price. Check FBL5N for the customer open item in Company A.
4. Create intercompany billing: The system should automatically propose IV billing from the same delivery. Create IV invoice. Verify FI in Company B: Dr IC Receivable / Cr IC Revenue (at transfer price). Verify FI in Company A: Dr IC Expense / Cr IC Payable.
5. Run FBL5N in both company codes: Company A shows customer open item (F2) and IC payable (IV). Company B shows IC receivable.

**Test 2: Intercompany Price Verification**

1. After step 4 above, check the pricing in the IV billing document (VF03): the IV price should reflect the transfer price from PI01 condition, NOT the customer price.
2. The margin between customer price (F2) and transfer price (IV) represents Company A's profit; Company B's revenue equals the transfer price.
3. Verify VKOA account determination: in Company B's IV billing FI document, revenue should post to the IC Revenue GL (8XXXXX), not the external revenue GL. In Company A's FI document, IC expense should post to the IC Expense GL.

### Cross-Module Perspective

**FI Account Structure:**
- Company A: Dr Customer (via VKOA ERL on F2) / Cr External Revenue; Dr IC Expense / Cr IC Payable (via IC billing)
- Company B: Dr COGS (OBYC at PGI) / Cr Inventory; Dr IC Receivable / Cr IC Revenue (via VKOA on IV billing)

**CO-PA Treatment:**
- In Company A, CO-PA (if configured) receives the profitability segment from the customer billing (F2) — revenue and customer COGS at the IC transfer price post to CO-PA for Company A's profitability.
- In Company B, IC revenue flows to CO-PA as IC sales revenue, with COGS from the GI posting.
- Transfer pricing adjustment requires coordination between the CO-PA configurations of both company codes.

**Period-End IC Reconciliation:**
- IC receivables (Company B) must match IC payables (Company A) before group consolidated financials are produced.
- F.13 (automatic clearing) or manual clearing (F-32) reconciles IC open items within a reconciliation cutoff.

**Integration Cross-References:**
- STO vs IC Billing comparison: `cross-module/mm-sd-integration.md` Section Stock Transport Orders
- VKOA IV billing account keys: `modules/sd/sd-advanced.md` Example 8
- Partner function configuration: `modules/sd/config-spro.md` Section 8

### Common Pitfalls

- **IV billing not created automatically:** If the delivering plant and ordering company code are not in different company codes, SAP does not trigger IC billing. Verify company code assignment (OX18: plant → company code).
- **Missing IC customer master:** The IV billing requires a customer master in the delivering company code (Company B) representing Company A. Without it, the IV billing fails with "partner not found."
- **Transfer price = 0:** If the PI01 condition record is missing or expired, the intercompany price is 0. The IV billing creates an IC invoice for zero value. Always verify PI01 condition records before go-live.
- **Revenue posts to wrong account:** If VKOA for IV billing uses the same account key as F2 billing, IC revenue posts to external revenue GL. Configure separate account determination tables for IC billing type or use a distinct account key (e.g., ERL2) for IV billing.
- **CO-PA segment mismatch:** If Company A and Company B have different CO-PA characteristics, the profitability analysis may not balance at the group level. Align CO-PA segment definitions across company codes before IC billing goes live.

---

## Playbook 3: Third-Party Drop Shipment

> In third-party processing, the company accepts the customer order in SD but the vendor ships directly to the customer — the company never physically handles the goods. The sales order automatically generates a purchase requisition that drives the MM procurement cycle, and the company earns margin between the vendor invoice (MIRO) and the customer invoice (VF01).

### Business Context

Third-party processing eliminates the company's warehouse from the delivery chain. It is used when:
- The company acts as an agent or broker: takes the order but lacks inventory capacity
- The vendor specializes in direct shipment (drop-ship fulfillment)
- Lead time reduction: vendor ships from their warehouse directly to the customer

The key characteristic: NO goods movement through the company's own warehouse. No movement type 601, no inventory posting. The company only sees two financial transactions: vendor invoice (MIRO) and customer billing (VF01).

### Prerequisites

- Item category TAS configured in VOV7 (billing relevance = B: order-related billing)
- Item category group BANS on the material master (MVKE-MTPOS) for third-party items, or manual override via OVLP
- Copy control configured for order-related billing (VTAF: billing document type from order)
- Vendor master with partner function OA (ordering address) for the vendor delivering to customer

### Configuration Walkthrough

#### Step 1: SD — Item Category TAS (Third-Party)

**T-code:** VOV7
**SPRO Path:** Sales and Distribution → Sales → Sales Documents → Sales Document Item → Define Item Categories
**Settings for TAS:**
- Item type: standard
- Billing relevance: **B** (order-related billing — CRITICAL: must be B, not A delivery-related, because no delivery is created for third-party)
- Create delivery: blank (no delivery for third-party)
- Purchasing: X (creates purchase requisition)
- Schedule line category: CS (third-party without GR requirement) or CB (third-party with statistical GR)

**Gotcha:** Billing relevance must be B (order-related). If set to A (delivery-related), billing cannot occur because no delivery is created in third-party processing. This is the most common third-party configuration error.

#### Step 2: SD — Schedule Line Category for Third-Party

**T-code:** VOV6
**Settings:** Schedule line category CS (or CB if statistical GR required):
- Movement type: blank (no physical goods movement)
- Item relevant for delivery: blank
- Purchasing/GR: triggers PR creation when set on the schedule line category
- CS = without GR (vendor invoice triggers billing); CB = with statistical GR (GR must be posted before billing is released)

The choice between CS and CB is a business decision: CB provides tighter control (buyer confirms GR before billing) at the cost of extra process steps.

#### Step 3: SD — Copy Control for Order-Related Billing

**T-code:** VTAF (billing document from sales document)
**Settings:** For sales document type OR with item category TAS → billing type F2:
- Billing quantity source: relevant billing quantity from schedule line (not from delivery)
- Data transfer routine: order-related billing routine

**Gotcha:** VTAF (order-to-billing) is used for third-party billing, NOT VTFL (delivery-to-billing). If VTFL is configured without VTAF, the billing due list (VF04) will not include third-party orders, and billing must be done manually with VF01.

#### Step 4: MM — Vendor Partner Functions for Drop Shipment

**T-code:** ME11 (info records) or directly on PO
**Settings:** The purchase order for third-party must have the customer's ship-to address as the delivery address on the PO item (EKPO-EVERS = third-party indicator). This is populated automatically from the sales order schedule line when PR is created.

Vendor partner function OA (Ordering Address) in the vendor master (LFA1/LFM1) is not typically the key config here — the delivery address on the third-party PO comes from the sales order's ship-to partner, populated via the automated PR creation.

#### Step 5: MM/SD — Account Assignment for CO

**Settings:** The purchase order from a third-party PR typically has account assignment category X (unknown at PR time, resolved at PO) or no account assignment (statistical GR scenario). For CO:
- If the company needs to track the cost against a project or cost center, configure account assignment category at the sales order level (account assignment from SD to MM).
- Account assignment category C (SD order) links the PO cost to the sales order for CO-PA purposes.

**Cross-reference:** OKB9 default account assignment configuration: `modules/co/config-spro.md`.

### Master Data Setup

| Object | Configuration | Purpose |
|--------|--------------|---------|
| Material master — MVKE-MTPOS | BANS (item cat group for third-party) | Ensures TAS item category is determined by OVLP for this material |
| Vendor master — LFA1/LFM1 | Standard vendor setup; no special consignment or drop-ship field | Vendor invoices at MIRO; delivery address from PO |
| Info record (ME11) | Standard purchasing info record (not consignment type) | Provides price and delivery time for PR-to-PO conversion |
| Source list (ME01) | Optional; links material to preferred vendor | Enables ME59N auto-conversion of third-party PR to PO |

### Process Flow

| Step | Activity | T-code | Who | Notes |
|------|----------|--------|-----|-------|
| 1 | Create sales order with TAS item | VA01 | Sales Rep | System auto-generates PR in background at order save |
| 2 | Review auto-generated PR | ME53N | Buyer | PR has account assignment = X (third-party); delivery address = customer ship-to |
| 3 | Convert PR to PO | ME21N (or ME59N) | Buyer | PO item has special stock = non-valuated (no inventory); delivery address on PO = customer |
| 4 | Send PO to vendor | — | Buyer | Vendor receives PO and ships directly to customer |
| 5 | Post statistical GR (if CB schedule line) | MIGO | Warehouse/AP | Statistical goods receipt — quantity confirmation only, no inventory change, no FI posting |
| 6 | Post vendor invoice | MIRO | AP Accountant | Dr GR/IR or DR purchase order expense / Cr Vendor. No inventory posting (no BSX) |
| 7 | Bill the customer | VF01/VF04 | Billing Clerk | Order-related billing (VTAF). FI: Dr Customer / Cr Revenue |

> **Statistical GR decision:** If schedule line category CS is used (no GR required), step 5 is skipped — vendor invoice immediately enables customer billing. If CB is used, a statistical GR must be posted before the billing document can be created. The statistical GR has no FI posting — it only confirms quantity for the billing release.

### Test Scenarios

**Test 1: Third-Party Order → Vendor Invoice → Customer Billing**

1. Create sales order: VA01, order type OR, enter material with MVKE-MTPOS = BANS. Item category should auto-determine to TAS. Verify schedule line category = CS (or CB). Save the order and check that a PR was automatically created — use ME53N, filter by reference (sales order number and item).
2. Convert PR to PO: ME21N, reference the PR. Verify delivery address on the PO item is the customer's ship-to address (not the company's plant address). PO item category must be blank (stock material) or specifically set for third-party.
3. Post vendor invoice: MIRO, reference the PO. If CS schedule line (no GR required), MIRO should post without requiring a GR reference. FI posting: Dr Purchase Account (no inventory) / Cr Vendor. Verify no inventory movement occurs in MB52 — company stock does not change.
4. Create customer billing: VF04, filter for billing due list. The third-party sales order should appear (billing relevance B creates billing duedate from order). Create billing document. Verify FI: Dr Customer / Cr Revenue.

**Test 2: Statistical GR Scenario (CB Schedule Line)**

1. Follow Test 1 steps 1-2 with schedule line category CB.
2. Post statistical GR: MIGO, Action = Goods Receipt, reference = third-party PO. Movement type = statistical (non-valuated). Verify no FI accounting document is created — statistical GR only updates quantities, not values.
3. Verify billing is now unblocked: VF04 should show the order as billable only after the statistical GR is posted. Without the GR, billing will be blocked.

**Test 3: Margin Analysis**

1. After completing Test 1, verify the margin:
   - Vendor cost: FBL1N — vendor open item = MIRO amount
   - Customer revenue: FBL5N — customer open item = billing amount
   - Gross margin = Revenue − Vendor cost
2. If CO-PA is configured, run KE24 to see the profitability segment for the third-party sales order — both revenue and the purchase cost should post to CO-PA.

### Cross-Module Perspective

**FI Account Assignment:**
- At vendor invoice (MIRO): Dr Third-Party Cost (no GR/IR clearing because no goods receipt in own warehouse) / Cr Vendor
- At customer billing (VF01, VTAF): Dr Customer (VKOA ERL) / Cr Revenue
- No COGS inventory posting occurs — there is no movement type 601 in third-party processing

**CO Account Assignment:**
- If account assignment category C (sales order) is used on the PO, the vendor cost posts directly to the CO-PA profitability segment of the sales order.
- This enables full margin visibility in CO-PA: revenue from VF01 billing vs. vendor cost from MIRO posting.

**No Inventory Impact:**
- MB52 does NOT change for third-party materials. The company's warehouse stock is unaffected.
- The FI balance sheet does NOT show inventory for third-party goods — they flow through the P&L directly (vendor expense matched against customer revenue).

**Integration Cross-References:**
- Third-party flow overview: `cross-module/mm-sd-integration.md` Section Third-Party Processing
- SD process summary: `modules/sd/processes.md` Section 7
- CO-PA account assignment: `modules/co/co-advanced.md`

### Common Pitfalls

- **Billing blocked — no billing relevance:** If TAS item category billing relevance is not set to B, the order never becomes billable. Check VOV7 for TAS item category configuration.
- **PR not created automatically:** If the schedule line category is not configured to create PRs (purchasing indicator must be active on the schedule line category in VOV6), no PR is generated at order save. The buyer must manually create the PO.
- **Statistical GR not posted (CB scenario):** With schedule line category CB, billing is blocked until a statistical GR is posted. This is often overlooked in testing — testers post MIRO and wonder why VF04 does not show the order as billable.
- **Wrong delivery address on PO:** If the delivery address on the third-party PO shows the company's plant address (not the customer's ship-to), the vendor ships to the wrong location. Verify that the PR-to-PO conversion correctly carries over the ship-to address from the sales order.
- **Account determination error at billing:** Third-party billing uses VTAF (order-to-billing) copy control. If VTAF is missing for the document type combination, billing fails. Verify VTAF for OR → F2 with TAS item category.

---

## Playbook 4: Subcontracting (Toll Processing)

> Subcontracting (toll processing) transfers company-owned components to an external vendor for processing, then receives finished goods back — using movement type 541 to send components (no FI posting) and automatic movement type 543 at goods receipt to consume components, with the subcontracting fee as the only external cost.

### Business Context

Subcontracting is used when the company has the raw materials but lacks the manufacturing capability or capacity to transform them. The vendor (subcontractor) performs the processing and returns the finished goods. Key characteristics:

- **Components remain company property:** Movement type 541 reclassifies components from unrestricted to subcontracting stock (special stock O) — no transfer of ownership to the vendor, no FI posting.
- **Vendor only charges for processing:** The subcontracting PO price represents the processing fee only, not the value of components.
- **Automatic component consumption:** When finished goods are received (MIGO against subcontracting PO), movement type 543 fires automatically to consume the components from subcontracting stock (special stock O) and posts GBB/VBO in FI.

### Prerequisites

- Subcontracting BOM: bill of materials (CS01/CS11) defining which components are needed per finished good
- Subcontracting purchase info record (ME11, info category = Subcontracting) with the processing fee
- Special procurement key MARC-SOBSL = 30 on the finished goods material master (MRP 2 view) — required for MRP to generate subcontracting PRs
- OBYC GBB/VBO configured for the component materials' valuation classes (subcontracting consumption account)

### Configuration Walkthrough

#### Step 1: MM — Subcontracting BOM (CS01)

**T-code:** CS01 (Create BOM) or CS11 (Display Multi-Level BOM)
**SPRO Path:** No SPRO path — master data transaction
**Settings:** Create a production BOM for the finished goods material with BOM usage = 1 (Production). List all components with required quantities per base quantity of finished goods. The BOM must exist at the plant level.

The subcontracting BOM drives:
- Which components are suggested on the subcontracting PO
- Which components are automatically consumed (543) at finished goods receipt

**Gotcha:** The BOM must be created with usage = 1 (Production) or usage = 5 (Subcontracting, if applicable). A PM or plant maintenance BOM (usage 4) will NOT be found by the subcontracting PO. If the BOM is missing, the component list on the PO will be empty and movement 543 will not fire.

#### Step 2: MM — Special Procurement Key MARC-SOBSL = 30

**T-code:** MM02 (Change Material Master)
**View:** MRP 2 (Procurement tab)
**Settings:** Field MARC-SOBSL = 30 (Subcontracting). This tells MRP that the finished goods material must be procured externally via subcontracting (not produced in-house and not standard purchase). When MRP calculates net requirements, it generates subcontracting PRs (not standard POs or planned orders).

**Gotcha:** If MARC-SOBSL is blank but MARC-BESKZ = E (external procurement), MRP generates standard purchase PRs — not subcontracting PRs. The buyer then creates a wrong PO type. Set SOBSL = 30 to ensure subcontracting PRs are generated.

See `modules/mm/mm-advanced.md` Decision Tree 9 for the complete special stock type reference.

#### Step 3: MM — Subcontracting Purchase Info Record

**T-code:** ME11
**Settings:** Info record category = Subcontracting. Vendor = subcontractor; material = finished goods; purchasing org; plant; processing fee price per finished goods unit. This is the price the subcontractor charges for the processing service only (not the component value).

The info record is linked to the BOM: the system reads the BOM to populate the component list on the subcontracting PO.

#### Step 4: FI — OBYC GBB/VBO Configuration

**T-code:** OBYC
**Transaction key:** GBB with modifier VBO (subcontracting consumption)
**Settings:** Configure GBB/VBO → GL account (subcontracting consumption expense) for each valuation class of the component materials.
**Gotcha:** Movement type 543 (automatic component consumption at subcontracting GR) fires GBB/VBO. If GBB/VBO is not configured for the component's valuation class, the GR will fail with an account determination error. The error message shows the missing OBYC entry.

See `modules/mm/mm-advanced.md` Section 1a for the GBB modifier reference including VBO.

#### Step 5: MM — Subcontracting PO Creation

**T-code:** ME21N
**Settings:** Document type NB; item category L (Subcontracting). Enter the subcontractor as vendor, finished goods as material, quantity, and price (processing fee). The system automatically proposes the component list from the BOM and the subcontracting info record. Verify component quantities and materials are correct.

**Gotcha:** Item category must be L (Subcontracting), not blank (standard). A standard PO for subcontracting materials will not trigger the 541/543 component handling.

### Master Data Setup

| Object | Configuration | T-code |
|--------|--------------|--------|
| Finished goods material master | MARC-SOBSL = 30 (MRP 2 view); MARC-BESKZ = E or X | MM01/MM02 |
| Component material master | Standard material; MARC-XCHPF may be set if batch-tracked | MM01/MM02 |
| Subcontracting BOM | FG material → component list with quantities | CS01 |
| Subcontracting info record | Vendor + FG material + processing fee | ME11 (info category = Subcontracting) |
| Subcontracting PO | Item category L; component list from BOM | ME21N |

### Process Flow

| Step | Activity | T-code | Movement Type | FI Posting |
|------|----------|--------|---------------|------------|
| 1 | MRP generates subcontracting PR | MD01/MD02 | — | None |
| 2 | Buyer creates subcontracting PO (item category L) | ME21N | — | None |
| 3 | Transfer components to subcontractor | MIGO | 541 | **NONE** — stock reclassification only (unrestricted → special stock O) |
| 4 | Verify components at subcontractor | MB52/MMBE | — | None; special stock O visible |
| 5 | Subcontractor returns finished goods | — | — | None |
| 6 | Post GR of finished goods against subcontracting PO | MIGO (101) | 101 + 543 (auto) | 101: Dr Inventory (BSX) + Cr GR/IR (WRX) for processing fee; 543 (auto): Dr Subcontracting Consumption (GBB/VBO) + Cr Component Inventory (BSX) |
| 7 | Post vendor invoice for processing fee | MIRO | — | Standard Dr GR/IR (WRX) / Cr Vendor |

> **541 has NO FI posting.** This is the most commonly misunderstood aspect of subcontracting. Movement 541 is a stock type change only — the components remain on the company's balance sheet as subcontracting stock (special stock O). The accounting event for component consumption occurs at GR via automatic movement 543.

### Test Scenarios

**Test 1: Component Transfer and Goods Receipt Verification**

1. Create subcontracting PO: ME21N, item category L, enter subcontractor as vendor, finished goods as material, processing fee price. Verify component list is populated from BOM. Check component quantities match BOM.
2. Transfer components to subcontractor: MIGO, movement type 541, reference the subcontracting PO. After posting, verify in MB52: component material should show in "Subcontracting" stock column (special stock O) for the subcontractor. Verify NO FI accounting document was created (check the material document — no FI document number should be linked).
3. Post finished goods receipt: MIGO, Action = Goods Receipt, reference = subcontracting PO. Movement type 101 fires automatically. Check the document — movement type 543 should also appear as an automatic sub-item consuming the components from special stock O.
4. Verify FI postings: Check the FI document linked to the MIGO 101. You should see: Dr Inventory (BSX, FG valuation class) / Cr GR/IR (WRX, at processing fee price) for the 101 posting; AND Dr Subcontracting Consumption (GBB/VBO, component valuation class) / Cr Component Inventory (BSX, component valuation class) for the automatic 543.
5. Run MB52: component quantity should now show zero in subcontracting stock (consumed by 543).

**Test 2: MRP-Driven Subcontracting**

1. Set MARC-SOBSL = 30 on the finished goods material master (MRP 2 view). Create a planned independent requirement (MD61) for the finished goods. Run MRP (MD01 or MD02). Check MRP results in MD04 — the system should have generated a subcontracting PR (procurement type = subcontracting), not a standard purchase PR.
2. Convert the subcontracting PR to PO: ME21N. Verify item category L is proposed.

**Test 3: CO Perspective — Cost Settlement**

1. After Test 1, check if a production order or internal order is involved (for make-to-order scenarios, a production order may be the receiver for the subcontracting cost).
2. If the subcontracting PO has account assignment = F (production order), the processing fee (from MIRO) and component consumption (from 543) both post to the production order. Run KO88 (internal order settlement) or CO88 (production order settlement) after the period. Verify actual costs settle to the product cost collector or cost center.
3. For standard make-to-stock subcontracting without order: the costs go directly to inventory (BSX) at standard cost, and variances (if standard price differs from actual) post to PRD.

### Cross-Module Perspective

**FI Account Flow:**
- Movement 541 (components to subcontractor): No FI posting. Balance sheet unchanged — components remain as subcontracting stock (special stock O) at plant level.
- Movement 101 (FG receipt): Dr FG Inventory (BSX) / Cr GR/IR Clearing (WRX) — at processing fee price. This reflects only the vendor's service charge.
- Movement 543 (automatic component consumption): Dr Subcontracting Consumption (GBB/VBO) / Cr Component Inventory (BSX) — at component standard or moving average price. This is the material cost of the finished goods.
- The full cost of the finished goods = processing fee (from 101 via WRX/MIRO) + component cost (from automatic 543 via GBB/VBO).

**CO Account Assignment:**
- For make-to-stock subcontracting: costs flow into inventory valuation. CO variance analysis (KKS2/KKBC_PKO) shows the difference between standard subcontracting cost and actual.
- For make-to-order or project-based: account assignment category on the PO routes costs to the production order (F) or WBS element (P). KO88/CJ88 settlement then moves these costs to the cost object receivers.

**Integration Cross-References:**
- Movement type 541 (no FI) and 543 (GBB/VBO): `modules/mm/mm-advanced.md` Section 1b
- Subcontracting overview: `cross-module/mm-sd-integration.md` Section Subcontracting
- Decision Tree 9 (special stock types): `modules/mm/mm-advanced.md`

### Common Pitfalls

- **541 does not appear in FBL3N:** Expected — movement 541 has no FI posting. Consultants checking the accounting document see nothing and think the posting failed. Check the material document (MB51) instead — 541 is a material document only.
- **543 not firing at GR:** If the BOM is missing or contains no components, or if the subcontracting PO has no component list, movement 543 will not fire. The FG inventory increases but components are not consumed — stock in special O remains. Check that item category L is used on the PO and BOM is correct.
- **GBB/VBO not configured:** The 543 posting fails with an account determination error. Run OMWB simulation for the component material to verify GBB/VBO is configured. Add missing OBYC entry for GBB/VBO + component valuation class.
- **Wrong item category on PO:** Using item category blank (standard) instead of L (subcontracting) means no component list, no 541, and no 543. The GR posts as a standard PO receipt (101 only) with no component handling.
- **Component shortage:** If components are insufficient for the subcontracting GR quantity, the 543 posting may partially consume or fail. Pre-check component availability (MD04 or MB52 for special stock O) before posting GR.

---

## Configuration Playbooks

---

## Playbook 5: Split Valuation

> Split valuation allows the same material number to be valued at different prices based on a differentiating characteristic (origin, quality grade, procurement type), with each valuation type maintaining separate stock quantities, prices, and optionally separate GL accounts in OBYC.

### Business Context

Standard valuation assigns one price to a material at a plant — either a single standard price or a single moving average price. Split valuation is required when the business needs to track the same material with different economic values:

- **Origin:** Domestic steel (lower duty) vs. imported steel (higher duty + freight)
- **Quality grade:** Grade A material vs. Grade B material (different selling prices/costs)
- **Procurement type:** In-house produced (standard cost) vs. externally purchased (market price)

Split valuation is configured per material per plant and requires activation at two levels: the global level (OMWC defines which valuation categories exist) and the material master level (the material is flagged for split valuation with the active valuation category).

### Prerequisites

- Valuation level = plant (OMWM must be set to plant-level valuation — CRITICAL, cannot change after first posting)
- OMWC global split valuation categories defined before material master setup
- OMSK account category references configured for each valuation type (required for separate GL accounts)
- OBYC BSX and WRX entries for each new valuation class used by the split valuation types

### Configuration Walkthrough

#### Step 1: MM — Activate Global Split Valuation (OMWC)

**T-code:** OMWC
**SPRO Path:** Materials Management → Valuation and Account Assignment → Split Valuation → Configure Split Valuation
**Settings in OMWC:**

1. **Global settings:** Activate split valuation globally (checkbox "Active Split Valuation")
2. **Valuation categories:** Define the characteristic that differentiates stock types. Standard SAP provides:
   - **Origin (H):** Domestic vs. imported
   - **Procurement type (B):** In-house vs. external
   - **Status (S):** New vs. repaired
   - Custom categories can be defined (e.g., "Q" for quality grade)
3. **Valuation types per category:** For category "H" (origin), define types: "Domestic" and "Imported". Each type gets its own price, stock quantity, and optionally its own valuation class.

**Gotcha:** OMWC has TWO levels: global level (what categories exist) and plant level (which categories are active in which plants). Define at global level first, then assign to plants. If a valuation category is defined globally but not assigned to a specific plant, it cannot be used in that plant.

#### Step 2: MM — Valuation Class per Valuation Type (OMSK)

**T-code:** OMSK
**Settings:** For each split valuation type that needs separate GL accounts, assign a distinct valuation class. This enables OBYC to post inventory movements to different GL accounts depending on the valuation type:

- Domestic stock (type "Domestic") → valuation class 3000 → OBYC BSX → GL 140000
- Imported stock (type "Imported") → valuation class 3010 → OBYC BSX → GL 140100

If separate GL accounts are NOT required (only separate pricing), all valuation types can share the same valuation class.

**Gotcha:** If the valuation class for the new valuation type is not assigned in OMSK and not configured in OBYC (BSX, WRX), every goods movement for that valuation type will fail with an account determination error.

#### Step 3: MM — Material Master — Activate Split Valuation

**T-code:** MM02 (Change Material Master) → Accounting 1 view
**Settings:** On the Accounting 1 view (MBEW), activate split valuation for the material:
- Set "Split Valuation" indicator to X
- Select the valuation category (e.g., "H" for origin)

After activation, a sub-ledger of MBEW is created: one MBEW record per valuation type (MBEW-BWTAR = valuation type). Each type has its own price, stock value, and quantity.

**Gotcha:** Split valuation can only be activated on a material with zero stock. If the material has stock, you must post it out (to a cost center or scrap) before activating split valuation, then re-receive into the correct valuation types. Plan activation carefully — it cannot be done in production without a stock-out.

#### Step 4: OBYC — Separate GL Accounts per Valuation Type

**T-code:** OBYC
**Settings:** For each new valuation class created in Step 2:
- **BSX:** Configure inventory GL account for the new valuation class
- **WRX:** Configure GR/IR clearing GL account (if same as standard, no action needed — WRX typically uses the same clearing account regardless of valuation type)
- **PRD:** Configure price difference account (if standard price is used)

The result: goods movements for "Domestic" stock post to GL 140000 (domestic inventory), while "Imported" stock movements post to GL 140100 (imported inventory). The chart of accounts distinguishes the stock by origin on the balance sheet.

#### Step 5: Production Order Integration

**For materials used in production orders (PP integration):**
- The production order component issue (movement 261) must specify the valuation type to determine which valuation type's stock is consumed.
- The finished goods receipt (movement 101 for production orders) also requires a valuation type — the standard valuation type for in-house production is typically "F" (In-House) or a custom type.
- If MRP is active, the planned order's procurement type drives which valuation type is used.

### Master Data Setup

| Object | Configuration | T-code |
|--------|--------------|--------|
| Global split valuation | Activate + define categories + types in OMWC | OMWC |
| Valuation class per type | OMSK: account category ref for each valuation type | OMSK |
| Material master | Accounting 1 view: activate split valuation; select category | MM02 |
| OBYC accounts | BSX, WRX, PRD per new valuation class | OBYC |
| Info records (if separate pricing) | ME11: one info record per vendor + material with valuation type in the info record | ME11 |

### Process Flow

| Step | Activity | T-code | Valuation Type Required? | Notes |
|------|----------|--------|--------------------------|-------|
| 1 | Create PO for imported material | ME21N | No — specified at GR | PO is for the material; valuation type entered at MIGO |
| 2 | Post GR of imported material | MIGO | Yes — "Imported" type | System creates MBEW record for "Imported" type; BSX posts to GL 140100 |
| 3 | Post GR of domestic material | MIGO | Yes — "Domestic" type | System creates MBEW record for "Domestic" type; BSX posts to GL 140000 |
| 4 | Issue component (261) | MIGO | Yes — specify which type | GI reduces the specified valuation type's stock only |
| 5 | Transfer between valuation types | MIGO or MB1B | Specify source and target | Use split valuation transfer posting to reclassify stock between types |
| 6 | Report by valuation type | MB52 | — | MB52 shows stock per valuation type separately |

### Test Scenarios

**Test 1: Separate GL Account Verification**

1. Activate split valuation for a test material (e.g., STEEL-001) with valuation category H (Origin). Define types: Domestic (valuation class 3000) and Imported (valuation class 3010). Configure OBYC BSX: 3000 → GL 140000; 3010 → GL 140100.
2. Post GR of 100 units — "Imported" type: MIGO, movement 101, enter valuation type = Imported. Check the FI document — BSX should post to GL 140100 (Imported inventory), WRX to the standard GR/IR account.
3. Post GR of 100 units — "Domestic" type: MIGO, movement 101, valuation type = Domestic. Check FI document — BSX should post to GL 140000 (Domestic inventory).
4. Run FBL3N for GL 140000 and 140100: verify each account shows only the correct valuation type's receipts.
5. Run MB52 for STEEL-001: verify 100 units Imported and 100 units Domestic shown separately with their respective prices.

**Test 2: Material Ledger Interaction (If ML Active)**

1. Run CKMLCP after the test period. Verify that split valuation types are each costed independently by Material Ledger — actual costs are calculated separately per valuation type.
2. The ML actual cost closing (CKMLCP) creates separate adjustment postings for each valuation type. The imported stock and domestic stock have independent actual cost layers.

**Test 3: Production Order Component Consumption**

1. Create a production order for a finished good that uses STEEL-001 as a component. Issue components to the production order (movement 261): MIGO, specify valuation type = Imported.
2. Verify the GI reduces only the Imported stock quantity. GL 140100 (Imported Inventory) is credited. Run KKS2 or production order report to see the actual component cost.

### Cross-Module Perspective

**FI Account Determination:**
- Each valuation type maps to its own MBEW record (MBEW-BWTAR = valuation type)
- BSX posts to the GL account determined by the valuation type's valuation class — enabling balance sheet differentiation by origin or quality
- WRX typically uses the same clearing account for all valuation types (unless separate clearing accounts are needed per origin)

**CO Perspective:**
- Cost center and internal order consumption (movement 261/201) uses the price from the specific valuation type's MBEW record — if "Imported" steel costs more than "Domestic," the cost difference is visible in CO cost center reports.
- Product costing (CK11N) with split valuation: the costing run values components at the "standard" valuation type's price. Separate costing runs for different procurement scenarios may be needed.

**Material Ledger Interaction:**
- If Material Ledger is active (optional in ECC 6, mandatory in S/4HANA), each valuation type is costed independently. The ML actual cost run (CKMLCP) calculates separate actual costs for Domestic and Imported stock.
- Reporting via CKMLMV (Material Ledger documents) shows the actual vs. standard cost by valuation type.

**Integration Cross-References:**
- Split valuation OMWC config chain: `modules/mm/mm-advanced.md` Decision Tree 6
- Valuation class setup chain: `modules/mm/mm-advanced.md` Section 1c
- OMWC Example 6 (split valuation FI posting): `modules/mm/mm-advanced.md` Example 6

### Common Pitfalls

- **Activation on non-zero stock:** Attempting to activate split valuation when the material has existing stock causes an error. The material must have zero stock first. Plan activation as a cutover activity.
- **Missing valuation type at GR:** If no valuation type is specified during goods receipt, SAP uses the default valuation type (if configured) or rejects the posting. Train users to always specify the valuation type for split-valuated materials.
- **OBYC missing for new valuation class:** Adding a new valuation type (e.g., "Grade C") with a new valuation class without updating OBYC causes account determination errors on all GRs for that type. Always update OBYC BSX and WRX when adding new valuation types.
- **Cannot aggregate stock reports:** MB52 shows separate lines per valuation type. Some managers expect a single stock line. This is expected behavior — split valuation intentionally segments the stock.

---

## Playbook 6: Special Procurement Keys

> Special procurement keys (MARC-SOBSL) tell MRP how to generate procurement elements for a material — enabling subcontracting, phantom assemblies, plant-to-plant transfer, and other non-standard procurement patterns without manual buyer intervention.

### Business Context

MRP normally generates either a planned order (for in-house production) or a purchase requisition (for external procurement) based on the procurement type (MARC-BESKZ). Special procurement keys extend this logic with 5 standard SAP codes that generate more specialized procurement elements:

| Code | Description | MRP Generates |
|------|-------------|---------------|
| 10 | Production in another plant | Stock transfer PR/planned order from supplying plant |
| 20 | Phantom assembly | BOM exploded but no procurement element created |
| 30 | Subcontracting | Subcontracting PR |
| 40 | Stock transfer from another plant | STO (stock transfer order) |
| 50 | WM-managed (not standard SAP special procurement) | Varies |

### Prerequisites

- Material master MRP 2 view (MARC-SOBSL) must be set before running MRP
- For code 10/40: source plant (supplying plant) must be configured in the material's MRP special procurement settings (MARC-SPEME = supplying plant)
- For code 30: subcontracting BOM and info record required (see Playbook 4)
- For code 20: phantom assembly BOM must exist with usage that MRP recognizes as phantom

### Configuration Walkthrough

#### Step 1: Material Master — Set Special Procurement Key

**T-code:** MM02
**View:** MRP 2 (Procurement tab)
**Settings:** Field MARC-SOBSL — enter the special procurement key:
- 30 = Subcontracting (most common for this playbook — see Playbook 4 for full detail)
- 10 = Production in another plant (MRP creates a planned order or PR for the supplying plant)
- 40 = Stock transfer from another plant (MRP creates an STO PR)
- 20 = Phantom assembly (BOM is exploded for dependent requirements but the phantom itself is not procured)

**For codes 10 and 40 — also set the supplying plant:**
Field MARC-SPEME = supplying plant number (e.g., Plant 1000 supplies Plant 2000).

#### Step 2: Special Procurement Key 10 — Production in Another Plant

**SPRO Path (configuration):** Production → Material Requirements Planning → Master Data → Define Special Procurement Types
**Settings:** Key 10 tells MRP that when Plant 2000 needs the material, it should be produced in Plant 1000. MRP creates a planned order in Plant 1000 for the required quantity. A stock transport order (or direct plant transfer) then moves the goods to Plant 2000.

**Account assignment:** Planned order in Plant 1000 → Production costs post to Plant 1000's cost center or product cost collector → transfer to Plant 2000 at standard price (cross-plant transfer).

#### Step 3: Special Procurement Key 20 — Phantom Assembly

**SPRO Path (configuration):** Production → Material Requirements Planning → Master Data → Define Special Procurement Types
**Settings:** A phantom assembly is a virtual BOM grouping that is not physically produced or procured as a standalone item. MRP explodes the BOM of the phantom to generate requirements for the phantom's components, but no planned order or PR is created for the phantom itself.

Use cases: Modular BOM design where subassemblies are logical groupings only; assembly-line feeding scenarios where components are picked individually rather than as a pre-assembled kit.

#### Step 4: Special Procurement Key 40 — Stock Transfer from Another Plant

**SPRO Path:** Same IMG node as key 10
**Settings:** Key 40 generates a stock transport order PR (STO PR) when the receiving plant needs material. The PR references the supplying plant (MARC-SPEME). The buyer converts the STO PR to a stock transport order PO (ME21N, document type UB).

MRP in the supplying plant (Plant 1000) also runs and creates a corresponding planned order or purchase PR to ensure Plant 1000 has enough stock to fulfill the transfer.

**Account assignment for STO:** Two-step STO — movement type 641 (goods issue at Plant 1000) → in-transit stock → movement type 101 (GR at Plant 2000). FI posts at each step: BSX credits Plant 1000 inventory, BSX debits Plant 2000 inventory. See `cross-module/mm-sd-integration.md` Stock Transport Orders for full STO flow.

### Master Data Setup

| Object | Configuration | T-code |
|--------|--------------|--------|
| Material master (receiving plant) | MARC-SOBSL + MARC-SPEME (supplying plant for codes 10/40) | MM02 (MRP 2 view) |
| Material master (supplying plant) | Standard procurement type — must have stock or production plan | MM02 |
| Subcontracting BOM (code 30) | BOM for the finished goods material | CS01 |
| Subcontracting info record (code 30) | Vendor + FG material + processing fee | ME11 |
| STO configuration (code 40) | Receiving plant → supplying plant STO setup | SPRO (MM → STO config) |

### Process Flow — Special Procurement Key 40 (STO)

| Step | Activity | T-code | Notes |
|------|----------|--------|-------|
| 1 | MRP run in receiving plant | MD01/MD02 | Generates STO PR for the receiving plant |
| 2 | Convert STO PR to STO PO | ME21N (type UB) | Document type UB = stock transport order |
| 3 | Goods issue at supplying plant | VL02N or MIGO | Movement type 641; stock moves to in-transit |
| 4 | Goods receipt at receiving plant | MIGO | Movement type 101 against the STO PO |
| 5 | Verify stock transfer | MMBE | Stock in-transit visible between steps 3 and 4 |

### Test Scenarios

**Test 1: Special Procurement Key 30 (Subcontracting) — MRP Generation**

1. Set MARC-SOBSL = 30 on the finished goods material (MRP 2 view). Create a demand (MD61 planned independent requirement or sales order). Run MRP (MD01/MD02 or MD03 for single material). Check MD04 — the MRP element should be a subcontracting PR (with subcontracting indication), NOT a standard purchase PR.
2. Convert the subcontracting PR to PO (ME21N, item category L). Verify item category L is proposed. Continue with the full subcontracting flow from Playbook 4.

**Test 2: Special Procurement Key 40 (STO) — Cross-Plant Transfer**

1. Set MARC-SOBSL = 40 and MARC-SPEME = Plant 1000 on the material master for Plant 2000. Create demand for Plant 2000 (MD61 or sales order for Plant 2000). Run MRP for Plant 2000. Check MD04 for Plant 2000 — MRP should generate an STO PR referencing Plant 1000 as the supplying plant.
2. Convert STO PR to STO PO (ME21N, document type UB). Verify the STO PO references Plant 1000 as the supplying plant and Plant 2000 as the receiving plant.
3. Post GI from Plant 1000: MIGO, movement 641. Check MMBE — stock shows in-transit. Post GR at Plant 2000: MIGO, movement 101. Verify Plant 2000 stock increases and in-transit clears.

**Test 3: Special Procurement Key 20 (Phantom Assembly)**

1. Set MARC-SOBSL = 20 on a phantom assembly material. Create a BOM for the phantom with its components. Create demand for a higher-level FG that includes the phantom in its BOM. Run MRP. Check MD04: the phantom assembly itself should have NO planned orders or PRs. Its components should have requirements from the BOM explosion.
2. Confirm that no procurement element was created for the phantom material itself — only its components appear in MRP requirements.

### Cross-Module Perspective

**FI Posting by Key:**
- Key 20 (phantom): No FI posting — phantom has no physical movement
- Key 30 (subcontracting): 541 (no FI), 101 (BSX/WRX for processing fee), 543 (GBB/VBO for components)
- Key 40 (STO): Movement 641 at supplying plant (BSX Cr), in-transit, 101 at receiving plant (BSX Dr) — two FI postings in two plants

**CO Perspective:**
- Key 40 (STO within one CC): Internal transfer at standard price; no intercompany posting. CO cost remains within the same controlling area — no reconciliation posting.
- Key 40 (STO cross-CC): Intercompany FI postings required (see `cross-module/mm-sd-integration.md`). CO reconciliation ledger may fire if the controlling area spans both company codes.
- Key 30 (subcontracting): See Playbook 4 CO section.

**Integration Cross-References:**
- Special stock types and procurement keys: `modules/mm/mm-advanced.md` Decision Tree 9
- STO mechanics: `cross-module/mm-sd-integration.md` Section Stock Transport Orders
- MRP type selection: `modules/mm/mm-advanced.md` Decision Tree 10

### Common Pitfalls

- **Wrong procurement element generated:** If MARC-SOBSL is set but MARC-BESKZ is wrong (e.g., BESKZ = F for in-house production but SOBSL = 30 for subcontracting), MRP may generate the wrong element type. MARC-BESKZ must be E (external) or X (both) for keys 30 and 40.
- **Missing supplying plant (codes 10/40):** If MARC-SPEME is blank for keys 10 or 40, MRP cannot generate the STO PR — it falls back to standard procurement. Always set MARC-SPEME when using keys 10/40.
- **Phantom assembly still receives planned orders:** If the BOM usage is wrong or MRP planning parameters on the phantom material are not correctly configured, MRP may create planned orders for the phantom. Verify BOM usage = 1 and phantom indicator is active.

---

## Playbook 7: Batch Management

> Batch management enables individual lot (batch) tracking for materials, supporting product traceability, shelf life management, quality control, and FIFO/FEFO picking in deliveries — with batch characteristics (classification) enabling powerful search strategies and regulatory compliance.

### Business Context

Batch management is required when materials must be tracked as individual lots: pharmaceuticals (FDA traceability), food products (FEFO rotation, allergen management), chemicals (certificate of analysis per batch), and industrial materials (quality grade per heat number). Each batch has its own:

- Stock quantity (separate from other batches)
- Characteristics (production date, expiry date, quality attributes via classification)
- Status (unrestricted, quality inspection, blocked)
- Price (if batch-specific valuation is active)

### Prerequisites

- Batch management activated at the correct level (client/plant/material — OMAD)
- Batch master (MSC1N) with relevant characteristics assigned
- Classification class (CT04) and characteristics (CT04) defined for batch attributes
- Shelf life management fields on material master if FEFO is required (MARC-MHDRP, MARC-MHDHB)

### Configuration Walkthrough

#### Step 1: MM — Batch Level Configuration (OMAD)

**T-code:** OMAD
**SPRO Path:** Logistics — General → Batch Management → Specify Batch Level and Activate Status Management
**Settings:** Batch uniqueness level:
- **Client level:** Batch number unique across all plants and materials (one batch = one object across the system)
- **Plant level:** Batch unique per material per plant (same batch number can exist in two plants for different materials)
- **Material level (default):** Batch unique per material (same batch number can exist for different materials at any plant)

**Gotcha:** Batch level CANNOT be changed after the first batch is created in the system. This is a go-live decision. Client-level batches are required for pharmaceutical traceability and regulatory scenarios. Plant-level is most common in manufacturing.

#### Step 2: MM — Batch Management Per Plant/Material (MARC-XCHPF)

**T-code:** MM02 (Material Master, Plant Data/Storage 1 view)
**Settings:** Field MARC-XCHPF = X activates batch management for this material at this plant. Without this flag, goods movements for the material do not require a batch number.

Alternatively, batch management can be activated by material type (SPRO → Logistics General → Batch Management → Define Batch Management per Material Type) — all materials of that type automatically require batches.

#### Step 3: MM — Classification: Characteristics (CT04) and Class (CL02)

**T-code:** CT04 (Create Characteristic), CL02 (Create Class)
**Settings:**
- Create characteristics for batch attributes: PROD_DATE (date), EXPIRY_DATE (date), QUALITY_GRADE (character string), LAB_RESULT (numeric with UoM)
- Create a class with class type 023 (Batch Class): CL02, assign the characteristics to the class
- Assign the class to the material via classification view in material master (MM02) or batch master

This classification data enables batch search strategies and FEFO sorting.

#### Step 4: MM — Shelf Life Management

**T-code:** MM02
**View:** Plant Data / Storage 1 (MARC) and Plant Data / Storage 2 (MARC)
**Settings:** For materials with expiry dates:
- MARC-MHDRP: Remaining shelf life (days required remaining at GR — GR is rejected if batch has less than MHDRP days remaining)
- MARC-MHDHB: Total shelf life (maximum days from production to expiry)
- MARC-IPRKZ: Batches are automatically expired when expiry date passes

After setting shelf life fields, the batch master must record the production date (from which the expiry date is calculated). T-code MM17 can update MHDRST (minimum remaining shelf life) for multiple materials at once.

#### Step 5: SD — Batch Search Strategies for Delivery (LS11/LS12)

**T-code:** LS11 (Define Strategy), LS12 (Search Strategy Assignment), MBC1 (Batch Search Strategy Records)
**SPRO Path:** Logistics — General → Batch Management → Batch Determination and Batch Check → Batch Search Strategy for Delivery
**Settings:**
- Define a search strategy type (e.g., FEFO = First Expiry First Out)
- The strategy specifies sort criteria for batches: earliest expiry date first
- Assign the strategy to the delivery movement type and plant
- Create batch search strategy condition records (MBC1): which strategy applies for which customer or material combination

**Gotcha:** Batch determination in SD uses the condition technique. Without MBC1 condition records, no strategy is assigned at delivery creation and the system picks any available batch (not necessarily FEFO). Always verify MBC1 records for the correct sales area and material combination.

#### Step 6: MM — Batch Determination in Goods Issue

For MM goods issues (movement 261, 601), batch determination can be activated via SPRO:
SPRO → Materials Management → Inventory Management → Goods Issue/Transfer Postings → Batch Classification

For complex MIGO batch finding, configure automatic batch determination using similar condition technique records as SD.

### Master Data Setup

| Object | Configuration | T-code |
|--------|--------------|--------|
| Characteristic (attribute) | Name, data type, value range | CT04 |
| Class (batch class) | Class type 023; assign characteristics | CL02 |
| Material master | MARC-XCHPF = X (batch managed); shelf life fields; classification view with batch class | MM01/MM02 |
| Batch master | Batch number, material, plant; characteristic values (production date, expiry, quality) | MSC1N |
| Batch search strategy records | Strategy + plant + material → search rule (FEFO, FIFO, etc.) | MBC1 |

### Process Flow

| Step | Activity | T-code | Batch Handling |
|------|----------|--------|----------------|
| 1 | GR of batch-managed material | MIGO | Enter batch number at GR (new batch if first receipt of lot). Enter production/expiry date on batch master. |
| 2 | Batch master maintenance | MSC1N | Record characteristics: quality grade, lab result, production date. This is classification data used in batch determination. |
| 3 | QM inspection (if applicable) | QA32 | Change batch status from "Quality Inspection" to "Unrestricted" after inspection passes |
| 4 | Create delivery for batch material | VL01N | Batch determination runs at delivery item level — system proposes batch based on strategy (FEFO, FIFO) |
| 5 | Confirm/override batch in delivery | VL02N | Picker can confirm proposed batch or override. Batch split: multiple batches can fill one delivery item (partial quantities from multiple batches) |
| 6 | Post goods issue | VL02N | Movement 601: only the specified batch's stock is reduced |
| 7 | Batch where-used traceability | VLBR, MB56 | VLBR shows all deliveries using a batch; MB56 shows batch usage in material documents |

### Test Scenarios

**Test 1: FEFO Batch Determination in Delivery**

1. Create batch master for material PHARMA-001 at Plant 1000: MSC1N. Enter batch "BATCH001," assign production date 01.01.2026, and expiry date 01.07.2026. Create another batch "BATCH002" with production date 01.02.2026 and expiry date 01.09.2026. Both batches should have stock in unrestricted.
2. Configure FEFO batch search strategy: LS11, define strategy type "FEFO" with sort criterion = expiry date ascending. Assign via MBC1 to Plant 1000 + material PHARMA-001.
3. Create sales order (VA01) and delivery (VL01N) for PHARMA-001. In VL02N, batch determination should automatically propose BATCH001 (earlier expiry date, FEFO = first expiry first out).
4. Verify by changing the proposed batch to BATCH002 and observe the system warning (if configured) or note that override is possible.

**Test 2: Shelf Life Check at Goods Receipt**

1. Set MARC-MHDRP = 30 (minimum 30 days remaining at GR) for PHARMA-001.
2. Attempt MIGO GR for PHARMA-001 with a batch whose remaining shelf life is only 20 days. The system should reject the GR with a shelf life error.
3. GR with a batch that has 45 days remaining — this should succeed.

**Test 3: Batch Traceability**

1. After delivering PHARMA-001 with BATCH001, run VLBR for BATCH001: the report should show all deliveries and customers that received this batch.
2. Run MB56 (Batch Where-Used): shows all goods movements for BATCH001 — GR, GI, delivery.
3. In a recall scenario, VLBR and MB56 together provide the complete regulatory traceability picture.

### Cross-Module Perspective

**FI Account Determination:**
- Batch management does NOT inherently change FI account determination — BSX still determines the inventory GL by valuation class (not by batch).
- Exception: If batch-specific valuation is active (each batch has its own price in MBEW), the valuation class can differ per batch, leading to different GL accounts. This is an advanced scenario combining batch management with split valuation.

**CO Perspective:**
- Batch characteristics can include CO account assignment data (cost center, internal order) for batches requiring special cost tracking.
- Production orders can issue specific batches (movement 261 with batch specification), enabling batch-level cost visibility in CO.

**SD Integration:**
- Batch determination in delivery uses condition technique (same framework as pricing). MBC1 condition records define which strategy applies per sales area, customer, or material combination.
- Batch split in delivery (VL02N): one delivery item can be filled from multiple batches. Each batch appears as a sub-item on the delivery with its own quantity. PGI reduces each batch's stock separately.

**Integration Cross-References:**
- Batch management decision tree: `modules/mm/mm-advanced.md` Decision Tree 7
- Batch determination in delivery: `modules/sd/tcodes.md` (VLBR, MBC1, CL20N)
- Shelf life fields (MARC-MHDRP, MHDHB): `modules/mm/master-data.md` Plant Data/Storage 1 view

### Common Pitfalls

- **No batch determination — any batch picked:** If MBC1 condition records are missing or expired, the system performs no automatic batch determination. The user must manually enter the batch. Set up MBC1 records for all required material/plant/strategy combinations.
- **Wrong batch level (client vs. plant):** If client-level batch uniqueness is required (regulatory) but plant-level is configured, batch numbers can duplicate across plants — creating incorrect traceability. Confirm batch level before first batch creation.
- **Shelf life not enforced:** If MARC-MHDRP is configured but the batch classification does not include the production/expiry date characteristic, the system cannot calculate remaining shelf life and the check is skipped. Verify the batch class includes LOBM_VFDAT (shelf life expiration date, standard SAP characteristic).
- **Batch split not activated in copy control:** Batch split in delivery requires a specific copy control setting (batch split allowed). Without it, deliveries force a single batch per delivery item even if multiple batches have the required quantity.

---

## Playbook 8: Serial Number Management

> Serial number management tracks individual serialized units through their full lifecycle — from goods receipt through warehouse, to delivery to the customer, and optionally to PM equipment master and FI fixed asset — with serial number profiles controlling at which transactions serial numbers are captured.

### Business Context

Serial numbers are used to track individual physical units when:
- **Warranty tracking:** Know exactly which unit was sold to which customer on which date
- **Regulatory compliance:** FDA, CE marking, or industry requirements for unit-level traceability
- **Asset management:** High-value equipment whose individual lifecycle must be managed (linked to FI asset master via equipment master)
- **Service/PM integration:** Serialized equipment creates an equipment master (PM module) enabling maintenance history, service orders, and spare parts tracking

Serial numbers are managed via serial number profiles (OISO) assigned to materials. The profile defines at which transactions (GR, GI, delivery, transfer posting) the system requires or allows serial number entry.

### Prerequisites

- Serial number profile defined in OISO (SPRO → Logistics General → Equipment and Technical Objects → Serial Numbers → Define Serial Number Profiles)
- Serial number profile assigned to material master (Plant Data/Storage 1 view, field MARC-SERAIL)
- Equipment master integration optional (configured in serial number profile — links serialized unit to PM equipment)
- FI asset integration optional (for high-value serialized equipment linked to asset sub-numbers)

### Configuration Walkthrough

#### Step 1: MM — Define Serial Number Profile (OISO)

**T-code:** OISO
**SPRO Path:** Logistics General → Equipment and Technical Objects → Serial Numbers → Define Serial Number Profiles

In OISO, define a profile (e.g., Z001) with the following settings:

| Transaction | Options |
|------------|---------|
| Goods Receipt (MIGO 101) | Required / Optional / Not allowed |
| Goods Issue (MIGO 201/261) | Required / Optional / Not allowed |
| Delivery (VL02N PGI, movement 601) | Required / Optional / Not allowed |
| Transfer Posting | Required / Optional / Not allowed |
| Equipment creation | Automatic (creates equipment master on GR) / Manual / None |

For warranty tracking: require serial numbers at GI (delivery). For full lifecycle: require at GR and GI. For asset integration: enable automatic equipment creation at GR.

**Gotcha:** If serial numbers are required at GR (profile setting = mandatory) but the GR is processed in MIGO without entering serial numbers, the posting fails. Train users on serial number entry screens before go-live. The serial number entry screen in MIGO is a sub-screen that appears after the main GR entry.

#### Step 2: MM — Assign Profile to Material Master

**T-code:** MM02
**View:** Plant Data / Storage 1
**Field:** MARC-SERAIL (Serial Number Profile)
**Settings:** Assign the serial number profile (e.g., Z001) to the material. Once assigned, all goods movements for this material at this plant will follow the serial number requirements defined in the profile.

**Gotcha:** After assigning a serial number profile to a material with existing stock, all future movements require serial numbers. Existing stock already in the system may not have serial numbers — this creates a data quality issue. Plan serial number activation as part of a controlled migration (stock-out and re-receive with serial numbers, or use a data migration program).

#### Step 3: SD — Serial Numbers in Delivery (VL02N)

**Configuration:** No special SPRO configuration needed for serial number entry in delivery if the serial number profile (OISO) is configured with delivery relevance. The serial number entry screen appears automatically in VL02N during PGI processing when the material has a serial number profile.

**Settings:** In VL02N, after entering the delivery quantity, navigate to the serial number screen (appears as a sub-tab or via menu). Enter the serial number(s) to be shipped to this customer. The system validates that the serial numbers entered are in stock (have been received in MM and are available for shipment).

**Gotcha:** If the serial number was received in MIGO but was not transferred to the correct storage location, it may not appear as available for the delivery. Check MMBE or IQ09 (Serial Number List) to verify serial number availability and location.

#### Step 4: PM — Equipment Master Integration

**T-code:** IE01 (Create Equipment) — automatically created if profile enables auto-creation
**Settings:** When a serialized material is received in MIGO (movement 101) and the serial number profile is configured for automatic equipment creation, the system creates a PM equipment master (EQUI table) linked to the serial number. The equipment master enables:
- Maintenance history per serial number
- Service orders (IW31) referencing the specific serialized unit
- Spare parts lists per equipment category
- Counter readings for preventive maintenance scheduling

The equipment is linked to the material and serial number: EQUI-MATNR + EQUI-SERNR.

#### Step 5: FI — Asset Sub-Number Integration (High-Value Equipment)

**T-code:** AS21 (Create Sub-Number), SPRO (asset serial number integration)
**SPRO Path:** Financial Accounting → Asset Accounting → Integration with Other Components → Integrate with Plant Maintenance

For high-value serialized equipment where each unit must be depreciated individually:
- The equipment master (from Step 4) is linked to an FI asset sub-number (ANLZ-ANLUN)
- The asset sub-number inherits the main asset's depreciation rules but tracks the individual unit's cost and book value
- When the serialized unit is sold (delivery + billing), the asset retirement posting (ABAVN) reduces the sub-number's book value and recognizes any gain/loss on disposal

### Master Data Setup

| Object | Configuration | T-code |
|--------|--------------|--------|
| Serial number profile | Define transaction requirements (GR, GI, delivery) + equipment creation setting | OISO |
| Material master | MARC-SERAIL = serial number profile | MM02 (Plant Data/Storage 1) |
| Equipment master (PM) | Created manually or automatically at GR; linked to serial number | IE01 (or automatic via OISO) |
| Asset master (FI) | Created per capital equipment lot; sub-numbers per serial number for high-value items | AS01 (asset), AS21 (sub-number) |

### Process Flow

| Step | Activity | T-code | Serial Number Handling |
|------|----------|--------|----------------------|
| 1 | GR of serialized material | MIGO (101) | Enter serial number(s) on serial number sub-screen. Each serial number = one unit. Equipment master created if OISO is configured. |
| 2 | Verify serial numbers in stock | IQ09 | Serial Number List: shows all serial numbers for a material with their current location (plant, storage location, special stock) |
| 3 | Transfer posting (optional) | MIGO / MB1B | Enter serial numbers when moving between storage locations. Serial number follows the physical unit. |
| 4 | Create delivery for serialized material | VL01N | Standard delivery creation |
| 5 | Assign serial numbers to delivery | VL02N | Enter specific serial numbers to ship to this customer. System validates serial number is in stock and unrestricted. |
| 6 | Post goods issue | VL02N | Movement 601. Serial numbers status changes from "In Stock" to "At Customer." Equipment master (if used) records the customer and delivery. |
| 7 | Billing | VF01/VF04 | Standard billing; serial number is traceable via delivery reference in the billing document |
| 8 | Serial number history/traceability | IQ09 | Full movement history per serial number: GR date, GR document, ship date, ship delivery, customer |

### Test Scenarios

**Test 1: GR → Delivery → Serial Number Traceability**

1. Create serial number profile Z001 in OISO: require serial numbers at GR and at delivery GI. Assign Z001 to material PUMP-001 in Plant 1000 (MM02, Plant Data/Storage 1, MARC-SERAIL = Z001).
2. Post GR: MIGO, movement 101, reference PO for PUMP-001. When the serial number sub-screen appears, enter serial numbers SN001, SN002, SN003 (for 3 units received). Verify the MIGO posting was successful.
3. Verify serial numbers in system: IQ09, filter for material PUMP-001, Plant 1000. Verify 3 serial numbers appear with status "In Warehouse."
4. Create delivery: VL01N from sales order for PUMP-001, quantity 2. In VL02N, before PGI, navigate to the serial number screen. Assign SN001 and SN002 to the delivery. Post PGI. Verify in IQ09: SN001 and SN002 show status "At Customer"; SN003 remains "In Warehouse."

**Test 2: Equipment Master Auto-Creation**

1. Configure OISO to create equipment automatically at GR. Post GR for PUMP-001 with serial number SN004. After the MIGO posting, run IE03 (Display Equipment) or search for equipment by serial number SN004. Verify that an equipment master was created automatically in PM with the serial number, material, and plant data.
2. In the equipment master, navigate to the "Structure" tab — the serialized unit is now available for maintenance planning.

**Test 3: FI Asset Integration**

1. Create an asset main number (AS01) for the PUMP category. Create asset sub-number SN001 (AS21) representing the specific serialized unit corresponding to serial number SN001.
2. Link the sub-number to the PM equipment master: in the equipment master (IE02), enter the asset sub-number in the asset reference field.
3. Run AFAB (depreciation) — verify the sub-number depreciates separately per its capitalization date.
4. When the serialized unit is sold and delivered to the customer, the billing triggers asset retirement (if integrated): ABAVN posts the book value write-off and any gain/loss on disposal.

### Cross-Module Perspective

**FI Account Assignment:**
- Serial numbers themselves do not change FI account determination — BSX still drives inventory GL account by valuation class, not by serial number.
- Exception: When a serialized unit is linked to a FI asset sub-number, depreciation (AFAB) posts to the asset's cost center. Asset retirement at sale time (ABAVN via VBREV linking to billing) creates FI postings for book value reduction and gain/loss.

**PM Integration:**
- Each serialized unit corresponds to one PM equipment master (EQUI table).
- Maintenance history (IW61 work orders, counters, technical findings) is tracked at the equipment level.
- Service orders (IW31) reference the equipment master, enabling repair cost collection per serial number.
- At GI/delivery, the equipment status can change automatically (e.g., from "In Plant" to "At Customer").

**SD Integration:**
- Serial numbers in delivery: the VL02N serial number screen allows picking specific serial numbers for specific customers — ensuring that warranty start dates are correctly recorded.
- Returns (VA01 RE): the return delivery in VL01N requires entry of the serial number being returned. The system validates that the serial number was previously delivered to this customer.

**Integration Cross-References:**
- Serial number profile decision tree: `modules/mm/mm-advanced.md` Decision Tree 8
- Equipment master PM integration: PM module documentation (not in scope of this KB)
- Asset accounting integration: `modules/fi/processes.md` Section Fixed Assets

### Common Pitfalls

- **Serial number not found at delivery:** The serial number was received in MIGO but the status in the serial number management is "Defective" or "In QM" — not "In Warehouse." Check IQ09 to confirm status. Resolve quality inspection or defect status before delivery.
- **Serial number profile change on material with stock:** Changing MARC-SERAIL after stock exists creates inconsistency — existing stock does not have serial numbers, new movements require them. Handle this via a data migration (stock-out + re-receive with serial numbers).
- **Auto-equipment creation causing number range issues:** If OISO is configured to auto-create equipment but the PM equipment number range (NUMM) is full or not configured, the MIGO GR fails. Set up equipment number ranges in PM before activating auto-creation.
- **Asset sub-number linkage missing:** If the equipment master is not linked to the FI asset sub-number, the depreciation and retirement postings cannot be automated. Manual journal entries for asset retirement at sale are error-prone. Link the PM equipment to FI asset sub-number during commissioning.
- **Batch + serial number on same material:** Some implementations require both batch and serial number management on the same material (e.g., pharmaceuticals with both lot tracking and unit tracking). In ECC 6, both can be active simultaneously — but every goods movement requires both a batch number AND a serial number. Test all movement types carefully before go-live.

---

## S/4HANA Differences

| Area | ECC 6 Behavior | S/4HANA Change | Impact on Playbooks |
|------|----------------|----------------|---------------------|
| Material documents | MKPF/MSEG tables | Single MATDOC table | All playbook movement types (101K, 411K, 541, 543, 631-634, 601) write to MATDOC; business logic unchanged |
| Vendor master | LFA1/LFB1/LFM1 | Business Partner (BUT000) | Consignment info records still maintained via ME11; vendor consignment logic unchanged |
| Customer master | KNA1/KNB1/KNVV | Business Partner (BUT000) | Consignment billing, IC billing unchanged; customer maintained via BP |
| Controlling Area | 1:many company code assignment | 1:1 strongly recommended | IC billing reconciliation simpler in S/4 with Universal Journal |
| Material Ledger | Optional | Mandatory | Split valuation actual costing always available in S/4; CKMLCP always required |
| Batch level | OMAD client/plant/material | Same options in S/4 | No change to batch management configuration |
| Serial numbers | Same profile-based approach | Same OISO configuration | No change; equipment integration unchanged |
| Intercompany billing | IV billing type; separate FI docs | Same billing; ACDOCA stores both CC postings | No functional change; IC clearing simplified by Universal Journal |
| CO-PA | COPA tables (CE1-CE4) | Merged into ACDOCA | Margin analysis results same; query layer changes |
| Reconciliation ledger (KALC) | Required for cross-CC CO | Eliminated — ACDOCA handles natively | IC billing cross-CC reconciliation automatic in S/4; KALC not needed |
| Subcontracting 541/543 | Same movement types | Same movement types; MATDOC | Business logic for 541 (no FI) and 543 (GBB/VBO) unchanged |
| Phantom assemblies | MRP key 20 | Same key; MRP Live in S/4 | pMRP (MD01N) evaluates phantom assemblies same way |
