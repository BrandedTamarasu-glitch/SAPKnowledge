# Phase 15: Deployment Documentation - Research

**Researched:** 2026-02-23
**Domain:** MCP server setup documentation for non-developer end users
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Audience & tone**
- Primary reader: business analyst / SAP consultant — comfortable with SAP GUI, not with terminals or Python
- Tone: friendly explainer with brief "why" at each stage
- Inline warning callout blocks for warnings and risky steps

**Guide structure & format**
- File: SETUP.md at repo root
- Top-level: TL;DR overview first, then two main sections: Claude Code + Claude Desktop
- Platform subsections (### macOS / ### Windows / ### Linux) within Claude Desktop
- All three platforms covered

**Platform & prerequisite depth**
- Nothing assumed — starts from Python install check
- Most-common-form commands (macOS/Linux), warning callout when Windows differs
- Inline warning notes at risky steps

**Verification step design**
- "Working" = server responds to a real test query
- Show expected output with each verification command
- End with: "Try asking: What does T-code MIGO do?"

### Claude's Discretion
- Exact placement of verification step(s)
- How to handle repo clone step
- Exact wording of "why" explanations

### Deferred Ideas (OUT OF SCOPE)
- None
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MCP-11 | Deployment guide: step-by-step setup for Claude Code (.mcp.json) and Claude Desktop (config.json) with verification steps | Full research completed: config paths, .mcp.json structure, verification commands, platform-specific Python install, venv paths, known pitfalls documented below |
</phase_requirements>

---

## Summary

Phase 15 produces a single SETUP.md at the repo root. The audience is an SAP consultant who knows SAP GUI deeply but has never opened a terminal. The guide must be self-contained — covering Python installation check, cloning the repo, building a venv, installing dependencies, and configuring the server in both Claude Code and Claude Desktop. Target: under 15 minutes following the guide.

The server is a Python stdio process (`scripts/mcp_server.py`) launched by `fastmcp==3.0.2`. Both Claude Code and Claude Desktop launch it by executing `.venv/bin/python scripts/mcp_server.py` (macOS/Linux) or `.venv\Scripts\python.exe scripts\mcp_server.py` (Windows). Both clients require absolute paths — relative paths do not work. The reader must substitute their own filesystem path in the config file.

Claude Desktop is available on macOS and Windows only. Linux users can use Claude Code (the terminal CLI) but cannot use Claude Desktop. The guide must be honest about this. Claude Code is the primary target; Claude Desktop is secondary.

**Primary recommendation:** Write the guide Claude Code-first (it's cross-platform and simpler), then cover Claude Desktop as a "also works in Claude Desktop" supplement. Be explicit that the reader must replace the example absolute paths with their own path.

---

## Standard Stack

This phase produces documentation, not code. The "stack" is the existing server that the guide explains.

### Existing Server Components (what the guide documents)

| Component | Value | Notes for Guide |
|-----------|-------|-----------------|
| Server entry point | `scripts/mcp_server.py` | Reader must not modify |
| Python dependency file | `scripts/requirements.txt` | Contains `fastmcp==3.0.2` and `PyYAML>=6.0` |
| Venv location | `.venv/` at repo root | Created with `python -m venv .venv` |
| macOS/Linux python bin | `.venv/bin/python` | Used in .mcp.json and claude_desktop_config.json |
| Windows python bin | `.venv\Scripts\python.exe` | Used in Windows config |
| Minimum Python version | 3.10 | fastmcp requires-python >=3.10 (verified: pyproject.toml) |
| Server name in config | `sap-kb` | The key used in .mcp.json `mcpServers` |

### No New Code in This Phase

The guide documents what already exists. No changes to `mcp_server.py`, `requirements.txt`, or `.mcp.json` are part of this phase.

---

## Architecture Patterns

### How the Server Starts (what the guide explains to the reader)

Both Claude Code and Claude Desktop use stdio transport. They launch the MCP server as a child process:

```
Claude (client)  <--stdio wire protocol-->  .venv/bin/python scripts/mcp_server.py
```

The reader needs to tell the client three things:
1. Which Python executable to use (the one inside `.venv/`)
2. Where the server script is (`scripts/mcp_server.py`)
3. Both must be absolute paths

### Claude Code Configuration (.mcp.json — project scope)

The repo already contains `.mcp.json` at the root. The reader **cannot use it as-is** because it contains the author's absolute path (`/home/corye/Claude/SAPKnowledge/`). The reader must update it to their own path.

**Current .mcp.json (what the reader finds in the repo):**
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "/home/corye/Claude/SAPKnowledge/.venv/bin/python",
      "args": ["/home/corye/Claude/SAPKnowledge/scripts/mcp_server.py"]
    }
  }
}
```

**What the reader must produce (macOS/Linux example, with their own path):**
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "/Users/yourname/SAPKnowledge/.venv/bin/python",
      "args": ["/Users/yourname/SAPKnowledge/scripts/mcp_server.py"]
    }
  }
}
```

