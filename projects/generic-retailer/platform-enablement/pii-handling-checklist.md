# PII Handling Checklist — [RETAILER] AI Systems

**Owner:** AI Platform Team — Governance Lead
**Required:** For any AI system that processes customer, employee, or patient data
**Process:** BU AI team completes → [DATA_GOVERNANCE] classification confirmed → Platform Team signs off

---

## What Counts as PII in [RETAILER] AI Systems

| Data Type | Classification | Notes |
|---|---|---|
| [LOYALTY_PROGRAM] account ID + transaction history | PII — Sensitive | [LOYALTY_SCALE]; highest risk |
| Customer name, email, address | PII — Standard | |
| Phone number | PII — Standard | |
| Payment card data | PII — Financial | Never enters AI systems — hard block |
| Employee name, ID, schedule | PII — Internal | |
| Employee performance data | PII — Sensitive Internal | |
| Pharmacy / prescription data | PHI | HIPAA — isolated environment required |
| Aggregated / anonymised signals (e.g. [ML_PARTNER] segment scores) | Non-PII | Confirm aggregation level with [ML_PARTNER] |
| Store-level sales data (no customer linkage) | Non-PII | |

---

## Checklist

### Before Data Onboarding

- [ ] All data sources identified and listed in the model card
- [ ] Each data source classified in [DATA_GOVERNANCE] — link provided
- [ ] PII data type confirmed (Standard / Sensitive / PHI)
- [ ] Data owner identified and notified
- [ ] Legal basis for processing confirmed (consent, legitimate interest, contract)
- [ ] PHI data: HIPAA isolated environment provisioned (do not proceed without this)
- [ ] Payment card data: confirmed NOT included (hard block — escalate if found)

### Data in Transit

- [ ] All data in transit encrypted (TLS 1.2 minimum, TLS 1.3 preferred)
- [ ] No PII in query parameters, URLs, or log lines
- [ ] [ML_PARTNER] API calls: confirm response payloads do not include raw customer PII (aggregated signals only)
- [ ] Cross-cloud data movement (if applicable): classified and filtered before entering [VECTOR_STORE]

### Data at Rest

- [ ] Training data stored with [DATA_GOVERNANCE]-enforced access controls
- [ ] RAG corpus: [DATA_GOVERNANCE] classification applied to all indexed documents
- [ ] No PII stored in vector embeddings without explicit approval
- [ ] [VECTOR_STORE] index access restricted to service principal — no public access
- [ ] PHI data: stored in isolated environment (separate from main AI platform)

### In Model / Agent Processing

- [ ] PII not included in prompts unless strictly necessary for the task
- [ ] If PII in prompts: output reviewed for PII leakage before returning to user
- [ ] PII redaction enabled in [CONTENT_SAFETY] output filter (Tier 2+)
- [ ] No PII logged in trace data (trace sampling excludes PII fields)
- [ ] Prompt injection defence in place — user input sanitised before inclusion in prompts

### Retention & Deletion

- [ ] Data retention period defined and documented in model card
- [ ] Deletion process confirmed: customer can request deletion of loyalty data; AI system must honour within 30 days
- [ ] Training data: retention aligned to model lifecycle — deleted when model is deprecated
- [ ] Logs: PII-containing logs retained no longer than 90 days (default); longer requires Governance Lead approval

### Third-Party & Subsidiary Data

- [ ] [ML_PARTNER] data: confirm contractual terms permit use in [RETAILER] AI training / inference
- [ ] [ML_PARTNER] data: confirm data sharing agreement covers the AI use case
- [ ] Any other third-party data: legal review of licence terms before use

---

## Prohibited Uses (Hard Blocks)

These uses are not permitted under any circumstances without Legal and Governance Lead sign-off:

1. **Payment card data** in any AI system input, training set, or RAG corpus
2. **PHI** outside of the HIPAA-isolated Pharmacy AI environment
3. **Biometric data** (facial recognition, fingerprint) without explicit Legal approval
4. **Employee data** used to make or influence employment decisions without legal review
5. **Minor data** (customers under 13) — COPPA implications; escalate immediately

---

## Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| AI/ML Lead (BU) | | | [ ] |
| Data Owner | | | [ ] |
| AI Platform Governance Lead | | | [ ] |
| Legal (PHI or prohibited use review) | | | [ ] |
