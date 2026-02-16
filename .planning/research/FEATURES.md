# Feature Landscape

**Domain:** SAP ECC 6.0 Knowledge Base for Claude Code Solutioning
**Researched:** 2026-02-16

## Table Stakes

Features users expect. Missing = knowledge base is useless compared to Claude's baseline training.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **T-Code Reference by Module** | Without correct T-codes, the knowledge base fails its primary use case. Users need transaction codes with descriptions, menu paths, and which module they belong to. | Medium | ~100-150 critical T-codes across MM/SD/FI/CO. Not all 103K -- curate the ones consultants actually use daily. |
| **SPRO/IMG Configuration Paths** | Config guidance is the #2 reason to build this. Users need exact SPRO navigation paths (e.g., SPRO > IMG > Materials Management > Valuation and Account Assignment > Account Determination). | High | Deep tree structure varies by EHP level. Document the path, the config table behind it, and what each setting controls. |
| **Org Structure Reference** | Every SAP conversation starts with org structure. Company Code, Plant, Storage Location, Sales Org, Distribution Channel, Division, Purchasing Org, Controlling Area -- and critically, the assignment rules between them. | Low | Relatively static content. One-to-many vs many-to-many relationships are the key value (e.g., plant to company code is many-to-one; plant to purchasing org is many-to-many). |
| **Module Integration Points** | The #1 thing Claude gets wrong today: how MM postings hit FI (OBYC), how SD billing hits FI (VKOA), how CO allocations work. Without this, solutioning advice misses downstream impacts. | High | Must cover automatic account determination: OBYC for MM-FI, VKOA for SD-FI, OKB9 for CO default account assignments. Document which movement types trigger which postings. |
| **ECC 6 vs S/4HANA Disambiguation** | The explicit pain point driving this project. Claude's training data mixes ECC and S/4 constantly. Every content piece must be marked as ECC 6 specific, with callouts where S/4 differs. | Medium | Key differences: ACDOCA universal journal (S/4 only), MATDOC replacing MKPF/MSEG, Business Partner replacing separate customer/vendor masters, account-based COPA as default in S/4. |
| **Business Process Maps (End-to-End)** | Users need to trace a business process across modules and transactions. P2P: ME51N > ME21N > MIGO > MIRO > F110. O2C: VA01 > VL01N > VL02N (PGI) > VF01 > F-28. | Medium | Map each step to: transaction code, module, what it creates (document type), and what it triggers downstream (FI posting, stock update, etc.). |
| **Master Data Structures** | Material Master (views and their purposes), Vendor Master (account groups), Customer Master (account groups), G/L Account Master, Cost Center/Cost Element/Profit Center. Without understanding master data, config advice is hollow. | Medium | Focus on which views/fields matter for which processes, not exhaustive field lists. E.g., material master Purchasing view is required for P2P, Sales views for O2C. |

## Differentiators

Features that set this knowledge base apart from "just asking Claude without context." These are where the real value lives.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Decision Trees for Solution Design** | When someone says "we need three-way matching," the knowledge base should walk through: what config is needed (tolerance keys, GR/IR settings), what T-codes are involved, what the process flow looks like, and what can go wrong. This is solutioning, not reference. | High | Start with 10-15 common business requirements mapped to SAP solution patterns. E.g., "consignment processing," "intercompany sales," "split valuation," "down payment processing." |
| **Account Determination Walkthroughs** | Step-by-step explanation of how SAP determines which G/L account to post to for a given transaction. OBYC logic for MM: movement type > valuation class > transaction event key > G/L account. VKOA logic for SD: chart of accounts > sales org > account key > G/L account. | High | This is the hardest thing for non-SAP people to understand and the most common source of incorrect FI postings. Visual/structured walkthroughs are extremely high value. |
| **Configuration Dependency Maps** | Which config depends on which other config. You cannot configure automatic account determination (OBYC) until you have valuation classes, which require valuation areas, which require plant assignments. Document prerequisite chains. | High | Prevents the #1 config mistake: trying to configure something before its prerequisites exist. Build as directed dependency graphs per module. |
| **Document Flow Explanations** | When a PO is created, what documents cascade? PO > Goods Receipt (material doc + accounting doc) > Invoice (MM invoice doc + accounting doc) > Payment (FI clearing doc). Map the full document chain with table references. | Medium | Users constantly ask "I posted X, why did Y happen?" Document flow answers this. Include the tables where each document lives (EKKO/EKPO, MKPF/MSEG, RBKP/RSEG, BKPF/BSEG). |
| **Movement Type Reference with FI Impact** | Movement types (101, 102, 103, 104, 105, 122, 161, 201, 261, 301, 309, 311, 541, etc.) are the backbone of inventory management. Each one has specific debit/credit patterns. Document what each does, when to use it, and what it posts to FI. | Medium | Consultants memorize maybe 10-15 movement types. Having a complete reference with FI posting logic is genuinely differentiating. |
| **Pricing Procedure Logic (SD)** | How SAP determines price in a sales order: pricing procedure determination (sales org + dist channel + division + doc pricing procedure + customer pricing procedure), condition types, access sequences, condition tables. | High | Pricing is the most complex area of SD configuration. A clear explanation of the determination chain is worth more than any T-code list. |
| **Period-End Close Checklists** | Month-end and year-end closing steps by module. MM: MMPV (period close), MR11 (GR/IR maintenance). FI: F101 (foreign currency valuation), F.5D (balance carryforward). CO: KSU5 (assessment), COIT (internal order settlement). | Medium | Operational knowledge that every SAP team needs and that Claude cannot reliably provide from training data alone. |
| **Common Error Messages with Resolutions** | Top 20-30 error messages per module with root cause and fix. E.g., M7021 "No new period allowed" means MMPV was not run. Or VF024 "Billing block" means the sales order has a billing block that must be removed. | Medium | This is the "Stack Overflow for SAP" content. Extremely practical, saves hours of troubleshooting. |
| **Cross-Module Scenario Playbooks** | End-to-end scenarios that span multiple modules: "Third-party processing" (SD triggers MM PO, vendor ships directly to customer), "Subcontracting" (MM provides components to vendor, receives finished goods), "Make-to-Order" (SD order triggers PP production order). | High | These are the scenarios where integration knowledge is tested. Claude without context gives generic answers; with these playbooks, it gives actionable step-by-step guidance. |

