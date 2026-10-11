import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SLIDES_DATA = [
    {
        "title": "Enterprise Document Intelligence & Workflow Automation Platform",
        "subtitle": "Comprehensive Final Defense (Reviews 1, 2, 3, & 4)\nPresented by: Final Year Project Team",
        "bullets": [
            "Domain: Distributed Systems, Information Retrieval, Cloud Security & Enterprise Software",
            "Core Triad: Polyglot Persistence | Access-Aware Vector RAG | Cryptographic Audit Chaining",
            "Event Pipeline: Apache Kafka Microservices Architecture with Real-Time Notification Center",
            "Validation: 21/21 Passing Automated Tests | Zero Authorization Leakage | ACID Row Locking"
        ]
    },
    {
        "title": "Executive Summary & Core Platform Vision",
        "subtitle": "Unifying Document Intelligence, Workflow Integrity, and Enterprise Security",
        "bullets": [
            "The Problem: Unstructured enterprise document silos (PDF/DOCX) create severe compliance risks, unauthorized data leakage, and manual approval bottlenecks.",
            "Polyglot Persistence Engine: Relational PostgreSQL (ACID & Audit), Flexible MongoDB (Metadata), and ChromaDB (Vector HNSW).",
            "Access-Aware Vector RAG: Security boundary enforced directly within the vector retrieval layer—eliminating post-retrieval data leakage.",
            "Serialized State Machine: Workflow transitions protected by PostgreSQL row-level locks (SELECT ... FOR UPDATE).",
            "SHA-256 Audit Trail: Cryptographically chained ledger providing verifiable tamper detection.",
            "Kafka Event Pipeline: Microservices-based decoupled notification routing for real-time workflow alerts."
        ]
    },
    {
        "title": "Four-Review Engineering Progression",
        "subtitle": "Systematic Evolution from Requirements to Production-Grade Platform",
        "bullets": [
            "Review 1 (Problem Formulation & Requirements): Literature survey, industry motivation, functional & non-functional specifications, user personas.",
            "Review 2 (Architecture & Modeling): Polyglot database schema design, multi-tenant RBAC security model, finite state machine formal grammar.",
            "Review 3 (Core Implementation & Security Proofs): Ingestion pipeline (PyMuPDF), Access-Aware RAG retrieval, cryptographic SHA-256 audit chain, concurrency row locking, 18/18 test suite.",
            "Review 4 (Decoupling, Messaging & Final Delivery): Microservices decomposition, Apache Kafka event-driven notifications, React Notification Center, 21/21 automated tests, 100% project completion."
        ]
    },
    {
        "title": "[REVIEW 1] Problem Definition & Industry Motivation",
        "subtitle": "Critical Vulnerabilities in Modern Enterprise Document Workflows",
        "bullets": [
            "Document Silos & Discovery Deficits: Traditional keyword search fails on complex legal contracts, financial statements, and technical policies.",
            "Catastrophic Data Leakage in AI Systems: Standard RAG pipelines retrieve confidential data into memory before filtering, exposing sensitive terms.",
            "Concurrency Conflicts & Workflow Desynchronization: Simultaneous reviews cause race conditions, resulting in contradictory approvals.",
            "Vulnerability to Audit Tampering: Relational database logs are easily mutable by privileged database administrators without detection.",
            "Objective: Design and build a zero-trust, access-aware platform that prevents unauthorized leakage while automating workflows."
        ]
    },
    {
        "title": "[REVIEW 1] Literature Survey & Comparative Analysis",
        "subtitle": "Evaluating Traditional Systems vs. Proposed Access-Aware Architecture",
        "bullets": [
            "Traditional DMS (SharePoint, Alfresco): Static schemas, no semantic vector retrieval, vulnerable to unauthorized manual overrides.",
            "Standard GenAI/RAG (LangChain, LlamaIndex): Applies security filtering after top-k vector search—retrieves unauthorized chunks into RAM.",
            "Our Proposed Innovation - Access-Aware RAG: Injects JWT tenant and department claims directly into ChromaDB query conditions.",
            "Blockchain-Inspired Cryptographic Auditing: Implements SHA-256 block hashing where each event cryptographically signs the preceding event hash.",
            "Row-Level ACID Locking: Utilizes explicit PostgreSQL locks to prevent race conditions during state transitions."
        ]
    },
    {
        "title": "[REVIEW 1] System Requirements Specification (SRS)",
        "subtitle": "Detailed Functional and Non-Functional Engineering Boundaries",
        "bullets": [
            "Functional Requirement 1: Multi-format document ingestion (PDF, DOCX) with text extraction, sliding window chunking, and embedding generation.",
            "Functional Requirement 2: Multi-tenant Role-Based Access Control (RBAC) with granular department scoping (legal, finance, general).",
            "Functional Requirement 3: Finite State Machine enforcing valid transitions (DRAFT -> UNDER_REVIEW -> APPROVED/REJECTED -> ARCHIVED).",
            "Functional Requirement 4: Access-Aware Semantic Search with exact source citations (document title, chunk ID, page number).",
            "Functional Requirement 5: Real-time Kafka-driven notifications for pending reviews, approvals, and system alerts.",
            "Non-Functional: Sub-200ms REST p95 latency, 0.00% data leakage across roles and tenants, sub-second vector search."
        ]
    },
    {
        "title": "[REVIEW 2] System Architecture & Microservices Decoupling",
        "subtitle": "Modular, Scalable, Polyglot Cloud Architecture",
        "bullets": [
            "React 18 SPA (Port 5173/3000): Vite, TypeScript, Tailwind CSS, Lucide icons, responsive dashboard, and Notification Center.",
            "Core API Gateway & Services (Port 8000): FastAPI backend handling auth, ingestion, workflow execution, RAG, and audit logging.",
            "Kafka Event Pipeline: Producers emit structured events on topic 'document.workflow.events'.",
            "Notification Microservice (Port 8001): Dedicated consumer group subscribing to workflow events and dispatching targeted alerts.",
            "Polyglot Persistence Layer: PostgreSQL 16 (relational/ACID), MongoDB 7.0 (flexible metadata), ChromaDB (cosine HNSW index)."
        ]
    },
    {
        "title": "[REVIEW 2] Polyglot Persistence Architecture",
        "subtitle": "Optimal Storage Technology for Each Enterprise Data Requirement",
        "bullets": [
            "PostgreSQL 16: Users, hashed credentials, roles, document status, workflow history, SHA-256 audit ledger, and notifications.",
            "MongoDB 7.0: Schema-free dynamic attributes (custom_fields, counterparty data, renewal terms, token statistics, tags).",
            "ChromaDB Vector Store: 384-dimensional dense embeddings (all-MiniLM-L6-v2) indexed using Hierarchical Navigable Small World (HNSW).",
            "Why Polyglot?: Relational DBs cannot scale arbitrary JSON metadata; NoSQL DBs lack ACID serializability; vector DBs lack relational joins.",
            "Seamless Resilient Fallback: Native local support with embedded SQLite/Postgres and mock fallbacks ensures zero runtime failures."
        ]
    },
    {
        "title": "[REVIEW 2] Multi-Tenant RBAC & Department Scoping",
        "subtitle": "Granular Authorization Matrix Enforced Across Storage Tiers",
        "bullets": [
            "ADMIN Role: Scope ['*'] - Full global access across all departments (legal, finance, general); can execute all workflow transitions.",
            "MANAGER Role: Scope ['finance', 'general'] - Can view, submit, and approve finance and general documents; strictly blocked from legal documents.",
            "EMPLOYEE Role: Scope ['general'] - Baseline operational access; submit-only permissions (approvals/rejections rejected with 403 Forbidden).",
            "TENANT-B USER: Multi-tenant isolation boundary - Sees 0 documents or notifications from tenant-default.",
            "Cryptographic Verification: JWT Bearer tokens signed with HMAC-SHA256 containing user ID, role, tenant, and department scopes."
        ]
    },
    {
        "title": "[REVIEW 2] Finite State Machine Formal Specification",
        "subtitle": "Strict Lifecycle Grammar with Guard Conditions",
        "bullets": [
            "Permitted Transitions: DRAFT -> UNDER_REVIEW -> APPROVED / REJECTED -> ARCHIVED.",
            "Guard Conditions: Only users with MANAGER or ADMIN role matching the document's department can approve or reject.",
            "Terminal States: REJECTED and ARCHIVED documents cannot undergo further state modifications.",
            "Concurrency Protection: Every transition runs inside a serialized transaction utilizing SELECT ... FOR UPDATE row-level locks.",
            "Audit Emission: Every transition automatically triggers both an immutable SHA-256 audit log and a Kafka workflow event."
        ]
    },
    {
        "title": "[REVIEW 3] Document Ingestion & Chunking Pipeline",
        "subtitle": "High-Fidelity Multi-Page Parsing & Dense Vector Indexing",
        "bullets": [
            "Multi-Engine Extraction: PyMuPDF extracts text, page boundaries, and token counts from PDFs; python-docx extracts DOCX structures.",
            "Sliding Window Chunking: 200-word chunk size with 40-word overlap preserves semantic context across page boundaries.",
            "Dense Embeddings: sentence-transformers/all-MiniLM-L6-v2 generates 384-dimensional dense vectors.",
            "Metadata Indexing: Each chunk indexed in ChromaDB with document_id, document_title, tenant_id, department, and classification.",
            "Performance: Sub-second ingestion for multi-page enterprise documents."
        ]
    },
    {
        "title": "[REVIEW 3] Access-Aware RAG Engine (Zero Data Leakage)",
        "subtitle": "Eliminating Vector-Layer Privacy Breaches",
        "bullets": [
            "Vulnerability Identified: Standard vector search retrieves nearest neighbors without authorization, filtering afterwards.",
            "Our Access-Aware Algorithm: Inject JWT tenant and department claims directly into ChromaDB vector retrieval query:",
            "Filter Syntax: {'$and': [{'tenant_id': {'$eq': tenant}}, {'department': {'$in': user_departments}}]}",
            "Empirical Result: Employee querying 'executive contract termination' receives 0 chunks and 0 sources.",
            "Admin querying same question receives full severance details with exact citations (Document title, Page 2, Chunk ID).",
            "Zero Authorization Leakage: 100% verified across adversarial test suites."
        ]
    },
    {
        "title": "[REVIEW 3] Cryptographic SHA-256 Audit Trail",
        "subtitle": "Blockchain-Inspired Tamper-Evident Security Ledger",
        "bullets": [
            "Chained Hash Construction: Hash_i = SHA-256(Hash_{i-1} + ActorID + Action + DocID + Timestamp + Metadata).",
            "Genesis Block: Initialized with static zero-hash (0000...0000).",
            "Logged Actions: DOCUMENT_UPLOADED, SUBMITTED_FOR_REVIEW, APPROVED, REJECTED, ARCHIVED, RAG_QUERY.",
            "Tamper Verification API (/audit/verify): Iterates from genesis to head, recalculating every hash block.",
            "Integrity Guarantee: Any manual modification or deletion breaks the hash chain and flags the exact record ID."
        ]
    },
    {
        "title": "[REVIEW 3] Concurrency Control & Row-Level Locking",
        "subtitle": "Preventing Workflow Race Conditions Under High Concurrency",
        "bullets": [
            "The Threat: Simultaneous approval attempts by two managers can create double transitions and corrupt audit records.",
            "PostgreSQL Row Lock: SELECT * FROM documents WHERE id = :id FOR UPDATE;",
            "Execution Behavior: First manager acquires lock, transitions document to APPROVED, commits transaction.",
            "Second Manager Handling: Acquires lock after commit, detects document is already APPROVED, safely rejected with HTTP 409 Conflict.",
            "Verified via automated concurrent test harness with 0 race condition failures."
        ]
    },
    {
        "title": "[REVIEW 3] Benchmark Metrics & Performance Validation",
        "subtitle": "Empirical Verification Under Sustained Workloads",
        "bullets": [
            "REST API Average Latency: 5.81 ms",
            "REST API 95th Percentile (p95): 113.02 ms",
            "System Throughput: 160.25 requests/second under sustained concurrent load.",
            "RAG Search Median Latency (p50): 921.62 ms (including embedding and context generation).",
            "Security Metric: 0.00% cross-tenant and cross-department authorization leakage.",
            "Reliability Metric: 100% successful tamper detection on corrupted audit blocks."
        ]
    },
    {
        "title": "[REVIEW 4] Microservices Architecture & Decoupling",
        "subtitle": "Autonomous Services with Independent Service Contracts",
        "bullets": [
            "Core Document Intelligence Service (Port 8000): Manages ingestion, relational metadata, vector RAG, and state transitions.",
            "Notification Microservice (Port 8001): Subscribes to Kafka topic, processes events, persists notifications, and serves notification queries.",
            "Frontend SPA (Port 5173 / 3000): React 18, Vite, TypeScript, Tailwind CSS with modular routing and real-time polling.",
            "Decoupled Communication: Event-driven pub/sub via Apache Kafka ensures asynchronous, non-blocking workflow operations.",
            "Container Orchestration: Multi-container docker-compose.yml defines services, networks, volumes, and healthchecks."
        ]
    },
    {
        "title": "[REVIEW 4] Apache Kafka Event-Driven Architecture",
        "subtitle": "Real-Time Enterprise Messaging for Workflow Events",
        "bullets": [
            "Topic: 'document.workflow.events' handles all lifecycle and state changes.",
            "Event Schema: event_id, event_type, document_id, document_title, department, from_status, to_status, actor_id, tenant_id, timestamp.",
            "Consumer Group: 'enterprise-notification-service' with automatic offset tracking.",
            "Dual-Mode Strategy: Connects to live Kafka cluster via aiokafka; automatically fails over to resilient in-memory event bus if Kafka is offline.",
            "Zero Downtime: Guarantees 100% operational demo during battery-powered review environments."
        ]
    },
    {
        "title": "[REVIEW 4] Real-Time Notification Center UI",
        "subtitle": "Interactive Notification Hub in React SPA",
        "bullets": [
            "Header Bell Icon: Displays real-time unread notification badge counter.",
            "Interactive Dropdown Tray: Chronological event stream with color-coded status badges and department tags.",
            "Direct Navigation: One-click deep links to navigate directly to the affected document workspace.",
            "Read Management: Individual 'Mark as Read' and bulk 'Mark All as Read' actions.",
            "Kafka Health Indicator: Visual badge confirming active event streaming pipeline."
        ]
    },
    {
        "title": "[REVIEW 4] Full Automated Test Suite (21/21 Tests Passing)",
        "subtitle": "Comprehensive Quality Assurance Across All Functional Layers",
        "bullets": [
            "Auth Tests (4): Valid login, invalid password rejection, valid JWT /me, invalid token rejection.",
            "Document Tests (5): Valid PDF/DOCX ingestion, empty file rejection, invalid MIME rejection, RBAC department filtering.",
            "Health & Metrics Tests (2): Multi-store health check (/health), Prometheus-style metrics (/metrics).",
            "Kafka & Notification Tests (3): Event publishing on transitions, consumer RBAC routing, mark-as-read actions.",
            "RAG Security Tests (3): Employee vs Admin confidentiality barrier, cross-tenant isolation, prompt injection defense.",
            "Workflow Tests (3): Valid state transitions, invalid transition rejection, concurrent approval race protection."
        ]
    },
    {
        "title": "[REVIEW 4] Live Demonstration Workflow",
        "subtitle": "End-to-End Walkthrough Scenarios for Evaluation",
        "bullets": [
            "Demo 1 - One-Click Role Switcher: Switch between Admin, Manager, and Employee seamlessly on the login page.",
            "Demo 2 - Document Ingestion: Upload an enterprise PDF, verify metadata in MongoDB, ACID record in Postgres, chunks in ChromaDB.",
            "Demo 3 - Access-Aware RAG Barrier: Query confidential executive agreement; verify Employee blocked (0 sources), Admin granted.",
            "Demo 4 - Workflow Transition & Kafka Alert: Submit invoice, observe instant Kafka notification in Bell drawer, approve as Manager.",
            "Demo 5 - Cryptographic Audit Verification: Verify 30+ blocks with unbroken SHA-256 chain on the audit dashboard."
        ]
    },
    {
        "title": "Technical Challenges & Engineering Solutions",
        "subtitle": "Overcoming Distributed Systems & Security Hurdles",
        "bullets": [
            "Vector-Layer Privacy Leak: Solved by moving authorization checks from post-retrieval into the vector database query filter.",
            "Approval Race Conditions: Solved by employing PostgreSQL SELECT ... FOR UPDATE row-level serialization locks.",
            "Polyglot State Synchronization: Solved by atomic ingestion coordinating MongoDB IDs, PostgreSQL records, and ChromaDB embeddings.",
            "Review Reliability (Offline/Battery): Solved by engineering dual-mode fallbacks for Kafka, PostgreSQL, and LLMs."
        ]
    },
    {
        "title": "Conclusion & Future Research Roadmap",
        "subtitle": "Project Completion Summary & Enterprise Extensions",
        "bullets": [
            "Conclusion: All requirements for Review 1, 2, 3, and 4 are 100% completed, verified, and running live.",
            "Key Innovation: Access-Aware RAG + Cryptographic Audit Chaining establishes a new standard for secure enterprise document workflows.",
            "Future Roadmap: Optical Character Recognition (OCR) for scanned PDFs; field-level redaction; distributed multi-region Kafka partitions.",
            "Thank You! Open for questions and live demonstration."
        ]
    }
]


