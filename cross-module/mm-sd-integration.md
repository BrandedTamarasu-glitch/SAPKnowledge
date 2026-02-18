---
module: cross-module
content_type: integration
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
related_modules: [mm, sd]
---

# MM-SD Integration Points

> ECC 6.0 reference. Documents every touchpoint where Materials Management and Sales & Distribution interact -- availability check, goods issue for delivery, returns, consignment, stock transport orders, third-party processing, and subcontracting. Each section provides the integration handoff detail and points to existing module files for full depth. For OBYC account determination details, see `modules/mm/mm-advanced.md`. For VKOA revenue account determination, see `modules/sd/sd-advanced.md`.

## Prerequisites

Read these module files for full detail on individual steps:

- `modules/sd/processes.md` -- O2C narrative, returns, consignment, third-party, subcontracting process flows
- `modules/sd/config-spro.md` -- OVZ2 availability check configuration, shipping point determination, copy control
- `modules/sd/integration.md` -- SD-FI integration catalog, VF01 billing trace, PGI COGS trace
- `modules/mm/integration.md` -- MM-FI integration catalog, MIGO 101 posting trace, GR/IR clearing
- `modules/mm/processes.md` -- P2P narrative, physical inventory
- `modules/mm/mm-advanced.md` -- OBYC walkthrough with 10+ worked examples including movement type 601

---

## Availability Check (ATP)

The availability check is the primary SD-to-MM handshake at sales order creation. When a user saves a sales order in VA01, the system checks material availability in MM to confirm whether the requested quantity can be delivered on the requested date.

### How SD Triggers the Check

At sales order save, schedule line determination reads two inputs:

1. **Checking group** (MARC-MTVFP on the material master MRP 3 view) -- defines WHAT stock and supply elements to include (unrestricted stock, quality inspection stock, purchase orders, production orders, planned orders)
2. **Checking rule** (assigned per SD document type via OVZ2) -- defines WHEN and HOW the check runs for this transaction type

The combination of checking group + checking rule determines the ATP scope. If either is blank, no availability check runs.

### What MM Provides

The ATP engine reads MM data to calculate available quantity:

- **Current stock:** Unrestricted stock from MARD (storage location) and MARC (plant level)
- **Planned receipts:** Purchase orders, production orders, planned orders from MRP tables (MDBS/MDPS)
- **Existing demand:** Other sales orders, deliveries, dependent requirements already consuming stock

The result is a confirmed quantity and confirmed date written to the schedule line (VBEP-BMENG = confirmed quantity).

### Check Types

| Check Type | Scope | Use Case |
|-----------|-------|----------|
| Stock check only (01) | Current unrestricted stock | Conservative -- only confirms against stock on hand |
| Stock + planned receipts (02) | Stock plus all planned supply elements | Standard -- considers incoming POs and production orders |
| Delivery scheduling | Adds transportation lead time to material availability | Full check including shipping time to customer |

See `modules/sd/config-spro.md` Section Availability Check (OVZ2) for SPRO-level configuration of checking groups and checking rules.

---

## Goods Issue for Delivery (PGI)

PGI is the central MM-SD-FI handoff for inventory and cost of goods sold. It is the moment when SD triggers an MM inventory reduction and an FI accounting posting.

### Trigger

Shipping Clerk clicks "Post Goods Issue" in VL02N. The system posts movement type 601 (goods issue for delivery).

### MM Consequence

- **Stock reduced:** MARD unrestricted stock quantity decreases by the delivery quantity
- **Material document created:** MKPF header + MSEG line items (delivery number referenced in MSEG)
- **Delivery status updated:** LIPS goods issue status = C (completely processed)

### FI Consequence (via OBYC)

Movement type 601 triggers OBYC account determination:

- **Dr COGS:** GBB modifier VAX (no CO account assignment) or VAY (with CO account assignment) + valuation class -> COGS GL account
- **Cr Inventory:** BSX + valuation class -> inventory GL account

The amount is at standard price (S-price materials) or moving average price (V-price materials).

### Document Links

```
Delivery (VL02N, LIKP/LIPS) -> Material Document (MKPF/MSEG) -> FI Accounting Document (BKPF/BSEG)
```

All three documents are cross-referenced. The material document number is stored in the delivery item (LIPS). The FI document number is stored in the material document (MSEG-BELNR_FI).

See `modules/mm/integration.md` Section 1 for the full MIGO/OBYC walkthrough (movement type 601 in the catalog). See `modules/sd/integration.md` Section 3 for the PGI COGS trace from the SD perspective.

> **PGI reversal:** Movement type 602 reverses the 601 posting with opposite Dr/Cr. Inventory is restocked, COGS is reversed. Accessible via VL02N -> Post Goods Issue -> Reverse.

