# Domain Pitfalls

**Domain:** SAP ECC 6.0 Curated Knowledge Base for LLM Consumption
**Researched:** 2026-02-16

## Critical Pitfalls

Mistakes that cause rewrites, produce harmful guidance, or undermine trust in the knowledge base.

### Pitfall 1: ECC 6 vs S/4HANA Content Contamination

**What goes wrong:** Reference content silently mixes ECC 6 and S/4HANA information. A document describes a process or T-code that works differently (or does not exist) in ECC 6 because the source material was written for S/4HANA. The LLM then confidently recommends S/4HANA-only features to users on ECC systems.

**Why it happens:** The majority of recent SAP content online (blogs, tutorials, SAP Help Portal updates) targets S/4HANA. Google results for "SAP MM goods receipt" increasingly return S/4HANA Fiori-based workflows. Writers unconsciously pull from these sources. Key structural differences are subtle -- for example, S/4HANA merges FI and CO into a single Universal Journal table (ACDOCA), eliminates separate customer/vendor master data in favor of Business Partners, and obsoletes roughly 233+ transaction codes from ECC.

**Consequences:** Users following the guidance attempt to use T-codes or configurations that do not exist in their ECC 6 system. Worse, they may attempt architectural decisions (like expecting Universal Journal behavior) that fundamentally do not apply. This destroys trust in the entire knowledge base.

**Prevention:**
- Every content file must have an explicit header: `System: SAP ECC 6.0 (EhP6-EhP8)` -- never leave version ambiguous
- Maintain a known-contamination checklist of the highest-risk areas: FI/CO (Universal Journal vs separate ledgers), Master Data (Business Partner vs KNA1/LFA1), Material Ledger behavior, and credit management (UKM vs FD32)
- When sourcing content, prefer SAP Help Portal filtered to ERP 6.0 (not S/4HANA), SAP Press books published before 2016, and community posts explicitly tagged ECC
- Include a `## Not in ECC 6` section in each module file listing commonly confused S/4HANA-only features

**Detection (warning signs):**
- References to Fiori apps or "Manage" app patterns (e.g., "Manage Purchase Orders" instead of ME23N)
- Mention of ACDOCA, Business Partner in non-CRM context, Simplified Data Model
- T-codes that start with BP (Business Partner) used for customer/vendor maintenance
- Any mention of "embedded analytics" or CDS views as standard functionality

**Phase relevance:** Must be enforced from Phase 1 (initial content creation) and validated in every review cycle.

---

### Pitfall 2: Enhancement Pack Ambiguity

**What goes wrong:** Content describes ECC 6.0 features without specifying which Enhancement Pack (EhP) introduced them. A feature available only in EhP7+ is documented as standard ECC 6 behavior. Organizations on EhP5 or EhP6 follow the guidance and find it does not apply.

**Why it happens:** ECC 6.0 spans EhP0 (2006) through EhP8 (2016) -- a decade of incremental feature delivery. Most documentation says "SAP ECC 6.0" without specifying the EhP level. Features like the new General Ledger migration tools, extended warehouse management integration, and various MM/SD enhancements were delivered incrementally across EhP levels.

**Consequences:** Recommendations reference functionality that does not exist in the reader's system. Configuration guides include steps for business functions that have not been activated. This is particularly dangerous because the features technically exist in the codebase but require explicit activation via Switch Framework (SFW5).

**Prevention:**
- Default content to EhP6 as the baseline (most common production level as of 2025-2026) and explicitly flag features requiring EhP7 or EhP8
- For each significant feature, note whether it requires a specific business function activation (e.g., LOG_MM_CI_1 for MM enhancements)
- Include a metadata field in each content file: `EhP Baseline: 6 | Features requiring EhP7+: [list]`

**Detection (warning signs):**
- Feature descriptions with no EhP attribution
- References to business functions without activation status notes
- Content sourced from SAP release notes for a specific EhP presented as general ECC content

**Phase relevance:** Address during Phase 1 content structure design. Enforce in Phase 2+ content authoring.

---

### Pitfall 3: T-Code and Menu Path Inaccuracy

**What goes wrong:** Transaction codes are listed with incorrect descriptions, wrong module assignments, or outdated menu paths. Configuration T-codes are listed without their prerequisite customizing steps. Users follow a T-code reference that leads them to the wrong transaction or a transaction that requires configuration they have not completed.

**Why it happens:** SAP has roughly 100,000 transaction codes. Many online T-code lists are scraped, copied, and re-copied without verification. Menu paths change across support pack levels. Some T-codes are technically present but functionally irrelevant without specific configuration (e.g., MIGO variants require movement type configuration). Third-party T-code lists frequently contain errors in module assignment (e.g., listing a CO T-code under FI, or a WM T-code under MM).

