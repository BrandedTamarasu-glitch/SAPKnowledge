---
module: mm
content_type: processes
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Materials Management — Business Processes

> ECC 6.0 reference. Each process documented as numbered narrative followed by summary table (Step | Activity | T-code | Role | Output). Roles: Requester, Materials Planner, Purchasing Manager, Buyer, Warehouse Team, AP Accountant, Finance Manager.

## 1. Procure-to-Pay (Standard PO Process)

The Procure-to-Pay (P2P) process covers the complete cycle from purchase requisition through vendor payment. This is the core MM business process and the primary MM-FI integration point.

### Narrative

**Step 1 — Create Purchase Requisition** (Requester / Materials Planner)
Create a purchase requisition in ME51N specifying material, quantity, delivery date, and plant. Set account assignment (cost center, internal order, or WBS element) — this drives CO postings and propagates through the entire P2P chain. Wrong account assignment here propagates to PO, GR, and invoice.

PRs can also be generated automatically by MRP (MD01/MD02) when net requirements calculation identifies a shortfall and the procurement type is external (MARC-BESKZ = E or X).

**Step 2 — Release (Approve) Purchase Requisition** (Purchasing Manager / Budget Owner)
If a release strategy is configured for PRs, the requisition must be approved before conversion to PO. Key T-codes:
- **ME28** — Collective release: shows a list of all PRs/POs pending release for a specific release code. Use for batch approvals.
- **ME29N** — Individual release: release a specific PO by number.

> Release strategy overview: Release strategies use characteristics (total value, material group, plant) to assign approval levels. Configuration detail (release groups, release codes, classification) defers to Phase 6. For Phase 5: know the concept and the T-codes.

**Step 3 — Create Purchase Order** (Buyer / Purchasing Agent)
Convert the approved PR to a PO using one of two methods:
- **ME21N** — Manual PO creation referencing the PR (most common). Buyer can modify quantities, delivery dates, pricing, and vendor selection.
- **ME59N** — Automatic PR-to-PO conversion. Requires source determination: system checks source list (EORD) → purchasing info record (EINE/EINA) → outline agreement. First valid source wins. Without a valid source, ME59N fails.

PO document type NB (standard PO) is the default. The PO may also require its own release strategy approval (separate from the PR release).

**Step 4 — Goods Receipt** (Warehouse Team / Receiving)
Post goods receipt in MIGO: Action = A01 (Goods Receipt), Reference = Purchase Order. Movement type 101 (GR against PO).

FI posting at goods receipt:
- **Dr BSX** (Inventory — stock account) — increases inventory value
- **Cr WRX** (GR/IR Clearing account) — interim account cleared by MIRO
- **Dr PRD** (Price Difference) — fires ONLY for standard price (S) materials when PO price differs from standard price. For moving average price (V) materials, BSX absorbs the full PO price — no PRD posting occurs.

Material document created: MKPF (header) + MSEG (line items). The GR quantity is compared to PO ordered quantity; tolerance controlled by OMGN.

> The GR-Based Invoice Verification flag (LFM1-WEBRE on the vendor master) means that MIRO cannot post the invoice until at least one GR exists for the PO line. This is the three-way match prerequisite.

**Step 5 — Invoice Verification (MIRO) — Three-Way Match** (AP Accountant)
Post the vendor invoice in MIRO (NOT FB60 — FB60 is for non-PO invoices only).

**Three-way match logic:**
MIRO reads the PO (price and quantity terms from EKKO/EKPO) and the GR documents (confirmed receipt quantities from EKBE). The system performs three comparisons:
1. **Invoice quantity vs GR quantity** — tolerance key DQ (and DW if GR qty = 0)
2. **Invoice price vs PO price** — tolerance key PP (and PS for estimated prices)
3. **Invoice amount vs calculated amount** — tolerance keys AN/AP/KW

For each comparison, the system checks against the tolerance limits configured in OMR6:
- If within ALL tolerances: invoice posts automatically → creates FI document
- If ANY tolerance exceeded: invoice is BLOCKED → requires MRBR release
- Exception: **BD tolerance** auto-posts small differences to a tolerance GL account without blocking

FI posting at invoice verification:
- **Dr WRX** (GR/IR Clearing — offsets the GR posting from Step 4)
- **Cr Vendor account** (sub-ledger, hits reconciliation account in GL)

> MIRO is the MM-FI handoff point. From this point forward, the vendor open item lives in FI (visible in FBL1N) and is picked up by the automatic payment program (F110).

> **CRITICAL:** For PO-based credit memos, use MIRO transaction type "Credit Memo" — NOT FB65. Using FB65 bypasses the three-way match, does not update MM tables (EKBE, RSEG), and creates reconciliation breaks between MM and FI.

**Step 6 — Release Blocked Invoices** (AP Accountant / Finance Manager)
If MIRO blocked the invoice due to tolerance exceedance, review the blocking reason in MRBR. Check:
- Was the quantity actually delivered (verify with MB51)?
- Was the price agreed (verify with ME23N PO terms)?
- Is this a known small variance within business policy?

