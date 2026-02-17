# Phase 2: Core Reference Framework - Research

**Researched:** 2026-02-16
**Domain:** SAP ECC 6.0 Organizational Structure + ECC vs S/4HANA Disambiguation
**Confidence:** HIGH

## Summary

Phase 2 delivers two content-heavy documents: (1) `reference/org-structure.md` — a comprehensive org structure reference with full field detail, cardinality, tables, T-codes, and cross-module impact for 16 org units, and (2) an expanded `.claude/rules/sap-disambiguation.md` with org-structure-specific S/4HANA rows plus inline blockquote callouts within the org structure reference itself.

This is a pure content-authoring phase — no infrastructure, no scripts, no new directories. The challenge is depth-vs-token-budget: 16 org units at full field detail could exceed the 5,000-token hard cap established in Phase 1. Research below provides the verified SAP domain knowledge (tables, T-codes, relationships, S/4HANA differences) that the planner needs, plus a token budget estimate and splitting recommendation.

**Primary recommendation:** Write `reference/org-structure.md` as one comprehensive file. Estimate lands at ~4,000-5,000 tokens (16,000-20,000 characters), which is within the Phase 1 hard cap for dense reference content. If it exceeds 5,000 tokens, the discretion area allows splitting by domain (FI/CO org units vs. Logistics org units). The disambiguation expansion is straightforward — add 5-8 org-specific rows to the existing table.

---

## 1. Verified Org Unit Domain Knowledge

**Confidence: HIGH** — Cross-referenced across SAP Help Portal, TCodeSearch.com, SAP Community, and multiple SAP tutorial sites.

### 1.1 Complete Org Unit Inventory (16 Units)

The CONTEXT.md specifies Core (12) + Extended (4) = 16 org units. Here is the verified reference data for each.

#### Core Org Units

| Org Unit | Field Code | Primary Table | Creation T-Code | Display T-Code | Parent Assignment |
|----------|-----------|---------------|-----------------|----------------|-------------------|
| Client | MANDT | T000 | SCC4 | SCC4 | (top level) |
| Company Code | BUKRS | T001 | OX02 | OX02 | Client |
| Plant | WERKS | T001W | OX10 | OX10 | Company Code (1:1) |
| Storage Location | LGORT | T001L | OX09 | OX09 | Plant (many:1) |
| Sales Organization | VKORG | TVKO | OVX5 | OVX5 | Company Code (many:1) |
| Distribution Channel | VTWEG | TVTW | OVXI | OVXI | Sales Org (many:many*) |
| Division | SPART | TSPA | OVXB | OVXB | Sales Org (many:many*) |
| Purchasing Organization | EKORG | T024E | OX08 | OX08 | Company Code (many:1) or Plant (many:many) |
| Purchasing Group | EKGRP | T024 | OME4 | OME4 | (not assigned to org unit; assigned in master data) |
| Controlling Area | KOKRS | TKA01 | OKKP | OKKP | Client (spans company codes) |
| Cost Center | KOSTL | CSKS (texts: CSKT) | KS01 | KS03 | Controlling Area |
| Profit Center | PRCTR | CEPC (texts: CEPCT) | KE51 | KE53 | Controlling Area |

*Distribution Channel and Division are assigned TO a Sales Organization via the "Set Up Sales Area" step (T-code OVXG). The Sales Area itself is the combination of Sales Org + Distribution Channel + Division.

#### Extended Org Units

| Org Unit | Field Code | Primary Table | Creation T-Code | Display T-Code | Notes |
|----------|-----------|---------------|-----------------|----------------|-------|
| Business Area | GSBER | TGSB (texts: TGSBT) | OX03 | OX03 | Cross-company-code; assigned at client level |
| Segment | SEGMENT | FAGL_SEGM (texts: FAGL_SEGMT) | (via SPRO) | SM30 V_FAGL_SEGM | Requires New GL + Document Splitting in ECC 6 |
| Functional Area | FKBER | TFKB (texts: TFKBT) | OKBD / FM_FUNCTION | OKBD | Cost-of-sales P&L; 4-char alphanumeric |

Note: Profit Center appears in both Core and Extended in the CONTEXT.md. It is already covered in Core above. In the extended context it is mentioned as "CO-based reporting unit alongside cost centers" — this is the same entity, not a separate one.

### 1.2 Cardinality Rules (Verified)

