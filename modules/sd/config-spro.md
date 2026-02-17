---
module: sd
content_type: config-spro
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# Sales & Distribution — SPRO/IMG Configuration

> ECC 6.0 reference. Configuration paths verified against SPRO transaction. Each step shows the IMG path and direct T-code shortcut where available. The condition technique (pricing section) is the foundational framework reused by output determination, account determination, text determination, and rebates.

## 1. Enterprise Structure

### Step 1: Define Sales Organization (OVXB)
**IMG Path:** Enterprise Structure > Definition > Sales and Distribution > Define, Copy, Delete, Check Sales Organization
Create or copy sales organizations. Each sales org is assigned to exactly one company code.

### Step 2: Define Distribution Channel (OVXI)
**IMG Path:** Enterprise Structure > Definition > Sales and Distribution > Define, Copy, Delete, Check Distribution Channel
Distribution channels represent how products reach customers (wholesale, retail, direct).

### Step 3: Define Division (OVXH)
**IMG Path:** Enterprise Structure > Definition > Sales and Distribution > Define, Copy, Delete, Check Division
Divisions segment the product portfolio (e.g., pumps, motors, services).

### Step 4: Assign Sales Organization to Company Code (OVXK)
**IMG Path:** Enterprise Structure > Assignment > Sales and Distribution > Assign Sales Organization to Company Code
Many-to-one: multiple sales orgs can share a company code.

### Step 5: Assign Distribution Channel to Sales Organization (OVXG)
**IMG Path:** Enterprise Structure > Assignment > Sales and Distribution > Assign Distribution Channel to Sales Organization

### Step 6: Assign Division to Sales Organization (OVXA)
**IMG Path:** Enterprise Structure > Assignment > Sales and Distribution > Assign Division to Sales Organization

### Step 7: Set Up Sales Area
**IMG Path:** Enterprise Structure > Assignment > Sales and Distribution > Set Up Sales Area
**Sales Area = Sales Org + Distribution Channel + Division.** This is the key organizational unit for SD. Pricing procedures, output, partners, and customer master data are all maintained at the sales area level.

### Step 8: Assign Sales Office/Sales Group (optional)
**IMG Path:** Enterprise Structure > Definition > Sales and Distribution > Maintain Sales Office / Maintain Sales Group
Sales offices and groups are optional subdivisions for sales team management.

### Step 9: Define Shipping Point (OVXD)
**IMG Path:** Enterprise Structure > Definition > Logistics Execution > Define, Copy, Delete, Check Shipping Points
Each shipping point is assigned to one plant.

### Step 10: Assign Shipping Point to Plant (OVXC)
**IMG Path:** Enterprise Structure > Assignment > Logistics Execution > Assign Shipping Point to Plant
Shipping point determination at order/delivery time uses: shipping condition (customer) + loading group (material) + plant > shipping point.

---

## 2. Sales Document Types & Item Categories

### Step 1: Define Sales Document Types (VOV8)
**IMG Path:** Sales and Distribution > Sales > Sales Documents > Sales Document Header > Define Sales Document Types
**T-code:** VOV8

Key fields per document type:
- **Document type** — OR (standard), RE (returns), CR (credit memo request), DR (debit memo request), CS (cash sale), RO (rush order), KB-KE-KR-KA (consignment), L2 (scheduling agreement), CQ (quantity contract), WK1 (value contract)
- **Number range** — internal (auto-assigned) or external (user-specified)
- **Item category group default** — proposes item category group if not from material master
- **Delivery type** — default delivery document type (LF for standard, LR for returns)
- **Billing type** — default billing type (F2 for invoice, RE for returns credit)
- **Pricing procedure (doc)** — document pricing procedure, input to OVKK determination
- **Credit check** — credit group assignment (blank = no check, 01 = sales order, 02 = delivery)

### Step 2: Assign Number Ranges (OVAZ/VN01)
**IMG Path:** Sales and Distribution > Sales > Sales Documents > Sales Document Header > Define Number Ranges for Sales Documents
**T-code:** VN01

### Step 3: Define Item Categories (VOV7)
**IMG Path:** Sales and Distribution > Sales > Sales Documents > Sales Document Item > Define Item Categories
**T-code:** VOV7

Key fields per item category:
- **Item type** — controls stock relevance, pricing, billing
- **Billing relevance** — A (delivery-related), B (order-related), blank (not billable)
- **Pricing** — X (pricing active), blank (no pricing)
- **Schedule line allowed** — controls whether schedule lines exist
- **Special stock** — W (consignment), blank (normal)
- **Business item** — relevant for returns, free goods

