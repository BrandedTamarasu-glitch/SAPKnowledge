# scripts/mcp_server.py
# SAP ECC 6 Knowledge Base MCP server — five read-only query tools.
# Transport: stdio (default for FastMCP 3.x mcp.run() with no args).
# Invocation: .venv/bin/python scripts/mcp_server.py
# DO NOT use print() — stdout is the MCP protocol wire.

import sys
from pathlib import Path

# Ensure scripts/ is on sys.path so kb_reader is importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastmcp import FastMCP
from kb_reader import (
    normalize_module,
    get_file_body,
    extract_tcode_section,
    find_section_by_topic,
    extract_disambiguation_rows,
    parse_frontmatter,
    search_kb,           # Phase 14: keyword search helper
    KB_ROOT,
    TCODE_FILE,
    OVERVIEW_FILE,
    CONFIG_FILE,
    PROCESS_FILE,
    DISAMBIGUATION_FILE,
)

mcp = FastMCP("SAP ECC 6 Knowledge Base")


@mcp.tool
def lookup_tcode(tcode: str) -> str:
    """Use this tool ONLY when the user asks about a specific SAP transaction
    code by name (e.g., 'ME21N', 'MIGO', 'VF01', 'FB50'). Do not use for
    general questions about SAP processes, configuration steps, or module
    overviews — use the appropriate specialized tool for those."""
    normalized = tcode.strip().upper()
    for module in ["MM", "SD", "FI", "CO"]:
        body, source = get_file_body(TCODE_FILE, module)
        section = extract_tcode_section(body, normalized)
        if section:
            return f"{section}\n\nSource: {source}"
    return (
        f"T-code {normalized} not found in this KB. "
        f"This KB covers MM, SD, FI, and CO transactions only. "
        f"PM, QM, PP, WM, and other modules are not included."
    )


@mcp.tool
def get_module_overview(module: str) -> str:
    """Use this tool ONLY when the user asks what topics, files, or content
    are available for a specific SAP module (MM, SD, FI, or CO), or asks
    for a module orientation (e.g., 'what does the MM KB cover?', 'show me
    the FI module index'). Do not use for specific T-code lookups or
    configuration step retrieval."""
    mod = normalize_module(module)
    if not mod:
        return (
            f"Module '{module}' is not covered in this KB. "
            f"Only MM (Materials Management), SD (Sales & Distribution), "
            f"FI (Financial Accounting), and CO (Controlling) are available."
        )
    body, source = get_file_body(OVERVIEW_FILE, mod)
    return f"{body.strip()}\n\nSource: {source}"


@mcp.tool
def get_config_path(module: str, topic: str) -> str:
    """Use this tool ONLY when the user asks for SPRO/IMG configuration steps,
    configuration paths, or how to configure a specific SAP setting (e.g.,
    'how do I configure tolerance keys in MM?', 'what is the IMG path for
    payment terms?'). Requires both a module (MM/SD/FI/CO) and a topic
    describing the configuration area."""
    mod = normalize_module(module)
    if not mod:
        return (
            f"Module '{module}' is not covered in this KB. "
            f"Only MM, SD, FI, and CO are available."
        )
    body, source = get_file_body(CONFIG_FILE, mod)
    section = find_section_by_topic(body, topic)
    if section:
        return f"{section}\n\nSource: {source}"
    return (
        f"No exact match for topic '{topic}' in {mod} SPRO configuration. "
        f"Try rephrasing the topic (e.g., use a keyword from the config area name). "
        f"Full configuration reference: {source}"
    )


@mcp.tool
def get_process_flow(module: str, process: str) -> str:
    """Use this tool ONLY when the user asks for a step-by-step SAP business
    process flow or process sequence (e.g., 'procure-to-pay steps', 'how does
    F110 payment run work', 'period-end close sequence for CO'). Requires both
    a module (MM/SD/FI/CO) and a process name or description. Do not use for
    single T-code lookups or SPRO configuration paths."""
    mod = normalize_module(module)
    if not mod:
        return (
            f"Module '{module}' is not covered in this KB. "
            f"Only MM, SD, FI, and CO are available."
        )
    body, source = get_file_body(PROCESS_FILE, mod)
    section = find_section_by_topic(body, process)
    if section:
        return f"{section}\n\nSource: {source}"
    return (
        f"No exact match for process '{process}' in {mod}. "
        f"Try rephrasing the process name (e.g., use keywords like 'payment run', "
        f"'goods receipt', 'period-end'). "
        f"Full process reference: {source}"
    )


@mcp.tool
def compare_ecc_s4(topic: str) -> str:
    """Use this tool ONLY when the user explicitly asks about differences between
    SAP ECC 6 and S/4HANA for a specific topic or feature (e.g., 'how does vendor
    master differ in S/4HANA?', 'ECC vs S/4 for material documents'). Do not use
    for general ECC 6 questions — this tool only returns ECC 6 vs S/4HANA comparison
    rows from the disambiguation table."""
    source = DISAMBIGUATION_FILE
    _, body = parse_frontmatter(KB_ROOT / source)
    rows = extract_disambiguation_rows(body, topic)
    if rows:
        return f"{rows}\n\nSource: {source}"
    return (
        f"No comparison data found for topic '{topic}'. "
        f"Available topics include: vendor master, customer master, material documents, "
        f"material ledger, general ledger, document splitting, cost of goods sold, "
        f"reporting, UI, credit management, output management, MRP, controlling area, "
        f"cost elements, profit center accounting, segment reporting, business area. "
        f"Source: {source}"
    )


@mcp.tool
def search_by_keyword(query: str) -> str:
    """Use this tool ONLY when the user asks a general SAP ECC 6 question that
    cannot be answered by any of the specific tools: lookup_tcode (for T-code
    names), get_config_path (for SPRO/IMG configuration), get_process_flow (for
    step-by-step business processes), get_module_overview (for module content
    index), or compare_ecc_s4 (for ECC vs S/4HANA differences). Use
    search_by_keyword as a last-resort fallback when the query is open-ended —
    for example: 'what is GR/IR clearing?', 'find content about tolerance keys',
    'show me everything about consignment stock'. Do NOT use for specific T-code
    lookups or SPRO path queries — use the specialized tools for those."""
    if not query.strip():
        return (
            "Please provide a keyword or phrase to search. "
            "Example: 'GR/IR clearing', 'tolerance keys', 'consignment stock'."
        )

    results, total = search_kb(query.strip())

    if not results:
        return (
            f"No results found for '{query}' in the SAP ECC 6 KB. "
            f"This KB covers MM, SD, FI, CO modules and cross-module processes. "
            f"Try rephrasing with a key term (T-code, config path, or process name). "
            f"For T-code lookup: use lookup_tcode. For SPRO paths: use get_config_path."
        )

    parts = []
    for r in results:
        section = f"{r['heading']}\n\n{r['excerpt']}\n\nSource: {r['source']}"
        parts.append(section)

    output = "\n\n---\n\n".join(parts)

    if total > len(results):
        output += (
            f"\n\n---\n\nShowing {len(results)} of {total}+ matches. "
            f"Refine your query for more targeted results."
        )

    return output


if __name__ == "__main__":
    mcp.run()
