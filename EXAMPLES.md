# SAP ECC 6 Knowledge Base — Code Examples

Runnable examples for querying the KB programmatically via Python (`kb_reader.py`) or the MCP server tools.

**Prerequisites:** Python 3.10+, dependencies installed (`pip install -r scripts/requirements.txt`), run from repo root.

---

## Example 1: Fetch the Complete Order-to-Cash Process Flow

Retrieves the full O2C process and extracts all SD-FI integration points.

```python
import sys
sys.path.insert(0, "scripts")

from kb_reader import get_file_body, find_section_by_topic, search_kb, PROCESS_FILE

# --- Step 1: Fetch the cross-module Order-to-Cash end-to-end flow ---
from pathlib import Path
from kb_reader import KB_ROOT, parse_frontmatter

o2c_path = KB_ROOT / "cross-module" / "order-to-cash.md"
_, o2c_body = parse_frontmatter(o2c_path)

print("=== Order-to-Cash Process Flow ===")
print(o2c_body[:3000])  # First 3000 chars — full flow is ~8000 chars

# --- Step 2: Extract the SD-FI integration section from the O2C flow ---
integration_section = find_section_by_topic(o2c_body, "integration")
if integration_section:
    print("\n=== SD-FI Integration Points (from O2C flow) ===")
    print(integration_section)

# --- Step 3: Get the dedicated SD-FI integration reference ---
sd_integration_path = KB_ROOT / "modules" / "sd" / "integration.md"
_, sd_integration_body = parse_frontmatter(sd_integration_path)

# Extract the FI-specific section
fi_section = find_section_by_topic(sd_integration_body, "FI")
if fi_section:
    print("\n=== SD → FI Integration Points (SD integration.md) ===")
    print(fi_section)

# --- Step 4: Keyword search across all KB files for "SD-FI" ---
results, total = search_kb("billing FI posting", max_results=5)
print(f"\n=== Keyword Search: 'billing FI posting' ({total}+ matches) ===")
for r in results:
    print(f"\n[{r['source']}] {r['heading']}")
    print(r['excerpt'])
    print(f"Source: {r['source']}")
```

**Output structure for `search_kb`:**
```python
[
    {
        "source": "modules/sd/integration.md",     # relative path from KB root
        "heading": "## SD-FI Integration Points",  # nearest parent heading
        "excerpt": "When VF01 posts a billing...", # 5-line context window
    },
    ...
]
```

---

## Example 2: Look Up a Transaction Code

```python
import sys
sys.path.insert(0, "scripts")

from kb_reader import get_file_body, extract_tcode_section, normalize_module, TCODE_FILE

def lookup_tcode(tcode: str, module: str) -> str:
    """Fetch the full reference entry for a T-code from the module's tcodes.md."""
    mod = normalize_module(module)
    if not mod:
        return f"Module '{module}' not in KB. Valid: MM, SD, FI, CO."

    body, source = get_file_body(TCODE_FILE, mod)
    section = extract_tcode_section(body, tcode)

    if not section:
        return f"T-code '{tcode.upper()}' not found in {mod} tcodes.md."

    return f"{section}\n\nSource: {source}"


# Examples
print(lookup_tcode("VF01", "SD"))   # Billing — Create Billing Document
print(lookup_tcode("MIGO", "MM"))   # Goods Movement
print(lookup_tcode("F-22", "FI"))   # AR — Enter Customer Invoice
print(lookup_tcode("KSB1", "CO"))   # Cost Center Actual Line Items
```

**Return value shape:**
```
### VF01 — Create Billing Document
**Module:** SD
**Menu Path:** Logistics → Sales and Distribution → Billing → Billing Document → Create
**Usage:** Creates billing documents from delivery or order references. Posts revenue to FI via VKOA.
**Gotcha:** ...

Source: modules/sd/tcodes.md
```

---

## Example 3: Get SPRO Configuration Steps by Topic

