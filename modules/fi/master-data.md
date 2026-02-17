---
module: fi
content_type: master-data
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Financial Accounting — Master Data

> ECC 6.0 reference. Fields are verified against ABAP Dictionary definitions. S/4HANA differences noted for vendor and customer master only.

## G/L Account Master

G/L accounts are split across two table segments: chart-of-accounts data (SKA1) and company-code-specific data (SKB1). Both are maintained simultaneously in FS00.

**Creation T-code:** FS00 (central maintenance — creates/updates both segments)
**Display T-code:** FS00, or SE16 on SKA1/SKB1 for raw table access

### SKA1 — G/L Account Master (Chart of Accounts Segment)

**Table key:** MANDT + KTOPL + SAKNR
**Scope:** Chart-of-accounts level; one record per account per chart of accounts. Contains account attributes that apply regardless of company code.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KTOPL | Chart of Accounts | INT, CAUS, CAUK |
| SAKNR | G/L Account Number | 100000, 400000, 800000 (up to 10 digits) |
| KTOKS | G/L Account Group | 0001 (assets), 1000 (revenue) — controls field layout and number range |
| XBILK | Balance Sheet Account Indicator | X = balance sheet account; blank = P&L account |
| GVTYP | P&L Statement Account Type | Relevant only when XBILK is blank; controls position in P&L structure |
| XLOEV | Deletion Flag | X = marked for deletion (central) |
| BILKT | Group Account Number | Used for consolidation and group reporting hierarchy |
| MUSTR | Sample Account Number | Template account controlling field settings for this account |

**Note:** SKA1 does NOT contain company-code-specific settings (posting block, field status, tax category). Those are in SKB1.

### SKB1 — G/L Account Master (Company Code Segment)

**Table key:** MANDT + BUKRS + SAKNR
**Scope:** Company-code level; one record per account per company code. An account can be in SKA1 but not yet in a specific company code's SKB1 (account not yet extended to that company code).

| Field | Description | Typical Values |
|-------|-------------|----------------|
| BUKRS | Company Code | 1000, 2000 |
| SAKNR | G/L Account Number | Links to SKA1 |
| XSPEB | Posting Block | X = blocked for posting in this company code |
| FSTAG | Field Status Group | G001, G004 — controls required/optional/hidden fields on posting screens |
| MWSKZ | Tax Category | + = output tax allowed; - = input tax allowed; blank = no tax |
| XMWNO | Post Without Tax Code Allowed | X = posting without tax code permitted even when MWSKZ is set |
| ZUAWA | Sort Key | 0 = manual; 001 = document number; 005 = document date — populates the Assignment field on line items |
| BUSAB | Accounting Clerk | MM, AP01 — responsible clerk abbreviation |

**CORRECTION note:** AKONT (reconciliation account number) is NOT a field in SKB1. The reconciliation account is stored in LFB1 (for vendors) and KNB1 (for customers), pointing to the GL account that serves as the sub-ledger reconciliation account. In SKB1, the field XINTIT indicates whether the account IS a reconciliation account (i.e., is managed by a sub-ledger).

---

## Vendor Master

Vendor master is split across three segments based on organizational scope. All segments are accessible via XK03 (central display) or FK03 (FI accounting view only).

**Creation T-codes:**
- XK01 — Central (creates LFA1 + LFB1 + LFM1 in one transaction; use in MM+FI environments)
- FK01 — FI accounting view only (creates LFA1 + LFB1; no purchasing data)
- MK01 — MM purchasing view only

### LFA1 — Vendor General Data

**Table key:** MANDT + LIFNR
**Scope:** Client level; applies across all company codes and purchasing organizations. Core identification and address data.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| LIFNR | Vendor Account Number | VENDOR001, 10000–99999 |
| KTOKK | Vendor Account Group | KRED (standard creditor), LIEF (supplier) |
| NAME1 | Name 1 | ABC Supplies GmbH |
| LAND1 | Country Key | US, DE, GB |
| STCD1 | Tax Number 1 | Federal tax ID or VAT registration number |
| ORT01 | City | New York, Frankfurt |
| REGIO | Region / State | NY, HE |
| SPERR | Central Posting Block | X = blocked for all company codes |
| LOEVM | Central Deletion Flag | X = flagged for deletion (central) |

### LFB1 — Vendor Company Code Data

