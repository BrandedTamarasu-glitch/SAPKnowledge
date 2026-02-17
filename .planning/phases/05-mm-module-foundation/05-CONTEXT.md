---
phase: 05-mm-module-foundation
created: 2026-02-16
status: final
areas_discussed: T-code coverage scope, Material master structure, Procure-to-pay process depth, SPRO configuration scope
---

# Phase 5 Context: MM Module Foundation

## Decisions

Locked choices from /gsd:discuss-phase. Downstream agents must honor these exactly.

### T-code Coverage Scope

- **Allocation target ~65 T-codes, purchasing-heavy:** ~25 purchasing (ME-family) / ~15 inventory management (MB-family) / ~15 invoice verification (MIR/MIRO-family) / ~10 MRP/planning (MD-family)
- **Document all three variants separately:** ME21N, ME22N, ME23N each get their own entry. Same for MIGO create/change/display. Don't collapse to one entry — users may need specific display or change variants.
- **Include key reporting T-codes:** MB51 (material document list), MB52 (warehouse stocks), ME2M (by material), ME2N (by PO number), ME2L (by vendor), ME80 (purchasing reports). These are heavily used day-to-day.
- **Same format as FI:** Workflow index table at top (process step → T-code quick lookup), then submodule sections with ### headings.

### Material Master Structure

- **Hybrid organization:** Organize by view group (mirrors the SAP UI), but call out the underlying table at each section header (MARA = client level, MARC = plant level, MARD = storage location, MBEW = valuation/accounting). Best of both worlds.
- **All views with key fields:** Document every view tab even if briefly — Basic Data 1/2, Purchasing, MRP 1/2/3/4, Plant Data & Storage 1/2, Accounting 1/2, Sales views (brief), Classification (brief). Users should know what exists.
- **Vendor master: full coverage in MM** — LFA1/LFB1/LFM1 fully documented even though FI already has it. Self-contained reference for consultants coming in through MM. Purchasing view emphasis: LFM1 fields (payment terms, purchasing currency, incoterms, order acknowledgment, min/max order values).
- **Info records and source lists in master-data.md:** EINE/EINA (info records, T-code ME11/ME12/ME13) and EORD (source list, T-code ME01/ME03) are master data — document them in master-data.md alongside material and vendor master.

### Procure-to-Pay Process Flow

- **Start from Purchase Requisition (ME51N):** Full upstream coverage — PR creation, PR approval (brief), PR-to-PO conversion (ME59N), then standard PO → GR → MIRO → F110.
- **Include release strategies — brief overview:** Cover the concept (characteristic-based approval levels), key T-codes (ME28/ME29N for approvals), and config objects (release indicator, release strategy, release group). Detailed SPRO config defers to Phase 6.
- **Full three-way match detail including SPRO paths:** Three-way match (PO qty/price vs GR qty vs invoice) is the heart of MM and the MM-FI handoff. Cover completely: how MIRO validates against PO and GR, tolerance key concept (BD/DQ/PP/ST/VP), SPRO path for tolerance groups, blocking reasons. Don't split this across phases.
- **Outline agreements — brief section:** Cover what contracts (ME31K) and scheduling agreements (ME31L) are, key T-codes (ME31K/ME32K/ME33K, ME31L/ME32L), and how they release to POs. No deep config.

### SPRO Configuration Scope

- **All 4 config areas in Phase 5:**
  1. Enterprise structure — plant parameters (OMSY), storage location setup (OMB2/OMB3), assignment to company code
  2. Purchasing — document types (OMBA), number ranges, tolerance keys, screen layout rules (OMF4/OMEC)
  3. Inventory Management — movement type config (OMJJ), GR/GI document settings, number ranges for material documents (OMBT)
  4. Invoice Verification / LIV (OLMR) — tolerance groups (BD/DQ/PP/ST/VP keys), blocking reasons, GR-based invoice verification setting

- **Valuation basics in Phase 5:** Price control (S = standard price vs V = moving average), valuation area = plant-level (standard), account category reference concept. SPRO path: OMWM. Detailed OBYC account determination defers to Phase 6.
- **No SPRO MRP config:** MRP fields are covered in material master (MRP 1/2 views) but SPRO MRP config (plant parameters OPPR, OMD4) is excluded from Phase 5. MRP is advanced territory.
- **One file — config-spro.md:** Same structure as FI — single file, organized into sections by area. SPRO reference path as section headers.

---

## Claude's Discretion

Areas where Claude makes the implementation choices.

- **Exact T-code selection within each family:** Which specific purchasing T-codes (ME21N vs ME25 vs MENGE etc.) to include in the ~25 purchasing slots is Claude's call. Prioritize the ones consultants use in every implementation.
- **View depth within "all views with key fields":** How many fields to document per view is Claude's judgment — focus on fields that have config implications or are commonly wrong. Flag fields where ECC vs S/4 differences matter.
- **Process narrative style:** FI processes.md used narrative-plus-table with role annotations. MM can use same format — Claude decides where inline annotations add value vs. cluttering the flow.
- **CORRECTION note blocks:** FI established CORRECTION blocks for commonly-wrong field locations. Use same pattern in MM wherever a field is frequently mis-documented or confused (e.g., valuation class is in Accounting 1 view, not Basic Data).

---

## Deferred Ideas

Out of scope for Phase 5. Don't include.

- **MRP SPRO configuration** (plant parameters, MRP controllers, planning horizon settings) — deferred out of Phase 5 entirely. MRP 1/2 material master fields are in scope; SPRO MRP config is not.
- **OBYC account determination detail** — price control basics are Phase 5; the full OBYC walkthrough (movement type → transaction key → valuation class → GL) is Phase 6.
- **Split valuation configuration** — advanced MM topic, Phase 6 decision trees.
- **Release strategy SPRO detail** — concept and T-codes in Phase 5; full SPRO release strategy config (characteristics, groups, strategies) in Phase 6.
- **Batch management** — deferred to Phase 12 scenario playbooks.
- **Serial number management** — deferred to Phase 12 scenario playbooks.
- **Special procurement types** (subcontracting, consignment, third-party) — deferred to Phase 12.
- **Consignment and pipeline materials** — deferred to Phase 12.
