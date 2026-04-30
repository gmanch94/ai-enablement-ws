---
name: model-card
description: Generate a model card covering overview, intended use, evals, limitations, governance, and versioning
---

# Skill: /model-card — Generate a Model Card

## Trigger
User runs `/model-card` followed by a model or feature description, or runs it alone.

## Behavior
1. Ask (if not provided): model name/version, use case, training/fine-tuning data summary, known limitations, and who owns this model in production
2. Generate a complete model card — do NOT leave sections blank; write "Not yet assessed" with a [TODO] tag if data is genuinely unavailable
3. Flag governance gaps as [RISK]
4. Recommend this card be stored in `/decisions/` or a dedicated `/model-cards/` directory

## Output Format

### Model Card: [Model Name vX.Y]
**Date:** [today]  
**Owner:** [team / person]  
**Status:** [Development / Staging / Production / Deprecated]

---

#### 1. Model Overview
| Field | Value |
|-------|-------|
| Model ID | |
| Base model (if fine-tuned) | |
| Model type | (e.g., LLM, classifier, embedder) |
| Framework | |
| Hosting | (cloud provider, region, endpoint type) |
| Version | |
| Last updated | |

#### 2. Intended Use
- **Primary use cases:** What this model is designed to do
- **Out-of-scope use cases:** What it should NOT be used for (be specific)
- **Target users:** Who will interact with this model directly or indirectly

#### 3. Training & Fine-Tuning Data
- Data sources and approximate size
- Date range of training data (knowledge cutoff if applicable)
- PII / sensitive data handling during training
- Data governance / consent status
- [RISK] flag if training data provenance is unclear

#### 4. Evaluation Results

| Benchmark / Eval | Score | Baseline | Date | Notes |
|-----------------|-------|----------|------|-------|

Include both task performance metrics and safety/fairness metrics. If evals haven't been run, flag [RISK: HIGH].

#### 5. Known Limitations & Failure Modes
Bullet list of known weaknesses, hallucination tendencies, demographic biases, or domain gaps. Be specific — vague limitations are not useful.

#### 6. Risks & Mitigations
| Risk | Severity | Mitigation in Place |
|------|----------|-------------------|

#### 7. Governance
| Item | Status |
|------|--------|
| PII handling policy documented | ✅ / ❌ |
| Data retention policy defined | ✅ / ❌ |
| Audit logging enabled | ✅ / ❌ |
| Human review process for high-stakes outputs | ✅ / ❌ |
| Incident response plan exists | ✅ / ❌ |
| Approved by AI governance board / review | ✅ / ❌ |

#### 8. Versioning & Change History
| Version | Date | Change Summary | Approved By |
|---------|------|---------------|-------------|

#### 9. Contact & Ownership
- Model owner (team + individual)
- On-call / incident contact
- Feedback channel for end users

## Quality Bar
- A model card without eval results is not production-ready — flag [RISK: HIGH] and recommend /eval-design
- "Not yet assessed" is acceptable; blank fields are not
- Governance section must be complete before the model card is used for a production deployment review