Standard item categories: TAN (standard), TANN (free of charge), TAX (text item), TAS (third-party), REN (returns), KBN (consignment fill-up), KEN (consignment issue).

### Step 4: Define Schedule Line Categories (VOV6)
**IMG Path:** Sales and Distribution > Sales > Sales Documents > Schedule Lines > Define Schedule Line Categories
**T-code:** VOV6

Key fields: movement type (601 for delivery GI, 631 for consignment issue), delivery block, availability check.
Standard schedule lines: CP (standard with ATP), CN (no ATP), DL (returns).

### Step 5: Item Category Determination (OVLP)
**IMG Path:** Sales and Distribution > Sales > Sales Documents > Sales Document Item > Assign Item Categories
**T-code:** OVLP

**4-key determination logic:**
1. **Sales document type** — from VOV8 (e.g., OR, RE)
2. **Item category group** — from material master MVKE-MTPOS (e.g., NORM, BANS, LUMP)
3. **Usage** — from order data (e.g., FREE for free goods, LEIH for loan, blank for standard)
4. **Higher-level item category** — for sub-items in BOM explosions (blank if top-level)

The system looks up the combination in OVLP table and proposes the item category. If no entry exists, the order line item cannot be created.

> **CRITICAL:** The item category group (key 2) comes from the **material master MVKE-MTPOS**, NOT from the sales document type. This is the most common item category determination error — if the material is missing MVKE-MTPOS, the determination fails with "item category not found."

---

## 3. Pricing (Condition Technique)

The condition technique is the central architectural framework in SD. It drives pricing, output determination, account determination, text determination, and rebates through a common 4-layer model:

**Layer 1 — Condition Tables (V/06):** Define what key fields to use for looking up condition records.
**Layer 2 — Access Sequences (V/07):** Define the search order — which condition tables to check and in what priority.
**Layer 3 — Condition Types (V/08):** Define the pricing element behavior (price, discount, surcharge, tax) and assign the access sequence.
**Layer 4 — Procedures (V/09):** Define the calculation schema — which condition types apply, in what order, with subtotals and formulas.

This 4-layer model is the SAME framework for pricing (V/06-V/09), output determination (NACE), and other condition-based functions. Learn it once, apply everywhere.

### Step 1: Define Condition Tables (V/06)
**IMG Path:** Sales and Distribution > Basic Functions > Pricing > Pricing Control > Define Condition Tables
**T-code:** V/06

Each condition table defines a key combination (e.g., table 004 = Customer/Material, table 005 = Customer/Material Group). The table number is used in access sequences.

### Step 2: Define Access Sequences (V/07)
**IMG Path:** Sales and Distribution > Basic Functions > Pricing > Pricing Control > Define Access Sequences
**T-code:** V/07

Access sequences define the search strategy: check condition table A first, then B, then C. First hit wins (if exclusive indicator is set). Access sequences are assigned to condition types.

### Step 3: Define Condition Types (V/08)
**IMG Path:** Sales and Distribution > Basic Functions > Pricing > Pricing Control > Define Condition Types
**T-code:** V/08

Key fields: calculation type (A=percentage, B=fixed amount, C=quantity), condition class (A=discount, B=price), plus/minus, access sequence assignment, condition category, rounding rule.

### Step 4: Define Pricing Procedures (V/09)
**IMG Path:** Sales and Distribution > Basic Functions > Pricing > Pricing Control > Define and Assign Pricing Procedures > Maintain Pricing Procedures
**T-code:** V/09

The pricing procedure is the calculation schema. Key columns per step: Step, Counter, Condition Type, Description, From, To, Manual, Required, Statistical, Print, Subtotal, Requirement, Alternative Calculation Type, Alternative Condition Base Value.

Subtotal fields (KOMP structure) control intermediate calculations: e.g., net value = base price - discounts; tax base = net value.

### Step 5: Pricing Procedure Determination (OVKK)
**IMG Path:** Sales and Distribution > Basic Functions > Pricing > Pricing Control > Define and Assign Pricing Procedures > Define Pricing Procedure Determination
**T-code:** OVKK

**Determination logic:** Sales Area + Document Pricing Procedure (from sales document type VOV8) + Customer Pricing Procedure (from customer master KNVV-KALKS) > Pricing Procedure.

> **Gotcha:** If no entry exists in OVKK for the three-key combination, the sales order will have NO pricing procedure and NO prices. This is one of the most common SD go-live errors. Always verify the OVKK entry after creating a new document type or customer pricing procedure.

---

## 4. Copy Control

Copy control governs how data flows between SD documents (order > delivery > billing). It defines WHAT is copied, WHEN copying is allowed (requirements), and HOW data is transferred (routines).

