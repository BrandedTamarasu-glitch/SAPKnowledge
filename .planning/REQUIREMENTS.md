# Requirements: SAP ECC 6 Knowledge Base

**Defined:** 2026-02-16
**Core Value:** When someone asks Claude "how do I do X in SAP," it gives the correct ECC 6 answer — right transaction, right config path, right module interactions.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Foundation

- [ ] **FOUND-01**: Always-loaded routing index in `.claude/rules/` that directs Claude to the correct module files based on query context
- [ ] **FOUND-02**: YAML frontmatter convention applied to every content file (module, ecc_version, confidence, last_verified, ehp_range)
- [ ] **FOUND-03**: Org structure reference covering company code, plant, storage location, sales org, distribution channel, division, purchasing org, purchasing group, controlling area, and their relationships
- [ ] **FOUND-04**: ECC 6 vs S/4HANA disambiguation framework with dedicated annotations in every content file calling out behavioral differences
- [ ] **FOUND-05**: Validation scripts that verify cross-references resolve, YAML frontmatter is present, file sizes stay within token budget, and no S/4HANA-only content leaks in
- [ ] **FOUND-06**: File/folder structure following module-first organization with child CLAUDE.md files for on-demand loading

### FI — Financial Accounting

- [ ] **FI-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [ ] **FI-02**: SPRO/IMG configuration paths for GL, AP, AR, and asset accounting with step-by-step guidance
- [ ] **FI-03**: Business process maps for record-to-report tied to specific transactions and config
- [ ] **FI-04**: Master data reference covering GL accounts, vendor master, customer master, asset master — key fields and relationships
- [ ] **FI-05**: Account determination logic for automatic postings (integration with MM and SD)
- [ ] **FI-06**: Configuration decision trees for common FI scenarios (parallel accounting, payment terms, dunning)
- [ ] **FI-07**: Common FI gotchas and troubleshooting guide specific to ECC 6

### MM — Materials Management

- [ ] **MM-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [ ] **MM-02**: SPRO/IMG configuration paths for purchasing, inventory management, and invoice verification with step-by-step guidance
- [ ] **MM-03**: Business process maps for procure-to-pay tied to specific transactions and config
- [ ] **MM-04**: Master data reference covering material master, vendor master, purchasing info records, source lists — key fields and relationships
- [ ] **MM-05**: Account determination walkthrough for MM (OBYC) — movement types to GL account mapping
- [ ] **MM-06**: Configuration decision trees for common MM scenarios (valuation, split valuation, release strategy, MRP)
- [ ] **MM-07**: Common MM gotchas and troubleshooting guide specific to ECC 6

### SD — Sales & Distribution

- [ ] **SD-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [ ] **SD-02**: SPRO/IMG configuration paths for sales, shipping, billing, and pricing with step-by-step guidance
- [ ] **SD-03**: Business process maps for order-to-cash tied to specific transactions and config
- [ ] **SD-04**: Master data reference covering customer master, material master (sales views), pricing conditions, output determination — key fields and relationships
- [ ] **SD-05**: Account determination walkthrough for SD (VKOA) — billing document to GL account mapping
- [ ] **SD-06**: Configuration decision trees for common SD scenarios (pricing procedures, copy control, partner determination, availability check)
- [ ] **SD-07**: Common SD gotchas and troubleshooting guide specific to ECC 6

### CO — Controlling

- [ ] **CO-01**: Curated T-code reference (50-80 transactions) with descriptions, menu paths, and usage context
- [ ] **CO-02**: SPRO/IMG configuration paths for cost center accounting, profit center accounting, internal orders, and product costing with step-by-step guidance
- [ ] **CO-03**: Business process maps for cost allocation and settlement tied to specific transactions and config
- [ ] **CO-04**: Master data reference covering cost centers, profit centers, internal orders, cost elements, activity types — key fields and relationships
- [ ] **CO-05**: Cost element mapping and CO-FI reconciliation walkthrough
- [ ] **CO-06**: Configuration decision trees for common CO scenarios (allocation cycles, settlement rules, transfer pricing)
- [ ] **CO-07**: Common CO gotchas and troubleshooting guide specific to ECC 6

### Integration

- [ ] **INTG-01**: MM→FI integration point documentation (goods receipt/issue postings, invoice verification, OBYC mapping)
- [ ] **INTG-02**: SD→FI integration point documentation (billing postings, revenue recognition, VKOA mapping)
- [ ] **INTG-03**: CO→FI integration point documentation (cost element types, reconciliation ledger, real-time integration)
- [ ] **INTG-04**: MM↔SD integration point documentation (availability check, goods issue for delivery, returns)

