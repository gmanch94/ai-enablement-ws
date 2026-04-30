---
name: adr
description: Generate a new Architecture Decision Record from a topic, decision description, or rough notes
---

# Skill: /adr — Generate Architecture Decision Record

## Trigger
User runs `/adr` followed by a topic, decision description, or rough notes.

## Behavior
1. Check `/decisions/` for existing ADRs — assign next sequential number
2. Identify the domain tag from: [llm] [mlops] [rag] [governance] [infra]
3. Ask ONE clarifying question if the decision is ambiguous — otherwise proceed
4. Generate a complete ADR using the template at `/templates/adr/ADR-TEMPLATE.md`
5. Surface 2–3 alternatives that should be considered if user hasn't named them
6. Flag any risks with [RISK: HIGH/MED/LOW]

## Output
- Full ADR document ready to save as `/decisions/ADR-XXXX-short-title.md`
- End with: "Save this as `ADR-XXXX-title.md`? I can also generate a follow-up ADR for any of the alternatives."

## Quality Bar
Every ADR must be actionable. If the context section is vague, say so and ask for
the specific driver (business need, technical constraint, or incident) before proceeding.
Never produce an ADR that reads like a blog post — it should read like a decision log.
