# Phase 11: Cross-Module Integration - Research

**Researched:** 2026-02-17
**Domain:** SAP ECC 6.0 Cross-Module Integration (E2E Processes + MM-SD Integration)
**Confidence:** HIGH

## Summary

Phase 11 populates the cross-module directory with end-to-end process flows (P2P, O2C, R2R), creates an MM-SD integration reference, and updates navigation files. The existing module content is comprehensive — MM, SD, FI, and CO each have detailed processes.md and integration.md files with T-code sequences, document traces, and period-end steps. The cross-module files currently exist as empty templates from Phase 1. The challenge is not generating content from scratch but synthesizing existing module content into cross-module narratives that complement (not duplicate) what already exists.

All four target files in cross-module/ exist as templates with "[To be populated]" placeholders. The cross-module/CLAUDE.md index exists but needs the mm-sd-integration.md entry added and routing text updated.

**Primary recommendation:** Structure each E2E file with an ASCII document chain header, prerequisites reading list, and step-by-step integration handoff narrative that uses inline brief + pointer format to reference existing module content rather than re-documenting it.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Step-by-step with every T-code in sequence — consultant implementation guide level
- Focus on integration handoffs between modules (complement existing module process files, don't re-document)
- ASCII document chain at the top of each E2E flow showing the document creation sequence
- Record-to-Report covers full cross-module period-end close: MM cutoffs → SD cutoffs → CO allocations/settlement → FI close, with ordering dependencies
- Core three MM-SD: availability check (ATP), goods issue for delivery, returns
- Extended MM-SD: consignment, stock transport orders, third-party processing, subcontracting
- MM-SD integration lives in cross-module/mm-sd-integration.md (new file)
- ATP: include different check types and how SD triggers each
- Returns: full reverse trace showing every document and module handoff
- Cross-references: inline brief + pointer (one-line summary + "See modules/xx/file.md Section X for full detail")
- Prerequisites reading list at top of each E2E file
- Update sap-routing.md with E2E process query rows
- Create cross-module/CLAUDE.md as index file
- Add "See Also" cross-references to existing module integration.md files
- One file per E2E process, replace existing templates in-place
- cross-module/CLAUDE.md follows same format as module CLAUDE.md files

### Claude's Discretion
- Exact ASCII document chain diagram style
- How much ATP configuration detail to include vs keeping it integration-focused
- Whether consignment and STO get their own sections or are subsections of the main MM-SD flow
- Level of detail in period-end ordering dependencies for R2R

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INTG-04 | MM-SD integration points (availability check, goods issue for delivery, returns) | Existing SD processes.md has O2C with PGI steps; SD config-spro.md has OVZ2 ATP config; MM integration.md has movement type 601 for PGI; SD integration.md has PGI COGS trace. New file cross-module/mm-sd-integration.md synthesizes these. |
| E2E-01 | Procure-to-Pay full process flow across MM and FI | MM processes.md has 7-step P2P narrative; MM integration.md has MIGO 101 trace, MIRO trace, GR/IR clearing; FI processes.md has F110 payment run. Template at cross-module/procure-to-pay.md ready for overwrite. |
| E2E-02 | Order-to-Cash full process flow across SD and FI | SD processes.md has 6-step O2C narrative; SD integration.md has VF01 billing trace, PGI COGS trace; FI processes.md has AR clearing. Template at cross-module/order-to-cash.md ready for overwrite. |
| E2E-03 | Record-to-Report full process flow across FI and CO with period-end | CO processes.md has 9-step period-end sequence; CO integration.md has CO-FI catalog and timing; FI processes.md has month-end close; MM integration.md has MM period-end (8 steps); SD integration.md has SD period-end (7 steps). Template at cross-module/record-to-report.md ready for overwrite. |

</phase_requirements>

## Architecture Patterns

### Recommended File Structure

```
cross-module/
├── CLAUDE.md                  # Index file (update existing)
├── procure-to-pay.md          # E2E-01: Overwrite template
├── order-to-cash.md           # E2E-02: Overwrite template
├── record-to-report.md        # E2E-03: Overwrite template
└── mm-sd-integration.md       # INTG-04: New file
```

Additional updates:
- `.claude/rules/sap-routing.md` — Add E2E routing rows
- `modules/mm/integration.md` — Add "See Also" to E2E and MM-SD content
- `modules/sd/integration.md` — Add "See Also" to E2E and MM-SD content
- `modules/fi/integration.md` — Add "See Also" to E2E content (if integration.md exists for FI; currently FI has account-determination.md instead)
- `modules/co/integration.md` — Add "See Also" to R2R content

### Pattern 1: E2E File Section Structure

Each E2E file should follow this consistent structure:

```markdown
---
module: cross-module
content_type: end-to-end-process
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: 2026-02-17
---

# [Process Name] (E2E)

> One-line summary

## Prerequisites

Read these module files for full detail on individual steps:
- `modules/xx/processes.md` — [what it covers]
- `modules/xx/integration.md` — [what it covers]

## Document Chain

```
[ASCII diagram showing document flow across modules]
```

## Process Flow

### Step N: [Step Name] (T-code)
**Module:** MM/SD/FI/CO
[One-line summary of what happens]
See `modules/xx/file.md` § Section Name for full detail.

**Integration handoff:** [What crosses module boundary and how]

## Period-End Considerations

[If applicable]

## Troubleshooting

[Common cross-module issues]

## S/4HANA Differences

[Key differences affecting the E2E flow]
```

### Pattern 2: ASCII Document Chain Style

Based on existing patterns in the knowledge base (e.g., MM integration.md traces), recommend this style:

```
PR (ME51N) → PO (ME21N) → GR Mat Doc (MIGO 101) → IR Doc (MIRO) → FI Invoice → Payment (F110)
 [MM]         [MM]         [MM → FI]                [MM → FI]       [FI]        [FI]
```

Each node shows the T-code and the module boundary where integration happens is marked with arrows. This matches the inline brief + pointer approach: the chain gives the overview, then each step section provides the handoff detail.

### Pattern 3: Inline Brief + Pointer Cross-References

Format for referencing existing module content without re-documenting:

```markdown
### Step 3: Goods Receipt (MIGO, movement type 101)
**Module:** MM → FI
GR creates material document (MKPF/MSEG) and simultaneously posts FI accounting document
via OBYC account determination (BSX inventory debit, WRX GR/IR clearing credit).
See `modules/mm/integration.md` § MIGO 101 Posting Trace for the full 5-step account determination walkthrough.
```

### Anti-Patterns to Avoid

- **Re-documenting module content:** The E2E files must NOT copy content from modules/xx/processes.md or integration.md. They synthesize the cross-module narrative and point back.
- **Missing the handoff:** Each step must explicitly state what document/data crosses from one module to another. A step that only describes what happens within one module belongs in the module file, not the E2E file.
- **Inconsistent cross-reference format:** Every pointer must use the same format: `See \`modules/xx/file.md\` § Section Name for full detail.`

## Existing Content Inventory

### What Already Exists (Don't Duplicate)

| Content | Location | Covers |
|---------|----------|--------|
| P2P 7-step narrative | `modules/mm/processes.md` § Procure-to-Pay | PR → PO → GR → MIRO → MRBR → F110 with FI postings |
| MIGO 101 posting trace | `modules/mm/integration.md` § Posting Trace: MIGO 101 | 5-step account determination walkthrough |
| MIRO posting trace | `modules/mm/integration.md` § Posting Trace: MIRO | 4-step vendor invoice trace |
| GR/IR clearing | `modules/mm/integration.md` § GR/IR Clearing | WRX, F.13, MR11 complete coverage |
| MM period-end | `modules/mm/integration.md` § Period-End MM-FI Sequence | 8-step cutoff sequence |
| OBYC walkthrough | `modules/mm/mm-advanced.md` § OBYC | 10+ worked examples |
| O2C 6-step narrative | `modules/sd/processes.md` § Order-to-Cash | VA01 → VL01N → PGI → VF01 → FI doc |
| VF01 billing trace | `modules/sd/integration.md` § Posting Trace: VF01 | 5-step revenue/receivable trace |
| PGI COGS trace | `modules/sd/integration.md` § Posting Trace: PGI | 3-step COGS/inventory trace |
| SD period-end | `modules/sd/integration.md` § Period-End SD-FI Sequence | 7-step cutoff sequence |
| VKOA walkthrough | `modules/sd/sd-advanced.md` § VKOA | 8 worked billing-to-GL examples |
| OVZ2 availability check | `modules/sd/config-spro.md` § Availability Check | Check types and configuration |
| Returns/consignment/3rd-party | `modules/sd/processes.md` § Special Processes | Return orders, consignment, third-party |
| F110 payment run | `modules/fi/processes.md` § Payment Run | 7-step payment run detail |
| Month-end close | `modules/fi/processes.md` § Month-End Close | 5-step FI close sequence |
| CO period-end | `modules/co/processes.md` § Period-End Closing | 9-step sequence with dependencies |
| CO-FI integration catalog | `modules/co/integration.md` § Integration Catalog | 3 directions, full touchpoint list |
| CO-FI reconciliation | `modules/co/co-advanced.md` § Reconciliation | Reconciliation ledger, KALC, COFIT |

### What Needs to Be Written (New Content)

| Deliverable | New Content Required |
|-------------|---------------------|
| `cross-module/procure-to-pay.md` | ASCII chain, prerequisites, integration handoff narrative synthesizing MM and FI content, cross-module troubleshooting |
| `cross-module/order-to-cash.md` | ASCII chain, prerequisites, integration handoff narrative synthesizing SD and FI content, cross-module troubleshooting |
| `cross-module/record-to-report.md` | ASCII chain, prerequisites, full period-end ordering (MM → SD → CO → FI) with dependency map, cross-module reconciliation |
| `cross-module/mm-sd-integration.md` | ATP check types and SD triggers, PGI/601 handoff, returns reverse trace, consignment flows, STO mechanics, third-party processing, subcontracting (SD→MM) |
| `cross-module/CLAUDE.md` | Add mm-sd-integration.md entry, update routing descriptions |
| `.claude/rules/sap-routing.md` | Add rows for E2E process queries |
| Module integration.md files | Add "See Also" sections pointing to new cross-module content |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Document chain diagrams | Complex box-drawing characters | Simple arrow chains with T-codes | Readability in plain text; consistent with existing traces in integration.md files |
| Movement type references | Inline explanations of every movement type | Pointer to `reference/movement-types.md` and `modules/mm/integration.md` | Already documented; avoid duplication |
| Account determination detail | Re-explaining OBYC/VKOA logic | Pointer to `modules/mm/mm-advanced.md` and `modules/sd/sd-advanced.md` | Already have 10+ and 8 worked examples respectively |
| Period-end step detail | Full re-documentation of each module's close steps | Pointer to each module's integration.md period-end section | Each module already has 5-9 step sequences |

**Key insight:** The E2E files are synthesis and navigation layer, not primary content. Their value is in showing the cross-module thread that no single module file can show.

## Common Pitfalls

### Pitfall 1: Content Duplication
**What goes wrong:** E2E file re-documents what modules/xx/processes.md already covers in full detail.
**Why it happens:** Natural tendency to make each file self-contained.
**How to avoid:** Every step in the E2E file gets exactly one line of summary + one pointer. If you're writing more than 3 lines about a single-module step, it belongs in the module file.
**Warning signs:** E2E file exceeds 300 lines; step descriptions longer than a short paragraph.

### Pitfall 2: Period-End Ordering Dependencies Wrong
**What goes wrong:** R2R file shows period-end steps in wrong order, or misses a dependency.
**Why it happens:** Each module's period-end is documented independently; cross-module ordering requires synthesis.
**How to avoid:** The correct cross-module ordering is: (1) MM cutoffs (MMRV, MMPV) → (2) SD cutoffs (billing due list, rebate settlements) → (3) CO allocations and settlements (KSU5, KO88, CJ88) → (4) FI close (foreign currency reval, regrouping, GR/IR, tax, reconciliation, close periods). CO must run after MM/SD because it needs all actual costs posted. FI close runs last because it needs all CO settlements reflected.
**Warning signs:** CO settlement listed before MM period-end; FI close listed before CO settlement.

### Pitfall 3: MM-SD Integration Missing the Inventory Bridge
**What goes wrong:** MM-SD file describes availability check and returns but misses the inventory posting mechanics that connect the two modules.
**Why it happens:** ATP is visible in SD (VA01 checks stock), but the underlying MM stock management (MARD/MARC tables, movement types) is less visible.
**How to avoid:** For each MM-SD touchpoint, explicitly document: (a) what SD triggers, (b) what MM does in response, (c) what document/data is created, (d) what FI posting results (if any).
**Warning signs:** Steps describe SD behavior without showing the MM consequence.

### Pitfall 4: Inconsistent Cross-Reference Format
**What goes wrong:** Some references use "See file.md" others use "Refer to file.md § Section" — reader can't reliably navigate.
**How to avoid:** Enforce one format: `See \`modules/xx/file.md\` § Section Name for full detail.`
**Warning signs:** Mixed reference styles within a single file.

### Pitfall 5: Missing S/4HANA Differences
**What goes wrong:** E2E files don't mention S/4HANA differences that affect the cross-module flow.
**Why it happens:** Each module file already has S/4 differences inline, but the cross-module impact may differ.
**How to avoid:** Each E2E file needs its own S/4HANA section highlighting differences that affect the end-to-end flow specifically (e.g., Universal Journal eliminates CO-FI reconciliation step in R2R; MATDOC replaces MKPF/MSEG in P2P document chain).

## Content Guidance by Deliverable

### Procure-to-Pay (E2E-01)

**Document chain:**
```
Purchase Req → Purchase Order → GR Material Doc → Invoice (IR) → FI Invoice Doc → Payment Doc
  ME51N          ME21N           MIGO (101)       MIRO           (auto)          F110
  [MM]           [MM]            [MM → FI]        [MM → FI]      [FI]            [FI]
```

**Integration handoffs to highlight:**
1. ME21N → MIGO: PO reference in goods receipt (EBELN/EBELP in MSEG)
2. MIGO 101 → FI: Automatic FI posting via OBYC (BSX/WRX) — pointer to MM integration.md
3. MIRO → FI: Vendor invoice creates FI document, clears GR/IR (WRX) — pointer to MM integration.md
4. MIRO → GR/IR clearing: Three-way match mechanics
5. F110 → Bank: Payment run clears vendor open items

**S/4 key difference:** MATDOC replaces MKPF/MSEG; Universal Journal replaces separate FI tables.

### Order-to-Cash (E2E-02)

**Document chain:**
```
Sales Order → Delivery → PGI (Goods Issue) → Billing Doc → FI Acctg Doc → Payment/Clearing
  VA01          VL01N      VL02N (601)        VF01         (auto)          F-28/F-32
  [SD]          [SD]       [SD → MM → FI]     [SD → FI]    [FI]            [FI]
```

**Integration handoffs to highlight:**
1. VA01 → MM: Availability check (ATP) — triggers stock check in MM
2. VL01N → MM: Delivery creates link to sales order; picking triggers MM reservation
3. VL02N PGI → MM → FI: Movement type 601 reduces inventory (MM), posts COGS and inventory change (FI via OBYC GBB/BSX)
4. VF01 → FI: Billing creates FI accounting document via VKOA (revenue credit, receivable debit)
5. F-28 → Clearing: Customer payment clears open receivable

**S/4 key difference:** Real-time COGS split available; VKOA still drives revenue but CDS views enable real-time reporting.

### Record-to-Report (E2E-03)

**Document chain (period-end sequence, not a single document flow):**
```
MM Cutoffs → SD Cutoffs → CO Allocations → CO Settlement → FI Valuations → FI Close
 MMRV/MMPV    VF04/VBO1    KSU5/KSV5       KO88/CJ88       FAGL_FC_VAL     MMPV/OB52
 [MM]         [SD]          [CO]             [CO → FI]       [FI]             [FI]
```

**Integration handoffs to highlight:**
1. MM cutoffs (MMRV open period, MMPV close period): Must complete before CO can see final actual costs
2. SD cutoffs (VF04 billing due list, rebate settlements): Revenue must be fully posted before CO
3. CO allocations (KSU5 assessment, KSV5 distribution): Redistribute costs across cost centers
4. CO settlement (KO88 orders, CJ88 projects): Posts to FI via settlement cost element (category 22)
5. FI valuations (FAGL_FC_VAL foreign currency, F.13 GR/IR regrouping): Adjustments before close
6. FI close (OB52 close posting periods): Final step after all modules complete

**Dependencies are strict:** CO settlement generates FI postings, so FI cannot close until CO is done. CO needs all actual costs, so MM and SD must close first.

**S/4 key difference:** CO-FI reconciliation step eliminated (Universal Journal); period-end still sequential but fewer reconciliation steps.

### MM-SD Integration (INTG-04)

**Section structure recommendation:**
1. **Availability Check (ATP)** — Core section
   - Check types: stock check only, planned receipts, delivery scheduling
   - How SD triggers: VA01 schedule line determination → OVZ2 check configuration
   - What MM provides: MARD/MARC stock data, MRP planned receipts
   - Configuration: Checking group (material master), checking rule (per transaction)

2. **Goods Issue for Delivery (PGI)** — Core section
   - VL02N posts goods issue with movement type 601
   - MM: Updates MARD stock, creates material document
   - FI: OBYC GBB/BSX posts COGS debit, inventory credit
   - Document links: Delivery → material document → FI document

3. **Returns** — Core section, full reverse trace
   - SD return order (VA01 with order type RE) → return delivery (VL01N) → GR back to stock (movement type 651) → credit memo (VF01)
   - Each step shows module handoff and document created

4. **Consignment** — Extended section
   - Fill (movement type 631), issue (633), returns (634), pickup (632)
   - Customer consignment stock tracked at customer level in MM
   - Billing only on issue (633) — revenue recognition point

5. **Stock Transport Orders** — Extended section
   - PO type UB, movement types 641 (GI sending) / 101 (GR receiving)
   - Cross-plant, possibly cross-company-code
   - SD delivery document created for shipping (if delivery-based STO)

6. **Third-Party Processing** — Extended section
   - SD order item category TAS → automatic PR creation → PO to vendor
   - Vendor ships directly to customer; no goods movement through own plant
   - Invoice verification (MIRO) for vendor; billing (VF01) for customer

7. **Subcontracting (SD → MM)** — Extended section
   - SD order triggers need; MRP creates subcontracting PR
   - Movement type 541 (components to subcontractor), 101 (finished goods receipt)
   - Covered briefly with pointer to modules/mm/processes.md for procurement side

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate module period-end docs | Cross-module R2R with ordering dependencies | Phase 11 (this phase) | First time full close sequence documented cross-module |
| Module-only integration files | E2E + module integration files complementary | Phase 11 | E2E provides the thread; module files provide the depth |

**No deprecated approaches** — this is new content creation, not refactoring existing patterns.

## Open Questions

1. **FI "integration.md" file**
   - What we know: FI has `account-determination.md` but no dedicated `integration.md` file
   - What's unclear: Should "See Also" cross-references go in `account-determination.md` or should a separate file be created?
   - Recommendation: Add "See Also" to `modules/fi/processes.md` instead, since that's where month-end close and payment run live. Do not create new files outside phase scope.

2. **ATP Configuration Depth**
   - What we know: OVZ2, checking groups, checking rules already in SD config-spro.md
   - What's unclear: How much configuration detail to include in MM-SD integration vs. pointing to config-spro.md
   - Recommendation: Include enough to explain the integration mechanics (what SD sends to MM and what comes back), point to config-spro.md for SPRO paths and field-level settings. This is Claude's discretion per CONTEXT.md.

3. **Consignment/STO Section Organization**
   - What we know: User said Claude's discretion on whether these get own sections or subsections
   - Recommendation: Give consignment and STO their own top-level sections (## level) since each has distinct movement types, document flows, and integration mechanics. Third-party and subcontracting can be briefer subsections since they're more straightforward.

## Sources

### Primary (HIGH confidence)
- `modules/mm/processes.md` — P2P 7-step narrative, special processes
- `modules/mm/integration.md` — 20 MM-FI touchpoints, posting traces, GR/IR, period-end
- `modules/mm/mm-advanced.md` — OBYC walkthrough with worked examples
- `modules/sd/processes.md` — O2C 6-step narrative, returns, consignment, third-party, subcontracting
- `modules/sd/integration.md` — 14 SD-FI touchpoints, billing trace, PGI trace, period-end
- `modules/sd/sd-advanced.md` — VKOA walkthrough with worked examples
- `modules/sd/config-spro.md` — OVZ2 availability check, shipping, copy control
- `modules/fi/processes.md` — Month-end close, F110 payment run
- `modules/co/processes.md` — Period-end 9-step sequence
- `modules/co/integration.md` — CO-FI catalog (3 directions), period-end timing
- `modules/co/co-advanced.md` — CO-FI reconciliation, KALC, COFIT
- All existing cross-module/ template files — confirmed placeholder status

### Secondary (MEDIUM confidence)
- SAP ECC 6.0 movement types for consignment (631-634) and STO (641/101) — from training knowledge, consistent with module content
- ATP check type mechanics — consistent with OVZ2 documentation in SD config-spro.md

## Metadata

**Confidence breakdown:**
- Existing content inventory: HIGH — all files read directly, content verified
- E2E file structure: HIGH — follows established patterns from 10 phases of prior work
- Cross-reference strategy: HIGH — user-specified format, consistent with KB conventions
- Period-end ordering: HIGH — verified against four module-specific period-end sequences
- MM-SD integration mechanics: MEDIUM — synthesized from module content and training knowledge; movement types for consignment/STO should be verified during implementation
- ATP configuration depth: MEDIUM — OVZ2 exists in SD config-spro.md but integration mechanics are from training knowledge

**Research date:** 2026-02-17
**Valid until:** 2026-03-17 (stable domain — SAP ECC 6.0 is not changing)
