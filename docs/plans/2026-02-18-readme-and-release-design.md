# README, Description & v0.1.0 Release — Design

**Date:** 2026-02-18
**Status:** Approved

## Context

The repository README.md is currently empty (just a heading). We are writing
a full README, setting a GitHub repository description, and creating the first
release tag v0.1.0 with hand-written release notes.

## Audience

General SAP practitioners (consultants, power users, learners) who work with
SAP ECC 6.0 and want Claude to give better, more accurate answers.

## README Structure — Option A (Usage-First)

### Sections in order

1. **Header** — one-line description, ECC 6.0 scope callout
2. **Using It** — full step-by-step instructions (the core value):
   - Step 1: Clone the repo
   - Step 2: Add global rule to `~/.claude/rules/sap-knowledge-base.md`
   - Step 3: Verify rule is loading via `/config`
   - Step 4: Ask SAP questions naturally (example prompts by topic)
   - Tips section
3. **What's Covered** — table: Module | Key Topics across MM, SD, FI, CO, Cross-module
4. **Scope & Confidence** — ECC 6.0 only note, frontmatter confidence levels
5. **License**

### Example prompts (by topic type)
- Transactions, Configuration, Process flows, Integration, Period-end,
  Troubleshooting, Playbooks, Design patterns

## GitHub Description

> SAP ECC 6.0 knowledge base for Claude Code — transaction codes, config paths, and process flows for MM, SD, FI, CO

## Release v0.1.0

- Tag: `v0.1.0`
- Title: `v0.1.0 — Initial SAP ECC 6.0 Knowledge Base`
- Notes: hand-written, organized by module coverage + cross-module content
- Tone: concise, practitioner-facing
- Include: scope note (ECC 6.0 only), pointer to README for setup
