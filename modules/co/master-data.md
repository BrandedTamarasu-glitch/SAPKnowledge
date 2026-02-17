---
module: co
content_type: master-data
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-17
---

# Controlling — Master Data

> ECC 6.0 reference. CO master data is organized under the Controlling Area (KOKRS). All objects below share the controlling area as a key field. For S/4HANA differences, see callouts at each section.

## Cost Element Categories (CRITICAL Reference)

Cost element categories define what a cost element CAN DO. This is the most commonly confused CO concept.

### Primary Cost Elements

Primary cost elements MUST have a corresponding GL account in FI (SKA1/SKB1) with the SAME number. The GL account must exist FIRST (FS00), then the cost element is created (KA01).

| Category | Name | Description | GL Account Required | Example Use |
|----------|------|-------------|--------------------|----|
| 1 | Primary costs/revenue | Standard P&L cost element | Yes | Salaries (KSTAR = GL account for salaries) |
| 3 | Accrual/deferral (FI side) | FI posts to one account, CO posts to another | Yes | Calculated depreciation vs actual |
| 4 | Accrual/deferral (CO side) | CO accrual cost element | Yes | CO imputed costs |
| 11 | Revenue | Revenue cost element | Yes | Sales revenue |
| 12 | Sales deduction | Discounts, rebates | Yes | Cash discounts given |
| 22 | External settlement | Settlement to external receiver (FI) | Yes | Settle order costs to GL account |

### Secondary Cost Elements

Secondary cost elements exist ONLY in CO — they have NO corresponding GL account. Created via KA06. They are used exclusively for CO-internal transactions.

| Category | Name | Description | GL Account Required | Example Use |
|----------|------|-------------|--------------------|----|
| 21 | Internal settlement | Settlement from order to CO receiver | No | Settle internal order to cost center |
| 31 | Order/project results analysis | WIP and results analysis | No | Production order WIP calculation |
| 41 | Overhead rates | Overhead surcharge postings | No | Apply overhead to internal orders (KGI2) |
| 42 | Assessment | Assessment cycle allocation | No | KSU5 posts with this CE — original CEs lost |
| 43 | Internal activity allocation | Activity type allocation | No | Activity allocation from sender CC to receiver |

> **CORRECTION:** Many sources incorrectly state that secondary cost elements "can" have a GL account. They CANNOT. Secondary cost elements (categories 21, 31, 41, 42, 43) are CO-only. If you need a cost element that posts to FI, you need a primary cost element. The KA06 transaction enforces this — it does not accept a GL account number.

> **S/4HANA CRITICAL:** In S/4HANA, cost elements are no longer separate master data. The cost element category is maintained directly on the GL account master (FS00). KA01 and KA06 are obsolete. Primary cost elements are simply P&L GL accounts with a cost element category assigned. Secondary cost elements still exist but are created as GL accounts of type "secondary cost element" (account type N).

---

## Cost Elements (CSKA / CSKB)

| Field | Table.Field | Description |
|-------|------------|-------------|
| Cost Element | CSKA-KSTAR | Cost element number (= GL account number for primary) |
| Chart of Accounts | CSKA-KTOPL | Chart of accounts key |
| Controlling Area | CSKB-KOKRS | Controlling area |
| Category | CSKB-KATYP | Cost element category (see table above) |
| Valid From | CSKB-DATAB | Start of validity period |
| Valid To | CSKB-DATBI | End of validity period |

**Key distinction:** CSKA is the chart-of-accounts level (shared across controlling areas using the same chart of accounts). CSKB is the controlling-area level (specific settings per controlling area). For most lookups, query CSKB.

**Text table:** CSKU (cost element texts, key: SPRAS + KTOPL + KSTAR)

**Create T-code:** KA01 (primary), KA06 (secondary)

---

## Cost Centers (CSKS / CSKT)

| Field | Table.Field | Description |
|-------|------------|-------------|
| Cost Center | CSKS-KOSTL | Cost center number |
| Controlling Area | CSKS-KOKRS | Controlling area |
| Company Code | CSKS-BUKRS | Assigned company code |
| Category | CSKS-KOSAR | Cost center category (H=overhead, F=production, V=sales, E=R&D, etc.) |
| Responsible Person | CSKS-VERAK | Person responsible (free text) |
| Profit Center | CSKS-PRCTR | Assigned profit center — CRITICAL for PCA reporting |
| Hierarchy Area | CSKS-KHINR | Position in standard hierarchy |
| Valid From | CSKS-DATAB | Start of validity period |
| Valid To | CSKS-DATBI | End of validity period |
| Currency | CSKS-WAERS | Cost center currency |
| Business Area | CSKS-GSBER | Business area assignment |

> **CORRECTION:** The profit center field (CSKS-PRCTR) is NOT optional in practice. While technically not a required field, if it is empty, costs posted to this cost center will NOT appear in PCA reports (KE5Z). Always assign a profit center to every cost center.

