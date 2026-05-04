# LLM Data Strategy — Data Readiness for LLM-Based Systems

**Status:** Reference
**Last updated:** 2026-05-04
**Audience:** AI architects, ML platform leads, transformation leads scoping LLM-based pilots

> **Scope:** This reference covers the data questions that must be answered before building an LLM-based system — context window vs. RAG architecture, eval corpus design, distillation economics, and data source governance. It is vendor-neutral and model-family agnostic.
>
> **Not in scope here:**
> - Custom ML model preprocessing (temporal splits, cold-start, data contracts for training pipelines) → see [ADR-0045](../decisions/ADR-0045-retail-ml-data-preprocessing-policy.md)
> - Cloud-specific retrieval service selection → see [ADR-0006 (Azure)](../decisions/ADR-0006-azure-rag-vector-retrieval.md) · [ADR-0015 (AWS)](../decisions/ADR-0015-aws-rag-vector-retrieval.md) · [ADR-0024 (GCP)](../decisions/ADR-0024-gcp-rag-vector-retrieval.md)
> - Vendor-specific context window sizes, pricing thresholds, or caching mechanics → see the model provider's documentation

---

## How to read this

Each section answers a pre-build sizing or architecture question:

- **Threshold** — the number or condition that drives the decision
- **Decision trigger** — what changes depending on which side of the threshold you land on
- **Rule of thumb label** — where the threshold is field practice rather than primary documentation; verify against your workload before committing architecture or budget

---

## 1. Context window vs. RAG: the first architecture decision

Before deciding to build a RAG pipeline, assess whether your reference material fits in the model's context window in a single call. If it does, RAG adds complexity with no benefit.

| Condition | What to do |
|---|---|
| Reference material fits in the model's context window AND is stable across requests | Long-context single call — skip RAG |
| Material exceeds the context window, OR changes frequently, OR requires per-request retrieval | RAG pipeline warranted |
| Multiple tenants each have a distinct corpus | RAG with tenant-scoped indexes — context contamination risk in shared long-context calls |
| Caller must verify which source span grounded the answer | RAG with span-level citation — long-context calls cannot provide span attribution without additional tooling |

**Check your model's context window.** Ranges vary significantly across model families (8K–1M+ tokens as of 2026). Do not assume a fixed number. Token-to-word conversion is approximately 0.75 tokens per English word (rule of thumb — density-dependent).

**Decision trigger.** If your working reference material fits in the context window *and* is stable across calls, do not build RAG. Retrieval adds latency, a chunking failure mode, a retrieval-miss failure mode, and an indexing maintenance burden. Build it only when the material exceeds the window, changes faster than requests are stable, or requires span citation.

---

## 2. RAG corpus sizing

When RAG is warranted, corpus size and update cadence determine the architecture tier.

### Corpus size tiers (rule of thumb — not primary-cited)

| Corpus size | Architecture |
|---|---|
| Fits in model context window | Long-context single call — skip RAG |
| 1–10× context window size | Chunked semantic retrieval (standard RAG): embed chunks, store in vector index, retrieve top-K at query time |
| > 10× context window, or multi-million-token corpus | Full retrieval pipeline: tiered indexing, BM25 + vector hybrid, semantic reranker, scheduled refresh |
| High update cadence (material changes faster than query patterns stabilize) | Add incremental indexing + freshness indicator regardless of corpus size |

**What breaks at each tier without the right architecture:**
- Skipping RAG at the 1–10× tier: truncation or multi-call patchwork introduces span stitching errors
- Standard RAG at the > 10× tier: retrieval latency and recall degrade; missing chunks produce confident-but-wrong answers
- No freshness signal on high-cadence corpora: stale answers from outdated index, with no indication to the caller that the source is stale

**Verify against your actual workload.** These tiers are sizing signals, not precise thresholds. Measure retrieval latency and recall on a representative sample of queries before committing to a tier.

### Chunking strategy shapes corpus quality

The retrieval unit is a chunk, not a document. Chunking decisions affect both recall and answer quality:

| Variable | Recommended default | When to deviate |
|---|---|---|
| Chunk size | 256–512 tokens | Larger (up to 1,024) for documents with long reasoning chains; smaller for FAQ-style content |
| Overlap | 10–15% of chunk size | Increase overlap when answers span chunk boundaries frequently |
| Chunk boundary | Sentence or paragraph boundary — never mid-sentence | Structure-aware chunking (headings, list items) for reference docs and runbooks |
| Chunk metadata | Source document ID, section title, last-updated timestamp | Always include; used for filtering and citation |

A corpus of chunks with no metadata cannot support citation, freshness filtering, or per-source access control.

