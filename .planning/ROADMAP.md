# Roadmap: SAP ECC 6 Knowledge Base

## Overview

This roadmap delivers a curated markdown knowledge base that transforms Claude Code into a reliable SAP ECC 6 solutioning assistant. Starting with foundational structure and FI (the integration backbone), expanding through core logistics modules (MM/SD), layering in cost accounting (CO), weaving cross-module integration, and culminating in solution design intelligence. Each phase delivers standalone value while building toward comprehensive ECC 6 reference coverage.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Repository Foundation** - Directory structure, YAML conventions, validation scripts
- [ ] **Phase 2: Core Reference Framework** - Org structure reference, ECC 6 vs S/4HANA disambiguation
- [ ] **Phase 3: FI Module Foundation** - T-codes, SPRO paths, processes, master data
- [ ] **Phase 4: FI Advanced & Integration Prep** - Account determination, decision trees, troubleshooting
- [ ] **Phase 5: MM Module Foundation** - T-codes, SPRO paths, processes, master data
- [ ] **Phase 6: MM Advanced & FI Integration** - OBYC account determination, decision trees, MM-FI integration
- [ ] **Phase 7: SD Module Foundation** - T-codes, SPRO paths, processes, master data
- [ ] **Phase 8: SD Advanced & FI Integration** - VKOA account determination, pricing basics, SD-FI integration
- [ ] **Phase 9: CO Module Foundation** - T-codes, SPRO paths, processes, master data
- [ ] **Phase 10: CO Advanced & FI Integration** - Cost element mapping, CO-FI reconciliation, decision trees
- [ ] **Phase 11: Cross-Module Integration** - MM-SD integration, end-to-end process flows
- [ ] **Phase 12: Solution Design Intelligence** - Design patterns, scenario playbooks, operational checklists

## Phase Details

### Phase 1: Repository Foundation
**Goal**: Establish file structure, metadata conventions, and quality validation that all subsequent content builds upon
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-05, FOUND-06
**Success Criteria** (what must be TRUE):
  1. Repository has complete directory structure (modules/, cross-module/, reference/, .claude/rules/)
  2. Every content file uses YAML frontmatter with required fields (module, ecc_version, confidence, last_verified, ehp_range)
  3. Validation scripts can verify cross-references, frontmatter presence, and file size budgets
  4. Routing index in .claude/rules/ directs Claude to correct module files based on query context
**Plans:** 3 plans

Plans:
- [ ] 01-01-PLAN.md — Directory structure, template files, and .claude/rules/ routing content
- [ ] 01-02-PLAN.md — Validation scripts and pre-commit hook
- [ ] 01-03-PLAN.md — Global loading configuration for cross-project access

### Phase 2: Core Reference Framework
**Goal**: Create always-available org structure and disambiguation framework that all module content references
**Depends on**: Phase 1
**Requirements**: FOUND-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. Org structure reference documents relationships between company code, plant, storage location, sales org, purchasing org, controlling area
  2. ECC 6 vs S/4HANA disambiguation framework exists with dedicated annotations for behavioral differences
  3. Every query touching org units resolves correct hierarchical relationships from reference
  4. Claude explicitly identifies when asked about S/4HANA-only features (Universal Journal, Business Partner, MATDOC)
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD

### Phase 3: FI Module Foundation
**Goal**: Deliver complete FI reference covering transactions, configuration, processes, and master data as integration target for all other modules
**Depends on**: Phase 2
**Requirements**: FI-01, FI-02, FI-03, FI-04
**Success Criteria** (what must be TRUE):
  1. User can find correct FI T-code (50-80 transactions) with menu path and usage context for GL, AP, AR, asset accounting
  2. User can navigate SPRO/IMG configuration for FI with step-by-step paths
  3. Record-to-report business process maps tie specific transactions to process steps
  4. Master data reference covers GL accounts, vendor master, customer master, asset master with key field explanations
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD
- [ ] 03-03: TBD

