# Technology Stack

**Project:** SAP ECC 6 Knowledge Base
**Researched:** 2026-02-16

## Executive Summary

This is not a traditional software project -- there is no runtime, no framework, no build step. The "stack" is a file organization system, markdown conventions, and content structure patterns optimized for Claude Code context loading. The technology decisions are about **how to structure content** so an LLM can consume it efficiently and accurately.

The core constraint: flat markdown files loaded into Claude Code's context window. No MCP server, no database, no ABAP. Every decision below serves one goal: **maximize the accuracy and usefulness of SAP ECC 6 reference content within Claude Code's context limits.**

---

## Recommended Stack

### Content Format

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Markdown (CommonMark) | N/A | All content files | LLMs parse markdown natively with high accuracy. Markdown is token-efficient -- 20-30% fewer tokens than HTML for equivalent content. Claude Code reads `.md` files without any conversion step. |
| YAML frontmatter | N/A | File metadata | Enables consistent metadata (module, last-verified, ECC-version, confidence) at the top of every file. Claude can parse YAML headers to understand file scope without reading the full document. |
| Git | 2.x | Version control, change tracking | Content accuracy is critical. Git provides diff history, blame for who verified what, and branch workflows for content review before merge. |

### Content Delivery Mechanism

| Technology | Purpose | Why |
|------------|---------|-----|
| Claude Code `@import` syntax | Load reference files into context | CLAUDE.md supports `@path/to/file` imports. Referenced files load into context at conversation start. Max recursion depth: 5 hops. This is the primary delivery mechanism. |
| `.claude/rules/*.md` | Module-specific rules and conventions | Rules files auto-load and support `paths:` frontmatter for conditional loading. Use for SAP module conventions that should apply when working in specific directories. |
| Directory-scoped `CLAUDE.md` | Per-module context | Child directory CLAUDE.md files load on-demand when Claude reads files in that directory. Use this for module-specific indexes. |

### Content Authoring

| Technology | Purpose | Why |
|------------|---------|-----|
| Any text editor | Writing markdown | No special tooling needed. VS Code with markdown preview is fine. |
| markdownlint | Linting consistency | Enforces heading hierarchy, consistent list formatting, no trailing spaces. LLMs parse well-structured markdown more reliably. |
| Git pre-commit hooks | Validation | Catch missing frontmatter, broken internal links, files exceeding size targets. |

### Quality Assurance

| Technology | Purpose | Why |
|------------|---------|-----|
| Shell scripts (bash/fish) | Content validation | Check frontmatter presence, file size limits, heading structure, internal link integrity. No heavy tooling needed for flat file validation. |
| `wc` / `tiktoken` | Token counting | Monitor file sizes to stay within context budget. A rough rule: 1 token per 4 characters in English text. |

---

## File Organization Pattern

**Confidence: HIGH** -- Based on Claude Code's documented loading behavior and LLM content consumption best practices.

### Directory Structure