```python
import sys
sys.path.insert(0, "scripts")

from kb_reader import get_file_body, find_section_by_topic, normalize_module, CONFIG_FILE

def get_config_steps(module: str, topic: str) -> str:
    """Find SPRO/IMG configuration steps for a topic within a module."""
    mod = normalize_module(module)
    if not mod:
        return f"Module '{module}' not in KB."

    body, source = get_file_body(CONFIG_FILE, mod)
    section = find_section_by_topic(body, topic)

    if not section:
        return f"No config section matching '{topic}' found in {mod} config-spro.md."

    return f"{section}\n\nSource: {source}"


# Examples
print(get_config_steps("MM", "tolerance"))        # MM LIV tolerance keys
print(get_config_steps("FI", "payment terms"))    # FI payment terms config
print(get_config_steps("SD", "pricing procedure")) # SD pricing setup
print(get_config_steps("CO", "cost center"))       # CO cost center config
```

---

## Example 4: Extract All SD-FI Integration Points Programmatically

Full extraction pipeline — returns a structured list of every SD→FI integration touchpoint.

```python
import sys
import re
sys.path.insert(0, "scripts")

from pathlib import Path
from kb_reader import KB_ROOT, parse_frontmatter, search_kb

def extract_sd_fi_integration_points() -> list[dict]:
    """
    Extract all SD-FI integration points from the KB.

    Returns a list of dicts:
        {"title": str, "content": str, "source": str}
    """
    points = []

    # Source 1: SD integration.md — dedicated SD-FI integration catalog
    sd_int_path = KB_ROOT / "modules" / "sd" / "integration.md"
    if sd_int_path.exists():
        _, body = parse_frontmatter(sd_int_path)
        # Split into sections and find FI-related ones
        sections = re.split(r"(?=^#{2,3} )", body, flags=re.MULTILINE)
        for section in sections:
            heading_match = re.match(r"^#{2,3} (.+)", section)
            if heading_match:
                heading = heading_match.group(1)
                if any(kw in heading.upper() for kw in ["FI", "REVENUE", "BILLING", "POSTING", "ACCOUNT"]):
                    points.append({
                        "title": heading,
                        "content": section.strip(),
                        "source": "modules/sd/integration.md",
                    })

    # Source 2: Cross-module O2C flow — integration sections
    o2c_path = KB_ROOT / "cross-module" / "order-to-cash.md"
    if o2c_path.exists():
        _, body = parse_frontmatter(o2c_path)
        sections = re.split(r"(?=^#{2,3} )", body, flags=re.MULTILINE)
        for section in sections:
            heading_match = re.match(r"^#{2,3} (.+)", section)
            if heading_match:
                heading = heading_match.group(1)
                if any(kw in heading.upper() for kw in ["FI", "INTEGRATION", "POSTING", "ACCOUNT"]):
                    points.append({
                        "title": heading,
                        "content": section.strip(),
                        "source": "cross-module/order-to-cash.md",
                    })

    # Source 3: Keyword search for any additional mentions
    results, _ = search_kb("SD FI integration posting", max_results=10)
    for r in results:
        if r["source"] not in {p["source"] for p in points}:
            points.append({
                "title": r["heading"],
                "content": r["excerpt"],
                "source": r["source"],
            })

    return points


# Run it
integration_points = extract_sd_fi_integration_points()
print(f"Found {len(integration_points)} SD-FI integration point sections:\n")
for p in integration_points:
    print(f"  [{p['source']}] {p['title']}")

# Print the first one in full
if integration_points:
    print(f"\n--- First result ---\n{integration_points[0]['content'][:800]}")
```

---

## Example 5: MCP Tool Calls via fastmcp Client

Use these if you're calling the server programmatically (e.g., from a test harness or another Python process) rather than through Claude.

