# DocIntel System Architecture: Distributed Multi-Model RAG & Vector Engine
**Document Revision**: v3.4  
**Author**: Principal Systems Architect  
**Department**: Engineering & AI Platform  

## 1. High-Level Architecture Overview
DocIntel utilizes a hybrid polyglot architecture ensuring zero data leakage, sub-100ms retrieval, and immutable audit logging.

```
[ Client Web App ] ──(HTTPS/Vite)──> [ FastAPI Gateway ]
                                           │
         ┌─────────────────────────────────┼──────────────────────────────┐
         ▼                                 ▼                              ▼
 [ PostgreSQL + pgvector ]        [ MongoDB Document Store ]     [ In-Memory Event Bus ]
   - HNSW Cosine Index               - Flexible JSON Metadata       - Kafka Consumer Daemon
   - Users & RBAC Tokens             - Extracted Entities           - Audit Event Queue
   - Cryptographic Ledger            - Page Layout Offsets          - WebSocket Alerts
```

## 2. Ingestion Pipeline & Chunking Strategy
1. **Extraction Engine**: Incoming `.pdf`, `.docx`, and `.md` streams are converted to unified UTF-8 page streams.
2. **Chunk Sizing**: 350-word windows with 35-word boundary overlaps to preserve semantic continuity across headings.
3. **Deterministic Feature Hashing**: 384-dimensional normalized vector projections enable zero-GPU cold starts on serverless environments.

## 3. Query Execution & Re-ranking
- **Hybrid Retrieval**: Combines Full-Text Search (Postgres TSVECTOR BM25 ranking) with cosine distance vector ranking:
  $$Score = 0.65 \times CosineSim + 0.35 \times TextRank$$
- **Access Control Filter**: Every vector search query appends mandatory SQL guardrails:
  `WHERE tenant_id = :tenant AND department = :dept`

## 4. Disaster Recovery & Replication
- PostgreSQL operates in Multi-AZ streaming replication with automated 60-second health check failover.
- WAL logs are archived continuously to object storage with 30-day point-in-time recovery (PITR).
