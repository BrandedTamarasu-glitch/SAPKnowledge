# Requirements: SAP ECC 6 Knowledge Base

**Defined:** 2026-02-16
**Updated:** 2026-02-23 (v1.1 milestone)
**Core Value:** When someone asks Claude "how do I do X in SAP," it gives the correct ECC 6 answer — right transaction, right config path, right module interactions.

## v1.1 Requirements

Requirements for v1.1 MCP Server release. Each maps to roadmap phases.

### MCP Server Infrastructure

- [x] **MCP-01**: Developer can install the MCP server using standard Python tooling (venv + pip install)
- [ ] **MCP-02**: MCP server runs via stdio transport registered at repo root (`.mcp.json`) for Claude Code + Claude Desktop

### MCP Query Tools

- [ ] **MCP-03**: User can look up any SAP T-code and get description, module, menu path, and usage context
- [ ] **MCP-04**: User can get an overview of available KB content for a specific module (MM/SD/FI/CO)
- [ ] **MCP-05**: User can retrieve SPRO/IMG configuration path and steps for a given module + topic
- [ ] **MCP-06**: User can retrieve a step-by-step process flow for a named SAP business process
- [ ] **MCP-07**: User can compare ECC 6 vs S/4HANA behavior for a given topic or feature
- [ ] **MCP-08**: User can search the full KB by keyword and get matching excerpts with source module/file

### Tool Design Quality

- [ ] **MCP-09**: Each tool description is written as an invocation condition for reliable LLM routing (not a developer description)
- [x] **MCP-10**: Tool responses use section-level extraction (not full file content) to stay within context limits

### Deployment

- [ ] **MCP-11**: Setup documentation enables a non-developer to configure the MCP server in Claude Code and Claude Desktop

## v1 Requirements

Requirements for initial release (v1.0 — all shipped).

### Foundation

- [x] **FOUND-01**: Always-loaded routing index in `.claude/rules/` that directs Claude to the correct module files based on query context
- [x] **FOUND-02**: YAML frontmatter convention applied to every content file (module, ecc_version, confidence, last_verified, ehp_range)
- [x] **FOUND-03**: Org structure reference covering company code, plant, storage location, sales org, distribution channel, division, purchasing org, purchasing group, controlling area, and their relationships
- [x] **FOUND-04**: ECC 6 vs S/4HANA disambiguation framework with dedicated annotations in every content file calling out behavioral differences
- [x] **FOUND-05**: Validation scripts that verify cross-references resolve, YAML frontmatter is present, file sizes stay within token budget, and no S/4HANA-only content leaks in
- [x] **FOUND-06**: File/folder structure following module-first organization with child CLAUDE.md files for on-demand loading

### FI — Financial Accounting

- [x] **FI-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [x] **FI-02**: SPRO/IMG configuration paths for GL, AP, AR, and asset accounting with step-by-step guidance
- [x] **FI-03**: Business process maps for record-to-report tied to specific transactions and config
- [x] **FI-04**: Master data reference covering GL accounts, vendor master, customer master, asset master — key fields and relationships
- [x] **FI-05**: Account determination logic for automatic postings (integration with MM and SD)
- [x] **FI-06**: Configuration decision trees for common FI scenarios (parallel accounting, payment terms, dunning)
- [x] **FI-07**: Common FI gotchas and troubleshooting guide specific to ECC 6

### MM — Materials Management

- [x] **MM-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [x] **MM-02**: SPRO/IMG configuration paths for purchasing, inventory management, and invoice verification with step-by-step guidance
- [x] **MM-03**: Business process maps for procure-to-pay tied to specific transactions and config
- [x] **MM-04**: Master data reference covering material master, vendor master, purchasing info records, source lists — key fields and relationships
- [x] **MM-05**: Account determination walkthrough for MM (OBYC) — movement types to GL account mapping
- [x] **MM-06**: Configuration decision trees for common MM scenarios (valuation, split valuation, release strategy, MRP)
- [x] **MM-07**: Common MM gotchas and troubleshooting guide specific to ECC 6

### SD — Sales & Distribution

- [x] **SD-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [x] **SD-02**: SPRO/IMG configuration paths for sales, shipping, billing, and pricing with step-by-step guidance
- [x] **SD-03**: Business process maps for order-to-cash tied to specific transactions and config
- [x] **SD-04**: Master data reference covering customer master, material master (sales views), pricing conditions, output determination — key fields and relationships
- [x] **SD-05**: Account determination walkthrough for SD (VKOA) — billing document to GL account mapping
- [x] **SD-06**: Configuration decision trees for common SD scenarios (pricing procedures, copy control, partner determination, availability check)
- [x] **SD-07**: Common SD gotchas and troubleshooting guide specific to ECC 6