```python
# Requires: pip install fastmcp
# Server must be running: .venv/bin/python scripts/mcp_server.py

import asyncio
from fastmcp import Client

async def query_sap_kb():
    async with Client("scripts/mcp_server.py") as client:

        # List all available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])
        # → ['lookup_tcode', 'get_module_overview', 'get_config_path',
        #    'get_process_flow', 'compare_ecc_s4', 'search_by_keyword']

        # Fetch Order-to-Cash process flow
        o2c = await client.call_tool("get_process_flow", {
            "module": "SD",
            "process": "order to cash"
        })
        print("\n=== O2C Process Flow ===")
        print(o2c.content[0].text[:1000])

        # Look up a T-code
        vf01 = await client.call_tool("lookup_tcode", {"tcode": "VF01"})
        print("\n=== VF01 ===")
        print(vf01.content[0].text)

        # Keyword search for SD-FI integration
        results = await client.call_tool("search_by_keyword", {
            "query": "billing document FI posting"
        })
        print("\n=== Search Results ===")
        print(results.content[0].text[:1500])

        # Compare ECC 6 vs S/4HANA for billing
        diff = await client.call_tool("compare_ecc_s4", {"topic": "output management"})
        print("\n=== ECC vs S/4 ===")
        print(diff.content[0].text)

asyncio.run(query_sap_kb())
```

---

## Key Files for Order-to-Cash + SD-FI Integration

| File | Contents |
|------|----------|
| `cross-module/order-to-cash.md` | Full O2C end-to-end process flow (SD → FI touchpoints) |
| `modules/sd/integration.md` | SD-FI integration point catalog (14 touchpoints, VF01→FI trace, VKOA) |
| `modules/sd/processes.md` | SD process flows: standard O2C, returns, billing cycles |
| `modules/fi/account-determination.md` | VKOA account determination framework (revenue account mapping) |
| `modules/sd/config-spro.md` | SPRO config for pricing, copy control, billing types |
| `cross-module/design-patterns.md` | Solution patterns including intercompany, third-party O2C variants |

All files use YAML frontmatter. Access with `parse_frontmatter(path)` → returns `(metadata_dict, body_str)`.

---

## Example 6: FI Account Determination — OBYC Transaction Key Lookup

Traces a goods movement to its GL accounts via the OBYC framework. Shows how to load the FI account determination file, query specific transaction keys, and handle missing sections gracefully.

```python
import sys
sys.path.insert(0, "scripts")

from pathlib import Path
from kb_reader import KB_ROOT, parse_frontmatter, find_section_by_topic, search_kb

# --- Load FI account determination file ---
acct_det_path = KB_ROOT / "modules" / "fi" / "account-determination.md"
meta, acct_det_body = parse_frontmatter(acct_det_path)
print(f"Confidence: {meta.get('confidence', 'unknown')}")  # e.g. "medium"


def get_obyc_framework() -> str:
    """Return the full OBYC determination chain explanation."""
    section = find_section_by_topic(acct_det_body, "OBYC Framework")
    if section is None:
        return "OBYC framework section not found in account-determination.md."
    return section


def get_transaction_key_info(key: str) -> str:
    """
    Look up a specific OBYC transaction key (BSX, GBB, WRX, PRD, etc.).
    Falls back to keyword search across all KB files if section lookup misses.
    """
    # Try direct section match first (fast path)
    section = find_section_by_topic(acct_det_body, key)
    if section:
        return section

    # Fall back to keyword search (broader — catches mentions across modules)
    results, total = search_kb(f"OBYC {key} account determination", max_results=5)
    if not results:
        return f"No KB content found for transaction key '{key}'."

    lines = [f"Keyword search for '{key}' ({total}+ matches across KB):\n"]
    for r in results:
        lines.append(f"[{r['source']}] {r['heading']}")
        lines.append(r['excerpt'])
        lines.append("")
    return "\n".join(lines)


def get_movement_type_posting(movement_type: str) -> str:
    """
    Explain which OBYC transaction keys fire for a given movement type.
    Movement types: 101 (GR vs PO), 261 (GI to production), 551 (scrapping), etc.
    """
    # Account determination file has worked examples per movement type
    section = find_section_by_topic(acct_det_body, f"Movement Type {movement_type}")
    if section:
        return section

    # Try searching by movement type number alone
    section = find_section_by_topic(acct_det_body, movement_type)
    if section:
        return section

    # Broader keyword search across MM files
    results, _ = search_kb(f"movement type {movement_type} GL account posting", max_results=5)
    if not results:
        return f"No posting details found for movement type {movement_type}."

    lines = [f"Results for movement type {movement_type}:\n"]
    for r in results:
        lines.append(f"[{r['source']}] {r['heading']}: {r['excerpt'][:200]}")
    return "\n".join(lines)


# Run examples
print("=== OBYC Framework ===")
print(get_obyc_framework()[:1500])

print("\n=== GBB Transaction Key ===")
print(get_transaction_key_info("GBB"))

print("\n=== Movement Type 261 — GI to Production ===")
print(get_movement_type_posting("261"))

print("\n=== Movement Type 101 — GR vs PO ===")
print(get_movement_type_posting("101"))
```

