---
name: checkpoint
description: Mid-task durability — dump current state and a next-step file before context fills, so the next session resumes without re-deriving where you were
---

# Skill: /checkpoint — Save State Before Compaction

Long sessions hit context limits. Compaction summaries are lossy — the next session may miss a half-finished edit, a decision-in-progress, or the exact file/line you were about to modify. The fix: write a durable checkpoint to disk before the cliff. `feedback_resource_check.md` warns about estimating token cost up front; this skill is the reactive complement — when you're already deep, save state.

## Trigger
User runs `/checkpoint` mid-session, OR you proactively suggest it when:
- Context is visibly heavy (long file reads, many tool results in window)
- About to start a substantial edit and a compaction notification has fired
- User says "context is getting full" / "let's checkpoint"

## Behavior
1. Identify the active workstream: what task, what files, what was just done, what's next.
2. Write a checkpoint file to `context/checkpoints/YYYY-MM-DD-HHMM-<topic>.md`.
3. If the work is code in flight, also write any unsaved edits to disk first — checkpoint is useless if the in-progress code is still in your head.
4. Return: file path + 3-bullet summary (what's saved, what's next, how to resume).

## Checkpoint file format

```markdown
# Checkpoint: <topic>
**Time:** YYYY-MM-DD HH:MM TZ
**Session intent:** [implement / debug / design / review]

## Current task
One sentence — what the user asked for, what we're doing.

## Where we are
Bullet list — concrete state. What files touched. What ran green. What's blocked.

## Next step (resume here)
The exact next action. File + line if it's an edit. Command + flags if it's a run.

## Loaded context that matters
- Decisions made this session (not yet in any ADR/doc)
- Constraints discovered this session (not yet in memory or code comments)
- Approaches tried + rejected this session

## Files modified this session (durable)
- path/to/file.py — what changed
- path/to/other.md — what changed

## Files modified this session (NOT YET WRITTEN — flush before resuming)
- (empty if all flushed)

## Open threads
- Question pending user answer
- Tool call awaiting result
- Background task running
```

## Output format

```
Checkpoint saved → context/checkpoints/2026-04-30-0942-argus-feedback-agent.md

Saved:
- Active task: wiring SC7 feedback_agent into orchestrator after approved-PROPOSE
- Next: edit app/agents/argus_orchestrator.py:124 to call feedback_agent after catalog_writer
- 2 files modified durable, 0 in-flight

Resume next session by reading the checkpoint file first.
```

## Quality Bar
- The "Next step" line must be unambiguous. Not "continue work on feedback agent" — instead "edit `app/agents/argus_orchestrator.py:124`, add `await feedback_agent.run(...)` after the `catalog_writer` call".
- Include enough decision context that the next session doesn't re-litigate. If you ruled out approach X, say so + why.
- Don't checkpoint trivial sessions. If the next step is "git commit and push", just do it.
- After writing the checkpoint, surface it to the user — they decide whether to compact, continue, or stop.

## When NOT to use
- Short sessions (<30 min, low context).
- Tasks with a natural commit point coming up — the commit is the checkpoint.
- Pure research/exploration with no in-flight edits.

## Related Memory
`feedback_resource_check.md` — pre-task estimation; this is the during-task complement.
