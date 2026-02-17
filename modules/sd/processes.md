---
module: sd
content_type: processes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# Sales & Distribution — Business Processes

> ECC 6.0 reference. Each process documented as numbered narrative followed by summary table (Step | Activity | T-code | Role | Output). Roles: Sales Rep, Sales Manager, Shipping Clerk, Warehouse Worker, Billing Clerk, AR Accountant, Credit Analyst.

## Document Flow Reference

The SD document chain creates linked documents traceable via VBFA (document flow table):

```
Inquiry (VA11)  →  Quotation (VA21)  →  Sales Order (VA01)  →  Delivery (VL01N)  →  PGI (VL02N)  →  Billing (VF01)  →  FI Document
  VBAK/VBAP         VBAK/VBAP            VBAK/VBAP              LIKP/LIPS           MKPF/MSEG         VBRK/VBRP          BKPF/BSEG
  Doc cat A          Doc cat B            Doc cat C              Doc cat J           Mat doc            Doc cat M          Accounting doc
```

Inquiry and quotation are optional pre-sales documents. The core flow is: Sales Order → Delivery → PGI → Billing → FI Document.

---

## 1. Standard Order-to-Cash (Sales Order → Invoice)

The standard O2C process covers the complete cycle from customer order through revenue recognition. This is the core SD business process and the primary SD-FI integration point.

### Narrative

**Step 1 — Create Sales Order** (Sales Rep)
Create a sales order in VA01 with document type OR (standard order). Enter sold-to party, material, quantity, requested delivery date, and PO number. The system:
- Proposes pricing from condition records (pricing procedure determined by OVKK)
- Proposes partner functions from customer master (KNVP → VBPA)
- Proposes payment terms, incoterms, shipping condition from customer master (KNVV)

Creates VBAK (header) + VBAP (item) + VBEP (schedule line) + VBPA (partners) + VBKD (business data).

Can also be created with reference to inquiry (VA11) or quotation (VA21) via copy control (VTAA).

**Step 1a — Availability Check (ATP)** (System — automatic)
If the checking group (MARC-MTVFP) and checking rule (from document type) are configured, the system performs an Available-to-Promise check at order save. ATP considers:
- Current stock (unrestricted)
- Planned receipts (POs, production orders, planned orders)
- Existing demand (other sales orders, deliveries, dependent requirements)

If insufficient stock exists for the requested date, the system proposes a confirmed date or partial confirmation. The schedule line (VBEP) records both requested quantity and confirmed quantity.

> ATP and credit check are **independent controls**. ATP checks material availability; credit check examines customer creditworthiness. Both can block the order, but for different reasons and with different resolution paths.

**Step 1b — Credit Check** (System — automatic)
If credit checking is configured (OVA8), the system checks the customer's credit exposure against the credit limit (FD32). The check can occur at:
- Sales order creation (credit group 01)
- Delivery creation (credit group 02)
- Goods issue / PGI (credit group 03)

If the credit limit is exceeded, the document is blocked. Credit analyst reviews and releases via VKM1 (orders), VKM4 (deliveries), or VKM5 (goods issue).

**Step 2 — Delivery Creation** (Shipping Clerk)
Create outbound delivery in VL01N from the sales order. The system determines:
- Shipping point (from shipping condition + loading group + plant → OVXC)
- Route (from departure country + shipping point + transportation group + destination → OVTC)
- Delivery quantities (from confirmed schedule line quantities)

Creates LIKP (delivery header) + LIPS (delivery items). Delivery date drives the transportation scheduling (loading date, goods issue date, delivery date).

**Step 3 — Pick, Pack, and Load** (Warehouse Worker)
In VL02N, confirm picked quantities. If Warehouse Management (WM) is active, transfer orders are created automatically. Packing uses handling units (HU). This step is optional for companies without warehouse automation — quantities can be confirmed directly.

**Step 4 — Post Goods Issue (PGI)** (Shipping Clerk)
Post goods issue in VL02N via the "Post Goods Issue" button. Movement type 601 (goods issue for delivery).