**Transaction key reference (from `account-determination.md`):**

| Key | Purpose | Account Modifier? |
|-----|---------|-------------------|
| BSX | Inventory balance sheet account (GR) | No — valuation class only |
| WRX | GR/IR clearing account | No — valuation class only |
| PRD | Price difference (standard price materials only) | Optional |
| GBB | Consumption/COGS/scrapping offsetting entries | Yes — VBR, VNG, VAX, VAY, etc. |

---

## Example 7: FI Account Determination Troubleshooting — Chained SPRO Lookups

Implements a full troubleshooting workflow by chaining multiple KB queries: symptom identification → account determination logic → SPRO configuration path → resolution steps.

```python
import sys
sys.path.insert(0, "scripts")

from pathlib import Path
from kb_reader import KB_ROOT, parse_frontmatter, find_section_by_topic, get_file_body, CONFIG_FILE

# Pre-load the FI files we'll chain through
acct_det_path = KB_ROOT / "modules" / "fi" / "account-determination.md"
_, acct_det_body = parse_frontmatter(acct_det_path)

fi_advanced_path = KB_ROOT / "modules" / "fi" / "fi-advanced.md"
_, fi_advanced_body = parse_frontmatter(fi_advanced_path)

fi_config_body, fi_config_source = get_file_body(CONFIG_FILE, "FI")


def diagnose_missing_gl_account(scenario: str) -> dict:
    """
    Troubleshoot a missing GL account determination error.

    scenario: description of the posting that failed, e.g.
        "GI to production order — no GL account found for GBB/VBR"
        "GR against PO — BSX not posting to inventory account"
        "F110 payment proposal missing vendor items"

    Returns a structured diagnosis dict with:
        - account_det_logic: how the determination works
        - spro_config_path: where to configure the fix in SPRO
        - resolution_steps: step-by-step fix instructions
    """
    result = {}

    # Step 1: Account determination logic (how it should work)
    # Search for relevant transaction key info based on scenario keywords
    for key in ["GBB", "BSX", "WRX", "PRD", "VKOA"]:
        if key.lower() in scenario.lower():
            section = find_section_by_topic(acct_det_body, key)
            if section:
                result["account_det_logic"] = section
                break
    # Generic fallback: return the OBYC framework overview
    if "account_det_logic" not in result:
        fallback = find_section_by_topic(acct_det_body, "OBYC Framework")
        result["account_det_logic"] = fallback or "See modules/fi/account-determination.md"

    # Step 2: SPRO config path — where to fix it
    # FI config-spro.md has FBZP, payment terms, tolerance groups, AA steps
    # OBYC itself is MM-side config — check MM config for the actual OBYC entries
    mm_config_body, mm_config_source = get_file_body(CONFIG_FILE, "MM")
    mm_config_section = find_section_by_topic(mm_config_body, "account determination")
    if mm_config_section:
        result["spro_config_path"] = f"{mm_config_section}\n\nSource: {mm_config_source}"
    else:
        # OBYC is not in FI SPRO — provide direct T-code guidance
        result["spro_config_path"] = (
            "OBYC configuration: T-code OBYC\n"
            "  → Select transaction key (e.g. GBB)\n"
            "  → New Entries: Chart of Accounts + Account Modifier + Valuation Class → GL Account\n"
            "For GBB/VBR (production consumption): add entry per valuation class with modifier VBR.\n"
            "For BSX (inventory): add entry per valuation class (no modifier)."
        )

    # Step 3: Resolution steps from fi-advanced.md troubleshooting symptoms
    # Check for known symptom patterns
    symptom_keywords = {
        "balance": "Balance Sheet Does Not Balance",
        "period": "Posting Period Not Open",
        "f110": "F110 Payment Proposal",
        "vendor": "F110 Payment Proposal Does Not Pick Up",
        "bank": "F110 Bank Account Not Selected",
        "splitting": "GLT2201",
        "depreciation": "AJAB Fails",
        "fs10n": "FS10N Shows Zero",
    }
    resolution = None
    scenario_lower = scenario.lower()
    for kw, symptom_heading in symptom_keywords.items():
        if kw in scenario_lower:
            resolution = find_section_by_topic(fi_advanced_body, symptom_heading)
            if resolution:
                break

    # Generic fallback: return the pitfall for missing OBYC entries
    if resolution is None:
        resolution = find_section_by_topic(fi_advanced_body, "Pitfall")

    result["resolution_steps"] = resolution or "See modules/fi/fi-advanced.md troubleshooting section."

    return result


# --- Example 1: GI to production order — GBB/VBR missing ---
print("=== Scenario: GI to production — GBB/VBR not configured ===\n")
diagnosis = diagnose_missing_gl_account("GI to production order — GBB VBR no GL account found")

print("ACCOUNT DETERMINATION LOGIC:")
print(diagnosis["account_det_logic"][:600])
print("\nSPRO CONFIG PATH:")
print(diagnosis["spro_config_path"][:400])
print("\nRESOLUTION STEPS:")
print(diagnosis["resolution_steps"][:600])


# --- Example 2: F110 payment run — items not picked up ---
print("\n\n=== Scenario: F110 vendor payment items missing from proposal ===\n")
diagnosis2 = diagnose_missing_gl_account("F110 payment proposal missing vendor items")

print("RESOLUTION STEPS:")
print(diagnosis2["resolution_steps"][:800])


# --- Example 3: Raw SPRO path lookup — asset accounting GL accounts ---
print("\n\n=== FI SPRO: Asset Accounting GL Account Assignment (AO90) ===")
ao90_section = find_section_by_topic(fi_config_body, "AO90")
if ao90_section:
    print(ao90_section[:600])
else:
    print("AO90 section not found — trying 'G/L Account Determination'...")
    fallback = find_section_by_topic(fi_config_body, "G/L Account")
    print(fallback[:600] if fallback else "Not found in FI config-spro.md.")
print(f"\nSource: {fi_config_source}")
```

