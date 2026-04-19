# PII Handling Checklist — Store Associate AI Copilot — SAMPLE (P1-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `platform-enablement/pii-handling-checklist.md`

**Owner:** AI Platform Team — Governance Lead
**Required:** For any AI system that processes customer, employee, or patient data
**Process:** BU AI team completes → Microsoft Purview classification confirmed → Platform Team signs off

---

## What Counts as PII in MidWest Grocery AI Systems

| Data Type | Classification | Notes |
|---|---|---|
| MidWest Rewards account ID + transaction history | PII — Sensitive | 12M+ household profiles; highest risk |
| Customer name, email, address | PII — Standard | |
| Phone number | PII — Standard | |
| Payment card data | PII — Financial | Never enters AI systems — hard block |
| Employee name, ID, schedule | PII — Internal | |
| Employee performance data | PII — Sensitive Internal | |
| Pharmacy / prescription data | PHI | HIPAA — isolated environment required |
| DataInsight Co. aggregated signals (replenishment scores, substitution recommendations by store/item) | **Non-PII** | Confirmed aggregated — no individual customer linkage in API response |
| Store-level sales data (no customer linkage) | Non-PII | |

---

## Scope Assessment for This Use Case

**Does this system process PII?**
> **No.** The Store Associate AI Copilot does not access customer loyalty data (MidWest Rewards). It does not access employee PII beyond what is implicit in the associate's store assignment (which determines which store's data is in scope). DataInsight Co. API calls return replenishment and substitution signals at the store/item level — no customer-level data is returned.

**This checklist is completed as a confirmatory exercise** to document the negative finding and ensure it is reviewed before production.

---

## Checklist

### Before Data Onboarding

- [x] All data sources identified and listed in the model card
  - SOP corpus (SharePoint → Azure AI Search `mwg-store-ops-sop-v3`)
  - DataInsight Co. replenishment API (real-time, store/item aggregated)
  - DataInsight Co. substitution API (real-time, store/item aggregated)
- [x] Each data source classified in Microsoft Purview — links provided
  - SOP corpus: `purview.mwg.com/classifications/store-ops-sop-corpus` — classified Non-PII ✅
  - DataInsight Co. APIs: confirmed by DataInsight Co. data team that response payloads contain no customer PII — aggregated store/item signals only. Classification: `purview.mwg.com/classifications/datainsight-store-signals`
- [x] PII data type confirmed: **No PII in scope**
- [x] Data owners identified: Store Operations (SOP corpus); DataInsight Co. (API signals)
- [x] Legal basis for processing confirmed: operational necessity — store management data
- [ ] PHI data: not applicable — no pharmacy data in scope
- [x] Payment card data: confirmed NOT included — no financial data in scope

### Data in Transit

- [x] All data in transit encrypted (TLS 1.3 — Azure AI Search, DataInsight Co. API, Foundry Agent Service)
- [x] No PII in query parameters, URLs, or log lines — confirmed: queries are operational text (e.g. "replenishment status for item 4821"); no customer identifiers
- [x] DataInsight Co. API calls: confirmed response payloads do not include customer PII — store/item signals only. Contractual confirmation obtained from DataInsight Co. data governance team (2026-07-15)
- [ ] Cross-cloud data movement: not applicable — all within Azure

### Data at Rest

- [x] SOP corpus: stored in Azure Blob Storage with Purview-enforced access controls; AI Search index access restricted to `associate-copilot-prod` managed identity (Search Index Data Reader role only)
- [x] RAG corpus: Purview classification applied to all indexed documents — confirmed Non-PII
- [x] No PII stored in vector embeddings — SOP/planogram content only
- [x] Azure AI Search index: restricted to Foundry Agent Service managed identity — no public access
- [ ] PHI data: not applicable

### In Model / Agent Processing

- [x] Associate queries are operational text — no PII in prompts (e.g. "what is the return policy for item X?")
- [x] Output filter applied — scans responses for any inadvertent PII leakage (customer names, loyalty IDs); none detected in eval runs
- [x] PII redaction enabled in Azure AI Content Safety output filter
- [x] No PII logged in Foundry Observability trace data — trace configuration excludes user query content after 30 days
- [x] Prompt injection defence: user input sanitised; role separation enforced in system prompt

### Retention & Deletion

- [x] Trace data retention: 30 days (standard operational logging)
- [x] SOP corpus documents: retained per Store Operations document lifecycle policy (annual review); deleted when policy is superseded
- [x] No customer deletion requests applicable — no customer data in this system

### Third-Party & Subsidiary Data (DataInsight Co.)

- [x] DataInsight Co. contractual terms: confirmed that use of store/item aggregated signals in MidWest Grocery AI inference is permitted under the existing DataInsight Co. data sharing agreement (DSA-2024-001, Section 4.2 — operational signal use)
- [x] DataInsight Co. data: confirmed as aggregated (store/item level); no individual customer PII

---

## Prohibited Uses — Confirmed Not Present

1. **Payment card data** — not present ✅
2. **PHI** — not present ✅
3. **Biometric data** — not present ✅
4. **Employee data for employment decisions** — not present ✅
5. **Minor data** — not present ✅

---

## Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| AI/ML Lead (BU) | Store Ops AI/ML Lead | 2026-08-20 | [x] |
| Data Owner | Store Operations + DataInsight Co. data governance rep | 2026-08-22 | [x] |
| AI Platform Governance Lead | AI Governance Lead | 2026-08-25 | [x] — confirmed: no PII in scope; checklist complete as negative finding |
| Legal | — | — | N/A — no PII; no legal review triggered |
