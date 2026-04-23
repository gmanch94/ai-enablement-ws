# Skill: /supply-chain-review — AI Supply Chain Security Review

## Trigger
User runs `/supply-chain-review` followed by a system description, or provides a model card, dependency manifest, or architecture doc.

## Behavior
1. Ask (if not provided): model source(s), embedding model, third-party APIs used, framework/library versions, whether an AI-BOM or model card exists
2. Review each supply chain layer in sequence (model → data → framework → runtime → third-party APIs)
3. Assign a trust level to each component (TRUSTED / CONDITIONAL / UNTRUSTED)
4. Surface all [RISK] findings with severity
5. Produce an action list ordered by severity
6. Flag any components that block a production deployment until resolved

## Framework References
- **OWASP LLM03 2025** — Supply Chain Vulnerabilities
- **MITRE ATLAS AML.T0010** — AI Supply Chain Compromise
- **OpenSSF Model Signing (OMS) Specification** — model integrity standard
- **SPDX 3.0 AI/ML extensions** — AI Bill of Materials standard
- **NIST AI 600-1** — model supply chain risk mapping

## Supply Chain Layers

### Layer 1 — Foundation Model / Base Model

| Check | How to Verify | Risk if Missing |
|-------|--------------|-----------------|
| Source is a known-trusted registry | HuggingFace (verified org), commercial API (OpenAI, Anthropic, Cohere), or internal registry | HIGH — unknown source may be trojanized |
| Model card exists | Read the model card: data sources, intended use, known limitations, eval results | MED — no insight into training data scope or bias |
| Version is pinned | Code references an exact model version/tag, not `latest` | MED — silent model drift; behavioral regression without notice |
| Cryptographic integrity verified | SHA256 hash or OMS signature checked at deploy time | HIGH — tampered weights deploy silently |
| License is approved | License reviewed against organization's approved list | MED — GPL-contaminated weights may create IP risk |

### Layer 2 — Training / Fine-Tune Data

| Check | How to Verify | Risk if Missing |
|-------|--------------|-----------------|
| Data sources documented | Explicit list of datasets used (public + proprietary) | HIGH — poisoned training data undetectable at inference time |
| PII scrub confirmed | Evidence of PII scan + redaction before fine-tuning | HIGH — model may memorize and regurgitate PII |
| Data lineage tracked | Can trace each training artifact to its origin | MED — no forensics path if poisoning suspected |
| Consent / licensing verified for public datasets | License reviewed for commercial use and model training permission | MED — IP and regulatory exposure |

### Layer 3 — Embedding Model

| Check | How to Verify | Risk if Missing |
|-------|--------------|-----------------|
| Embedding model is version-pinned | Exact model name + version in code/config, not resolved dynamically | HIGH — embedding space drift breaks retrieval silently |
| Source verified (same as L1) | Same provenance checks as foundation model | HIGH |
| Hash verified at load time | Embedding model weights checked against known good hash | MED — tampered embeddings corrupt entire vector store |
| Embedding model change triggers re-index | Process exists to re-embed corpus when model changes | MED — stale embeddings with new model = semantic drift |

### Layer 4 — Frameworks & Libraries

| Check | How to Verify | Risk if Missing |
|-------|--------------|-----------------|
| All AI/ML dependencies pinned to exact versions | `requirements.txt` / `pyproject.toml` / `package-lock.json` with exact versions | HIGH — transitive dependency attack surface |
| SBOM generated | SBOM (CycloneDX or SPDX 3.0) exists for the deployment artifact | MED — no inventory = no vulnerability scanning |
| CVE scan runs in CI | Dependency scan in pipeline (e.g., `pip-audit`, `trivy`, `snyk`) | HIGH — known CVEs in ML libs go unpatched |
| Unpinned `latest` tags blocked | CI fails if `latest` or unversioned deps detected | MED — silent upgrades introduce breaking changes |

### Layer 5 — Plugins, Tools & Third-Party APIs

| Check | Trust Level | Criteria |
|-------|-------------|---------|
| Internal / first-party tool | TRUSTED | Owned, audited, signed, versioned |
| Major platform API (OpenAI, Azure, AWS, GCP) | CONDITIONAL | DPA signed, SOC2, data residency confirmed |
| Open-source community plugin | CONDITIONAL | Actively maintained, pinned version, CVE-scanned |
| Unknown / community-contributed plugin | UNTRUSTED | Block until provenance verified |
| Third-party data enrichment API | CONDITIONAL | Data egress reviewed, PII classification applied |

Flag any UNTRUSTED component as [RISK: HIGH] — it blocks production until resolved.

### Layer 6 — AI Bill of Materials (AI-BOM)

An AI-BOM extends a traditional SBOM to cover model-specific artifacts. Check for:

| Field | Required? | Notes |
|-------|-----------|-------|
| Base model name + version + source URL | Yes | |
| Base model hash / OMS signature | Yes | |
| Embedding model name + version + hash | Yes | |
| Training datasets (name, version, license) | Yes | |
| Fine-tuning data sources | Yes if fine-tuned | |
| Framework versions (LangChain, LlamaIndex, etc.) | Yes | |
| Third-party APIs and their DPA status | Yes | |
| Model card reference | Yes | |
| Last updated date | Yes | |

If no AI-BOM exists: flag [RISK: HIGH] — recommend generating one using SPDX 3.0 AI/ML fields.

## Trust Level Definitions

| Level | Meaning | Deployment Gate |
|-------|---------|----------------|
| TRUSTED | Provenance verified, signed, pinned, licensed, scanned | No gate — proceed |
| CONDITIONAL | Partially verified; known risk with mitigations in place | Document mitigation; approved before prod |
| UNTRUSTED | Provenance unknown or unverifiable | **Blocks production until resolved** |

## Output Format

### Supply Chain Review: [System Name]
**Date:** [today]  
**Scope:** [models, data, frameworks, APIs reviewed]  
**Overall Posture:** [GREEN / AMBER / RED]

---

#### Layer Summary

| Layer | Components Reviewed | Trust Level | Open Risks |
|-------|---------------------|-------------|-----------|
| Foundation model | | | |
| Training / fine-tune data | | | |
| Embedding model | | | |
| Frameworks & libraries | | | |
| Plugins & third-party APIs | | | |
| AI-BOM | | | |

---

#### Risk Register

| # | Layer | Component | Risk | Severity | Blocks Prod? | Recommended Action |
|---|-------|-----------|------|----------|-------------|-------------------|

---

#### Production Gate Checklist
Before deploying to production, the following must be confirmed:

- [ ] All models pinned to exact version with hash verified
- [ ] AI-BOM generated and committed to repo
- [ ] No UNTRUSTED components in the dependency graph
- [ ] CVE scan passing in CI with zero HIGH/CRITICAL findings
- [ ] DPA in place for all third-party LLM APIs handling user data
- [ ] Embedding model version-pinned; re-index process documented
- [ ] Model card reviewed and attached to deployment artifact

---

#### Action List (ordered by severity)
1. [HIGH] …
2. [MED] …
3. [LOW] …

## Quality Bar
- A component with no provenance is UNTRUSTED by default — do not assume safety
- Version pinning without hash verification is incomplete — both are required
- A DPA gap for any third-party API that processes user data is always [RISK: HIGH], regardless of the API's reputation
- If the AI-BOM doesn't exist, flag it immediately — it cannot be produced after the fact for data already ingested
- The embedding model is part of the supply chain — it is the most commonly overlooked component