**Consequences:** At best, users waste time. At worst, they execute wrong transactions, post to wrong accounts, or believe a capability does not exist because they used the wrong T-code.

**Prevention:**
- Limit T-code documentation to the most-used 50-80 per module (MM, SD, FI, CO), not exhaustive lists
- For each T-code, document: code, description, module, purpose, prerequisite config, and one common use case
- Verify every T-code against SAP's SE93 descriptions (available in SAP Help Portal's transaction code documentation)
- Never bulk-copy T-code lists from third-party sites without verification

**Detection (warning signs):**
- T-code lists with more than 200 entries per module (signals bulk-copied, unverified content)
- T-codes listed without descriptions or with single-word descriptions
- Menu paths that include "SAP Easy Access" without the full navigation hierarchy
- Missing distinction between display (e.g., ME23N) and change (e.g., ME22N) variants

**Phase relevance:** Phase 2 (content authoring). Build a T-code verification checklist before writing module content.

---

### Pitfall 4: Context Window Overflow and Lost-in-the-Middle Degradation

**What goes wrong:** The knowledge base grows to consume most or all of the LLM's context window. Even within the window limit, critical information buried in the middle of large documents is effectively ignored by the model. The LLM produces answers that miss relevant content that is technically present in context.

**Why it happens:** SAP is vast. The temptation is to document everything -- every T-code, every config step, every integration point. Four modules (MM, SD, FI, CO) with thorough coverage can easily exceed 100,000 tokens. Research on "lost in the middle" (Liu et al., 2024, published in TACL) demonstrates that LLMs show a U-shaped attention pattern: they attend well to content at the beginning and end of the context, but significantly degrade when critical information is in the middle.

**Consequences:** The knowledge base is loaded but the LLM ignores most of it. Users get generic answers despite having detailed reference material. Worse, the model may confidently answer from its training data (which may include S/4HANA content) rather than from the provided context, because the relevant context section did not receive sufficient attention.

**Prevention:**
- Set a hard token budget per module file (target: 8,000-12,000 tokens per module, total knowledge base under 60,000 tokens)
- Structure files so the most critical information (key T-codes, critical config, integration points) appears in the first and last sections of each file
- Use a modular loading strategy: load only the relevant module file(s) for a given query rather than the entire knowledge base
- Prefer dense, structured formats (tables, bulleted lists) over narrative prose -- they compress more information into fewer tokens
- Include a master index file that the LLM reads first to determine which module files to reference

**Detection (warning signs):**
- Any single markdown file exceeding 15,000 tokens
- Total loaded context exceeding 80,000 tokens
- LLM answers that contradict information present in the loaded context
- LLM answers that are suspiciously generic despite specific reference content being available

**Phase relevance:** Phase 1 (architecture/structure design). Must be a hard constraint before any content is written.

---

### Pitfall 5: Generic Content That Adds No Value Over Training Data

**What goes wrong:** The knowledge base contains textbook-level descriptions that the LLM already knows from training. Content like "MM stands for Materials Management and handles procurement" adds zero value and wastes context window space. The knowledge base becomes a worse version of what Claude already knows.

**Why it happens:** Authors default to comprehensive documentation style, starting from basics. SAP training materials follow a pedagogical structure (overview, then details) that is appropriate for human learning but wasteful for LLM context. There is a natural tendency to "cover the basics" before getting specific.

**Consequences:** Precious context window is consumed by information the LLM already has. The unique value of the knowledge base -- org-specific process flows, specific T-code guidance for common scenarios, ECC-specific gotchas, cross-module integration details -- gets crowded out by generic content.

**Prevention:**
- Apply the "would Claude already know this?" test to every section. If yes, cut it
- Focus content on: (a) ECC 6-specific details that distinguish it from S/4HANA, (b) cross-module integration specifics, (c) common configuration patterns with specific settings, (d) decision frameworks for choosing between approaches, (e) gotchas and warnings that are not in standard documentation
- Never include module overview paragraphs, SAP history, or acronym definitions
- Each section should pass the "actionable specificity" test: does this content enable someone to do something they could not do with just the LLM's training data?

**Detection (warning signs):**
- Sections that start with "X module is responsible for..."
- Content that reads like a Wikipedia article about SAP
- Absence of specific T-codes, table names, configuration paths, or field values
- Content that could apply to any ERP system, not specifically SAP ECC 6

**Phase relevance:** Phase 1 (content strategy) and Phase 2 (content authoring). Establish the "no generic content" rule before writing begins.

---

## Moderate Pitfalls

### Pitfall 6: Cross-Module Integration Gaps

**What goes wrong:** Module files are written in isolation. The MM file describes procurement end-to-end but does not explain how goods receipt triggers FI postings via automatic account determination (OBYC). The SD file covers order-to-cash but omits the handoff to FI via billing document account assignment (VKOA). Users ask cross-module questions and the LLM cannot synthesize an answer because the integration logic is not documented.

