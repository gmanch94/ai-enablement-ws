---
name: doc-framing-check
description: Scan a project's docs (README, CLAUDE.md, ADRs, runbooks) for inconsistent project naming, scope, or framing — catches the "README says retail, CLAUDE.md still says Kroger" class of bug
---

# Skill: /doc-framing-check — Doc Framing Consistency Audit

Documentation drifts. Someone updates the README to be generic, but CLAUDE.md still names a specific customer. ADRs reference an old project name. Runbooks contradict the architecture diagram. Each individual doc looks fine — the inconsistency only shows when read together.

## Trigger
User runs `/doc-framing-check <project-dir>` — e.g. `/doc-framing-check projects/argus` or `/doc-framing-check .` for repo-wide.

## Behavior
1. Identify the canonical framing source. Default order: `README.md` → `<dir>/README.md` → user override. Read it. Extract: project name, one-line description, scope nouns (e.g. "retail catalog", "ML pipeline"), key tech stack terms.
2. Build a target framing summary. Show it to the user. Ask: "Is this the canonical framing? (y / edit)"
3. Scan the rest of the project's docs for divergence:
   - `CLAUDE.md` (root + project-level)
   - `*.md` in `docs/`, `decisions/`, `runbooks/`, `context/`
   - `pyproject.toml` `[project].description`, `[tool.agents-cli].description`
   - First H1 + first paragraph of any other top-level `*.md`
4. Flag any doc that uses a name, scope, or framing inconsistent with canonical. Quote the offending line. Suggest the fix.
5. Report as a table. Do not auto-edit — user picks which to take.

## What counts as "inconsistent"

| Type | Example |
|---|---|
| **Customer/vertical drift** | README: "retail catalog"; CLAUDE.md: "Kroger catalog" |
| **Scope mismatch** | README: "5-agent pipeline"; ADR: "3-agent pipeline" |
| **Tech stack drift** | README: "BigQuery Vector Search"; runbook: "Pinecone" |
| **Status drift** | README: "MVP working ✓"; CLAUDE.md: "PoC in progress" |
| **Name drift** | README/code: `argus`; one ADR: `Project Catalog Watcher` |

## What does NOT count
- Different levels of detail (README terse, ADR deep) — fine.
- Tone differences (CLAUDE.md prescriptive, README descriptive) — fine.
- Demo-specific references in demo materials (e.g. `docs/demos/`) — fine, demos are allowed to name a customer.

## Output format

```
Canonical (from README.md):
  Name: Argus
  Scope: retail product catalog integrity
  Stack: ADK · FastAPI · BigQuery Vector Search · Slack · A2A
  Status: MVP working ✓ (143/143 tests)

Drift detected:

| File                                   | Line | Issue                                | Suggested fix |
|----------------------------------------|------|--------------------------------------|---------------|
| projects/argus/CLAUDE.md               | 3    | Says "Kroger catalog integrity"      | "retail catalog integrity" |
| decisions/ADR-0046-...md               | 12   | Says "4-agent pipeline"              | "5-agent pipeline" (matches README) |
| docs/runbooks/argus-local-dev-runbook.md | 5  | Stack omits "A2A"                    | Add A2A to stack line |

3 inconsistencies. Apply fixes? (y / pick / no)
```

## Quality Bar
- Trust README as canonical unless user says otherwise. README is the public face; everything else aligns to it.
- Quote the actual line — never paraphrase. The user is going to grep for exactly that string.
- Don't flag stylistic differences. Flag factual/scope contradictions.
- Demo materials are allowed to name a specific customer; don't flag those unless user asks for strict mode.
