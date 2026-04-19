# AI Architect Workspace

A structured working environment for AI architecture, MLOps design, and AI enablement — built for use with [Claude Code](https://claude.ai/code).

---

## What This Is

A personal knowledge base and decision record for an AI Architect. Contains:
- **Reference cheatsheets** for Azure, AWS, and GCP AI/MLOps stacks (kept current via automated monthly monitoring)
- **Architecture Decision Records (ADRs)** for key design choices
- **Custom Claude commands** for architecture review, threat modelling, cost estimation, and more
- **Diagrams and project artefacts** organised by concern

---

## Folder Structure

```
ai-enablement-ws/
├── CLAUDE.md                          ← Claude Code instructions (auto-loaded every session)
├── COMMANDS.md                        ← Quick reference for all custom commands
│
├── reference/                         ← Stable reference material (loaded on demand, not at session start)
│   ├── azure-ai-mlops-cheatsheet.md   ← Azure / Microsoft Foundry AI stack
│   ├── aws-ai-mlops-cheatsheet.md     ← AWS AI/MLOps stack
│   ├── gcp-ai-mlops-cheatsheet.md     ← GCP / Vertex AI stack
│   ├── cross-cloud-ai-comparison.md   ← Side-by-side service mapping across all three clouds
│   └── cloud-ai-course-business-cheatsheet.md  ← Business/non-technical AI reference
│
├── decisions/                         ← Architecture Decision Records
│   ├── ADR-0001-langgraph-multi-agent-orchestration.md
│   ├── ADR-0002-kroger-azure-primary-ai-platform.md
│   └── ADR-0003-kroger-agentic-replenishment.md
│
├── templates/
│   └── adr/
│       └── ADR-TEMPLATE.md            ← Blank ADR template
│
├── skills/                            ← Skill files for Claude commands (subset of commands below)
│   ├── review.md                      ← /review
│   ├── adr.md                         ← /adr
│   ├── tradeoff.md                    ← /tradeoff
│   ├── threat-model.md                ← /threat-model
│   ├── update-cheatsheet.md           ← /update-cheatsheet (Azure)
│   ├── update-cheatsheet-aws.md       ← /update-cheatsheet-aws
│   └── update-cheatsheet-gcp.md       ← /update-cheatsheet-gcp
│                                        (note: /rfc, /diagram, /cost-model are Claude-native — no skill file needed)
│
├── context/                           ← Active project briefs (short-lived, drop here when working a task)
├── diagrams/                          ← Mermaid diagrams
└── projects/                          ← Per-project artefacts
    ├── kroger/                        ← Kroger AI enablement work
    │   ├── brief.md / executive-brief.md / okrs.md / org-design.md
    │   ├── platform-enablement/       ← Runbooks, guides, templates (onboarding, eval, PII, etc.)
    │   └── prds/
    └── generic-retailer/              ← Generic retailer pattern (reusable)
        ├── brief.md / executive-brief.md / okrs.md / org-design.md
        ├── platform-enablement/       ← Same runbook set as kroger
        └── prds/
```

---

## Custom Commands

Run these with `/command-name` in any Claude Code session:

| Command | What it does |
|---|---|
| `/review` | Full architecture review against the standard checklist |
| `/adr` | Generate a new ADR from a description |
| `/rfc` | Scaffold an RFC doc for a proposed system change |
| `/tradeoff` | Structured trade-off analysis (build/buy/borrow) |
| `/diagram` | Suggest a Mermaid diagram for a described system |
| `/threat-model` | AI-specific threat model for a described component |
| `/cost-model` | Estimate token + infra cost for an AI workload |
| `/update-cheatsheet` | Web-search Azure AI updates, diff, propose changes |
| `/update-cheatsheet-aws` | Web-search AWS AI updates, diff, propose changes |
| `/update-cheatsheet-gcp` | Web-search GCP AI updates, diff, propose changes |
| `/cross-cloud` | Compare services across Azure, AWS, and GCP |

---

## Reference Cheatsheets

Each cheatsheet covers 1st-party services and key SDKs, organised by concern:

| Cheatsheet | Coverage |
|---|---|
| [Azure AI/MLOps](reference/azure-ai-mlops-cheatsheet.md) | Microsoft Foundry, Azure ML, Azure OpenAI, Agent Services, Governance |
| [AWS AI/MLOps](reference/aws-ai-mlops-cheatsheet.md) | Amazon Bedrock, SageMaker AI, AgentCore, Nova, Guardrails |
| [GCP AI/MLOps](reference/gcp-ai-mlops-cheatsheet.md) | Vertex AI, Gemini, Agent Engine, ADK, BigQuery, Model Armor |
| [Cross-Cloud Comparison](reference/cross-cloud-ai-comparison.md) | Service-to-service mapping and key differentiators |
| [Cloud AI — Business](reference/cloud-ai-course-business-cheatsheet.md) | Non-technical / executive reference for cloud AI concepts |

Cheatsheets are verified against official release notes and event announcements (re:Invent, Google Cloud Next, Microsoft Ignite/Build). Last verified: **April 2026**.

### Automated Monitoring

A monthly scheduled agent ([`ai-cheatsheet-monitor-all-clouds`](https://claude.ai/code/scheduled/trig_01CjsAenUy7bcsWnypCwp2cT)) clones this repo on the 1st of each month, searches for updates across all three clouds, and produces a diff report. Run `/update-cheatsheet`, `/update-cheatsheet-aws`, or `/update-cheatsheet-gcp` to review and apply flagged changes.

---

## ADR Conventions

- **Location:** `/decisions/ADR-XXXX-short-title.md`
- **Status:** `Proposed | Accepted | Deprecated | Superseded`
- **Required sections:** Context, Decision, Consequences, Alternatives Considered
- **Domain tags:** `[llm]` `[mlops]` `[rag]` `[governance]` `[infra]`

---

## Architecture Principles

1. **Separation of concerns** — LLM layer ≠ orchestration layer ≠ data layer
2. **Observability first** — traces, logs, and evals from day one
3. **Graceful degradation** — AI features must have fallback paths
4. **Governance by design** — audit trails, PII handling, model versioning are not afterthoughts
5. **Async over sync** — prefer event-driven patterns for AI workloads
