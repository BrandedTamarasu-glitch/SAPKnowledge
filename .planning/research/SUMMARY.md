# Project Research Summary

**Project:** SAP ECC 6 Knowledge Base for Claude Code
**Domain:** Enterprise Software Reference Documentation
**Researched:** 2026-02-16
**Confidence:** HIGH

## Executive Summary

This is not a traditional software project — it's a content curation and structure project. The goal is to build a flat-file markdown knowledge base optimized for LLM consumption via Claude Code's context loading system. The recommended approach treats this as an **information architecture problem** where the "stack" is file organization patterns, the "features" are curated content types (T-codes, SPRO paths, integration points), and the "architecture" is a hierarchical directory structure leveraging Claude Code's on-demand loading mechanisms.

The core constraint is Claude's context window. Expert practitioners address this by implementing **progressive context loading**: a minimal always-loaded foundation (ECC 6 disambiguation rules, cross-module integration index) combined with on-demand module-specific content that loads only when relevant. Content must be token-efficient (markdown tables, structured sections, no generic text), ECC 6-specific (not contaminated with S/4HANA patterns), and organized by SAP module structure (MM, SD, FI, CO) since that's how SAP practitioners naturally navigate the domain.

The critical risks are (1) ECC 6 vs S/4HANA content contamination — most online SAP content now targets S/4HANA, requiring aggressive filtering, (2) context window overflow — comprehensive SAP coverage can easily exceed 100K tokens if not carefully structured, and (3) generic content waste — documenting what Claude already knows from training data provides zero incremental value. Mitigate by: enforcing explicit ECC 6 version markers on every file, setting hard token budgets per module (8-12K tokens), and applying a "would Claude already know this?" filter to every section.

## Key Findings

### Recommended Stack

This is a content delivery system, not a runtime application. The "stack" consists of markdown file conventions and Claude Code's memory loading mechanisms. Markdown (CommonMark) is the only content format because LLMs parse it natively with high accuracy and it's 20-30% more token-efficient than HTML equivalents. YAML frontmatter provides metadata (module, ECC version, confidence level) that Claude can parse without reading full documents. Git provides version control critical for content accuracy tracking.

**Core technologies:**
- **Markdown with YAML frontmatter**: All content files — token-efficient, LLM-native parsing, metadata for scope understanding
- **Claude Code @import syntax**: Content delivery mechanism — loads referenced files into context up to 5 hops deep, enables selective loading
- **.claude/rules/ auto-loading**: Always-available foundation — disambiguation rules and integration index load automatically every session
- **Directory-scoped CLAUDE.md files**: On-demand module indexing — child directory CLAUDE.md loads when Claude accesses files in that subtree
- **Shell scripts for validation**: Quality assurance — check frontmatter, file sizes, heading structure, internal link integrity without heavy tooling

**Critical non-choices:**
- No MCP server (project constraint)
- No database, no build system, no runtime
- No HTML, no AsciiDoc (less LLM-accurate)
- No separate data files (markdown tables are sufficient and more efficient)

### Expected Features

The knowledge base must provide what Claude's training data lacks: ECC 6-specific details, cross-module integration mechanics, and actionable solutioning patterns. Table stakes are T-code references (curated 100-150 per module, not exhaustive dumps), SPRO configuration paths (exact navigation with prerequisites), org structure relationships (company code to plant, plant to purchasing org assignments), module integration points (OBYC for MM-FI, VKOA for SD-FI), and ECC 6 vs S/4HANA disambiguation (explicitly marked on every file).

