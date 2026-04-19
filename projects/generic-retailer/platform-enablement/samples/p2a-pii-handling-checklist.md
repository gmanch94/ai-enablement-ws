# PII Handling Checklist — Conversational Shopping Assistant — SAMPLE (P2-A)

> **SAMPLE ARTIFACT** — fictional MidWest Grocery context. See `samples/README.md`.
> Blank template: `platform-enablement/pii-handling-checklist.md`

**Owner:** AI Platform Team — Governance Lead
**Required:** For any AI system that processes customer, employee, or patient data
**Process:** BU AI team completes → Microsoft Purview classification confirmed → Platform Team signs off

---

## What Counts as PII in MidWest Grocery AI Systems

| Data Type | Classification | Notes |
|---|---|---|
| MidWest Rewards account ID + transaction history | PII — Sensitive | 12M+ household profiles; highest risk — **in scope for this use case** |
| Customer name, email, address | PII — Standard | In scope — used for session identity |
| Phone number | PII — Standard | Not in scope for this use case |
| Payment card data | PII — Financial | Never enters AI systems — hard block |
| Employee data | PII — Internal | Not in scope |
| Pharmacy / prescription data | PHI | Not in scope |
| DataInsight Co. Personalisation API response (ranked product list) | **Non-PII** | API returns a ranked product list only — no raw customer record; confirmed with DataInsight Co. |
| Session transcript (customer shopping intent, dietary preferences) | PII — Standard | Customer-provided in session; retained for 30 days; PII-stripped after 7 days |

---

## Scope Assessment for This Use Case

**Does this system process PII?**
> **Yes — PII-Sensitive.** The Conversational Shopping Assistant processes MidWest Rewards customer loyalty profiles for personalisation. The customer's loyalty account ID is used to call the DataInsight Co. Personalisation API at session start. The API returns a ranked product list (non-PII) — the loyalty ID is not stored in agent context after the initial call. Session transcripts (customer-typed shopping intent, dietary preferences) are retained for 30 days and stripped of PII after 7 days.

---

## Checklist

### Before Data Onboarding

- [x] All data sources identified and listed in the model card:
  - MidWest Rewards loyalty profile (customer ID → DataInsight Co. Personalisation API call at session start)
  - Product inventory index (Azure AI Search `mwg-product-inventory-realtime` — Non-PII)
  - Personalised pricing API (returns customer-specific prices — contains loyalty ID in request)
  - Session transcript (customer-typed text in session)
- [x] Each data source classified in Microsoft Purview:
  - MidWest Rewards data: `purview.mwg.com/classifications/midwestrewards-loyalty-data` — PII-Sensitive ✅
  - Product inventory: `purview.mwg.com/classifications/product-catalogue-inventory` — Non-PII ✅
  - DataInsight Co. API response: confirmed Non-PII (ranked product list, no customer record) ✅
  - Session transcript: PII-Standard (customer-typed text may include dietary conditions, family info)
- [x] PII data type confirmed: PII-Sensitive (MidWest Rewards)
- [x] Data owners identified: Digital / Loyalty (MidWest Rewards); Digital / Supply Chain (inventory + pricing); DataInsight Co. (Personalisation API)
- [x] Legal basis for processing confirmed: CCPA consent (personalisation opt-in); legitimate interest for product availability; customer consent obtained via MidWest Grocery app privacy disclosure (updated March 2027)
- [ ] PHI data: not applicable — pharmacy excluded from this use case
- [x] Payment card data: confirmed NOT included — pricing API returns prices only, no payment data

### Data in Transit

- [x] All data in transit encrypted (TLS 1.3): loyalty ID to DataInsight Co. API; personalised pricing API calls; Azure AI Search queries
- [x] No loyalty ID in query parameters or log lines — loyalty ID passed as an Authorization header in DataInsight Co. API call, not in URL query params; excluded from trace logs
- [x] DataInsight Co. Personalisation API: confirmed response is ranked product list only — no customer PII returned. Contractual confirmation: DSA-2024-001, Section 4.3 (personalisation use)
- [x] Session transcripts: transmitted over HTTPS; not logged in raw form beyond 7 days

### Data at Rest

- [x] MidWest Rewards profile: not stored in agent context — loyalty ID used only at session start for Personalisation API call; API response (ranked list) cached in session memory only
- [x] Product inventory index: Azure AI Search `mwg-product-inventory-realtime` — Non-PII; access restricted to `shopping-assistant-prod` managed identity
- [x] No customer PII in vector embeddings — product catalogue only
- [x] Session transcripts: stored for 30 days in Azure Blob Storage (customer-aiml-sessions container); PII fields (dietary conditions, family composition inferred from queries) stripped after 7 days via automated PII redaction job
- [x] No loyalty ID stored in Foundry Observability trace data — trace sampling configured to exclude session context fields

### In Model / Agent Processing

- [x] Customer loyalty ID used only for DataInsight Co. Personalisation API call — not included in LLM prompts; API returns ranked product list that is included in prompt context
- [x] Dietary constraint information: typed by customer in session; included in LLM prompt as session context; not persisted beyond session
- [x] PII output filter enabled: output scanned for loyalty IDs, customer names, account numbers before returning to customer
- [x] No customer loyalty ID surfaced in agent output
- [x] PII redaction enabled in Azure AI Content Safety output filter
- [x] No PII logged in Foundry Observability traces — trace configuration reviewed and confirmed by Platform Team
- [x] Prompt injection defence: customer input sanitised; loyalty ID never accessible via prompt injection

### Retention & Deletion

- [x] Session transcript retention: 30 days raw; PII-stripped after 7 days (automated job runs nightly)
- [x] Deletion on customer request: customer can request deletion of loyalty data via MidWest Grocery privacy portal; AI system must remove session transcripts within 30 days of request — deletion workflow confirmed with Digital team
- [x] DataInsight Co. Personalisation API: no customer data retained by DataInsight Co. beyond the API call — confirmed in DataInsight Co. data processing addendum (DPA-2027-003)

### Third-Party & Subsidiary Data (DataInsight Co.)

- [x] DataInsight Co. contractual terms: use of MidWest Rewards loyalty IDs to call DataInsight Co. Personalisation API for shopping recommendations is permitted under DSA-2024-001, Section 4.3
- [x] DataInsight Co. API response: Non-PII (ranked product list) — no raw customer data stored by DataInsight Co. per DPA-2027-003
- [x] Customer opt-out of personalisation: honoured immediately — when customer selects "shop without personalisation", loyalty ID is not sent to DataInsight Co. API; session uses anonymous mode (no loyalty signals)

---

## Prohibited Uses — Confirmed Not Present

1. **Payment card data** — not present ✅
2. **PHI** — not present ✅
3. **Biometric data** — not present ✅
4. **Employee data for employment decisions** — not present ✅
5. **Minor data (under 13)** — MidWest Rewards requires age 18+; COPPA not triggered ✅

---

## Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| AI/ML Lead (BU) | Digital AI/ML Lead | 2027-04-10 | [x] |
| Data Owner | Digital / Loyalty team + DataInsight Co. data governance rep | 2027-04-15 | [x] |
| AI Platform Governance Lead | AI Governance Lead | 2027-04-20 | [x] |
| Legal / Chief Privacy Officer | MidWest Grocery Legal | 2027-05-01 | [x] — CCPA consent mechanism confirmed; session transcript retention policy approved; opt-out mechanism confirmed compliant |
