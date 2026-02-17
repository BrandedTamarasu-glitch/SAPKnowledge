---
module: sd
content_type: tcodes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# Sales & Distribution — Transaction Codes

> ECC 6.0 reference. T-codes listed work in both ECC 6.0 and S/4HANA via SAP GUI. S/4HANA also offers equivalent Fiori apps. Key S/4 differences: customer master XD01/VD01 → Business Partner (BP); output determination NACE → BRF+ output management; credit management FD32 → FSCM/UKM.

## Workflow Index

| Process Stage | T-code(s) | Submodule | Notes |
|---|---|---|---|
| Inquiry | VA11 | Sales | Pre-sales document (optional) |
| Quotation | VA21 | Sales | Pre-sales document (optional) |
| Sales Order Creation | VA01 | Sales | Doc type OR=standard, RE=returns, CR/DR=credit/debit memo |
| Sales Order Change/Display | VA02, VA03 | Sales | |
| Scheduling Agreement (SD) | VA31 | Sales | Long-term delivery schedule |
| Contract (SD) | VA41 | Sales | Quantity or value contract |
| Delivery Creation | VL01N | Shipping | From sales order |
| Delivery Change (incl. PGI) | VL02N | Shipping | PGI posted here via Post Goods Issue |
| Delivery Display | VL03N | Shipping | |
| Collective Delivery | VL04 | Shipping | Batch delivery processing |
| Delivery Monitor | VL06O | Shipping/Reporting | Primary delivery worklist |
| Delivery Due List | VL10A | Shipping | Background delivery creation |
| GI for Deliveries | VL06G | Shipping | Deliveries ready for goods issue |
| Shipment | VT01N | Shipping | Transportation planning |
| Billing Creation | VF01 | Billing | Single document |
| Billing Due List | VF04 | Billing | Collective billing |
| Billing Change/Display | VF02, VF03 | Billing | |
| Billing Cancel | VF11 | Billing | Creates cancellation document |
| Invoice List | VF21 | Billing | Consolidated invoicing |
| Blocked Billing Docs | VFX3 | Billing | Release blocked documents |
| Rebate Settlement (Partial) | VF44 | Billing | Partial rebate credit memo |
| Rebate Settlement (Final) | VF45 | Billing | Final settlement closes agreement |
| Condition Record Maint | VK11, VK12, VK13 | Pricing | Create/change/display condition records |
| Condition Tables | V/06 | Pricing | Config: define condition tables |
| Access Sequences | V/07 | Pricing | Config: define access sequences |
| Condition Types | V/08 | Pricing | Config: define condition types |
| Pricing Procedures | V/09 | Pricing | Config: define procedures |
| Pricing Procedure Assign | OVKK | Pricing | Config: determination assignment |
| Output Condition Records | VV31, VV32, VV33 | Output | Create/change/display output records |
| Output Determination Config | NACE | Output | Central output config (V1/V2/V3) |
| Customer Credit Data | FD32 | Credit | S/4: replaced by UKM |
| Credit Block Review | VKM1 | Credit | Blocked SD documents |
| Released SD Docs (Credit) | VKM3 | Credit | Released from credit block |
| Credit Block — Delivery | VKM4 | Credit | Deliveries blocked by credit |
| Credit Block — Goods Issue | VKM5 | Credit | PGI blocked by credit |
| Rebate Agreement | VBO1 | Rebates | Create rebate agreement |
| Rebate Settlement (Batch) | VBOF | Rebates | Mass settlement |
| Customer Master (SD) | VD01, VD02, VD03 | Master Data | SD views only (KNA1+KNVV) |
| Customer Master (Central) | XD01, XD02, XD03 | Master Data | All views (KNA1+KNB1+KNVV) |
| Customer-Material Info | VD51 | Master Data | Customer material cross-reference |
| Sales Order List | VA05 | Reporting | By customer, material, date |
| Billing Doc List | VF05 | Reporting | By payer, date, amount |
| Backorder Processing | V.02 | Reporting | ATP reallocation |
| Batch Where-Used (Deliveries) | VLBR | Batch Determination | Batch traceability |
| SD Information System | MCTA, MCTC | Reporting | Statistical analyses (LIS) |

---

## Sales Documents

### VA11 — Create Inquiry