These are the assignment relationships between org units. Each verified against multiple sources.

| From | To | Cardinality | Assignment T-Code | Notes |
|------|----|-------------|-------------------|-------|
| Plant | Company Code | 1:1 (each plant belongs to exactly one CC) | OX18 | Fundamental; cannot be changed after transactions posted |
| Sales Org | Company Code | many:1 (many sales orgs per CC) | OVX3 | SD billing posts to FI under this CC |
| Purchasing Org | Company Code | many:1 (optional; can be cross-CC) | OX01 | If assigned: company-code-specific purchasing |
| Purchasing Org | Plant | many:many | OX17 | Required for procurement; defines which POrg can procure for which plant |
| Controlling Area | Company Code | 1:many (one CA spans multiple CCs) | OX19 | All CCs must share same chart of accounts and fiscal year variant |
| Distribution Channel | Sales Org | many:many (via Sales Area) | OVXK | Assigned to Sales Org to form part of Sales Area |
| Division | Sales Org | many:many (via Sales Area) | OVXA | Assigned to Sales Org to form part of Sales Area |
| Storage Location | Plant | many:1 (many SLocs per plant) | OX09 | Created within a plant context |
| Cost Center | Controlling Area | many:1 | KS01 | Organized in standard hierarchy |
| Profit Center | Controlling Area | many:1 | KE51 | Organized in standard hierarchy |
| Business Area | Client | many:1 | OX03 | Shared across all company codes |
| Segment | Profit Center | derived | (via PC master data) | Segment is maintained on profit center master record |

### 1.3 Key Configuration Facts Per Org Unit

These details are what the CONTEXT.md means by "every configurable field with description and typical values" and "what is configured AT each org level."

**Client (MANDT)**
- System-level container; all data partitioned by client
- Key field: MANDT (3-digit, e.g., 100, 200, 800)
- Configured at client level: currency decimal format, date format, logon client settings
- Typical values: 000 (SAP reference), 001 (delivery), 100-899 (customizing/production)

**Company Code (BUKRS)**
- 4-character alphanumeric code
- Configured at CC level: company code currency, chart of accounts, fiscal year variant, posting period variant, field status variant, tolerance groups, payment terms, tax settings
- Key fields in T001: BUKRS, BUTXT (name), ORT01 (city), LAND1 (country), WAERS (currency), KTOPL (chart of accounts), PERIV (fiscal year variant), KKBER (credit control area)
- Typical pattern: one CC per legal entity (country-based for tax isolation)

**Plant (WERKS)**
- 4-character alphanumeric code
- Configured at plant level: valuation area (usually = plant), MRP settings, factory calendar, address, batch management settings
- Key fields in T001W: WERKS, NAME1, BWKEY (valuation area), FABKL (factory calendar), KUNNR (customer number of plant for intercompany)
- Typical pattern: one plant per physical location or manufacturing site

**Storage Location (LGORT)**
- 4-character alphanumeric code (within a plant)
- Configured at SLoc level: negative stock allowed, physical inventory settings
- Key fields in T001L: WERKS, LGORT, LGOBE (description)
- Typical pattern: separate SLocs for raw materials, finished goods, QA, scrap

**Sales Organization (VKORG)**
- 4-character alphanumeric code
- Configured at Sales Org level: pricing, credit control area assignment, incoterms
- Key fields in TVKO: VKORG, BUKRS (assigned company code), VKBUR (sales office)
- Typical pattern: one per market region or sales channel

**Distribution Channel (VTWEG)**
- 2-character alphanumeric code
- Configured at DC level: partner determination, pricing conditions
- Key fields in TVTW: VTWEG
- Typical values: 10 (direct sales), 20 (wholesale), 30 (retail)
- Common DC optimization: Define common distribution channels (OVR1) to share master data across DCs

**Division (SPART)**
- 2-character alphanumeric code
- Configured at Division level: material determination, product hierarchy
- Key fields in TSPA: SPART
- Typical values: 01 (product line A), 02 (product line B)
- Common Division optimization: Define common divisions (OVR2) to share master data across divisions

**Sales Area (VKORG + VTWEG + SPART)**
- Not a separate org unit — it is the combination of Sales Org + Distribution Channel + Division
- Set up via OVXG
- All SD master data (customer, pricing, material determination) is maintained per Sales Area