### CO — Controlling

- [x] **CO-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [x] **CO-02**: SPRO/IMG configuration paths for cost center accounting, profit center accounting, internal orders, and product costing with step-by-step guidance
- [x] **CO-03**: Business process maps for cost allocation and settlement tied to specific transactions and config
- [x] **CO-04**: Master data reference covering cost centers, profit centers, internal orders, cost elements, activity types — key fields and relationships
- [x] **CO-05**: Cost element mapping and CO-FI reconciliation walkthrough
- [x] **CO-06**: Configuration decision trees for common CO scenarios (allocation cycles, settlement rules, transfer pricing)
- [x] **CO-07**: Common CO gotchas and troubleshooting guide specific to ECC 6

### Integration

- [x] **INTG-01**: MM→FI integration point documentation (goods receipt/issue postings, invoice verification, OBYC mapping)
- [x] **INTG-02**: SD→FI integration point documentation (billing postings, revenue recognition, VKOA mapping)
- [x] **INTG-03**: CO→FI integration point documentation (cost element types, reconciliation ledger, real-time integration)
- [x] **INTG-04**: MM↔SD integration point documentation (availability check, goods issue for delivery, returns)

### End-to-End Processes

- [x] **E2E-01**: Procure-to-Pay full process flow across MM and FI with transaction sequence, document flow, and integration touchpoints
- [x] **E2E-02**: Order-to-Cash full process flow across SD and FI with transaction sequence, document flow, and integration touchpoints
- [x] **E2E-03**: Record-to-Report full process flow across FI and CO with period-end activities, reconciliation steps, and reporting

### Solution Design

- [x] **SOLN-01**: Solution design patterns mapping common business requirements to SAP ECC 6 capabilities with recommended configuration approach
- [x] **SOLN-02**: Scenario playbooks for complex processes (consignment, intercompany sales, third-party processing, subcontracting)
- [x] **SOLN-03**: Scenario playbooks for complex config (split valuation, special procurement, batch management, serial numbers)
- [x] **SOLN-04**: Operational checklists for month-end and year-end close across MM, SD, FI, CO

## v2 Requirements

### Additional Modules

- **PP-01**: Production Planning module — T-codes, config, MRP, production orders, shop floor
- **PM-01**: Plant Maintenance module — T-codes, config, work orders, maintenance plans
- **HCM-01**: Human Capital Management — T-codes, config, personnel admin, payroll

### Advanced Content

- **ADV-01**: Enhancement Pack delta documentation (EhP6 through EhP8 feature differences)
- **ADV-02**: Country-specific localization content (tax procedures, payment methods, dunning by country)
- **ADV-03**: Authorization concept reference (authorization objects, roles, profiles per module)

### Advanced MCP Tools

- **MCP-A01**: `get_account_determination` tool — OBYC/VKOA decision chain across MM and FI files
- **MCP-A02**: `get_scenario_playbook` tool — cross-module synthesis for complex scenario queries
- **MCP-A03**: `get_decision_tree` tool — configuration decision guidance for complex SAP scenarios

## Out of Scope

| Feature | Reason |
|---------|--------|
| S/4HANA how-to content | ECC 6 only — S/4 referenced only for disambiguation |
| ABAP development reference | Focus is functional solutioning, not custom code |
| Company-specific config values | General reference only, no internal system data |
| REST API / hosted endpoint | MCP server is local/org deployment via stdio, not a public HTTP API |
| Exhaustive T-code lists | Curated 50-80 per module; exhaustive lists waste context and introduce accuracy risk |
| SAP table/field-level documentation | Referenced inline only where needed, not standalone |
| Screenshots or images | Markdown text only for Claude Code consumption |
| Semantic search / embeddings | KB structure + keyword search covers 80%+ of patterns at a fraction of the complexity |

## Traceability

### v1.1 Requirements

| Requirement | Phase | Status |
|-------------|-------|--------|
| MCP-01 | Phase 13 | Complete |
| MCP-02 | Phase 13 | Pending |
| MCP-03 | Phase 13 | Pending |
| MCP-04 | Phase 13 | Pending |
| MCP-05 | Phase 13 | Pending |
| MCP-06 | Phase 13 | Pending |
| MCP-07 | Phase 13 | Pending |
| MCP-08 | Phase 14 | Pending |
| MCP-09 | Phase 13 | Pending |
| MCP-10 | Phase 13 | Complete |
| MCP-11 | Phase 15 | Pending |

**Coverage:**
- v1.1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

### v1 Requirements

All 42 v1 requirements complete ✓

---
*Requirements defined: 2026-02-16*
*Last updated: 2026-02-23 after v1.1 milestone start*