---

## Returns

Returns is the full reverse of the O2C cycle. Each step below shows which module owns the step, what document is created, and what crosses the module boundary.

### Step-by-Step Reverse Trace

**Step 1: SD Return Order** (Module: SD)
Create sales order in VA01 with document type RE. Enter customer and reference the original order or billing document. Item category REN (returns) is proposed by item category determination.

- **Document created:** Sales order (VBAK/VBAP) with return-specific item category
- **Module boundary:** None yet -- this is a pure SD document

**Step 2: Return Delivery** (Module: SD)
Create return delivery in VL01N referencing the returns order. Delivery type LR (returns delivery) is proposed by copy control. This represents expected incoming goods from the customer.

- **Document created:** Delivery document (LIKP/LIPS) with return delivery type LR
- **Module boundary:** None yet -- delivery document is SD-owned

**Step 3: Goods Receipt of Returns** (Module: SD -> MM -> FI)
Post goods receipt for the return delivery via VL02N or MIGO with reference to the return delivery. Movement type 651 (returns from customer).

- **Document created:** Material document (MKPF/MSEG)
- **MM consequence:** MARD unrestricted stock increases by the returned quantity
- **FI consequence:** OBYC posts Dr Inventory (BSX) / Cr COGS reversal (GBB) -- reverses the original 601 posting
- **Module boundary:** SD triggers the GR; MM processes the stock update; FI records the accounting entry

**Step 4: Credit Memo** (Module: SD -> FI)
Create billing document in VF01 from the returns order. Billing type RE (returns credit) creates a credit memo.

- **Document created:** Billing document (VBRK/VBRP) + FI accounting document (BKPF/BSEG)
- **FI consequence:** VKOA posts Dr Revenue (ERL) / Cr Customer -- reduces the customer's receivable balance
- **Module boundary:** SD billing triggers the FI revenue reversal posting

### Returns Document Flow

```
Return Order (VA01 RE) -> Return Delivery (VL01N LR) -> GR (651, MKPF/MSEG) -> Credit Memo (VF01 RE, VBRK -> BKPF)
     [SD]                      [SD]                     [SD -> MM -> FI]              [SD -> FI]
```

See `modules/sd/processes.md` Section 2 (Returns) for the full SD-side process narrative.

---

## Consignment

Consignment is a multi-step MM-SD process where stock is placed at the customer site but remains company-owned until the customer withdraws it. Each step has distinct movement types and different billing implications. Customer consignment stock is tracked in MM at the storage location level with special stock indicator W.

### Consignment Movement Types

| Step | Doc Type | Movement Type | Stock Change | Billing | Revenue |
|------|----------|---------------|-------------|---------|---------|
| Fill-Up | KB | 631 | Unrestricted -> consignment at customer (W) | No | No -- goods still company-owned |
| Issue | KE | 633 | Consignment at customer -> sold | Yes | Yes -- revenue recognition point |
| Returns | KA | 634 | Returned after issue -> consignment at customer | Credit memo | Reverses revenue |
| Pickup | KR | 632 | Consignment at customer -> unrestricted | No | No -- goods returned to own stock |

### Integration Handoffs

- **Fill-Up (631):** SD order type KB triggers delivery and PGI with movement type 631. MM reduces unrestricted stock and creates consignment stock at the customer (special stock W). No FI revenue posting -- the goods remain on the company's balance sheet as inventory. No billing document.

- **Issue (633):** SD order type KE triggers the critical handoff. Movement type 633 removes consignment stock at the customer. This is the revenue recognition point -- billing occurs, creating an FI document via VKOA (Dr Customer / Cr Revenue). OBYC posts Dr COGS / Cr Inventory for the cost side.

- **Returns (634):** SD order type KA returns goods that were previously issued (633). Movement type 634 puts stock back into consignment at customer. Credit memo reverses the revenue posting.

- **Pickup (632):** SD order type KR retrieves unsold consignment stock. Movement type 632 moves stock from consignment at customer back to unrestricted. No billing, no revenue impact.

> **Key integration point:** Billing and revenue recognition occur ONLY on consignment issue (633). All other consignment movements are inventory reclassifications with no revenue impact. This is the critical handoff between MM inventory management and SD billing.

See `modules/sd/processes.md` Section 6 (Consignment) for the SD-side process narrative.

---

## Stock Transport Orders (STO)

Stock transport orders use a purchase order (PO type UB) to transfer stock between plants. When the plants are in different company codes, intercompany billing is triggered through SD.

### Basic Flow

