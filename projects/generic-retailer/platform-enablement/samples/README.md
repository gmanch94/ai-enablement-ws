# Platform Enablement — Sample Artifacts

These are **filled-in examples** of the blank templates in `platform-enablement/`.
Use them to understand how to complete each artifact for a real client engagement.

---

## Fictional Client: MidWest Grocery

All samples use a fictional retailer so examples are concrete without referencing any real company.

| Placeholder | Sample Value |
|---|---|
| `[RETAILER]` | MidWest Grocery |
| `[ML_PARTNER]` | DataInsight Co. (analytics subsidiary) |
| `[CLOUD_PRIMARY]` | Azure |
| `[LLM_PLATFORM]` | Microsoft Foundry |
| `[VECTOR_STORE]` | Azure AI Search |
| `[AGENT_SERVICE]` | Foundry Agent Service |
| `[CONTENT_SAFETY]` | Azure AI Content Safety |
| `[DATA_GOVERNANCE]` | Microsoft Purview |
| `[LOYALTY_PROGRAM]` | MidWest Rewards |
| `[LOYALTY_SCALE]` | 12M+ households |
| `[ERP_SYSTEM]` | SAP S/4HANA |
| `[RETAILER_TAG]` | `mwg` |

---

## Sample Index

### Sample A — Store Associate AI Copilot (P1-A, Tier 2)

Internal, advisory RAG agent. Good example of a typical Tier 2 governance profile.

| File | What it shows |
|---|---|
| [p1a-risk-tier-intake.md](p1a-risk-tier-intake.md) | How to classify an internal RAG + live-API agent as Tier 2 |
| [p1a-model-card.md](p1a-model-card.md) | Completed model card for a production RAG agent |
| [p1a-pii-handling-checklist.md](p1a-pii-handling-checklist.md) | PII checklist when using ML partner signals (no direct loyalty PII) |

### Sample B — Conversational Shopping Assistant (P2-A, Tier 3)

Customer-facing agent with health/dietary claims and loyalty data. Shows the full Tier 3 governance stack including Responsible AI Assessment.

| File | What it shows |
|---|---|
| [p2a-risk-tier-intake.md](p2a-risk-tier-intake.md) | How to classify a customer-facing agent as Tier 3 |
| [p2a-model-card.md](p2a-model-card.md) | Completed model card for a customer-facing agentic system |
| [p2a-pii-handling-checklist.md](p2a-pii-handling-checklist.md) | PII checklist for direct loyalty profile usage at scale |
| [p2a-responsible-ai-assessment.md](p2a-responsible-ai-assessment.md) | Full 9-section RAI assessment including red team summary |

---

## How to Use These Samples

1. Open the blank template (e.g. `../model-card-template.md`)
2. Open the corresponding sample (e.g. `p1a-model-card.md`)
3. Use the sample as a reference for what level of detail is expected
4. Replace all sample values with your client's actual information
5. Delete this samples folder from client deliverables — it is internal reference only
