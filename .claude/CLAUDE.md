# Claude Code Behavior — SAP Knowledge Base

## Navigation

1. Check `.claude/rules/sap-routing.md` first — it maps query topics to the correct module directory
2. Read the module's `CLAUDE.md` (e.g., `modules/mm/CLAUDE.md`) for file orientation
3. Read specific content files referenced by the module index

## Rules

- Always check frontmatter `confidence` level before citing content (high/medium/low)
- Content marked `confidence: low` needs verification before presenting as authoritative
- When content mentions S/4HANA, it is for **disambiguation only** — this KB covers ECC 6.0
- Do not mix ECC 6 and S/4HANA behavior in answers unless explicitly comparing them
- Use `@file` references from module CLAUDE.md files to load content on-demand