**Windows example:**
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "C:\\Users\\yourname\\SAPKnowledge\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\yourname\\SAPKnowledge\\scripts\\mcp_server.py"]
    }
  }
}
```

**Key constraint:** Relative paths are not allowed in `.mcp.json`. Claude Code will fail silently if a relative path is provided. (MEDIUM confidence — documented in Claude Code docs and multiple community sources; relative paths throw errors.)

**Security prompt:** The first time Claude Code opens a project with a `.mcp.json`, it prompts for approval before activating the server. The reader should expect this prompt and click "Allow." (MEDIUM confidence — documented behavior, but a known bug on macOS sometimes skips the prompt; the guide should mention both cases.)

### Claude Desktop Configuration (claude_desktop_config.json)

**Config file locations (HIGH confidence — verified via official MCP docs and modelcontextprotocol.io):**

| Platform | Config file path |
|----------|-----------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | NOT APPLICABLE — Claude Desktop not available on Linux |

**Opening via UI (preferred for non-developers):**
Claude Desktop menu → Settings → Developer → Edit Config

This avoids the reader needing to navigate the filesystem manually.

**JSON to add (macOS example):**
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "/Users/yourname/SAPKnowledge/.venv/bin/python",
      "args": ["/Users/yourname/SAPKnowledge/scripts/mcp_server.py"]
    }
  }
}
```

**After editing:** Completely quit Claude Desktop and relaunch. Changes do not take effect on the running instance.

### Verification — Claude Code

Two methods, both should be shown:

**Method 1: List configured servers (terminal, before opening Claude Code session)**
```bash
claude mcp list
```
Expected output contains `sap-kb` in the list.

**Method 2: /mcp slash command (inside Claude Code session)**
```
/mcp
```
Shows connected servers, their status, and available tools. If `sap-kb` is listed as "connected" with 6 tools visible, setup succeeded.

**Method 3: Real query (the ultimate verification)**
Ask: `What does T-code MIGO do?`
Expected: Claude responds with a description of MIGO (Goods Movement transaction), drawn from the KB. This is the "working" test the CONTEXT.md specifies.

### Verification — Claude Desktop

After restart, a hammer/tools icon appears in the bottom-right of the chat input area. Clicking it shows connected servers and tools. Then ask: `What does T-code MIGO do?`

### Recommended Project Structure for the Guide

The guide documents a fixed structure — the reader does not choose it:

```
SAPKnowledge/        ← repo root (reader's absolute path goes here)
├── .mcp.json        ← Claude Code config (reader edits this file)
├── .venv/           ← Python virtual environment (reader creates this)
│   ├── bin/python   ← macOS/Linux executable
│   └── Scripts/     ← Windows executable location
├── scripts/
│   ├── mcp_server.py
│   └── requirements.txt
└── SETUP.md         ← the file being written
```