**Must have (table stakes):**
- **T-Code reference by module**: 50-80 most-used T-codes per module with descriptions, menu paths, and common use cases
- **SPRO/IMG configuration paths**: Exact navigation sequences with prerequisite dependencies and what each setting controls
- **Org structure reference**: Company code, plant, sales org, purchasing org relationships and assignment rules
- **Module integration points**: Automatic account determination (OBYC, VKOA), document flow triggers, cross-module data dependencies
- **ECC 6 vs S/4HANA disambiguation**: Every file marked as ECC 6 with callouts where S/4 differs (Universal Journal, Business Partner, MATDOC)
- **Business process maps**: End-to-end flows with T-code sequences (P2P: ME51N > ME21N > MIGO > MIRO, O2C: VA01 > VL01N > VF01)
- **Master data structures**: Material master views, vendor/customer account groups, G/L account master, cost centers — what matters for which processes

**Should have (competitive differentiators):**
- **Decision trees for solution design**: "If you need three-way matching, configure X, use T-codes Y, avoid pitfall Z"
- **Account determination walkthroughs**: Step-by-step OBYC logic (movement type > valuation class > transaction key > G/L account)
- **Configuration dependency maps**: Prerequisite chains — cannot configure OBYC until valuation classes exist, which require plants
- **Document flow explanations**: PO > GR (material + accounting doc) > Invoice > Payment with table references (EKKO/EKPO, MKPF/MSEG, BKPF/BSEG)
- **Movement type reference with FI impact**: 101, 102, 261, 301, etc. with specific debit/credit posting patterns
- **Pricing procedure logic (SD)**: Determination chain from sales org + doc type to condition tables
- **Period-end close checklists**: Month/year-end steps by module (MMPV, MR11, F.5D, KSU5)
- **Common error messages with resolutions**: Top 20-30 per module with root cause and fix

**Defer (anti-features to avoid):**
- Exhaustive T-code dumps (103K+ codes — adds noise not signal)
- ABAP code samples (out of scope, different audience)
- Company-specific config values (non-portable, wastes context)
- S/4HANA how-to content (creates the confusion this project eliminates)
- Training curriculum (reference lookup, not pedagogy)
- Screenshots/images (cannot load into LLM context)
- Table field documentation (SE11 does this, minimal ROI)

### Architecture Approach

A hierarchical flat-file system exploiting Claude Code's progressive loading: always-loaded foundation in `.claude/rules/` (3 files: ECC disambiguation, org structure quick-ref, integration index), on-demand module content in `modules/{MM,SD,FI,CO}/` subdirectories (each with CLAUDE.md index, tcodes.md, config-spro.md, processes.md, integration.md, patterns.md), cross-module end-to-end processes in `cross-module/` (procure-to-pay.md, order-to-cash.md, automatic-postings.md), and lookup tables in `reference/` (movement-types.md, posting-keys.md, ecc6-vs-s4.md).

**Major components:**
1. **.claude/rules/ foundation** — Always-loaded ECC 6 identity, org structure reference, master integration index (~3-5K tokens)
2. **Module directories (MM/SD/FI/CO)** — On-demand loading via child CLAUDE.md when subtree entered; each module 8-12K tokens total split across 6-7 files
3. **Cross-module process files** — End-to-end P2P, O2C, R2R narratives stitching multiple modules; load on demand for scenario questions
4. **Reference lookup tables** — Movement types, document types, posting keys; dense structured data for quick lookups

**Key patterns:**
- **Module-local CLAUDE.md as router**: Each module directory gets an index file listing contents and when to use each file
- **T-code tables with context**: Not bare lists — include menu path, usage scenario, related T-codes
- **SPRO paths as navigable trees**: Indented notation matching actual IMG click paths with prerequisites
- **Integration points as bidirectional maps**: Document both directions (MM->FI posting and FI view of that same posting)
- **@import cross-references**: Use `@../../path/to/file.md` for explicit linking Claude can resolve

**Anti-patterns identified:**
- Monolithic module files (triggers lost-in-the-middle degradation)
- Loading everything into .claude/rules/ (wastes context on unrelated queries)
- Generic SAP content without ECC 6 specificity (adds zero value over training data)
- Orphaned cross-references without @import links (Claude cannot navigate)

### Critical Pitfalls