### Phase 4: FI Advanced & Integration Prep
**Goal**: Layer on FI account determination logic, decision frameworks, and troubleshooting that enable MM/SD integration in later phases
**Depends on**: Phase 3
**Requirements**: FI-05, FI-06, FI-07
**Success Criteria** (what must be TRUE):
  1. Account determination logic for automatic postings (integration with MM and SD) is documented with examples
  2. Configuration decision trees guide common FI scenarios (parallel accounting, payment terms, dunning)
  3. Common FI gotchas and troubleshooting guide resolves ECC 6-specific issues
  4. User can answer "what GL account gets debited when MM posts goods receipt" from content
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

### Phase 5: MM Module Foundation
**Goal**: Deliver complete MM reference covering transactions, configuration, processes, and master data for procurement and inventory
**Depends on**: Phase 4
**Requirements**: MM-01, MM-02, MM-03, MM-04
**Success Criteria** (what must be TRUE):
  1. User can find correct MM T-code (50-80 transactions) with menu path and usage context for purchasing, inventory, invoice verification
  2. User can navigate SPRO/IMG configuration for MM with step-by-step paths
  3. Procure-to-pay business process maps tie specific transactions to process steps
  4. Master data reference covers material master, vendor master, purchasing info records, source lists with key field explanations
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD
- [ ] 05-03: TBD

### Phase 6: MM Advanced & FI Integration
**Goal**: Document OBYC account determination, MM decision trees, troubleshooting, and complete MM-FI integration point
**Depends on**: Phase 5
**Requirements**: MM-05, MM-06, MM-07, INTG-01
**Success Criteria** (what must be TRUE):
  1. OBYC account determination walkthrough explains movement type to GL account mapping with step-by-step examples
  2. Configuration decision trees guide common MM scenarios (valuation, split valuation, release strategy, MRP)
  3. Common MM gotchas and troubleshooting guide resolves ECC 6-specific issues
  4. MM-FI integration point documentation covers goods receipt/issue postings, invoice verification, OBYC mapping completely
  5. User can trace "what happens in FI when I post MIGO with movement type 101" from content
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD
- [ ] 06-03: TBD

### Phase 7: SD Module Foundation
**Goal**: Deliver complete SD reference covering transactions, configuration, processes, and master data for order-to-cash
**Depends on**: Phase 6
**Requirements**: SD-01, SD-02, SD-03, SD-04
**Success Criteria** (what must be TRUE):
  1. User can find correct SD T-code (50-80 transactions) with menu path and usage context for sales, shipping, billing, pricing
  2. User can navigate SPRO/IMG configuration for SD with step-by-step paths
  3. Order-to-cash business process maps tie specific transactions to process steps
  4. Master data reference covers customer master, material master sales views, pricing conditions, output determination with key field explanations
**Plans**: TBD

Plans:
- [ ] 07-01: TBD
- [ ] 07-02: TBD
- [ ] 07-03: TBD

### Phase 8: SD Advanced & FI Integration
**Goal**: Document VKOA account determination, SD decision trees (including pricing foundations), troubleshooting, and complete SD-FI integration point
**Depends on**: Phase 7
**Requirements**: SD-05, SD-06, SD-07, INTG-02
**Success Criteria** (what must be TRUE):
  1. VKOA account determination walkthrough explains billing document to GL account mapping with step-by-step examples
  2. Configuration decision trees guide common SD scenarios (pricing procedures, copy control, partner determination, availability check)
  3. Common SD gotchas and troubleshooting guide resolves ECC 6-specific issues
  4. SD-FI integration point documentation covers billing postings, revenue recognition, VKOA mapping completely
  5. User can trace "what happens in FI when I post VF01 billing document" from content
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD
- [ ] 08-03: TBD

### Phase 9: CO Module Foundation
**Goal**: Deliver complete CO reference covering transactions, configuration, processes, and master data for cost accounting
**Depends on**: Phase 8
**Requirements**: CO-01, CO-02, CO-03, CO-04
**Success Criteria** (what must be TRUE):
  1. User can find correct CO T-code (50-80 transactions) with menu path and usage context for cost center accounting, profit centers, internal orders, product costing
  2. User can navigate SPRO/IMG configuration for CO with step-by-step paths
  3. Business process maps for cost allocation and settlement tie specific transactions to process steps
  4. Master data reference covers cost centers, profit centers, internal orders, cost elements, activity types with key field explanations