**Text table:** CSKT (cost center texts, key: KOKRS + KOSTL + DATBI + SPRAS)

**Create T-code:** KS01

**Standard Hierarchy:** Every cost center must belong to the standard hierarchy (defined via OKEON). The hierarchy has a root node (controlling area level) with branches. Cost center groups (KSH1) create additional grouping for reporting and allocation cycles.

---

## Internal Orders (AUFK)

| Field | Table.Field | Description |
|-------|------------|-------------|
| Order Number | AUFK-AUFNR | Internal order number (12 digits, leading zeros) |
| Order Type | AUFK-AUART | Controls behavior: number range, settlement profile, budgeting, planning |
| Controlling Area | AUFK-KOKRS | Controlling area |
| Company Code | AUFK-BUKRS | Company code |
| Responsible CC | AUFK-KOSTV | Responsible cost center |
| Profit Center | AUFK-PRCTR | Profit center assignment |
| Object Class | AUFK-OBJNR | CO object number (used for totals table lookups) |
| Settlement CE | AUFK-KSTAR | Default settlement cost element |
| Status | via JEST/TJ02 | System status: CRTD (created), REL (released), TECO (technically complete), CLSD (closed) |
| Currency | AUFK-WAERS | Order currency |
| Valid From | AUFK-PDAT1 | Order start date |
| Valid To | AUFK-PDAT3 | Order end date |

**Settlement Rule (COBRB):**
The settlement rule defines WHERE costs are settled (receivers). Maintained on the order via KO02 -> Settlement Rule button.

| COBRB Field | Description |
|-------------|-------------|
| AUFNR | Source order |
| KONTY | Receiver type: CTR (cost center), ORD (order), FXA (fixed asset/AUC), PSP (WBS), RKS (CO-PA segment), KST (GL account) |
| EMPGE | Receiver object number |
| PROZS | Settlement percentage |

> **CORRECTION:** The settlement rule is NOT part of the AUFK table — it is in COBRB (settlement rule table). Many references incorrectly show settlement fields on AUFK. AUFK-KSTAR holds the DEFAULT settlement cost element, but the actual receiver definition is in COBRB.

**Create T-code:** KO01

**Status Management:** Internal orders follow a status lifecycle. Key transitions:
- CRTD -> REL (release for posting — no costs can be posted until released)
- REL -> TECO (technically complete — no more postings, but settlement still possible)
- TECO -> CLSD (closed — no further activity, archived)
Gotcha: Setting TECO prevents further postings. If additional costs arrive after TECO, the order must be reopened (remove TECO status in KO02).

---

## Activity Types (CSLA / CSLT)

| Field | Table.Field | Description |
|-------|------------|-------------|
| Activity Type | CSLA-LSTAR | Activity type key |
| Controlling Area | CSLA-KOKRS | Controlling area |
| Activity Unit | CSLA-LEINH | Unit of measure (H=hours, MIN=minutes, ST=pieces) |
| Price Indicator | CSLA-TARKZ | Price determination: 1=plan price automatic, 2=plan price manual, 3=target=actual |
| Allocation Cost Element | CSLA-STRKZ | Default cost element for allocation (category 43) |
| Activity Type Category | CSLA-LATYP | Category: 1=manual entry/manual allocation, 2=indirect determination/indirect allocation |
| Valid From | CSLA-DATAB | Start of validity period |
| Valid To | CSLA-DATBI | End of validity period |

**Text table:** CSLT (activity type texts, key: KOKRS + LSTAR + DATBI + SPRAS)

**Create T-code:** KL01

**Activity Prices:** Planned via KP26 (change) / KP27 (display). Activity price = fixed portion + variable portion per unit. The system uses these prices to value activity allocations at period-end. If no price is planned, allocations post at zero value.

> **CORRECTION:** The activity type is NOT the same as the cost element used for allocation. The activity type (CSLA-LSTAR) measures the output quantity. The allocation uses a secondary cost element (category 43) defined in the activity type master or the allocation configuration. Do not confuse the activity type key with the cost element number.

---

## Profit Centers (CEPC / CEPCT)

> **S/4HANA NOTE:** In S/4HANA, the separate PCA ledger (GLPCA/GLPCT) is eliminated. Profit center data is in the Universal Journal (ACDOCA). CEPC master data still exists. KE5x T-codes still work but read from ACDOCA.

| Field | Table.Field | Description |
|-------|------------|-------------|
| Profit Center | CEPC-PRCTR | Profit center number |
| Controlling Area | CEPC-KOKRS | Controlling area |
| Company Code | CEPC-BUKRS | Company code |
| Segment | CEPC-SEGMENT | Segment for segment reporting (New GL) |
| Responsible Person | CEPC-VERAK | Person responsible |
| Profit Center Group | via SETHEADER/SETNODE | Hierarchy group membership |
| Valid From | CEPC-DATAB | Start of validity period |
| Valid To | CEPC-DATBI | End of validity period |

