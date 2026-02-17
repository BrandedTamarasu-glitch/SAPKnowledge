---
module: reference
content_type: org-structure
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# SAP ECC 6.0 — Organizational Structure Reference

> Comprehensive reference for all org units, their relationships, key fields, and configuration. ECC 6.0 specific — S/4HANA differences noted inline where significant.

## Hierarchy

```
Client (MANDT)
├── Company Code (BUKRS) ── fiscal year, currency, chart of accounts
│   ├── Plant (WERKS) ── manufacturing, procurement, valuation
│   │   └── Storage Location (LGORT) ── physical inventory
│   └── Business Area (GSBER) ── optional, cross-CC reporting
├── Controlling Area (KOKRS) ── can span multiple company codes
│   ├── Cost Center (KOSTL) ── organized in standard hierarchy
│   └── Profit Center (PRCTR) ── organized in standard hierarchy
│       └── Segment (SEGMENT) ── derived from profit center (New GL required)
├── Sales Organization (VKORG)
│   └── Distribution Channel (VTWEG)
│       └── Division (SPART)
│           └── = Sales Area (VKORG + VTWEG + SPART)
├── Purchasing Organization (EKORG)
│   └── Purchasing Group (EKGRP)
└── Functional Area (FKBER) ── cost-of-sales P&L reporting
```

## Org Units

### Client (MANDT)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| MANDT | Client number (3-digit) | 100, 200, 800 |
| MTEXT | Client description | Production, Test, Customizing |
| CCCATEGORY | Client category | P=production, T=test, C=customizing |

**Table:** T000 | **Create:** SCC4 | **Display:** SCC4
**Configured here:** Currency decimal format, date format, logon settings
**Common pattern:** 000 (SAP reference), 001 (delivery), 100-899 (customizing/production)
**Cross-module impact:** All data partitioned by client — users, master data, transactions

---

### Company Code (BUKRS)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| BUKRS | Company code (4-char) | 1000, US01, DE01 |
| BUTXT | Company name | Acme US Inc., Acme GmbH |
| ORT01 | City | New York, Frankfurt |
| LAND1 | Country key | US, DE, GB |
| WAERS | Local currency | USD, EUR, GBP |
| KTOPL | Chart of accounts | INT, CAUS |
| PERIV | Fiscal year variant | K4=calendar year, V3=Apr-Mar |

**Table:** T001 | **Create:** OX02 | **Display:** OX02
**Configured here:** Fiscal year variant, chart of accounts, local currency, posting period variant, field status variant, tolerance groups, tax settings
**Common pattern:** One company code per legal entity; country-based for tax isolation
**Cross-module impact:** All MM goods movements (MIGO) and SD billing (VF01) from assigned plants/sales orgs generate FI postings in this company code

> S/4HANA: No significant structural change. Company code remains the core FI org unit. Universal Journal (ACDOCA) replaces separate FI/CO tables but CC concept unchanged.

---

### Plant (WERKS)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| WERKS | Plant key (4-char) | 1000, US10 |
| NAME1 | Plant name | Chicago Plant, Hamburg Factory |
| BWKEY | Valuation area (usually = plant) | 1000, US10 |
| FABKL | Factory calendar | US, DE |
| KUNNR | Customer number for intercompany | 1234 |

**Table:** T001W | **Create:** OX10 | **Display:** OX10
**Configured here:** Valuation area, MRP settings, factory calendar, batch management
**Common pattern:** One plant per physical location or manufacturing site
**Cross-module impact:** Goods movements in this plant post to the assigned company code's books; valuation area determines inventory value

See: `modules/mm/CLAUDE.md` for goods movement and procurement details

---

### Storage Location (LGORT)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| WERKS | Parent plant | 1000 |
| LGORT | Storage location key (4-char) | 0001, RM01, FG01 |
| LGOBE | Description | Main Store, Raw Materials, Finished Goods |

**Table:** T001L | **Create:** OX09 | **Display:** OX09
**Configured here:** Negative stock allowed (via plant-level config), physical inventory settings
**Common pattern:** Separate SLocs for raw materials (RM01), finished goods (FG01), QA, scrap
**Cross-module impact:** Inventory balances tracked at plant+SLoc level; movements between SLocs are transfer postings (mvt type 311)