FI posting at PGI:
- **Dr COGS** (Cost of Goods Sold — from VKOA account determination)
- **Cr BSX** (Inventory — stock account from OBYC)

Material document created: MKPF (header) + MSEG (line items). Stock is reduced. The delivery status updates to "goods issue posted."

> PGI is the SD-MM/FI handoff for inventory and COGS. From this point, the inventory reduction is posted and the cost side of the transaction is complete in FI.

> **S/4HANA Note:** MKPF/MSEG replaced by single MATDOC table at PGI. Business process unchanged.

**Step 5 — Create Billing Document** (Billing Clerk)
Create billing document in VF01 (single) or VF04 (billing due list for collective processing). The billing document type is determined by copy control (VTFL: delivery type → billing type). Standard: delivery type LF → billing type F2 (invoice).

FI posting at billing:
- **Dr Customer** (AR sub-ledger — reconciliation account from KNB1-AKONT)
- **Cr Revenue** (revenue GL account — from VKOA account determination)
- **Dr/Cr Tax** (output tax — from MWST condition type → tax GL account)

Creates VBRK (billing header) + VBRP (billing items) + BKPF/BSEG (FI accounting document).

> VF01/VF04 is the SD-FI handoff for revenue. From this point, the customer open item lives in FI (visible in FBL5N) and is picked up by dunning (F150) or cleared by incoming payment (F-28/F-06).

**Step 6 — Payment Receipt** (AR Accountant)
Customer payment is processed in FI via incoming payment (F-28), automatic clearing (F.13), or lockbox processing. The customer open item created by billing is cleared.

> **Cross-reference:** Payment processing is fully documented in `modules/fi/processes.md` (AR section). The O2C handoff: VF01 creates the customer open item → FI processes the payment → FBL5N shows cleared status.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Create sales order (with pricing, partners) | VA01 | Sales Rep | Sales order (VBAK/VBAP) with confirmed quantities |
| 1a | Availability check (ATP) | Automatic | System | Confirmed qty in schedule line (VBEP) |
| 1b | Credit check | Automatic | System | Order blocked if limit exceeded → VKM1 |
| 2 | Create outbound delivery | VL01N | Shipping Clerk | Delivery (LIKP/LIPS) with shipping point, route |
| 3 | Pick, pack, load | VL02N | Warehouse Worker | Picked quantities confirmed |
| 4 | Post goods issue (PGI) | VL02N | Shipping Clerk | Material doc (601); FI: Dr COGS / Cr Inventory |
| 5 | Create billing document | VF01/VF04 | Billing Clerk | Billing doc (VBRK/VBRP); FI: Dr Customer / Cr Revenue |
| 6 | Receive customer payment | F-28/F.13 | AR Accountant | Payment cleared (see FI processes.md) |

---

## 2. Returns (RMA Process)

**Step 1 — Create Returns Order** (Sales Rep)
Create sales order in VA01 with document type RE. Enter the customer and reference the original order or billing document. Item category REN allows negative billing (credit).

**Step 2 — Return Delivery** (Shipping Clerk)
Create return delivery in VL01N referencing the returns order. The delivery type LR (returns delivery) is proposed by copy control. The return delivery represents expected incoming goods from the customer.

**Step 3 — Goods Receipt of Returns** (Warehouse Worker)
Post goods receipt for the return delivery in VL02N (or MIGO with reference to the return delivery). Movement type 651 (returns from customer). FI posting: Dr Inventory / Cr COGS reversal.

**Step 4 — Credit Memo or Re-Delivery** (Billing Clerk)
Create billing document in VF01 from the returns order. Billing type RE (returns credit) creates a credit memo. FI posting: Dr Revenue / Cr Customer (reduces customer balance).

Alternatively, the customer may receive a replacement delivery instead of a credit.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Create returns order | VA01 (RE) | Sales Rep | Returns order with REN item category |
| 2 | Create return delivery | VL01N | Shipping Clerk | Returns delivery (LR) |
| 3 | Goods receipt of returns | VL02N | Warehouse Worker | Material doc (651); FI: Dr Inv / Cr COGS |
| 4 | Create credit memo | VF01 | Billing Clerk | Credit memo; FI: Dr Revenue / Cr Customer |