**Menu Path:** Logistics → Sales and Distribution → Sales → Inquiry → Create
**Usage:** Pre-sales document recording customer interest. Optional step — many implementations skip inquiry and start with quotation or order. Creates VBAK/VBAP entries with document category A.

### VA12 — Change Inquiry

**Menu Path:** Logistics → Sales and Distribution → Sales → Inquiry → Change

### VA13 — Display Inquiry

**Menu Path:** Logistics → Sales and Distribution → Sales → Inquiry → Display

---

### VA21 — Create Quotation

**Menu Path:** Logistics → Sales and Distribution → Sales → Quotation → Create
**Usage:** Formal offer to customer with pricing and validity period. Can be created with reference to inquiry. Document category B.
**Gotcha:** Quotation validity (VBAK-ANGDT/BNDDT) controls whether the quotation can be referenced by a sales order — expired quotations cannot be copied.

### VA22 — Change Quotation

**Menu Path:** Logistics → Sales and Distribution → Sales → Quotation → Change

### VA23 — Display Quotation

**Menu Path:** Logistics → Sales and Distribution → Sales → Quotation → Display

---

### VA01 — Create Sales Order

**Menu Path:** Logistics → Sales and Distribution → Sales → Order → Create
**Usage:** Core SD transaction. Document type determines the business scenario:
- **OR** — Standard order
- **RE** — Returns order (triggers return delivery + credit memo)
- **CR** — Credit memo request
- **DR** — Debit memo request
- **CS** — Cash sale (immediate billing + delivery)
- **RO** — Rush order (immediate delivery)
- **KB** — Consignment fill-up (stock vendor consignment at customer)
- **KE** — Consignment issue (customer consumes consignment stock)
- **KR** — Consignment pickup (return consignment stock)
- **KA** — Consignment returns

Availability check (ATP) and credit check execute automatically at order save (if configured).
**Gotcha:** CRITICAL — The document type drives ALL downstream behavior: item categories, schedule line categories, delivery type, billing type, and copy control. Wrong document type = wrong process.

### VA02 — Change Sales Order

**Menu Path:** Logistics → Sales and Distribution → Sales → Order → Change

### VA03 — Display Sales Order

**Menu Path:** Logistics → Sales and Distribution → Sales → Order → Display
**Usage:** Most commonly used for order status tracking and document flow review (Environment → Document Flow).

---

### VA31 — Create Scheduling Agreement

**Menu Path:** Logistics → Sales and Distribution → Sales → Scheduling Agreement → Create
**Usage:** Long-term sales agreement with delivery schedule lines. Customer-facing equivalent of MM scheduling agreement (ME31L).

### VA32 — Change Scheduling Agreement

**Menu Path:** Logistics → Sales and Distribution → Sales → Scheduling Agreement → Change

### VA33 — Display Scheduling Agreement

**Menu Path:** Logistics → Sales and Distribution → Sales → Scheduling Agreement → Display

---

### VA41 — Create Contract

**Menu Path:** Logistics → Sales and Distribution → Sales → Contract → Create
**Usage:** Long-term sales agreement (quantity or value) with a customer. Release orders (VA01) reference the contract.

### VA42 — Change Contract

**Menu Path:** Logistics → Sales and Distribution → Sales → Contract → Change

### VA43 — Display Contract

**Menu Path:** Logistics → Sales and Distribution → Sales → Contract → Display

---

## Shipping & Delivery

### VL01N — Create Outbound Delivery

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → Create → Single Document → With Reference to Sales Order
**Usage:** Creates delivery document (LIKP/LIPS) from sales order. Shipping point determined automatically from plant + shipping condition + loading group.
**Gotcha:** VL01N creates the delivery but does NOT post goods issue. PGI is a separate step in VL02N.

### VL02N — Change Outbound Delivery

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → Change → Single Document
**Usage:** Change delivery quantities, pick confirmation, and POST GOODS ISSUE (PGI). PGI button posts movement type 601 (goods issue for delivery). FI posting: Dr COGS / Cr Inventory (via OBYC GBB/VAX or VAY and BSX).
**Gotcha:** PGI is posted WITHIN VL02N, not as a separate transaction. This is the SD-FI handoff for cost of goods sold.

### VL03N — Display Outbound Delivery

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → Display → Single Document

