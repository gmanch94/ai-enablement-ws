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
│   ├── cloud-ai-course-business-cheatsheet.md  ← Business/non-technical AI reference
│   ├── opensource-ai-mlops-cheatsheet.md  ← Open-source LLM, serving, RAG, eval, MLOps tools (cloud-agnostic)
│   ├── prompt-engineering-cookbook.md      ← 6 principles, 8 patterns, anti-patterns, eval bar
│   ├── feature-engineering-cookbook.md     ← Feature taxonomy, 12 highest-ROI patterns, anti-patterns
│   ├── llm-vendor-comparison.html          ← Interactive vendor matrix + risk-weighted scoring
│   ├── ai-governance-framework.md          ← General AI governance (NIST AI RMF, EU AI Act, GDPR)
│   ├── ai-hr-governance-framework.md       ← HR-specific overlay (EEOC 4/5ths, GDPR Art. 22, NYC LL 144, IL AIVIA)
│   └── llm-data-strategy.md               ← Data readiness for LLM-based systems (context window vs RAG, eval corpus, distillation economics, source governance)
│
├── decisions/                         ← Architecture Decision Records (ADR-0001 – ADR-0041)
│   ├── ADR-0001-langgraph-multi-agent-orchestration.md
│   ├── ADR-0002-retailer-x-azure-primary-ai-platform.md
│   ├── ADR-0003-retailer-x-agentic-replenishment.md
│   ├── ADR-0004 – ADR-0012  (Azure: LLM, Agents, RAG, ML Platform, Data, Compute, Orchestration, Observability, Governance)
│   ├── ADR-0013 – ADR-0021  (AWS:   LLM, Agents, RAG, ML Platform, Data, Compute, Orchestration, Observability, Governance)
│   ├── ADR-0022 – ADR-0030  (GCP:   LLM, Agents, RAG, ML Platform, Data, Compute, Orchestration, Observability, Governance)
│   ├── ADR-0031-claude-enterprise-rollout.md  [llm][governance] Proposed
│   └── ADR-0032 – ADR-0041  (OSS:   LLM Selection, Inference, Agents, RAG, Vector DBs, Eval, Observability, MLOps, Fine-Tuning, SDKs)
│
├── templates/
│   ├── adr/
│   │   └── ADR-TEMPLATE.md            ← Blank ADR template
│   ├── eval/
│   │   └── model-evaluation-canvas.html    ← 7-question pre-deployment model review canvas
│   └── governance/
│       ├── genai-risk-checklist.html       ← 3-question risk classifier + tier-scoped checklist
│       ├── governance-playbook-general.html ← Before-you-deploy 13-item governance playbook
│       ├── bias-audit-general.html         ← General-purpose bias audit (NIST AI RMF + EEOC)
│       └── bias-audit-hr.html              ← HR-specific bias audit with EEOC 4/5ths calc
│
├── .claude/commands/                  ← Slash commands (type /command-name in Claude Code)
│   ├── review.md                      ← /review
│   ├── adr.md                         ← /adr
│   ├── tradeoff.md                    ← /tradeoff
│   ├── threat-model.md                ← /threat-model
│   ├── eval-design.md                 ← /eval-design
│   ├── prompt-review.md               ← /prompt-review
│   ├── rag-design.md                  ← /rag-design
│   ├── agent-design.md                ← /agent-design
│   ├── model-card.md                  ← /model-card
│   ├── rollout.md                     ← /rollout
│   ├── pii-scan.md                    ← /pii-scan
│   ├── runbook.md                     ← /runbook
│   ├── update-cheatsheet-azure.md     ← /update-cheatsheet-azure
│   ├── update-cheatsheet-aws.md       ← /update-cheatsheet-aws
│   ├── update-cheatsheet-gcp.md       ← /update-cheatsheet-gcp
│   └── update-cheatsheet-opensource.md ← /update-cheatsheet-opensource
│                                        (note: /rfc, /diagram, /cost-model, /cross-cloud are Claude-native — no skill file needed)
│
├── context/                           ← Active project briefs (short-lived, drop here when working a task)
├── diagrams/                          ← Mermaid diagrams
└── projects/                          ← Per-project artefacts
    ├── retailer-x/                    ← Retailer-X AI enablement work
    │   ├── brief.md / executive-brief.md / okrs.md / org-design.md
    │   ├── platform-enablement/       ← Runbooks, guides, templates (onboarding, eval, PII, etc.)
    │   └── prds/
    └── generic-retailer/              ← Generic retailer pattern (reusable)
        ├── brief.md / executive-brief.md / okrs.md / org-design.md
        ├── platform-enablement/       ← Same runbook set as retailer-x
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
| `/eval-design` | Scaffold evaluation framework — metrics, test sets, drift triggers |
| `/prompt-review` | Audit prompt for clarity, injection risk, token efficiency, hallucination surface |
| `/rag-design` | Design RAG architecture — chunking, embedding, retrieval, re-ranking |
| `/agent-design` | Design agentic loop — tools, memory, termination, guardrails, fallbacks |
| `/model-card` | Generate model card — overview, intended use, evals, limitations, governance |
| `/rollout` | Design phased rollout — shadow → canary → limited GA → full GA |
| `/pii-scan` | Map PII exposure across AI data lifecycle |
| `/runbook` | Generate AI incident runbook — degradation, hallucination, cost blowout |
| `/update-cheatsheet-azure` | Web-search Azure AI updates, diff, propose changes |
| `/update-cheatsheet-aws` | Web-search AWS AI updates, diff, propose changes |
| `/update-cheatsheet-gcp` | Web-search GCP AI updates, diff, propose changes |
| `/update-cheatsheet-opensource` | Web-search OSS AI/MLOps releases, diff, propose changes |
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
| [Open-Source AI/MLOps](reference/opensource-ai-mlops-cheatsheet.md) | OSS LLMs, inference engines, RAG, eval, observability, MLOps (cloud-agnostic) |

