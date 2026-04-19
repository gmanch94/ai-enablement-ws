# ADR-0015: AWS — RAG & Vector Retrieval

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [rag]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

RAG pipelines on AWS require a managed retrieval layer that handles chunking, embedding, and hybrid retrieval, and a cost-efficient vector store for large-scale embedding indexes. Teams should not build bespoke chunking and embedding pipelines when managed services exist. A decision is needed on the canonical AWS RAG and vector storage pattern.

## Decision

We will use **Amazon Bedrock Knowledge Bases** as the primary managed RAG service — handling automatic chunking, embedding, vector storage, and retrieval without custom pipeline code. **Amazon S3 Vectors** (GA) is the default vector storage backend for Knowledge Bases and standalone vector workloads requiring cost-efficient storage at scale (up to 2B vectors per index). **Amazon OpenSearch Service** is used when hybrid (vector + keyword) retrieval or advanced query patterns are required beyond Knowledge Bases' capabilities.

## Rationale

1. **Bedrock Knowledge Bases eliminates RAG plumbing** — automatic chunking, embedding (via Bedrock embedding models), vector indexing, and retrieval are fully managed. Teams should not build custom chunking pipelines for standard document RAG.
2. **S3 Vectors for cost-efficient vector storage** — at ~100ms query latency with 2B vectors per index and S3 pricing, S3 Vectors provides a dramatically lower-cost vector store than OpenSearch or third-party solutions for most RAG workloads. GA since 2026 with 14-region availability.
3. **OpenSearch for hybrid retrieval** — when RAG requires BM25 keyword search combined with vector search (e.g., product search with lexical matching), OpenSearch Service's k-NN + BM25 hybrid mode is the right tier. This is not the default — S3 Vectors + Knowledge Bases covers the majority of document RAG use cases.
4. **Native AgentCore integration** — Bedrock Knowledge Bases integrate directly with Bedrock Agents and AgentCore, enabling RAG-augmented agents without custom retrieval code.

## Consequences

### Positive
- Zero-infrastructure RAG — Knowledge Bases handles chunking, embedding, and retrieval configuration
- S3 Vectors pricing significantly undercuts OpenSearch for pure vector workloads at scale
- Knowledge Bases support S3, Confluence, and SharePoint as data sources natively

### Negative / Trade-offs
- Bedrock Knowledge Bases has limited chunking customisation — for complex document structures (nested tables, multi-column PDFs), custom chunking pipelines may be required before ingestion
- S3 Vectors query latency (~100ms) may be too high for interactive user-facing RAG with strict p99 SLAs — use OpenSearch (lower latency) for sub-50ms requirements
- Amazon Kendra (enterprise search) has a high base cost ($1K+/month) without proportional advantage over Knowledge Bases for most RAG use cases

### Risks
- [RISK: MED] Knowledge Bases data source sync frequency determines knowledge freshness — configure incremental sync via EventBridge triggers on S3 data updates; do not rely solely on scheduled syncs
- [RISK: LOW] S3 Vectors is GA but relatively new — monitor AWS release notes for API changes in first 12 months; pin SDK version

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Amazon Kendra | High cost ($1K+/month base); strong for enterprise document search but not cost-effective for custom RAG pipelines where Knowledge Bases suffices |
| Self-managed FAISS on EC2 | No managed infra, no HA, no incremental update support; high ops burden; reserve for custom embedding research |
| Third-party vector DBs (Pinecone, Weaviate, Qdrant) | External vendor dependency, data egress costs, separate IAM integration; S3 Vectors covers the same requirement within the AWS trust boundary |
| DynamoDB for vector storage | DynamoDB is not a vector database — no native ANN search; use only for agent session state and feature serving (see ADR-0017) |

## Implementation Notes

1. Default path: Bedrock Knowledge Bases with S3 as data source + S3 Vectors as the vector backend
2. For hybrid retrieval: create OpenSearch Service domain with k-NN plugin enabled; configure Knowledge Bases to use OpenSearch as the vector store
3. Use `amazon-bedrock-agent-runtime` SDK: `retrieve_and_generate()` for single-call RAG; `retrieve()` for custom retrieval + generation pipelines
4. Knowledge Bases data sync: configure EventBridge rule on S3 `ObjectCreated` events to trigger incremental ingestion
5. Set chunking strategy: `FIXED_SIZE` with 512 tokens and 10% overlap as the default; switch to `SEMANTIC` chunking for mixed-format document corpora

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