---

## Don't Hand-Roll

This phase is documentation-only. However, the guide must not instruct the reader to:

| Problem | Don't Instruct | Use Instead | Why |
|---------|---------------|-------------|-----|
| Python version management | Install pyenv or conda | python.org installer (Windows) or brew (macOS) | Non-developer audience; simpler single-step install |
| Dependency management | Write a setup.py or build a wheel | `pip install -r scripts/requirements.txt` | Already provided in repo |
| JSON editing | Use a code editor with a plugin | Any text editor (Notepad on Windows, TextEdit on macOS, nano on Linux) | Audience does not have VS Code or similar |
| Finding absolute paths | Explain `pwd`/`$PWD` in depth | Show exact `pwd` command + show how to read the output | One concrete command is enough |
| MCP wire protocol | Explain stdio protocol internals | Skip entirely — "the server talks to Claude automatically" | Out of scope for non-developer audience |

---

## Common Pitfalls

### Pitfall 1: Absolute Path Still Points to Author's Machine
**What goes wrong:** Reader copies `.mcp.json` as-is. Claude Code tries to launch `/home/corye/Claude/SAPKnowledge/.venv/bin/python` which does not exist on their machine. The server silently fails to start.
**Why it happens:** `.mcp.json` is checked into the repo with the author's absolute path.
**How to avoid:** The guide must explicitly call out "you must replace this path" with a warning callout. Show the `pwd` command to get their path. Provide a fill-in-the-blank template.
**Warning signs:** `/mcp` shows sap-kb as disconnected, or the first query gets no KB data.

### Pitfall 2: Venv Not Built Before Editing Config
**What goes wrong:** Reader edits `.mcp.json` first, then Claude Code tries to launch the server, but `.venv/bin/python` does not exist yet because `python -m venv .venv` has not been run.
**Why it happens:** Eager readers jump to the "fun" config step before prerequisites.
**How to avoid:** Order the guide strictly: 1) Python check, 2) clone repo, 3) create venv, 4) install deps, 5) edit config. The guide must enforce this sequence.
**Warning signs:** Error like "No such file or directory: .venv/bin/python"

