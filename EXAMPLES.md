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
