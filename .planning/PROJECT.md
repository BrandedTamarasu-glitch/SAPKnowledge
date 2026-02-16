# SAP ECC 6 Knowledge Base

## What This Is

A curated collection of structured markdown reference files covering SAP ECC 6.0, designed to be loaded into Claude Code's context to make it a reliable SAP solutioning assistant. The knowledge base covers transaction codes, configuration paths, business process mappings, integration points, and solution design patterns — all specific to ECC 6 (not S/4HANA).

## Core Value

When someone in the organization asks Claude "how do I do X in SAP," it gives the correct ECC 6 answer — right transaction, right config path, right module interactions — not a generic or S/4HANA-confused response.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Curated T-code reference for MM, SD, FI, CO with descriptions, menu paths, and usage context
- [ ] SPRO/IMG configuration guides with step-by-step paths specific to ECC 6
- [ ] Business process maps (procure-to-pay, order-to-cash, record-to-report) tied to transactions and config
- [ ] Module integration point documentation (MM→FI postings, SD→FI billing, CO→FI reconciliation, etc.)
- [ ] Org structure reference (company code, plant, storage location, sales org, purchasing org, controlling area)
- [ ] ECC 6 vs S/4HANA disambiguation — explicit callouts where behavior differs
- [ ] Solution design patterns — common business requirements mapped to SAP capabilities
- [ ] Markdown files structured for Claude Code context loading

### Out of Scope

- S/4HANA-specific content — this is ECC 6 only, with S/4 noted only for disambiguation
- Company-specific config values — this is general ECC 6 reference, not your system's specific settings
- ABAP development reference — focus is functional solutioning, not custom code
- MCP server infrastructure — delivering as flat markdown files, not a server
- PP, PM, HCM modules — deferred to v2 after format is proven with MM/SD/FI/CO

## Context

- Target platform: Claude Code with markdown files loaded into context
- SAP version: ECC 6.0 (EHP levels vary but content targets broadly applicable ECC 6 behavior)
- Content sources: SAP Help Portal, public SAP documentation, curated from established SAP knowledge
- Audience: Entire organization — must be accurate enough for non-SAP-experts to rely on
- Pain points driving this: Claude currently confuses ECC 6 with S/4HANA, gives vague config advice, doesn't know correct T-codes/menu paths, and misses integration points between modules

## Constraints

- **Content accuracy**: Must be verifiable against SAP official documentation — wrong answers erode trust org-wide
- **ECC 6 specificity**: Every piece of content must be validated as applicable to ECC 6.0, not assumed from S/4HANA docs
- **Context window**: Markdown files must be structured so relevant content can be loaded selectively (not everything at once)
- **No internal data**: Knowledge base contains only publicly available SAP reference information

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Markdown files over MCP server | Simpler, no infrastructure, portable, anyone with Claude Code can use | — Pending |
| Prioritize MM/SD/FI/CO for v1 | Core logistics and finance modules, highest org usage, proves format before expanding | — Pending |
| ECC 6 only, S/4 disambiguation | Prevents the #1 pain point — Claude mixing up ECC and S/4 behavior | — Pending |
| Public sources only | Keeps knowledge base shareable, avoids internal data concerns | — Pending |

---
*Last updated: 2026-02-16 after initialization*