**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD
- [ ] 09-03: TBD

### Phase 10: CO Advanced & FI Integration
**Goal**: Document cost element mapping, CO-FI reconciliation, decision trees, troubleshooting, and complete CO-FI integration point
**Depends on**: Phase 9
**Requirements**: CO-05, CO-06, CO-07, INTG-03
**Success Criteria** (what must be TRUE):
  1. Cost element mapping and CO-FI reconciliation walkthrough explains cost element types and reconciliation ledger
  2. Configuration decision trees guide common CO scenarios (allocation cycles, settlement rules, transfer pricing)
  3. Common CO gotchas and troubleshooting guide resolves ECC 6-specific issues
  4. CO-FI integration point documentation covers cost element types, reconciliation ledger, real-time integration completely
  5. User can trace "how cost center postings reconcile with FI" from content
**Plans**: TBD

Plans:
- [ ] 10-01: TBD
- [ ] 10-02: TBD
- [ ] 10-03: TBD

### Phase 11: Cross-Module Integration
**Goal**: Complete integration coverage with MM-SD touchpoints and deliver end-to-end process flows spanning multiple modules
**Depends on**: Phase 10
**Requirements**: INTG-04, E2E-01, E2E-02, E2E-03
**Success Criteria** (what must be TRUE):
  1. MM-SD integration point documentation covers availability check, goods issue for delivery, returns completely
  2. Procure-to-Pay full process flow documents transaction sequence, document flow, integration touchpoints across MM and FI
  3. Order-to-Cash full process flow documents transaction sequence, document flow, integration touchpoints across SD and FI
  4. Record-to-Report full process flow documents period-end activities, reconciliation steps, reporting across FI and CO
  5. User can answer "what's the complete flow from PO to payment" or "from sales order to revenue recognition" from content
**Plans**: TBD

Plans:
- [ ] 11-01: TBD
- [ ] 11-02: TBD
- [ ] 11-03: TBD

### Phase 12: Solution Design Intelligence
**Goal**: Layer solution design patterns, scenario playbooks, and operational checklists on top of complete module and integration foundation
**Depends on**: Phase 11
**Requirements**: SOLN-01, SOLN-02, SOLN-03, SOLN-04
**Success Criteria** (what must be TRUE):
  1. Solution design patterns map common business requirements to SAP ECC 6 capabilities with recommended configuration approach
  2. Scenario playbooks guide complex processes (consignment, intercompany sales, third-party processing, subcontracting)
  3. Scenario playbooks guide complex config (split valuation, special procurement, batch management, serial numbers)
  4. Operational checklists cover month-end and year-end close across MM, SD, FI, CO with specific T-codes and sequence
  5. User can answer "how do I implement consignment in ECC 6" or "what's the month-end close checklist" from content
**Plans**: TBD

Plans:
- [ ] 12-01: TBD
- [ ] 12-02: TBD
- [ ] 12-03: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Repository Foundation | 0/3 | Planning complete | - |
| 2. Core Reference Framework | 0/TBD | Not started | - |
| 3. FI Module Foundation | 0/TBD | Not started | - |
| 4. FI Advanced & Integration Prep | 0/TBD | Not started | - |
| 5. MM Module Foundation | 0/TBD | Not started | - |
| 6. MM Advanced & FI Integration | 0/TBD | Not started | - |
| 7. SD Module Foundation | 0/TBD | Not started | - |
| 8. SD Advanced & FI Integration | 0/TBD | Not started | - |
| 9. CO Module Foundation | 0/TBD | Not started | - |
| 10. CO Advanced & FI Integration | 0/TBD | Not started | - |
| 11. Cross-Module Integration | 0/TBD | Not started | - |
| 12. Solution Design Intelligence | 0/TBD | Not started | - |
