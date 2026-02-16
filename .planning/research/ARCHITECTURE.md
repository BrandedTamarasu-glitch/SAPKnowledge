# Architecture Patterns

**Domain:** SAP ECC 6.0 Curated Knowledge Base for Claude Code
**Researched:** 2026-02-16

## Recommended Architecture

A flat-file markdown knowledge base organized into module directories, loaded into Claude Code via the `.claude/rules/` auto-loading mechanism and `@import` references. The architecture exploits Claude Code's hierarchical memory system to deliver module-specific SAP knowledge on demand without overwhelming the context window.

### Design Principle: Selective Loading Over Monolith

Claude Code's context window is finite. Loading all SAP knowledge for all modules at once is wasteful when a user asks about one procurement process. The architecture splits content so that:

1. **Always-loaded content** (CLAUDE.md + rules/) provides the index, cross-reference map, and lookup instructions
2. **On-demand content** (module directories) gets pulled in when Claude reads files in those subtrees
3. **Deep-reference content** (@import from within files) chains detail when needed

### File/Folder Hierarchy

```
SAPKnowledge/
├── CLAUDE.md                          # Root: project purpose, how to use this KB, module index
├── .claude/
│   ├── CLAUDE.md                      # Claude Code instructions: "when asked about SAP, read from modules/"
│   └── rules/
│       ├── sap-general.md             # Always loaded: ECC 6 vs S/4 disambiguation rules
│       ├── org-structure.md           # Always loaded: org unit hierarchy reference
│       └── integration-map.md         # Always loaded: cross-module integration point index
│
├── modules/
│   ├── CLAUDE.md                      # Module-level: index of all modules, when to use each
│   │
│   ├── mm/                            # Materials Management
│   │   ├── CLAUDE.md                  # MM overview, sub-file index, key concepts
│   │   ├── tcodes.md                  # T-code reference (ME21N, ME51N, MIGO, etc.)
│   │   ├── config-spro.md            # SPRO/IMG paths for MM configuration
│   │   ├── processes.md              # Procure-to-pay process flow with T-code mapping
│   │   ├── master-data.md            # Material master, vendor master, info records
│   │   ├── integration.md            # MM integration points (MM->FI, MM->SD, MM->CO)
│   │   └── patterns.md              # Solution design patterns for common MM scenarios
│   │
│   ├── sd/                            # Sales and Distribution
│   │   ├── CLAUDE.md                  # SD overview, sub-file index
│   │   ├── tcodes.md
│   │   ├── config-spro.md
│   │   ├── processes.md              # Order-to-cash process flow
│   │   ├── master-data.md            # Customer master, material determination, pricing
│   │   ├── integration.md            # SD->FI billing, SD->MM availability
│   │   └── patterns.md
│   │
│   ├── fi/                            # Financial Accounting
│   │   ├── CLAUDE.md
│   │   ├── tcodes.md
│   │   ├── config-spro.md
│   │   ├── processes.md              # Record-to-report, period close
│   │   ├── master-data.md            # Chart of accounts, G/L accounts, vendor/customer
│   │   ├── integration.md            # FI<->CO reconciliation, FI<->MM automatic postings
│   │   └── patterns.md
│   │
│   └── co/                            # Controlling
│       ├── CLAUDE.md
│       ├── tcodes.md
│       ├── config-spro.md
│       ├── processes.md              # Cost center accounting, internal orders, profitability
│       ├── master-data.md            # Cost centers, cost elements, profit centers
│       ├── integration.md            # CO->FI reconciliation, CO->MM cost assignment
│       └── patterns.md
│
├── cross-module/                      # Content that spans multiple modules
│   ├── CLAUDE.md                      # Index of cross-module topics
│   ├── procure-to-pay.md            # End-to-end P2P: MM + FI + CO touchpoints
│   ├── order-to-cash.md             # End-to-end O2C: SD + FI + CO touchpoints
│   ├── record-to-report.md          # End-to-end R2R: FI + CO
│   ├── automatic-postings.md        # OBYC/account determination across modules
│   └── org-structure-design.md      # How org units relate across all modules
│
└── reference/                         # Lookup tables and quick-reference
    ├── CLAUDE.md
    ├── movement-types.md             # Goods movement types (101, 201, 301, etc.)
    ├── document-types.md             # FI document types, MM document types
    ├── posting-keys.md               # Debit/credit posting keys
    └── ecc6-vs-s4.md                # Comprehensive ECC 6 vs S/4HANA differences
```