## Anti-Features

Features to explicitly NOT build. Including these would waste effort or actively harm the knowledge base.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Exhaustive T-Code Dumps** | There are 103,725 T-codes in ECC 6. Dumping them all adds noise, not signal. Most are system-internal or rarely used. Claude's context window is precious. | Curate 100-150 T-codes per module that consultants actually use. Organize by process, not alphabetically. |
| **ABAP Code Samples** | Out of scope per PROJECT.md. This is a functional solutioning knowledge base. ABAP content would bloat the context and serve a different audience. | Reference relevant function modules or BAPIs only when they are part of integration patterns (e.g., BAPI_PO_CREATE1 for PO creation via integration). |
| **Company-Specific Configuration Values** | Specific GL account numbers, cost center hierarchies, or org unit IDs are meaningless outside one system. Including them makes the knowledge base non-portable. | Document the structure and logic (e.g., "you need a valuation grouping code per valuation area") not specific values. |
| **S/4HANA How-To Content** | Scope is ECC 6. Including S/4 how-to content will cause exactly the confusion this project exists to eliminate. | Only reference S/4 in disambiguation callouts: "In S/4HANA, this changes to X. In ECC 6, the behavior is Y." |
| **SAP Basis/System Administration** | Transport management, kernel upgrades, system monitoring, user administration. Different audience, different knowledge domain. | Mention Basis-adjacent topics only where they directly affect functional work (e.g., transport requests for config moves). |
| **Training Curriculum or Exercises** | This is a reference for Claude, not a training course. Tutorial-style content wastes context window and does not serve the lookup use case. | Structure content for quick retrieval: headers, tables, concise explanations. Assume the reader knows SAP basics. |
| **PDF/Screenshot-Heavy Content** | Markdown files for Claude Code. Images cannot be loaded into context. Screenshots of SAP screens add zero value. | Describe menu paths and screen layouts in text. Use ASCII tables or structured markdown for visual concepts. |
| **Table Field-Level Documentation** | Documenting every field in EKKO, BSEG, VBAK etc. is massive effort for marginal value. SAP's data dictionary (SE11) already does this. | Document key fields that drive business logic (e.g., EKKO-BSART for PO document type, EKKO-LIFNR for vendor) and their significance, not every field. |

## Feature Dependencies

```
Org Structure Reference
  --> Master Data Structures (master data is organized by org units)
    --> T-Code Reference (T-codes operate on master/transactional data)
      --> Business Process Maps (processes chain T-codes together)
        --> Document Flow Explanations (process steps create document chains)

SPRO/IMG Configuration Paths
  --> Configuration Dependency Maps (paths have prerequisite chains)
    --> Account Determination Walkthroughs (account determination is configured via SPRO)
      --> Module Integration Points (integration is configured through account determination)

ECC 6 vs S/4HANA Disambiguation
  --> (crosscuts everything -- applied as annotations on all other content)

Movement Type Reference
  --> Module Integration Points (movement types trigger FI postings)
  --> Document Flow (movement types create material/accounting documents)

Business Process Maps
  --> Decision Trees for Solution Design (processes inform solution patterns)
  --> Cross-Module Scenario Playbooks (processes combine into scenarios)
  --> Period-End Close Checklists (processes create period-end work)
```

