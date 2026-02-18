# README, Description & v0.1.0 Release Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Write the README.md, set the GitHub repo description, push all commits, and create the v0.1.0 release.

**Architecture:** Write README.md directly (no tests — pure markdown content), set repo description via `gh repo edit`, push, tag v0.1.0, then create GitHub release via `gh release create`.

**Tech Stack:** Markdown, git, GitHub CLI (`gh`)

---

### Task 1: Write README.md

**Files:**
- Modify: `README.md`

**Step 1: Write the full README**

Replace the contents of `README.md` with:

```markdown
# SAP ECC 6.0 Knowledge Base for Claude Code

A curated reference for SAP ECC 6.0 — transaction codes, SPRO configuration paths, process flows, and integration points across MM, SD, FI, and CO. Designed to give Claude accurate, module-specific context when answering SAP questions.

> **Scope:** ECC 6.0 only. S/4HANA differences are noted for disambiguation, not as primary reference.

---

## Using It

### Step 1 — Clone the repo

```bash
git clone https://github.com/BrandedTamarasu-glitch/SAPKnowledge.git ~/Claude/SAPKnowledge
```

### Step 2 — Add the global rule to Claude Code

Create `~/.claude/rules/sap-knowledge-base.md` with this content:

```
For SAP ECC 6.0 questions, read from ~/Claude/SAPKnowledge/

The knowledge base contains module-specific reference for MM, SD, FI, CO with
transaction codes, SPRO configuration paths, process flows, and integration points.

Start with the module's CLAUDE.md file for orientation, or read
~/Claude/SAPKnowledge/.claude/rules/sap-routing.md for the full routing index.

Important: This knowledge base covers ECC 6.0 only, not S/4HANA.
```

### Step 3 — Verify it's loading

Open Claude Code in any project and run `/config`. Look for the rule file listed under **Global rules**. If it appears, you're set.

### Step 4 — Ask SAP questions naturally

Claude will automatically route SAP questions to the right content. No extra commands needed. Just ask:

| Topic | Example prompt |
|---|---|
| Transactions | "What T-code posts a goods receipt?" |
| Configuration | "What's the SPRO path to configure pricing procedures in SD?" |
| Process flows | "Walk me through the Order-to-Cash process end to end" |
| Integration | "How does internal order settlement create an FI document?" |
| Period-end | "What's the month-end close sequence for CO?" |
| Troubleshooting | "Why would a goods movement fail account determination?" |
| Playbooks | "How does intercompany stock transfer work in SAP?" |
| Design patterns | "What SAP approach should I use for make-to-order vs make-to-stock?" |

### Tips

- Mention the module when you know it for faster routing: *"In MM, how do I configure automatic account determination?"*
- Cross-module questions work too — the KB covers P2P, O2C, and R2R end to end
- Ask *"how confident is the KB on this?"* if content feels uncertain — each file has a frontmatter confidence level (high / medium / low)
- This KB works alongside your project `CLAUDE.md` files — both are loaded together

---

## What's Covered

| Module | Key Topics |
|---|---|
| **MM** — Materials Management | Purchase orders, goods receipt/issue, inventory management, vendor master, MRP, movement types, account determination (OBYC) |
| **SD** — Sales & Distribution | Sales orders, delivery, billing, pricing procedures, credit management, output (NACE), customer master |
| **FI** — Financial Accounting | General ledger (Classic GL + New GL), accounts payable, accounts receivable, asset accounting, bank accounting, period-end close |
| **CO** — Controlling | Cost centers, internal orders, profit centers, allocations, settlement, CO-FI integration, period-end sequence |
| **Cross-module** | Procure-to-Pay (P2P), Order-to-Cash (O2C), Record-to-Report (R2R), scenario playbooks, solution design patterns, month-end and year-end close checklists |
| **Reference** | Movement types, document types, posting keys, org structure |

---

## Scope & Confidence

This knowledge base covers **ECC 6.0 (Enhancement Packs 0–8)**. It is not a replacement for SAP Help Portal documentation — it is structured context optimized for Claude Code sessions.

Content files include a frontmatter `confidence` field:
- `high` — verified against SAP documentation or confirmed in live systems
- `medium` — standard practice, likely accurate but not independently verified
- `low` — needs verification before treating as authoritative

When answering questions, Claude will note the confidence level if relevant.

---

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: write full README with setup instructions and content map"
```

---

### Task 2: Set GitHub repo description

**Step 1: Set description via GitHub CLI**

```bash
gh repo edit BrandedTamarasu-glitch/SAPKnowledge \
  --description "SAP ECC 6.0 knowledge base for Claude Code — transaction codes, config paths, and process flows for MM, SD, FI, CO"
```

Expected: No output (success) or "✓ Edited repository BrandedTamarasu-glitch/SAPKnowledge"

---

### Task 3: Push all commits

**Step 1: Push to origin**

```bash
git push origin main
```

Expected: summary of commits pushed, no errors.

---

### Task 4: Tag and create v0.1.0 release

**Step 1: Create and push the tag**

```bash
git tag v0.1.0
git push origin v0.1.0
```

**Step 2: Create the GitHub release**

```bash
gh release create v0.1.0 \
  --title "v0.1.0 — Initial SAP ECC 6.0 Knowledge Base" \
  --notes "$(cat <<'EOF'
## Initial Release

This is the first structured release of the SAP ECC 6.0 Knowledge Base for Claude Code.

### What's Included

**MM — Materials Management**
- Transaction codes: purchasing, goods movements, inventory, vendor master
- Configuration: account determination (OBYC), movement type customization, MRP
- Processes: Procure-to-Pay end-to-end, goods receipt/invoice verification
- Integration: MM→FI account determination, MM→SD availability check

**SD — Sales & Distribution**
- Transaction codes: order management, delivery, billing, pricing
- Configuration: pricing procedures, output (NACE), credit management
- Processes: Order-to-Cash end-to-end
- Integration: SD→FI billing, SD→MM availability and goods issue

**FI — Financial Accounting**
- Transaction codes: GL, AP, AR, asset accounting, bank accounting
- Configuration: chart of accounts, document types, posting keys, fiscal year
- Processes: period-end close sequence, document parking and clearing
- Integration: FI↔CO reconciliation, FI←MM/SD automatic postings

**CO — Controlling**
- Transaction codes: cost centers, internal orders, profit centers, allocations, settlement
- Configuration: controlling area, cost element categories, settlement profiles
- Processes: period-end CO sequence, allocation cycles, order settlement
- Integration: CO↔FI integration catalog (21 scenarios across 3 directions)

**Cross-Module**
- End-to-end process playbooks: P2P, O2C, R2R
- 8 scenario playbooks: consignment, intercompany, third-party, subcontracting, split valuation, batch management, serial number, project stock
- 12 solution design patterns for common business requirements
- Month-end and year-end close checklists with T-codes and sequence

**Reference**
- Movement type catalog
- Document type and posting key tables
- Org structure reference

### Scope

ECC 6.0 (Enhancement Packs 0–8) only. S/4HANA differences are noted inline for disambiguation.

### Setup

See [README](README.md) for installation and usage instructions.
EOF
)"
```

Expected: URL of new release printed to terminal.

---
