# ADR-0006: Azure — RAG & Vector Retrieval

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

RAG pipelines on Azure require a retrieval layer that supports hybrid search (vector + keyword + semantic reranking), integrates with the Foundry agent and LLM stack, and can ground enterprise data from multiple sources (SharePoint, OneLake, ADLS Gen2, web). A decision is needed on the canonical vector store and enterprise knowledge grounding pattern.

## Decision

We will use **Azure AI Search** as the primary retrieval store for RAG — handling chunking, embedding, indexing, and hybrid retrieval. For enterprise knowledge grounding across corporate data sources without custom RAG plumbing, we will use **Foundry IQ** as the managed knowledge engine. **Azure Cosmos DB** (DiskANN vector) is reserved for operational workloads that require vector search alongside low-latency transactional access.

## Rationale

1. **Hybrid retrieval in one service** — Azure AI Search natively combines dense vector search, BM25 keyword search, and semantic reranking (via Azure OpenAI). No separate reranking service or query fusion layer is needed.
2. **Foundry IQ eliminates bespoke connectors** — Foundry IQ handles SharePoint, OneLake, ADLS Gen2, and web crawl ingestion with Purview governance applied automatically. Teams should not build custom ingestion pipelines for these sources.
3. **Operational vs analytical RAG** — Cosmos DB vector (DiskANN) is the right choice when vector search must coexist with OLTP access patterns (e.g., product catalog with embeddings, user profile grounding). It is not cost-effective as a pure RAG store.
4. **SDK maturity** — `azure-search-documents` (GA) has a stable chunking and push-indexing API that integrates directly with `azure-ai-inference` embeddings.

## Consequences

### Positive
- Single retrieval service handles the full hybrid search requirement without multi-service query fusion
- Foundry IQ removes weeks of connector development for SharePoint and OneLake sources
- AI Search integrates with Azure ML pipelines for automated re-indexing on data updates

### Negative / Trade-offs
- Azure AI Search is not the lowest-cost vector store at scale — S3 tier required for large indexes
- Foundry IQ is tightly coupled to the Foundry ecosystem; switching retrieval backends later requires re-ingestion
- No native graph retrieval — for knowledge graph RAG patterns, a custom solution on Cosmos DB is required

### Risks
- [RISK: MED] Foundry IQ knowledge freshness depends on connector sync frequency — set up incremental sync schedules and monitor staleness
- [RISK: LOW] AI Search index schema changes require full re-indexing — design schema with headroom for field additions; avoid breaking schema changes post-production

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Azure Cosmos DB DiskANN as primary RAG store | Optimised for OLTP + vector combined; more expensive than AI Search for pure retrieval at scale; lacks semantic reranking |
| Azure DocumentDB vector | GA (Ignite 2025) but less mature than AI Search for hybrid retrieval; consider for open-source-compatible deployments |
| Third-party vector DB (Pinecone, Weaviate, Qdrant) | Adds external vendor dependency, separate billing, egress costs, and security boundary; no Entra integration |
| Self-managed pgvector on Azure PostgreSQL | Valid for small-scale or SQL-native teams; lacks semantic reranking and scale of AI Search |

## Implementation Notes

1. Use `azure-search-documents` SDK with integrated vectorisation (connect to Azure OpenAI text-embedding-3-large)
2. Enable semantic ranker on the index — negligible cost for meaningful recall improvement
3. For Foundry IQ: connect SharePoint and OneLake sources in the Foundry workspace; configure Purview sensitivity label enforcement before ingestion
4. Set re-indexing triggers via Azure ML Pipelines on ADLS Gen2 data arrival events
5. Use Cosmos DB DiskANN only when the same document must serve OLTP reads and vector retrieval in the same transaction boundary

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