**Prevention:**
- Include an explicit "Integration Points" section in every module file
- Document the key cross-module triggers: MM-FI (OBYC valuation class to G/L mapping), SD-FI (VKOA account determination for billing), MM-SD (material master sales views, availability check), CO-FI (cost element linkage, assessment/distribution cycles), SD-MM (third-party order processing, intercompany)
- Create a dedicated INTEGRATION.md file that maps cross-module data flows for the top 5 end-to-end processes (Procure-to-Pay, Order-to-Cash, Record-to-Report, Plan-to-Produce, Hire-to-Retire if HR is in scope)

**Detection (warning signs):**
- Module files that never reference T-codes or tables from other modules
- No mention of automatic account determination configuration
- Questions about "what happens in FI when..." that the LLM cannot answer from loaded context

**Phase relevance:** Phase 2 (content authoring). Assign integration points as explicit deliverables, not afterthoughts.

---

### Pitfall 7: Configuration Without Context

**What goes wrong:** Content lists configuration T-codes and settings but not WHY a setting should have a particular value. For example, documenting that movement type 101 is for goods receipt without explaining when to use 101 vs 103 (GR to blocked stock) vs 105 (GR to production). Users get a reference sheet but cannot make decisions.

**Prevention:**
- For every configuration setting, include: what it controls, common values, when to choose each value, and what goes wrong with the wrong choice
- Frame configuration as decision trees, not flat lists: "If [scenario], use [setting] because [reason]"
- Include the business scenario that drives the configuration choice, not just the technical setting

**Detection (warning signs):**
- Configuration tables with columns for "Setting" and "Value" but no "When/Why" column
- Content that reads like IMG (Implementation Guide) node descriptions without business context
- No mention of consequences for wrong settings

**Phase relevance:** Phase 2 (content authoring). Build decision-tree templates before writing configuration content.

---

### Pitfall 8: SAP Help Portal Link Rot

**What goes wrong:** Content references SAP Help Portal URLs that break within weeks or months. SAP has a well-documented history of restructuring their help portal, invalidating URLs. Any content that depends on these links for verification or deeper reading becomes degraded.

**Prevention:**
- Never include SAP Help Portal URLs in the knowledge base content itself -- they will break
- Instead, reference by: SAP Note number (e.g., "SAP Note 2249880"), Help Portal document title and path (e.g., "SAP Help > ERP > MM > Purchasing > Purchase Order"), or table/T-code reference that can be independently searched
- Store source URLs in a separate metadata/sourcing file for author reference, not in the user-facing content

**Detection (warning signs):**
- Markdown files with help.sap.com URLs
- "For more information, see [link]" patterns in the content
- Review cycle reveals broken links

**Phase relevance:** Phase 1 (content structure standards). Establish the no-URL rule upfront.

---

### Pitfall 9: Localization and Country-Specific Assumption Leakage

**What goes wrong:** Content assumes a specific country's configuration (typically US or Germany) without stating the assumption. Tax procedure, payment method, dunning, output determination, and pricing all vary significantly by country. SAP ECC supports 65 countries with different localizations. A document describing tax calculation with TAXUSJ (US tax) is useless for a UK implementation using TAXGB.

**Prevention:**
- Explicitly state country assumptions in every section that involves localization-sensitive configuration (tax, payments, legal reporting, output types)
- Focus content on country-agnostic concepts and flag where country-specific configuration diverges
- If the knowledge base serves a specific org, document that org's country scope and limit localization content accordingly
- Include a "Localization-Sensitive" tag on sections that vary by country

**Detection (warning signs):**
- Tax procedure references without country context
- Payment method configuration without specifying country
- Output determination setup that assumes a specific form type
- Dunning procedures described without noting country-specific legal requirements

**Phase relevance:** Phase 2 (content authoring). Define the target country scope before writing tax/payment/legal content.

---

## Minor Pitfalls

### Pitfall 10: Organizational Structure Overload

**What goes wrong:** Content exhaustively documents every possible organizational unit (company code, plant, storage location, purchasing organization, sales organization, distribution channel, division, etc.) and their relationships, consuming significant token budget on structural content that varies entirely by implementation.

**Prevention:**
- Document organizational structures as a concept overview with a relationship diagram, not as exhaustive configuration guides
- Focus on: what decisions each org unit drives, common mistakes in org structure design, and how org units affect cross-module behavior
- Keep this to one concise section, not a chapter

**Phase relevance:** Phase 2 (content authoring). Allocate a fixed, small token budget for org structure content.

---

### Pitfall 11: Neglecting Batch/Background Processing Context

**What goes wrong:** Content describes interactive transactions but omits batch processing variants (MRP runs via MD01/MDBT, payment runs via F110, dunning via F150, billing due list via VF04) and their scheduling/monitoring requirements. Users ask "how do I run MRP" and get the foreground T-code instead of the production-appropriate batch approach.

