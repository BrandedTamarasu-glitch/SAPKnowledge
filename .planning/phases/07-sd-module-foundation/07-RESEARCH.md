# Phase 7: SD Module Foundation - Research

**Researched:** 2026-02-17
**Domain:** SAP ECC 6.0 Sales & Distribution (SD) module content authoring
**Confidence:** HIGH

## Summary

Phase 7 delivers complete SD reference content following the same structural patterns established in Phases 3 (FI) and 5 (MM). The SD module is the third of four module foundations. All four deliverables (tcodes.md, master-data.md, processes.md, config-spro.md) follow locked formats from prior phases. The CLAUDE.md index already exists with the correct file structure.

SD is the broadest of the four modules in submodule coverage: sales order processing, shipping/delivery, billing, pricing (condition technique), output determination, credit management, returns, rebates, consignment, third-party processing, and foreign trade. This breadth drives the upper T-code target (65-80) and creates a large config-spro.md file. The condition technique is the central architectural concept in SD — it drives pricing, output determination, account determination, and text determination through a common framework (condition tables, access sequences, condition types, procedure).

**Primary recommendation:** Author all four content files following FI/MM patterns exactly, with SD-specific depth on the condition technique (pricing, output, account determination) and copy control as the two most complex configuration areas.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

#### T-code Coverage Scope
- Full breadth across all SD submodules: Sales (VA01-VA03), Shipping/Delivery (VL01N-VL06), Billing (VF01-VF04), Pricing (VK11-VK13), Output Determination (VV31-VV33, NACE), Credit Management (FD32, VKM1-VKM5), Returns, Rebates (VBO1-VBO3), Foreign Trade, Batch Determination
- Target 65-80 T-codes (upper range due to SD's broader submodule coverage)
- Follow the same format as FI and MM: frontmatter + workflow index table + ### submodule sections
- Pricing T-codes should include condition technique detail inline (access sequences, condition tables, V/06)

#### Master Data Structure
- Single file (master-data.md) consistent with FI and MM pattern
- Full customer master: all three levels (general KNA1, company code KNB1, sales area KNVV) with SD emphasis — self-contained, not just SD views
- Include condition records (pricing master data) in detail: KONH/KONP tables, condition types (PR00, K004, K005, MWST), access sequences, validity periods
- Include output determination master data: output types, condition records for output (print, EDI, email), partner-based output determination

#### Order-to-Cash Process Depth
- Full variant coverage: standard O2C, returns (RMA), credit/debit memos, cash sales, rush orders, consignment (fill-up/issue/pickup/return), third-party processing
- Include document flow diagrams showing the complete document chain: inquiry -> quotation -> order -> delivery -> PGI -> billing doc -> FI doc with table references (VBAK/VBAP -> LIKP/LIPS -> VBRK/VBRP)
- Include availability check (ATP) and credit check as inline process steps
- Follow the same narrative-plus-table format with role annotations used in FI and MM processes

#### SPRO Configuration Scope
- Full breadth: enterprise structure, sales document types, item categories, schedule line categories, delivery types, billing types, pricing procedure assignment (OVKK), condition types, access sequences, output determination (NACE), partner determination, copy control, text determination, incompletion procedures, availability check, credit management config
- Full copy control documentation: VTAA, VTLA, VTFL, VTAF with key fields at header + item level, requirements, data transfer routines
- Item category determination logic: document the 4-key determination in OVLP/VOV4
- Single file (config-spro.md) consistent with FI and MM pattern

### Claude's Discretion
- Exact T-code count within the 65-80 range
- How deep to go on foreign trade and rebate T-codes (foundation level is fine)
- Whether to include incomplete document flow variants (inquiry and quotation are optional)
- Level of detail on credit management config vs deferring deep credit to Phase 8
- How to handle the large volume of SD config in a single file (section organization)

### Deferred Ideas (OUT OF SCOPE)
None specified.

</user_constraints>

## Standard Stack

This phase produces markdown reference content, not software. The "stack" is the established content patterns from prior phases.

### Core Patterns (from Phases 3 and 5)

| Pattern | Source | Purpose | Applies To |
|---------|--------|---------|------------|
| Frontmatter + workflow index + submodule sections | FI tcodes.md, MM tcodes.md | T-code reference structure | SD tcodes.md |
| Single master-data.md with table-per-segment format | FI master-data.md, MM master-data.md | Master data reference | SD master-data.md |
| Narrative-plus-table with role annotations | FI processes.md, MM processes.md | Business process flows | SD processes.md |
| SPRO step-by-step with IMG path + T-code | FI config-spro.md, MM config-spro.md | Configuration reference | SD config-spro.md |
| CORRECTION note blocks | FI/MM master-data.md | Flag commonly-wrong field locations | SD master-data.md |
| S/4HANA callout at section header (not per-field) | FI master-data.md (customer master) | Disambiguation without contamination | SD master-data.md (customer master) |

### Validation Constraints

| Constraint | Source | Value |
|-----------|--------|-------|
| Token budget (tcodes) | validate.py | 5000 tokens (~20,000 chars) |
| Token budget (config-spro) | validate.py | 5000 tokens (~20,000 chars) |
| Token budget (processes) | validate.py | 4000 tokens (~16,000 chars) |
| Token budget (master-data) | validate.py | 4000 tokens (~16,000 chars) |
| Required frontmatter fields | validate.py | module, content_type, ecc_version, ehp_range, confidence, last_verified |
| Valid module value | validate.py | "sd" |
| S/4HANA contamination check | validate.py | MATDOC, ACDOCA, Universal Journal = CRITICAL; Business Partner = WARNING (allowed in S/4HANA callout sections) |

**Token budget concern:** SD config-spro.md will be the largest file in the knowledge base due to the breadth of SD configuration (condition technique, copy control, item category determination, partner determination, output determination, availability check, credit management). The 5000-token budget (~20,000 chars) may be tight. Prior decision from Phase 6 (06-03): token budget warnings are accepted for large content files.

## Architecture Patterns

### Recommended File Structure (SD Module)

All files already exist as stubs in `modules/sd/`. Phase 7 populates four of them:

```
modules/sd/
├── CLAUDE.md           # Already populated — update File Index "Read When" guidance
├── tcodes.md           # Phase 7: SD-01
├── config-spro.md      # Phase 7: SD-02
├── processes.md        # Phase 7: SD-03
├── master-data.md      # Phase 7: SD-04
├── integration.md      # Phase 8 (deferred)
└── patterns.md         # Phase 12 (deferred)
```

### Pattern 1: tcodes.md Structure

**What:** Frontmatter + workflow index table + submodule sections with ### headings per T-code.

**Established format (from FI/MM):**
- Workflow index table at top: Process Stage | T-code(s) | Submodule | Notes
- Each T-code gets a ### heading with: Menu Path, Usage paragraph, Gotcha (optional)
- Submodule sections separated by `---` horizontal rules
- T-codes grouped by business function, not alphabetically

**SD-specific submodule sections (recommended):**
1. Sales Documents (VA01-VA05, VA41-VA43, VA31-VA33, VA11-VA13)
2. Shipping & Delivery (VL01N-VL06, VL10A-VL10H, VT01N-VT03N)
3. Billing (VF01-VF04, VF11, VF21-VF27, VFX3)
4. Pricing (VK11-VK13, V/06, V/07, V/08, V/09)
5. Output Determination (VV31-VV33, NACE, VV21-VV23)
6. Credit Management (FD32, VKM1-VKM5, OVA8)
7. Returns & Complaints (VA01 with doc type RE, VL01N return delivery)
8. Rebates (VBO1-VBO3, VBOF)
9. Reporting & Analysis (VA05, VF05, VL06O, MC+)
10. Master Data (VD01-VD03, XD01-XD03, VD51-VD53, BP cross-ref)

### Pattern 2: master-data.md Structure

**What:** Single file with table-per-segment format, CORRECTION blocks, S/4HANA callout.

**SD-specific content sections (recommended):**
1. Customer Master (all three levels — self-contained)
   - KNA1: General Data (client level) — address, industry, tax numbers
   - KNB1: Company Code Data — reconciliation account, payment terms, dunning
   - KNVV: Sales Area Data — pricing, shipping, billing, partner functions, account assignment groups
   - S/4HANA note: Business Partner replacement (one callout at section header)
2. Condition Records (Pricing Master Data)
   - KONH: Condition Record Header — condition type, key combination, validity
   - KONP: Condition Record Item — rate, amount, currency, scales
   - Standard condition types: PR00 (base price), K004/K005 (material/customer discounts), MWST (tax), RA00 (rebate)
   - Access sequences: how the system searches for condition records
3. Output Determination Master Data
   - Output types: BA00 (order confirmation), LD00 (delivery note), RD00 (billing document)
   - Condition records for output: medium (print/fax/EDI/email), timing, partner
   - NACE navigation: application, output type, access sequence
4. Material Master Sales Views (brief, cross-reference to MM master-data.md)
   - MVKE: Sales Organization Data — delivering plant, item category group, account assignment group material
   - MARA sales-relevant fields: division (SPART), cross-distribution-chain status

**CORRECTION blocks to include (known common mistakes):**
- KVGR1-5 are in KNVV, not KNB1 (already in FI master-data.md — reinforce in SD context)
- KTGRD (customer account assignment group) is in KNVV Billing tab, not KNA1
- KTGRM (material account assignment group) is in MVKE (Sales Org 2 view), not MARA
- Delivering plant (DWERK) is in MVKE, not MARC

### Pattern 3: processes.md Structure

**What:** Narrative-plus-table format with role annotations at each step.

**SD-specific process variants (per locked decision):**

1. **Standard Order-to-Cash** (primary process — most detailed)
   - Inquiry (VA11) -> Quotation (VA21) -> Sales Order (VA01) -> Delivery (VL01N) -> PGI (VL02N) -> Billing (VF01) -> FI Document (automatic)
   - Document flow: VBAK/VBAP -> LIKP/LIPS -> VBRK/VBRP -> BKPF/BSEG
   - Inline: availability check (ATP) at VA01, credit check at VA01/VL01N
   - Roles: Sales Rep, Shipping Clerk, Billing Clerk, AR Accountant

2. **Returns (RMA)**
   - Returns order (VA01, doc type RE) -> Return delivery (VL01N) -> Goods receipt of returns (MIGO or VL02N) -> Credit memo request (VA01, doc type CR) or billing (VF01, doc type RE)

3. **Credit/Debit Memos**
   - Credit memo request (VA01, doc type CR) -> Credit memo billing (VF01) -> FI posting
   - Debit memo request (VA01, doc type DR) -> Debit memo billing (VF01) -> FI posting

4. **Cash Sales & Rush Orders**
   - Cash sale (VA01, doc type CS) -> immediate delivery + billing in one step
   - Rush order (VA01, doc type RO) -> delivery created automatically

5. **Consignment**
   - Fill-up (VA01, doc type KB) -> Consignment issue (VA01, doc type KE) -> Consignment pickup/returns (VA01, doc type KR/KA)

6. **Third-Party Processing**
   - Sales order (VA01, item cat TAS) -> automatic PR to vendor -> vendor ships direct to customer -> MIRO invoice -> billing to customer

### Pattern 4: config-spro.md Structure

**What:** SPRO step-by-step with IMG path + T-code, organized by functional area.

**SD-specific section organization (discretion area — recommendation):**

Given the volume of SD configuration, organize into 8 major sections:

1. **Enterprise Structure** — Sales org, distribution channel, division, sales area assignment, shipping point assignment
2. **Sales Document Types** — VOV8 (define), OVAZ (assign number ranges), item categories (VOV7), schedule line categories (VOV6), item category determination (OVLP/VOV4)
3. **Pricing** — Condition technique core: V/06 (condition tables), V/07 (access sequences), V/08 (condition types), V/09 (pricing procedures), OVKK (pricing procedure determination/assignment)
4. **Copy Control** — VTAA (order-to-order), VTLA (order-to-delivery), VTFL (delivery-to-billing), VTAF (billing-to-order) with key fields, requirements, data transfer routines
5. **Delivery** — Delivery types (OVLK), shipping point determination (OVXC), route determination (OVTC), picking/packing
6. **Billing** — Billing types (VOFA), billing plan types, revenue account determination (VKOA brief cross-ref to FI account-determination.md)
7. **Output Determination** — NACE procedure, output types, access sequences for output, medium/timing config
8. **Supporting Functions** — Partner determination, text determination, incompletion procedures, availability check control (OVZ2), credit management config (OVA8 brief)

### Pattern 5: CLAUDE.md Update

The existing SD CLAUDE.md needs its File Index updated with specific "Read When" guidance (per 03-04 decision), matching the level of specificity in FI and MM CLAUDE.md files.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Condition technique explanation | One-off inline explanations per pricing/output/text | Single reusable explanation of the 4-layer model (condition table -> access sequence -> condition type -> procedure) at the start of config-spro.md, referenced by all sections that use it | The condition technique is the same framework for pricing, output, account determination, text determination, and rebates — explaining it once prevents contradictions |
| Customer master documentation | Separate SD-only customer master doc | Self-contained section in master-data.md covering all 3 levels (KNA1/KNB1/KNVV) with SD emphasis | FI master-data.md already documents KNA1/KNB1/KNVV but with FI emphasis — SD master-data.md must be self-contained per locked decision, not just cross-reference |
| Document flow diagrams | ASCII art or complex formatting | Text-based flow with arrow notation + table mapping | Matches FI/MM process format; renders in any markdown viewer |
| VKOA account determination | Full VKOA deep-dive | Brief cross-reference to FI account-determination.md (which already has VKOA framework) | VKOA is already documented in FI; SD references it for revenue account determination |

**Key insight:** The condition technique is the single most important architectural concept in SD. It appears in pricing, output determination, account determination, text determination, and batch determination. Documenting the framework once and then applying it per area prevents inconsistency and saves token budget.

## Common Pitfalls

### Pitfall 1: Token Budget Overflow on config-spro.md

**What goes wrong:** SD has more configuration areas than FI or MM. Attempting to document all of them at the same depth as FI config-spro.md will exceed the 5000-token budget.
**Why it happens:** SD SPRO has ~15 distinct configuration areas vs ~10 for FI and ~8 for MM.
**How to avoid:** (1) Document the condition technique framework ONCE and reference it from pricing, output, text, rebate sections. (2) Keep foreign trade and rebate config at foundation level (per discretion area). (3) Credit management config: brief overview only, with note that deep credit management defers to Phase 8.
**Warning signs:** config-spro.md exceeding 20,000 characters during authoring.

### Pitfall 2: Customer Master Duplication vs Self-Containment

**What goes wrong:** FI master-data.md already documents KNA1, KNB1, and KNVV. If SD master-data.md merely cross-references FI, it violates the locked decision for self-contained SD customer master. If it fully duplicates, the two files may become inconsistent.
**Why it happens:** Customer master spans FI and SD — it belongs to both modules.
**How to avoid:** SD master-data.md includes all three levels (KNA1/KNB1/KNVV) as a self-contained section with SD emphasis. KNA1 and KNB1 coverage can be briefer (key fields only) while KNVV gets full detail. The FI version has FI emphasis (reconciliation accounts, payment terms, dunning). The two files are complementary, not contradictory — they emphasize different fields of the same tables.
**Warning signs:** Copy-pasting FI master-data.md customer section verbatim into SD.

### Pitfall 3: Mixing Up Item Category Determination Keys

**What goes wrong:** Item category determination in SD uses a 4-key lookup (sales document type + item category group + usage + higher-level item category). Documenting only 2-3 of the keys or confusing their sources leads to incorrect guidance.
**Why it happens:** The 4-key determination is unique to SD and unintuitive. The item category group comes from the material master (MVKE-MTPOS), not the sales document.
**How to avoid:** Document all 4 keys explicitly with their sources: (1) sales document type from VOV8, (2) item category group from material master MVKE-MTPOS, (3) usage (free goods, text item, etc.), (4) higher-level item category (for sub-items in BOMs). Reference OVLP (the determination table) and VOV4/VOV7 (item category definition).
**Warning signs:** Item category guidance that omits any of the 4 keys.

### Pitfall 4: Copy Control Documentation Missing Key Fields

**What goes wrong:** Copy control (VTAA, VTLA, VTFL, VTAF) has header-level AND item-level settings. Documenting only header-level copy control misses the item-level requirements and data transfer routines that control actual behavior.
**Why it happens:** Copy control screens have two levels (header, item) and the item level is where the critical settings live (requirements for copying, data transfer routines for field mapping).
**How to avoid:** For each copy control T-code, document both header and item level. Key fields at item level: requirement (BEDINGUNG), data transfer routine (DTEFR), pricing type (KNPRS), copy quantity (MNGGS). Note that requirements are ABAP routines checked at copy time — they control WHEN copying is allowed.
**Warning signs:** Copy control section that lacks "requirements" and "data transfer routines" fields.

### Pitfall 5: S/4HANA Contamination in Output Determination

**What goes wrong:** Describing BRF+ output management (S/4HANA) when the KB covers ECC 6.0 NACE-based output determination.
**Why it happens:** Output management was fundamentally changed in S/4HANA (NACE-based -> BRF+-based). Online references often default to S/4HANA.
**How to avoid:** Stick to NACE condition-based output determination for ECC 6.0. Include a brief S/4HANA note that BRF+ replaces NACE in S/4HANA, but all config guidance is for NACE.
**Warning signs:** References to BRF+, output management framework, or PPF (Post Processing Framework) as the primary approach.

### Pitfall 6: Availability Check and Credit Check Conflation

**What goes wrong:** Treating availability check (ATP) and credit check as the same thing or conflating their configuration.
**Why it happens:** Both are "checks" that happen during sales order processing and can block the order. But they use completely different mechanisms.
**How to avoid:** Document them as separate inline steps in the O2C process. ATP uses checking groups (OVZ2) + checking rules + requirements classes. Credit check uses credit control area (OVA8) + credit group + risk category. They are independent controls.
**Warning signs:** A single "checking" section that mixes ATP and credit terminology.

## Code Examples

Not applicable — this phase produces markdown reference content, not code. The "examples" are the content format patterns documented above in Architecture Patterns.

### Content Format Example: Workflow Index Table (from FI tcodes.md)

```markdown
## Workflow Index

| Process Stage | T-code(s) | Submodule | Notes |
|---|---|---|---|
| Sales Order Creation | VA01 | Sales | Standard order; also inquiry VA11, quotation VA21 |
| Sales Order Change/Display | VA02, VA03 | Sales | |
| Delivery Creation | VL01N | Shipping | From sales order |
| ...
```

### Content Format Example: Process Narrative Step (from MM processes.md)

```markdown
**Step 4 — Goods Receipt** (Warehouse Team / Receiving)
Post goods receipt in MIGO: Action = A01 (Goods Receipt), Reference = Purchase Order.
Movement type 101 (GR against PO).

FI posting at goods receipt:
- **Dr BSX** (Inventory — stock account) — increases inventory value
- **Cr WRX** (GR/IR Clearing account) — interim account cleared by MIRO
```

### Content Format Example: Master Data Table (from FI master-data.md)

```markdown
### KNVV — Customer Sales Area Data

**Table key:** MANDT + KUNNR + VKORG + VTWEG + SPART
**Scope:** Sales area level. SD-facing fields used in pricing and sales statistics.

| Field | Description | Typical Values |
|-------|-------------|----------------|
| KVGR1 | Customer Group 1 | 01, 02, 03 — used in pricing condition access sequences |
```

## State of the Art

Not applicable in the conventional sense. SD in ECC 6.0 is a stable, mature system. There are no "old vs current approaches" within ECC 6.0 itself. The relevant distinction is ECC 6.0 vs S/4HANA, which is handled by the disambiguation rules.

| ECC 6.0 Approach (This KB) | S/4HANA Replacement | Disambiguation Note |
|----------------------------|--------------------|--------------------|
| XD01/FD01/VD01 customer master | Business Partner (BP) | Single callout at customer master section header |
| NACE condition-based output | BRF+ output management | Note in output determination section |
| FD32 credit management | FSCM Credit Management (UKM) | Note in credit management section |
| VA01 sales order | Manage Sales Orders Fiori app | GUI T-codes still work in S/4 — note for disambiguation only |
| Classic pricing (V/06-V/09) | Same condition technique in S/4 | No change — pricing is the same |

## Discretion Recommendations

Based on research of the content scope and token budgets:

### T-code Count: Recommend 72-75

Reasoning: SD has more submodules than FI (55 T-codes) or MM (67 T-codes). The locked scope includes sales, shipping, billing, pricing, output, credit management, returns, rebates, foreign trade, and batch determination. A count of 72-75 covers all submodules at foundation depth without padding.

### Foreign Trade and Rebate Depth: Foundation Level

Reasoning: Foreign trade (VX11-VX13, customs, licenses) and rebates (VBO1-VBO3, VBOF) are specialized areas used by a subset of implementations. Foundation level = 3-5 T-codes each with brief Usage paragraphs, no deep config. Sufficient for "find the right T-code" use case without consuming token budget.

### Include Inquiry and Quotation in Document Flow: Yes, but brief

Reasoning: Inquiry (VA11) and quotation (VA21) are optional steps in many implementations, but they are part of the complete SD document chain. Include them in the document flow diagram with a note that they are optional pre-sales documents. Include them as T-codes in tcodes.md. Keep process narrative brief — 1 step covering both.

### Credit Management Config: Brief in Phase 7, Deep in Phase 8

Reasoning: Credit management configuration (OVA8, credit control area, automatic credit check) is a significant area. For Phase 7, include the essential config steps (define credit control area, assign to company code, set credit groups, assign checking rules). Defer deep credit to Phase 8 (SD Advanced). This matches how FI handled payment terms (basics in Phase 3, deep config in Phase 4).

### config-spro.md Organization: 8-Section Structure

Reasoning: The 8-section structure proposed in Architecture Patterns above balances completeness with navigability. Key principle: document the condition technique framework ONCE (in the Pricing section) and reference it from Output Determination, Text Determination, and any other area that uses it. This saves ~2000 characters of budget.

## SD T-code Inventory (Research Compilation)

Comprehensive list organized by submodule. This is the research input for the planner to allocate across tasks.

### Sales Documents (~15 T-codes)
- VA01/VA02/VA03 — Create/Change/Display Sales Order
- VA05 — List of Sales Orders
- VA11/VA12/VA13 — Create/Change/Display Inquiry
- VA21/VA22/VA23 — Create/Change/Display Quotation
- VA31/VA32/VA33 — Create/Change/Display Scheduling Agreement (SD)
- VA41/VA42/VA43 — Create/Change/Display Contract (SD)

### Shipping & Delivery (~10 T-codes)
- VL01N — Create Outbound Delivery (from sales order)
- VL02N — Change Outbound Delivery (PGI posted here)
- VL03N — Display Outbound Delivery
- VL04 — Change Deliveries (collective processing)
- VL06O — Outbound Delivery Monitor
- VL06G — List of Outbound Deliveries for Goods Issue
- VL10A-VL10H — Delivery Due List variants (by sales order, by PO, etc.)
- VT01N/VT02N/VT03N — Create/Change/Display Shipment

### Billing (~10 T-codes)
- VF01 — Create Billing Document
- VF02 — Change Billing Document
- VF03 — Display Billing Document
- VF04 — Process Billing Due List
- VF11 — Cancel Billing Document
- VF21 — Create Invoice List
- VF26 — Cancel Invoice List
- VFX3 — Blocked Billing Documents
- VF44/VF45 — Rebate settlement

### Pricing (~8 T-codes)
- VK11/VK12/VK13 — Create/Change/Display Condition Record
- V/06 — Define Condition Tables
- V/07 — Define Access Sequences
- V/08 — Define Condition Types
- V/09 — Define Pricing Procedures
- OVKK — Pricing Procedure Determination (assignment)

### Output Determination (~6 T-codes)
- VV31/VV32/VV33 — Create/Change/Display Output Condition Record
- NACE — Output Determination Procedures
- VV21/VV22/VV23 — Create/Change/Display Output Type (alternative path)

### Credit Management (~6 T-codes)
- FD32 — Change Customer Credit Data
- FD33 — Display Customer Credit Data
- VKM1 — Blocked SD Documents (credit)
- VKM3 — Released SD Documents
- VKM4 — Blocked SD Documents for Delivery
- VKM5 — Blocked SD Documents for Goods Issue

### Returns & Complaints (~3 T-codes)
- VA01 (doc type RE) — Returns Order (same T-code, different document type)
- VA01 (doc type CR/DR) — Credit/Debit Memo Request
- VL01N (return delivery) — Return Delivery

### Rebates (~4 T-codes)
- VBO1/VBO2/VBO3 — Create/Change/Display Rebate Agreement
- VBOF — Rebate Settlement (batch)

### Foreign Trade (~3 T-codes)
- VX11/VX12/VX13 — Foreign Trade Data for Billing Document (or LLE1/LLE2/LLE3 for customs)

### Master Data (~6 T-codes)
- VD01/VD02/VD03 — Create/Change/Display Customer (SD view only)
- XD01/XD02/XD03 — Create/Change/Display Customer (all views — already in FI, cross-ref)
- VD51/VD52/VD53 — Customer-Material Info Records

### Reporting (~5 T-codes)
- VA05 — List of Sales Orders
- VL06O — Outbound Delivery Monitor
- VF05 — List of Billing Documents
- MC+ reports — SD Information System (MCTA, MCTC, etc.)
- V.02 — Backorder Processing

**Total: ~76 T-codes** (within the 65-80 target range)

## SD Key Tables Reference (for master-data.md and processes.md)

| Table | Description | Key | Used In |
|-------|-------------|-----|---------|
| VBAK | Sales Document Header | VBELN | VA01-VA03, all SD documents |
| VBAP | Sales Document Item | VBELN + POSNR | VA01-VA03, all SD documents |
| VBEP | Sales Document Schedule Line | VBELN + POSNR + ETENR | Schedule lines |
| VBPA | Sales Document Partner | VBELN + POSNR + PARVW | Partner functions |
| VBKD | Sales Document Business Data | VBELN + POSNR | Payment terms, incoterms |
| LIKP | Delivery Header | VBELN | VL01N-VL03N |
| LIPS | Delivery Item | VBELN + POSNR | VL01N-VL03N |
| VBRK | Billing Document Header | VBELN | VF01-VF03 |
| VBRP | Billing Document Item | VBELN + POSNR | VF01-VF03 |
| VBFA | Document Flow | VBELV + POSNV + VBELN + POSNN | Cross-document tracing |
| KONH | Condition Record Header | KNUMH | Pricing, output, account det. |
| KONP | Condition Record Item | KNUMH + KOPOS | Pricing amounts/rates |
| KONV | Conditions in Documents | KNUMV + KPOSN | Pricing result per SD doc |
| KNA1 | Customer General Data | KUNNR | Customer master |
| KNB1 | Customer Company Code | KUNNR + BUKRS | Customer master |
| KNVV | Customer Sales Area | KUNNR + VKORG + VTWEG + SPART | Customer master |
| KNVP | Customer Partner Functions | KUNNR + VKORG + VTWEG + SPART + PARVW | Partner determination |
| MVKE | Material Sales Org Data | MATNR + VKORG + VTWEG | Material master sales views |

## Open Questions

1. **Token budget for config-spro.md**
   - What we know: SD config has ~15 areas; FI config-spro.md uses ~12,000 chars; MM config-spro.md uses ~9,000 chars. SD will be larger.
   - What's unclear: Whether all areas can fit at proper depth within 20,000 chars.
   - Recommendation: Start with the 8-section structure. If budget overflows, reduce foreign trade and rebate config to brief pointers. The validate.py token budget warnings are accepted (prior decision 06-03).

2. **VKOA cross-reference vs duplication**
   - What we know: FI account-determination.md already has the VKOA framework documented. SD config-spro.md needs to reference revenue account determination.
   - What's unclear: How much VKOA detail to include in SD config-spro.md vs just cross-referencing FI.
   - Recommendation: Brief VKOA overview in SD config-spro.md (just the assignment T-code and 5 access levels), cross-reference FI account-determination.md for the full worked examples. This avoids duplication.

3. **Condition technique depth in tcodes.md vs config-spro.md**
   - What we know: Locked decision says "Pricing T-codes should include condition technique detail inline." The condition technique is also core config in config-spro.md.
   - What's unclear: How much condition technique detail to inline in tcodes.md vs keeping it in config-spro.md.
   - Recommendation: In tcodes.md pricing section, include a brief explanation of the condition technique 4-layer model (condition table -> access sequence -> condition type -> procedure) with the V/06-V/09 T-codes. config-spro.md has the full step-by-step configuration detail with SPRO paths and key fields.

## Sources

### Primary (HIGH confidence)
- Existing KB files: FI tcodes.md, FI config-spro.md, FI processes.md, FI master-data.md, FI account-determination.md — verified patterns and format
- Existing KB files: MM tcodes.md, MM config-spro.md, MM processes.md, MM master-data.md, MM mm-advanced.md, MM integration.md — verified patterns and format
- Existing KB files: SD CLAUDE.md, SD stub files — verified file structure exists
- validate.py — verified structural constraints, token budgets, frontmatter requirements
- SAP ECC 6.0 SD knowledge from training data (T-codes, table names, SPRO paths, condition technique framework) — HIGH confidence for ECC 6.0 SD fundamentals as they are stable/mature

### Secondary (MEDIUM confidence)
- T-code count estimation (76 T-codes) — based on systematic submodule enumeration; actual count may shift +/- 5 during authoring
- Token budget estimates for SD files — extrapolated from FI/MM file sizes; actual sizes depend on authoring decisions

### Tertiary (LOW confidence)
- None. SD in ECC 6.0 is well-understood from training data. No external web searches were needed because the domain is stable and the content patterns are fully established from prior phases.

## Metadata

**Confidence breakdown:**
- Content patterns (from FI/MM): HIGH — directly read and verified from existing files
- SD T-code inventory: HIGH — ECC 6.0 SD T-codes are stable, well-documented in training data
- SD table structures: HIGH — ABAP Dictionary table names and key structures are stable facts
- Token budget feasibility: MEDIUM — extrapolated from FI/MM sizes; SD config-spro.md may exceed budget
- Discretion recommendations: MEDIUM — based on research judgment, not user direction

**Research date:** 2026-02-17
**Valid until:** Indefinitely (ECC 6.0 is frozen; content patterns are established)