1. **ECC 6 vs S/4HANA content contamination** — Most online SAP content now targets S/4HANA (Universal Journal, Business Partner, Fiori apps). Contamination destroys trust. Prevention: explicit `System: SAP ECC 6.0 (EhP6-EhP8)` header on every file, checklist of high-risk areas (FI/CO ledgers, master data, credit management), prefer pre-2016 sources, include "Not in ECC 6" sections listing commonly confused S/4-only features. Detection: references to ACDOCA, Business Partner, Fiori apps, "embedded analytics."

2. **Context window overflow and lost-in-the-middle degradation** — SAP knowledge across 4 modules can easily exceed 100K tokens. Research shows LLMs have U-shaped attention (strong at beginning/end, weak in middle). Prevention: hard token budget per module (8-12K), structure files so critical info is in first/last sections, modular loading strategy, prefer dense formats (tables over prose), master index for routing. Detection: any file over 15K tokens, total context over 80K, answers contradicting loaded context.

3. **Generic content that adds no value** — Documenting what Claude already knows wastes context. Prevention: apply "would Claude already know this?" test to every section, focus on ECC 6-specific details/cross-module integration/config patterns/decision frameworks/gotchas, never include module overview paragraphs or acronym definitions, each section must enable action not possible with training data alone. Detection: sections starting with "X module is responsible for," Wikipedia-style content, no specific T-codes/tables/paths.

4. **Enhancement Pack ambiguity** — ECC 6.0 spans EhP0 (2006) through EhP8 (2016). Features are EhP-specific but rarely labeled. Prevention: default to EhP6 baseline (most common), flag features requiring EhP7+, note business function activation requirements, include metadata `EhP Baseline: 6 | Features requiring EhP7+: [list]`. Detection: feature descriptions with no EhP attribution, business function references without activation notes.

5. **Cross-module integration gaps** — Module files written in isolation miss integration logic (MM GR triggering FI postings via OBYC, SD billing account assignment via VKOA). Prevention: explicit "Integration Points" section in every module file, document key triggers (MM-FI OBYC, SD-FI VKOA, CO-FI cost elements), create dedicated INTEGRATION.md mapping top 5 end-to-end processes. Detection: module files never referencing other modules' T-codes/tables, no OBYC/VKOA mention, cannot answer "what happens in FI when..." from context.

## Implications for Roadmap

Based on research, a bottom-up dependency-driven approach is critical. SAP's architecture requires foundational elements (org structure, FI backbone) before module-specific content can be meaningful. The feature dependency analysis from FEATURES.md and architecture patterns from ARCHITECTURE.md suggest a 4-phase structure.

### Phase 1: Foundation & Structure
**Rationale:** Everything else depends on org structure definitions and FI as the integration backbone. Cannot document MM->FI postings without FI documented first. Cannot explain SPRO config without org structure reference. This phase establishes the skeleton and disambiguation framework.

**Delivers:**
- Repository structure (`modules/`, `cross-module/`, `reference/`, `.claude/rules/`)
- `.claude/rules/sap-general.md` — ECC 6 identity and disambiguation rules
- `.claude/rules/org-structure.md` — Company code, plant, sales org hierarchy reference
- `modules/fi/` directory complete — FI is the integration target for all other modules
- `reference/ecc6-vs-s4.md` — Master disambiguation document
- Validation scripts (check frontmatter, file sizes, token counts)

**Addresses features:**
- Org structure reference (table stakes)
- ECC 6 vs S/4HANA disambiguation framework (table stakes)
- FI T-codes, SPRO paths, processes, master data (prerequisite for all integration)

**Avoids pitfalls:**
- ECC/S4 contamination by establishing disambiguation rules upfront
- Context overflow by setting token budgets and validation scripts
- Generic content by defining the "would Claude know this?" filter in content guidelines

**Research flag:** Standard patterns — FI module structure is well-documented, no additional research needed.

### Phase 2: Core Logistics (MM & SD)
**Rationale:** With FI foundation in place, build the two highest-usage operational modules. MM and SD integration with FI is where most cross-module questions arise. These modules enable meaningful end-to-end process documentation in Phase 3.