### Pitfall 3: Windows Path Backslash Confusion
**What goes wrong:** Reader types `C:\Users\name\SAPKnowledge` into JSON but does not double the backslashes. JSON parses `\U`, `\S` etc. as escape sequences, causing parse errors or wrong paths.
**Why it happens:** Windows uses backslashes but JSON requires `\\` to represent a single `\`.
**How to avoid:** Show Windows example JSON with `\\` explicitly. Alternatively, note that forward slashes also work in Windows JSON (`C:/Users/name/SAPKnowledge`).
**Warning signs:** JSON parse error when Claude Desktop starts, or server not found.

### Pitfall 4: Claude Desktop Not Fully Quit (Restart Required)
**What goes wrong:** Reader saves `claude_desktop_config.json` and clicks the X button, then reopens. On macOS, the app may not have fully quit (it stays in the dock/tray). The server does not load because config was not read on this session start.
**Why it happens:** Claude Desktop must read config at launch time.
**How to avoid:** Instruct: "Quit completely — on macOS use Cmd+Q, not just closing the window." On Windows, check the system tray.
**Warning signs:** Server does not appear in tools list after "restart."

### Pitfall 5: Python Version Too Old
**What goes wrong:** Reader has Python 3.8 or 3.9 from a previous install. `pip install -r scripts/requirements.txt` fails because `fastmcp==3.0.2` requires Python >=3.10.
**Why it happens:** macOS ships with Python stubs or old versions; Windows may have an old install from years ago.
**How to avoid:** Start the guide with an explicit version check: `python3 --version` (macOS/Linux) or `python --version` (Windows). If below 3.10, install fresh.
**Warning signs:** pip install error mentioning Python version requirement.

### Pitfall 6: Linux User Tries Claude Desktop
**What goes wrong:** Reader follows the "Claude Desktop" section but can't find the download for Linux.
**Why it happens:** Claude Desktop is macOS and Windows only (confirmed February 2026).
**How to avoid:** Add a clear note at the top of the Claude Desktop section: "Claude Desktop is available on macOS and Windows only. Linux users: use the Claude Code section above."

### Pitfall 7: Windows PowerShell Execution Policy Blocks venv Activation
**What goes wrong:** Reader runs `\.venv\Scripts\Activate.ps1` to activate the venv in PowerShell and gets "running scripts is disabled."
**Why it happens:** Default PowerShell execution policy on Windows 10/11 blocks unsigned scripts.
**How to avoid:** The guide does NOT need to instruct activation — the reader never needs to "activate" the venv. They just need the absolute path to `.venv\Scripts\python.exe`. Activation is only needed if the reader wants to run Python commands interactively. The guide should use the venv Python directly (`python -m venv .venv` then `.venv/bin/python -m pip install -r scripts/requirements.txt`).

### Pitfall 8: .mcp.json Approval Prompt on First Use
**What goes wrong:** Reader opens Claude Code in the project directory and gets a security prompt asking to approve the MCP server. They click "Deny" not understanding what it is.
**Why it happens:** Claude Code prompts for approval before loading project-scoped `.mcp.json` servers.
**How to avoid:** Warn the reader: "The first time you open Claude Code in this folder, it will ask permission to connect to the SAP KB server. Click Allow." (Note: a known bug on some macOS versions means this prompt may not appear; in that case the server loads automatically.)

---

## Code Examples

### Finding Your Absolute Path (what the guide will show)

**macOS/Linux:**
```bash
# In Terminal, navigate to where you cloned the repo, then:
pwd
# Output example: /Users/yourname/Documents/SAPKnowledge
```

**Windows (PowerShell):**
```powershell
# In PowerShell, navigate to the repo folder, then:
Get-Location
# Output example: C:\Users\yourname\Documents\SAPKnowledge
```

### Create Venv and Install Dependencies (macOS/Linux)
```bash
# From the repo root:
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
```

### Create Venv and Install Dependencies (Windows PowerShell)
```powershell
# From the repo root:
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r scripts\requirements.txt
```

### Verify Dependencies Installed Correctly
```bash
.venv/bin/python -c "import fastmcp; print('OK')"
# Expected output: OK
```
Windows version:
```powershell
.venv\Scripts\python.exe -c "import fastmcp; print('OK')"
```

### Complete .mcp.json Template (macOS/Linux)
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "/REPLACE/WITH/YOUR/PATH/.venv/bin/python",
      "args": ["/REPLACE/WITH/YOUR/PATH/scripts/mcp_server.py"]
    }
  }
}
```

### Complete .mcp.json Template (Windows)
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "C:\\REPLACE\\WITH\\YOUR\\PATH\\.venv\\Scripts\\python.exe",
      "args": ["C:\\REPLACE\\WITH\\YOUR\\PATH\\scripts\\mcp_server.py"]
    }
  }
}
```

### Claude Desktop Config (append to existing mcpServers, or create new file)
```json
{
  "mcpServers": {
    "sap-kb": {
      "command": "/REPLACE/WITH/YOUR/PATH/.venv/bin/python",
      "args": ["/REPLACE/WITH/YOUR/PATH/scripts/mcp_server.py"]
    }
  }
}
```

### Verify Claude Code Sees the Server
```bash
claude mcp list
```
Expected output contains `sap-kb`.

---

## State of the Art

| Area | Current Approach | Notes |
|------|-----------------|-------|
| Claude Desktop availability | macOS + Windows only | Linux not supported (confirmed Feb 2026) |
| Claude Code config | `.mcp.json` at repo root (project scope) | Requires absolute paths |
| MCP transport for local servers | stdio (child process) | No network port needed |
| Python min version for fastmcp | >=3.10 | fastmcp pyproject.toml verified |
| Config file name (Claude Desktop) | `claude_desktop_config.json` | Not `config.json` — easy to misremember |
| Log location on macOS | `~/Library/Logs/Claude/mcp*.log` | Useful for troubleshooting section |
| Log location on Windows | `%APPDATA%\Claude\logs\mcp*.log` | Same |

---

## Open Questions

1. **Does the existing `.mcp.json` need a note in the file itself?**
   - What we know: The file contains the author's hardcoded path
   - What's unclear: Whether a comment in the JSON (not valid JSON) or a companion `.mcp.json.example` would be cleaner
   - Recommendation: SETUP.md should instruct the reader to edit `.mcp.json` in place; optionally add a `# This file requires editing` note in the README header