---

## 3. Eval corpus for LLM-based systems

LLM evaluation requires a different corpus design than classic ML. Outputs are variable-length natural language; ground truth is often a rubric, not a label.

### Minimum corpus sizes (rule of thumb — informed by field practice)

| Eval type | Minimum to start | Grow to | Blocking / advisory |
|---|---|---|---|
| Regression (prompt change detection) | 30–50 | 200–500 | Blocking on > 5% quality drop |
| Format compliance (schema, length, structure) | 50–100 | — | Blocking — any failure |
| Tool-call accuracy (function name, parameter extraction) | 50–150 | — | Blocking — per-tool threshold |
| Grounding / hallucination | 50–200 | — | Blocking — per-task threshold |
| Adversarial / jailbreak | 30–100 | Refresh quarterly | Advisory |
| Cost-per-task | 100+ (sampled from production) | — | Alert on > 20% regression |
| Latency (p50 / p95) | 30–50 | — | Alert on > 20% regression |
| Refusal calibration | 50–100 | — | Advisory |

**Minimum viable eval for a first pilot:** 30-row regression + 50-row format compliance. No LLM-based system should go to Week 1 without these locked. Without a regression eval, you cannot distinguish prompt improvement from regression when you make changes.

### Ground truth sourcing

| Source | Good for | Risk |
|---|---|---|
| Human-authored expected outputs | Regression, format, grounding | Expensive; annotator disagreement on open-ended outputs |
| LLM-generated synthetic cases | Format compliance, tool-call accuracy, schema edge cases | Biased toward what the model can imagine — add human-authored adversarial cases |
| Production traffic (sampled, anonymized) | Cost-per-task, latency, regression seeds | Most representative; requires PII scrub pipeline before use |
| Expert-reviewed rubric scores | Open-ended quality judgment | Requires domain SME time; rubric drift over versions |

**Golden eval set.** Designate a held-out set that is never used for prompt tuning. Use it exclusively for: (a) pre-release final gate, (b) regression testing after model version changes, (c) monitoring for quality drift. This is the same golden dataset concept as ADR-0045 §7 — applied to LLM-based systems rather than custom ML models.

**Do not use LLM-as-judge as your only eval.** LLM judges are biased toward verbosity, self-consistency, and their own output style. Use them for initial triage, not as a blocking gate without human calibration.

---

## 4. Distillation economics: when to train a classifier instead

LLM per-request cost is justified when the task requires reasoning, generalization, or natural language generation. It is not justified for high-volume rule-extractable classification at the economics of a trained classifier.

### Distillation trigger signals (rule of thumb — not primary-cited)

| Signal | Threshold | Action |
|---|---|---|
| Request volume | > 10M requests/month on a rule-extractable classification task | Distill: use LLM to label, then train a small classifier |
| Unit cost target | < $0.001 / request | Classical ML or rules — LLM cost at any model tier exceeds this |
| Task complexity | Clearly rule-extractable (spam, intent routing, basic content tier) | Distill; route the ambiguous tail to LLM |

**Distillation data requirements (rule of thumb):**
- 1K–10K labeled examples for a small transformer-class classifier (DistilBERT, small BERT variant)
- Generate labels offline in batch: send unlabeled samples to the LLM, collect output, human-review 5–10% before training
- Do not distill prematurely: below the volume threshold, per-request LLM cost is lower than distillation overhead (labeling cost + training infra + model serving + maintenance)
- Retain the LLM for the tail of ambiguous cases where classifier confidence falls below threshold

**What distillation does not replace:** Tasks requiring reasoning across multiple evidence sources, tasks with rare or novel edge cases the classifier hasn't seen, tasks requiring natural language generation (not just classification output). Do not distill these — the classifier will fail on exactly the cases where the LLM adds the most value.

---

## 5. Data source taxonomy and governance flags

Where does the data for an LLM-based system come from? Each source has a different architecture fit, governance requirement, and freshness profile.