### Component Boundaries

| Component | Responsibility | Always Loaded? | Communicates With |
|-----------|---------------|----------------|-------------------|
| `.claude/rules/sap-general.md` | ECC 6 identity, version disambiguation | Yes (auto-loaded) | All module files |
| `.claude/rules/org-structure.md` | Org unit hierarchy quick-reference | Yes (auto-loaded) | All module config files |
| `.claude/rules/integration-map.md` | Master index of all cross-module integration points | Yes (auto-loaded) | All module integration.md files |
| `modules/{module}/CLAUDE.md` | Module overview and file index | On-demand (when subtree entered) | All files within that module |
| `modules/{module}/tcodes.md` | Transaction code reference for one module | On-demand | processes.md, config-spro.md |
| `modules/{module}/config-spro.md` | SPRO/IMG configuration paths | On-demand | org-structure.md, master-data.md |
| `modules/{module}/processes.md` | Business process flows with T-code mapping | On-demand | tcodes.md, integration.md |
| `modules/{module}/integration.md` | How this module connects to others | On-demand | Other modules' integration.md, cross-module/ |
| `modules/{module}/patterns.md` | Solution design patterns | On-demand | All files in module |
| `cross-module/` | End-to-end process documentation spanning modules | On-demand | All module files |
| `reference/` | Lookup tables (movement types, doc types, posting keys) | On-demand | All module files |

### Data Flow: How Content Gets Loaded Into Claude

```
User asks: "How do I configure automatic account determination for goods receipt in MM?"

1. ALWAYS IN CONTEXT (loaded at session start):
   .claude/rules/sap-general.md    --> "This is ECC 6, not S/4HANA"
   .claude/rules/integration-map.md --> "MM->FI auto postings: see OBYC, modules/mm/integration.md"
   .claude/rules/org-structure.md   --> "Valuation area = plant level in ECC 6"

2. CLAUDE READS (on-demand, Claude navigates to relevant files):
   modules/mm/CLAUDE.md            --> MM overview, directs to config-spro.md and integration.md
   modules/mm/config-spro.md       --> SPRO path: MM > Valuation > Account Determination
   modules/mm/integration.md       --> OBYC details, valuation class -> G/L mapping
   cross-module/automatic-postings.md --> Full account determination walkthrough

3. REFERENCE LOOKUP (if needed):
   reference/movement-types.md     --> Movement type 101 = GR to warehouse
```

**Key insight:** Claude Code loads CLAUDE.md files in child directories when it reads files in those subtrees. This means placing a CLAUDE.md in each module directory acts as a local index -- Claude gets the module overview automatically when it opens any file in that module.

### How @import References Work Across Modules

Within any file, use `@path/to/file` to reference related content. Claude Code resolves these relative to the containing file, up to 5 levels deep.

**Example in `modules/mm/integration.md`:**
```markdown
## MM -> FI Automatic Account Determination

The key transaction is OBYC. For the full account determination logic across all modules,
see @../../cross-module/automatic-postings.md

Valuation class configuration is in @config-spro.md under "Valuation and Account Assignment."

For the org structure context (valuation area = plant in ECC 6), see
@../../.claude/rules/org-structure.md
```

**Cross-reference strategy:**
- Module-internal references: relative paths (`@tcodes.md`, `@config-spro.md`)
- Cross-module references: relative paths up (`@../../cross-module/procure-to-pay.md`)
- Always-available references: absolute from project root or relative up to `.claude/rules/`

### Content File Internal Structure (Standard Template)

Every content file follows a consistent structure so Claude can parse predictably:

