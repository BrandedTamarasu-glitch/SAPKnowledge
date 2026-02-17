---
module: mm
content_type: master-data
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# Materials Management — Master Data

> ECC 6.0 reference. Material master organized by view group (mirrors SAP UI); underlying table noted at each section header. CORRECTION blocks flag fields that are commonly documented in the wrong view.

## Material Master

The material master is the central data repository for all materials. Data is distributed across multiple tables by organizational level:
- **MARA** — Client level (general data: description, base UoM, material type)
- **MARC** — Plant level (MRP, purchasing, planning parameters)
- **MARD** — Storage location level (stock quantities)
- **MBEW** — Valuation area level (accounting, price control, standard price)

T-codes: MM01 (Create), MM02 (Change), MM03 (Display)

### Basic Data 1 View (Table: MARA — Client Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Material Number | Unique material identifier | MARA-MATNR | Up to 18 chars in ECC 6; 40 chars in S/4HANA |
| Material Type | Controls procurement type, account determination | MARA-MTART | e.g., ROH=raw material, FERT=finished goods, HIBE=operating supplies |
| Industry Sector | Industry-specific view selection | MARA-MBRSH | Determines which views are available |
| Base Unit of Measure | Inventory unit | MARA-MEINS | All stock quantities stored in this UoM |
| Material Group | Grouping for reporting/sourcing | MARA-MATKL | |
| Old Material Number | Legacy system cross-reference | MARA-BISMT | Used during migration |
| Division | SD-relevant; sales area assignment | MARA-SPART | Brief — full detail in SD module |

### Basic Data 2 View (Table: MARA — Client Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Document Number | Link to document management | MARA-ZEINR | Engineering drawing reference |
| CAD Indicator | CAD system link | MARA-CADKZ | |

> Basic Data 2 is lightly used in most implementations. Key fields are document management links.

### Purchasing View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Purchasing Group | Buyer responsible for procurement | MARC-EKGRP | Plant-level assignment |
| Planned Delivery Time | Lead time from vendor in days | MARC-PLIFZ | Used by MRP for planned order scheduling |
| GR Processing Time | Days from GR to availability | MARC-WEBAZ | |
| Under/Over Delivery Tolerance | Acceptable delivery variance | MARC-UEETO / MARC-UNETO | Percentage tolerance |
| Order Unit | PO unit of measure (if different from base UoM) | MARC-BSTME | Conversion maintained in MARM |

> **CORRECTION 4:** Purchasing Group (EKGRP) in PO context comes from the **material master Purchasing view (MARC)**, NOT the vendor master. The vendor master has a purchasing organization (LFM1) but does NOT have a purchasing group field. Purchasing group = which buyer handles procurement for this material at this plant.

### MRP 1 View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| MRP Type | Planning method | MARC-DISMM | VB=manual reorder point, PD=MRP, ND=no MRP, VV=forecast-based |
| Reorder Point | Stock level triggering replenishment | MARC-MINBE | Only active when MRP type = VB or VM |
| MRP Controller | Planner responsible | MARC-DTEFP | Assigned to a person or group |
| Lot Size | Lot sizing procedure | MARC-DISLS | EX=lot-for-lot, FX=fixed lot, WB=weekly, MB=monthly |
| Planned Delivery Time | Lead time for MRP scheduling | MARC-PLIFZ | Same field as Purchasing view |

> **CORRECTION 3:** Reorder Point (MINBE) and MRP Type (DISMM) are in the **MRP 1 view (MARC)**, NOT Basic Data. Basic Data 1/2 contains only client-level data (description, base UoM, material type). All planning parameters are plant-level in MARC.

### MRP 2 View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Procurement Type | Internal/external/both | MARC-BESKZ | E=external (purchase), F=in-house (production), X=both |
| Special Procurement | Subcontracting, consignment, etc. | MARC-SOBSL | Deferred to Phase 12 — document field existence only |
| Safety Stock | Buffer stock quantity | MARC-EISBE | |
| In-house Production Time | Manufacturing lead time | MARC-DZEIT | Only for F or X procurement type |
| Scheduling Margin Key | Float times for scheduling | MARC-FHORI | |
| GR Processing Time | Days from GR to availability | MARC-WEBAZ | |

### MRP 3 View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Availability Check Group | Controls ATP check behavior | MARC-MTVFP | Links to checking rule |
| Total Replenishment Lead Time | Overall lead time | MARC-WZEIT | Used for planning time fence |
| Consumption Mode | Forward/backward consumption of planned independent requirements | MARC-VRMOD | |

### MRP 4 View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Repetitive Manufacturing Profile | For repetitive manufacturing | MARC-SAUFT | |
| Individual/Collective Requirements | MRP lot creation | MARC-SBDKZ | |

> MRP 3 and MRP 4 are lightly used in standard MM implementations. Most key planning fields are in MRP 1 and MRP 2.