def create_presentation(output_path="docs/Enterprise_Document_Intelligence_Review_4_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    DARK_NAVY = RGBColor(15, 23, 42)     # #0f172a
    ACCENT_BLUE = RGBColor(37, 99, 235)  # #2563eb
    TEXT_DARK = RGBColor(30, 41, 59)     # #1e293b
    TEXT_MUTED = RGBColor(100, 116, 139) # #64748b
    BG_LIGHT = RGBColor(248, 250, 252)   # #f8fafc
    WHITE = RGBColor(255, 255, 255)

    for i, slide_info in enumerate(SLIDES_DATA):
        slide = prs.slides.add_slide(blank_layout)

        # Header background banner
        header_shape = slide.shapes.add_shape(
            1, Inches(0), Inches(0), Inches(13.333), Inches(1.3)
        )
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = DARK_NAVY
        header_shape.line.color.rgb = DARK_NAVY

        # Slide Number Badge
        badge_shape = slide.shapes.add_shape(
            1, Inches(12.0), Inches(0.35), Inches(0.9), Inches(0.55)
        )
        badge_shape.fill.solid()
        badge_shape.fill.fore_color.rgb = ACCENT_BLUE
        badge_shape.line.color.rgb = ACCENT_BLUE
        tf_badge = badge_shape.text_frame
        tf_badge.text = f"{i+1}/22"
        tf_badge.paragraphs[0].font.size = Pt(14)
        tf_badge.paragraphs[0].font.bold = True
        tf_badge.paragraphs[0].font.color.rgb = WHITE
        tf_badge.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(11.0), Inches(0.9))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide_info["title"]
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = WHITE

        # Subtitle
        subtitle_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.5), Inches(0.6))
        tf_sub = subtitle_box.text_frame
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = slide_info["subtitle"]
        p_sub.font.size = Pt(15)
        p_sub.font.italic = True
        p_sub.font.color.rgb = ACCENT_BLUE

        # Content Box with Bullets
        content_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(11.7), Inches(4.8))
        tf_content = content_box.text_frame
        tf_content.word_wrap = True

        for b_idx, bullet in enumerate(slide_info["bullets"]):
            p_b = tf_content.add_paragraph() if b_idx > 0 else tf_content.paragraphs[0]
            p_b.text = f"•  {bullet}"
            p_b.font.size = Pt(15)
            p_b.font.color.rgb = TEXT_DARK
            p_b.space_after = Pt(12)

    prs.save(output_path)
    print(f"PowerPoint Presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    create_presentation()