- **PO creation:** ME21N with document type UB. Receiving plant creates PO against the supplying plant.
- **Goods issue at sending plant:** Movement type 641 reduces stock at the issuing plant.
- **Goods receipt at receiving plant:** Movement type 101 increases stock at the receiving plant.

### Variants

| Variant | Steps | In-Transit Stock | SD Involvement |
|---------|-------|-----------------|----------------|
| One-step (direct) | Single posting: 641 GI + 101 GR simultaneously | No | No |
| Two-step (with in-transit) | Separate GI (641) and GR (101) | Yes -- stock in transit between postings | No |
| Delivery-based STO | SD delivery document (VL10B) created for shipping leg | Depends on config | Yes -- delivery note for transportation |

### Cross-Company-Code STO

When the sending and receiving plants belong to different company codes, the STO triggers intercompany billing:

- The supplying plant ships via an SD delivery document
- Intercompany billing creates an invoice between the two company codes
- FI documents are created in both company codes (intercompany receivable/payable)

See `modules/mm/processes.md` for procurement-side STO detail. See `modules/sd/sd-advanced.md` Example 8 for the intercompany billing FI posting.

---

## Third-Party Processing

In third-party processing, the company takes the customer order in SD but the vendor ships directly to the customer. No goods movement passes through the company's own warehouse.

### Integration Flow

1. **SD order** (VA01): Item category TAS (third-party) is determined. System automatically creates a purchase requisition in MM.
2. **MM purchase order** (ME21N): Buyer converts the auto-generated PR to a PO. Delivery address on the PO is the customer's ship-to address.
3. **Vendor ships directly to customer:** No delivery document created in SD. No MIGO goods receipt against own inventory.
4. **Vendor invoice** (MIRO): AP Accountant posts the vendor invoice. Goods receipt is statistical -- no physical inventory movement at the company's plant.
5. **Customer billing** (VF01): Order-related billing (not delivery-related). FI posts Dr Customer / Cr Revenue via VKOA.

### Key Integration Points

- **No inventory posting:** Movement types 101/601 do NOT fire. There is no stock in the company's warehouse. Only financial postings occur.
- **SD triggers MM:** The sales order automatically creates the purchase requisition -- this is the SD-to-MM handoff.
- **Two independent invoices:** MIRO for the vendor (MM -> FI); VF01 for the customer (SD -> FI). The margin is the difference.

See `modules/sd/processes.md` Section 7 (Third-Party Processing) for the full SD-side narrative.

---

## Subcontracting (SD Triggers MM)

When an SD sales order creates demand for a finished good that requires subcontracting, MRP generates a subcontracting purchase requisition. The company sends components to the subcontractor and receives finished goods back.

### Integration Flow

1. **SD order** creates demand for the finished good
2. **MRP** (MD01/MD02) generates a subcontracting PR based on the material's procurement type and special procurement key
3. **Component transfer** (movement type 541): Components sent to subcontractor. Stock reclassified from unrestricted to subcontracting stock (special stock O). No FI posting -- this is a stock type change, not a valuation event.
4. **Finished goods receipt** (MIGO, movement type 101 against subcontracting PO): Finished goods received into inventory. Simultaneously, movement type 543 fires automatically to consume the components from subcontracting stock.

### FI Postings

- **541 (components out):** No FI posting. Stock reclassification only.
- **101 (finished goods in):** Dr Inventory (BSX) / Cr GR/IR Clearing (WRX) -- standard GR posting
- **543 (component consumption, automatic):** Dr Subcontracting Consumption (GBB/VBO) / Cr Inventory (BSX) -- components consumed

See `modules/mm/processes.md` for procurement-side subcontracting detail. See `modules/mm/mm-advanced.md` Example 4 for the full 541/543 worked example with Dr/Cr entries.

---

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on MM-SD Integration |
|----------------|----------------|-----------------------------|
| Basic ATP check (OVZ2 checking groups) | Advanced Available-to-Promise (aATP) available | Enhanced ATP with rule-based allocation, product substitution; basic ATP still works |
| Material documents in MKPF/MSEG | Single MATDOC table | PGI (601), returns GR (651), consignment (631-634), STO (641) all write to MATDOC instead of MKPF/MSEG; same OBYC determination logic |
| Consignment movement types 631-634 | Same movement types | Underlying tables change (MATDOC); business process and billing trigger unchanged |
| STO with optional SD delivery | Delivery-based STO enhanced with Advanced Shipping | More shipping options; basic STO logic unchanged |
| Third-party item category TAS | Same item category | Fiori apps available for approval workflows; core process unchanged |
| Subcontracting movement types 541/543 | Same movement types | MATDOC replaces MKPF/MSEG; component consumption logic unchanged |
| NACE output for delivery notes | BRF+ output management | Delivery note output framework changes; PGI posting unchanged |
