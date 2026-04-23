# Skill: /pii-scan — PII Exposure Audit for AI Data Flows

## Trigger
User runs `/pii-scan` followed by a system description, data flow diagram, or architecture description.

## Behavior
0. **Before accepting input:** Ask the user to redact actual sensitive values from their description — replace real API keys, endpoint URLs, dataset names, and individual records with placeholders (e.g. `[API_KEY]`, `[ENDPOINT]`). The analysis requires *categories* and *flows*, not real values.
1. Extract all data elements mentioned or implied by the description
2. Map each element across the AI data lifecycle stages
3. Assign a risk level per intersection (data element × lifecycle stage)
4. Recommend mitigations for all MED and HIGH risk intersections
5. Surface governance gaps as [RISK] findings
6. Recommend ADRs for any PII handling decisions not yet documented

## AI Data Lifecycle Stages

| Stage | Description |
|-------|-------------|
| **Ingest** | Raw data entering the system (upload, API, scrape, ETL) |
| **Preprocess** | Cleaning, normalization, format conversion |
| **Embed** | Converting text/data to vector representations |
| **Store** | Persistence — databases, vector stores, object storage, logs |
| **Retrieve** | Pulling data for context (RAG, memory lookup) |
| **Prompt** | Data included in LLM context window |
| **Generate** | LLM output (may reflect or infer PII) |
| **Log / Trace** | Observability data — traces, request logs, audit trails |
| **Cache** | Short-term storage of inputs or outputs |
| **Export / Downstream** | Data leaving the system (API response, reports, downstream pipelines) |

## PII Categories

| Category | Examples |
|----------|---------|
| Direct identifiers | Name, email, phone, SSN, passport number |
| Quasi-identifiers | DOB, ZIP code, job title, employer (linkable in combination) |
| Sensitive attributes | Health, financial, legal, political, religious data |
| Behavioral / inferred | Usage patterns, preferences, LLM-inferred attributes |
| Credentials | Passwords, API keys, tokens (treat as PII equivalent) |

## Risk Level Guide
- **HIGH**: PII directly exposed with no controls, or controls are manual/undocumented
- **MED**: PII present but behind a control that could fail or is not systematically enforced
- **LOW**: PII present but adequately controlled and documented

## Output Format

### PII Scan Report: [System Name]
**Date:** [today]  
**System:** [description]  
**Overall Risk:** [GREEN / AMBER / RED]

---

#### 1. Data Inventory
List all data elements identified (explicit + inferred from the description). Flag any that are [ASSUMED].

---

#### 2. PII Exposure Matrix

| Data Element | PII Category | Ingest | Preprocess | Embed | Store | Retrieve | Prompt | Generate | Log | Cache | Export |
|-------------|-------------|--------|-----------|-------|-------|---------|--------|---------|-----|-------|--------|
| [element] | [category] | ✅/⚠️/❌/— | ... | | | | | | | | |

Legend: ✅ = controlled | ⚠️ = partial / MED risk | ❌ = exposed / HIGH risk | — = not present at this stage

---

#### 3. High-Priority Findings
For each HIGH and MED cell in the matrix:

| # | Data Element | Stage | Risk | Finding | Recommended Mitigation |
|---|-------------|-------|------|---------|----------------------|

---

#### 4. Governance Gaps
| Control | Status | Notes |
|---------|--------|-------|
| Data classification policy exists | ✅ / ❌ | |
| PII redaction before embedding | ✅ / ❌ | |
| Vector store access controls | ✅ / ❌ | |
| LLM prompt logging opt-out / masking | ✅ / ❌ | |
| Retention / deletion policy defined | ✅ / ❌ | |
| Data processing agreement (DPA) in place for 3rd-party LLMs | ✅ / ❌ | |
| Audit trail for PII access | ✅ / ❌ | |

---

#### 5. Recommended Mitigations (prioritized)
Numbered list, HIGH first. Each mitigation includes: what to do, where to implement, effort estimate (LOW/MED/HIGH).

#### 6. Recommended ADRs
PII handling decisions that should be captured as ADRs.

## Quality Bar
- The prompt stage is almost always an exposure point — if it's marked clean without explanation, push back
- Logging is the most commonly overlooked PII surface — always call it out
- If a third-party LLM API is in the data flow, the DPA gap must be flagged regardless of other controls
