# Retail AI Enablement — Template Guide

This folder is a **reusable template** for a large-format retailer AI Enablement programme.
Fill in the placeholders, choose your cloud stack, and you have a complete programme brief.

---

## How to Use This Template

**Step 1 — Fill the placeholder table below.**
Open each file and replace every `[PLACEHOLDER]` with the client's actual value.

**Step 2 — Choose your cloud stack.**
Use the Cloud Mapping table to substitute cloud-specific service names into the PRDs.

**Step 3 — Confirm [ML_PARTNER] integration pattern.**
See the ML Partner section below. Pick the pattern that matches the client's situation.

**Step 4 — Mark optional PRDs.**
P3-B (Pharmacy Copilot) is only relevant if the retailer operates a pharmacy.
Delete or retain based on the client's business.

**Step 5 — Calibrate thresholds.**
Eval thresholds in the PRDs are universal starting points — good for any retailer.
The OKR ranges are directional; calibrate once baselines are established.

---

## Placeholder Index

| Placeholder | What to fill | Example (Kroger) |
|---|---|---|
| `[RETAILER]` | Company name | Kroger |
| `[RETAILER_DIGITAL]` | Digital storefront (website / app) | kroger.com / Kroger app |
| `[LOYALTY_PROGRAM]` | Name of the loyalty programme | Kroger Plus |
| `[LOYALTY_SCALE]` | Loyalty programme scale (households) | 60M+ households |
| `[ML_PARTNER]` | Analytics subsidiary or ML vendor | 84.51° |
| `[ML_PARTNER_TYPE]` | Subsidiary / third-party vendor / internal platform | Subsidiary |
| `[ML_PARTNER_SIGNALS]` | What signals [ML_PARTNER] provides | Replenishment, substitution, store layout, item location |
| `[ML_PARTNER_DELIVERY]` | How signals are delivered | REST APIs + pub/sub topics |
| `[CLOUD_PRIMARY]` | Primary cloud platform | Azure |
| `[CLOUD_SECONDARY]` | Secondary cloud (omit if single-cloud) | GCP |
| `[LLM_SERVICE]` | LLM API service | Azure OpenAI |
| `[LLM_PLATFORM]` | LLM + agent hosting platform | Microsoft Foundry |
| `[VECTOR_STORE]` | RAG / vector search service | Azure AI Search |
| `[AGENT_SERVICE]` | Managed agent hosting service | Foundry Agent Service |
| `[AGENT_FRAMEWORK]` | Agent orchestration framework | Microsoft Agent Framework |
| `[CONTENT_SAFETY]` | Output safety / content moderation service | Azure AI Content Safety |
| `[DATA_GOVERNANCE]` | Data lineage and PII classification platform | Microsoft Purview |
| `[MESSAGING_BUS]` | Event bus / pub-sub service | Azure Service Bus |
| `[ML_PLATFORM]` | ML training and experiment tracking | Azure Machine Learning |
| `[OBSERVABILITY]` | Monitoring and observability platform | Azure Monitor + Foundry Observability |
| `[CONTAINER_REGISTRY]` | Container image registry | Azure Container Registry |
| `[SECRET_STORE]` | Secrets management service | Azure Key Vault |
| `[COST_MANAGEMENT]` | Cloud cost visibility and attribution tool | Azure Cost Management |
| `[AGENT_IDENTITY]` | Managed identity system for agents | Entra Agent ID |
| `[ERP_SYSTEM]` | ERP system for order submission | SAP / Oracle |
| `[WMS_SYSTEM]` | Warehouse management system | [Client WMS] |
| `[MEDIA_NETWORK]` | Retail media network name | KPM (Kroger Precision Marketing) |
| `[COMPETITOR_MEDIA]` | Competing retail media networks | Walmart Connect, Amazon Ads |
| `[PHARMACY_PRESENT]` | Does retailer have a pharmacy? (Yes/No) | Yes |
| `[DATE]` | Document date | 2026-04-18 |

---

## Cloud Mapping Table

Use this table to substitute cloud-specific service names when the client's primary cloud differs from Azure.

| Capability | Azure | AWS | GCP |
|---|---|---|---|
| LLM API | Azure OpenAI | Amazon Bedrock | Vertex AI (Gemini) |
| Agent hosting | Foundry Agent Service | Bedrock Agents | Vertex AI Agent Builder |
| Agent framework | Microsoft Agent Framework | Bedrock Agents Framework | Agent Development Kit (ADK) |
| Vector / RAG search | Azure AI Search | Amazon OpenSearch / Knowledge Bases | Vertex AI Search |
| ML platform | Azure Machine Learning | Amazon SageMaker | Vertex AI |
| Content safety | Azure AI Content Safety | Amazon Bedrock Guardrails | Vertex AI Safety filters |
| Data governance / PII | Microsoft Purview | AWS Macie + Glue Data Catalog | Google Cloud Data Catalog + DLP |
| Event bus / pub-sub | Azure Service Bus | Amazon SQS / SNS / EventBridge | Google Cloud Pub/Sub |
| Container registry | Azure Container Registry | Amazon ECR | Google Artifact Registry |
| Secret store | Azure Key Vault | AWS Secrets Manager | Google Secret Manager |
| Cost management | Azure Cost Management | AWS Cost Explorer | Google Cloud Billing |
| Observability | Azure Monitor | Amazon CloudWatch | Google Cloud Monitoring |
| Agent identity | Entra Agent ID | IAM roles (service accounts) | GCP Service Accounts + Workload Identity |
| Health data (HIPAA) | Azure Health Data Services | AWS HealthLake | Google Cloud Healthcare API |
| Vision / multimodal | Azure AI Vision | Amazon Rekognition | Vertex AI Vision |