---

### Sales Organization (VKORG)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| VKORG | Sales org key (4-char) | 1000, US10 |
| BUKRS | Assigned company code | 1000 |

**Table:** TVKO | **Create:** OVX5 | **Display:** OVX5
**Configured here:** Pricing procedures, credit control area assignment, incoterms
**Common pattern:** One per market region or sales channel
**Cross-module impact:** SD billing documents (VF01) create FI accounting documents in the assigned company code; revenue and receivables post here

See: `modules/sd/CLAUDE.md` for sales process details

---

### Distribution Channel (VTWEG)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| VTWEG | Distribution channel key (2-char) | 10, 20, 30 |

**Table:** TVTW | **Create:** OVXI | **Display:** OVXI
**Configured here:** Partner determination, pricing conditions (per sales area)
**Common pattern:** 10=direct sales, 20=wholesale, 30=retail
**Cross-module impact:** Part of Sales Area — determines which master data (customer, pricing, material determination) is referenced; shared via OVR1 to reduce master data maintenance

---

### Division (SPART)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| SPART | Division key (2-char) | 01, 02 |

**Table:** TSPA | **Create:** OVXB | **Display:** OVXB
**Configured here:** Material determination, product hierarchy (per sales area)
**Common pattern:** One per product line (01=product line A, 02=product line B)
**Cross-module impact:** Part of Sales Area; used in business area derivation (plant + division combination); shared via OVR2

---

### Sales Area (VKORG + VTWEG + SPART)

Sales Area is the combination of Sales Organization + Distribution Channel + Division. It is not a separate org unit with its own master data table.

**Set up:** OVXG (assign distribution channel and division to sales organization)

All SD master data — customer master (sales area data), pricing conditions, material determination — is maintained per Sales Area. Changing the Sales Area combination changes which master data is referenced in sales documents.

See: `modules/sd/CLAUDE.md` for sales process details

---

### Purchasing Organization (EKORG)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| EKORG | Purchasing org key (4-char) | 1000, PU01 |
| BUKRS | Company code (if CC-specific) | 1000 (blank if cross-CC) |

**Table:** T024E | **Create:** OX08 | **Display:** OX08
**Configured here:** Purchasing value limits, tolerance settings
**Common pattern:** Three assignment modes: (a) company-code-specific (assigned to one CC via OX01), (b) cross-plant within one CC, (c) cross-company-code (not assigned to any CC — serves all CCs)
**Cross-module impact:** Purchase orders and invoice verification (MIRO) generate FI postings in the assigned company code

See: `modules/mm/CLAUDE.md` for procurement process details

---

### Purchasing Group (EKGRP)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| EKGRP | Purchasing group key (3-char) | 001, PG1 |
| EKNAM | Purchasing group name | Corporate Buying, Plant Procurement |
| EKTEL | Telephone number | +1-312-555-0100 |

**Table:** T024 | **Create:** OME4 | **Display:** OME4
**Configured here:** Configured at client level; not assigned to org unit in hierarchy
**Common pattern:** Represents a buyer or group of buyers; assigned in purchasing documents and material master (purchasing view)
**Cross-module impact:** Controls authorization for purchasing documents; used in release strategies

---

### Controlling Area (KOKRS)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KOKRS | Controlling area key (4-char) | 1000, CO01 |
| BEZEI | Name | Central Controlling Area |
| KOINH | CO area currency | USD, EUR |
| KTOPL | Chart of accounts | INT, CAUS |

**Table:** TKA01 | **Create:** OKKP | **Display:** OKKP
**Configured here:** Fiscal year variant, operating concern, CO version, cost center standard hierarchy, profit center standard hierarchy
**Common pattern:** Assignment control option 1 = CO area same as CC (1:1 recommended); option 2 = cross-company-code (1:many). All CCs under one CA must share same chart of accounts and fiscal year variant.
**Cross-module impact:** All cost postings (cost centers, internal orders, profit centers) within assigned CCs managed under this CA; settlements can cross CC boundaries within same CA

> S/4HANA: 1:1 (CA = CC) strongly recommended. Company code validation in OKKP is mandatory and cannot be deactivated. Cross-CC allocation technically possible but discouraged. S/4HANA Cloud Public Edition enforces single controlling area (A000).

