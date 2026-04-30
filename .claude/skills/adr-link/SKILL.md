---
name: adr-link
description: After creating an ADR, run the cross-referencing checklist — update README Artifacts table, add Related Decisions section to source proposal, cross-link sibling ADRs to each other
---

# Skill: /adr-link — ADR Cross-Referencing Checklist

Every new ADR triggers the same three follow-ups: (1) the project README's Artifacts table needs a row, (2) the source proposal/brainstorm needs a "Related Decisions" entry, (3) sibling ADRs in the same series need backlinks. Manual every time. Easy to forget. Documented in `feedback_adr_cross_referencing.md`.

This skill runs the checklist.

## Trigger
User runs `/adr-link <ADR-XXXX-title.md>` — path to a newly created ADR. Single ADR or a comma-separated list.

## Behavior
1. Read the ADR(s). Extract: number, title, one-line summary (first non-empty line of Decision section), domain tag, source proposal/brainstorm references.
2. Find the project README. Default search order: same-project `README.md` → repo `README.md`. Confirm with user if ambiguous.
3. Find sibling ADRs (same domain tag OR adjacent ADR numbers in same project). Show user the candidates.
4. For each task, propose an exact edit. Show diff. User approves each before applying.

## The checklist

### 1. README Artifacts table
- Locate `## Artifacts` section in the project README.
- Propose new row:
  ```
  | <Title> | [`decisions/ADR-XXXX-...md`](relative-path) | <one-line purpose> |
  ```
- Insert in numerical order with sibling ADR rows.

### 2. Related Decisions in source proposal
- The ADR's Context section usually cites a proposal/brainstorm. Find that file.
- If it has a `## Related Decisions` section → append `- ADR-XXXX: <title> — <one-liner>`.
- If no such section → propose adding one near the top (after Status/Date) or at the bottom, user picks.

### 3. Sibling ADR backlinks
- For each sibling ADR (same series), check if it has a "Related ADRs" / "See also" section.
- If yes → append the new ADR.
- If no → flag, but don't add a section unilaterally to existing ADRs (low signal-to-noise).

## Output format

```
ADR-0050-argus-adk-tool-dependency-injection.md

Proposed updates:

[1] projects/argus/README.md — Artifacts table
    + | Tool Testability | [`decisions/ADR-0050-...md`](../../decisions/ADR-0050-...md) | `_underscore` DI pattern, no GCP in CI |
    Insert at line 70 (after ADR-0049 row). Apply? (y/n)

[2] docs/brainstorms/2026-04-25-argus-catalog-agent-requirements.md — Related Decisions
    + - ADR-0050: ADK tool dependency injection — testability via `_`-prefixed params
    Append to existing section at line 142. Apply? (y/n)

[3] Sibling ADRs (ADR-0046..0049) — backlinks
    ADR-0046 has "Related ADRs": will append
    ADR-0047 has no Related section: SKIP (don't add section to existing ADR)
    ADR-0048 has "Related ADRs": will append
    ADR-0049 has "Related ADRs": will append
    Apply backlinks to 0046/0048/0049? (y/n/pick)
```

## Quality Bar
- Show diffs, not just descriptions. User must see exactly what's about to land.
- One-line summaries — Artifacts table rows must stay scannable.
- Never insert a Related/Sibling section into an existing ADR that doesn't have one. Only append.
- If the ADR is `Proposed` (not Accepted), still link it — but flag status in the Artifacts row.

## Related Memory
`feedback_adr_cross_referencing.md` — the original checklist this skill automates.
