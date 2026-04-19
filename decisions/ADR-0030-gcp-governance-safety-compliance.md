# ADR-0030: GCP — Governance, Safety & Compliance

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [governance]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

Enterprise AI workloads on GCP require governance at multiple layers: LLM input/output safety filtering, training data PII detection and lineage, data exfiltration prevention, and fine-grained identity and access management for ML workloads. Governance must be designed in from the start — not added after an incident. This is architecture principle #4 in CLAUDE.md.

## Decision

We will use:
- **Model Armor** for LLM safety guardrails — prompt injection detection, content filtering, and grounding checks across all Gemini and third-party model calls
- **Cloud DLP** (Data Loss Prevention) for automated PII detection, classification, and de-identification in training datasets and RAG sources
- **Dataplex** as the unified data governance layer — cataloguing, lineage tracking, data quality rules, and classification across GCS, BigQuery, and other GCP data assets
- **VPC Service Controls** for perimeter-based data exfiltration prevention around Vertex AI, BigQuery, and GCS
- **Cloud IAM + Workload Identity Federation** for least-privilege access to ML workloads and CI/CD pipelines
- **BigQuery Governance** (Preview) for training data asset discovery, classification, and quality enforcement within BigQuery

## Rationale

1. **Model Armor for consistent LLM safety** — applies safety policies uniformly across all Gemini model tiers and third-party models (Llama, Mistral) on Vertex AI. Without Model Armor, each model deployment requires separate safety configuration — a governance gap that grows with the model catalog.
2. **Cloud DLP for automated PII handling** — manual PII tracking does not scale for enterprise datasets. Cloud DLP scans GCS and BigQuery assets automatically, classifies findings (names, SSNs, credit card numbers), and can de-identify in-place before training data is consumed.
3. **Dataplex for data lineage and quality** — training data lineage (raw source → curated → training dataset → model) must be traceable for compliance and debugging. Dataplex provides this lineage automatically across GCP data assets, with data quality rules that gate data into the curated zone.
4. **VPC Service Controls as the hard perimeter** — even with IAM correctly configured, data exfiltration via compromised credentials or misconfigured API calls is a risk. VPC Service Controls enforces that Vertex AI, BigQuery, and GCS API calls can only occur within the defined service perimeter — a network-level control that IAM alone cannot provide.
5. **Workload Identity Federation for CI/CD** — service account keys in CI/CD pipelines are a persistent security risk. Workload Identity Federation allows GitHub Actions and Cloud Build to impersonate service accounts using short-lived OIDC tokens without key files.

## Consequences

### Positive
- Model Armor applies uniformly across all model families — no per-model safety configuration gap
- Cloud DLP findings integrate with Security Command Center — PII events surface in the centralised security view
- Workload Identity Federation eliminates service account key rotation overhead from CI/CD pipelines

### Negative / Trade-offs
- Model Armor adds latency per inference call (typically 30–100ms) — budget for this in p99 latency targets for customer-facing applications
- VPC Service Controls require careful policy authoring — overly restrictive perimeters can block legitimate service-to-service calls; test in `dry-run` mode before enforcing
- BigQuery Governance is Preview — do not rely on it as the sole governance mechanism for regulated training data; use Dataplex (GA) as the primary layer

### Risks
- [RISK: HIGH] VPC Service Controls misconfiguration — an overly broad `deny` policy can break Vertex AI pipeline steps that access GCS or BigQuery; always validate perimeter changes in `dry-run` mode for 48 hours before enforcement
- [RISK: MED] Cloud DLP scan latency for large datasets — DLP scans are asynchronous; enforce a data quarantine pattern (data lands in a staging bucket, DLP scans, findings are reviewed, data promoted to curated bucket only on pass)
- [RISK: LOW] Model Armor false positives on legitimate prompts — tune confidence thresholds per deployment tier; log all filtered requests to Cloud Logging for review and threshold calibration

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Third-party content safety (Guardrails.ai, NeMo) | No GCP-native integration, separate vendor data egress, additional ops burden; Model Armor covers the requirement within the GCP trust boundary |
| Custom PII scanning with spaCy/Presidio | Valid supplemental approach for specialised entities; not a replacement for Cloud DLP's managed, scalable detection across diverse PII categories |
| Cloud IAM alone (no VPC Service Controls) | IAM controls identity-based access; VPC Service Controls adds network-perimeter protection against exfiltration even with valid credentials; both are required |
| Collibra / Alation for data governance | Enterprise data governance tools valid for multi-cloud; for GCP-primary AI workloads, Dataplex provides the required lineage, cataloguing, and quality capabilities without an additional vendor |

## Implementation Notes

1. Model Armor: enable on all Vertex AI model deployments via the Model Armor API; configure `HARM_BLOCK_THRESHOLD` per content category (`HATE_SPEECH`, `DANGEROUS`, `HARASSMENT`); log all filtered requests with `logging.severity=WARNING`
2. Cloud DLP: create `InspectTemplate` with info types (`PERSON_NAME`, `EMAIL_ADDRESS`, `CREDIT_CARD_NUMBER`, `US_SOCIAL_SECURITY_NUMBER`); schedule daily scans on curated GCS bucket and BigQuery ML datasets
3. Dataplex: create lake with zone hierarchy (`raw` → `curated` → `production`); attach GCS and BigQuery assets; configure data quality rules as SQL assertions per dataset
4. VPC Service Controls: create service perimeter including `aiplatform.googleapis.com`, `bigquery.googleapis.com`, `storage.googleapis.com`; add all ML service accounts and CI/CD runners to the perimeter access level
5. Workload Identity Federation: `gcloud iam workload-identity-pools create`; configure OIDC provider for GitHub Actions; bind with `roles/iam.workloadIdentityUser` on the ML service account — never create service account keys for CI/CD

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