### VTAA — Order to Order Copy Control
**IMG Path:** Sales and Distribution > Sales > Maintain Copy Control for Sales Documents
**T-code:** VTAA

Used for: quotation > order, contract > release order, returns > credit memo request. Header and item level settings.

### VTLA — Order to Delivery Copy Control
**IMG Path:** Sales and Distribution > Shipping > Maintain Copy Control for Deliveries
**T-code:** VTLA

Used for: sales order > outbound delivery. Controls whether partial deliveries are allowed and how quantities are proposed.

### VTFL — Delivery to Billing Copy Control
**IMG Path:** Sales and Distribution > Billing > Billing Documents > Maintain Copy Control for Billing Documents
**T-code:** VTFL

Used for: delivery > invoice, delivery > pro forma. Most critical copy control — controls billing quantity source and pricing behavior.

### VTAF — Billing to Order Copy Control (Cancellation/Credit)
**IMG Path:** Sales and Distribution > Billing > Billing Documents > Maintain Copy Control from Billing Document to Sales Document
**T-code:** VTAF

Used for: billing document > credit memo request, billing cancellation scenarios.

**Key Fields at Item Level (all copy control T-codes):**

| Field | Description | Common Values |
|-------|-------------|---------------|
| Requirement | ABAP routine checked at copy time — controls WHEN copying is allowed | 001 (header: order has deliveries), 002 (item: complete reference) |
| Data Transfer Routine | ABAP routine controlling HOW fields are mapped during copy | 001 (header), 002 (item), varies by scenario |
| Pricing Type | Controls pricing recalculation at copy | B (carry over and redetermine), C (copy pricing), D (redetermine from scratch), G (copy and redetermine freight) |
| Copy Quantity | What quantity to propose | MNGGS field: from delivery qty, from order qty |
| Billing Quantity | Source of billing quantity | E (from delivery), blank (from order) |

> **CRITICAL:** Requirements and data transfer routines are ABAP routines (checked at runtime). If the requirement routine returns false, the system refuses to copy. If the data transfer routine is missing or wrong, fields are not mapped. Always check BOTH header and item level — item-level settings override header behavior.

---

## 5. Delivery

### Step 1: Define Delivery Types (OVLK)
**IMG Path:** Sales and Distribution > Shipping > Deliveries > Define Delivery Types
**T-code:** OVLK

Standard types: LF (outbound delivery), LR (returns delivery), NL (replenishment delivery). Key fields: number range, order reference (mandatory/optional), goods movement type at PGI.

### Step 2: Shipping Point Determination
**IMG Path:** Sales and Distribution > Shipping > Basic Shipping Functions > Shipping Point Determination > Assign Shipping Points
**T-code:** OVXC (assignment table)

**Determination logic:** Shipping Condition (from customer master KNVV-VSBED) + Loading Group (from material master MARC-LADGR) + Plant > Shipping Point.

If no entry exists, delivery creation fails with "shipping point could not be determined."

### Step 3: Route Determination (OVTC)
**IMG Path:** Sales and Distribution > Shipping > Basic Shipping Functions > Routes > Define Routes / Route Determination
**T-code:** OVTC

Route determination: country of departure + shipping point + transportation group + country of destination + transportation zone > route. Routes drive lead time calculation and freight pricing.

### Step 4: Picking and Packing
**IMG Path:** Sales and Distribution > Shipping > Picking > Define Picking / Packing
Picking is confirmed in VL02N by entering picked quantities. Warehouse Management (WM) integration generates transfer orders automatically if WM is active. Packing uses handling unit management (HU).

---

## 6. Billing

### Step 1: Define Billing Types (VOFA)
**IMG Path:** Sales and Distribution > Billing > Billing Documents > Define Billing Types
**T-code:** VOFA

Standard types: F2 (invoice), G2 (credit memo), L2 (debit memo), RE (returns credit), S1 (cancellation), F5 (pro forma). Key fields: number range, transaction group, account determination (SD > FI posting rules), cancel billing type.

### Step 2: Revenue Account Determination (VKOA — brief)
**IMG Path:** Sales and Distribution > Basic Functions > Account Assignment / Costing > Revenue Account Determination > Define Access Sequences and Account Determination Types

Revenue account determination uses the condition technique (same 4-layer model as pricing) to find the GL account for billing postings. The standard access sequence checks:
1. Customer account assignment group (KTGRD from KNVV)
2. Material account assignment group (KTGRM from MVKE)
3. Account key (from pricing procedure — ERL for revenue, ERS for sales deductions, MWS for tax)