**Table key:** MANDT + LIFNR + BUKRS
**Scope:** Company code level; one record per vendor per company code. FI-specific payment and accounting settings.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| LIFNR | Vendor Account Number | Links to LFA1 |
| BUKRS | Company Code | 1000 |
| AKONT | Reconciliation Account (GL) | 160000 (Accounts Payable reconciliation GL account) |
| ZTERM | Payment Terms Key | 0001 (14 days 2%, 30 net), Z030 (30 days net) |
| ZWELS | Payment Methods | C (check), T (bank transfer), E (EFT) |
| FDGRV | Planning Group | A1 (domestic supplier), A2 (foreign supplier) |
| BUSAB | Accounting Clerk | AP01 |
| ZUAWA | Sort Key | 031 (vendor number) |
| REPRF | Check for Duplicate Invoice | X = duplicate invoice check active |
| TOGRU | Tolerance Group | blank = system default tolerance |
| ZAHLS | Payment Block | A = payment blocked, blank = not blocked |

**CORRECTION — Field name:** The planning group field is FDGRV (not FDGRP — FDGRP does not exist in LFB1). Confirm via SE11 on table LFB1 if in doubt.

**Key link:** AKONT in LFB1 must point to a GL account in SKA1/SKB1 that is flagged as a reconciliation account (SKB1.XINTIT = X). The FI posting to the vendor sub-ledger automatically updates this GL reconciliation account.

### LFM1 — Vendor Purchasing Organization Data

**Table key:** MANDT + LIFNR + EKORG
**Scope:** Purchasing organization level; MM-facing fields. Relevant for MM-FI integration (GR-based invoice verification, payment terms used in PO).

| Field | Description | Typical Values |
|-------|-------------|----------------|
| LIFNR | Vendor Account Number | Links to LFA1 |
| EKORG | Purchasing Organization | 1000 |
| WAERS | Purchase Order Currency | USD, EUR |
| WEBRE | GR-Based Invoice Verification | X = required (MIRO must reference GR); blank = not required |
| ZTERM | Payment Terms (Purchasing) | 0001 — may differ from FI payment terms in LFB1 |
| INCO1 | Incoterms Part 1 | CIF, FOB, EXW |
| INCO2 | Incoterms Part 2 | New York (delivery place) |

---

## Customer Master

Customer master is split across three segments. All segments accessible via XD03 (central) or FD03 (FI accounting view).

**Creation T-codes:**
- XD01 — Central (creates KNA1 + KNB1 + KNVV in one transaction; use in SD+FI environments)
- FD01 — FI accounting view only (creates KNA1 + KNB1; no sales data)
- VD01 — SD sales view only

> **S/4HANA Note:** In S/4HANA, the vendor master (LFA1/LFB1/LFM1) and customer master (KNA1/KNB1/KNVV) are replaced by the **Business Partner** model (table BUT000 with partner function role tables). XK01/FK01/XD01/FD01 are obsolete in S/4HANA; Business Partner (BP transaction) replaces all of them. This distinction is critical when migrating from ECC to S/4HANA.

### KNA1 — Customer General Data

**Table key:** MANDT + KUNNR
**Scope:** Client level; core identification and address data.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KUNNR | Customer Number | CUST001, 10000–99999 |
| KTOKD | Customer Account Group | KUNA (standard), DEBTR |
| NAME1 | Name 1 | Acme Corporation |
| LAND1 | Country Key | US, DE |
| STCD1 | Tax Number 1 | Federal tax ID |
| ORT01 | City | Chicago, London |
| REGIO | Region / State | IL, LDN |
| BRSCH | Industry Key | Industry classification code |

### KNB1 — Customer Company Code Data

**Table key:** MANDT + KUNNR + BUKRS
**Scope:** Company code level; FI-specific payment and accounting settings.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KUNNR | Customer Number | Links to KNA1 |
| BUKRS | Company Code | 1000 |
| AKONT | Reconciliation Account (GL) | 140000 (Accounts Receivable reconciliation GL account) |
| ZTERM | Payment Terms | 0001, Z030 |
| BUSAB | Accounting Clerk | AR01 |
| ZUAWA | Sort Key | 001 (document number) |
| SPERR | Posting Block (Company Code) | X = blocked for posting |
| TOGRU | Tolerance Group | blank = system default |

**Note:** KVGR1-5 (customer group classification fields) are NOT in KNB1. They are in KNVV (sales area data). See KNVV section below.

### KNVV — Customer Sales Area Data

