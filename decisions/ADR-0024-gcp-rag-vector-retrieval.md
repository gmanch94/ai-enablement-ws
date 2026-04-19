# ADR-0024: GCP — RAG & Vector Retrieval

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

RAG pipelines on GCP require a managed retrieval layer that addresses the demo-to-production gap — reliable chunking, embedding, indexing, and retrieval at production scale, not just PoC quality. A decision is needed on the canonical GCP RAG and vector storage pattern, distinguishing between knowledge-base RAG and operational RAG (where vector search coexists with transactional database queries).

## Decision

We will use **Vertex AI RAG Engine** (GA, Feb 2025) as the primary managed RAG service — handling chunking, embedding, retrieval, and grounding for knowledge-base workloads. **AlloyDB AI** (GA) is used for operational RAG — where vector search must coexist with transactional data (product catalogs, user profiles, real-time inventory). **MCP Toolbox for Databases** (see ADR-0023) provides agent-to-database access for structured grounding via SQL. **Vertex AI Agent Builder** (via Vertex AI Search) handles enterprise document search agents.

## Rationale

1. **Vertex AI RAG Engine for production-grade RAG** — addresses the demo-to-prod gap explicitly: production RAG requires reliable chunking (not just splitting on newlines), embedding management, index versioning, and retrieval quality evaluation. RAG Engine provides these without custom code.
2. **AlloyDB AI for operational RAG** — when an agent must combine "find products similar to this embedding" with "where current stock > 0 AND price < $50", a vector-capable relational database is required, not a pure vector store. AlloyDB AI's native Gemini embedding integration and multimodal retrieval alongside PostgreSQL SQL makes it the right choice.
3. **Vertex AI Search for enterprise document grounding** — for agents grounded in internal documents (PDFs, Drive, SharePoint), Vertex AI Agent Builder's Vertex AI Search provides managed data stores with no custom indexing pipeline.
4. **MCP Toolbox for agent database access** — rather than giving agents raw database credentials and unparameterised queries, MCP Toolbox provides typed, governed tool definitions that call databases safely.

## Consequences

### Positive
- Vertex AI RAG Engine integrates directly with Agent Engine and ADK — no custom retrieval code in agent logic
- AlloyDB AI eliminates the need for a separate vector database alongside a relational database for operational use cases
- Vertex AI Search handles connector complexity (Drive, SharePoint) without custom ingestion pipelines

### Negative / Trade-offs
- Vertex AI RAG Engine has limited chunking strategy options compared to custom chunking pipelines (LlamaIndex, Unstructured) — complex document types may require preprocessing before ingestion
- AlloyDB AI is PostgreSQL-compatible but not a drop-in replacement for Cloud SQL — evaluate migration effort for existing Cloud SQL workloads before migrating to AlloyDB AI
- Cloud Spanner vector search is a viable alternative for globally-distributed transactional + vector workloads but at significantly higher cost than AlloyDB AI for regional deployments

### Risks
- [RISK: MED] RAG Engine index freshness — configure automated re-ingestion schedules when source data changes; stale indexes cause hallucinated "facts" from outdated information
- [RISK: LOW] AlloyDB AI embedding calls use Gemini embedding model — embedding costs are billed per call during indexing; estimate embedding cost for large catalogs before committing to AlloyDB AI for high-cardinality data

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Cloud Spanner with Vector Search | Globally distributed with strong consistency — correct for global-scale transactional + vector; significantly more expensive than AlloyDB AI for regional workloads |
| BigQuery vector search | Good for analytics-adjacent RAG (queries over training data); too slow (seconds-scale) for interactive retrieval in user-facing RAG applications |
| Third-party vector DBs (Pinecone, Weaviate, Qdrant) | External vendor dependency, data egress from GCP, separate IAM; Vertex AI RAG Engine and AlloyDB AI cover the requirement within the GCP trust boundary |
| Self-managed pgvector on Cloud SQL | Valid for small-scale; lacks AlloyDB AI's native Gemini embedding integration, multimodal retrieval, and scale |

## Implementation Notes

1. Vertex AI RAG Engine: create corpus via `google-cloud-aiplatform`; ingest GCS documents; query via `rag.retrieval_query()` in ADK agent tool definitions
2. AlloyDB AI: enable `google_ml_integration` extension; use `embedding()` function for in-database embedding generation; create `vector` index with `scann` for high-throughput ANN queries
3. MCP Toolbox: define database tools in `toolbox.yaml` with parameterised queries (no string interpolation); deploy to Cloud Run and connect to ADK agents via MCP
4. Vertex AI Agent Builder: create data store in Agent Builder console; connect to Drive, GCS, or web crawl; expose as Vertex AI Search tool in ADK agent
5. Set re-ingestion triggers: Cloud Scheduler job → Cloud Functions → RAG Engine `import_rag_files()` for scheduled freshness; EventArc on GCS upload for event-driven freshness

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