**Chaining pattern summary:**

```
Symptom
  → find_section_by_topic(acct_det_body, transaction_key)   # how it works
      → find_section_by_topic(config_body, "account determination")  # where to configure
          → find_section_by_topic(advanced_body, symptom_keyword)     # how to fix it
```

Each step has a `None` fallback so the chain never silently fails — callers always get actionable content or a clear "not found" message.

---

## Example 8: MCP Tool Calls for FI Account Determination

Use the MCP server to navigate FI account determination configuration via the `get_config_path` and `search_by_keyword` tools. Includes response parsing for structured extraction.

```python
# Requires: pip install fastmcp
# Server starts automatically when Client() opens

import asyncio
import re
from fastmcp import Client


async def query_fi_account_determination():
    async with Client("scripts/mcp_server.py") as client:

        # --- 1. Get the SPRO path for FI automatic postings (OBYC, OBA1, OBXU) ---
        config_result = await client.call_tool("get_config_path", {
            "module": "FI",
            "topic": "automatic postings"
        })
        config_text = config_result.content[0].text
        print("=== FI Automatic Postings SPRO Path ===")
        print(config_text[:1200])

        # --- 2. Search for GBB account modifier reference ---
        gbb_results = await client.call_tool("search_by_keyword", {
            "query": "GBB account modifier VBR production consumption"
        })
        gbb_text = gbb_results.content[0].text

        # Parse the structured search response
        # Response format: "Found N results for '...'\n\n[source] heading\nexcerpt\n---"
        result_blocks = re.split(r"\n---+\n", gbb_text)
        print(f"\n=== GBB Search: {len(result_blocks)} result blocks ===")
        for block in result_blocks[:3]:  # show first 3
            lines = block.strip().splitlines()
            if lines:
                print(f"\n  {lines[0]}")          # [source] heading
                print(f"  {lines[1][:150]}..." if len(lines) > 1 else "")

        # --- 3. Get the FI AP payment run process (includes F110 sequence) ---
        f110_process = await client.call_tool("get_process_flow", {
            "module": "FI",
            "process": "AP payment run"
        })
        f110_text = f110_process.content[0].text

        # Extract just the summary table rows
        table_rows = []
        in_table = False
        for line in f110_text.splitlines():
            if line.startswith("| Step") or line.startswith("|---"):
                in_table = True
            if in_table and line.startswith("|"):
                table_rows.append(line)
            elif in_table and not line.startswith("|"):
                break  # end of table

        print("\n=== F110 Payment Run — Step Summary ===")
        print("\n".join(table_rows[:10]))  # first 10 rows

        # --- 4. Look up OBYC T-code entry ---
        obyc_tcode = await client.call_tool("lookup_tcode", {"tcode": "FBZP"})
        print("\n=== FBZP T-code (F110 prerequisite configuration) ===")
        print(obyc_tcode.content[0].text[:600])

        # --- 5. Compare ECC 6 vs S/4HANA for account determination ---
        s4_diff = await client.call_tool("compare_ecc_s4", {
            "topic": "vendor master"
        })
        print("\n=== ECC vs S/4 — Vendor Master Differences ===")
        print(s4_diff.content[0].text[:500])


asyncio.run(query_fi_account_determination())
```