---

## [ML_PARTNER] Integration Patterns

Choose the pattern that matches the client's situation. Update architecture sections in all PRDs accordingly.

### Pattern A — Analytics Subsidiary (e.g. 84.51° / Kroger)

- [ML_PARTNER] is a wholly-owned or majority-owned subsidiary
- Signals available via internal APIs and pub/sub topics
- Data governance boundary still exists — treat as a managed third party
- Fallback required: [ML_PARTNER] has its own roadmap; Kroger's capability must stand independently

**Implication for PRDs:** Include [ML_PARTNER] API adapters as tool calls; build fallback to internal signals if [ML_PARTNER] API unavailable.

### Pattern B — Third-Party ML Vendor

- [ML_PARTNER] is a commercial analytics vendor (e.g. dunnhumby, Nielsen, 1WorldSync)
- Signals delivered via contracted API; rate limits and SLAs apply
- Data governance boundary is contractual — PII terms must be reviewed before use in AI systems

**Implication for PRDs:** All PRD sections referencing [ML_PARTNER] require SLA and rate limit confirmation before architecture is finalised. Replace "enrichment layer" language with "contracted signal source."

### Pattern C — Internal ML Platform

- Retailer has its own ML/data science team producing recommendations internally
- Signals available via internal microservices or data warehouse
- Tightest integration possible; also highest maintenance burden

**Implication for PRDs:** Replace [ML_PARTNER] API calls with internal service endpoints. Remove fallback language — internal platform is a dependency, not enrichment.

---

## Optional PRDs

| PRD | Optional? | Condition |
|---|---|---|
| P3-B: Pharmacy AI Copilot | Yes | Only if retailer operates a pharmacy |
| P2-B: Retail Media AI | Yes | Only if retailer operates a retail media / advertising network |
| P3-A: Fresh & Perishables | Recommended | Any retailer with significant fresh/produce department |
| P3-C: Supply Chain Disruption Agent | Recommended | Any retailer with complex supplier network |

---

## Thresholds — Universal vs Calibrate

### Universal (do not change)

These thresholds are grounded in industry standards and regulatory risk. They apply to any retailer.

| Threshold | Value | Reason |
|---|---|---|
| Dietary constraint compliance | ≥ 0.97 | Regulatory and health liability |
| Groundedness (SKUs exist in catalogue) | 100% | No hallucinated products |
| PII exposure incidents | 0 | Contractual and regulatory |
| Content Safety block rate (customer-facing) | ≤ 0.1% | Brand and regulatory |
| Inventory accuracy (no OOS recommendations) | ≥ 0.98 | Customer trust |

### Calibrate once baseline is known

| Threshold | Default | Notes |
|---|---|---|
| Recommendation relevance | ≥ 0.82 | Adjust based on assortment complexity |
| Auto-approval accuracy (replenishment) | ≥ 0.90 | Adjust based on supplier reliability |
| Knowledge Agent resolution rate | 60–80% | Adjust based on corpus quality |
| Basket size uplift target | +3–8% | Calibrate from A/B baseline |
| Associate DAU rate | 30–60% | Calibrate from pilot store cohort |

---

## Files in This Template

| File | What it is |
|---|---|
| `TEMPLATE-GUIDE.md` | This file — placeholder index, cloud mapping, usage instructions |
| `README.md` | Project structure and tier map |
| `brief.md` | Full technical project brief |
| `executive-brief.md` | Executive summary (external audience) |
| `org-design.md` | Team structure, ownership matrix, RACI |
| `okrs.md` | OKRs across 5 objectives, 18-month horizon |
| `prds/P0-A-ai-enablement-platform.md` | AI Enablement Platform PRD |
| `prds/P0-B-ai-governance-framework.md` | AI Governance Framework PRD |
| `prds/P1-A-associate-copilot.md` | Store Associate AI Copilot PRD |
| `prds/P1-B-agentic-replenishment.md` | Agentic Replenishment Orchestration PRD |
| `prds/P1-C-knowledge-agent.md` | Enterprise Knowledge Agent PRD |
| `prds/P1-D-engineering-ai-enablement.md` | Engineering AI Enablement PRD |
| `prds/P2-A-conversational-shopping-assistant.md` | Conversational Shopping Assistant PRD |
| `prds/P2-B-retail-media-ai.md` | Retail Media AI Enhancement PRD |
| `prds/P3-A-fresh-perishables.md` | Fresh & Perishables Waste Reduction PRD |
| `prds/P3-B-pharmacy-copilot.md` | Pharmacy AI Copilot PRD *(optional)* |
| `prds/P3-C-supply-chain-agent.md` | Supply Chain Disruption Agent PRD |