**Purchasing Organization (EKORG)**
- 4-character alphanumeric code
- Three assignment modes: (a) company-code-specific (assigned to one CC), (b) cross-plant within one CC, (c) cross-company-code (not assigned to any CC)
- Key fields in T024E: EKORG, BUKRS (if company-code-specific)
- Typical pattern: one POrg per CC or centralized across CCs

**Purchasing Group (EKGRP)**
- 3-character alphanumeric code
- Not an org unit in the strict hierarchy — it is a buyer or group of buyers
- Configured at client level via OME4
- Assigned in purchasing documents and material master (purchasing view)
- Key field in T024: EKGRP, EKNAM (name), EKTEL (phone)

**Controlling Area (KOKRS)**
- 4-character alphanumeric code
- Configured at CA level: fiscal year variant, operating concern assignment, CO version, cost center and profit center standard hierarchies
- Key fields in TKA01: KOKRS, BEZEI (name), KOINH (CO area currency), KTOPL (chart of accounts), CESSION_ACTIVE (profit center scenario)
- Assignment control: option 1 = "CO area same as company code" (1:1); option 2 = "cross-company-code cost accounting" (1:many)
- All CCs under one CA must share: same chart of accounts, same fiscal year variant

**Cost Center (KOSTL)**
- 10-character alphanumeric code
- Configured per cost center: responsible person, category (production, admin, sales, R&D), currency, hierarchy area
- Key fields in CSKS: KOSTL, BUKRS (company code), KOSAR (category), VERAK (responsible person), WAERS (currency)
- Organized in standard hierarchy (required, defined in OKEON/KSH1)

**Profit Center (PRCTR)**
- 10-character alphanumeric code
- Configured per profit center: responsible person, segment (for IFRS reporting), hierarchy area
- Key fields in CEPC: PRCTR, BUKRS (company code), SEGMENT (if New GL), VERAK (responsible person)
- Organized in standard hierarchy (required, defined in KCH1)

**Business Area (GSBER)**
- 4-character alphanumeric code
- Cross-company-code reporting entity — shared at client level
- Originally used for cross-CC balance sheets; largely superseded by profit center/segment reporting
- Derived automatically from plant/division combination or entered manually
- SAP recommendation: use profit center instead of business area for new implementations

**Segment (SEGMENT)**
- 10-character alphanumeric code
- Requires New GL (FAGL) activation in ECC 6 + document splitting active
- Used for IFRS 8 / US GAAP ASC 280 segment reporting
- Derived from profit center master data (field SEGMENT in CEPC) during posting
- Not entered manually on documents — always derived

**Functional Area (FKBER)**
- 4-character alphanumeric code
- Used for cost-of-sales P&L reporting (as opposed to total-cost P&L)
- Categories: Production, Administration, Sales & Marketing, R&D, etc.
- Derived from cost center (via substitution) or entered on GL account master
- Niche usage — mainly relevant for companies required to report cost-of-sales format

---

## 2. S/4HANA Differences for Org Structure

**Confidence: HIGH for major items, MEDIUM for nuanced items** — Verified against SAP Press, SAP Community, SAP Learning, and multiple SAP consultant sources.

### 2.1 Org-Structure-Specific S/4HANA Differences

These are differences that should appear as inline `> S/4HANA:` callouts within the org structure reference AND as new rows in `sap-disambiguation.md`.

