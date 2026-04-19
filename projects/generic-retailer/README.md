# [RETAILER] AI Enablement — Template

Reusable Senior AI Architect programme brief for a large-format retailer's funded AI mandate.

**See [`TEMPLATE-GUIDE.md`](TEMPLATE-GUIDE.md) before editing — fill placeholders, choose cloud stack, confirm [ML_PARTNER] pattern.**

## Status

Template — customise before use.

## Folder Structure

```
projects/generic-retailer/
├── TEMPLATE-GUIDE.md                    ← start here; placeholder index + cloud mapping
├── README.md                            ← this file
├── brief.md                             ← full technical project brief
├── executive-brief.md                   ← executive summary (external audience)
├── org-design.md                        ← team structure, ownership matrix, RACI
├── okrs.md                              ← OKRs across 5 objectives, 18-month horizon
├── platform-enablement/                 ← governance & ops artifacts for platform team
│   ├── README.md
│   ├── risk-tier-intake.md
│   ├── model-card-template.md
│   ├── pii-handling-checklist.md
│   ├── responsible-ai-assessment.md
│   ├── eval-baseline-guide.md
│   ├── sdk-standards.md
│   ├── prompt-versioning-guide.md
│   ├── cost-tagging-standards.md
│   ├── agent-identity-runbook.md
│   ├── model-rollback-runbook.md
│   ├── incident-response-guide.md
│   ├── onboarding-guide.md
│   └── cicd-pipeline-template.md
└── prds/
    ├── P0-A-ai-enablement-platform.md       ← AI Enablement Platform PRD
    ├── P0-B-ai-governance-framework.md      ← AI Governance Framework PRD
    ├── P1-A-associate-copilot.md            ← Store Associate AI Copilot PRD
    ├── P1-B-agentic-replenishment.md        ← Agentic Replenishment Orchestration PRD
    ├── P1-C-knowledge-agent.md             ← Enterprise Knowledge Agent PRD
    ├── P1-D-engineering-ai-enablement.md   ← Engineering AI Enablement PRD
    ├── P2-A-conversational-shopping-assistant.md  ← Conversational Shopping Assistant PRD
    ├── P2-B-retail-media-ai.md             ← Retail Media AI Enhancement PRD
    ├── P3-A-fresh-perishables.md           ← Fresh & Perishables Waste Reduction PRD
    ├── P3-B-pharmacy-copilot.md            ← Pharmacy AI Copilot PRD (optional)
    └── P3-C-supply-chain-agent.md          ← Supply Chain Disruption Agent PRD
```

## Project Tiers

| Tier | Projects | Target Timeline |
|---|---|---|
| P0 — Foundation | AI Enablement Platform, AI Governance Framework | Month 0–3 |
| P1 — Internal High ROI | Associate Copilot, Agentic Replenishment, Knowledge Agent, Engineering AI Enablement | Month 2–9 |
| P2 — Customer-Facing | Conversational Shopping Assistant, Retail Media AI | Month 9–15 |
| P3 — Specialised | Fresh & Perishables, Pharmacy Copilot *(optional)*, Supply Chain Agent | Month 15+ |

## Key Context

- **Cloud:** `[CLOUD_PRIMARY]` primary, `[CLOUD_SECONDARY]` secondary (update or remove if single-cloud)
- **Org model:** Federated AI — central platform team sets guardrails, BU teams own delivery
- **ML Signals:** `[ML_PARTNER]` provides `[ML_PARTNER_SIGNALS]` via `[ML_PARTNER_DELIVERY]` — enrichment layer, not a hard dependency
- **Mandate:** Funded — build shared capability, not disconnected pilots
- **Constraint:** Governance must be a platform feature, not a manual process

## Guiding Principle

> Don't build AI features. Build AI capability.

Every project sits on a shared platform, shares governance, and compounds value over time.