```markdown
# [Module] - [Topic]

> ECC 6.0 specific. For S/4HANA differences, see @../../reference/ecc6-vs-s4.md

## Quick Reference
[Table or bullet list for fast lookups]

## Detail
[Expanded explanations, SPRO paths, process steps]

## Integration Points
[How this topic connects to other modules -- with @import links]

## Common Scenarios
[FAQ-style: "When you need to X, do Y"]
```

## Patterns to Follow

### Pattern 1: Module-Local CLAUDE.md as Router

**What:** Each module directory gets a CLAUDE.md that acts as a table of contents and routing guide.
**When:** Always -- this is the primary navigation mechanism.
**Why:** Claude Code auto-loads CLAUDE.md when entering a subtree, giving Claude immediate orientation.

```markdown
# SAP MM - Materials Management

## When to Use This Module
- Procurement of goods and services
- Inventory management and goods movements
- Invoice verification

## File Index
| File | Contains | Use When |
|------|----------|----------|
| @tcodes.md | Transaction codes | Looking up a T-code or finding the right transaction |
| @config-spro.md | SPRO/IMG paths | Configuring MM settings |
| @processes.md | Process flows | Understanding procure-to-pay or inventory processes |
| @master-data.md | Master data objects | Working with material masters, vendor masters |
| @integration.md | Cross-module links | Understanding MM postings to FI, CO |
| @patterns.md | Design patterns | Solving common business requirements |

## Key Concepts
- Valuation area = Plant (ECC 6 default)
- Purchasing organization can be cross-company-code
- Movement types drive automatic account determination
```

### Pattern 2: T-Code Tables with Context

**What:** T-code files use structured tables with description, menu path, usage context, and related T-codes.
**When:** Every module's tcodes.md.
**Why:** Bare T-code lists are useless. Context makes them actionable.

```markdown
## Procurement T-Codes

| T-Code | Description | Menu Path | When to Use | Related |
|--------|-------------|-----------|-------------|---------|
| ME21N | Create Purchase Order | Logistics > MM > Purchasing > PO > Create | Standard PO creation | ME22N (change), ME23N (display) |
| ME51N | Create Purchase Requisition | Logistics > MM > Purchasing > PR > Create | Internal procurement request | ME52N, ME53N |
| MIGO | Goods Movement | Logistics > MM > Inventory Mgmt > Goods Movement | GR, GI, transfers | MB51 (doc list) |
```

### Pattern 3: SPRO Paths as Navigable Trees

**What:** Configuration content uses indented tree notation matching the actual SPRO/IMG path.
**When:** Every module's config-spro.md.
**Why:** Users need the exact click path, not just the node name.

```markdown
## Account Determination for Goods Movement

**SPRO Path:**
> IMG > Materials Management > Valuation and Account Assignment
>   > Account Determination
>     > Account Determination Without Wizard
>       > Configure Automatic Postings (OBYC)

**What it controls:** Maps movement type + valuation class to G/L accounts
**Key settings:**
- Transaction key BSX = inventory posting
- Transaction key WRX = GR/IR clearing
- Valuation class from material master (Accounting view)

**Prerequisites:** Chart of accounts assigned to company code, valuation area = plant
**Integration:** Posts to FI automatically. See @integration.md
```

### Pattern 4: Integration Points as Bidirectional Maps

**What:** Integration files document both directions of every cross-module touchpoint.
**When:** Every module's integration.md and the master integration-map.md in rules/.
**Why:** "MM posts to FI" is incomplete without knowing what triggers it, what determines the account, and how to troubleshoot.