| Org Unit / Area | ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|----------------|--------|
| Controlling Area assignment | 1:many supported (one CA spans multiple CCs); option 1 or 2 in OKKP | Strongly recommended 1:1 (CA = CC). Company code validation in OKKP is mandatory and cannot be deactivated. Cross-CC allocation still technically possible but discouraged. | New implementations default to 1:1. Migrations may retain 1:many but face restrictions. |
| Vendor/Customer Master | Separate vendor (LFA1) and customer (KNA1) masters; T-codes XK01, FK01, MK01, XD01, FD01, VD01 | Business Partner (BP transaction, BUT000 table). CVI synchronizes BP with legacy KNA1/LFA1 tables. Old T-codes work via compatibility views but are deprecated. | Mandatory CVI conversion before S/4 migration. |
| Cost Element | Separate primary/secondary cost element master (KA01/KA06); table CSKA/CSKB | Cost elements are GL accounts — no separate master data. Primary cost elements = P&L GL accounts. Secondary = category 90 accounts. | T-codes KA01/KA06 obsolete. Maintain via FS00. |
| Profit Center Accounting | Separate PCA ledger in EC-PCA (tables GLPCA, GLPCT); optional real-time update | Integrated into Universal Journal (ACDOCA). Real-time, no separate ledger. Profit center is a standard dimension. | Tables GLPCA removed. All reporting from ACDOCA. |
| Segment Reporting | Requires New GL activation + document splitting in ECC 6 | Always available — document splitting and segment derive from profit center natively. | Lower barrier to entry for segment reporting. |
| Business Area | Functional but discouraged. Used for cross-CC balance sheets. | Still functional but further discouraged. SAP recommends profit center and segment for all internal and external reporting. | No technical removal, but best practice is to migrate away. |
| Material Ledger | Optional per plant (activate in CKMLCP) | Mandatory, always active. Part of ACDOCA. Cannot be deactivated. | Impacts valuation in every plant. |
| General Ledger | Classic GL or New GL (FAGL). Separate tables (GLT0 classic, FAGLFLEXT new). | Universal Journal (ACDOCA). Single table for FI+CO+ML+PCA. | All GL reporting from ACDOCA. |
| Functional Area | Optional, requires configuration for cost-of-sales reporting | Still optional but easier to implement — functional area derivation improved in S/4. | Minor simplification. |

### 2.2 Org Units With NO Significant S/4 Differences

These org units function identically in ECC 6 and S/4HANA:

- **Client** — Same concept, same table (T000)
- **Company Code** — Same table (T001), same creation T-code (OX02)
- **Plant** — Same table (T001W), same creation T-code (OX10)
- **Storage Location** — Same table (T001L), same creation T-code (OX09)
- **Sales Organization** — Same table (TVKO), same creation T-code (OVX5)
- **Distribution Channel** — Same table (TVTW), same creation T-code (OVXI)
- **Division** — Same table (TSPA), same creation T-code (OVXB)
- **Purchasing Organization** — Same table (T024E), same creation T-code (OX08)
- **Purchasing Group** — Same table (T024), same creation T-code (OME4)

**Recommendation for Claude's Discretion area:** For org units with no S/4 differences, omit the inline callout entirely (don't clutter with "no change"). In the consolidated S/4 summary table at the end of org-structure.md, include a brief note: "Client, Company Code, Plant, Storage Location, Sales Org, Distribution Channel, Division, Purchasing Org, Purchasing Group — no significant org-structure-level changes in S/4HANA."

---

## 3. Cross-Module Assignment Consequences

**Confidence: HIGH** — Standard SAP integration knowledge, verified across sources.

These "downstream consequences" are what the CONTEXT.md means by "cross-module assignment consequences."

| Assignment | Consequence |
|------------|-------------|
| Plant -> Company Code | Goods movements in MM (MIGO) generate FI postings in this company code's books. Valuation area typically = plant, so inventory valuation is under this CC. |
| Sales Org -> Company Code | SD billing documents (VF01) create FI accounting documents in this company code. Revenue and receivables post here. |
| Purchasing Org -> Company Code | Purchase orders and invoice verification (MIRO) generate FI postings in this company code. |
| Controlling Area -> Company Code | All cost postings (to cost centers, internal orders, profit centers) within this CC are managed under this CA. CA must share chart of accounts with all assigned CCs. |
| Cost Center -> Controlling Area | Cost center postings (labor, overhead) are reported and allocated within this CA. Settlements cross CC boundaries only within the same CA. |
| Profit Center -> Segment | Whenever a document posts to a profit center, the segment is derived from the PC master data. This enables segment-level financial statements (requires New GL + document splitting). |
| Business Area derivation | Business area is derived from plant + division during SD billing and MM goods movements. This enables cross-CC balance sheet reporting by business area. |
| Sales Area (VKOrg + VTW + SPT) | Customer master data, pricing conditions, and material determination are all maintained per Sales Area. Changing the Sales Area combination affects which master data is referenced. |
| Purchasing Org -> Plant (many:many) | Determines which purchasing org can create POs for which plant. A plant can be serviced by multiple POrgs (e.g., central + local). |

---

## 4. Token Budget Analysis

**Confidence: MEDIUM** — Estimates based on character-count heuristic (chars/4) from Phase 1 research.

### 4.1 Estimated Content Size

The org-structure.md file needs to contain:

