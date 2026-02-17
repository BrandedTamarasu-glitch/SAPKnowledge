---
module: sd
content_type: master-data
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# Sales & Distribution — Master Data

> ECC 6.0 reference. Master data objects and key fields for SD module. Customer master documented self-contained (all three levels) with SD emphasis. For material master details beyond sales views, see `modules/mm/master-data.md`.

## 1. Customer Master

> **S/4HANA Note:** In S/4HANA, the customer master (KNA1/KNB1/KNVV) is maintained through Business Partner (BP) transaction using BUT000/BUT0BK tables with CVI (Customer-Vendor Integration) synchronizing to KNA1/KNB1/KNVV. All T-codes (XD01, VD01, FD01) still work in S/4HANA but create/update BP underneath. This section documents the ECC 6.0 table structure which remains the runtime data model in both ECC and S/4.

The customer master has three levels, each stored in a separate table:

### KNA1 — Customer General Data

**Table key:** MANDT + KUNNR
**Scope:** Client level. One record per customer across the entire SAP system. Contains address, communication, control data. Does NOT contain any sales- or company-code-specific data.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KUNNR | Customer number | 10-digit, alpha-numeric |
| NAME1/NAME2 | Customer name (lines 1-2) | |
| STRAS | Street address | |
| ORT01 | City | |
| PSTLZ | Postal code | |
| LAND1 | Country key | US, DE, GB |
| SPRAS | Language key | EN, DE |
| BRSCH | Industry sector | Used in account determination (VKOA) |
| KTOKD | Account group | Controls number range and screen layout |
| STCEG | VAT registration number | Tax determination input |
| KATR1-10 | Customer attributes | Search terms and classification |

### KNB1 — Customer Company Code Data

**Table key:** MANDT + KUNNR + BUKRS
**Scope:** Company code level. One record per customer per company code. Contains FI-relevant data: reconciliation account, payment terms, dunning. Created when FI extends the customer.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| AKONT | Reconciliation account | GL account for AR sub-ledger (e.g., 140000) |
| ZTERM | Payment terms | Z001 (Net 30), Z060 (Net 60) |
| MAHNA | Dunning procedure | 0001 (standard 4-level dunning) |
| ZWELS | Payment methods | C (check), T (bank transfer) |
| FDGRV | Cash management planning group | Controls cash flow forecasting |
| TOGRU | Tolerance group | Controls payment difference tolerance (OBA3) |

### KNVV — Customer Sales Area Data

**Table key:** MANDT + KUNNR + VKORG + VTWEG + SPART
**Scope:** Sales area level. One record per customer per sales organization + distribution channel + division. This is the primary SD master data segment — controls pricing, shipping, billing, and partner determination behavior.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KALKS | Customer pricing procedure | 1 (standard) — input to OVKK pricing procedure determination |
| KDGRP | Customer group | 01, 02 — used in pricing condition access sequences |
| KVGR1-5 | Customer groups 1-5 | Flexible groupings for pricing, statistics, reporting |
| BZIRK | Sales district | Geographic grouping for sales reporting |
| VKBUR | Sales office | Organizational assignment for sales rep |
| VKGRP | Sales group | Team within sales office |
| KTGRD | Customer account assignment group | Input to VKOA revenue account determination — Billing tab |
| WAERS | Currency | USD, EUR — order currency default |
| KZAZU | Order combination indicator | Controls whether orders can be combined for delivery |
| LPRIO | Delivery priority | 01 (high) - 99 (low) — affects delivery due list sequence |
| VSBED | Shipping condition | 01 (standard), 02 (express) — input to shipping point determination |
| INCO1/INCO2 | Incoterms | CIF, FOB, EXW + named place |
| ZTERM | Payment terms (SD) | Overrides KNB1 payment terms for SD billing |
| VWERK | Delivering plant | Default delivering plant (can override at order level) |
| PODKZ | POD indicator | Proof of delivery relevant |
| ANTLF | Max partial deliveries | Controls how many partial deliveries are allowed |

> **CORRECTION:** KVGR1-5 (customer groups for pricing) are in **KNVV** (Sales Area Data), NOT in KNB1 (Company Code Data). This is one of the most commonly misattributed field locations. Check: SE11 → KNVV → field KVGR1.

> **CORRECTION:** KTGRD (customer account assignment group) is in **KNVV Billing tab**, NOT in KNA1 (General Data). KTGRD is a key input to VKOA revenue account determination. Check: SE11 → KNVV → field KTGRD.

**Partner Functions (KNVP):**
Partner functions define relationships at the sales area level: SP (sold-to), SH (ship-to), BP (bill-to), PY (payer). Stored in KNVP table (KUNNR + VKORG + VTWEG + SPART + PARVW). Default partner functions are proposed from KNVP into every sales document (VBPA) and can be overridden at document level.

---

## 2. Condition Records (Pricing Master Data)

Condition records are the pricing master data in SD. They store prices, discounts, surcharges, and taxes. The condition technique determines which records are found and applied during order pricing.

### KONH — Condition Record Header

**Table key:** KNUMH (condition record number, internal)
**Scope:** One header per condition record. Links condition type + key combination to a validity period.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KNUMH | Condition record number | Internal number, auto-assigned |
| KVEWE | Application | A (pricing), B (output), C (account determination) |
| KOTABNR | Condition table | Number of the condition table (V/06) that defines the key fields |
| KAPPL | Application indicator | V (SD pricing) |
| KSCHL | Condition type | PR00, K004, K005, MWST, RA00 |
| DATAB | Valid-from date | |
| DATBI | Valid-to date | 99991231 = no end date |

### KONP — Condition Record Item