**Delivers:**
- `modules/mm/` directory complete — Procurement, inventory, invoice verification
- `modules/sd/` directory complete — Order-to-cash, pricing, shipping, billing
- `.claude/rules/integration-map.md` — Master index of MM<->FI and SD<->FI touchpoints
- `reference/movement-types.md` — Movement type reference with FI posting impacts
- `reference/document-types.md` — FI, MM, SD document type catalog
- `reference/posting-keys.md` — Debit/credit posting key reference

**Addresses features:**
- T-code reference for MM and SD (table stakes)
- SPRO/IMG configuration paths for MM and SD (table stakes)
- Module integration points for MM-FI and SD-FI (table stakes)
- Business process maps for P2P and O2C foundations (table stakes)
- Movement type reference with FI impact (differentiator)

**Uses stack elements:**
- Module-local CLAUDE.md as router pattern
- T-code tables with context pattern
- SPRO paths as navigable trees pattern
- Integration points as bidirectional maps pattern

**Avoids pitfalls:**
- Cross-module integration gaps by building integration-map.md concurrently
- T-code inaccuracy by limiting to curated 50-80 per module and verifying via SE93 descriptions
- Enhancement Pack ambiguity by establishing EhP6 baseline and flagging EhP7+ features

**Research flags:**
- **MM module:** Moderate research need — Procurement workflows are standard, but ECC 6-specific OBYC account determination logic may need validation during content authoring
- **SD module:** Moderate research need — Pricing procedure determination chain is complex; may need targeted research on ECC 6-specific VKOA logic vs S/4HANA changes

### Phase 3: Controlling & Cross-Module Integration
**Rationale:** CO depends on FI (cost element = G/L account in ECC 6) and on MM/SD for cost flows. With all four core modules documented, can now write authoritative end-to-end process walkthroughs that span multiple modules.

**Delivers:**
- `modules/co/` directory complete — Cost center accounting, internal orders, profitability, product costing
- `cross-module/procure-to-pay.md` — Full P2P: MM + FI + CO touchpoints
- `cross-module/order-to-cash.md` — Full O2C: SD + FI + CO touchpoints
- `cross-module/record-to-report.md` — Full R2R: FI + CO period-end processes
- `cross-module/automatic-postings.md` — Account determination walkthroughs (OBYC, VKOA, OKB9)
- Update `integration-map.md` with CO integration points

**Addresses features:**
- T-code reference for CO (table stakes)
- Module integration points for CO-FI and CO-MM (table stakes)
- Master data structures for CO (cost centers, cost elements, profit centers) (table stakes)
- Account determination walkthroughs (differentiator)
- Document flow explanations across modules (differentiator)
- Configuration dependency maps (differentiator)

**Implements architecture:**
- Cross-module process files component
- End-to-end narrative stitching multiple modules

**Avoids pitfalls:**
- Cross-module integration gaps by treating integration as first-class deliverable
- Configuration without context by framing OBYC/VKOA as decision trees with business scenarios

**Research flags:**
- **CO module:** Standard patterns — cost center accounting well-documented
- **Cross-module processes:** Low research need — process flows are documented, synthesis required not new research

### Phase 4: Solutioning Intelligence & Operational Content
**Rationale:** With all foundational and process content in place, layer on the highest-value differentiators: solution design patterns, scenario playbooks, and operational checklists. These require all prior content as building blocks.

**Delivers:**
- `modules/{module}/patterns.md` for each module — Decision trees for common business requirements
- Cross-module scenario playbooks — Third-party order processing, subcontracting, make-to-order
- Pricing procedure logic deep-dive for SD
- Period-end close checklists by module (MMPV, MR11, F.5D, KSU5, COIT)
- Common error messages with resolutions (incremental, top 20-30 per module)

**Addresses features:**
- Decision trees for solution design (differentiator)
- Pricing procedure logic (differentiator)
- Cross-module scenario playbooks (differentiator)
- Period-end close checklists (differentiator)
- Common error messages with resolutions (differentiator)

