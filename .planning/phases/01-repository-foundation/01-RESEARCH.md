# Phase 1 Research: Repository Foundation

**Phase:** 01 - Repository Foundation
**Researched:** 2026-02-16
**Overall Confidence:** HIGH

## Executive Summary

Phase 1 establishes the scaffolding that all subsequent SAP content builds upon: directory structure, YAML frontmatter conventions, Claude Code loading configuration, and validation scripts. No SAP content is authored -- only the framework and quality gates.

The most architecturally significant decision is the "from any project directory" requirement. After researching Claude Code's loading mechanisms in detail, there are three viable approaches to make the SAP knowledge base accessible from any project: (1) `~/.claude/rules/` for always-loaded routing content, (2) `additionalDirectories` in `~/.claude/settings.json` for on-demand module access, and (3) `@~/path/to/file` imports from a user-level CLAUDE.md. The recommended approach combines all three for a layered loading strategy.

The validation tooling is straightforward: Python scripts using `python-frontmatter` for YAML parsing, character-based token estimation (no API dependency), and regex-based S/4HANA contamination detection. A pre-commit hook wraps the validation for automated enforcement.

---

## 1. Claude Code Loading Mechanisms (Critical Path)

**Confidence: HIGH** -- Verified against official Anthropic documentation at [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) and [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings).

### What Loads Automatically vs On-Demand

| Mechanism | Loads When | Scope | Token Cost |
|-----------|-----------|-------|------------|
| `~/.claude/CLAUDE.md` | Every session, every project | Global personal | Always paid |
| `~/.claude/rules/*.md` | Every session, every project | Global personal | Always paid |
| `.claude/rules/*.md` (project) | Every session in that project | Project-wide | Always paid |
| `.claude/CLAUDE.md` (project) | Every session in that project | Project-wide | Always paid |
| `./CLAUDE.md` (root) | Every session in that project | Project-wide | Always paid |
| Child `CLAUDE.md` files | When Claude reads files in that subtree | Directory-scoped | On-demand |
| `@path/to/file` imports | When the containing file is loaded | Chained from parent | On-demand or always, depends on parent |
| `--add-dir` directories | When explicitly configured | Session or settings | File reads on-demand |

### Key Behaviors Verified

1. **`~/.claude/rules/` auto-loads into every project** -- All `.md` files are discovered recursively. Subdirectories are supported. Symlinks work (circular ones handled gracefully). User-level rules load before project-level rules (project rules have higher priority if they conflict).

2. **`@import` syntax** -- Use `@path/to/file` anywhere in a CLAUDE.md or rules file. Relative paths resolve relative to the containing file, not the working directory. Absolute paths and `@~/path` (home directory) are supported. Max recursion depth: 5 hops. First-time imports in a project show an approval dialog.

3. **`additionalDirectories` in settings** -- Can be configured in `~/.claude/settings.json` under `permissions.additionalDirectories`. By default, CLAUDE.md files from additional directories are NOT loaded. Setting `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` enables loading CLAUDE.md + `.claude/rules/*.md` from those directories.

4. **Path-specific rules** -- Rules in `.claude/rules/` support YAML frontmatter with a `paths:` field for conditional loading. Rules without `paths:` load unconditionally. Glob patterns supported: `**/*.ts`, `src/**/*`, `*.{ts,tsx}`, brace expansion.

