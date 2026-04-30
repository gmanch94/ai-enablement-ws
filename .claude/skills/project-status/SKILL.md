---
name: project-status
description: Refresh a project's status — derive current state from code/tests/git, regenerate the project's status memory entry and (if requested) a status section in the README
---

# Skill: /project-status — Refresh Project Status

Status memories rot. The Argus and Kroger memory entries both share the same shape (status, architecture, run commands, known workarounds) and both drift from reality between sessions. This skill recomputes status from primary sources (code, tests, git) and refreshes the memory entry — never the reverse.

## Trigger
User runs `/project-status <project-dir>` — e.g. `/project-status projects/argus`.

## Behavior
1. Identify the project's existing memory entry by checking `MEMORY.md` for entries that reference the project path or name. If multiple, ask which to refresh.
2. Compute current status from primary sources — never trust the existing memory:
   - **Tests**: run the test command from `CLAUDE.md` or `pyproject.toml`. Capture pass/fail count.
   - **Git**: branch name, commits since main, last commit date, uncommitted changes.
   - **Stack/architecture**: from `pyproject.toml` deps + agent/module structure, NOT from existing memory.
   - **Run commands**: from `CLAUDE.md` Run Commands table if present, else from scripts in `scripts/`.
   - **Known workarounds / gotchas**: only carry forward existing memory entries IF still applicable — re-verify each one.
3. Diff new vs existing memory. Show user what's about to change.
4. On approval, write the updated memory file. Update its `description:` frontmatter line if status changed materially (e.g. "PoC" → "MVP working").
5. Optionally refresh a "## Status" section in the project's README if the user asks.

## What goes in the memory

| Field | Source |
|---|---|
| Status (one line) | Test pass rate + working flow + last meaningful change |
| Architecture (terse) | Module/agent list from code |
| Run commands | CLAUDE.md or scripts/ — not memory |
| Pre-demo / known workarounds | Existing memory, re-verified |
| Last refreshed | today's date |

## Output format

```
Refreshing project_argus.md from primary sources…

Computed status:
  Branch: gm_updates (3 commits ahead of main)
  Last commit: 2026-04-30 (2e890b3 — Drop Kroger reference from Argus CLAUDE.md)
  Tests: 143/143 pass (12.4s)
  Server: app.fast_api_app:app starts clean
  Stack: ADK 1.27 · FastAPI · BigQuery · Slack · A2A

Diff vs existing memory:

- Status line:
    OLD: "MVP reached 2026-04-24"
    NEW: "MVP working ✓ — 143 tests pass, 3 commits ahead on gm_updates as of 2026-04-30"
- Workarounds:
    KEEP: gcloud quota project per-shell (still applicable)
    KEEP: ARGUS_EMBEDDING_LOCATION=us-central1 (still in code)
    DROP: "playground doesn't exercise A2A" — already moved to CLAUDE.md, not memory-worthy

Apply? (y / edit / no)
```

## Quality Bar
- Code/tests/git are authoritative. Memory is summary, never source of truth.
- If the existing memory disagrees with code, code wins — and the memory gets corrected.
- Don't hoard outdated workarounds. If a workaround is now in CLAUDE.md or fixed in code, drop it from memory.
- Status line must be falsifiable — "MVP working" alone is weak; "143 tests pass on commit 2e890b3" is strong.

## Related
- `/compound` — captures one-time learnings from a session
- `/checkpoint` — saves in-flight session state
- `/project-status` (this skill) — refreshes long-lived project memory

The three are different tools. Don't conflate.
