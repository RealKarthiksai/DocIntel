#!/usr/bin/env python3
"""
Enterprise Document Generator for DocIntel Platform
Generates 20 diverse, realistic corporate documents (.pdf, .docx, .txt, .md)
across Finance, Legal, HR, Engineering, and Security departments.
"""

import os
import pymupdf
import docx

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documents", "sample")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DOCUMENTS = [
    # 1. FINANCE
    {
        "filename": "Q1_2027_SaaS_Revenue_Forecast.pdf",
        "type": "pdf",
        "title": "Q1 2027 SaaS Revenue & Margin Forecast",
        "dept": "Finance",
        "classification": "Confidential",
        "content": """ACME GLOBAL HOLDINGS - FINANCIAL PLANNING & ANALYSIS
Title: Q1 2027 SaaS Recurring Revenue & Gross Margin Forecast
Date: January 15, 2027 | Prepared by: Strategic Finance & Treasury

1. EXECUTIVE SUMMARY
Acme Global projects Annual Recurring Revenue (ARR) to surpass $84.5M in Q1 2027, representing a 28.4% Year-over-Year expansion. The acceleration is primarily driven by Enterprise Tier adoption and multi-cloud database connector expansions.

2. REVENUE RECOGNITION BREAKDOWN (USD Millions)
- Enterprise Platform Licenses: $42.1M (50% of total ARR)
- AI Model Training & Inference Add-on: $18.4M (22% of total ARR)
- Professional Migration & Custom Integrations: $12.0M (14% of total ARR)
- 24/7 Premium Mission-Critical Support: $12.0M (14% of total ARR)
Total Consolidated Projected Gross Revenue: $84.5M

3. MARGIN PROFILES & COST OF GOODS SOLD (COGS)
- Cloud Infrastructure (AWS / GCP / Azure egress): $11.2M
- Third-Party LLM API Costs & GPU Clusters: $6.8M
- Support Engineering Headcount: $5.1M
Gross Margin: 72.6% (Expansion of 310 bps vs Q4 2026).

4. COVENANTS AND PAYMENT TERMS
All customer agreements exceeding $250,000 require Net 30 payment terms and dual executive sign-off. Wire instructions are locked under strict dual-custody verification.
"""
    },
    {
        "filename": "Q4_Vendor_Procurement_Invoices.docx",
        "type": "docx",
        "title": "Q4 Vendor Procurement & Technology Invoices Batch",
        "dept": "Finance",
        "classification": "Internal",
        "content": """GLOBAL PROCUREMENT & ACCOUNTS PAYABLE
Document Type: Vendor Batch Requisition & Payment Approval
Audit Cycle: Q4 Corporate Review

1. BATCH OVERVIEW
This batch contains vendor invoices submitted for dual-custody approval before wire release. Total batch obligation is $1,425,800.00 across 4 tier-1 suppliers.

2. INVOICE LINE ITEMS
- Vendor: Databricks Cloud Analytics
  Invoice Ref: DBX-2026-9812
  Amount: $620,000.00
  Description: Annual Lakehouse compute nodes and serverless SQL warehouse credits.
  Approval Status: Requires Engineering VP and Finance Director sign-off.

- Vendor: Snowflake Enterprise Computing
  Invoice Ref: SNOW-4421-B
  Amount: $415,000.00
  Description: Cross-region data sharing and elastic storage replication.
  Approval Status: Verified against master agreement terms.

- Vendor: CrowdStrike Falcon Cybersecurity
  Invoice Ref: CS-SEC-8801
  Amount: $240,800.00
  Description: 12,000 Endpoint EDR agents and managed threat hunting coverage.

- Vendor: GitHub Enterprise Cloud
  Invoice Ref: GH-ORG-3109
  Amount: $150,000.00
  Description: Copilot Business licenses and Actions CI/CD runner minutes.

3. PAYMENT DIRECTIVES
All disbursements must execute via Automated Clearing House (ACH) or Fedwire with cryptographic token verification. No checks or single-party transfers authorized.
"""
    },
    {
        "filename": "Capital_Asset_Depreciation_Schedule.txt",
        "type": "txt",
        "title": "Capital Asset Depreciation & Tax Amortization Schedule",
        "dept": "Finance",
        "classification": "Internal",
        "content": """CAPITAL EXPENDITURE ASSET LEDGER (MACRS 5-YEAR & 7-YEAR SCHEDULE)
Classification: Internal Corporate Accounting Record
Fiscal Year: 2026 - 2027

Asset Category 1: High-Performance GPU Computing Clusters
- Description: 32x NVIDIA H100 SXM5 80GB Server Nodes
- Purchase Date: March 2026
- Capitalized Cost: $2,840,000.00
- Depreciation Method: Modified Accelerated Cost Recovery System (MACRS) 5-Year
- Year 1 Depreciation Rate: 20.00% ($568,000.00)
- Year 2 Depreciation Rate: 32.00% ($908,800.00)
- Residual Salvage Value: $142,000.00

Asset Category 2: Office Facilities & Data Center Infrastructure
- Description: Primary Austin Data Center Backup Generators & HVAC Upgrades
- Purchase Date: August 2026
- Capitalized Cost: $1,250,000.00
- Depreciation Method: Straight Line (15-Year Life)
- Annual Deduction: $83,333.33

Auditor Sign-off: Ernst & Young LLP
Review Status: Pending Dual Controller Review
"""
    },

    # 2. LEGAL & CONTRACTS
    {
        "filename": "Master_Services_Agreement_CloudScale.pdf",
        "type": "pdf",
        "title": "Master Services Agreement - CloudScale Technologies",
        "dept": "Legal",
        "classification": "Confidential",
        "content": """MASTER SERVICES AGREEMENT (MSA)
Contract Identification: MSA-2027-CS-0091
Effective Date: February 1, 2027
Parties: Acme Corporation ('Client') and CloudScale Networks LLC ('Service Provider')

1. SCOPE OF SERVICES
Service Provider agrees to deliver managed cloud orchestration, zero-downtime database failover, and multi-region Kubernetes routing in accordance with Exhibit A (Statement of Work).

2. SERVICE LEVEL AGREEMENT (SLA) & UPTIME COMMITMENT
2.1 Uptime Guarantee: Service Provider guarantees a monthly availability rate of 99.99% ('Four Nines').
2.2 Penalty Offsets: If monthly uptime drops below 99.95%, Client shall receive a 15% billing credit. If uptime drops below 99.90%, Client shall receive a 35% billing credit and retains the right to terminate without penalty.

3. DATA PRIVACY & INTELLECTUAL PROPERTY
All Client data ingested or processed by Service Provider remains the exclusive property of Client. Service Provider shall not use Client data for model training, telemetry harvesting, or benchmarking without express written consent.

4. INDEMNIFICATION & LIABILITY CAP
Total cumulative liability for breach of confidentiality or data protection obligations shall be capped at three times (3x) the annual contract value ($1,800,000.00 USD).

5. GOVERNING LAW & ARBITRATION
This Agreement is governed by the laws of the State of Delaware. Any unresolved disputes shall be submitted to binding commercial arbitration in Wilmington, Delaware under AAA rules.
"""
    },
    {
        "filename": "Mutual_Non_Disclosure_Agreement_Tier1.docx",
        "type": "docx",
        "title": "Standard Mutual Non-Disclosure Agreement (MNDA)",
        "dept": "Legal",
        "classification": "Internal",
        "content": """STANDARD CORPORATE MUTUAL NON-DISCLOSURE AGREEMENT
Legal Document ID: MNDA-STANDARD-v4

1. DEFINITION OF CONFIDENTIAL INFORMATION
'Confidential Information' refers to any proprietary, technical, financial, or commercial information disclosed by either Party to the other, whether orally, in writing, electronically, or via source code repositories.

2. OBLIGATIONS OF THE RECEIVING PARTY
The Receiving Party agrees:
- To protect Confidential Information with the same degree of care it uses for its own sensitive data, but no less than reasonable care.
- Not to disclose Confidential Information to any third party except employees, legal counsel, and financial advisors who have an operational need-to-know.
- To use Confidential Information solely for the purpose of evaluating potential business transactions.

3. EXCLUSIONS FROM CONFIDENTIALITY
Information is not confidential if it:
(a) is or becomes publicly known through no breach by Receiving Party;
(b) was already known to Receiving Party prior to disclosure without restriction;
(c) is independently developed without reference to the Disclosing Party's data.

4. TERM AND SURVIVAL
This Agreement shall remain in effect for two (2) years. The confidentiality obligations regarding trade secrets and source code shall survive indefinitely.
"""
    },
    {
        "filename": "Patent_Assignment_and_IP_Transfer.pdf",
        "type": "pdf",
        "title": "Employee Patent Assignment & Proprietary Inventions Transfer",
        "dept": "Legal",
        "classification": "Restricted",
        "content": """INVENTION ASSIGNMENT AND PROPRIETARY INFORMATION AGREEMENT
Classification: STRICTLY RESTRICTED (Legal / Executive)
Reference: PAT-IP-2027-012

1. RECITALS
This Agreement ensures that all intellectual property, algorithmic designs, cryptographic protocols, neural network weights, and software architectures created by employees in the scope of employment are exclusively assigned to Acme Corporation.

2. SCOPE OF INVENTIONS ASSIGNED
Employee hereby transfers and irrevocably assigns to Company all right, title, and interest worldwide in and to:
- US Patent Application No. 18/942,109: 'Deterministic Cryptographic Hash Chaining for Distributed Ledger Workflows'
- US Patent Application No. 18/942,110: 'Zero-Copy Vector Quantization for Serverless Neural Search'
- All registered copyrights, trade dress, masks, and architectural schematics related to the DocIntel Platform.

3. GOVERNING JURISDICTION & WAIVER
Employee waives all moral rights and confirms receipt of adequate consideration under the corporate invention reward program.
"""
    },

    # 3. HUMAN RESOURCES
    {
        "filename": "2027_Comprehensive_Employee_Handbook.docx",
        "type": "docx",
        "title": "Global Employee Handbook & Workplace Guidelines 2027",
        "dept": "HR",
        "classification": "Internal",
        "content": """ACME CORPORATION - GLOBAL EMPLOYEE HANDBOOK
Version: 5.2 | Effective Date: January 1, 2027
Approved by: Chief People Officer & General Counsel

1. WELCOME & CORE VALUES
At Acme Corporation, our mission is to empower global knowledge workers through secure intelligence tools. Our core pillars are:
- Radical Transparency: We document decisions in open architecture records.
- Customer Privacy First: Zero tolerance for unauthorized data sharing.
- Continuous Innovation: We encourage bold experiments with structured safety guardrails.

2. WORK ENVIRONMENT & FLEXIBLE SCHEDULES
- Hybrid Workplace Policy: Team members may work remotely up to three (3) days per week, subject to departmental manager alignment.
- Core Collaboration Hours: Teams are expected to be available for synchronous communication between 10:00 AM and 3:00 PM local time.
- Home Office Stipend: All full-time employees are eligible for an annual $1,200 equipment refresh allowance.

3. PAID TIME OFF (PTO) & PARENTAL LEAVE
- Flexible Vacation: Salaried employees receive flexible PTO with a mandatory minimum of 15 days taken annually.
- Parental Leave: 16 weeks of fully paid leave for birth, adoption, or foster placement for all primary and secondary caregivers.
- Wellness Days: The company observes quarterly global recharge days where all non-critical operations are paused.

4. HARASSMENT & EQUAL EMPLOYMENT OPPORTUNITY
Acme Corporation is committed to a harassment-free workplace. Violations should be reported directly to People Ops or via the anonymous ethics hotline.
"""
    },
    {
        "filename": "Executive_Compensation_and_Equity_Framework.pdf",
        "type": "pdf",
        "title": "Executive Compensation & Performance Equity Incentive Plan",
        "dept": "HR",
        "classification": "Restricted",
        "content": """BOARD OF DIRECTORS - COMPENSATION COMMITTEE
Title: Executive Long-Term Equity Incentive Program (LTI)
Fiscal Year: 2027 - 2029 | Classification: STRICTLY RESTRICTED

1. PURPOSE AND ELIGIBILITY
This program aligns C-Suite and Vice President leadership with multi-year shareholder value creation. Eligible roles include CEO, CTO, CFO, CRO, and General Counsel.

2. INCENTIVE STRUCTURE
- Base Salary: Targeted at 50th percentile of peer SaaS benchmarks ($400,000 - $550,000).
- Annual Performance Bonus: 60% of base, contingent on achieving ARR expansion targets ($95M) and Net Revenue Retention (NRR > 125%).
- Performance Stock Units (PSUs): 4-year vesting with double-trigger change-of-control protection.

3. CLAWBACK PROVISIONS
In the event of financial restatement or verified compliance malfeasance, the Board reserves the right to claw back any equity grants or bonuses disbursed within the trailing 36 months.
"""
    },
    {
        "filename": "Remote_Work_Security_and_Equipment_Policy.txt",
        "type": "txt",
        "title": "Remote Work Security & Asset Protection Standards",
        "dept": "HR",
        "classification": "Public",
        "content": """INFORMATION SECURITY & PEOPLE OPERATIONS DIRECTIVE
Topic: Work-From-Anywhere Hardware and Credential Standards
Distribution: Public Corporate Policy

1. EQUIPMENT REQUIREMENTS
- Employees must use only company-managed Apple MacBooks or Lenovo ThinkPads enrolled in MDM (Mobile Device Management).
- Personal computers (BYOD) are strictly prohibited from connecting to corporate GitHub, Jira, and production cloud consoles.
- Full-disk encryption (FileVault / BitLocker) is mandatory and continuously audited.

2. NETWORK SECURITY
- Public Wi-Fi networks (airports, cafes) require the mandatory corporate WireGuard VPN tunnel.
- Household Wi-Fi routers must utilize WPA3 or WPA2-Enterprise encryption with default administrative passwords modified.

3. LOST OR STOLEN DEVICES
In the event of hardware loss or theft, notify security-incident@company.com within two (2) hours to trigger remote cryptographic wiping.
"""
    },

    # 4. ENGINEERING & ARCHITECTURE
    {
        "filename": "System_Architecture_Distributed_RAG.md",
        "type": "md",
        "title": "Distributed Multi-Model RAG Architecture Specification",
        "dept": "Engineering",
        "classification": "Internal",
        "content": """# DocIntel System Architecture: Distributed Multi-Model RAG & Vector Engine
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
  $$Score = 0.65 \\times CosineSim + 0.35 \\times TextRank$$
- **Access Control Filter**: Every vector search query appends mandatory SQL guardrails:
  `WHERE tenant_id = :tenant AND department = :dept`

## 4. Disaster Recovery & Replication
- PostgreSQL operates in Multi-AZ streaming replication with automated 60-second health check failover.
- WAL logs are archived continuously to object storage with 30-day point-in-time recovery (PITR).
"""
    },
    {
        "filename": "Zero_Trust_API_Gateway_Security_Playbook.pdf",
        "type": "pdf",
        "title": "Zero-Trust API Gateway Security & Threat Mitigation",
        "dept": "Engineering",
        "classification": "Confidential",
        "content": """ENTERPRISE SECURITY ENGINEERING SPECIFICATION
Title: Zero-Trust API Gateway Architecture & Threat Mitigation
Classification: Confidential Technical Blueprint

1. AUTHENTICATION & TOKEN LIFECYCLE
- All ingress traffic terminates at Envoy API Gateways enforcing TLS 1.3 with strict Forward Secrecy cipher suites.
- Identity is verified via ephemeral RS256/HS256 JWT tokens with a maximum lifespan of 24 hours.
- Token revocation is enforced across distributed nodes using token-fingerprint blacklists.

2. RATE LIMITING & DOS MITIGATION
- Public Endpoints (/auth/login): 5 requests per minute per IP using token-bucket rate limiters.
- Authenticated Ingestion (/documents/upload): 50 requests per hour per user account.
- Payload Body Size Limit: Strict 25 MB ceiling enforced at NGINX reverse proxy buffer.

3. DATABASE CONNECTION RESILIENCE
- Asyncpg connection pooling: Minimum 5 connections, maximum 20 connections per serverless worker.
- Pool pre-ping (`pool_pre_ping=True`) verifies socket health before query execution to eliminate stale socket crashes.
"""
    },
    {
        "filename": "SRE_Incident_Response_and_On_Call_Runbook.docx",
        "type": "docx",
        "title": "SRE Incident Management & Escalation Runbook",
        "dept": "Engineering",
        "classification": "Internal",
        "content": """SITE RELIABILITY ENGINEERING (SRE) RUNBOOK
Title: Production Sev-1 and Sev-2 Incident Response Protocol
Target Audience: On-Call Engineers, Engineering Managers, SREs

1. SEVERITY LEVEL DEFINITIONS
- SEV-1 (Critical Outage): Core document upload or vector search is down for > 20% of users. Maximum response time: 5 minutes.
- SEV-2 (Degraded Performance): Query latency > 2.5s or notification consumer backlog > 5,000 events. Maximum response time: 15 minutes.
- SEV-3 (Minor Defect): Single non-critical endpoint error with active fallback. Maximum response time: 2 hours.

2. INCIDENT COMMAND CHAIN
- Incident Commander (IC): Leads the war room, assigns tasks, and coordinates triage.
- Communications Lead: Posts updates to internal status channels every 15 minutes.
- Operations Lead: Inspects distributed trace logs, Grafana dashboards, and database connections.

3. ROLLBACK PROCEDURES
If a production deployment introduces critical defects:
`kubectl rollout undo deployment/docintel-backend-prod -n production`
Verify pods reach healthy status within 45 seconds before closing the war room.
"""
    },

    # 5. SECURITY & COMPLIANCE
    {
        "filename": "SOC2_Type_II_Compliance_Audit_Report.pdf",
        "type": "pdf",
        "title": "SOC-2 Type II Independent Service Auditor Report",
        "dept": "Security",
        "classification": "Confidential",
        "content": """INDEPENDENT SERVICE AUDITOR'S REPORT (SOC 2 TYPE II)
Audit Period: January 1, 2026 - December 31, 2026
Auditing Firm: PricewaterhouseCoopers LLP (PwC)
Scope: Security, Confidentiality, and Availability Trust Services Criteria

1. OPINION OF INDEPENDENT AUDITOR
In our opinion, Acme Corporation has maintained, in all material respects, effective controls to provide reasonable assurance that its service commitments and system requirements were achieved based on the applicable trust services criteria.

2. TEST OF OPERATING EFFECTIVENESS
- Control CC6.1 (Logical Access): 100% of tested user accounts enforced multi-factor authentication (MFA) via FIDO2 WebAuthn keys.
- Control CC6.6 (Boundary Protection): Firewalls and Kubernetes network policies successfully blocked unauthorized ingress traffic across all 12 sampling rounds.
- Control CC7.2 (Vulnerability Management): Critical CVEs were remediated within the mandatory 48-hour SLA window.

3. CRYPTOGRAPHIC DATA INTEGRITY FINDINGS
The DocIntel platform's SHA-256 audit ledger was evaluated. Zero hash chain bifurcations or broken sequence numbers were observed across 1.4 million recorded events.
"""
    },
    {
        "filename": "Vendor_Third_Party_Risk_Assessment.docx",
        "type": "docx",
        "title": "Third-Party Vendor Cybersecurity Risk Assessment",
        "dept": "Security",
        "classification": "Internal",
        "content": """CHIEF INFORMATION SECURITY OFFICER (CISO) DIRECTIVE
Topic: Third-Party Vendor Security Evaluation Matrix
Standard: NIST SP 800-161 Supply Chain Risk Management

1. EVALUATION CRITERIA
All external cloud and software vendors with access to company data must achieve a minimum security score of 85/100 across the following categories:
- Data Encryption: AES-256 at rest, TLS 1.3 in transit.
- Disaster Recovery: RPO < 1 hour, RTO < 4 hours.
- Personnel Screening: Mandatory background checks for all infrastructure engineers.
- Bug Bounty Program: Active vulnerability disclosure program with external researcher triage.

2. VENDOR RISK TIERS
- Tier 1 (High Risk): Cloud hosting, identity providers, database backends. Requires annual full penetration test review.
- Tier 2 (Medium Risk): Customer support ticketing, analytics tools. Requires quarterly questionnaire renewal.
- Tier 3 (Low Risk): General office collaboration software without access to production data.
"""
    },
    {
        "filename": "Data_Retention_and_Right_To_Be_Forgotten_Policy.txt",
        "type": "txt",
        "title": "GDPR & CCPA Data Retention and Erasure Policy",
        "dept": "Security",
        "classification": "Public",
        "content": """GLOBAL PRIVACY DIRECTIVE: DATA RETENTION & ERASURE
Compliance Alignment: EU GDPR Article 17 ('Right to Erasure') & CCPA Section 1798.105
Public Document Reference: PRIV-2027-RET

1. DEFAULT RETENTION SCHEDULES
- Customer Transaction Records: Retained for seven (7) years to comply with tax and audit regulations.
- Inactive Account Profiles: Automatically purged after 24 months of verified inactivity.
- Application Diagnostic Logs: Retained in warm storage for 30 days, compressed in cold storage for 90 days, then irreversibly erased.

2. DATA ERASURE WORKFLOW
When a verified erasure request is received:
1. Customer metadata is deleted from relational databases and MongoDB collections within 72 hours.
2. Vector embeddings associated with the user are scrubbed from the vector index.
3. Cryptographic audit logs retain an anonymized SHA-256 verification hash confirming the erasure action without storing PII.
"""
    }
]

