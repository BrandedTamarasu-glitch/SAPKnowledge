---
module: fi
content_type: account-determination
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-16
---

# Financial Accounting — Account Determination

> ECC 6.0 reference. Account determination maps business transactions to GL accounts automatically. This file covers the OBYC framework (MM integration), VKOA framework (SD integration overview), and FI-only automatic postings.

---

## 1. How Account Determination Works (OBYC Framework)

### Determination Path

When a goods movement posts in MIGO (or background via MFBF), the system follows this chain to arrive at a GL account:

```
Movement type (MIGO/MFBF)
    → OMJJ: which transaction keys fire for this movement type
        → OBYC: transaction key + valuation class [+ account modifier]
            → GL account
```

Each element in this path:

**Movement type** — The trigger event. Examples:
- 101 = Goods receipt against purchase order
- 102 = Reversal of goods receipt
- 261 = Goods issue to production order
- 262 = Reversal of goods issue
- 551 = Scrapping / destruction of stock
- 601 = Goods issue for delivery (SD)

**OMJJ** — The movement type configuration transaction. For each movement type, OMJJ defines which OBYC transaction keys are triggered and whether the posting is a debit or credit. This is where you read "movement type 101 triggers BSX (Dr inventory) and WRX (Cr GR/IR clearing)." You typically read OMJJ during analysis; you do not reconfigure it during normal implementations.

**Transaction keys** — The codes in OBYC that link to GL accounts. Core keys relevant to MM postings:

| Key | Name | What It Posts |
|-----|------|---------------|
| BSX | Inventory posting | Stock / inventory balance sheet account |
| WRX | GR/IR clearing | Goods receipt / invoice receipt clearing account |
| PRD | Price differences | Variance between PO price and standard price |
| GBB | Offsetting entries for inventory postings | Consumption, scrapping, COGS |
| KON | Consignment payables | Liability to vendor for consignment stock withdrawals |
| AKO | Consignment liabilities correction | Correction postings for consignment |
| EIN | Purchasing account | Country-specific (DE/AT) — purchasing value per account method |

**Valuation class** — From the material master, Accounting 1 view (field BKLAS). Groups materials into categories so the same transaction key can post to different GL accounts depending on what type of material is involved. Representative examples:

| Valuation Class | Typical Material Type |
|----------------|----------------------|
| 3000 | Raw materials |
| 3100 | Semi-finished goods |
| 7920 | Finished goods |
| 6000 | Spare parts / consumables |

**Account modifier** — Only three transaction keys support account modifiers: GBB, PRD, and KON. BSX and WRX do NOT use account modifiers — they determine the GL account from the valuation class alone. The account modifier sub-classifies the posting within a transaction key, allowing one transaction key to post to multiple different GL accounts depending on the business context.

---

### How to Navigate OBYC

**Reading current config (diagnostic path):**
T-code OBYC → Enter chart of accounts (if prompted) → Enter or select transaction key (e.g., BSX) → The system displays a table showing: chart of accounts | valuation class | (account modifier if applicable) | GL debit account | GL credit account. Use this to answer "what GL account does BSX post to for valuation class 3000 in chart of accounts INT?"

**Setting up during implementation (setup path):**
T-code OBYC → Select transaction key → New Entries (F5) → Enter:
- Chart of accounts (e.g., INT)
- Valuation class (e.g., 3000)
- Account modifier (only for GBB, PRD, KON — leave blank for BSX, WRX)
- Debit GL account
- Credit GL account (for clearing accounts like WRX, both Dr and Cr are the same account)

Save. The assignment takes effect immediately for new postings.

> **Note on valuation grouping codes:** In multi-valuation-area setups (multiple company codes sharing a chart of accounts), a valuation grouping code may be inserted between the chart of accounts and valuation class in OBYC. This is configured in OMWD and OMWM. For single-company-code implementations this level is not relevant.

---

## 2. MM Goods Receipt — Worked Example (Movement Type 101)

### Transaction Keys That Fire for Movement Type 101