## MVP Recommendation

**Phase 1 -- Foundation (must ship first):**
1. **Org Structure Reference** -- prerequisite for everything else, low complexity
2. **T-Code Reference by Module** -- immediate practical value, medium complexity
3. **ECC 6 vs S/4HANA Disambiguation** -- the pain point driving the project, applied as annotations
4. **Master Data Structures** -- needed to make T-code reference meaningful

**Phase 2 -- Process Knowledge:**
5. **Business Process Maps (P2P, O2C, R2R)** -- ties T-codes into actionable flows
6. **Movement Type Reference with FI Impact** -- backbone of MM operations
7. **Document Flow Explanations** -- answers "what happened when I posted X?"

**Phase 3 -- Configuration Depth:**
8. **SPRO/IMG Configuration Paths** -- high complexity, needs foundation content first
9. **Module Integration Points** -- requires process maps as context
10. **Account Determination Walkthroughs (OBYC, VKOA)** -- requires config paths and integration points
11. **Configuration Dependency Maps** -- requires SPRO paths to exist

**Phase 4 -- Solutioning Intelligence:**
12. **Decision Trees for Solution Design** -- requires all prior content as building blocks
13. **Cross-Module Scenario Playbooks** -- highest complexity, highest differentiation
14. **Pricing Procedure Logic (SD)** -- deep SD-specific content
15. **Period-End Close Checklists** -- operational content, can be built in parallel
16. **Common Error Messages with Resolutions** -- can be built incrementally as other content matures

**Defer:** Error messages and period-end checklists can be added incrementally at any phase since they have no strict dependencies.

## Rationale for Ordering

The ordering follows two principles:

1. **Dependency chain:** You cannot explain a business process without T-codes, you cannot explain integration without processes, you cannot explain solution design without integration. Build bottom-up.

2. **Value gradient:** Each phase delivers usable value on its own. Phase 1 alone makes Claude a better SAP reference tool. Phase 2 makes it a process guide. Phase 3 makes it a config assistant. Phase 4 makes it a solutioning partner.

## Sources

- [SAP T-Code List by Module - Pathlock](https://pathlock.com/blog/sap-t-code-list/)
- [SAP ECC 6 Business Transactions - Roland Blog](https://rolandblogsite.wordpress.com/2016/10/20/sap-ecc-6-business-transactions/)
- [Integration Point of MM-FI-SD in SAP ERP - SAP Community](https://blogs.sap.com/2013/12/31/integration-point-of-mm-fi-sd-in-sap-erp/)
- [FI-SD Integration VKOA Understanding Flow - SAP Community](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/fi-sd-integration-vkoa-understanding-flow-sap-ecc/ba-p/13488492)
- [SAP Complete SPRO Configuration Template - erpdb.info](https://www.erpdb.info/sap-complete-spro-configuration-manual/)
- [Key Differences Between SAP ECC and S/4HANA - SAP Press](https://blog.sap-press.com/key-differences-between-sap-ecc-and-sap-s4hana-a-detailed-comparison)
- [SAP ECC vs S/4HANA Complete Guide - Pathlock](https://pathlock.com/blog/sap-ecc-vs-sap-s4hana/)
- [Step-by-Step Procure to Pay Process - SAP Community](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/step-by-step-to-run-a-simple-procure-to-pay-process/ba-p/13448109)
- [Step-by-Step Order to Cash Process - SAP Community](https://blogs.sap.com/2020/03/02/step-by-step-to-run-a-simple-order-to-cash-process/)
- [SAP MM-FI Integration Notes - ERP Documents](https://erp-docs.com/2923/sap-mm-fi-integration-notes/)
- [SAP Joule for Consultants - SAP](https://www.sap.com/products/artificial-intelligence/ai-assistant/sap-consulting-capability.html)
- [SAP MM Enterprise Structure - TutorialsPoint](https://www.tutorialspoint.com/sap_mm/sap_mm_enterprise_structure.htm)
- [SAP FI Configuration List - SAP Online Tutorials](https://www.saponlinetutorials.com/sap-fi-configuration-sap-menu-path-sap-fi-navigations/)
- [P2P Process in SAP MM Visual Walkthrough - GTR Academy](https://gtracademy.org/procure-to-pay-process-in-sap-mm/)
- [SAP MM End-to-End P2P T-Codes - PortSAP](https://portsapblogging.com/2024/03/22/sap-mm-end-to-end-purchase-to-pay-p2p-with-the-t-codes-you-actually-use/)