See: `modules/co/CLAUDE.md` for cost accounting details

---

### Cost Center (KOSTL)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KOSTL | Cost center key (10-char) | 0000001000, ADMIN-001 |
| BUKRS | Company code | 1000 |
| KOSAR | Category | production, admin, sales, R&D |
| VERAK | Responsible person | JSMITH |
| WAERS | Currency | USD, EUR |

**Table:** CSKS (texts: CSKT) | **Create:** KS01 | **Display:** KS03
**Configured here:** Category, responsible person, hierarchy area, currency
**Common pattern:** Organized in standard hierarchy (required, defined in OKEON/KSH1); typically mirrors organizational departments
**Cross-module impact:** Receives cost postings from FI (overhead, labor); allocations and assessments distribute costs within the controlling area

See: `modules/co/CLAUDE.md` for cost center accounting details

---

### Profit Center (PRCTR)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| PRCTR | Profit center key (10-char) | 0000001000, PROD-001 |
| BUKRS | Company code | 1000 |
| SEGMENT | IFRS 8 segment (if New GL active) | EMEA, APAC |
| VERAK | Responsible person | MJONES |

**Table:** CEPC (texts: CEPCT) | **Create:** KE51 | **Display:** KE53
**Configured here:** Responsible person, segment assignment, hierarchy area
**Common pattern:** Organized in standard hierarchy (required, defined in KCH1); represents a business unit or product group for internal P&L
**Cross-module impact:** Enables profit center accounting for internal P&L; segment is derived from profit center during posting; all FI postings can carry profit center via document splitting (New GL)

> S/4HANA: Profit Center Accounting integrated into Universal Journal (ACDOCA). Separate PCA ledger (EC-PCA, tables GLPCA/GLPCT) eliminated. Real-time — no reconciliation needed. Profit center is a standard ACDOCA dimension.

See: `modules/co/CLAUDE.md` for profit center accounting details

---

### Business Area (GSBER)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| GSBER | Business area key (4-char) | 1000, BA01 |

**Table:** TGSB (texts: TGSBT) | **Create:** OX03 | **Display:** OX03
**Configured here:** Cross-company-code; shared at client level
**Common pattern:** Used for cross-CC balance sheet reporting; derived from plant+division combination or entered manually on documents
**Cross-module impact:** Derived automatically during SD billing and MM goods movements; enables cross-CC financial statements by business area; requires separate reconciliation (not automatic)

> S/4HANA: Still functional but further discouraged. SAP recommends profit center + segment for all internal and external reporting. No technical removal but best practice is to migrate away.

---

### Segment (SEGMENT)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| SEGMENT | Segment key (10-char) | EMEA, APAC, AMERICAS |

**Table:** FAGL_SEGM (texts: FAGL_SEGMT) | **Create:** via SPRO (SM30 V_FAGL_SEGM) | **Display:** SM30 V_FAGL_SEGM
**Configured here:** Segment code and description only; derivation rule configured on profit center master data
**Common pattern:** Used for IFRS 8 / US GAAP ASC 280 segment reporting; typically 3-8 segments per company

**CRITICAL ECC 6 NOTE:** Requires New GL (FAGL) activation AND document splitting configured. Classic GL does not support segments.

**Cross-module impact:** Derived from profit center during posting — not entered manually on documents; enables segment-level financial statements

> S/4HANA: Always available natively — document splitting and segment derivation from profit center work without New GL activation prerequisite. Lower barrier to entry for segment reporting.

---

### Functional Area (FKBER)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| FKBER | Functional area key (4-char) | 0100, 0200 |

**Table:** TFKB (texts: TFKBT) | **Create:** OKBD | **Display:** OKBD
**Configured here:** Functional area code and description; derivation configured via substitution or GL account master
**Common pattern:** Categories: Production, Administration, Sales & Marketing, R&D; derived from cost center (via substitution) or entered on GL account master
**Cross-module impact:** Enables cost-of-sales P&L reporting format (as opposed to total-cost P&L); niche usage for companies required to report cost-of-sales format (common in US GAAP)

> S/4HANA: Still optional but derivation improved; cost-of-sales accounting configuration simplified.

---

## Assignment Rules

