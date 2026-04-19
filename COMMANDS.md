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

### `/eval-design [LLM feature description]`
Scaffolds an evaluation framework: metrics, test sets, pass/fail gates, drift triggers.
> Best for: before shipping any LLM feature, establishing eval baselines

### `/prompt-review [prompt]`
Audits a prompt for clarity, injection risk, token efficiency, hallucination surface, and fallback behavior.
> Best for: pre-production prompt audits, red-teaming new prompts

### `/rag-design [use case]`
Designs a RAG architecture: chunking strategy, embedding model, retrieval pattern, re-ranking, and observability.
> Best for: new search/retrieval features, improving existing RAG quality

### `/agent-design [agent description]`
Designs an agentic loop: tools, memory, termination conditions, guardrails, and fallback paths.
> Best for: new autonomous agents, multi-step LLM workflows

### `/model-card [model or system description]`
Generates a model card template: overview, intended use, evals, limitations, and governance.
> Best for: shipping models or AI features that need documentation

### `/rollout [feature description]`
Designs a phased rollout: shadow → canary → limited GA → full GA, with eval gates and rollback triggers.
> Best for: any AI feature going to production

### `/pii-scan [system or data flow description]`
Maps PII exposure points across the AI data lifecycle: ingest, embed, prompt, log, cache, export.
> Best for: pre-launch privacy reviews, compliance audits

### `/runbook [system description]`
Generates an AI incident runbook covering model degradation, hallucination spikes, cost blowouts, and more.
> Best for: on-call prep, new AI systems going live

---

## Cheatsheet Update Commands

### `/update-cheatsheet-azure`
Web-searches for Azure AI/MLOps updates, diffs against the Azure cheatsheet, proposes changes for approval.

### `/update-cheatsheet-aws`
Web-searches for AWS AI/MLOps updates, diffs against the AWS cheatsheet, proposes changes for approval.

### `/update-cheatsheet-gcp`
Web-searches for GCP AI/MLOps updates, diffs against the GCP cheatsheet, proposes changes for approval.

### `/update-cheatsheet-opensource`
Web-searches for OSS AI/MLOps releases, diffs against the open-source cheatsheet, proposes changes for approval.

### `/cross-cloud [service or approach]`
Compares services or architectural approaches across Azure, AWS, and GCP using the cross-cloud comparison reference.

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