def generate_pdf(doc_info, file_path):
    doc = pymupdf.open()
    # Split text into pages roughly every 1600 characters or 25 lines
    lines = doc_info["content"].strip().split("\n")
    lines_per_page = 28
    
    for i in range(0, len(lines), lines_per_page):
        page_lines = lines[i:i + lines_per_page]
        page = doc.new_page(width=595, height=842) # A4
        
        # Header banner
        page.insert_text(
            (40, 45), 
            f"DOCINTEL ENTERPRISE • {doc_info['dept'].upper()} • {doc_info['classification'].upper()}", 
            fontsize=8, 
            color=(0.4, 0.4, 0.5)
        )
        
        # Body text
        y = 80
        for line in page_lines:
            if line.isupper() and len(line) < 40:
                page.insert_text((40, y), line, fontsize=11, fontname="helv", color=(0.1, 0.1, 0.2))
                y += 18
            else:
                page.insert_text((40, y), line, fontsize=9.5, fontname="helv", color=(0.15, 0.15, 0.15))
                y += 15
                
        # Footer
        page.insert_text(
            (40, 810), 
            f"Confidential & Proprietary • Document ID: {doc_info['filename']}", 
            fontsize=7.5, 
            color=(0.6, 0.6, 0.6)
        )
        
    doc.save(file_path)
    doc.close()