---

### VL04 — Change Deliveries (Collective)

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → Change → Collective Processing
**Usage:** Process multiple deliveries at once — useful for batch PGI.

### VL06O — Outbound Delivery Monitor

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → List Outbound Deliveries → For Outbound Delivery
**Usage:** Primary delivery worklist — shows deliveries by status (open for picking, open for PGI, goods issued). Best single-screen delivery management view.

---

### VL10A — Delivery Due List (Sales Orders)

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → Create → Collective Processing → Delivery Due List → Sales Orders
**Usage:** Background creation of deliveries for sales orders due for shipping. Used as scheduled job for high-volume environments.

### VL06G — List of Outbound Deliveries for Goods Issue

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Outbound Delivery → List Outbound Deliveries → For Goods Issue
**Usage:** All deliveries ready for goods issue — pick worklist for warehouse.

---

### VT01N — Create Shipment

**Menu Path:** Logistics → Sales and Distribution → Transportation → Shipment → Create → Single Document
**Usage:** Groups multiple deliveries into a shipment for transportation planning. Assigns carrier, route, and shipment dates.

### VT02N — Change Shipment

**Menu Path:** Logistics → Sales and Distribution → Transportation → Shipment → Change → Single Document

### VT03N — Display Shipment

**Menu Path:** Logistics → Sales and Distribution → Transportation → Shipment → Display → Single Document

---

## Billing

### VF01 — Create Billing Document

**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Create
**Usage:** Creates billing document (invoice, credit memo, debit memo) from delivery or order. Billing type determined by copy control (VTFL for delivery→billing, VTAF for order→billing). FI document created automatically: Dr Customer (Cr Revenue).
**Gotcha:** VF01 processes ONE document at a time. For mass billing, use VF04.

### VF02 — Change Billing Document

**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Change

### VF03 — Display Billing Document

**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Display
**Usage:** Review billing document, pricing, and FI document number. Use Environment → Document Flow to trace back to delivery and order.

### VF04 — Process Billing Due List

**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Process Billing Due List
**Usage:** Collective billing — processes all deliveries/orders due for billing in batch. Primary billing transaction for high-volume environments.
**Gotcha:** VF04 can create individual or collective invoices (split by payer, billing date, etc.) based on copy control settings.

### VF11 — Cancel Billing Document

**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Cancel
**Usage:** Reversal of billing document. Creates a cancellation document that reverses the FI posting.
**Gotcha:** Cancellation does NOT delete — it creates a new document reversing the original. Both remain visible in document flow.

---

### VF21 — Create Invoice List

**Menu Path:** Logistics → Sales and Distribution → Billing → Invoice List → Create
**Usage:** Combines multiple billing documents for a payer into a single invoice list (factored invoicing). Used when customer receives periodic consolidated invoices.

### VF26 — Cancel Invoice List

**Menu Path:** Logistics → Sales and Distribution → Billing → Invoice List → Cancel

### VFX3 — Blocked Billing Documents

**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Blocked Billing Documents
**Usage:** Review and release billing documents blocked due to credit, incomplete data, or pricing issues.

---

### VF44 — Rebate Settlement: Partial

**Menu Path:** Logistics → Sales and Distribution → Billing → Rebate → Settle Rebate Agreement → Partial Settlement
**Usage:** Creates credit memo for accrued rebate amount up to current date. Agreement remains open.

### VF45 — Rebate Settlement: Final

**Menu Path:** Logistics → Sales and Distribution → Billing → Rebate → Settle Rebate Agreement → Final Settlement
**Usage:** Final settlement closes the rebate agreement and creates final credit memo.

---

## Pricing

Pricing in SD uses the **condition technique** — a reusable 4-layer framework also used for output determination, account determination, and text determination.

**Condition Technique Overview:**
1. **Condition Tables (V/06)** — Define the key combination for looking up condition records (e.g., customer + material, material group, price list)
2. **Access Sequences (V/07)** — Define the search order: which condition tables to check and in what priority (most specific → most general)
3. **Condition Types (V/08)** — Define pricing element behavior: PR00 = base price, K004 = material discount, K005 = customer-specific discount, MWST = tax, RA00 = rebate accrual
4. **Pricing Procedures (V/09)** — Define the calculation sequence: which condition types apply, in what order, with subtotals, requirements, and alternative condition base values