| Source type | Best fit for | Governance flag | Key risk |
|---|---|---|---|
| **First-party operational data** — support tickets, call transcripts, historical decisions, internal logs | RAG corpus, eval seed cases, distillation labels | PII / PHI likely. Scrub at gateway before any LLM API call. Confirm data classification and DLP policy handling. | Staleness: ops data from 12+ months ago may reflect superseded policies or edge cases no longer representative |
| **Internal knowledge base** — wikis, SOPs, policy docs, code repos, runbooks | RAG corpus, grounding source, system prompt context | Lower PII risk than ops data, but may contain trade secrets. Verify data classification before loading. | Unstructured format requires a chunking strategy. Stale pages silently degrade answer quality — wire a refresh cadence. |
| **Production traffic (anonymized)** — sampled real requests and responses | Cost eval corpus (100+ tasks), latency eval seeds, regression ground truth | PII scrub required before use. Do not send raw logs to external APIs. Log pipeline and sampling strategy required. | Most representative source; also the hardest to access without a proper log and sampling pipeline |
| **Synthetic labels from LLM** — LLM labels a sample; labels train a downstream classifier or seed an eval | Distillation training data, eval annotations | No PII enters the labeling call if input is redacted first. Run in batch (lower cost). | LLM-generated labels are biased toward the model's own output style. Human-review 5–10% sample before training. |
| **User feedback signals** — thumbs up/down, explicit corrections, escalations | Eval grounding, quality regression signal | Low PII risk if feedback is sparse and separated from content. | Signal rate is low (1–5% of sessions generate explicit feedback). Supplement with implicit signals: edits to LLM output, task abandonment rate, re-submission rate. |
| **Public / licensed datasets** — jailbreak corpora, prompt injection benchmarks, open domain QA | Adversarial eval (30–100 examples, refresh quarterly) | Verify license before use. Common adversarial corpora are MIT or CC-licensed. | Adversarial techniques drift. A corpus from 12+ months ago misses current technique classes. Refresh quarterly minimum. |
| **Synthetic test cases from LLM** — LLM writes adversarial prompts, edge cases, format variants | Format compliance eval, tool-call accuracy, schema edge cases | No PII risk if input prompts are clean. | Synthetic tests are biased toward what the LLM can imagine — not what users will actually do. Add human-authored adversarial cases. |

### Governance check before loading any source

Answer three questions before any source enters the pipeline:

1. **PII / PHI?** → Scrub at the gateway before any external API call. Pseudonymize, do not pass raw identifiers.
2. **Data classification / DLP policy?** → Confirm handling path with security and privacy team. Internal classification tiers determine whether the source can leave the network.
3. **Inference geography constraint?** → If regulatory or contractual requirements restrict where inference happens, confirm the LLM provider supports the required region and configure accordingly before testing with any real data.

---

## 6. Pre-pilot data readiness checklist

Before Week 1 of any LLM-based pilot:

- [ ] **Architecture decision made:** context window vs. RAG evaluated (§1). If RAG: corpus size tier identified (§2).
- [ ] **Data source(s) identified:** which rows in §5 does this use case draw from?
- [ ] **PII / PHI scrub path defined** for any source containing regulated data (§5 governance flag).
- [ ] **Data classification confirmed** with security / privacy for all sources.
- [ ] **Inference geography confirmed** for any source with residency constraints.
- [ ] **Eval corpus scoped:** at minimum 30-row regression + 50-row format compliance (§3).
- [ ] **If volume > 10M req/mo on a rule-extractable task:** distillation plan in place (§4).
- [ ] **If RAG:** chunking strategy defined; metadata fields identified (source ID, section, timestamp).
- [ ] **If RAG:** corpus freshness cadence confirmed — how often does the index need to be refreshed?

---

## How this reference connects to the rest

| Question | Go here |
|---|---|
| Which cloud service should handle retrieval? | [ADR-0006 (Azure)](../decisions/ADR-0006-azure-rag-vector-retrieval.md) · [ADR-0015 (AWS)](../decisions/ADR-0015-aws-rag-vector-retrieval.md) · [ADR-0024 (GCP)](../decisions/ADR-0024-gcp-rag-vector-retrieval.md) |
| Data preprocessing policy for custom ML training (temporal splits, PII, data contracts) | [ADR-0045](../decisions/ADR-0045-retail-ml-data-preprocessing-policy.md) |
| Dataset readiness audit for a specific retail ML use case | `/dataset-readiness` command |
| Dataset × use case dependency matrix for retail ML | [`use-case-dataset-matrix.md`](../projects/generic-retailer/data-preprocessing/use-case-dataset-matrix.md) |
| Claude-specific numbers (200K context, cache floor %, distillation req/mo threshold) | [`claude-platform-playbook / data-advisory.md`](https://github.com/gmanch94/claude-platform-playbook/blob/main/artifacts/data-advisory.md) |
| Cloud data ingestion service selection (Azure / AWS / GCP) | [ADR-0008](../decisions/ADR-0008-azure-data-ingestion-feature-management.md) · [ADR-0017](../decisions/ADR-0017-aws-data-ingestion-feature-management.md) · [ADR-0026](../decisions/ADR-0026-gcp-data-ingestion-feature-management.md) |

---

`© gmanch94 · CC-BY-4.0 · As of 2026-05.`