**Text table:** CEPCT (profit center texts, key: KOKRS + PRCTR + DATBI + SPRAS)

**Create T-code:** KE51

**Profit Center Hierarchy:** Mandatory standard hierarchy defined in controlling area settings. Additional groups via KCH1.

**PCA Separate Ledger (ECC 6 specific):**
In ECC 6, PCA maintains its own ledger tables:
- **GLPCA** — PCA actual line items
- **GLPCT** — PCA totals

These tables mirror FI postings but from a profit center perspective. For PCA to be complete, EVERY FI posting must carry a profit center assignment. Methods:
1. **Document splitting** (New GL) — automatic profit center derivation
2. **Substitution rules** (1KEF) — rule-based profit center assignment
3. **Manual entry** — user enters profit center on FI document

Gotcha: If FI postings lack profit center assignments, KE5Z (PCA report) totals will not match FAGLB03 (FI report) totals. This reconciliation gap is the #1 PCA issue in ECC 6.

---

## Statistical Key Figures

| Field | Table | Description |
|-------|-------|-------------|
| Statistical Key Figure | TKA3A-STAGR | Key figure key |
| Controlling Area | TKA3A-KOKRS | Controlling area |
| Key Figure Category | TKA3A-SSTYP | 1=fixed value (carried forward), 2=totals value (cumulated) |
| Unit | TKA3A-MSEHI | Unit of measure (e.g., FTE, SQM) |

**Create T-code:** KK01 (create), KK02 (change), KK03 (display)
**Enter values:** KB31N (enter statistical key figure values)

**Usage:** Statistical key figures measure non-monetary quantities (headcount, square meters, phone lines) used as allocation bases in assessment/distribution cycles. Example: allocate rent costs based on square meters occupied.

**Two categories:**
- **Fixed value (1):** Value is entered once and carried forward to subsequent periods automatically. Example: headcount (stays constant until changed).
- **Totals value (2):** Value must be entered each period. Previous values do not carry forward. Example: machine hours (varies each period).

---

## CO Totals and Document Tables

### Totals Tables

| Table | Content | Key Fields |
|-------|---------|------------|
| COSP | CO totals — primary postings | KOKRS + LEDNR + OBJNR + GJAHR + WRTTP + VERSN + KSTAR + HRKFT + ... |
| COSS | CO totals — secondary postings | Same structure as COSP |

**OBJNR** is the CO object number — a concatenated key that encodes the object type and number (e.g., "KS" + controlling area + cost center for cost centers). Use function module CONVERSION_EXIT_ALPHA_INPUT or the AUFK/CSKS master data tables to decode.

**WRTTP** (value type): 04 = actual, 01 = plan version 0. Period values stored in WKG001-WKG016 (controlling area currency) and WOG001-WOG016 (object currency).

### Document Tables

| Table | Content | Key Fields |
|-------|---------|------------|
| COBK | CO document header | KOKRS + BELNR + BUZEI |
| COEP | CO document line items | KOKRS + BELNR + BUZEI |

CO documents are separate from FI documents (BKPF/BSEG). A single FI posting may generate multiple CO line items (e.g., posting to a cost center with activity allocation). The FI document number is in COEP-BELNR (reference) but the CO document has its own number.

---

## Relationship Map

```
Controlling Area (TKA01)
+-- Cost Elements (CSKA/CSKB)
|   +-- Primary (cat 1,3,4,11,12,22) -- maps 1:1 to GL account (SKA1/SKB1)
|   +-- Secondary (cat 21,31,41,42,43) -- CO-only, no GL account
+-- Cost Center Standard Hierarchy (SETNODE/SETHEADER)
|   +-- Cost Centers (CSKS)
|       +-- Activity Types (CSLA) -- output measurement for the CC
|       +-- Statistical Key Figures (TKA3A) -- allocation bases
+-- Internal Orders (AUFK)
|   +-- Settlement Rules (COBRB) -- defines receivers
|       +-- Receivers: CC, IO, GL, AUC, WBS, CO-PA segment
+-- Profit Center Standard Hierarchy (SETNODE/SETHEADER)
|   +-- Profit Centers (CEPC)
|       +-- PCA Ledger (GLPCA/GLPCT) -- ECC 6 separate ledger
+-- CO Totals: COSP (primary) + COSS (secondary)
+-- CO Documents: COBK (header) + COEP (line items)
```

**Key assignments:**
- Cost Center -> Profit Center (CSKS-PRCTR): costs on the CC appear on the PC
- Internal Order -> Profit Center (AUFK-PRCTR): order costs appear on the PC
- Internal Order -> Responsible Cost Center (AUFK-KOSTV): organizational ownership
- Controlling Area -> Company Code (OX19/OKKP): 1:many in ECC 6
