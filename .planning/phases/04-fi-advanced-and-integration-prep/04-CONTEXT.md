# Phase 4: FI Advanced & Integration Prep - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Layer advanced FI reference on top of Phase 3's foundation: complete account determination logic (with full path tracing and worked examples), decision trees for 7 common FI configuration dilemmas, and a dual-purpose troubleshooting guide (implementation pitfalls + symptom-based diagnosis). This phase also pre-documents the full OBYC GR/GI account determination path as integration prep for Phase 6 (MM-FI) and Phase 8 (SD-FI).

What this phase does NOT include: other MM movement types beyond GR/GI (Phase 6), full VKOA detail (Phase 8), CO integration (Phase 10).

</domain>

<decisions>
## Implementation Decisions

### Account Determination — Depth & Format

- **Full path traced for every scenario**: movement type → valuation class → OBYC transaction key → account modifier → GL account. Consultant can follow the chain from scratch.
- **Format**: Logic explanation first, then a worked example with concrete Dr/Cr journal entries. Account numbers are labeled as representative examples (not real implementation values).
- **Four scenario groups to cover:**
  1. MM goods receipt (BSX = inventory, WRX = GR/IR clearing, PRD = price differences, GBB = offsetting)
  2. MM goods issue (GBB with account modifier VBR for consumption, VNG for scrapping, VAX for COGS)
  3. SD billing / revenue — VKOA basics: how revenue account determination works at the framework level (Phases 6/8 own the deep-dive)
  4. FI-only automatic postings: F.05 FX valuation (exchange rate difference GL accounts), F110 cash discount (ZDI/SKT), clearing account mechanics
- **Both reading AND setup**: How to navigate OBYC/VKOA to read current config (diagnostic path), plus how to set it up during implementation.
- **File**: New file `modules/fi/account-determination.md` (not integration.md — complex enough to stand alone)

### Account Determination — Integration Prep Scope

- Phase 4 owns the **full OBYC walkthrough for GR and GI** (movement types 101, 102, 261, 262, 551). This is the core MM-FI story.
- Phase 6 (MM Advanced) extends to other movement types (transfers, stock transport orders, consignment).
- Phase 8 (SD Advanced) owns the full VKOA detail (condition tables, access sequences, account assignment groups).
- Phase 4 establishes the **VKOA framework** (what VKOA is, how it relates to KOFI, the role of customer account assignment group KTGRD and material account assignment group) — enough context for users to understand Phase 8 content.

### Decision Trees — Format

- **Dual format**: Q&A routing (if/then questions to reach the right approach) followed by a comparison table (approach / when to use / config implications / trade-offs). Q&A routes; table explains.
- **Seven scenarios** (the 3 named from ROADMAP + 4 selected additions):
  1. Parallel accounting — leading ledger only vs. non-leading ledgers vs. document splitting only
  2. Payment terms — number of terms, baseline date logic, installments
  3. Dunning — procedure configuration decisions (levels, intervals, minimum amounts)
  4. New GL ledger strategy — when to add a non-leading ledger vs. use document splitting alone
  5. Reconciliation account assignment — one per company code vs. multiple by vendor/customer type
  6. Tolerance group design — number of groups, limit structures for AP invoice approval
  7. Asset class strategy — granular (many classes) vs. broad (few classes), when each helps
- **Depth per scenario**: Full scenario including config implications — self-contained guide, not just a pointer to config-spro.md.
- **File**: Combined with troubleshooting in `modules/fi/fi-advanced.md`

### Troubleshooting Guide — Structure

- **Two sections in one file**:
  1. **Implementation Pitfalls** — organized by setup mistake; what to avoid and why; useful during implementation
  2. **Troubleshooting Symptoms** — organized by what the consultant observes; root cause; full resolution path
- **Four priority areas** for both sections:
  1. New GL vs Classic GL confusion (FS10N shows zeroes, FAGLB03 vs FBL3N vs FAGLL03 confusion)
  2. Document splitting side effects (zero balance clearing account errors, incomplete splits)
  3. Asset Accounting year-end sequence errors (AFAB/AJRW/AJAB out of order)
  4. F110 Automatic Payment Program (proposal not picking up items, bank account not selected)
- **Depth per entry**: Symptom + root cause + **full resolution path** — self-contained, no need to cross-reference other files to fix the problem.
- **File**: Combined with decision trees in `modules/fi/fi-advanced.md`

### File Structure

Phase 4 produces two new files:
- `modules/fi/account-determination.md` — account determination framework, full OBYC GR/GI walkthrough, VKOA framework intro, FI-only auto postings
- `modules/fi/fi-advanced.md` — 7 decision trees (Q&A + comparison tables) + implementation pitfalls + symptom troubleshooting guide

### Claude's Discretion

- Exact structure of Q&A routing within each decision tree (number of branching questions)
- Whether to use sub-sections or a table for the worked Dr/Cr examples
- Ordering of the seven decision tree scenarios within fi-advanced.md
- How many pitfall/symptom entries per FI area beyond the 4 priority areas

</decisions>

<specifics>
## Specific Ideas

- Account determination worked examples should use representative account numbers clearly labeled as examples (e.g., "14000 = Inventory, 19110 = GR/IR Clearing") — not suggest these are universal
- The four troubleshooting areas map to the four most common FI gotchas from Phase 3 content — the symptom entries should cross-reference back to the Phase 3 tcodes/config-spro files for additional context

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-fi-advanced-and-integration-prep*
*Context gathered: 2026-02-17*