def generate_docx(doc_info, file_path):
    doc = docx.Document()
    
    # Document Title
    doc.add_heading(doc_info["title"], level=0)
    
    p_meta = doc.add_paragraph()
    p_meta.add_run(f"Department: {doc_info['dept']} | Classification: {doc_info['classification']}\n").bold = True
    
    # Sections
    sections = doc_info["content"].split("\n\n")
    for sec in sections:
        lines = sec.strip().split("\n")
        if lines:
            if lines[0].isupper() or lines[0].startswith("1.") or lines[0].startswith("2.") or lines[0].startswith("3.") or lines[0].startswith("4."):
                doc.add_heading(lines[0], level=2)
                for body_line in lines[1:]:
                    doc.add_paragraph(body_line)
            else:
                doc.add_paragraph(sec)
                
    doc.save(file_path)

def generate_text(doc_info, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(doc_info["content"])

def main():
    print(f"[*] Generating {len(DOCUMENTS)} realistic enterprise documents into: {OUTPUT_DIR}")
    for doc in DOCUMENTS:
        target_path = os.path.join(OUTPUT_DIR, doc["filename"])
        file_type = doc["type"]
        
        if file_type == "pdf":
            generate_pdf(doc, target_path)
        elif file_type == "docx":
            generate_docx(doc, target_path)
        else:
            generate_text(doc, target_path)
            
        print(f"  [CREATED] {doc['filename']} ({doc['dept']} - {doc['classification']})")
        
    print("[SUCCESS] All sample enterprise files created successfully.")

if __name__ == "__main__":
    main()