```
SAP-Knowledge/
├── CLAUDE.md                          # Master index -- @imports by module
├── .claude/
│   └── rules/
│       ├── sap-terminology.md         # SAP naming conventions for all content
│       └── disambiguation.md          # ECC 6 vs S/4HANA rules
├── modules/
│   ├── MM/
│   │   ├── CLAUDE.md                  # MM module index (on-demand load)
│   │   ├── overview.md                # MM module summary, org structure
│   │   ├── tcodes.md                  # MM transaction codes reference
│   │   ├── spro-paths.md             # MM SPRO/IMG config paths
│   │   ├── processes/
│   │   │   ├── procurement.md         # Procure-to-pay process
│   │   │   ├── inventory.md           # Inventory management
│   │   │   └── invoice-verification.md
│   │   └── integration/
│   │       ├── mm-fi.md               # MM-FI integration points
│   │       └── mm-sd.md               # MM-SD integration points
│   ├── SD/
│   │   ├── CLAUDE.md
│   │   ├── overview.md
│   │   ├── tcodes.md
│   │   ├── spro-paths.md
│   │   ├── processes/
│   │   │   ├── order-to-cash.md
│   │   │   ├── pricing.md
│   │   │   └── shipping.md
│   │   └── integration/
│   │       ├── sd-fi.md
│   │       └── sd-mm.md
│   ├── FI/
│   │   ├── CLAUDE.md
│   │   ├── overview.md
│   │   ├── tcodes.md
│   │   ├── spro-paths.md
│   │   ├── processes/
│   │   │   ├── gl-accounting.md
│   │   │   ├── accounts-payable.md
│   │   │   ├── accounts-receivable.md
│   │   │   └── asset-accounting.md
│   │   └── integration/
│   │       ├── fi-co.md
│   │       ├── fi-mm.md
│   │       └── fi-sd.md
│   └── CO/
│       ├── CLAUDE.md
│       ├── overview.md
│       ├── tcodes.md
│       ├── spro-paths.md
│       ├── processes/
│       │   ├── cost-center-accounting.md
│       │   ├── internal-orders.md
│       │   ├── profitability-analysis.md
│       │   └── product-costing.md
│       └── integration/
│           └── co-fi.md
├── cross-module/
│   ├── org-structure.md               # Company code, plant, sales org relationships
│   ├── number-ranges.md               # Number range concepts across modules
│   ├── master-data.md                 # Material master, customer master, vendor master
│   └── document-flow.md              # End-to-end document flow across modules
├── reference/
│   ├── glossary.md                    # SAP terminology definitions
│   ├── ecc-vs-s4hana.md             # Disambiguation: what changed in S/4HANA
│   └── common-tables.md             # Key database tables by module
└── scripts/
    ├── validate-content.sh            # Check frontmatter, sizes, links
    └── count-tokens.sh                # Estimate token usage per file
```

### Why This Structure

1. **Module-first organization** matches how SAP practitioners think. When someone asks about procurement, they think "MM module" not "process category."

2. **On-demand loading via child CLAUDE.md files.** Claude Code loads child directory CLAUDE.md files only when it accesses files in that directory. This means the MM index loads only when MM content is relevant -- saving context budget.

3. **Integration as a first-class directory.** SAP's complexity lives at module boundaries. Dedicated integration files (mm-fi.md, sd-fi.md) prevent integration knowledge from being scattered across module files.

4. **Cross-module directory for shared concepts.** Org structure, master data, and document flow span all modules. Duplicating this in each module wastes tokens and creates consistency risks.

5. **Processes subdirectory** maps to real SAP business processes (procure-to-pay, order-to-cash), which is how users actually ask questions.

---

## Markdown Structure Conventions

**Confidence: HIGH** -- Based on LLM content parsing research and Claude Code behavior.

### File Template

Every content file must follow this structure:

```markdown
---
module: MM
area: procurement
ecc_version: "6.0"
last_verified: 2026-02-16
confidence: HIGH
related:
  - modules/FI/integration/fi-mm.md
  - modules/SD/integration/sd-mm.md
---

# Procurement Process (MM)

> One-sentence summary of what this file covers and when to reference it.

## Overview

[2-3 paragraphs of context. What is this, why does it matter, how does it fit.]

## Key Transaction Codes

| T-Code | Name | Purpose | Menu Path |
|--------|------|---------|-----------|
| ME21N | Create Purchase Order | Create PO with reference to PR, contract, or manually | Logistics > MM > Purchasing > Purchase Order > Create |
| ME51N | Create Purchase Requisition | Internal request for procurement | Logistics > MM > Purchasing > Purchase Requisition > Create |

## SPRO Configuration Paths

| Setting | SPRO Path | Purpose |
|---------|-----------|---------|
| Document Types | SPRO > MM > Purchasing > Purchase Order > Define Document Types | Define PO document types (NB, FO, etc.) |

## Process Flow

1. **Purchase Requisition** (ME51N) -- internal request
2. **Request for Quotation** (ME41) -- optional, for competitive bidding
3. **Purchase Order** (ME21N) -- commitment to vendor
4. **Goods Receipt** (MIGO) -- physical receipt of materials
5. **Invoice Verification** (MIRO) -- match invoice to PO and GR

## Integration Points

- **FI:** GR creates FI posting (inventory account debit, GR/IR clearing credit)
- **CO:** PO line items can carry cost center or internal order assignments
- **SD:** Intercompany procurement triggers SD billing

## ECC 6 vs S/4HANA

| Aspect | ECC 6.0 | S/4HANA |
|--------|---------|---------|
| PO Interface | ME21N (SAP GUI) | Fiori app "Create Purchase Order" |
| Material Ledger | Optional | Mandatory |
| MRP | MD01/MD02 | Simplified via MRP Live |

## Common Issues

- [Practical notes about common misconfigurations or gotchas]
```