---

## 3. Credit and Debit Memos

### Credit Memo Request → Credit Memo
**Step 1 — Create Credit Memo Request** (Sales Rep): VA01, doc type CR. Captures the reason for the credit (pricing error, damaged goods, goodwill). Requires approval before billing.
**Step 2 — Block/Release** (Sales Manager): Credit memo request may be blocked for approval. Release via billing block removal in VA02.
**Step 3 — Create Credit Memo** (Billing Clerk): VF01 creates billing type G2 (credit memo). FI posting: Dr Revenue / Cr Customer.

### Debit Memo Request → Debit Memo
**Step 1 — Create Debit Memo Request** (Sales Rep): VA01, doc type DR. Used when the customer was undercharged.
**Step 2 — Create Debit Memo** (Billing Clerk): VF01 creates billing type L2 (debit memo). FI posting: Dr Customer / Cr Revenue.

---

## 4. Cash Sales

VA01 with document type CS (cash sale). The system creates the order, delivery, and billing document simultaneously. The customer pays immediately at the point of sale — no open item is created. FI posting: Dr Cash/Bank / Cr Revenue.

Gotcha: Cash sales require a specific delivery type and billing type configured in VOV8. The item category determination uses the CS document type to propose the correct item category.

---

## 5. Rush Orders

VA01 with document type RO (rush order). The delivery is created automatically at order save (no separate VL01N step). The rest of the process follows standard O2C: manual PGI in VL02N → billing in VF01. Rush orders skip the delivery creation queue but still require PGI and billing as separate steps.

---

## 6. Consignment

Consignment is a multi-step process where stock is placed at the customer site but remains company-owned until the customer withdraws (issues) it.

**Consignment Fill-Up (KB):** VA01, doc type KB → delivery → PGI (movement type 631). Stock moves to consignment at customer (special stock W). No billing — goods still belong to the company.

**Consignment Issue (KE):** VA01, doc type KE → delivery → PGI (movement type 633). Customer withdraws from consignment stock. Billing now occurs — revenue recognized.

**Consignment Pickup (KR):** VA01, doc type KR → return delivery → GR (movement type 632). Company retrieves unsold consignment stock. No billing.

**Consignment Returns (KA):** VA01, doc type KA → return delivery → GR (movement type 634). Customer returns already-issued consignment goods. Credit memo issued.

### Summary Table

| Scenario | Doc Type | Movement Type | Billing | Stock Type |
|----------|----------|---------------|---------|------------|
| Fill-Up | KB | 631 (issue to consignment) | No | Special stock W at customer |
| Issue | KE | 633 (consignment issue) | Yes — revenue recognized | Unrestricted → sold |
| Pickup | KR | 632 (return from consignment) | No | Returns to unrestricted |
| Returns | KA | 634 (consignment returns) | Credit memo | Returns after issue |

---

## 7. Third-Party Processing

In third-party processing, the company takes the customer order but the vendor ships directly to the customer. The company never handles the goods.

**Step 1 — Create Sales Order** (Sales Rep): VA01 with item category TAS (third-party). The system automatically creates a purchase requisition (PR) in the background.

**Step 2 — Create Purchase Order** (Buyer): Convert the auto-generated PR to a PO (ME21N) to the vendor. The PO delivery address is the customer's ship-to address.

**Step 3 — Vendor Ships to Customer** (Vendor): The vendor ships directly to the customer. No delivery document is created in SD.

**Step 4 — Invoice from Vendor** (AP Accountant): Post the vendor invoice in MIRO. The goods receipt is statistical (no physical inventory movement in your warehouse).

**Step 5 — Bill the Customer** (Billing Clerk): Create billing document in VF01 from the sales order (order-related billing, not delivery-related). FI posting: Dr Customer / Cr Revenue.

> Third-party processing spans MM (purchasing) and SD (sales). The sales order triggers the MM procurement cycle. Key config: item category TAS with billing relevance = B (order-related billing).