### Plant Data / Storage 1 View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Batch Management | Batch-managed material flag | MARC-XCHPF | Per-plant activation |
| Storage Conditions | Temperature, humidity requirements | MARC-RAUBE | |
| Temperature Conditions | Specific temperature control | MARC-TEMPB | |

> **CORRECTION 7:** The batch management indicator (XCHPF) for per-plant control is in **Plant Data / Storage 1 view (MARC)**, NOT Basic Data. The material type can mandate batches at client level, but per-plant activation is in this view.

### Plant Data / Storage 2 View (Table: MARC — Plant Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Profit Center | Default profit center for the material at this plant | MARC-PRCTR | Used in CO postings and profit center accounting |
| Issue Storage Location | Default GI storage location | MARC-LGPRO | |

### Accounting 1 View (Table: MBEW — Valuation Area Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Valuation Class | Links material to OBYC account determination | MBEW-BKLAS | CRITICAL for MM-FI integration |
| Price Control | Standard (S) or Moving Average (V) | MBEW-VPRSV | Determines inventory valuation method |
| Standard Price | Current standard price per base UoM | MBEW-STPRS | Only active when price control = S |
| Moving Average Price | Current MAP per base UoM | MBEW-VERPR | Only active when price control = V |
| Total Stock Value | Current total inventory value | MBEW-SALK3 | |
| Price Unit | Number of units for price (e.g., price per 1, 10, 100) | MBEW-PEINH | |

> **CORRECTION 1:** Valuation Class (BKLAS) is in the **Accounting 1 view (MBEW)**, NOT Basic Data or Purchasing. It is the critical field linking the material to OBYC account determination. Many consultants look for it in Basic Data 1 because "it seems like a general attribute" — it is plant/valuation-area-specific, stored in MBEW.

> **CORRECTION 2:** Price Control (VPRSV) is in the **Accounting 1 view (MBEW)**, NOT MRP or Purchasing. S = Standard Price (PRD fires on GR if PO price differs). V = Moving Average Price (BSX absorbs full PO price, no PRD). When troubleshooting OBYC postings, always check Accounting 1 first.

> **CORRECTION 6:** The **current standard price** used for inventory valuation is MBEW-STPRS (Accounting 1 view). The Costing views hold cost estimates from CO-PC. A cost estimate must be marked and released before it updates MBEW-STPRS. For the operative price, read Accounting 1 — not the Costing view.

> S/4HANA note: Material Ledger is mandatory in S/4HANA (optional in ECC 6). In S/4HANA, moving average price materials also maintain actual cost layer.

### Accounting 2 View (Table: MBEW — Valuation Area Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Tax Data | Tax classification fields | MBEW region | Country-specific tax indicators |

> Accounting 2 is country-specific. Key fields vary by country tax configuration.

### Sales Views (Brief — see SD module for full detail)

Sales views (Sales Org 1/2, Sales General/Plant Data) are maintained in the material master but belong to SD. Key tables: MVKE (Sales Org Data), MARA (general sales fields).

Brief fields of MM relevance:
- MARA-SPART (Division) — set in Basic Data 1
- MVKE-DWERK (Delivering Plant) — links SD to MM plant

> Full sales view coverage deferred to Phase 7 (SD Module Foundation).

### Classification View (Brief)

The Classification view links the material to classes and characteristics (CL01/CL02). Used for variant configuration, batch determination, and material search. Not table-based in the traditional sense — data stored in classification tables (AUSP, CABN, KSSK).

> Classification detail deferred to Phase 12 (scenario playbooks).

### Storage Location Data (Table: MARD — Storage Location Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Unrestricted Stock | Available stock quantity | MARD-LABST | Main stock quantity field |
| Quality Inspection Stock | Stock in QI status | MARD-INSME | |
| Blocked Stock | Unusable stock | MARD-SPEME | |
| Storage Bin | Physical location reference | MARD-LGPBE | Simple bin assignment (not WM) |

---

## Vendor Master

> **S/4HANA note:** In S/4HANA, vendor master (XK01/FK01/MK01, tables LFA1/LFB1/LFM1) is replaced by Business Partner (transaction BP, table BUT000). XK01 and FK01 are obsolete in S/4HANA. In ECC 6.0, the vendor master remains the standard.

T-codes: XK01 (Create Central), XK02 (Change), XK03 (Display), FK01 (Create FI only), MK01 (Create Purchasing only)

The vendor master has three segments:

### LFA1 — General Data (Client Level)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Vendor Number | Unique vendor identifier | LFA1-LIFNR | External or internal number range per account group |
| Name | Vendor name lines | LFA1-NAME1 to NAME4 | Up to 4 lines |
| Search Term | Short search key | LFA1-SORTL | Used in matchcode search |
| Country | Country key | LFA1-LAND1 | Drives tax and address formatting |
| Language | Communication language | LFA1-SPRAS | |
| Tax Numbers | Tax ID fields | LFA1-STCD1 to STCD4 | Country-specific |

