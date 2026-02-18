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