| Section | Content | Estimated Characters | Estimated Tokens |
|---------|---------|---------------------|-----------------|
| Frontmatter + introduction | YAML + 3-line intro | 400 | 100 |
| ASCII hierarchy tree (expanded) | Full tree with all 16 units | 1,200 | 300 |
| Per-unit detail tables (16 units) | ~600-800 chars each: field table + notes | 10,000-12,800 | 2,500-3,200 |
| Cardinality reference table | One table, ~12 rows | 1,200 | 300 |
| Cross-module consequences table | One table, ~9 rows | 1,000 | 250 |
| Inline S/4 callouts | ~8 callouts * 150 chars | 1,200 | 300 |
| Consolidated S/4 summary table | One table, ~10 rows | 1,500 | 375 |
| Cross-references | 5-8 forward links | 400 | 100 |
| **Total** | | **17,000-19,000** | **4,250-4,750** |

### 4.2 Budget Assessment

- Phase 1 established a **5,000-token hard cap** for dense reference content
- Estimated range: **4,250-4,750 tokens** — within budget but close to the cap
- The file is intentionally dense (lookup reference, not prose)

### 4.3 Splitting Strategy (If Needed)

If the final file exceeds 5,000 tokens:

**Option A (recommended):** Tighten per-unit detail tables. Use abbreviations in "Typical Values" column. Remove most verbose explanations. Target: save 500-800 tokens.

**Option B:** Split into two files:
- `reference/org-structure.md` — hierarchy tree, cardinality, cross-module consequences (~2,500 tokens)
- `reference/org-structure-detail.md` — per-unit field detail tables, S/4 callouts (~2,500 tokens)
- Add both to `reference/CLAUDE.md` index

**Recommendation:** Start with one file. Only split if actual character count exceeds 20,000 (5,000 tokens). The planner should include a verification step that checks character count after content is written.

---

## 5. Existing Content to Extend (Not Duplicate)

**Confidence: HIGH** — Direct reading of existing files.

### 5.1 sap-org-structure.md (Always-Loaded Rule)

The existing `.claude/rules/sap-org-structure.md` (created in Phase 1) contains:
- ASCII tree with 9 org units (Client, Company Code, Plant, Storage Location, Business Area, Controlling Area, Cost Center, Profit Center, Sales Org, Distribution Channel, Division, Purchasing Org, Purchasing Group)
- Key assignments section with 4 cardinality rules
- Total: ~28 lines, ~112 characters per line average = ~3,136 chars = ~784 tokens

**Phase 2 action:** This file stays as-is (it is the compact, always-loaded summary). The new `reference/org-structure.md` is the comprehensive reference that Claude reads on-demand when detailed org structure questions arise. The rules file should get a cross-reference added: "For full detail, see `reference/org-structure.md`".

### 5.2 sap-disambiguation.md (Always-Loaded Rule)

The existing `.claude/rules/sap-disambiguation.md` has 12 rows covering:
- Vendor master, Customer master, Material documents, Material Ledger, General Ledger, Document splitting, COGS, Reporting, UI, Credit management, Output management, MRP

**Phase 2 action:** Add 5-8 new rows for org-structure-specific S/4 differences:
1. Controlling Area assignment (1:1 enforcement)
2. Cost element (no separate master)
3. Profit Center Accounting (in Universal Journal)
4. Segment reporting (always available)
5. Business Area (further discouraged)

Must stay within the combined rules token budget (~1,500 total for all 3 rules files). Current combined estimate from Phase 1 STATE.md: ~809 tokens. Adding 5-8 rows (~40-60 chars each) = ~200-300 additional chars = ~50-75 tokens. New total: ~860-885 tokens. Well within budget.

### 5.3 reference/CLAUDE.md (Index)

Current index has: movement-types.md, document-types.md, posting-keys.md.

**Phase 2 action:** Add `org-structure.md` entry to the File Index table with appropriate "Read When" guidance.

---

## 6. Architecture Patterns

### 6.1 Recommended Document Structure for org-structure.md