**Avoids pitfalls:**
- Configuration without context by presenting config as scenario-driven decision trees
- Batch/background processing neglect by including batch variants in period-end checklists

**Research flags:**
- **Solution design patterns:** Needs targeted research — Decision trees for specific scenarios (consignment, split valuation, third-party) may require validation with SAP community or Notes
- **SD pricing procedures:** High research need — Pricing is the most complex SD area; may need `/gsd:research-phase` for condition table/access sequence determination logic

### Phase Ordering Rationale

- **Bottom-up dependencies:** FI before MM/SD/CO because all post to FI. Org structure before all modules because config requires org units. This is SAP's own architectural dependency chain.
- **Value gradient:** Each phase delivers usable value standalone. Phase 1 = better reference tool. Phase 2 = process guide. Phase 3 = config assistant. Phase 4 = solutioning partner.
- **Risk front-loading:** Disambiguation and context budget constraints are Phase 1 concerns to avoid rework. Integration gaps are Phase 2/3 concerns where most questions arise.
- **Deferral of high-complexity/low-dependency features:** Solution design patterns and pricing procedure deep-dives are valuable but can be built only after foundational content exists. They're also the features most likely to need iterative refinement based on usage.

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 2 (SD content):** Pricing procedure determination logic is complex and documentation quality varies; may need `/gsd:research-phase` specifically for condition technique
- **Phase 4 (solution patterns):** Decision trees for specific scenarios (consignment, split valuation, third-party order processing) may need SAP Note searches or community validation

**Phases with standard patterns (skip research):**
- **Phase 1 (FI foundation):** FI module structure and integration patterns are extremely well-documented
- **Phase 2 (MM content):** Procurement workflows follow standard patterns; ECC 6 behavior is well-established
- **Phase 3 (CO content):** Cost center accounting and internal orders have stable, documented patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | Based on Claude Code official documentation, progressive context loading research, and LLM markdown parsing behavior. The flat-file markdown approach with .claude/rules/ auto-loading and @import syntax is well-tested. Token efficiency claims verified via multiple sources. |
| Features | **HIGH** | Feature set derived from SAP community consensus (highest-voted questions/topics), official T-code lists, SPRO documentation, and practitioner feedback on most-used capabilities. MVP phasing matches dependency analysis and aligns with "table stakes vs differentiators" framework. |
| Architecture | **HIGH** | Directory structure and loading patterns follow documented Claude Code behavior and align with SAP's module-first mental model. Context window budgets based on empirical token counting. Cross-referencing strategy leverages @import resolution. Anti-patterns identified via lost-in-the-middle research. |
| Pitfalls | **HIGH** | Top pitfalls validated across multiple sources: ECC/S4 contamination confirmed via SAP community complaints about broken documentation, context window issues grounded in LLM research (Liu et al. 2024), Enhancement Pack ambiguity documented in community Q&A, integration gaps align with most common SAP support questions. |

**Overall confidence:** **HIGH**

The research converged on consistent recommendations across all four areas. The "non-traditional project" nature (content curation not software development) was recognized in all research outputs. Core constraints (no MCP, context window limits, ECC 6 specificity) were consistently addressed. The phased approach aligns with both technical dependencies (FI before other modules) and domain expertise (module integration points are where SAP complexity lives).

### Gaps to Address

- **Enhancement Pack baseline decision**: Research recommends EhP6 as baseline, but if target users are on EhP5 or EhP8, content may need adjustment. **Resolution:** Survey target users during Phase 1 to confirm EhP distribution; adjust baseline if needed before Phase 2 content authoring.

- **Country localization scope**: Pitfall 9 identifies country-specific configuration as a risk, but research did not determine target geography. Tax, payment, dunning, and output determination vary significantly by country. **Resolution:** Define country scope in Phase 1 planning; if multi-country, establish which countries and flag localization-sensitive sections during content authoring.