**Prevention:**
- For every major process, document both interactive and batch variants
- Note which approach is appropriate for production vs testing
- Include monitoring T-codes (SM37, SM36 for job scheduling)

**Phase relevance:** Phase 2 (content authoring). Include batch processing as a standard section template.

---

### Pitfall 12: Stale Content Without a Maintenance Plan

**What goes wrong:** Knowledge base is created once and never updated. SAP Notes, support pack corrections, and community-discovered issues accumulate. Content that was accurate at creation time drifts. There is no trigger or process for updates.

**Prevention:**
- Establish a quarterly review cadence (lightweight -- check for SAP Notes affecting documented areas)
- Tag each file with `Last verified: YYYY-MM-DD`
- Maintain a change log that tracks what was updated and why
- Since ECC 6 is in maintenance mode (not receiving new features), drift is slower than for S/4HANA, but corrections and community knowledge still evolve

**Phase relevance:** Phase 3+ (post-launch maintenance). Define the maintenance cadence during Phase 1 planning.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Content structure design | Context window overflow (Pitfall 4) | Set token budgets and file structure before any writing |
| Content strategy | Generic content (Pitfall 5) | Define the "would Claude know this?" test as a gate |
| MM content authoring | ECC/S4 contamination (Pitfall 1) in procurement workflows | S/4HANA simplified procurement is heavily documented online; verify ECC-specific flows |
| SD content authoring | ECC/S4 contamination (Pitfall 1) in credit management | S/4HANA UKM replaces FD32-based credit; ensure ECC credit management is documented |
| FI content authoring | ECC/S4 contamination (Pitfall 1) in ledger architecture | New GL vs Universal Journal is the single biggest ECC/S4 difference; get this right |
| CO content authoring | Integration gaps (Pitfall 6) with FI | CO-FI integration is where most cross-module questions arise |
| T-code reference creation | Inaccuracy (Pitfall 3) from bulk copying | Verify each T-code; limit scope to most-used |
| Integration documentation | Cross-module gaps (Pitfall 6) | Write integration docs as a dedicated deliverable, not a footnote |
| Review and validation | Enhancement pack ambiguity (Pitfall 2) | Review every feature claim for EhP attribution |
| Ongoing maintenance | Content staleness (Pitfall 12) | Define review cadence before launch |

## Sources

- [SAP Help Portal - EhP8 for ERP 6.0](https://help.sap.com/doc/1dc4f8c981ea45d8801fe2aa9682d751/6.18.latest/en-US/loio3764eddbf3f94d3c8249ca6b7119e72a.pdf)
- [SAP Community - EhP6 vs EhP7 Differences](https://community.sap.com/t5/enterprise-resource-planning-q-a/difference-between-ehp6-and-ehp7-in-sap-ecc-6-0/qaq-p/12590553)
- [SAP Community - Broken Help Portal Links](https://community.sap.com/t5/technology-q-a/why-are-sap-help-documentation-links-always-broken/qaq-p/12493224)
- [SAP Community - Outdated Documentation](https://community.sap.com/t5/sap-builders-discussions/outdated-useless-documentation/m-p/13763829)
- [SAP Blog - ECC to S/4HANA Transaction Code Mapping](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/how-to-find-replaced-sap-s4-hana-transaction-codes-against-ecc-obsolete/ba-p/13552479)
- [Key Differences Between SAP ECC and S/4HANA (SAP Press)](https://blog.sap-press.com/key-differences-between-sap-ecc-and-sap-s4hana-a-detailed-comparison)
- [Understanding Obsolete Transactions in S/4HANA (SOAIS)](https://soais.com/understanding-obsolete-transactions-in-sap-s-4hana/)
- [S/4HANA Finance - New vs Old Transaction Codes](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/s-4hana-finance-new-vs-old-transaction-code/ba-p/13409452)
- [Lost in the Middle: How Language Models Use Long Contexts (Liu et al., 2024)](https://arxiv.org/abs/2307.03172)
- [JetBrains Research - Efficient Context Management for LLM Agents (2025)](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
- [SAP Knowledge Graphs for LLM Grounding](https://community.sap.com/t5/technology-blog-posts-by-sap/knowledge-graphs-for-llm-grounding-and-avoiding-hallucination/ba-p/13779734)
- [RAG Playbook: Structuring Knowledge Bases (Regal AI)](https://www.regal.ai/blog/rag-playbook-structuring-knowledge-bases)
- [SAP MM-SD and SD-FI Integration Points (ERP Documents)](https://erp-docs.com/2777/sap-mm-sd-and-sd-fi-integration-points/)
- [SAP ERP Country-Specific Localization Guides (KBA 3421840)](https://userapps.support.sap.com/sap/support/knowledge/en/3421840)