**Assignment (OVKK):** Pricing procedure is assigned to the combination of sales area + document pricing procedure (from sales document type) + customer pricing procedure (from customer master KNVV-KALKS).

### VK11 — Create Condition Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Conditions → Select Using Condition Type → Create
**Usage:** Maintain pricing master data (KONH/KONP tables). Select condition type first (e.g., PR00 for base price), then enter key combination and rate. Validity period controls when the price is effective.

### VK12 — Change Condition Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Conditions → Select Using Condition Type → Change

### VK13 — Display Condition Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Conditions → Select Using Condition Type → Display

---

### V/06 — Define Condition Tables

**Menu Path:** SPRO → Sales and Distribution → Basic Functions → Pricing → Pricing Control → Define Condition Tables
**Usage:** Create or modify the field catalog (key combination) for condition record lookup.
**Gotcha:** Changing a condition table after records exist requires regeneration — plan tables carefully before go-live.

### V/07 — Define Access Sequences

**Menu Path:** SPRO → Sales and Distribution → Basic Functions → Pricing → Pricing Control → Define Access Sequences
**Usage:** Define the search strategy — which condition tables to check and in what order. First hit wins (unless exclusive indicator is off).

### V/08 — Define Condition Types

**Menu Path:** SPRO → Sales and Distribution → Basic Functions → Pricing → Pricing Control → Define Condition Types
**Usage:** Define pricing element properties: calculation type (percentage, fixed, formula), condition class (price, discount, surcharge, tax), access sequence assignment, condition category.

### V/09 — Define Pricing Procedures

**Menu Path:** SPRO → Sales and Distribution → Basic Functions → Pricing → Pricing Control → Define and Assign Pricing Procedures → Maintain Pricing Procedures
**Usage:** Build the pricing calculation schema — step sequence, condition type per step, from/to references, requirements, alternative calculation types, subtotal fields (KOMP).

### OVKK — Pricing Procedure Determination

**Menu Path:** SPRO → Sales and Distribution → Basic Functions → Pricing → Pricing Control → Define and Assign Pricing Procedures → Define Pricing Procedure Determination
**Usage:** Assigns pricing procedure to sales area + document pricing procedure + customer pricing procedure combination.
**Gotcha:** If no entry exists in OVKK for the combination, no pricing procedure is found and the order has no prices — a common go-live error.

---

## Output Determination

Output determination in ECC 6.0 uses the **condition technique** (same framework as pricing). S/4HANA replaces NACE-based output with BRF+ output management — all guidance here is ECC 6.0.

### VV31 — Create Output Condition Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Output → Sales Documents → Create
**Usage:** Create output condition records specifying medium (1=print, 2=fax, 5=EDI, 7=email), timing (1=send immediately, 4=send with next selection), partner, and language for a specific output type.

### VV32 — Change Output Condition Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Output → Sales Documents → Change

### VV33 — Display Output Condition Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Output → Sales Documents → Display

---

### NACE — Output Determination Procedures

**Menu Path:** SPRO → Cross-Application Components → Output Control → Output Determination
**Usage:** Central entry point for output determination configuration. Select the application to access output types, access sequences, and procedure assignments:
- **V1** — Sales (order confirmations)
- **V2** — Shipping (delivery notes, packing lists)
- **V3** — Billing (invoices, credit memos)
- **V4** — Transportation (shipment documents)
**Gotcha:** NACE is the single entry point for ALL output determination — sales order confirmations, delivery notes, invoices, shipping labels all configured through NACE with different application codes.

### VV21 — Create Output Type (Alternative)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Output → Sales Documents → Create (alternative path)
**Usage:** Alternative path for maintaining output types — less commonly used than NACE.

### VV22 — Change Output Type

**Menu Path:** Logistics → Sales and Distribution → Master Data → Output → Sales Documents → Change

### VV23 — Display Output Type

**Menu Path:** Logistics → Sales and Distribution → Master Data → Output → Sales Documents → Display

---

## Credit Management

Credit management in ECC 6.0 uses classic credit checking (FD32 + automatic credit check). S/4HANA replaces this with FSCM Credit Management (UKM transactions).

