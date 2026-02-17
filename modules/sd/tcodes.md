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
