---
module: cross-module
content_type: e2e-process
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
related_modules:
  - sd
  - fi
  - mm
---

# Order-to-Cash (O2C) — End-to-End Process

> ECC 6.0. Traces the complete sales cycle from sales order through customer payment, highlighting every integration handoff where a document crosses module boundaries. For S/4HANA differences, see the S/4HANA Differences section below.

## Prerequisites

Read these module files for full detail on individual steps:

- `modules/sd/processes.md` -- O2C 6-step narrative with ATP check, credit check, and document flow
- `modules/sd/integration.md` -- VF01 billing trace (5-step revenue/receivable), PGI COGS trace (3-step inventory/COGS)
- `modules/fi/processes.md` -- Month-End Close (AR clearing), Financial Reporting
- `modules/sd/sd-advanced.md` -- VKOA account determination walkthrough with worked billing-to-GL examples and debugging path
- `cross-module/mm-sd-integration.md` -- Availability Check (ATP) detail and Goods Issue for Delivery mechanics (when available)

## Document Chain

```
Sales Order -> Delivery -> PGI (Goods Issue) -> Billing Doc -> FI Acctg Doc -> Payment/Clearing
  VA01          VL01N      VL02N (601)         VF01          (auto)           F-28/F-32
  [SD]          [SD]       [SD -> MM -> FI]    [SD -> FI]    [FI]             [FI]
```

## Process Flow

### Step 1: Sales Order (VA01)

**Module:** SD (with MM availability check handoff)
Sales order created with document type OR (standard). System proposes pricing from condition records (OVKK), partner functions from customer master (KNVP), and payment terms from KNVV. At order save, two automatic checks may fire:

- **ATP check** -- If checking group (MARC-MTVFP) and checking rule are configured, the system checks available stock in MM (MARD/MARC stock, planned receipts, existing demand). Insufficient stock results in partial confirmation or proposed later date.
- **Credit check** -- If configured (OVA8), system compares customer credit exposure against credit limit (FD32). Exceeded limit blocks the order for review via VKM1.

See `modules/sd/processes.md` Section 1, Steps 1-1b for full ATP and credit check detail.

**Integration handoff:** The ATP check is an SD -> MM boundary crossing -- SD reads MM stock data (MARD/MARC) and planned supply (MRP elements) to confirm quantities. No FI document created.

---

### Step 2: Delivery (VL01N)

**Module:** SD
Outbound delivery created from the sales order. System determines shipping point (from shipping condition + loading group + plant via OVXC) and route. Delivery quantities come from confirmed schedule line quantities.
See `modules/sd/processes.md` Section 1, Step 2 for delivery creation detail.

**Integration handoff:** Delivery links back to the sales order via VBFA (document flow). MM reservation may be created for the delivery quantity. No FI document at this point.

---

### Step 3: Post Goods Issue (VL02N, movement type 601)

**Module:** SD -> MM -> FI
Shipping Clerk posts goods issue in VL02N. Movement type 601 (goods issue for delivery). This is a three-module handoff: SD triggers, MM processes the inventory reduction, and FI receives the accounting document.

FI posting (via OBYC, not VKOA):
- **Dr COGS** (from OBYC GBB/VAX or VAY + valuation class) -- cost of goods sold
- **Cr BSX** (Inventory) -- stock account reduced

Material document (MKPF/MSEG) created. Stock quantity reduced in MARD/MARC. Delivery status updates to "goods issue posted."
See `modules/sd/integration.md` Section 3 for the full PGI COGS trace (material document creation, OBYC account determination, FI document creation).

**Integration handoff:** PGI is the cost side of the O2C cycle. COGS is posted at PGI time via OBYC (GBB modifier VAX for standard, VAY with CO account assignment). This is independent of the revenue posting at billing -- they use different account determination frameworks (OBYC vs VKOA) and fire at different process steps.

> **CRITICAL DISTINCTION:** The COGS GL account comes from **OBYC** (GBB/VAX or VAY), NOT from VKOA. VKOA handles the revenue side at billing. Do not confuse them. See `modules/sd/integration.md` Section 3 for detail.

---

### Step 4: Billing (VF01)