### Why These Conventions

| Convention | Rationale |
|------------|-----------|
| **YAML frontmatter** | Lets scripts validate content; lets Claude understand file scope from the first few lines without reading the full document |
| **One-sentence summary after H1** | Claude can determine relevance from the first ~50 tokens, deciding whether to read further |
| **Tables for T-codes and SPRO paths** | Tables are extremely token-efficient for structured reference data. LLMs parse markdown tables with high accuracy. |
| **Numbered lists for process flows** | Sequence matters in SAP processes. Numbered lists encode order explicitly. |
| **ECC vs S/4HANA section** | Disambiguation is a stated project requirement. Consistent placement means Claude always knows where to find it. |
| **Related files in frontmatter** | Enables Claude to follow cross-references without searching the filesystem |

### Heading Hierarchy Rules

- `#` H1: One per file, the file's topic
- `##` H2: Major sections (Overview, T-Codes, SPRO Paths, Process Flow, Integration, ECC vs S/4HANA)
- `###` H3: Sub-sections within a major section
- Never skip levels (no H1 to H3). LLMs use heading hierarchy to understand content scope.

### Content Writing Rules

- **Sentences under 20 words.** Shorter sentences reduce LLM misinterpretation.
- **Active voice.** "The system posts a document" not "A document is posted by the system."
- **No ambiguous pronouns.** "The purchase order" not "it" when the antecedent is unclear.
- **SAP terms in bold on first use** with a brief definition. After that, use the term normally.
- **T-codes always in code formatting.** Write `ME21N` not ME21N. Consistent formatting helps LLM recognition.
- **SPRO paths use `>` separator.** Write `SPRO > MM > Purchasing > Purchase Order` for consistent parsing.

---

## Context Window Budget

**Confidence: MEDIUM** -- Based on Claude Code context window behavior and progressive loading patterns. Exact token limits may shift with model updates.

### File Size Targets

| File Type | Target Size | Max Size | Rationale |
|-----------|-------------|----------|-----------|
| Module overview | 800-1200 tokens (~3-5 KB) | 2000 tokens | Loaded frequently; must be concise |
| T-code reference | 1000-2000 tokens (~4-8 KB) | 3000 tokens | Dense tables are token-efficient |
| SPRO paths | 800-1500 tokens (~3-6 KB) | 2500 tokens | Reference tables, scan-friendly |
| Process file | 1500-2500 tokens (~6-10 KB) | 4000 tokens | Needs narrative + tables + integration |
| Integration file | 500-1000 tokens (~2-4 KB) | 1500 tokens | Focused on boundaries, should be tight |
| Cross-module file | 1000-2000 tokens (~4-8 KB) | 3000 tokens | Shared reference, moderate depth |
| Glossary | 1500-2500 tokens (~6-10 KB) | 4000 tokens | Many short definitions, acceptable larger |

### Loading Strategy

```
Root CLAUDE.md (@imports):
  - Cross-module essentials only (~2000 tokens)
  - @cross-module/org-structure.md
  - @reference/glossary.md (or subset)
  - Module indexes listed but NOT @imported (load on demand)

Per-module CLAUDE.md (on-demand):
  - Module overview + key T-codes summary (~1500 tokens)
  - @imports for the most critical process file
  - Other files listed as "read when needed"
```