### End-to-End Processes

- [ ] **E2E-01**: Procure-to-Pay full process flow across MM and FI with transaction sequence, document flow, and integration touchpoints
- [ ] **E2E-02**: Order-to-Cash full process flow across SD and FI with transaction sequence, document flow, and integration touchpoints
- [ ] **E2E-03**: Record-to-Report full process flow across FI and CO with period-end activities, reconciliation steps, and reporting

### Solution Design

- [ ] **SOLN-01**: Solution design patterns mapping common business requirements to SAP ECC 6 capabilities with recommended configuration approach
- [ ] **SOLN-02**: Scenario playbooks for complex processes (consignment, intercompany sales, third-party processing, subcontracting)
- [ ] **SOLN-03**: Scenario playbooks for complex config (split valuation, special procurement, batch management, serial numbers)
- [ ] **SOLN-04**: Operational checklists for month-end and year-end close across MM, SD, FI, CO

## v2 Requirements

### Additional Modules

- **PP-01**: Production Planning module — T-codes, config, MRP, production orders, shop floor
- **PM-01**: Plant Maintenance module — T-codes, config, work orders, maintenance plans
- **HCM-01**: Human Capital Management — T-codes, config, personnel admin, payroll

### Advanced Content

- **ADV-01**: Enhancement Pack delta documentation (EhP6 through EhP8 feature differences)
- **ADV-02**: Country-specific localization content (tax procedures, payment methods, dunning by country)
- **ADV-03**: Authorization concept reference (authorization objects, roles, profiles per module)

## Out of Scope

| Feature | Reason |
|---------|--------|
| S/4HANA how-to content | ECC 6 only — S/4 referenced only for disambiguation |
| ABAP development reference | Focus is functional solutioning, not custom code |
| Company-specific config values | General reference only, no internal system data |
| MCP server infrastructure | Delivering as flat markdown, no server to maintain |
| Exhaustive T-code lists | Curated 50-80 per module; exhaustive lists waste context and introduce accuracy risk |
| SAP table/field-level documentation | Referenced inline only where needed, not standalone |
| Screenshots or images | Markdown text only for Claude Code consumption |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Pending |
| FOUND-02 | Phase 1 | Pending |
| FOUND-03 | Phase 1 | Pending |
| FOUND-04 | Phase 1 | Pending |
| FOUND-05 | Phase 1 | Pending |
| FOUND-06 | Phase 1 | Pending |
| FI-01 | Phase 1 | Pending |
| FI-02 | Phase 1 | Pending |
| FI-03 | Phase 1 | Pending |
| FI-04 | Phase 1 | Pending |
| FI-05 | Phase 1 | Pending |
| FI-06 | Phase 1 | Pending |
| FI-07 | Phase 1 | Pending |
| MM-01 | Phase 2 | Pending |
| MM-02 | Phase 2 | Pending |
| MM-03 | Phase 2 | Pending |
| MM-04 | Phase 2 | Pending |
| MM-05 | Phase 2 | Pending |
| MM-06 | Phase 2 | Pending |
| MM-07 | Phase 2 | Pending |
| SD-01 | Phase 2 | Pending |
| SD-02 | Phase 2 | Pending |
| SD-03 | Phase 2 | Pending |
| SD-04 | Phase 2 | Pending |
| SD-05 | Phase 2 | Pending |
| SD-06 | Phase 2 | Pending |
| SD-07 | Phase 2 | Pending |
| CO-01 | Phase 3 | Pending |
| CO-02 | Phase 3 | Pending |
| CO-03 | Phase 3 | Pending |
| CO-04 | Phase 3 | Pending |
| CO-05 | Phase 3 | Pending |
| CO-06 | Phase 3 | Pending |
| CO-07 | Phase 3 | Pending |
| INTG-01 | Phase 3 | Pending |
| INTG-02 | Phase 3 | Pending |
| INTG-03 | Phase 3 | Pending |
| INTG-04 | Phase 3 | Pending |
| E2E-01 | Phase 4 | Pending |
| E2E-02 | Phase 4 | Pending |
| E2E-03 | Phase 4 | Pending |
| SOLN-01 | Phase 4 | Pending |
| SOLN-02 | Phase 4 | Pending |
| SOLN-03 | Phase 4 | Pending |
| SOLN-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 42 total
- Mapped to phases: 42
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-16*
*Last updated: 2026-02-16 after initial definition*