2. **Git clone vs ZIP download for the repo**
   - What we know: The repo is at GitHub (BrandedTamarasu-glitch/SAPKnowledge per MEMORY.md). ZIP download works without git installed; git clone requires git.
   - What's unclear: Whether the non-developer audience is more likely to have git available or not
   - Recommendation (Claude's Discretion): Offer both options. Primary: "Code > Download ZIP" button for readers without git. Secondary: `git clone` for readers who do have git. ZIP avoids needing to explain git, but git clone is better for receiving future updates. Present ZIP as the path of least resistance.

3. **Verification placement**
   - What we know: CONTEXT.md leaves exact placement to Claude's Discretion
   - Recommendation: Place a "smoke test" verification immediately after the venv/install step (test that Python + fastmcp are working before touching any config), and a second "full test" at the end of each section (Claude Code section, Claude Desktop section) using the MIGO query.

4. **Windows Python command: `python` vs `python3`**
   - What we know: On macOS/Linux, `python3` is the correct command (macOS ships a `python` stub that may point to Python 2 or nothing). On Windows, the installer from python.org adds `python` to PATH (not `python3`).
   - Recommendation: Use `python3` for macOS/Linux instructions, `python` for Windows. Flag this difference with a warning callout.

---

## Sources

### Primary (HIGH confidence)
- Official Claude Code MCP docs (code.claude.com/docs/en/mcp) — .mcp.json format, scopes, `/mcp` command, `claude mcp list`, relative paths not allowed
- modelcontextprotocol.io/docs/develop/connect-local-servers — claude_desktop_config.json paths for macOS and Windows, restart requirement, log locations, JSON format
- claude.com/download — Confirmed Claude Desktop is macOS + Windows only (no Linux)
- fastmcp pyproject.toml (github.com/jlowin/fastmcp) — requires-python >=3.10

### Secondary (MEDIUM confidence)
- WebSearch for Linux MCP config path (`~/.config/Claude/claude_desktop_config.json`) — multiple community sources agree but Claude Desktop does not exist on Linux, so this is moot
- WebSearch: Windows .mcp.json path format with `\\` — confirmed by multiple MCP setup guides
- WebSearch: first-use approval prompt behavior — documented but known bug (Issue #9189 on anthropics/claude-code) means behavior may vary

### Tertiary (LOW confidence)
- `/mcp` command output format — described in community blogs and Claude Code cheat sheets; exact UI may vary by Claude Code version
- Tools icon appearance in Claude Desktop — described in official MCP quickstart; UI details may change with app updates

---

## Metadata

**Confidence breakdown:**
- Config file paths: HIGH — official docs + claude.com/download
- Absolute path requirement: HIGH — official Claude Code docs explicit
- Python minimum version: HIGH — fastmcp pyproject.toml
- Claude Desktop Linux availability: HIGH — claude.com/download confirms macOS + Windows only
- /mcp command output format: MEDIUM — community sources, no official sample output
- First-use approval prompt: MEDIUM — documented but known macOS bug

**Research date:** 2026-02-23
**Valid until:** 2026-05-23 (90 days — config paths are stable; UI details may shift with app updates)
