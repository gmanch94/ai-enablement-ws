---
name: compound
description: Capture session learnings as a structured solution doc in docs/solutions/ — the knowledge flywheel
---

# Skill: /compound — Capture Session Learnings

Run after completing any meaningful design session, POC, ADR, or implementation work. Extracts what was learned and writes it to `docs/solutions/` so future sessions start with context instead of re-deriving it.

## Trigger
User runs `/compound` after completing a session of work, OR at natural breakpoints in a multi-day effort.

## Behavior
1. Review the session work: what was built, decided, or discovered
2. Identify what is non-obvious — patterns, gotchas, dead ends, constraints that aren't visible in the code or docs
3. Write a solution doc to `docs/solutions/YYYY-MM-DD-<topic>-solution.md`
4. Check if any memory entries in `MEMORY.md` should be updated or added based on learnings
5. Surface any new open questions or follow-up ADRs the work revealed

## What to capture (the non-obvious stuff)

| Category | Capture when... |
|----------|----------------|
| **Why this approach** | The chosen pattern wasn't obvious — alternatives were considered and rejected |
| **Gotchas** | Something didn't work as expected; a constraint emerged mid-session |
| **Validated assumptions** | Something that was uncertain before this session is now confirmed with evidence |
| **Dead ends** | Approach tried and abandoned, and why — saves future sessions from retrying |
| **Constraints discovered** | Platform limits, API behaviors, infra requirements that aren't in docs |
| **Open questions** | Unanswered questions that the next session should start with |

## What NOT to capture
- Information already in ADRs, proposals, or code comments
- Things derivable from reading the current state of the files
- Generic summaries of what was done (the commit/PR captures that)

## Output Format

### Solution: [Topic]
**Date:** [today]  
**Session type:** [design / POC / ADR / debug / review]  
**Related artifacts:** [links to ADRs, proposals, brainstorms, PRs]

---

#### What was built / decided
One paragraph. What exists now that didn't before, or what is resolved now that wasn't.

#### Why this approach (not the obvious one)
What alternatives were ruled out and why. What constraint forced this choice.

#### Gotchas & constraints discovered
Bullet list. Each item: what it is, where it bites you, how to avoid it.

#### Validated assumptions
What we believed before that we now have evidence for (or against).

#### Dead ends (don't retry these)
What was tried, what failed, why. Short — enough to recognize the trap.

#### Open questions for next session
What's still unresolved. What the next session should start by answering.

---

## Quality Bar
- If you can't name one non-obvious finding, the session may not warrant a solution doc — skip it
- Don't pad with obvious recaps — "we decided to use BigQuery" is not a learning if it was always the plan
- A useful solution doc is one where future-you, picking this up cold in 3 months, would say "glad I read that"