```markdown
---
module: reference
content_type: org-structure
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-16
---

# SAP ECC 6.0 — Organizational Structure Reference

> Comprehensive reference for all org units...

## Hierarchy

[ASCII tree — expanded version of .claude/rules/sap-org-structure.md]

## Org Unit Details

### Client (MANDT)
| Field | Description | Typical Values |
|-------|-------------|----------------|
| ... | ... | ... |

**Table:** T000 | **T-Code:** SCC4 (create/display)
**Configured here:** [what is set at this level]

> S/4HANA: [inline callout if applicable]

### Company Code (BUKRS)
[same pattern]
...

## Assignment Rules

| From | To | Cardinality | T-Code | Impact |
...

## Cross-Module Consequences

| Assignment | Downstream Impact |
...

## S/4HANA Differences Summary

| Area | ECC 6 | S/4HANA | Impact |
...

See also: `.claude/rules/sap-disambiguation.md` for non-org-structure S/4 differences.
```

### 6.2 Anti-Patterns to Avoid

- **Duplicating the always-loaded tree:** The compact tree in `.claude/rules/sap-org-structure.md` must remain lean. Do not bloat it with Phase 2 detail. Instead, the comprehensive reference file is read on-demand.
- **Prose-heavy org unit descriptions:** This is a reference file, not a textbook. Use tables for structured data, bullet points for notes, and blockquotes only for S/4 callouts. Minimize paragraph text.
- **Forgetting forward cross-references:** The org-structure reference will mention T-codes, config paths, and integration points that are not yet populated (Phases 3-10). Use explicit forward references: "See `modules/fi/tcodes.md`" — even though those files are currently templates. This establishes the navigation pattern.
- **Mixing ECC and S/4 content in main flow:** S/4 differences go in clearly delineated callouts and the summary table, never in the main ECC 6 content. This is the established convention from Phase 1.

---

## 7. Common Pitfalls

### Pitfall 1: Controlling Area Cardinality Confusion
**What goes wrong:** Stating that ECC requires 1:1 controlling area to company code, or that S/4HANA requires 1:1.
**Truth:** ECC supports both 1:1 and 1:many (set via OKKP assignment control). S/4HANA *strongly recommends* 1:1 and enforces company code validation (cannot be deactivated), but 1:many still technically works for on-premise installations with migration scenarios. S/4HANA Cloud Public Edition enforces a single controlling area (A000).
**How to avoid:** State ECC supports both modes, note S/4HANA recommendation clearly, distinguish between on-premise and cloud.

### Pitfall 2: Purchasing Org Assignment Modes
**What goes wrong:** Stating that Purchasing Org is always assigned to a Company Code.
**Truth:** There are three modes: (a) assigned to one CC = company-code-specific, (b) assigned to CC and plant = cross-plant within CC, (c) NOT assigned to any CC = cross-company-code purchasing. Mode (c) means the POrg can procure for plants in different CCs.
**How to avoid:** Document all three modes explicitly.

### Pitfall 3: Sales Area is Not a Separate Org Unit
**What goes wrong:** Treating Sales Area as an independent org unit with its own table and T-code.
**Truth:** Sales Area is the *combination* of Sales Org + Distribution Channel + Division. It has no separate master data table. The combination is set up via OVXG but is not independently maintained.
**How to avoid:** Describe it as a derived combination, not a standalone entity.

### Pitfall 4: Business Area vs. Profit Center
**What goes wrong:** Treating business areas and profit centers as interchangeable.
**Truth:** Business areas are cross-CC reporting entities derived from plant+division during posting. Profit centers are CO entities with their own hierarchy, settled through PCA. Both can produce internal balance sheets, but business areas are legacy and SAP recommends profit centers + segments for new implementations.
**How to avoid:** Document both, note the SAP recommendation, explain derivation logic for business areas.

### Pitfall 5: Segment Requires New GL in ECC 6
**What goes wrong:** Describing segment reporting as always available in ECC 6.
**Truth:** Segment is only available if New GL (FAGLFLEXT) is activated AND document splitting is configured. Classic GL does not support segments. This is a significant ECC 6 constraint that does not exist in S/4HANA (where it is always available).
**How to avoid:** Explicitly note the New GL prerequisite for ECC 6.

### Pitfall 6: Token Budget Overrun
**What goes wrong:** Writing verbose prose descriptions per org unit, exceeding the 5,000-token cap.
**How to avoid:** Use the table-first format (field | description | typical values). Keep explanatory text to 2-3 bullet points per org unit. Run character count verification after writing.

---

## 8. Don't Hand-Roll

