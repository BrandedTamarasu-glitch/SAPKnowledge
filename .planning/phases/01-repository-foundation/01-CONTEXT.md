# Phase 1: Repository Foundation - Context

**Gathered:** 2026-02-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the file/folder structure, YAML frontmatter conventions, Claude Code loading configuration, and validation scripts that all subsequent SAP content builds upon. No SAP content is authored in this phase — only the scaffolding and quality gates.

</domain>

<decisions>
## Implementation Decisions

### Directory Organization
- Top-level structure: `modules/`, `cross-module/`, `reference/`, `.claude/rules/`
- Module folders: `modules/fi/`, `modules/mm/`, `modules/sd/`, `modules/co/`
- One file per content type within each module: tcodes.md, config-spro.md, processes.md, master-data.md, integration.md, patterns.md (~6-7 files per module)
- Cross-module content lives in two places: module-specific integration in each `modules/xx/integration.md`, and full E2E flows in `cross-module/`
- Shared reference content split: compact index in `.claude/rules/`, full detail in `reference/`

### File Naming & Metadata
- Full YAML frontmatter on every content file: module, ecc_version (6.0), ehp_range (0-8), confidence (high/medium/low), last_verified (date)
- EhP baseline is broad (EhP 0-8) — document core ECC 6 behavior, annotate where specific Enhancement Pack matters
- ECC 6 vs S/4HANA differences marked two ways: inline callout blocks for critical differences at point of use, plus dedicated "ECC 6 vs S/4HANA" section at bottom of each file for comprehensive list

### Claude's Discretion
- File naming convention within module folders (descriptive kebab-case vs numbered prefix)
- Token budget per file (research suggested 800-2500, up to 5000 for dense topics — Claude calibrates based on content type)

### Claude Code Loading Strategy
- Always-loaded content in `.claude/rules/`: routing index, ECC vs S/4 quick reference, org structure summary — all three, kept concise
- On-demand loading via both mechanisms: CLAUDE.md per module folder (directory-based) + @import references from routing index (explicit)
- **Critical: Must work from any project directory**, not just from within SAPKnowledge/ — this means the loading mechanism needs to be globally accessible (likely via `~/.claude/` rules or similar), not reliant on being cd'd into the repo

### Validation & Quality Gates
- Validation scripts check all four areas: structure (frontmatter, required fields, correct directory), token budget, cross-reference integrity, S/4 contamination detection
- Runs both as pre-commit hook and manual command for ad-hoc checks
- Strictness: block commits on critical failures (S/4 contamination, missing frontmatter), warn only on minor issues (token budget exceeded)
- Script language: Claude's discretion (shell or Python based on complexity needs)

</decisions>

<specifics>
## Specific Ideas

- S/4 contamination detection should flag known S/4-only terms: Universal Journal, MATDOC, Business Partner (as replacement for vendor/customer master), ACDOCA, and obsolete T-codes
- The "from any project" requirement is the most architecturally significant decision — it changes how `.claude/rules/` files are deployed (global vs project-local)
- Routing index should tell Claude which files to @import based on query context (e.g., "procurement question → @modules/mm/tcodes.md, @modules/mm/processes.md")

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-repository-foundation*
*Context gathered: 2026-02-16*
