---
name: track
description: Append raw session findings to today's daily log (docs/daily/YYYY-MM-DD.md) — fast scratch capture that feeds /compound
---

# Skill: /track — Daily Session Log

Run at the end of any session, or at any natural pause, to capture raw findings while context is fresh. No LLM judgment — just append bullets. `/compound` distills these into solution docs at natural milestones.

## Trigger
User runs `/track` during or at the end of a session.

## Behavior
1. Determine today's date → target: `docs/daily/YYYY-MM-DD.md` in the current project root
2. Create the file with a date header if it doesn't exist
3. Infer 2-4 bullets from the session: decisions made, gotchas hit, things tried, next steps surfaced
4. Append a timestamped section to the file
5. If the daily file has 3+ sections (busy day), remind: "Consider running `/compound` to distill these into a solution doc."

## What to capture
- Decisions made and why (if non-obvious)
- Gotchas discovered — constraints, API behaviors, things that didn't work as expected
- Dead ends tried and abandoned
- Next steps or open questions that emerged

## What NOT to capture
- Obvious recaps ("we used BigQuery", "tests pass")
- Things already in solution docs or ADRs
- In-progress task state (use tasks for that)

## Output format

```markdown
# Daily Log — YYYY-MM-DD

## [HH:MM] [brief topic]
- [finding]
- [finding]
- [finding]
```

Each session appends a new `## [HH:MM]` section. Multiple sessions in a day stack vertically.

## Quality bar
- If you can't name one non-obvious finding, skip the entry — don't pad
- Raw is fine; `/compound` will polish
- A good entry is one where tomorrow-you would say "right, that's why we did it that way"