**Table key:** KNUMH + KOPOS (item number within record)
**Scope:** Rate/amount detail for the condition record.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KBETR | Rate (condition amount) | 100.00 (price), 5.00 (% discount) |
| KONWA | Rate unit (currency or %) | USD, EUR, % |
| KPEIN | Pricing unit | 1 (per each), 100 (per 100) |
| KMEIN | Unit of measure | EA, KG, L |
| KSTBM | Scale basis quantity | For scale pricing |
| MXWRT | Maximum condition value | Upper cap for discounts |

### Standard Condition Types

| Condition Type | Description | Calculation | Typical Access Sequence |
|----------------|-------------|-------------|-------------------------|
| PR00 | Base price | Fixed amount per unit | Material + sales org → material + dist channel → material |
| K004 | Material discount | Percentage | Material + customer |
| K005 | Customer-specific discount | Percentage | Customer + material |
| K007 | Material group discount | Percentage | Customer + material group |
| MWST | Output tax | Percentage | Country + tax classification customer + tax classification material |
| RA00 | Rebate accrual | Percentage | Customer + material (validity = rebate agreement period) |
| KF00 | Freight | Fixed amount per weight | Shipping point + route + weight group |

### Access Sequences — How the System Searches

An access sequence defines the search strategy for condition records. The system checks condition tables in priority order and uses the first record found (unless the exclusive indicator is turned off).

Example for PR00 (base price):
1. Check table for Customer + Material (most specific)
2. Check table for Price List + Material
3. Check table for Material + Sales Org (most general)

If a record is found at step 1, steps 2-3 are skipped. This "most-specific-first" logic is the core of SD pricing flexibility.

---

## 3. Output Determination Master Data

Output determination uses the condition technique to find output records specifying what documents to produce (print, fax, EDI, email), when, and to whom.

### Output Types (Standard)

| Output Type | Application | Description | Default Medium |
|-------------|-------------|-------------|----------------|
| BA00 | V1 (Sales) | Order confirmation | 1 (Print) |
| BA01 | V1 (Sales) | Order confirmation (external) | 1 (Print) |
| LD00 | V2 (Shipping) | Delivery note | 1 (Print) |
| RD00 | V3 (Billing) | Billing document (invoice) | 1 (Print) |
| RD03 | V3 (Billing) | Invoice list | 1 (Print) |
| PK00 | V2 (Shipping) | Packing list | 1 (Print) |

### Output Condition Records

Output condition records (maintained via VV31-VV33 or NACE) specify:
- **Medium:** 1=Print, 2=Fax, 5=EDI, 7=Email (SAPconnect)
- **Timing:** 1=Send immediately, 2=Send with periodically scheduled job, 3=Send using GOS, 4=Send with next selection (batch)
- **Partner:** Which partner function receives the output (SP=sold-to, SH=ship-to, BP=bill-to)
- **Language:** Output language for the document

The access sequence determines which condition table keys are used for finding the output record (e.g., sales org + order type, or customer + sales org).

### Partner-Based Output Determination

For partner-dependent outputs, the system reads KNVP (partner functions) to determine the partner and then checks output condition records for that partner. Example: order confirmation goes to SP (sold-to), delivery note goes to SH (ship-to), invoice goes to BP (bill-to).

---

## 4. Material Master — Sales Views

Material master is primarily documented in `modules/mm/master-data.md`. This section covers the SD-specific views only.

### MVKE — Sales Organization Data

**Table key:** MANDT + MATNR + VKORG + VTWEG
**Scope:** Sales org + distribution channel level. Controls SD-specific behavior per material per sales channel.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| DWERK | Delivering plant | Default plant for deliveries — shipping point derived from here |
| MTPOS | Item category group | NORM, BANS, LUMP — input to item category determination (4-key lookup) |
| KTGRM | Account assignment group material | 01 (finished goods), 02 (trading goods) — input to VKOA revenue account determination |
| KONDM | Material pricing group | Groups materials for pricing condition access sequences |
| MVGR1-5 | Material groups 1-5 | Flexible groupings for pricing and statistics |
| PRODH | Product hierarchy | Classification for reporting and pricing |
| VMSTA | Distribution channel status | Controls whether material can be sold in this channel |
| AUMNG | Minimum order quantity | Minimum qty per order line |
| SCMNG | Delivery unit | Rounding quantity for delivery |

> **CORRECTION:** KTGRM (account assignment group material) is in **MVKE** (Sales Org 2 view), NOT in MARA (General/Plant Data). KTGRM is a key input to VKOA revenue account determination alongside KTGRD from customer master. Check: SE11 → MVKE → field KTGRM.

> **CORRECTION:** DWERK (delivering plant) is in **MVKE** (Sales Org 1 view), NOT in MARC (Plant Data). DWERK is the default plant for SD deliveries and drives shipping point determination. MARC-WERKS is the plant key for the material-plant record, which is a different concept. Check: SE11 → MVKE → field DWERK.

### MARA — Sales-Relevant General Fields

A few MARA fields are relevant to SD:

| Field | Description | SD Relevance |
|-------|-------------|-------------|
| SPART | Division | Org structure: part of sales area key (VKORG + VTWEG + SPART) |
| MSTAE | Cross-distribution status | Blocks sales across all distribution channels |
| MEINS | Base unit of measure | Default UoM in sales orders (can be overridden by VRKME in MVKE) |

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|--------|
| Customer master: KNA1/KNB1/KNVV tables | Business Partner (BP) with CVI sync | Runtime tables unchanged; maintenance via BP |
| VD01/XD01/FD01 for customer creation | BP transaction for creation | Legacy T-codes still work |
| KONH/KONP condition record tables | Same tables in S/4 | No change — condition technique unchanged |
| Output records via NACE/VV31 | BRF+ output management | NACE still works for custom/legacy outputs |