**Total startup budget:** ~3500-5000 tokens for root context. Additional module context loads on demand at ~2000-4000 tokens per module accessed.

**Why not load everything at once:** A full knowledge base across 4 modules with all process, integration, and reference files could easily reach 40,000-60,000 tokens. Loading everything at startup wastes context on modules irrelevant to the current question and triggers the "lost in the middle" problem where LLMs lose accuracy on content buried in large context windows.

---

## What NOT To Do

### Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|--------------|--------------|-----------------|
| **One giant file per module** | Files over 5000 tokens trigger lost-in-the-middle. Claude loses accuracy on content in the middle of large documents. | Split by concern: overview, t-codes, SPRO, processes, integration |
| **Deep nesting (4+ directory levels)** | Claude Code's file discovery gets noisy. Users struggle to find content. | Max 3 levels: `modules/MM/processes/procurement.md` |
| **HTML in markdown** | HTML wastes tokens on tags. LLMs parse markdown natively but must work harder with HTML. | Pure CommonMark markdown only. No `<div>`, no `<table>`. |
| **Duplicate content across files** | Creates consistency nightmares. When T-code `MIGO` behavior is described in 3 files, updates get missed. | Single source of truth per concept. Cross-reference via relative links and frontmatter `related:` field. |
| **Generic headers** ("Overview", "Details") | LLMs use headers for semantic understanding. "Overview" says nothing about content. | Descriptive headers: "Procurement Process Flow", "MM-FI Integration Points" |
| **Embedding images or diagrams** | Claude Code reads text, not images in markdown files. Token budget wasted on base64-encoded images that provide no value. | Describe diagrams as structured text, tables, or ASCII. |
| **@importing all files from root CLAUDE.md** | Blows the context budget on startup. Every imported file loads immediately and fully. | Import only cross-module essentials. Let module CLAUDE.md files handle module-specific imports. |
| **Storing raw SAP help text** | SAP documentation is verbose, repetitive, and written for a different context. LLMs perform worse on copied reference text than on curated summaries. | Curate and rewrite. Extract the actionable knowledge, discard the boilerplate. |
| **Version-ambiguous content** | If a file doesn't state whether it describes ECC 6 or S/4HANA, Claude will guess -- and may guess wrong. | Every file has `ecc_version` in frontmatter. Every file has an "ECC 6 vs S/4HANA" section where differences exist. |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Content format | Markdown | JSON/YAML data files | JSON is more structured but far more token-expensive. Markdown gives structure via headings/tables while remaining token-efficient. |
| Content format | Markdown | AsciiDoc | AsciiDoc has richer semantics but LLMs are trained predominantly on markdown. Sticking with markdown ensures the best parsing accuracy. |
| Delivery mechanism | `@import` + on-demand CLAUDE.md | MCP server | Project constraint: no MCP server. Even if allowed, flat files are simpler to maintain and version. |
| Delivery mechanism | `@import` + on-demand CLAUDE.md | RAG with vector DB | Overkill for a curated knowledge base. RAG adds infrastructure complexity. For ~50-80 curated files, direct loading is simpler and more reliable. |
| Validation | Shell scripts | Custom Node.js linter | Shell scripts (`wc`, `grep`, frontmatter checks) handle all validation needs. No build toolchain to maintain. |
| Organization | Module-first directories | Process-first directories | SAP practitioners think in modules. Process-first (e.g., "procure-to-pay/") would scatter MM, FI, and SD content across a single process directory, making per-module reference harder. |
| T-code format | Tables in markdown | Separate structured data files | Tables are scannable and token-efficient. Separate data files would need a loading/formatting step. |

---

## Tooling Setup

### Repository Initialization