### FD32 — Change Customer Credit Data

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Credit Management → Master Data → Change
**Usage:** Maintain credit limit, credit exposure, risk category, and credit group per credit control area.
**Gotcha:** FD32 is also accessible from the customer master (XD02) via credit management views. S/4HANA note: replaced by UKM_BP (Business Partner credit management).

### FD33 — Display Customer Credit Data

**Menu Path:** Accounting → Financial Accounting → Accounts Receivable → Credit Management → Master Data → Display

---

### VKM1 — Blocked SD Documents (Credit)

**Menu Path:** Logistics → Sales and Distribution → Credit Management → Exceptions → Blocked SD Documents
**Usage:** List all sales documents blocked by credit check. Credit representative reviews and decides to release or reject.

### VKM3 — Released SD Documents

**Menu Path:** Logistics → Sales and Distribution → Credit Management → Exceptions → Released SD Documents
**Usage:** List of SD documents that were released from credit block.

### VKM4 — Blocked SD Documents for Delivery

**Menu Path:** Logistics → Sales and Distribution → Credit Management → Exceptions → Blocked SD Documents for Delivery
**Usage:** Deliveries blocked by credit check at delivery creation.

### VKM5 — Blocked SD Documents for Goods Issue

**Menu Path:** Logistics → Sales and Distribution → Credit Management → Exceptions → Blocked SD Documents for Goods Issue
**Usage:** Deliveries blocked at PGI by credit check.

---

## Returns & Complaints

Returns and credit/debit memos use the same VA01 transaction with different document types. No separate T-codes exist — the document type controls the process variant.

### VA01 (doc type RE) — Create Returns Order

**Usage:** Customer returns merchandise. Doc type RE triggers return delivery (VL01N creates inbound delivery) and subsequent credit memo or re-delivery. Item category REN (returns) allows negative billing.

### VA01 (doc type CR) — Create Credit Memo Request

**Usage:** Request to issue a credit to the customer. After approval, billing (VF01) creates a credit memo that posts Dr Revenue / Cr Customer in FI.

### VA01 (doc type DR) — Create Debit Memo Request

**Usage:** Request to charge the customer an additional amount. Billing creates a debit memo (Dr Customer / Cr Revenue).

---

## Rebates

Rebates are periodic volume-based discounts settled retrospectively. Foundation-level coverage — deep rebate configuration defers to Phase 8.

### VBO1 — Create Rebate Agreement

**Menu Path:** Logistics → Sales and Distribution → Master Data → Agreements → Rebate Agreement → Create
**Usage:** Creates rebate agreement with condition type (RA00 = rebate accrual), rebate recipient (payer), validity period, and volume targets.

### VBO2 — Change Rebate Agreement

**Menu Path:** Logistics → Sales and Distribution → Master Data → Agreements → Rebate Agreement → Change

### VBO3 — Display Rebate Agreement

**Menu Path:** Logistics → Sales and Distribution → Master Data → Agreements → Rebate Agreement → Display

### VBOF — Rebate Settlement (Batch)

**Menu Path:** Logistics → Sales and Distribution → Billing → Rebate → Settle Rebate Agreement → Batch Processing
**Usage:** Mass settlement of rebate agreements.
**Gotcha:** Rebate settlement creates credit memos via the billing process — ensure copy control for rebate billing types is configured.

---

## Foreign Trade

Foundation-level coverage. Foreign trade manages export/import compliance, customs declarations, and license management.

### VX11 — Foreign Trade Data: Create

**Menu Path:** Not available via standard menu — access via transaction code directly.
**Usage:** Maintain foreign trade data for billing documents (export declarations, customs tariff numbers, country of origin).

### VX12 — Foreign Trade Data: Change

**Menu Path:** Access via transaction code directly.

### VX13 — Foreign Trade Data: Display

**Menu Path:** Access via transaction code directly.

---

## Batch Determination

Batch determination in SD uses the condition technique to automatically find and assign batches during delivery processing. Relevant for batch-managed materials (MARC-XCHPF = X).

### VLBR — Batch Where-Used List (Deliveries)

**Menu Path:** Logistics → Sales and Distribution → Shipping and Transportation → Batch Information → Delivery Batch Where-Used List
**Usage:** Find which deliveries a specific batch was used in. Critical for batch traceability and recall scenarios.

