# SAP ECC 6 Knowledge Base — MCP Server Setup

This guide walks you through configuring the SAP KB MCP server so Claude can query the knowledge base directly as a tool. Designed for SAP consultants and business analysts — if you've never used a terminal before, this guide covers every step.

## TL;DR

Three things to do:

1. Install Python 3.10 or newer
2. Set up the server environment (one-time, about 5 minutes)
3. Tell Claude where to find it (edit one config file)

**Estimated time: 10–15 minutes.** You'll end with Claude answering SAP questions directly from the KB.

Jump to your setup target:
- [Section 1: Claude Code](#section-1-claude-code)
- [Section 2: Claude Desktop](#section-2-claude-desktop) (macOS and Windows only)

---

## Prerequisites

Complete these steps once before configuring either Claude Code or Claude Desktop.

### Step 1: Check your Python version

The server requires Python 3.10 or newer. Python is a programming language — you're not writing any code, but you do need it installed to run the server.

Open a terminal (macOS/Linux) or PowerShell (Windows) and run:

- **macOS/Linux:**
  ```bash
  python3 --version
  ```

> **⚠️ Windows note:** Use `python --version` instead — the Windows installer adds `python` to your PATH, not `python3`.
> ```powershell
> python --version
> ```

Expected output: `Python 3.10.x` or higher.

If you see `Python 3.9.x` or lower, or "command not found", install a newer version:

- **macOS:** Download from [python.org/downloads](https://python.org/downloads) or run `brew install python` if you have Homebrew
- **Windows:** Download from [python.org/downloads](https://python.org/downloads) — during installation, check **"Add Python to PATH"** before clicking Install
- **Linux (Ubuntu/Debian):** `sudo apt install python3`
- **Linux (Fedora):** `sudo dnf install python3`

---

### Step 2: Get the repository

This is the folder containing the SAP knowledge content and the server files.

**Primary path — no git required (simpler for most readers):**

1. Go to [github.com/BrandedTamarasu-glitch/SAPKnowledge](https://github.com/BrandedTamarasu-glitch/SAPKnowledge)
2. Click the green **Code** button → **Download ZIP**
3. Extract the ZIP to a folder you'll remember, for example `Documents/SAPKnowledge`

**Alternative — if you have git installed:**
```bash
git clone https://github.com/BrandedTamarasu-glitch/SAPKnowledge.git
```

---

### Step 3: Find your absolute path

The config files need the full path to your folder — not a shortcut like `~/Documents`. Think of it like a full postal address instead of "my house."

Open Terminal (macOS/Linux) or PowerShell (Windows), navigate into the SAPKnowledge folder, then run:

- **macOS/Linux:**
  ```bash
  pwd
  ```
  Example output: `/Users/yourname/Documents/SAPKnowledge`

- **Windows PowerShell:**
  ```powershell
  Get-Location
  ```
  Example output: `C:\Users\yourname\Documents\SAPKnowledge`

Copy this output — you'll need it in every step below. Replace `/REPLACE/WITH/YOUR/PATH` in all examples with this value.

---

### Step 4: Create the virtual environment

A virtual environment is an isolated copy of Python just for this project. It prevents the server's dependencies from conflicting with anything else on your computer.

Run this command from inside the SAPKnowledge folder:

- **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  ```

> **⚠️ Windows note:** Use `python` instead of `python3`:
> ```powershell
> python -m venv .venv
> ```

---

### Step 5: Install the server's dependencies

This downloads the one library the server needs (fastmcp). It only runs once.

- **macOS/Linux:**
  ```bash
  .venv/bin/python -m pip install -r scripts/requirements.txt
  ```

> **⚠️ Windows note:** The path to the virtual environment's Python is different on Windows:
> ```powershell
> .venv\Scripts\python.exe -m pip install -r scripts\requirements.txt
> ```

> **⚠️ Warning:** Do NOT run `pip install` without the `.venv/bin/python` prefix. Using the system pip would install into your global Python installation instead of the isolated environment.

**Smoke test — verify the install worked before touching any Claude config:**

The server needs to be runnable before Claude can connect to it. Run:

- **macOS/Linux:**
  ```bash
  .venv/bin/python -c "import fastmcp; print('OK')"
  ```

- **Windows:**
  ```powershell
  .venv\Scripts\python.exe -c "import fastmcp; print('OK')"
  ```

Expected output: `OK`

If you see an error mentioning Python version, your Python is older than 3.10 — go back to Step 1 and install a newer version.

---

## Section 1: Claude Code

Claude Code is the terminal-based Claude client. It auto-discovers MCP servers configured in a `.mcp.json` file at the project root — which this repo already provides.

### Step 6: Update .mcp.json with your path

The repo ships with a `.mcp.json` file that points to the author's computer. You need to update it to point to YOUR copy of the repo.

> **⚠️ Warning — this is the most common setup failure.** The file currently contains `/home/corye/Claude/SAPKnowledge/` — that path does not exist on your machine. You must replace it with your own path from Step 3.

Here is what the file currently looks like (so you know what to find):

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

Replace it with your path. **macOS/Linux template:**

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

> **⚠️ Windows note — backslash warning:** On Windows, use double backslashes (`\\`) in JSON paths, or use forward slashes — both work. Do NOT use single backslashes — they cause JSON parse errors and the server will not start.

**Windows template:**

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

Open `.mcp.json` in any text editor (Notepad on Windows, TextEdit on macOS, or nano in terminal). Replace both occurrences of the path with your own path from Step 3.

---

### Step 7: Open Claude Code in the repo folder

Open Terminal (macOS/Linux) or PowerShell (Windows), navigate into the SAPKnowledge folder, then run:

```bash
claude
```

> **⚠️ Note:** The first time you open Claude Code in this folder, it may ask permission to connect to the SAP KB server. Click **Allow**. On some macOS versions this prompt does not appear — if so, the server loads automatically.

---

### Step 8: Verify Claude Code setup

Two ways to confirm the server is connected:

**Method 1 — List servers from the terminal (run before starting a Claude session):**
```bash
claude mcp list
```
Expected: `sap-kb` appears in the list.

**Method 2 — /mcp inside a Claude session:**

Type `/mcp` in the Claude Code prompt. Expected: `sap-kb` is listed as connected with 6 tools available.

If `sap-kb` shows as "disconnected": double-check that the path in `.mcp.json` matches your actual folder location from Step 3.

---

### Step 9: Try your first query

Ask Claude:

> What does T-code MIGO do?

Expected: Claude responds with a description of MIGO (Goods Movement transaction in MM), drawn from the SAP KB. If you see a real answer — setup is complete.

---

## Section 2: Claude Desktop

> **⚠️ Platform availability:** Claude Desktop is available on **macOS and Windows only**. If you are on Linux, use [Section 1: Claude Code](#section-1-claude-code) instead — there is no Claude Desktop for Linux.

Claude Desktop uses a separate config file. You'll add the same server information there.

**Before continuing:** Complete Steps 1–5 above first. Python, the virtual environment, and the dependencies must already be installed.

---

### macOS

#### Step 10: Open the Claude Desktop config file

The easiest method uses the app's built-in editor:

Claude Desktop → Settings (gear icon) → Developer → **Edit Config**

This opens `claude_desktop_config.json` directly in your default text editor. If the file is empty, start with `{}`.

Manual path if needed: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Step 11: Add the server entry

Add the `sap-kb` entry inside `mcpServers`. If `mcpServers` already exists with other entries, add the `sap-kb` block alongside them.

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

Replace `/REPLACE/WITH/YOUR/PATH` with your path from Step 3 (for example: `/Users/yourname/Documents/SAPKnowledge`).

#### Step 12: Quit and relaunch Claude Desktop

> **⚠️ Warning:** Closing the window is NOT enough on macOS — the app stays running in the background. Use **Cmd+Q** to fully quit, then reopen Claude Desktop.

#### Step 13: Verify Claude Desktop setup

After relaunch, look for a hammer/tools icon in the bottom-right corner of the chat input area. Click it — `sap-kb` should appear with 6 tools listed.

Then ask:

> What does T-code MIGO do?

Expected: Claude Desktop responds with KB content. If you see a real answer — setup is complete.

If the server doesn't appear: check `~/Library/Logs/Claude/` for `mcp*.log` files — they show why the server failed to start.

---

### Windows

#### Step 10: Open the Claude Desktop config file

Easiest method: Claude Desktop → Settings → Developer → **Edit Config**

Manual path if needed: `%APPDATA%\Claude\claude_desktop_config.json`

(Paste `%APPDATA%\Claude\` into Windows Explorer's address bar to navigate there directly.)

#### Step 11: Add the server entry

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

> **⚠️ Backslash warning:** Use double backslashes (`\\`) or forward slashes in the JSON path. Single backslashes will cause a parse error and the server will not start.

Replace `C:\\REPLACE\\WITH\\YOUR\\PATH` with your path from Step 3.

#### Step 12: Quit and relaunch Claude Desktop

> **⚠️ Warning:** Check the system tray (bottom-right corner of the taskbar) — Claude Desktop may still be running there after you close the window. Right-click the icon and choose **Quit**, then reopen Claude Desktop.

#### Step 13: Verify Claude Desktop setup

Same as macOS — look for the hammer/tools icon in the chat input area, click it to confirm `sap-kb` is listed with 6 tools, then ask:

> What does T-code MIGO do?

If the server doesn't appear: check `%APPDATA%\Claude\logs\` for `mcp*.log` files.

---

### Linux

> **⚠️ Note:** Claude Desktop is not available on Linux. Use [Section 1: Claude Code](#section-1-claude-code) instead. Claude Code works the same on Linux as on macOS.