**Table key:** MANDT + KUNNR + VKORG + VTWEG + SPART
**Scope:** Sales area level (sales org + distribution channel + division). SD-facing fields used in pricing and sales statistics.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KUNNR | Customer Number | Links to KNA1 |
| VKORG | Sales Organization | 1000 |
| VTWEG | Distribution Channel | 10 |
| SPART | Division | 00 |
| KVGR1 | Customer Group 1 | 01, 02, 03 — used in pricing condition access sequences |
| KVGR2 | Customer Group 2 | SD pricing classification |
| KVGR3 | Customer Group 3 | SD pricing classification |
| KVGR4 | Customer Group 4 | SD pricing classification |
| KVGR5 | Customer Group 5 | SD pricing classification |
| KTGRD | Account Assignment Group | 01 (domestic), 02 (export) — drives revenue account determination in SD billing |
| ZTERM | Payment Terms (SD) | May differ from FI payment terms in KNB1 |

**CORRECTION — KVGR field location:** KVGR1-5 (customer groups 1-5) are in KNVV, not KNB1. They are SD-oriented classification fields used in pricing condition access sequences. KNB1 does not contain KVGR fields. If querying these fields, always join against KNVV with the sales area key.

---

## Asset Master

Asset master is split across three segments. Full asset record is viewed in AS03 or AW01N (Asset Explorer).

**Creation T-codes:** AS01 (create asset), AS02 (change), AS03 (display), AW01N (Asset Explorer — drilldown view)

### ANLA — Asset Master General Data

**Table key:** MANDT + BUKRS + ANLN1 + ANLN2
**Scope:** General asset identification, classification, and description. ANLN2 = subnumber (0000 = main asset; 0001, 0002 = subnumbers for partial retirements or additions).

| Field | Description | Typical Values |
|-------|-------------|----------------|
| BUKRS | Company Code | 1000 |
| ANLN1 | Main Asset Number | 100000 |
| ANLN2 | Asset Subnumber | 0000 (main), 0001 (first addition) |
| ANLKL | Asset Class | 1000 (buildings), 2000 (vehicles), 3000 (machinery and equipment) |
| TXA50 | Asset Description | Office Equipment XY-123 |
| AKTIV | Asset Capitalization Date | Date asset placed in service (starts depreciation) |
| DEAKT | Asset Deactivation Date | Blank while active; set on retirement |

**CORRECTION — KOSTL not in ANLA:** Cost center (KOSTL) is NOT a direct field in ANLA. It is stored in ANLZ (time-dependent segment) to support cost center changes over the asset's life. See ANLZ section.

### ANLB — Asset Depreciation Terms

**Table key:** MANDT + BUKRS + ANLN1 + ANLN2 + AFABE
**Scope:** Depreciation terms per depreciation area (AFABE). One record per asset per depreciation area (e.g., book depreciation, tax depreciation, IFRS).

| Field | Description | Typical Values |
|-------|-------------|----------------|
| AFABE | Depreciation Area | 01 (book/commercial), 10 (tax), 15 (IFRS), 20 (cost accounting) |
| AFASL | Depreciation Key | LINR (straight-line), DBNL (declining balance) |
| NDJAR | Useful Life in Years | 10 (machinery), 40 (buildings) |
| NDPER | Useful Life in Periods (months) | 0 when years are used; 6 for partial-year adjustments |

**Note:** Depreciation areas are defined in the Chart of Depreciation (EC08). Area 01 is always the leading book depreciation area that posts to GL.

### ANLZ — Asset Master Time-Dependent Data

**Table key:** MANDT + BUKRS + ANLN1 + ANLN2 + BDATU (valid-to date)
**Scope:** Time-dependent organizational assignments. A new ANLZ record is created each time an assignment (e.g., cost center) changes, preserving the history of which cost center bore the asset's costs over time.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KOSTL | Cost Center | 1000 (IT), 2000 (Production) |
| KOSTLV | Responsible Cost Center | May differ from KOSTL in some configurations |
| PRCTR | Profit Center | PC-1000 |
| GSBER | Business Area | 0001 |
| FKBER | Functional Area | 0100 (Administration), 0200 (Production) |
| BDATU | Valid-To Date (key field) | 99991231 = current record; earlier date = historical |
| ADATU | Valid-From Date | Date this organizational assignment became effective |

**Time-dependency explanation:** When you transfer an asset to a different cost center (ABUMN or AS02 cost center change), SAP creates a new ANLZ record with ADATU = transfer date and closes the previous record with BDATU = transfer date - 1. This allows reporting of depreciation by cost center for the correct periods. To see the current assignment, read ANLZ where BDATU = '99991231'.