| From | To | Cardinality | Assignment T-Code | Notes |
|------|----|-------------|-------------------|-------|
| Plant | Company Code | many:1 | OX18 | Cannot change after transactions posted |
| Sales Org | Company Code | many:1 | OVX3 | SD billing posts to FI under this CC |
| Purchasing Org | Company Code | many:1 (optional) | OX01 | If assigned: company-code-specific purchasing |
| Purchasing Org | Plant | many:many | OX17 | Defines which POrg can procure for which plant |
| Controlling Area | Company Code | 1:many | OX19 | All CCs must share chart of accounts + fiscal year variant |
| Distribution Channel | Sales Org | many:many | OVXK | Forms part of Sales Area |
| Division | Sales Org | many:many | OVXA | Forms part of Sales Area |
| Storage Location | Plant | many:1 | OX09 | Created within a plant context |
| Cost Center | Controlling Area | many:1 | KS01 | Organized in standard hierarchy (OKEHN) |
| Profit Center | Controlling Area | many:1 | KE51 | Organized in standard hierarchy (KCH1) |
| Business Area | Client | n/a | OX03 | Shared across all company codes; client-level |
| Segment | Profit Center | derived | (PC master data KE51) | Maintained on profit center master record |

## Cross-Module Consequences

| Assignment | Downstream Impact |
|------------|-------------------|
| Plant → Company Code | Goods movements (MIGO) generate FI postings in this CC's books. Valuation area typically = plant. |
| Sales Org → Company Code | SD billing (VF01) creates FI accounting documents. Revenue and receivables post to this CC. |
| Purchasing Org → Company Code | Purchase orders and invoice verification (MIRO) generate FI postings in this CC. |
| Controlling Area → Company Code | All cost postings (cost centers, internal orders, profit centers) managed under this CA. CA must share chart of accounts with all assigned CCs. |
| Cost Center → Controlling Area | Cost postings reported and allocated within this CA. Settlements cross CC boundaries only within same CA. |
| Profit Center → Segment | Segment derived from PC master data during posting. Enables segment-level financial statements (requires New GL + document splitting in ECC 6). |
| Business Area derivation | Derived from plant + division during SD billing and MM goods movements. Enables cross-CC balance sheet by business area. |
| Sales Area combination | Customer master, pricing conditions, material determination all maintained per Sales Area. Changing combination changes referenced master data. |
| Purchasing Org → Plant | Determines which POrg can create POs for which plant. A plant can be serviced by multiple POrgs. |

## S/4HANA Differences Summary

| Area | ECC 6 Behavior | S/4HANA Change | Impact |
|------|----------------|----------------|--------|
| Controlling Area | 1:many CC assignment via OKKP | 1:1 strongly recommended; CC validation mandatory | New implementations use 1:1 |
| Cost Elements | Separate master data (KA01/KA06, CSKA/CSKB) | GL accounts serve as cost elements; no separate master | KA01/KA06 obsolete |
| Profit Center Accounting | Separate PCA ledger (EC-PCA, GLPCA/GLPCT tables) | Integrated in Universal Journal (ACDOCA) | Real-time, no reconciliation |
| Segment Reporting | Requires New GL + document splitting | Always available natively | Lower barrier to entry |
| Business Area | Functional, used for cross-CC reporting | Further discouraged; use PC + segment | Migration recommended |
| Material Ledger | Optional per plant (activate via CKMLCP) | Mandatory, always active, part of ACDOCA | Impacts valuation in every plant |
| Functional Area | Optional, requires substitution config | Still optional but derivation improved | Minor simplification |

Client, Company Code, Plant, Storage Location, Sales Org, Distribution Channel, Division, Purchasing Org, Purchasing Group — no significant org-structure-level changes in S/4HANA.

See also: `.claude/rules/sap-disambiguation.md` for non-org-structure S/4HANA differences.

## Cross-References

- Org structure summary (always loaded): `.claude/rules/sap-org-structure.md`
- ECC vs S/4 disambiguation: `.claude/rules/sap-disambiguation.md`
- FI module (GL, AP, AR, assets): `modules/fi/CLAUDE.md`
- MM module (procurement, inventory): `modules/mm/CLAUDE.md`
- SD module (sales, shipping, billing): `modules/sd/CLAUDE.md`
- CO module (cost centers, profit centers): `modules/co/CLAUDE.md`