```bash
# Initialize the knowledge base
mkdir -p modules/{MM,SD,FI,CO}/{processes,integration}
mkdir -p cross-module reference scripts .claude/rules

# Create root CLAUDE.md
touch CLAUDE.md

# Create module indexes
for mod in MM SD FI CO; do
  touch "modules/$mod/CLAUDE.md"
  touch "modules/$mod/overview.md"
  touch "modules/$mod/tcodes.md"
  touch "modules/$mod/spro-paths.md"
done

# Create cross-module files
touch cross-module/{org-structure,number-ranges,master-data,document-flow}.md
touch reference/{glossary,ecc-vs-s4hana,common-tables}.md
```

### Validation Script (scripts/validate-content.sh)

```bash
#!/usr/bin/env bash
# Validate all markdown content files
# Checks: frontmatter presence, file size, heading structure

errors=0

for file in $(find modules cross-module reference -name "*.md" -not -name "CLAUDE.md"); do
  # Check frontmatter
  if ! head -1 "$file" | grep -q "^---$"; then
    echo "MISSING FRONTMATTER: $file"
    errors=$((errors + 1))
  fi

  # Check file size (warn over 10KB, error over 15KB)
  size=$(wc -c < "$file")
  if [ "$size" -gt 15000 ]; then
    echo "TOO LARGE (${size}B): $file -- split this file"
    errors=$((errors + 1))
  elif [ "$size" -gt 10000 ]; then
    echo "WARNING large (${size}B): $file -- consider splitting"
  fi

  # Check for H1
  if ! grep -q "^# " "$file"; then
    echo "MISSING H1: $file"
    errors=$((errors + 1))
  fi
done

echo "Validation complete. Errors: $errors"
exit $errors
```

### Token Counting (scripts/count-tokens.sh)

```bash
#!/usr/bin/env bash
# Rough token count: ~4 characters per token for English text
echo "File Token Estimates:"
echo "====================="
total=0
for file in $(find modules cross-module reference -name "*.md" | sort); do
  chars=$(wc -c < "$file")
  tokens=$((chars / 4))
  total=$((total + tokens))
  printf "%6d tokens  %s\n" "$tokens" "$file"
done
echo "====================="
printf "%6d tokens  TOTAL\n" "$total"
```

---

## Sources

- [Claude Code Memory Documentation](https://code.claude.com/docs/en/memory) -- Authoritative reference for CLAUDE.md loading behavior, @import syntax, .claude/rules/, on-demand loading (HIGH confidence)
- [Using CLAUDE.MD files (Anthropic blog)](https://claude.com/blog/using-claude-md-files) -- Official guidance on CLAUDE.md patterns
- [Progressive Context Loading](https://williamzujkowski.github.io/posts/from-150k-to-2k-tokens-how-progressive-context-loading-revolutionizes-llm-development-workflows/) -- Evidence for on-demand loading vs monolithic approach
- [LLM-Friendly Content in Markdown (Webex Developer Blog)](https://developer.webex.com/blog/boosting-ai-performance-the-power-of-llm-friendly-content-in-markdown) -- Markdown optimization for LLM consumption
- [Chunking Strategies (Pinecone)](https://www.pinecone.io/learn/chunking-strategies/) -- Token budgeting and chunking best practices
- [Markdown vs HTML for LLM Context](https://www.searchcans.com/blog/markdown-vs-html-llm-context-optimization-2026/) -- Token efficiency comparison
- [SAP ECC vs S/4HANA (Pathlock)](https://pathlock.com/blog/sap-ecc-vs-sap-s4hana/) -- Module-level differences for disambiguation content
- [SAP ECC vs S/4HANA (SAP Press)](https://blog.sap-press.com/key-differences-between-sap-ecc-and-sap-s4hana-a-detailed-comparison) -- Detailed comparison for ECC vs S/4HANA sections
- [SAP T-Code Reference (Pathlock)](https://pathlock.com/blog/sap-t-code-list/) -- T-code organization patterns by module
- [SAP SPRO IMG Structure](https://www.saponlinetutorials.com/menu-path-img-sap-spro-sap-project-reference-object/) -- SPRO path documentation format