```markdown
## MM -> FI: Goods Receipt Posting

**Trigger:** MIGO goods receipt (movement type 101)
**What posts:** Inventory account (debit) + GR/IR clearing (credit)
**Account determination:** OBYC transaction keys BSX + WRX
**Determined by:** Valuation class (material master) + chart of accounts
**FI document type:** WE (goods receipt)
**Troubleshooting:** If posting fails, check OBYC config for the valuation class + chart of accounts combination

**Reverse direction (FI perspective):**
See @../../modules/fi/integration.md for how FI views these automatic postings
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Monolithic Module Files

**What:** Putting all MM content in a single 2000-line `mm.md` file.
**Why bad:** Wastes context window. When Claude needs one T-code, it loads everything about MM. Claude Code truncates lines over 2000 characters and the file becomes unwieldy.
**Instead:** Split by concern (tcodes, config, processes, integration, patterns). Each file stays under 500 lines ideally, 800 max.

### Anti-Pattern 2: Generic SAP Content Without ECC 6 Specificity

**What:** Writing "you can configure account determination in SAP" without specifying ECC 6 behavior.
**Why bad:** This is exactly the problem the KB exists to solve. Claude already knows generic SAP. It needs ECC 6-specific paths, behaviors, and gotchas.
**Instead:** Every statement should be ECC 6-verified. Where S/4HANA differs, call it out explicitly.

### Anti-Pattern 3: Loading Everything Into .claude/rules/

**What:** Putting all SAP content files into `.claude/rules/` so they auto-load every session.
**Why bad:** `.claude/rules/` content loads into context at session start, every session. 4 modules x 7 files = 28 files always consuming context window, even when the user asks about something unrelated to SAP.
**Instead:** Only put the index/routing/disambiguation content in rules/. Put substantive content in module directories for on-demand loading.

### Anti-Pattern 4: Orphaned Cross-References

**What:** Mentioning "see the FI integration" without an @import link.
**Why bad:** Claude cannot reliably navigate without explicit paths. Vague references create dead ends.
**Instead:** Always use `@relative/path/to/file.md` for cross-references. Claude Code resolves these and can follow them.

## Cross-Referencing Strategy

### Three Tiers of Reference

**Tier 1 -- Always Available (rules/):**
The integration-map.md in `.claude/rules/` is the master cross-reference index. It lists every integration point with the file path to detailed documentation. This is always in context so Claude can route any cross-module question.

```markdown
# SAP ECC 6 Integration Map

## MM <-> FI
| Touchpoint | Trigger | MM File | FI File |
|------------|---------|---------|---------|
| Goods receipt posting | MIGO (mvt 101) | @../modules/mm/integration.md | @../modules/fi/integration.md |
| Invoice verification | MIRO | @../modules/mm/integration.md | @../modules/fi/integration.md |
| Automatic account determination | OBYC | @../modules/mm/config-spro.md | @../modules/fi/config-spro.md |