5. **Known limitation** -- `@file` autocomplete in the TUI does not suggest files from `--add-dir` directories ([issue #7412](https://github.com/anthropics/claude-code/issues/7412), open). Manual paths still work. This affects DX but not functionality.

### The "From Any Project" Architecture

**Problem:** The SAP knowledge base lives in its own repository (`~/Claude/SAPKnowledge/`). Users need it accessible when working in ANY project directory -- not just when `cd`'d into the knowledge base itself.

**Recommended Solution: Three-Layer Loading**

```
Layer 1: ~/.claude/rules/sap-routing.md          (always loaded, every project)
         - Compact routing index (~200-400 tokens)
         - Tells Claude: "For SAP questions, read from ~/Claude/SAPKnowledge/modules/"
         - Contains @~/Claude/SAPKnowledge/.claude/rules/sap-core.md import

Layer 2: ~/.claude/settings.json                  (configured once)
         {
           "permissions": {
             "additionalDirectories": ["~/Claude/SAPKnowledge"]
           },
           "env": {
             "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD": "1"
           }
         }
         - Gives Claude read access to the knowledge base from any project
         - Loads the KB's own .claude/rules/ and CLAUDE.md files

Layer 3: SAPKnowledge/.claude/rules/*.md          (loaded via Layer 2)
         SAPKnowledge/modules/*/CLAUDE.md          (on-demand when Claude navigates)
         - Full routing index, disambiguation rules, org structure reference
         - Module CLAUDE.md files load when Claude reads into module directories
```

**Why this approach:**
- Layer 1 is tiny (routing pointer only) -- minimal context cost on non-SAP projects
- Layer 2 makes the full KB accessible without manual `--add-dir` flags each session
- Layer 3 uses Claude Code's native on-demand loading so module content only enters context when relevant

**Alternative considered: Symlinks.** Could symlink `~/.claude/rules/sap/` to `SAPKnowledge/.claude/rules/`. This works (symlinks are supported), but means always-loaded rules content grows with the KB. The `additionalDirectories` approach is better because module CLAUDE.md files load on-demand rather than always.

**Alternative considered: Only `~/.claude/rules/` with `@~/` imports.** Could put everything in global rules with `@~/Claude/SAPKnowledge/...` imports. Problem: imports in always-loaded files are always loaded, so this pulls all referenced content into every project session. Too expensive in tokens.

---

## 2. Directory Structure Design

**Confidence: HIGH** -- Decisions locked in CONTEXT.md, consistent with ecosystem research.

### Final Structure

```
SAPKnowledge/
├── CLAUDE.md                           # Project purpose, usage instructions
├── .claude/
│   ├── CLAUDE.md                       # Claude Code behavior: how to navigate this KB
│   └── rules/
│       ├── sap-routing.md              # Routing index: query type -> file mapping
│       ├── sap-disambiguation.md       # ECC 6 vs S/4HANA quick reference
│       └── sap-org-structure.md        # Org unit hierarchy summary
│
├── modules/
│   ├── fi/
│   │   ├── CLAUDE.md                   # FI module index, file routing
│   │   ├── tcodes.md
│   │   ├── config-spro.md
│   │   ├── processes.md
│   │   ├── master-data.md
│   │   ├── integration.md
│   │   └── patterns.md
│   ├── mm/
│   │   ├── CLAUDE.md
│   │   ├── tcodes.md
│   │   ├── config-spro.md
│   │   ├── processes.md
│   │   ├── master-data.md
│   │   ├── integration.md
│   │   └── patterns.md
│   ├── sd/
│   │   └── [same structure]
│   └── co/
│       └── [same structure]
│
├── cross-module/
│   ├── CLAUDE.md                       # Cross-module topic index
│   ├── procure-to-pay.md
│   ├── order-to-cash.md
│   └── record-to-report.md
│
├── reference/
│   ├── CLAUDE.md                       # Reference lookup index
│   ├── movement-types.md
│   ├── document-types.md
│   └── posting-keys.md
│
├── scripts/
│   ├── validate.py                     # Main validation script
│   └── requirements.txt                # python-frontmatter, pyyaml
│
└── .githooks/
    └── pre-commit                      # Calls scripts/validate.py
```

### File Naming Convention (Claude's Discretion Area)

**Recommendation: Descriptive kebab-case, no numbered prefix.**

Rationale:
- `tcodes.md` is self-documenting; `01-tcodes.md` adds cognitive overhead for no LLM benefit
- Claude Code navigates by file content and CLAUDE.md indexes, not alphabetical sort order
- Kebab-case is the established convention in the markdown ecosystem
- Numbered prefixes create friction when inserting new files (renumbering)

Names: `tcodes.md`, `config-spro.md`, `processes.md`, `master-data.md`, `integration.md`, `patterns.md`

---

## 3. YAML Frontmatter Convention

**Confidence: HIGH** -- Standard markdown convention, well-supported tooling.

### Required Fields (Locked Decisions)

```yaml
---
module: mm                    # Module code: fi, mm, sd, co, cross-module, reference
content_type: tcodes          # What this file contains: tcodes, config-spro, processes, master-data, integration, patterns
ecc_version: "6.0"           # Always "6.0" for this KB
ehp_range: "0-8"             # EhP applicability (broad default)
confidence: high              # high, medium, low -- content verification level
last_verified: 2026-02-16    # Date content was last verified against SAP documentation
---
```

### Design Decisions

**`ehp_range` as string, not integer.** The context discussion established EhP 0-8 as the broad baseline. Using a string like `"0-8"` or `"6-8"` communicates range clearly. Individual features that require specific EhP levels get inline callouts, not separate frontmatter fields.

**`confidence` as enum, not percentage.** Three levels (high/medium/low) are sufficient for human/LLM consumption. A numeric confidence score implies false precision. Definitions:
- `high`: Verified against SAP Help Portal or authoritative SAP Press source
- `medium`: Sourced from multiple community references, not formally verified
- `low`: Single source or from training data, needs verification

**`last_verified` as ISO date.** Enables validation scripts to flag stale content (e.g., warn if not verified in 12+ months).

### Frontmatter for Cross-Module and Reference Files

```yaml
---
module: cross-module          # or "reference"
content_type: e2e-process     # or "lookup-table"
ecc_version: "6.0"
ehp_range: "0-8"
confidence: medium
last_verified: 2026-02-16
related_modules:              # Additional field for cross-module content
  - mm
  - fi
---
```

---

## 4. Token Budget Strategy

**Confidence: MEDIUM** -- Token counting without Anthropic's API is approximate. Character-based heuristics are within ~10-15% of actual counts.

### Budget Targets (Claude's Discretion Area)

**Recommendation: 800-3000 tokens per file, hard cap at 5000.**

Rationale from context discussion: "800-2500 suggested, up to 5000 for dense topics."

| Content Type | Target Range | Hard Cap | Notes |
|-------------|-------------|----------|-------|
| Module CLAUDE.md | 200-400 | 600 | Index only, must be lean |
| tcodes.md | 1500-3000 | 5000 | 50-80 T-codes, table format is token-dense |
| config-spro.md | 1500-3000 | 5000 | SPRO paths with step-by-step guidance |
| processes.md | 1000-2500 | 4000 | Process flows with T-code references |
| master-data.md | 1000-2500 | 4000 | Field descriptions, key relationships |
| integration.md | 800-2000 | 3000 | Cross-module touchpoints |
| patterns.md | 1000-2500 | 4000 | Scenario-based design guidance |
| .claude/rules/*.md | 200-500 | 800 | Always-loaded; every token counts |

### Token Estimation Method

**Use character count / 4 as the primary heuristic.** This is the standard approximation for English text and works within ~15% for structured markdown.

For validation scripts, implement:

```python
def estimate_tokens(text: str) -> int:
    """Estimate token count using character-based heuristic.

    Claude's tokenizer averages ~4 characters per token for English text.
    Structured markdown with tables and code blocks may be slightly higher.
    This is a conservative estimate (may overcount by ~10-15%).
    """
    return len(text) // 4
```

**Why not use Anthropic's Token Count API:** It requires an API key and network access. Validation scripts should work offline, fast, in CI, and without secrets. The heuristic is good enough for budget enforcement -- we are setting guidelines, not billing.

**Why not tiktoken:** It is OpenAI's tokenizer, not Anthropic's. Results diverge for Claude models. Using it gives false precision with inaccurate numbers. The character heuristic is more honest about its approximation.

---

## 5. Validation Script Design

**Confidence: HIGH** -- Standard Python scripting, well-established libraries.

### Technology Choice: Python

**Why Python over shell scripts:** The context discussion mentioned shell scripts, but Python is better here because:
- `python-frontmatter` library provides robust YAML extraction from markdown
- Regex-based S/4 contamination detection is cleaner in Python
- Cross-reference resolution requires path manipulation (Python's `pathlib` is excellent)
- Single script with multiple checks vs. fragile piped shell commands
- Works identically on Linux, macOS, and WSL

### Library: `python-frontmatter`

**Package:** `python-frontmatter` (PyPI)
**What it does:** Parses markdown files, extracts YAML frontmatter as a dictionary, provides the markdown body separately.
**Why this one:** Production-stable, simple API, handles edge cases (missing frontmatter, malformed YAML). The `frontmatter` package (different name) is less maintained.

Source: [python-frontmatter on PyPI](https://pypi.org/project/python-frontmatter/)

### Validation Checks

The validation script should implement five check categories with two severity levels:

#### Critical (block commit):

1. **Missing frontmatter** -- Every `.md` file in `modules/`, `cross-module/`, `reference/` must have YAML frontmatter with all required fields.
2. **Invalid frontmatter values** -- `module` must be a known value (fi, mm, sd, co, cross-module, reference). `confidence` must be high/medium/low. `ecc_version` must be "6.0". `last_verified` must be a valid date.
3. **S/4HANA contamination** -- Regex scan for known S/4-only terms in content body (not frontmatter, not code blocks).

#### Warning (allow commit, report):

4. **Token budget exceeded** -- File exceeds hard cap for its content type.
5. **Cross-reference integrity** -- `@path/to/file` references point to files that exist. Broken references reported but not blocking (files may not exist yet during phased development).

### S/4HANA Contamination Detection

From context discussion, detection should flag these terms/patterns:

```python
S4_CONTAMINATION_PATTERNS = [
    # Core S/4 concepts
    r'\bUniversal\s+Journal\b',
    r'\bACDOCA\b',
    r'\bMATDOC\b',
    r'\bBusiness\s+Partner\b(?!.*\b(CRM|IS-)\b)',  # BP in non-CRM context
    r'\bSimplified\s+Data\s+Model\b',

    # S/4-only transactions and apps
    r'\bManage\s+Purchase\s+Orders?\b',             # Fiori app name pattern
    r'\bManage\s+Sales\s+Orders?\b',
    r'\bManage\s+Journal\s+Entries\b',
    r'\bBP\s+transaction\b',                         # BP as vendor/customer maintenance

    # S/4 technical markers
    r'\bCDS\s+[Vv]iews?\b(?!.*\b(BW|HANA|optional)\b)',  # CDS as standard feature
    r'\b[Ee]mbedded\s+[Aa]nalytics\b',
    r'\bFiori\s+[Ll]aunchpad\b',

    # Obsoleted concepts
    r'\bMaterial\s+Ledger\b(?!.*\b(optional|activate)\b)', # ML is optional in ECC, mandatory in S/4
]
```

**Important nuance:** Some terms (Business Partner, CDS Views, Material Ledger) exist in ECC in limited contexts. The regex patterns above include negative lookaheads to reduce false positives. The validation should flag these as warnings requiring human review, not as automatic failures. However, per context discussion, S/4 contamination is "block on critical" -- so the most unambiguous markers (ACDOCA, MATDOC, Universal Journal, Simplified Data Model) should be hard blocks, while ambiguous ones (Business Partner, CDS Views) should be warnings.

### Script Structure

```python
#!/usr/bin/env python3
"""validate.py - SAP Knowledge Base validation script.

Usage:
    python validate.py [--strict] [path...]

    --strict: Treat warnings as errors (for CI)
    path...:  Specific files/directories to check (default: all content)

Exit codes:
    0: All checks passed
    1: Critical errors found
    2: Warnings found (only with --strict)
"""
```

### Pre-Commit Hook

Two options for the pre-commit hook:

**Option A: Direct git hook (recommended for simplicity)**

```bash
#!/usr/bin/env bash
# .githooks/pre-commit
python3 scripts/validate.py $(git diff --cached --name-only --diff-filter=ACM -- '*.md')
```

Configure git to use the hooks directory:
```bash
git config core.hooksPath .githooks
```

**Option B: pre-commit framework**

The `pre-commit` Python framework is more powerful but adds a dependency. For a knowledge base repo (not a code project), Option A is sufficient. The pre-commit framework adds value when you have multiple hook types, language-specific hooks, and shared hooks across repos. Overkill here.

---

## 6. Routing Index Design

**Confidence: HIGH** -- Based on verified Claude Code loading behavior.

### What the Routing Index Does

The routing index lives in `.claude/rules/sap-routing.md` and is always loaded into context. Its job: tell Claude which files to read based on the user's question topic. This prevents Claude from guessing file locations or reading everything.

### Routing Index Structure

```markdown
---
paths: []
---

# SAP ECC 6 Knowledge Base - Routing Index

When asked about SAP ECC 6, use this index to find the right reference files.

## Module Routing

| Topic | Module | Key Files |
|-------|--------|-----------|
| Procurement, purchasing, POs, vendors | MM | modules/mm/ |
| Inventory, goods movements, MIGO | MM | modules/mm/tcodes.md, modules/mm/processes.md |
| Sales orders, deliveries, billing | SD | modules/sd/ |
| General ledger, AP, AR, assets | FI | modules/fi/ |
| Cost centers, internal orders, profit centers | CO | modules/co/ |
| Account determination, OBYC, VKOA | Cross-module | modules/mm/integration.md, modules/sd/integration.md |
| End-to-end processes (P2P, O2C, R2R) | Cross-module | cross-module/ |
| Movement types, document types, posting keys | Reference | reference/ |

## How to Use

1. Identify the SAP module from the user's question
2. Navigate to the appropriate module directory
3. Read the module's CLAUDE.md for orientation
4. Read the specific content file(s) relevant to the question

## Important

- This knowledge base covers **SAP ECC 6.0 only** (not S/4HANA)
- When content mentions S/4HANA, it is for disambiguation only
- Always check the file's frontmatter for confidence level and last_verified date
```

### Token Budget for Always-Loaded Rules

The three always-loaded rules files in `.claude/rules/` should collectively stay under **1500 tokens**. This is the "tax" paid on every session, even non-SAP ones. Breakdown:

| File | Purpose | Target Tokens |
|------|---------|---------------|
| `sap-routing.md` | Query-to-file routing table | 300-500 |
| `sap-disambiguation.md` | Top 10-15 ECC vs S/4 differences | 400-600 |
| `sap-org-structure.md` | Org unit hierarchy summary | 200-400 |

The global `~/.claude/rules/sap-routing.md` (Layer 1 of the three-layer approach) should be even smaller -- just a pointer. Around 100-200 tokens:

```markdown
# SAP Knowledge Base

For SAP ECC 6.0 questions, read from ~/Claude/SAPKnowledge/

The knowledge base contains module-specific reference for MM, SD, FI, CO with
transaction codes, SPRO configuration paths, process flows, and integration points.

Start with the module's CLAUDE.md file for orientation.
```

---

## 7. ECC 6 vs S/4HANA Marking Convention

**Confidence: HIGH** -- Locked decision from context discussion.

### Dual Marking Approach

Per context discussion: "ECC 6 vs S/4HANA differences marked two ways: inline callout blocks + dedicated section per file."

**Inline callout format:**

```markdown
## Vendor Master Data

The vendor master is maintained via T-code XK01/XK02/XK03 (or FK01/FK02/FK03 for
FI-only views and MK01/MK02/MK03 for MM-only views).

> **S/4HANA difference:** In S/4HANA, the separate vendor master (LFA1) and customer
> master (KNA1) are replaced by the Business Partner (BP transaction, BUT000 table).
> Vendor/customer T-codes still work via compatibility views but are deprecated.
```

**Dedicated section (bottom of file):**

```markdown
## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|--------|
| Separate vendor master (LFA1) | Business Partner (BUT000) | T-codes XK01/MK01 deprecated |
| Material documents in MKPF/MSEG | MATDOC single table | Different table structure |
| Optional Material Ledger | Mandatory Material Ledger | Always active, cannot deactivate |
```

---

## 8. Template Files for Phase 1

Phase 1 should produce template/skeleton files that later phases fill with content. These templates enforce the conventions established here.

### Module CLAUDE.md Template

```markdown
---
module: {module_code}
content_type: index
ecc_version: "6.0"
ehp_range: "0-8"
confidence: high
last_verified: {date}
---

# SAP {Module Name}

## When to Use This Module
- [Primary use case 1]
- [Primary use case 2]

## File Index

| File | Contains | Read When |
|------|----------|-----------|
| @tcodes.md | Transaction codes | Looking up T-codes or finding the right transaction |
| @config-spro.md | SPRO/IMG configuration paths | Configuring {module} settings |
| @processes.md | Business process flows | Understanding end-to-end processes |
| @master-data.md | Master data objects | Working with master data records |
| @integration.md | Cross-module integration | Understanding postings to other modules |
| @patterns.md | Solution design patterns | Solving common business requirements |

## Key Concepts
- [Concept 1]
- [Concept 2]
```

### Content File Template

```markdown
---
module: {module_code}
content_type: {type}
ecc_version: "6.0"
ehp_range: "0-8"
confidence: low
last_verified: {date}
---

# {Module} - {Topic}

> ECC 6.0 specific. For S/4HANA differences, see the S/4HANA Differences section below.

## Quick Reference

[Table or bullet list for fast lookups - to be populated]

## Detail

[Expanded content - to be populated]

## Integration Points

[Cross-module connections - to be populated]

## Common Scenarios

[FAQ-style guidance - to be populated]

## S/4HANA Differences

| ECC 6 Behavior | S/4HANA Change | Impact |
|----------------|----------------|--------|
| [To be populated] | | |
```

---

## 9. Implementation Sequence Recommendation

Based on dependency analysis, the work within Phase 1 should follow this order:

### Plan 1: Directory Structure + Templates
1. Create the full directory tree
2. Place template CLAUDE.md files in each module and section directory
3. Create template content files (empty with frontmatter only)
4. Verify Claude Code loads the structure correctly by testing on-demand loading

### Plan 2: Validation Scripts
1. Implement `validate.py` with all five check categories
2. Create `requirements.txt` with `python-frontmatter`
3. Write the pre-commit hook
4. Configure git hooks path
5. Run validation against the template files to verify it works

### Plan 3: Global Loading Configuration
1. Create `~/.claude/rules/sap-routing.md` (Layer 1 pointer)
2. Configure `~/.claude/settings.json` with `additionalDirectories` (Layer 2)
3. Test from a different project directory to verify the knowledge base is accessible
4. Document the setup steps for other users

**Why this order:**
- Plan 1 must come first because Plans 2 and 3 need files to validate and load
- Plan 2 can start once the directory structure exists (validates against templates)
- Plan 3 depends on the project's own `.claude/rules/` being in place (created in Plan 1)

---

## 10. Risks and Open Questions

### Risk: `additionalDirectories` CLAUDE.md loading is opt-in

The `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` environment variable must be set. This is an extra configuration step that could be missed. Mitigation: document clearly in the project README and the global routing pointer.

### Risk: Always-loaded token budget creep

As the knowledge base grows, there will be pressure to add more content to `.claude/rules/`. Every token there is paid on every session. Mitigation: hard cap of 1500 tokens combined for all rules files. Validation script should enforce this.

### Risk: @import approval dialog

First-time `@import` in a project shows an approval dialog. If declined, imports are permanently disabled for that project. Mitigation: document this clearly. If declined, user must re-approve (method TBD -- may require clearing project settings).

### Open Question: Does `additionalDirectories` + `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` load child CLAUDE.md on-demand?

The documentation confirms it loads `.claude/rules/*.md` and CLAUDE.md from additional directories. It is not 100% clear whether the on-demand child CLAUDE.md loading (entering subtrees) works the same way as it does in the primary working directory. This needs empirical testing in Plan 3.

**Confidence: MEDIUM** -- The docs say the feature loads "CLAUDE.md, .claude/CLAUDE.md, and .claude/rules/*.md" but do not explicitly address subtree on-demand loading for additional directories.

### Open Question: File size for tcodes.md

50-80 T-codes per module, each with description, menu path, and usage context. A rough estimate: 80 T-codes * 3 lines * 60 chars = ~14,400 chars = ~3,600 tokens. This is within the 5,000 token hard cap but at the upper end. May need to split into subcategories (e.g., `tcodes-purchasing.md`, `tcodes-inventory.md`) if token counts exceed budget. This is a Phase 3+ concern, not Phase 1.

---

## Sources

### Official Documentation (HIGH confidence)
- [Claude Code Memory Documentation](https://code.claude.com/docs/en/memory) -- Authoritative source for CLAUDE.md loading, @import syntax, rules directory, auto memory
- [Claude Code Settings Documentation](https://code.claude.com/docs/en/settings) -- Settings hierarchy, additionalDirectories, environment variables

### GitHub Issues (HIGH confidence for specific claims)
- [Issue #990: Syntax for including CLAUDE.md files](https://github.com/anthropics/claude-code/issues/990) -- @import syntax decision
- [Issue #7412: @mentions don't work with additional directories](https://github.com/anthropics/claude-code/issues/7412) -- Known limitation, open bug

### Community Resources (MEDIUM confidence)
- [Claude Code Rules Directory Guide](https://claudefa.st/blog/guide/mechanics/rules-directory) -- Practical usage patterns for rules/
- [The Ultimate Guide to CLAUDE.md](https://www.buildcamp.io/guides/the-ultimate-guide-to-claudemd) -- Community best practices
- [python-frontmatter on PyPI](https://pypi.org/project/python-frontmatter/) -- Library for YAML frontmatter parsing
- [Anthropic Token Count API](https://docs.anthropic.com/en/api/messages-count-tokens) -- Official token counting (not used in validation, but reference)
- [Token Counting Guide 2025](https://www.propelcode.ai/blog/token-counting-tiktoken-anthropic-gemini-guide-2025) -- Character heuristic validation

### Ecosystem Research (from prior phase)
- `/home/corye/Claude/SAPKnowledge/.planning/research/ARCHITECTURE.md` -- File hierarchy design
- `/home/corye/Claude/SAPKnowledge/.planning/research/STACK.md` -- Technology stack decisions
- `/home/corye/Claude/SAPKnowledge/.planning/research/PITFALLS.md` -- S/4 contamination patterns