> Full VKOA deep-dive (worked examples, debugging) is documented in `modules/fi/account-determination.md` and expanded in Phase 8 (SD Advanced). This section provides the framework entry point only.

### Step 3: Billing Plan Types (optional)
**IMG Path:** Sales and Distribution > Billing > Billing Plan > Define Billing Plan Types
For milestone billing and periodic billing scenarios. Define billing dates, rules, and percentage splits.

---

## 7. Output Determination

Output determination in ECC 6.0 uses the **condition technique** (same 4-layer framework documented in the Pricing section above). The only difference is the application area.

### Step 1: Access NACE
**IMG Path:** SPRO > Cross-Application Components > Output Control > Output Determination
**T-code:** NACE

Select the application to configure:
- **V1** — Sales document outputs (order confirmations)
- **V2** — Shipping document outputs (delivery notes, packing lists)
- **V3** — Billing document outputs (invoices, credit memos)
- **V4** — Transportation outputs

### Step 2: Maintain Output Types
Within each application in NACE, define output types (e.g., BA00 for order confirmation, LD00 for delivery note, RD00 for invoice). Each output type has:
- **Access sequence** — search strategy for finding output condition records
- **Default values** — medium (print/fax/EDI/email), timing, partner function
- **Print program and form** — SAPscript form, Smart Form, or PDF form name

### Step 3: Assign Output Determination Procedure
Within NACE, assign the output determination procedure to the document type (e.g., V10000 procedure assigned to order type OR for application V1). The procedure lists which output types are checked and in what order.

> **S/4HANA Note:** S/4HANA replaces NACE-based output with BRF+ output management framework. NACE configuration still works in S/4HANA for legacy/custom outputs, but new implementations should use BRF+. All guidance in this file is for ECC 6.0 NACE-based output.

---

## 8. Supporting Functions

### Partner Determination
**IMG Path:** Sales and Distribution > Basic Functions > Partner Determination > Set Up Partner Determination
Define partner function groups and mandatory/optional partner functions per document type. Standard partner functions: AG (sold-to), WE (ship-to), RE (bill-to), RG (payer), VE (sales rep). Partner determination procedure assigned to document type controls which partner functions are required.

### Text Determination
**IMG Path:** Sales and Distribution > Basic Functions > Text Control > Define Text Types / Define Access Sequences for Texts
Uses the condition technique. Text types (header text, item text, delivery text) are determined by text determination procedures assigned to document types. Texts copy via copy control settings.

### Incompletion Procedures
**IMG Path:** Sales and Distribution > Basic Functions > Log of Incomplete Items > Define Incompletion Procedures
**T-code:** V_20 (assign to document types), OVA2 (define procedures)
Define which fields must be filled before a document can be saved or processed. Warning (allows save) vs. Error (blocks save) status per field. Separate procedures for header, item, schedule line, and partner data.

### Availability Check (OVZ2)
**IMG Path:** Sales and Distribution > Basic Functions > Availability Check and Transfer of Requirements > Availability Check > Availability Check with ATP Logic > Define Checking Groups
**T-code:** OVZ2

Define checking groups that control:
- **What stock is included** — unrestricted, quality inspection, blocked, in-transit
- **What supply is included** — purchase orders, production orders, planned orders, purchase requisitions
- **What demand is included** — sales orders, deliveries, dependent requirements

Checking group is assigned to material (MARC-MTVFP) and combined with checking rule (from document type) to determine the availability check scope.

> ATP (Available-to-Promise) and credit check are independent controls. ATP checks material availability; credit check examines customer creditworthiness. Do not conflate them.

### Credit Management Configuration (Brief)
**IMG Path:** Sales and Distribution > Basic Functions > Credit Management/Risk Management
**T-code:** OVA8

Key config steps:
1. **Define credit control area** — typically 1:1 with company code
2. **Assign credit control area to company code** — OB38
3. **Define credit groups** — group document types for credit checking (e.g., 01 = sales orders, 02 = deliveries)
4. **Assign sales documents to credit groups** — links VOV8 document types to credit groups
5. **Define automatic credit check rules** — static check (credit limit), dynamic check (open items + open orders), max document value

> Deep credit management configuration (risk categories, credit exposure calculation, workflow integration) defers to Phase 8 (SD Advanced).

---

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|--------|
| NACE condition-based output | BRF+ output management | New output framework |
| FD32 classic credit mgmt | FSCM Credit Management (UKM/OVA8 replaced) | New credit engine |
| Pricing condition technique | Same in S/4 — no change | V/06-V/09 unchanged |
| Classic availability check | Same ATP logic in S/4; also aATP (advanced ATP) | Enhanced options available |