- **Token budget validation**: Context window estimates are theoretical (8-12K per module, <60K total). Actual token counts will vary with content density. **Resolution:** Implement token counting script in Phase 1; validate budgets after Phase 2 completion; adjust Phase 3/4 scope if budget is tighter than estimated.

- **Source verification cadence**: Pitfall 12 notes content staleness risk. ECC 6 is in maintenance mode (no new features), but SAP Notes and corrections accumulate. **Resolution:** Define quarterly review cadence; assign content owner for each module; establish SAP Note monitoring process (filter by module, ECC 6 relevance).

- **Pricing procedure depth**: SD pricing is flagged as high-complexity in Phase 4. Unclear whether full condition technique depth is in scope or if a conceptual overview suffices. **Resolution:** During Phase 2 SD authoring, assess common pricing questions; if deep condition table/access sequence detail is frequently needed, plan `/gsd:research-phase` for Phase 4; otherwise, defer to post-launch incremental content.

## Sources

### Primary (HIGH confidence)
- [Claude Code Memory Documentation](https://code.claude.com/docs/en/memory) — CLAUDE.md hierarchy, .claude/rules/ auto-loading, @import syntax, on-demand loading behavior
- [Anthropic Blog - Using CLAUDE.md Files](https://claude.com/blog/using-claude-md-files) — Official guidance on CLAUDE.md usage patterns
- [Lost in the Middle: How Language Models Use Long Contexts (Liu et al., 2024)](https://arxiv.org/abs/2307.03172) — Context window attention degradation research
- [SAP Help Portal - EhP8 for ERP 6.0](https://help.sap.com/doc/1dc4f8c981ea45d8801fe2aa9682d751/6.18.latest/en-US/loio3764eddbf3f94d3c8249ca6b7119e72a.pdf) — Official ECC 6 documentation
- [SAP Press - Key Differences Between SAP ECC and S/4HANA](https://blog.sap-press.com/key-differences-between-sap-ecc-and-sap-s4hana-a-detailed-comparison) — Authoritative ECC vs S/4 comparison

### Secondary (MEDIUM confidence)
- [Builder.io - How to Write a Good CLAUDE.md File](https://www.builder.io/blog/claude-md-guide) — Best practices for CLAUDE.md organization
- [Progressive Context Loading](https://williamzujkowski.github.io/posts/from-150k-to-2k-tokens-how-progressive-context-loading-revolutionizes-llm-development-workflows/) — Evidence for on-demand loading vs monolithic approach
- [LLM-Friendly Content in Markdown (Webex Developer Blog)](https://developer.webex.com/blog/boosting-ai-performance-the-power-of-llm-friendly-content-in-markdown) — Markdown optimization for LLM consumption
- [Pathlock - SAP T-Code List by Module](https://pathlock.com/blog/sap-t-code-list/) — T-code organization patterns
- [SAP Community - Integration Point of MM-FI-SD](https://blogs.sap.com/2013/12/31/integration-point-of-mm-fi-sd-in-sap-erp/) — Cross-module integration points
- [SAP Community - FI-SD Integration VKOA](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/fi-sd-integration-vkoa-understanding-flow-sap-ecc/ba-p/13488492) — VKOA account determination
- [TutorialsPoint - SAP MM Enterprise Structure](https://www.tutorialspoint.com/sap_mm/sap_mm_enterprise_structure.md) — Org structure hierarchy

### Tertiary (LOW confidence, requires validation)
- [Regal AI - RAG Playbook: Structuring Knowledge Bases](https://www.regal.ai/blog/rag-playbook-structuring-knowledge-bases) — General knowledge base patterns (not SAP-specific)
- [JetBrains Research - Efficient Context Management for LLM Agents (2025)](https://blog.jetbrains.com/research/2025/12/efficient-context-management/) — Context management strategies (not Claude Code-specific)

---

*Research completed: 2026-02-16*
*Ready for roadmap: Yes*