Problems that look simple but have nuance:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Org unit hierarchy visualization | Custom nested markdown | ASCII tree diagram (already established in Phase 1) | ASCII trees are compact, readable, and the established convention |
| S/4 difference tracking | Separate S/4 reference file | Inline callouts + consolidated table (dual approach from CONTEXT.md) | Keeps ECC and S/4 info co-located for easy navigation |
| Cardinality documentation | Prose descriptions of relationships | Structured table with From/To/Cardinality/T-Code columns | Tables are scannable; prose is ambiguous for many:many relationships |
| Cross-reference links | Implicit "see module X" | Explicit backtick paths: "See `modules/fi/tcodes.md`" | Explicit paths enable validation scripts to check reference integrity |

---

## 9. Code Examples (Content Templates)

### 9.1 Per-Unit Detail Block Template

```markdown
### Company Code (BUKRS)

| Field | Description | Typical Values |
|-------|-------------|----------------|
| BUKRS | Company code key | 4-char, e.g., 1000, US01, DE01 |
| BUTXT | Company name | Legal entity name |
| ORT01 | City | Company headquarters city |
| LAND1 | Country key | 2-char ISO, e.g., US, DE, GB |
| WAERS | Local currency | 3-char ISO, e.g., USD, EUR, GBP |
| KTOPL | Chart of accounts | 4-char, e.g., INT, CAUS, CADE |
| PERIV | Fiscal year variant | 2-char, e.g., K4 (calendar year) |

**Table:** T001 | **Create:** OX02 | **Display:** OX02
**Configured here:** Fiscal year variant, chart of accounts, local currency, posting period variant, field status variant, tolerance groups, tax settings

**Common pattern:** One company code per legal entity. Country-based separation for tax isolation (e.g., US01 for US operations, DE01 for Germany).

**Cross-module impact:** All MM goods movements (MIGO) and SD billing (VF01) from plants/sales orgs assigned to this CC generate FI postings here.

> S/4HANA: No significant structural change. Company code remains the core FI org unit. Universal Journal (ACDOCA) replaces separate FI/CO tables but CC concept is unchanged.

See: `modules/fi/config-spro.md` for company code configuration paths
```

### 9.2 Inline S/4 Callout Style

```markdown
> S/4HANA: Vendor master (LFA1) and customer master (KNA1) replaced by Business Partner (BP transaction, BUT000 table). Old T-codes (XK01, FK01, MK01) work via CVI compatibility views but are deprecated. Mandatory CVI conversion required before S/4 migration.
```

### 9.3 Consolidated S/4 Summary Table Style

```markdown
## S/4HANA Differences Summary

| Area | ECC 6 Behavior | S/4HANA Change | Impact |
|------|---------------|----------------|--------|
| Controlling Area | 1:many CC assignment via OKKP | 1:1 strongly recommended; CC validation mandatory | New implementations use 1:1 |
| Cost Elements | Separate master (KA01/KA06, CSKA/CSKB) | GL accounts serve as cost elements; no separate master | KA01/KA06 obsolete |
| Profit Center Accounting | Separate PCA ledger (EC-PCA, GLPCA) | Integrated in Universal Journal (ACDOCA) | Real-time, no reconciliation needed |
| Segment Reporting | Requires New GL + document splitting | Always available natively | Lower barrier to entry |
| Business Area | Functional, used for cross-CC reporting | Further discouraged; use PC + segment | No removal, but migration recommended |

Client, Company Code, Plant, Storage Location, Sales Org, Distribution Channel, Division, Purchasing Org, Purchasing Group — no significant org-structure-level changes in S/4HANA.
```

---

## 10. Implementation Sequence Recommendation

Based on the analysis, Phase 2 should have **2 plans**:

### Plan 1: Org Structure Reference Document
- Create `reference/org-structure.md` with all 16 org units
- Full content writing: ASCII tree, per-unit detail tables, cardinality rules, cross-module consequences, inline S/4 callouts, consolidated S/4 summary table
- Update `reference/CLAUDE.md` index to include the new file
- Add cross-reference in `.claude/rules/sap-org-structure.md` pointing to the comprehensive reference
- Verify: character count check (must be under 20,000 chars / 5,000 tokens)
- Verify: all 16 org units covered with table, T-code, and at least 3 key fields each

### Plan 2: Disambiguation Framework Expansion
- Expand `.claude/rules/sap-disambiguation.md` with 5-8 org-structure-specific S/4 rows
- Verify: combined rules files token budget still under 1,500
- Verify: each new row follows the established 3-column format (ECC 6 Behavior | S/4HANA Change | Impact)
- Verify: forward cross-references to `reference/org-structure.md` where appropriate