| Transaction Key | Dr/Cr | What It Posts | Account Modifier Used? | GL Account Determined By |
|----------------|-------|---------------|----------------------|--------------------------|
| BSX | Dr | Inventory / stock account | No | Valuation class only |
| WRX | Cr | GR/IR clearing account | No | Valuation class only |
| PRD | Dr or Cr | Price difference (standard price only) | Optional | Valuation class (+ modifier if configured) |

**Important note on PRD:** PRD fires for movement type 101 ONLY when the material has standard price control (price control indicator **S** in the material master Accounting 1 view). For moving average price materials (price control indicator **V**), the price difference is absorbed directly into BSX — the stock account value adjusts to the actual PO price, and no separate PRD posting occurs. This is one of the most common account determination questions in FI-MM integration.

### Movement Type 101 — Standard Price Material Worked Example

Scenario: Goods receipt for purchase order. Raw material (valuation class 3000). Standard price 100.00 EUR. PO price 105.00 EUR. Quantity: 1 unit.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Inventory — representative example) | 100.00 | Dr | BSX: valuation class 3000 → GL 140000 |
| 191100 (GR/IR Clearing — representative example) | 105.00 | Cr | WRX: valuation class 3000 → GL 191100 |
| 310000 (Price Differences — representative example) | 5.00 | Dr | PRD: standard price variance (PO 105 - standard 100) |

> **Note:** Account numbers are representative examples. Your implementation will have different GL accounts based on your chart of accounts and OBYC configuration. The determination logic — which transaction key maps to which GL account — is what matters.

**Balancing check:** Dr 100 + Dr 5 = 105 = Cr 105. Document balances.

### Movement Type 101 — MAP Material Worked Example

Scenario: Same setup but material has moving average price (price control V). Current MAP = 98.00 EUR. PO price = 105.00 EUR.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 140000 (Inventory — representative example) | 105.00 | Dr | BSX: MAP material — stock value posts at PO price |
| 191100 (GR/IR Clearing — representative example) | 105.00 | Cr | WRX: clears at PO price |

No PRD posting for MAP materials. The moving average price in the material master is recalculated after the GR.

### Movement Type 102 — GR Reversal

Movement type 102 is the reversal of 101. The same OBYC transaction keys fire (BSX, WRX, PRD if applicable) with the exact opposite debit/credit signs. The system generates a reversal document that mirrors the original 101 document. No special OBYC configuration needed — it inherits from 101.

---

## 3. MM Goods Issue — Worked Examples (Movement Types 261, 551)

### GBB Account Modifier Reference

GBB is the most important transaction key for goods issue postings because it handles the offsetting (consumption/COGS/loss) side of inventory reductions. The account modifier determines which specific expense or COGS account receives the posting.

| Modifier | Purpose | Typical Movement Types |
|----------|---------|----------------------|
| AUF | GR for production/process orders without account assignment | 101 for production order |
| BSA | Initial stock balance entry | 561 |
| INV | Inventory differences (physical inventory) | 701 / 702 |
| VAX | GI for sales orders WITHOUT CO account assignment (COGS) | 601 |
| VAY | GI for sales orders WITH CO account assignment (WBS element, internal order) | 601 with WBS/order |
| VBR | Internal goods issues: cost centers, production orders, maintenance orders | 201, 261 |
| VNG | Scrapping and destruction | 551, 552 |
| ZOB | GR without purchase order (other receipts) | 501 |

