# AI Architect — Command Reference

## Daily Workflow Commands

### `/review [design or description]`
Full architecture review. Produces a structured report with risk rating, findings table,
checklist assessment, and recommended ADRs.
> Best for: design docs, PR descriptions, new system proposals

### `/adr [topic or decision notes]`
Generates a complete ADR. Auto-assigns the next sequential number.
Checks existing decisions to avoid duplication.
> Best for: capturing decisions made in meetings, formalizing PoC outcomes

### `/rfc [proposed change]`
Scaffolds an RFC for broader team review. Lighter than an ADR — used before a decision
is made, to invite comment.
> Best for: proposing significant changes that need stakeholder input

### `/tradeoff [decision + options]`
Weighted trade-off matrix with a concrete recommendation.
> Best for: build/buy/borrow decisions, framework selection, vendor evaluation

### `/diagram [system description]`
Outputs a Mermaid diagram (architecture, sequence, or data flow — whichever fits).
Ready to paste into docs or Notion.
> Best for: quickly visualizing a described system or flow

### `/threat-model [component or system]`
AI-specific threat model covering prompt injection, data poisoning, PII leakage,
excessive agency, and supply chain risks.
> Best for: pre-launch security reviews, new agentic components

### `/cost-model [workload description]`
Rough order-of-magnitude cost estimate: token usage + infra.
Surfaces the top cost drivers and optimization levers.
> Best for: pre-proposal sizing, budget conversations with leadership

---

## Useful Claude Code Native Commands

```bash
# Open workspace in Claude Code
claude /path/to/ai-architect-workspace

# Start a session with explicit context
claude --context CLAUDE.md

# Run a command non-interactively
claude -p "/review [paste design here]"

# Continue last session
claude --continue
```

---

## File Conventions

| Type | Path | Naming |
|------|------|--------|
| ADR | `/decisions/` | `ADR-0001-short-title.md` |
| RFC | `/templates/rfc/` | `RFC-YYYY-MM-short-title.md` |
| Diagram | `/diagrams/` | `[system]-[type]-diagram.md` |
| Project brief | `/context/` | `[project-name]-brief.md` |
| Review report | `/projects/[name]/` | `review-YYYY-MM-DD.md` |
