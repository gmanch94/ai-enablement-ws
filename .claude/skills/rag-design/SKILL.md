---
name: rag-design
description: Design a RAG architecture — chunking, embedding, retrieval pattern, re-ranking, and observability
---

# Skill: /rag-design — Design a RAG Architecture

## Trigger
User runs `/rag-design` followed by a description of their data and use case, or runs it alone.

## Behavior
1. Ask (if not provided): corpus type, approximate size, update frequency, query patterns, latency budget, and whether accuracy or speed is the priority trade-off
2. Work through each design decision sequentially — chunking → embedding → indexing → retrieval → re-ranking → generation
3. Flag risks at each layer
4. Recommend tooling from the established stack (LlamaIndex, LangChain, LangGraph)
5. Surface decisions that should become ADRs

## Design Decision Tree

### Chunking Strategy
| Corpus Type | Recommended Strategy |
|-------------|---------------------|
| Long-form docs (PDFs, reports) | Recursive character splitting, 512–1024 tokens, 10–20% overlap |
| Structured data (tables, CSVs) | Row-level or semantic table chunking; do NOT split mid-row |
| Code | Function/class-level splitting; preserve imports in context |
| Conversations / transcripts | Turn-level or fixed-window with speaker labels preserved |
| Mixed | Hybrid — apply type detection before chunking |

### Embedding Model Selection
| Constraint | Recommendation |
|------------|---------------|
| On-prem / data residency | `sentence-transformers` (all-mpnet-base-v2 or BGE-M3) |
| Cloud / quality priority | OpenAI `text-embedding-3-large` or Google `text-embedding-004` |
| Multilingual | BGE-M3 or `multilingual-e5-large` |
| Low latency | `text-embedding-3-small` or `bge-small-en` |

### Retrieval Pattern
- **Dense only**: good for semantic similarity, struggles with keyword/entity matching
- **Sparse only (BM25)**: good for keyword/entity, struggles with paraphrase
- **Hybrid (dense + sparse)**: recommended default — combine with RRF (Reciprocal Rank Fusion)
- **Multi-query**: generate N query variants before retrieval — reduces single-query brittleness

### Re-ranking
- Always add a cross-encoder re-ranker when top-k > 5 or precision is critical
- Recommended: `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast) or Cohere Rerank (cloud)
- Re-rank top-20, pass top-5 to generation

## Output Format

### RAG Architecture Design: [Use Case]
**Corpus:** [description]  
**Query Pattern:** [description]  
**Latency Budget:** [Xms end-to-end]  
**Priority:** [Accuracy / Speed / Cost]

---

#### 1. Chunking
Recommended strategy + rationale. Flag if corpus needs pre-processing before chunking.

#### 2. Embedding
Model recommendation + hosting mode (local vs. API). Note token limits and batch costs.

#### 3. Vector Store
Recommendation from: pgvector, Pinecone, Weaviate, Qdrant, ChromaDB, Vertex AI Vector Search.
Include: index type (HNSW vs IVF), namespace/tenant strategy, update/upsert pattern.

#### 4. Retrieval Pattern
Dense / sparse / hybrid recommendation with top-k and score threshold.

#### 5. Re-ranking
Whether to include, which model, and the top-k to pass downstream.

#### 6. Generation Prompt Design
Key guidance: cite sources, handle "not found" gracefully, set context window budget.

#### 7. Observability
Metrics to track: retrieval recall@k, faithfulness, latency per stage, chunk hit rate.

#### 8. Risks & Trade-offs
| Risk | Severity | Mitigation |
|------|----------|-----------|

#### 9. Recommended ADRs
Decisions that should be captured (embedding model, vector store, retrieval pattern).

## Quality Bar
- Retrieval pattern must account for the query type — never default to dense-only without justification
- Always include a "not found" fallback — what does the system do when retrieval returns nothing useful?
- Latency budget must be allocated across stages: embedding + retrieval + rerank + generation