**Critical distinction:** Production order GI (movement type 261) uses GBB/**VBR**. Sales order GI (movement type 601) uses GBB/**VAX** (without CO account assignment) or GBB/**VAY** (with CO account assignment). These are different modifiers pointing to different GL accounts — a common source of account determination errors when both production and sales are active.

### Movement Type 261 — GI to Production Order (GBB/VBR)

Scenario: Goods issue to production order for raw material (valuation class 3000). Moving average price 100.00 EUR. Quantity: 1 unit.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 400000 (Production Consumption — representative example) | 100.00 | Dr | GBB/VBR: valuation class 3000 + modifier VBR → GL 400000 |
| 140000 (Inventory — representative example) | 100.00 | Cr | BSX: valuation class 3000 → GL 140000 |

The debit goes to GBB/VBR (consumption account on the P&L). The credit reduces inventory via BSX.

### Movement Type 551 — Scrapping (GBB/VNG)

Scenario: Scrapping of raw material (valuation class 3000). MAP 100.00 EUR. Quantity: 1 unit.

| Account | Amount (EUR) | Dr/Cr | Source |
|---------|-------------|-------|--------|
| 520000 (Scrapping Loss — representative example) | 100.00 | Dr | GBB/VNG: valuation class 3000 + modifier VNG → GL 520000 |
| 140000 (Inventory — representative example) | 100.00 | Cr | BSX: valuation class 3000 → GL 140000 |

Scrapping posts the loss to a scrapping/destruction expense account (GBB/VNG) and credits inventory (BSX).

### Reversal — Movement Type 262

Movement type 262 is the reversal of 261 (GI reversal). Same OBYC keys (GBB/VBR, BSX), opposite Dr/Cr signs. The inventory is restocked and the consumption account is reversed.

### OBYC Setup for GBB

When configuring GBB in OBYC, the entry requires the account modifier in addition to the chart of accounts and valuation class:

```
OBYC → Transaction key GBB → New Entries:
  Chart of accounts: INT
  Account modifier: VBR
  Valuation class: 3000
  GL account (debit): 400000
  GL account (credit): 400000 (same account — it is always debited for GI)
```

Each modifier (VBR, VNG, VAX, VAY, etc.) requires its own separate entry per valuation class.

---

## 4. VKOA Framework — SD Revenue Account Determination

> **Scope boundary:** This section establishes the framework for Phase 4 FI context. Phase 8 (SD Advanced) owns the full VKOA deep-dive including condition table maintenance, account assignment group configuration, worked billing-to-GL examples, and revenue recognition variants.

### What VKOA Is

VKOA is the SD-side equivalent of OBYC. Where OBYC maps MM goods movements to GL accounts, VKOA maps SD billing document line items to revenue, COGS, and freight GL accounts. T-code: VKOA.

VKOA is accessed via SPRO → Sales and Distribution → Basic Functions → Account Assignment/Costing → Revenue Account Determination → Assign GL Accounts.

### KOFI vs KOFK

Two condition types drive SD account determination:

| Condition Type | Purpose | Destination |
|---------------|---------|-------------|
| KOFI | FI account determination | Posts to revenue GL accounts in FI |
| KOFK | CO account determination | Posts to CO-PA profitability objects (Profitability Analysis) |

Phase 4 focuses on KOFI only. KOFK is CO integration deferred to Phase 10 (CO Advanced).

When SD billing runs, the system executes KOFI to find the revenue GL account. KOFK runs simultaneously if CO-PA is active to assign the posting to a profitability segment.

### KOFI Access Sequence — 5 Access Levels

The KOFI condition type uses access sequence KOFI00. The system searches through these 5 levels from most specific to least specific. The first match found wins — the system stops searching.

| Access Level | Condition Table | Fields Used | Meaning |
|-------------|----------------|------------|---------|
| 1 | Table 1 | Chart of Accounts + Sales Org + Cust AAG + Mat AAG + Account Key | Most specific — all fields match |
| 2 | Table 2 | Chart of Accounts + Sales Org + Cust AAG + Account Key | No material account assignment group |
| 3 | Table 3 | Chart of Accounts + Sales Org + Mat AAG + Account Key | No customer account assignment group |
| 4 | Table 4 | Chart of Accounts + Cust AAG + Mat AAG + Account Key | No sales org |
| 5 | Table 5 | Chart of Accounts + Account Key | Catch-all fallback — matches on chart of accounts and account key only |

**Best practice:** Configure at least table 5 (catch-all) and table 1 (most specific) for each account key. Table 5 ensures no missing account determination errors; table 1 enables differentiation by customer or material type.

### Key Fields Driving VKOA

**Account Key** — From the pricing procedure (T-code V/08, condition type level, AcctKey column). Standard account keys:

| Account Key | Purpose |
|------------|---------|
| ERL | Revenue (main sales revenue posting) |
| ERS | Sales deductions / discounts / rebates |
| ERF | Freight revenue |
| MWS | Output tax (posted to tax GL account) |
| EIN | Cost posting (for COGS in certain scenarios) |

**KTGRD — Customer Account Assignment Group** — Stored in table KNVV (customer sales area data), Billing Documents tab, field "Acct assmt grp" (KTGRD). Classifies customers for revenue determination purposes. Example values:

| KTGRD | Meaning |
|-------|---------|
| 01 | Domestic revenue customers |
| 02 | Export revenue customers |
| 03 | Intercompany customers |

See modules/fi/master-data.md KNVV section for where this field is maintained.

**Material Account Assignment Group** — Stored in the material master, Sales Org 2 view (field "Acct assmt grp material", KTGRM). Classifies materials for revenue determination. Example values:

| KTGRM | Meaning |
|-------|---------|
| 01 | Standard materials |
| 02 | Service materials |
| 03 | Third-party materials |

**Sales Organization** — The SD org unit. Revenue GL accounts can be differentiated by sales org, allowing different company codes with different charts of accounts to have separate VKOA entries.

### Diagnostic Path — Reading Current VKOA Config

T-code VKOA → Select application V (Sales & Distribution) → Select condition type KOFI → Select access table (start with table 1 for most specific, table 5 for catch-all) → View the entries. Each row shows: chart of accounts + (sales org) + (customer AAG) + (material AAG) + account key → GL account.

To answer "what GL account does revenue post to for domestic customers selling finished goods?": Look for table 1 entry with account key ERL + customer AAG 01 + material AAG 01.

### Setup Path — Configuring VKOA

VKOA → Select KOFI → Select condition table (e.g., table 1) → New Entries → Enter:
- Chart of accounts (e.g., INT)
- Sales organization (e.g., 1000)
- Customer account assignment group (e.g., 01)
- Material account assignment group (e.g., 01)
- Account key (e.g., ERL)
- GL account (e.g., 800000 for domestic revenue — representative example)

Save. Active immediately for new billing documents.

---

## 5. FI-Only Automatic Postings

These postings originate within FI processes — not from MM goods movements or SD billing. They occur during month-end closing or payment processing.

---

### 5a. Foreign Currency Valuation — F.05 / OBA1

**What it does:** Program F.05 runs month-end revaluation of foreign currency open items and account balances. When exchange rates change between the original posting date and the valuation date, F.05 calculates the difference and posts unrealized FX gains or losses.

**Configuration in OBA1:** T-code OBA1 defines which GL accounts receive the valuation postings. Two key groupings:

**KDB — Non-open-item GL accounts (balance sheet foreign currency accounts)**
Used for GL accounts that hold foreign currency balances but are not managed on an open item basis (e.g., foreign currency bank accounts). The GL master record in FS00 has an "Exchange rate difference key" field — enter a KDB grouping code there. In OBA1, that grouping code maps to gain and loss GL accounts.

**KDF — Open items: vendor/customer and open-item GL accounts**
Used for:
- Vendor open items (AP subledger accounts — uses the reconciliation account as the key)
- Customer open items (AR subledger accounts — uses the reconciliation account as the key)
- Open-item managed GL accounts (non-reconciliation accounts flagged as OI-managed)

For KDF, enter the reconciliation account (or GL account for direct OI accounts), and assign the gain GL account and loss GL account for that grouping.

**IMG Path:**
SPRO → Financial Accounting (New) → General Ledger Accounting (New) → Periodic Processing → Valuate → Define Accounts for Foreign Currency Valuation

**F.05 execution:**
Transaction F.05 → Enter company code, valuation date, exchange rate type → Select which areas to valuate (G/L accounts, customer open items, vendor open items) → Execute. Posts in test mode first; post actual documents only when verified.

---

### 5b. Cash Discount GL Account Configuration — OBXU / OBXI

> **CORRECTION:** Cash discount GL accounts are NOT configured in OBB8. OBB8 defines payment terms (days, percentages for the discount calculation) only. The GL accounts that receive the cash discount postings are configured in OBXU and OBXI.

**OBXU — Cash discount received (AP side)**
When the company pays a vendor invoice early and the vendor grants a discount, the cash discount amount posts to the GL account configured in OBXU. This is a gain for the company.

Navigation: SPRO → Financial Accounting (New) → Accounts Receivable and Accounts Payable → Business Transactions → Outgoing Payments → Outgoing Payments Global Settings → Define Accounts for Cash Discount Taken (Automatic Postings)

Or directly: T-code OBXU

**OBXI — Cash discount paid (AR side)**
When a customer pays early and the company grants a discount, the cash discount amount posts to the GL account configured in OBXI. This is an expense for the company.

Navigation: SPRO → Financial Accounting (New) → Accounts Receivable and Accounts Payable → Business Transactions → Incoming Payments → Incoming Payments Global Settings → Define Accounts for Cash Discount Granted (Automatic Postings)

Or directly: T-code OBXI

**Configuration in OBXU / OBXI:**
Both transactions use the same structure: enter chart of accounts → assign the GL account for cash discount. No valuation class or account modifier — a single GL account per chart of accounts (though splitting by debit/credit indicator is possible for more granular control).

---

### 5c. Clearing Account Mechanics

Clearing accounts are intermediate accounts that temporarily hold a posting until the offsetting transaction arrives, at which point both sides are "cleared" (matched) and the account returns to zero.

**GR/IR Clearing Account (WRX)**
The most important clearing account in the MM-FI integration:
- **Credited by MIGO** (goods receipt, movement type 101) via OBYC transaction key WRX. At this point the vendor invoice has not yet arrived.
- **Debited by MIRO** (invoice verification / logistics invoice verification). When the vendor invoice is posted, MIRO debits the GR/IR account and credits the vendor account.
- **Cleared by F.13** (automatic clearing). After the GR and IR postings exist, F.13 matches them and generates a clearing document that removes both open items from the GR/IR account. What remains (if anything) is a quantity/price difference that has not been fully matched.

> **Critical implementation note:** The GR/IR clearing account must be flagged as "open item managed" in FS00 (the OI indicator on the Control Data tab). If this flag is missing, F.13 cannot clear the account — postings accumulate on the account with no mechanism for automatic clearance. This is a common implementation oversight that creates reconciliation problems at go-live.

**Asset Clearing Accounts**
When asset acquisitions are posted via F-91 (post document for asset) and the invoice has not yet arrived, the system can post to an asset clearing account instead of directly to the vendor. The asset clearing account acts as a liability placeholder. When the vendor invoice arrives, the clearing account is cleared against the vendor. Configuration: T-code OAYR (asset clearing accounts for asset acquisition postings).

**Bank Clearing Accounts**
Used in the bank reconciliation process. Incoming and outgoing payment postings may first hit a bank clearing account (e.g., outgoing check clearing), which is then cleared when the bank statement confirms the payment cleared the bank. FF67 (manual bank statement) or FEBAN (electronic bank statement processing) handles this clearance.

**GR/IR Account Maintenance — MR11**
When GR/IR items remain open after a reasonable period (vendor invoice never arrived, or goods never received for a posted invoice), use MR11 to analyze and post the GR/IR account maintenance document. MR11 clears the one-sided entry by posting a balancing entry to a defined offset account.

---

## 6. Summary — Account Determination Quick Reference

| Scenario | OBYC Key | Account Modifier | GL Determined By |
|----------|----------|-----------------|-----------------|
| GR against PO — inventory | BSX | None | Valuation class |
| GR against PO — clearing | WRX | None | Valuation class |
| GR against PO — price variance (standard price only) | PRD | Optional | Valuation class |
| GI to production order | GBB | VBR | Val. class + VBR |
| GI for scrapping | GBB | VNG | Val. class + VNG |
| GI for sales order delivery (no CO) | GBB | VAX | Val. class + VAX |
| GI for sales order delivery (with CO) | GBB | VAY | Val. class + VAY |
| SD revenue | VKOA/KOFI | Account key ERL | Cust AAG + Mat AAG + Acct Key |
| SD discount | VKOA/KOFI | Account key ERS | Cust AAG + Mat AAG + Acct Key |
| FX revaluation (open items) | OBA1/KDF | — | Reconciliation account |
| FX revaluation (GL balances) | OBA1/KDB | — | Exchange rate diff key |
| Cash discount received (AP) | OBXU | — | Chart of accounts |
| Cash discount paid (AR) | OBXI | — | Chart of accounts |