## SD <-> FI
| Touchpoint | Trigger | SD File | FI File |
|------------|---------|---------|---------|
| Billing document posting | VF01 | @../modules/sd/integration.md | @../modules/fi/integration.md |
| Revenue account determination | VKOA | @../modules/sd/config-spro.md | @../modules/fi/config-spro.md |
```

**Tier 2 -- Module-Level Integration Files:**
Each module's `integration.md` documents outbound and inbound integration points from that module's perspective, with @import links to the other module's files.

**Tier 3 -- End-to-End Process Files:**
`cross-module/` directory contains full process walkthroughs (P2P, O2C, R2R) that stitch together content from multiple modules into a narrative flow.

### Reference Resolution Order

When Claude encounters a cross-module question:
1. Check `integration-map.md` (always in context) for routing
2. Open the relevant module's `integration.md` for detail
3. If end-to-end process context needed, open `cross-module/{process}.md`
4. For lookup values, open `reference/{topic}.md`

## Suggested Build Order

The build order follows SAP's own dependency chain: FI is the backbone that everything posts to, org structure must exist before module config, and cross-module content requires individual modules to exist first.

### Phase 1: Foundation (Build First)

**Why first:** Everything else depends on these. Org structure defines the entity hierarchy that every module's config references. FI is the universal integration target.

1. `.claude/rules/sap-general.md` -- ECC 6 identity and disambiguation rules
2. `.claude/rules/org-structure.md` -- Company code, plant, sales org, purchasing org, controlling area hierarchy
3. `modules/fi/` -- FI is the integration backbone; MM, SD, and CO all post to FI
4. `reference/ecc6-vs-s4.md` -- Disambiguation reference needed from day one

**Dependency rationale:** You cannot document MM->FI postings without having the FI side documented. You cannot document SPRO config without the org structure reference.

### Phase 2: Core Logistics

**Why second:** MM and SD are the highest-usage modules and have the richest integration with FI.

5. `modules/mm/` -- Procurement and inventory; heavy FI integration via OBYC
6. `modules/sd/` -- Sales and billing; heavy FI integration via VKOA
7. `.claude/rules/integration-map.md` -- Can now be populated with MM<->FI and SD<->FI touchpoints
8. `reference/movement-types.md`, `reference/document-types.md`, `reference/posting-keys.md`

**Dependency rationale:** MM and SD integration files reference FI content (built in Phase 1). The integration map needs at least two modules documented to be useful.

### Phase 3: Controlling and Cross-Module

**Why third:** CO depends on FI (cost element = G/L account in ECC 6) and on MM/SD for cost flows. Cross-module content requires all four modules.

9. `modules/co/` -- Controlling; depends on FI for cost elements, MM for cost assignment
10. `cross-module/procure-to-pay.md` -- Requires MM + FI
11. `cross-module/order-to-cash.md` -- Requires SD + FI
12. `cross-module/record-to-report.md` -- Requires FI + CO
13. `cross-module/automatic-postings.md` -- Requires MM + SD + FI
14. Update `integration-map.md` with CO integration points

### Phase 4: Polish and Validation

15. `cross-module/org-structure-design.md` -- Design guidance pulling from all modules
16. Root `CLAUDE.md` and all module `CLAUDE.md` files -- Finalize routing/index content
17. Validation pass: verify every @import resolves, every T-code is ECC 6 correct, every SPRO path is accurate

## Scalability Considerations

| Concern | 4 Modules (v1) | 8 Modules (v2: +PP, PM, QM, WM) | 12+ Modules |
|---------|-----------------|-----------------------------------|-------------|
| rules/ size | ~3 files, <150 lines total | ~3 files, ~250 lines | Split integration-map.md into integration-map-logistics.md, integration-map-finance.md |
| Navigation | Module CLAUDE.md sufficient | Add `modules/CLAUDE.md` module selector | Consider categorized subdirs: `modules/logistics/mm/` |
| Cross-module files | 5 files manageable | ~10 files, add process index | Process catalog with @import chains |
| Context usage | Comfortable | Monitor rules/ total size | May need path-scoped rules via YAML frontmatter |

## Context Window Budget Estimate

| Content Tier | Estimated Size | Loading Behavior |
|-------------|---------------|------------------|
| `.claude/rules/` (3 files) | ~3,000-5,000 tokens | Always loaded |
| Module CLAUDE.md (entered module) | ~500-800 tokens | On-demand per module |
| Individual content file | ~1,500-3,000 tokens per file | On-demand when read |
| Typical query loads | ~8,000-15,000 tokens total | 2-4 files per question |

**Target:** Keep always-loaded content under 5,000 tokens. Keep individual files under 3,000 tokens. A typical SAP question should require loading 2-4 on-demand files, consuming roughly 10,000-15,000 tokens of context -- well within budget for Claude Code's working context.

## Sources

- [Claude Code Memory Documentation](https://code.claude.com/docs/en/memory) -- Official docs on CLAUDE.md hierarchy, .claude/rules/, @import syntax, loading behavior (HIGH confidence)
- [Builder.io - How to Write a Good CLAUDE.md File](https://www.builder.io/blog/claude-md-guide) -- Best practices for CLAUDE.md organization (MEDIUM confidence)
- [Anthropic Blog - Using CLAUDE.md Files](https://claude.com/blog/using-claude-md-files) -- Official guidance on CLAUDE.md usage patterns (HIGH confidence)
- [SAP Community - Integration Point of MM-FI-SD](https://blogs.sap.com/2013/12/31/integration-point-of-mm-fi-sd-in-sap-erp/) -- Cross-module integration points (MEDIUM confidence)
- [TutorialsPoint - SAP MM Enterprise Structure](https://www.tutorialspoint.com/sap_mm/sap_mm_enterprise_structure.md) -- Org structure hierarchy (MEDIUM confidence)
- [ERPROOTS - SAP Organizational Structure](https://erproots.com/sap-organizational-structure/) -- Org unit relationships and assignments (MEDIUM confidence)
