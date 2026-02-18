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