**Parsing the `search_by_keyword` response:**

```python
# Response text structure:
# "Found 8 results for 'GBB account modifier'
#
# [modules/fi/account-determination.md] GBB Account Modifier Reference
# GBB is the most important transaction key for goods issue postings...
# ---
# [modules/mm/integration.md] MM-FI Account Determination
# ..."

def parse_search_response(text: str) -> list[dict]:
    """Parse search_by_keyword MCP response into structured list."""
    blocks = re.split(r"\n---+\n", text)
    results = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # First line: [source] heading
        first_line_match = re.match(r"\[(.+?)\]\s+(.+)", block)
        if first_line_match:
            source = first_line_match.group(1)
            heading = first_line_match.group(2)
            excerpt = block[first_line_match.end():].strip()
            results.append({"source": source, "heading": heading, "excerpt": excerpt})
    return results
```

---

---

## Example 9: CO Month-End Close — Extract and Look Up All Required T-codes

Parses the CO period-end closing sequence from `processes.md`, extracts every T-code (including composite entries like `KSU5/KSV5` and `OKP1 / COPI`), looks each one up in `tcodes.md` for menu path, usage, and gotchas, and falls back to `search_kb` for T-codes without a dedicated entry.

```python
import sys
import re
sys.path.insert(0, "scripts")

from kb_reader import (
    get_file_body, find_section_by_topic, extract_tcode_section,
    search_kb, TCODE_FILE, PROCESS_FILE,
)

# --- Step 1: Load CO process and T-code files ---
process_body, process_source = get_file_body(PROCESS_FILE, "CO")
tcode_body,   tcode_source   = get_file_body(TCODE_FILE,   "CO")


# --- Step 2: Locate the period-end closing sequence section ---
close_section = find_section_by_topic(process_body, "Period-End CO Closing Sequence")
if close_section is None:
    raise ValueError("Month-end close section not found in modules/co/processes.md")


# --- Step 3: Parse the sequence table ---
# Table columns: Step | Activity | T-code | Purpose | Dependencies
TABLE_ROW_RE = re.compile(
    r"^\|\s*([^|\-][^|]*?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
    re.MULTILINE,
)

steps = []
for match in TABLE_ROW_RE.finditer(close_section):
    step_raw, activity, tcode_raw, purpose, dependencies = match.groups()
    step = step_raw.strip()
    # Skip header and separator rows
    if step.lower() == "step" or not step:
        continue
    steps.append({
        "step":         step,
        "activity":     activity.strip(),
        "tcode_raw":    tcode_raw.strip(),
        "purpose":      purpose.strip(),
        "dependencies": dependencies.strip(),
    })


# --- Step 4: Normalize T-codes (split "KSU5/KSV5", "OKP1 / COPI", etc.) ---
def split_tcodes(raw: str) -> list[str]:
    """
    Split composite T-code strings into a clean list.
    Handles: "KSU5/KSV5"  "OKP1 / COPI"  "KKAX/KKA2"  "KO88"
    """
    # Split on whitespace, slash, or comma
    parts = re.split(r"[\s/,]+", raw)
    # Keep only valid T-code-shaped tokens (2–8 uppercase alphanum chars)
    return [p.strip().upper() for p in parts if re.match(r"^[A-Z0-9_]{2,10}$", p.strip())]


# --- Step 5: Look up each T-code with a graceful fallback ---
def lookup_tcode_details(tcode: str) -> dict:
    """
    Primary:  extract_tcode_section() on CO tcodes.md.
    Fallback: search_kb() across all KB files.
    Returns a dict with tcode, found, menu_path, usage, gotcha, source.
    """
    base = {"tcode": tcode, "menu_path": "", "usage": "", "gotcha": ""}

    # --- Primary: dedicated tcodes.md entry ---
    section = extract_tcode_section(tcode_body, tcode)
    if section:
        for line in section.splitlines():
            if line.startswith("**Menu Path:**"):
                base["menu_path"] = line.replace("**Menu Path:**", "").strip()
            elif line.startswith("**Usage:**"):
                base["usage"] = line.replace("**Usage:**", "").strip()
            elif line.startswith("**Gotcha:**"):
                base["gotcha"] = line.replace("**Gotcha:**", "").strip()
        return {**base, "found": True, "source": tcode_source}

    # --- Fallback: keyword search ---
    results, _ = search_kb(f"{tcode} CO controlling period-end", max_results=3)
    if results:
        r = results[0]
        return {
            **base,
            "found":     True,
            "usage":     r["excerpt"][:200],
            "menu_path": "(found via search — no dedicated tcode entry)",
            "source":    r["source"],
        }

    return {**base, "found": False, "source": ""}


# --- Step 6: Build the enriched close checklist ---
def build_close_checklist() -> list[dict]:
    """
    Returns every CO month-end close step enriched with full T-code details.
    """
    checklist = []
    for step in steps:
        tcodes = split_tcodes(step["tcode_raw"])
        checklist.append({
            **step,
            "tcodes": [lookup_tcode_details(t) for t in tcodes],
        })
    return checklist


# === Run and print ===
checklist = build_close_checklist()

# Summary table
print(f"{'Step':<5}  {'T-code(s)':<22}  {'Activity':<34}  {'KB?'}")
print("-" * 70)
for item in checklist:
    tcode_str = " / ".join(t["tcode"] for t in item["tcodes"])
    kb_flag   = "✓" if all(t["found"] for t in item["tcodes"]) else "?"
    print(f"{item['step']:<5}  {tcode_str:<22}  {item['activity'][:33]:<34}  {kb_flag}")

# Full T-code reference
print("\n" + "=" * 70)
print("CO MONTH-END CLOSE — FULL T-CODE REFERENCE")
print("=" * 70)

for item in checklist:
    print(f"\n── Step {item['step']}: {item['activity']}")
    print(f"   Purpose:      {item['purpose']}")
    print(f"   Depends on:   {item['dependencies']}")
    for t in item["tcodes"]:
        if t["found"]:
            print(f"\n   {t['tcode']}")
            print(f"   Menu:    {t['menu_path'] or '(not in KB)'}")
            print(f"   Usage:   {t['usage'][:120] or '(not in KB)'}")
            if t["gotcha"]:
                print(f"   ⚠ Note:  {t['gotcha'][:120]}")
            print(f"   Source:  {t['source']}")
        else:
            print(f"\n   {t['tcode']}  ⚠ Not found in KB — verify manually")
```

