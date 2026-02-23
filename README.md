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

Claude Code automatically loads all `.md` files under `~/.claude/rules/` as global rules — no additional configuration needed.

### Step 3 — Verify it's loading

Open Claude Code in any project and run `/config`. Look for the rule file listed under **Global rules**. Alternatively, ask Claude: *"Do you have a global rule about SAP?"* — it should confirm the knowledge base is active.

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

## MCP Server (Claude Code + Claude Desktop)

The knowledge base also works as an MCP server — Claude can query it directly as a tool, rather than reading markdown files. This enables lower-context usage and works in Claude Desktop as well as Claude Code.

See [SETUP.md](SETUP.md) for step-by-step setup instructions (Python required; 10–15 minutes; no coding needed).

**Available MCP tools:**

| Tool | What it does |
|---|---|
| `lookup_tcode` | Full entry for a known T-code (menu path, usage, gotchas) |
| `get_module_overview` | File index and key concepts for a module |
| `get_config_path` | SPRO/IMG configuration path for a topic |
| `get_process_flow` | Step-by-step business process flow |
| `compare_ecc_s4` | ECC 6 vs S/4HANA differences for a topic |
| `search_by_keyword` | Full-text search across all KB files |

---

## Programmatic API

The KB ships with a Python library (`scripts/kb_reader.py`) for direct programmatic access — useful for building tools, running batch queries, or integrating the KB into an application.

```python
import sys
sys.path.insert(0, "scripts")

from kb_reader import (
    KB_ROOT,             # Path: repo root
    get_file_body,       # load any KB file body by module + template name
    parse_frontmatter,   # read YAML frontmatter + body from a file
    find_section_by_topic,   # locate a section by heading keyword
    extract_tcode_section,   # pull a complete T-code entry
    search_kb,           # full-text keyword search across all files
)

# Example: get the SPRO path for OBYC in MM
body, source = get_file_body("config-spro", "MM")
section = find_section_by_topic(body, "OBYC")
print(section)
```

See [EXAMPLES.md](EXAMPLES.md) for 17 runnable examples covering common integration patterns.

---

## Code Examples

[EXAMPLES.md](EXAMPLES.md) contains 17 runnable Python examples demonstrating how to query the KB programmatically and via MCP:

| Example | What it demonstrates |
|---|---|
| 1 | Fetch the complete Order-to-Cash process flow |
| 2 | Look up a transaction code |
| 3 | Get SPRO configuration steps by topic |
| 4 | Extract all SD-FI integration points programmatically |
| 5 | MCP tool calls via `fastmcp` client |
| 6 | FI account determination — OBYC transaction key lookup |
| 7 | FI account determination troubleshooting — chained SPRO lookups |
| 8 | MCP tool calls for FI account determination |
| 9 | CO month-end close — extract and look up all required T-codes |
| 10 | Internal order settlement — query and validate process flow |
| 11 | Design patterns with SPRO configuration paths |
| 12 | MM account determination failure — query construction and diagnosis |
| 13 | Confidence levels and ECC 6 vs S/4HANA handling |
| 14 | Query routing — module detection, intent classification, tool prioritization |
| 15 | Fallback strategy for out-of-scope queries |
| 16 | T-code discovery by functional description |
| 17 | FI SPRO account determination — KB structure, helper contracts, full error handling |

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