Release in MRBR posts the invoice. Alternatively, the buyer may need to correct the PO or the warehouse may need to correct the GR before releasing.

**Step 7 — Payment** (AP Accountant)
Once the MIRO invoice is posted and the vendor open item appears in FBL1N, it is picked up by the automatic payment program F110.

> **Cross-reference:** F110 is fully documented in `modules/fi/processes.md` (AP Payment Run section). The P2P handoff: MIRO creates the vendor open item → F110 pays it → FBL1N shows cleared status. Do not duplicate the F110 7-step sequence here.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Create purchase requisition | ME51N | Requester / Materials Planner | PR with material, quantity, delivery date, account assignment |
| 2a | Release PR (collective list) | ME28 | Purchasing Manager | Approved PR (release status set) |
| 2b | Release PR (individual) | ME29N | Purchasing Manager | Approved PR |
| 3a | Create PO (manual from PR) | ME21N | Buyer | Purchase order NB with PO number |
| 3b | Create PO (auto from PR) | ME59N | Buyer / System | POs created for all PRs with valid sources |
| 4 | Goods receipt against PO | MIGO (101) | Warehouse Team | Material document; FI posting BSX/WRX/PRD |
| 5 | Invoice verification (three-way match) | MIRO | AP Accountant | FI document; vendor open item; or BLOCKED status |
| 6 | Release blocked invoice | MRBR | AP Accountant / Finance Manager | Invoice posted; vendor open item created |
| 7 | Vendor payment | F110 | AP Accountant | Payment document; vendor cleared (see FI processes.md) |

---

## 2. Outline Agreements (Brief Overview)

Outline agreements are long-term purchasing arrangements. Two types:

### Contracts (ME31K / ME32K / ME33K)

A contract defines terms (price, quantity or value limits, validity period) without specifying delivery dates. Purchase orders are created against the contract to trigger actual procurement (release orders).

- **Quantity Contract (type MK):** Vendor agrees to supply a total quantity at agreed price over validity period
- **Value Contract (type WK):** Vendor agrees to supply up to a total value over validity period

**Release process:** Buyer creates a PO (ME21N) referencing the contract number in the "Agreement" field. The PO draws down the contract's released quantity/value. Track contract utilization via ME33K.

### Scheduling Agreements (ME31L / ME32L)

A scheduling agreement combines the contract with delivery schedule lines. The vendor knows when and how much to deliver — no separate PO is needed. MRP can generate schedule lines automatically.

- **Delivery schedules** are maintained via ME38 (Maintain Schedule Lines) or generated by MRP
- Goods receipt posted with MIGO referencing the scheduling agreement number

> Full outline agreement configuration (release documentation, copy control, condition records) defers to Phase 6.

---

## 3. Physical Inventory Process

Physical inventory verifies that system stock quantities match actual warehouse quantities. SAP supports annual, continuous, and cycle counting methods. This process covers the standard annual physical inventory workflow.

### Narrative

**Step 1 — Create physical inventory document** (Warehouse Team / Materials Planner)
Use MI01 to create a physical inventory document specifying plant, storage location, and posting date. The system generates a count document listing all materials at the selected storage location. Stock can optionally be frozen (posting block) during counting to prevent movements.

**Step 2 — Perform physical count** (Warehouse Team)
Print the count sheets from the physical inventory document. Warehouse staff physically count stock and record results on the count sheets.

**Step 3 — Enter count results** (Warehouse Team)
Use MI04 to enter the actual count quantities against the physical inventory document. For each material, enter the counted quantity. Zero counts must be explicitly entered (not left blank).

**Step 4 — Analyze differences** (Materials Planner / Finance Manager)
Review the difference list (MI20 — Print List of Differences) comparing system stock vs counted stock. Investigate significant variances before posting.

**Step 5 — Post inventory differences** (Materials Planner)
Use MI07 to post the inventory differences. The system creates material documents and FI documents:
- **Surplus (count > system):** Movement type 701 — increases stock (Dr BSX, Cr inventory difference account)
- **Shortage (count < system):** Movement type 702 — decreases stock (Dr inventory difference account, Cr BSX)

The inventory difference account is configured via OBYC transaction key INV.

### Summary Table

| Step | Activity | T-code | Role | Output |
|------|----------|--------|------|--------|
| 1 | Create physical inventory document | MI01 | Warehouse Team / Materials Planner | PI document with material list per storage location |
| 2 | Perform physical count | — (manual) | Warehouse Team | Count sheets with actual quantities |
| 3 | Enter count results | MI04 | Warehouse Team | Count quantities entered against PI document |
| 4 | Analyze differences | MI20 | Materials Planner / Finance Manager | Difference report: system qty vs actual qty |
| 5 | Post inventory differences | MI07 | Materials Planner | Material documents (701/702); FI adjustment postings |