**Expected summary output:**
```
Step   T-code(s)               Activity                             KB?
----------------------------------------------------------------------
1      KB61                    Repost CO line items                  ✓
2      KGI2                    Calculate actual overhead             ✓
3      KSU5                    Run assessment cycles                 ✓
4      KSV5                    Run distribution cycles               ✓
5      KO88                    Settle internal orders                ✓
6      CO88                    Settle production orders              ✓
6a     KKAX / KKA2             WIP/Results analysis                  ?
7      KSII                    Calculate actual activity prices      ✓
8      1KEG                    Transfer pricing (PCA)                ?
9      OKP1 / COPI             Lock CO period                        ?
```

T-codes marked `?` are not in CO `tcodes.md` but are found via `search_kb` fallback — the code still returns useful context from whichever KB file mentions them.

**Using the MCP server instead (equivalent queries via fastmcp client):**

```python
import asyncio
from fastmcp import Client

async def get_co_close_tcodes_via_mcp():
    async with Client("scripts/mcp_server.py") as client:

        # Get the full CO period-end process (includes the sequence table)
        process_result = await client.call_tool("get_process_flow", {
            "module": "CO",
            "process": "period-end close"
        })
        process_text = process_result.content[0].text
        print("=== CO Period-End Sequence ===")
        print(process_text[:2000])

        # Look up core period-end T-codes individually for full details
        core_tcodes = ["KB61", "KGI2", "KSU5", "KSV5", "KO88", "CO88", "KSII"]
        for tcode in core_tcodes:
            result = await client.call_tool("lookup_tcode", {"tcode": tcode})
            text = result.content[0].text
            # Extract just the first 3 lines (heading + usage)
            summary = "\n".join(text.splitlines()[:4])
            print(f"\n── {tcode}\n{summary}")

        # Search for less common close T-codes not in tcodes.md
        for tcode in ["KKAX", "1KEG", "COPI"]:
            results = await client.call_tool("search_by_keyword", {
                "query": f"{tcode} CO period-end controlling"
            })
            text = results.content[0].text
            # First result line is the source and heading
            first_line = text.strip().splitlines()[0] if text.strip() else "No results"
            print(f"\n── {tcode} (search fallback): {first_line}")

asyncio.run(get_co_close_tcodes_via_mcp())
```