### MBC1 — Create Batch Search Strategy

**Menu Path:** Logistics → Logistics Execution → Shipping → Batch Determination → Batch Search Strategy → Create
**Usage:** Maintain batch search strategies that define how the system selects batches during delivery processing. Search strategy uses condition technique (access sequence → strategy type → sort rules) to find eligible batches by FIFO, FEFO (expiration), or custom criteria.
**Gotcha:** Batch determination must be activated per movement type and plant — inactive by default.

### CL20N — Object Assignment to Classes (Batch Classification)

**Menu Path:** Cross-Application Components → Classification System → Assignment → Assign Object to Classes
**Usage:** Classify batches with characteristics (production date, shelf life, quality grade) used by batch search strategy selection criteria. Without classification, automatic batch determination has no attributes to search on.

---

## Master Data

### VD01 — Create Customer (Sales)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partner → Customer → Create → Sales and Distribution
**Usage:** Creates KNA1 (general) + KNVV (sales area data) without FI company code data. Use when FI manages company code extensions separately.
**Gotcha:** VD01 creates KNA1 + KNVV but NOT KNB1 — customer cannot receive invoices in FI until FI extends with FD01. S/4HANA note: replaced by Business Partner (BP) transaction.

### VD02 — Change Customer (Sales)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partner → Customer → Change → Sales and Distribution

### VD03 — Display Customer (Sales)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partner → Customer → Display → Sales and Distribution

---

### XD01 — Create Customer (Central)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partner → Customer → Create → Complete
**Usage:** Creates all three levels: KNA1 (general) + KNB1 (company code) + KNVV (sales area) in one transaction. Preferred when both SD and FI data are maintained together.

### XD02 — Change Customer (Central)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partner → Customer → Change → Complete

### XD03 — Display Customer (Central)

**Menu Path:** Logistics → Sales and Distribution → Master Data → Business Partner → Customer → Display → Complete

---

### VD51 — Create Customer-Material Info Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Agreements → Customer-Material Info → Create
**Usage:** Links customer's material number to SAP material number. Maintains customer-specific description and delivery plant.

### VD52 — Change Customer-Material Info Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Agreements → Customer-Material Info → Change

### VD53 — Display Customer-Material Info Record

**Menu Path:** Logistics → Sales and Distribution → Master Data → Agreements → Customer-Material Info → Display

---

## Reporting & Analysis

### VA05 — List of Sales Orders

**Menu Path:** Logistics → Sales and Distribution → Sales → Information System → Orders → VA05 - List of Sales Orders
**Usage:** Quick list of sales orders by customer, material, or date range. Shows order status, delivery status, billing status.

### VF05 — List of Billing Documents

**Menu Path:** Logistics → Sales and Distribution → Billing → Information System → VF05 - List of Billing Documents
**Usage:** Search billing documents by payer, billing date, or amount.

### VL06O — Outbound Delivery Monitor (Cross-listed)

Cross-listed from Shipping — primary delivery reporting tool. See Shipping & Delivery section above.

### V.02 — Backorder Processing

**Menu Path:** Logistics → Sales and Distribution → Sales → Backorders
**Usage:** Reassign confirmed quantities between sales orders when ATP is insufficient. Reallocate stock from lower-priority orders to higher-priority ones.

### MC+ Reports (MCTA, MCTC) — SD Information System

**Menu Path:** Logistics → Sales and Distribution → Sales Information System → Standard Analyses
**Usage:** Statistical analyses of sales, deliveries, billing by various dimensions. Reads LIS data (S tables).
**Gotcha:** MC reports rely on statistics update being active (V/LA, V/LB) — if turned off, reports show no data.

---

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|--------|
| Customer master: XD01/VD01 (KNA1/KNB1/KNVV) | Business Partner (BP) — BUT000 | All customer T-codes still work but maintain BP underneath |
| Output: NACE condition-based | BRF+ output management | New output framework; NACE still works for custom outputs |
| Credit: FD32 classic credit mgmt | FSCM Credit Management (UKM) | New credit engine with real-time exposure |
| Sales orders: VA01 SAP GUI | Manage Sales Orders Fiori app | GUI T-codes still functional in S/4 |
| Material documents: MKPF/MSEG at PGI | MATDOC single table | Technical change; business process unchanged |