**Module:** SD -> FI
Billing document created from the delivery (or from billing due list VF04 for collective processing). Billing type determined by copy control (VTFL). The system executes VKOA account determination to find revenue GL accounts.

FI posting (via VKOA):
- **Dr Customer** (AR sub-ledger -- reconciliation account from KNB1-AKONT)
- **Cr Revenue** (from VKOA ERL determination using KTGRD + KTGRM + account key)
- **Dr/Cr Tax** (output tax from MWST condition type)

See `modules/sd/integration.md` Section 2 for the full VF01 billing trace (billing document creation, VKOA lookup, FI document creation, customer open item, document flow update).

**Integration handoff:** This is the revenue side of the O2C cycle. The FI document is created automatically at billing. The customer open item appears in FBL5N and is picked up by dunning (F150) or cleared by incoming payment (F-28).

---

### Step 5: Customer Payment (F-28)

**Module:** FI
Customer payment received and processed via incoming payment (F-28), automatic clearing (F.13), or lockbox processing. The customer open item created by billing in Step 4 is cleared.
See `modules/fi/processes.md` for AR payment processing context.

**Integration handoff:** None outbound -- payment is FI-internal. The customer open item transitions from BSID (open) to BSAD (cleared).

---

### Step 6: Dunning (F150)

**Module:** FI
If payment is overdue, the dunning program generates dunning notices based on the dunning procedure configured on the customer master (KNB1-MAHNA). Dunning levels escalate with aging.
See `modules/fi/processes.md` for dunning context.

**Integration handoff:** None -- FI-internal collections process. Dunning does not create FI postings (except for interest charges if configured).

---

## Cross-Module Troubleshooting

Common cross-module O2C issues. For module-specific troubleshooting, see `modules/sd/sd-advanced.md` Section 3 and `modules/fi/fi-advanced.md` Troubleshooting.

| Issue | Root Cause | Resolution |
|-------|-----------|------------|
| PGI fails -- account determination error at goods issue | Missing OBYC entry for GBB/VAX (or VAY) + valuation class combination | Check material valuation class (MM03 Accounting 1); check OBYC for GBB + modifier VAX + valuation class; see `modules/mm/mm-advanced.md` Symptom 1 |
| VF01 billing fails -- revenue account determination error | Missing VKOA entry for ERL + KTGRD + KTGRM combination, or KTGRD/KTGRM blank on master data | Check customer KTGRD (KNVV Billing tab) and material KTGRM (MVKE Sales Org 2); see `modules/sd/sd-advanced.md` Symptom 6 |
| Delivery blocked -- no confirmed quantity | ATP check found no stock; schedule line confirmed qty = 0 | Check MD04 for stock/requirements; rework ATP in VA02; see `modules/sd/sd-advanced.md` Symptom 5 |
| COGS posted but no revenue (period mismatch) | PGI posted in period N but billing runs in period N+1 | Post manual accrual (FBS1: Dr Unbilled Receivables / Cr Accrued Revenue); see `modules/sd/integration.md` Section 5b |
| Billing document created but no FI document | Pro forma billing type (F5/F8) used, or billing block active | Check billing type in VF03; pro forma does not post to FI by design; see `modules/sd/sd-advanced.md` Symptom 7 |

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact on O2C Flow |
|----------------|----------------|-------------------|
| Material documents at PGI in MKPF/MSEG | Single MATDOC table | PGI creates MATDOC instead of MKPF/MSEG; OBYC determination unchanged |
| Customer master KNA1/KNB1/KNVV | Business Partner (BP, BUT000) | Billing posts to BP reconciliation account; customer maintenance via BP |
| Classic GL or New GL | Universal Journal (ACDOCA) | All O2C FI postings (COGS and revenue) go to ACDOCA |
| Material Ledger optional | Material Ledger mandatory | COGS at PGI may use actual cost instead of standard; real-time COGS split available |
| NACE output for billing | BRF+ output management | Billing output format changes; FI posting unchanged |
| FD32 classic credit management | FSCM/UKM credit management | New credit engine; billing-to-FI posting unchanged |
| VKOA still drives revenue account determination | Same VKOA in S/4 | No change; CDS views enable real-time revenue reporting |