---

## Key Files for CO Month-End Close

| File | Contents |
|------|----------|
| `modules/co/processes.md` | CO business process flows including the **9-step period-end closing sequence** (KB61 → KGI2 → KSU5/KSV5 → KO88/CO88 → KSII → lock) with dependency rules |
| `modules/co/tcodes.md` | ~63 CO T-codes: KB61, KGI2, KSU5, KSV5, KO88, CO88, KSII and all master data / reporting T-codes with menu paths, usage, gotchas |
| `modules/co/co-advanced.md` | 10 troubleshooting symptoms for period-end failures (zero allocations, missing settlement rules, KE5Z vs FI reconciliation gaps) |
| `modules/co/integration.md` | CO-FI integration catalog: which CO T-codes create FI documents (only KO88 with KST/FXA receiver and KALC); CO-internal-only T-codes (no FI impact) |
| `cross-module/record-to-report.md` | Full R2R end-to-end close sequence: FI period-end → MM period-end → CO period-end with cross-module timing dependencies |

---

## Key Files for FI Account Determination

| File | Contents |
|------|----------|
| `modules/fi/account-determination.md` | OBYC framework, GBB modifiers (VBR/VNG/VAX/VAY), VKOA/KOFI for SD revenue, OBA1/OBXU/OBXI for FI-only postings |
| `modules/fi/config-spro.md` | SPRO paths: FBZP (F110 config), payment terms (OBB8), asset accounting (EC08→OAOB→OAOA→AO90→AFAMA) |
| `modules/fi/fi-advanced.md` | 7 decision trees + 7 pitfalls + 7 troubleshooting symptoms (F110, AJAB, GLT2201, FS10N zero balances) |
| `modules/fi/processes.md` | Business process flows: GL posting cycle, month-end close, F110 payment run, financial reporting |
| `modules/mm/account-determination.md` | MM-side OBYC setup detail (valuation class, movement type configuration) |
| `cross-module/order-to-cash.md` | End-to-end O2C flow including SD → FI posting touchpoints |