**Why this order:**
- Plan 1 is the bulk of the work (content authoring for org-structure.md). It can be done independently.
- Plan 2 is smaller (adding rows to an existing file) and should reference the org-structure.md for consistency. However, it has no hard dependency — the disambiguation rows can be written without the org-structure file existing first.
- Both plans can run in parallel if needed, but sequential is cleaner for consistency.

---

## 11. Open Questions

### 1. Exact Field Lists Per Org Unit
**What we know:** The primary table and key fields for each org unit are verified. The CONTEXT.md asks for "every configurable field."
**What's unclear:** Listing truly every configurable field would make each org unit section very long (T001 alone has 100+ fields). The practical interpretation is "every field that an SAP functional consultant needs to know about" — typically 5-10 key fields per org unit.
**Recommendation:** Include 5-10 key fields per org unit in the detail table. Add a note: "For complete field list, see table [TABLE_NAME] via SE11." This keeps the reference actionable without becoming an ABAP data dictionary dump.

### 2. Token Count Accuracy
**What we know:** Character/4 heuristic gives ~15% margin of error.
**What's unclear:** Exact token count for the final file.
**Recommendation:** Run the Phase 1 validation script after writing the content. If the script is not yet functional (validation scripts were Plan 01-03), use `wc -c` and divide by 4 as the heuristic.

---

## Sources

### Primary (HIGH confidence)
- [TCodeSearch.com - SAP Tables and T-Codes](https://www.tcodesearch.com) — Verified table names (T001, T001W, T001L, TVKO, TVTW, TSPA, T024E, T024, TKA01, CSKS, CEPC, TGSB, FAGL_SEGM, TFKB) and T-codes (OX02, OX10, OX09, OVX5, OVXI, OVXB, OX08, OME4, OKKP, KS01, KE51, OX03, OKBD)
- [SAP Help Portal - Assigning Controlling Areas](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/5e23dc8fe9be4fd496f8ab556667ea05/7ae7ed5142de7131e10000000a174cb4.html) — Controlling area assignment rules
- [LeanX - SAP Table Reference](https://leanx.eu/en/sap/table/) — Table field verification for T001, T001W, TVKO, TKA01

### Secondary (MEDIUM confidence)
- [SAP Press - Key Differences ECC vs S/4HANA](https://blog.sap-press.com/key-differences-between-sap-ecc-and-sap-s4hana-a-detailed-comparison) — Business Partner consolidation, Universal Journal, Material Ledger changes
- [SAP Community - Controlling Area and Company Code](https://community.sap.com/t5/enterprise-resource-planning-q-a/controlling-area-and-its-relation-with-company-code/qaq-p/12567587) — 1:1 vs 1:many discussion
- [SAP Community - S/4HANA OKKP Company Code Validation](https://community.sap.com/t5/enterprise-resource-planning-q-a/s4-hana1709-deactivate-co-company-code-validation-indicator-okkp/qaq-p/528036) — Mandatory CC validation in S/4HANA
- [SAP Community - Profit Center and Segment Structures](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/mastering-cost-center-profit-center-amp-segment-structures-in-sap-s-4hana/ba-p/13708698) — Segment derivation from profit center
- [SAP Online Tutorials - Enterprise Structure T-codes](https://www.saponlinetutorials.com/) — Creation T-codes and assignment T-codes
- [TutorialsPoint - SAP MM Organizational Units](https://www.tutorialspoint.com/sap_mm/sap_mm_organizational_units.htm) — Purchasing org assignment modes

### Tertiary (LOW confidence)
- Token budget estimates — based on character count heuristic, not measured. Needs validation after content authoring.

## Metadata

**Confidence breakdown:**
- Org unit domain knowledge: HIGH — Multiple sources cross-referenced for all 16 org units, tables, and T-codes
- S/4HANA differences: HIGH (major items) / MEDIUM (nuanced items like controlling area enforcement level)
- Architecture/format: HIGH — Follows established Phase 1 conventions
- Token budget: MEDIUM — Heuristic-based estimation, needs empirical validation
- Pitfalls: HIGH — Drawn from verified domain knowledge contradictions

**Research date:** 2026-02-16
**Valid until:** Indefinitely (SAP ECC 6.0 org structure is stable; no further ECC releases)
