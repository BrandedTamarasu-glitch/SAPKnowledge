# Phase 15: Deployment Documentation - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Create a single setup guide (SETUP.md at repo root) that a non-developer colleague can follow to configure the SAP ECC 6 KB MCP server in Claude Code and/or Claude Desktop. The guide covers everything from Python installation through a working first query. No new server capabilities — documentation only.

</domain>

<decisions>
## Implementation Decisions

### Audience & tone
- Primary reader: business analyst / SAP consultant — comfortable with SAP GUI, not with terminals or Python
- Tone: friendly explainer — brief context at each step explaining why, not just what
- Explain WHY at each major stage (one sentence per section, e.g., "This creates an isolated Python environment so nothing conflicts with your system")
- Warnings and gotchas use highlighted blocks: ⚠️ Note: or > **Warning:** callout blocks for things that commonly go wrong
- Inline ⚠️ blocks within risky steps (not just a troubleshooting section at the end)

### Guide structure & format
- File: `SETUP.md` at repo root (alongside README.md)
- Top-level structure: brief TL;DR overview first (sets expectations), then two main sections: **Section 1: Claude Code** and **Section 2: Claude Desktop**
- Quick-start summary at the top: "What you'll do: 1. Install Python 2. Set up environment 3. Register the server" — 3-line overview before any steps
- Platform-specific sections within Claude Desktop: `### macOS`, `### Windows`, `### Linux` as separate subsections (not inline callout boxes)
- All three platforms covered: macOS, Windows, Linux

### Platform & prerequisite depth
- Assume NOTHING: guide starts from zero — includes a "check if Python 3 is installed" step with a link for installing it if not, then clone repo instructions
- OS command differences: use the most common form (macOS/Linux), add a ⚠️ callout when Windows differs (e.g., `python` vs `python3`, path separators)
- Troubleshooting: inline ⚠️ notes at each step where failures are most common (not a separate troubleshooting section)
- Claude Desktop config file path shown for all three platforms

### Verification step design
- "Working" = server responds to a test query (highest confidence — reader calls lookup_tcode and gets a real answer)
- Verification placement: Claude's discretion (place where it makes the most structural sense — likely once per section or once at the end after both sections)
- Each verification step shows: command + expected output description ("You should see: sap-kb connected, 6 tools available — then ask...")
- End with a "try your first query" prompt: suggest "What does T-code MIGO do?" to demonstrate end-to-end

### Claude's Discretion
- Exact placement of verification step(s) (once per section vs once at end)
- How to handle the repo clone step (git clone vs download ZIP — pick what's simpler for non-developers)
- Exact wording of the "why" explanations at each step

</decisions>

<specifics>
## Specific Ideas

- "15 minutes or less" is the success bar — the guide should feel completable, not daunting
- The reader is comfortable with SAP GUI daily but has never touched a terminal — tone should never assume they know what a virtual environment is
- Sample query at the end: "What does T-code MIGO do?" — intentionally a simple MM lookup to show immediate value

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 15-deployment-documentation*
*Context gathered: 2026-02-23*