### LFB1 — Company Code Data (FI Segment)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Reconciliation Account | GL account for AP sub-ledger | LFB1-AKONT | Must be an AP reconciliation account in SKB1 |
| Payment Terms | Default payment terms | LFB1-ZTERM | Can be overridden at PO level |
| Payment Method | Check, wire, ACH, etc. | LFB1-ZWELS | Must match FBZP payment method config |
| Tolerance Group | Invoice tolerance group | LFB1-TOGRU | Links to OMR6 tolerance limits |
| Withholding Tax | Tax withholding codes | LFB1-QSSKZ | Country-specific |
| Clerk | Internal reference clerk | LFB1-BUSAB | AP clerk assignment |

### LFM1 — Purchasing Organization Data (MM Segment — emphasis per CONTEXT.md)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Purchasing Currency | Currency for POs | LFM1-WAERS | Default currency on purchase orders |
| Payment Terms (Purchasing) | Payment terms for purchasing | LFM1-ZTERM | Overrides LFB1-ZTERM for PO-related invoices |
| Incoterms | Delivery terms | LFM1-INCO1 / INCO2 | e.g., FOB, CIF, DDP + location |
| Minimum Order Value | Min PO amount | LFM1-MINBW | PO below this amount triggers warning |
| Tax Indicator | Default tax code | LFM1-MWSKZ | Purchasing tax indicator |
| GR-Based Invoice Verification | GR required before invoice posting | LFM1-WEBRE | Default for vendor's POs |
| ERS Indicator | Evaluated Receipt Settlement flag | LFM1-LETEFP | Enables MRRL automatic invoicing |
| Order Acknowledgment | Require vendor confirmation | LFM1-AB_BEST | |
| Sales Contact | Vendor sales rep | LFM1-VERKF | |
| Phone | Vendor contact phone | LFM1-TELF1 | |

> **CORRECTION 5:** GR-Based Invoice Verification (WEBRE) is in the **vendor purchasing view (LFM1)**, NOT controlled at the PO document type or company code level. When WEBRE = X, MIRO requires a goods receipt to exist before invoice posting. The flag can also be set at the individual PO line level (EKPO-WEPOS), but the default comes from LFM1.

---

## Purchasing Info Records

T-codes: ME11 (Create), ME12 (Change), ME13 (Display)

Purchasing info records store vendor-specific pricing and delivery data for a material. Two tables:

### EINA — Info Record Header (Vendor + Material)

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Info Record Number | System-generated ID | EINA-INFNR | |
| Vendor | Vendor number | EINA-LIFNR | |
| Material | Material number | EINA-MATNR | Can be blank for non-stock info records |
| Material Group | Material group (if no material number) | EINA-MATKL | Used for text-based info records |
| Deletion Indicator | Marked for deletion | EINA-LOEKZ | |

### EINE — Info Record Purchasing Org Data

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Purchasing Org | Purchasing organization | EINE-EKORG | Key field — info record is per purchasing org |
| Plant | Plant (optional) | EINE-WERKS | If blank, applies to all plants in the purch org |
| Net Price | Vendor price per order unit | EINE-NETPR | Price on PO defaults from here |
| Price Unit | Price per X units | EINE-PEINH | e.g., price per 1, 10, 100 |
| Order Unit | Unit of measure for ordering | EINE-BSTME | May differ from base UoM (MARA-MEINS) |
| Planned Delivery Time | Vendor lead time in days | EINE-APLFZ | MRP uses this for scheduling |
| Minimum Order Quantity | Vendor minimum | EINE-NORBM | |
| Validity Start/End | Price validity period | EINE-DATAB / EINE-DATBI | |
| Incoterms | Delivery terms | EINE-INCO1 / INCO2 | Overrides vendor master if maintained |
| Conditions | Pricing conditions | Via condition tables | Gross price, discounts, surcharges |

> Info records are used by ME59N (automatic PR-to-PO conversion) for source determination. Without a valid info record or source list entry, ME59N cannot automatically create POs.

---

## Source Lists

T-codes: ME01 (Maintain), ME03 (Display)

Source lists define the authorized vendors for a specific material at a specific plant.

### EORD — Source List

Key fields:
| Field | Description | Table.Column | Notes |
|-------|-------------|--------------|-------|
| Material | Material number | EORD-MATNR | |
| Plant | Plant | EORD-WERKS | Source list is per material + plant |
| Validity Start/End | Source validity period | EORD-VDATU / EORD-BDATU | |
| Vendor | Authorized vendor | EORD-LIFNR | |
| Purchasing Org | Purchasing organization | EORD-EKORG | |
| Outline Agreement | Link to contract/scheduling agreement | EORD-EBESSION | Optional — ties source to a specific agreement |
| Fixed Source | Preferred/mandatory source | EORD-FLIFN | If set, this vendor is always used |
| Blocked Source | Vendor blocked for this material | EORD-NOTKZ | Prevents PO creation with this vendor |
| MRP Indicator | MRP-relevant source | EORD-AUTEFP | Source used by MRP for planned order creation |

> Source list maintenance is required per plant when source list requirement is activated (SPRO T-code: OMGM). Without it, ME59N cannot determine the vendor automatically.