Cheatsheets are verified against official release notes and event announcements (re:Invent, Google Cloud Next, Microsoft Ignite/Build). Last verified: **April 2026**.

---

## Operational Cookbooks, Frameworks, and Templates

Architect-grade reference and templates for prompt/feature engineering, vendor selection, model evaluation, governance, and bias audit. Pair with the matching skills in the table above (e.g., `feature-engineering-cookbook.md` ↔ `/dataset-readiness` + `/eval-design`; `bias-audit-*.html` ↔ `/red-team`; `genai-risk-checklist.html` ↔ `/threat-model`).

| Artifact | Type | Companion skill(s) |
|---|---|---|
| [`reference/prompt-engineering-cookbook.md`](reference/prompt-engineering-cookbook.md) | Cookbook | `/prompt-review`, `/eval-design` |
| [`reference/feature-engineering-cookbook.md`](reference/feature-engineering-cookbook.md) | Cookbook | `/dataset-readiness`, `/eval-design` |
| [`reference/llm-vendor-comparison.html`](reference/llm-vendor-comparison.html) | Interactive matrix | `/tradeoff`, ADR-0031 |
| [`reference/ai-governance-framework.md`](reference/ai-governance-framework.md) | Framework | `/threat-model`, `/red-team`, `/model-card` |
| [`reference/ai-hr-governance-framework.md`](reference/ai-hr-governance-framework.md) | Framework (sector overlay) | `/threat-model`, `/red-team` (HR/employment context) |
| [`templates/eval/model-evaluation-canvas.html`](templates/eval/model-evaluation-canvas.html) | Canvas | `/eval-design`, `/review` |
| [`templates/governance/genai-risk-checklist.html`](templates/governance/genai-risk-checklist.html) | Tier-scoped checklist | `/threat-model`, `/red-team`, `/pii-scan` |
| [`templates/governance/governance-playbook-general.html`](templates/governance/governance-playbook-general.html) | Playbook | `/review`, `/model-card` |
| [`templates/governance/bias-audit-general.html`](templates/governance/bias-audit-general.html) | Audit template | `/red-team`, `/eval-design` |
| [`templates/governance/bias-audit-hr.html`](templates/governance/bias-audit-hr.html) | Audit template (HR) | `/red-team`, `/eval-design` (HR context) |

### Automated Monitoring

A monthly scheduled agent ([`ai-cheatsheet-monitor-all-clouds`](https://claude.ai/code/scheduled/trig_01CjsAenUy7bcsWnypCwp2cT)) clones this repo on the 1st of each month, searches for updates across all three clouds, and produces a diff report. Run `/update-cheatsheet-azure`, `/update-cheatsheet-aws`, or `/update-cheatsheet-gcp` to review and apply flagged changes.

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
