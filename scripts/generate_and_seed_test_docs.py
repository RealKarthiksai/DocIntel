#!/usr/bin/env python3
"""
Comprehensive Test Document Generator & Seeder.
Generates 17 realistic enterprise test documents in documents/sample/ (PDF, DOCX, TXT, MD)
and uploads them to the running FastAPI platform with full metadata, workflows, and ACLs.
"""

import os
import io
import json
import asyncio
import httpx
import pymupdf
import docx

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "documents", "sample")
os.makedirs(SAMPLES_DIR, exist_ok=True)
API_BASE = "http://localhost:8000"

TEST_DOCUMENTS_SPEC = [
    # --- LEGAL DEPARTMENT ---
    {
        "filename": "Vendor_Agreement.pdf",
        "filetype": "pdf",
        "title": "Vendor Master Services Agreement",
        "department": "legal",
        "classification": "internal",
        "vendor": "ABC Technologies Inc",
        "tags": ["contract", "vendor", "sla", "delaware"],
        "custom_fields": {"renewal_period": "12 months", "risk_level": "medium", "governing_law": "Delaware", "contract_value": "$250,000"},
        "transition_to": "APPROVED",
        "pages": [
            "VENDOR MASTER SERVICES AGREEMENT\n\nParties: Alpha Global Enterprises ('Client') and ABC Technologies Inc ('Vendor').\n\n1. SCOPE OF SERVICES\nVendor shall provide enterprise cloud infrastructure management, data pipeline orchestration, and technical support as detailed in Exhibit A.\n\n2. TERM AND RENEWAL\nThis Agreement commences on October 1, 2026 and shall remain in effect for an initial period of twelve (12) months. It will automatically renew for successive 12-month periods unless either party provides timely notice.",
            "3. TERMINATION CLAUSE\nThe agreement requires 30 days written notice for standard termination without cause. Either party may terminate immediately upon material breach if uncured within fifteen (15) days of notice.\n\n4. FEES AND PAYMENT\nInvoices will be submitted monthly. Payment terms are Net 30 days from date of invoice receipt.\n\n5. GOVERNING LAW\nThis Agreement shall be governed by the laws of the State of Delaware."
        ]
    },
    {
        "filename": "Executive_Contract.pdf",
        "filetype": "pdf",
        "title": "Executive Employment Agreement - Confidential",
        "department": "legal",
        "classification": "confidential",
        "vendor": "Board Compensation Committee",
        "tags": ["executive", "contract", "confidential", "severance"],
        "custom_fields": {"base_salary": "$650,000", "severance_months": 18, "equity_acceleration": True, "risk_level": "critical"},
        "transition_to": "UNDER_REVIEW",
        "pages": [
            "CONFIDENTIAL EXECUTIVE EMPLOYMENT AGREEMENT\n\nClassification: RESTRICTED / HIGHLY CONFIDENTIAL\nDepartment: LEGAL / EXECUTIVE\n\nParties: Enterprise Corporation and Chief Executive Officer.\n\n1. COMPENSATION & INCENTIVES\nBase compensation shall be $650,000 annually. Target annual performance incentive is 100% of base salary subject to board milestones.\n\n2. EQUITY INCENTIVES\nGrant of 250,000 stock options vesting over four years with a 1-year cliff.",
            "3. TERMINATION CONDITIONS & SEVERANCE\nThe executive agreement provides 90 days written notice for termination without cause and full golden parachute provisions. Upon termination without cause or change of control, the executive shall receive eighteen (18) months of base salary continuation, full acceleration of all unvested equity awards, and 24 months of executive healthcare continuation.\n\n4. NON-COMPETE COVENANTS\nThe executive agrees not to engage in competing business activities for a period of twenty-four (24) months following separation."
        ]
    },
    {
        "filename": "Mutual_Non_Disclosure_Agreement.docx",
        "filetype": "docx",
        "title": "Mutual Non-Disclosure Agreement (NDA)",
        "department": "legal",
        "classification": "confidential",
        "vendor": "Corporate Legal Counsel",
        "tags": ["legal", "nda", "confidential", "intellectual-property"],
        "custom_fields": {"term_years": 3, "dispute_resolution": "Arbitration", "jurisdiction": "New York"},
        "transition_to": "APPROVED",
        "paragraphs": [
            "MUTUAL NON-DISCLOSURE AND PROPRIETARY INFORMATION AGREEMENT",
            "This Mutual Non-Disclosure Agreement ('Agreement') is entered into by and between Enterprise Corporation and Participating Partner.",
            "1. DEFINITION OF CONFIDENTIAL INFORMATION: Confidential Information includes all non-public technical, financial, operational, product design, software source code, customer identities, and business strategies disclosed by either party directly or indirectly.",
            "2. STANDARD OF CARE: The Recipient party agrees to protect disclosed Confidential Information with the same degree of care it exercises regarding its own confidential assets of similar importance, but in no case less than reasonable care.",
            "3. TERM & SURVIVAL: This obligation of confidentiality shall remain binding for three (3) years from the date of final disclosure, preserving all trade secret protections indefinitely.",
            "4. GOVERNING LAW: This Agreement shall be construed in accordance with the substantive laws of the State of New York."
        ]
    },

    # --- HUMAN RESOURCES (HR) DEPARTMENT ---
    {
        "filename": "Employee_Policy.pdf",
        "filetype": "pdf",
        "title": "Global Employee Workplace Policy",
        "department": "hr",
        "classification": "internal",
        "vendor": "People Operations & HR Guild",
        "tags": ["hr", "workplace", "pto", "remote-work"],
        "custom_fields": {"effective_date": "2026-10-01", "pto_days": 20, "remote_days_per_week": 2},
        "transition_to": "APPROVED",
        "pages": [
            "GLOBAL EMPLOYEE WORKPLACE POLICY\n\n1. WORKING HOURS & ATTENDANCE\nThe standard workweek is 40 hours, Monday through Friday. Core operating hours are 9:00 AM to 5:00 PM local time.\n\n2. REMOTE WORK GUIDELINES\nEligible employees may work remotely up to two (2) days per week with direct manager approval. High-speed secure broadband and compliance with data protection rules are mandatory.",
            "3. PAID TIME OFF (PTO)\nFull-time personnel accrue twenty (20) days of paid annual leave per calendar year. Unused leave up to five (5) days may carry over to the subsequent year.\n\n4. CODE OF ETHICS\nAll staff must maintain respect, fairness, and zero tolerance for discrimination, harassment, or retaliation in all interactions."
        ]
    },
    {
        "filename": "HR_Employee_Handbook.docx",
        "filetype": "docx",
        "title": "Enterprise Employee Onboarding Handbook",
        "department": "hr",
        "classification": "internal",
        "vendor": "Global Talent Team",
        "tags": ["hr", "onboarding", "benefits", "probation"],
        "custom_fields": {"probation_period_months": 3, "health_plan": "Tier 1 Comprehensive", "relocation_assistance": True},
        "transition_to": "APPROVED",
        "paragraphs": [
            "ENTERPRISE EMPLOYEE ONBOARDING & CULTURE HANDBOOK",
            "Welcome to Enterprise Corporation. This handbook outlines company standards, fringe benefits, compensation structures, and professional development opportunities.",
            "1. PROBATIONARY TIMELINE: All new full-time hires undergo a 90-day introductory review period. Regular performance syncs occur at 30, 60, and 90 days with department managers.",
            "2. HEALTH & WELLNESS BENEFITS: Medical, dental, and vision insurance coverage commences on the first calendar day of the month following the hire date. The employer covers 85% of employee premiums.",
            "3. LEARNING & CONTINUING EDUCATION: Each team member is eligible for an annual professional development stipend of $2,500 for certified coursework, books, and industry conferences.",
            "4. GRIEVANCE REPORTING: Open-door communication is encouraged. Confidential human resources mediation is accessible anytime via hr-escalations@enterprise.com."
        ]
    },
    {
        "filename": "Executive_Severance_Policy.txt",
        "filetype": "txt",
        "title": "Executive Compensation & HR Severance Policy",
        "department": "hr",
        "classification": "confidential",
        "vendor": "Executive Compensation Committee",
        "tags": ["hr", "executive", "severance", "canary"],
        "custom_fields": {"fund_code": "HR-SECRET-8821", "parachute_multiplier": "1.5x", "restricted": True},
        "transition_to": "UNDER_REVIEW",
        "content": (
            "Executive Employment and Severance Agreement - RESTRICTED HR CONFIDENTIAL.\n\n"
            "In the event of an involuntary change in organizational control, senior leadership receives 18 months accelerated salary.\n"
            "The authorized executive golden parachute fund code is HR-SECRET-8821.\n"
            "Termination without cause requires 90 days written notification.\n"
            "Stock option grants accelerate 100% upon change-in-control triggers as ratified by the Board of Directors."
        )
    },

    # --- FINANCE DEPARTMENT ---
    {
        "filename": "Finance_Invoice.pdf",
        "filetype": "pdf",
        "title": "Q3 Enterprise Infrastructure Invoice",
        "department": "finance",
        "classification": "internal",
        "vendor": "CloudScale Infrastructure Corp",
        "tags": ["invoice", "finance", "q3", "gpu", "infrastructure"],
        "custom_fields": {"amount": "$148,500.00", "payment_terms": "Net 45", "invoice_no": "INV-2026-8921", "currency": "USD"},
        "transition_to": "UNDER_REVIEW",
        "pages": [
            "ENTERPRISE BILLING STATEMENT & INVOICE\n\nInvoice Number: INV-2026-8921\nDate: September 15, 2026\nBilled To: Enterprise Document Automation Division\nVendor: CloudScale Infrastructure Corp\n\nLINE ITEMS:\n1. Dedicated GPU Inference Cluster (3 Months) - $85,000.00\n2. Enterprise High-Throughput NVMe Storage (500TB) - $42,500.00\n3. 24/7 Managed SRE Monitoring Support - $21,000.00\n\nTOTAL AMOUNT DUE: $148,500.00 USD",
            "PAYMENT TERMS & WIRE INSTRUCTIONS:\nPayment Terms: Net 45 Days.\nBank: First International Commerce Bank\nAccount: 4892-0091-7721\nRouting: 021000021\nSWIFT: FICBUS33\nTax ID (EIN): 84-2910391\nLate payment penalty: 1.5% per month on overdue balances."
        ]
    },
    {
        "filename": "Q4_Financial_Audit_Report.txt",
        "filetype": "txt",
        "title": "Q4 Financial Audit & Revenue Projections",
        "department": "finance",
        "classification": "confidential",
        "vendor": "KPMG External Audit Team",
        "tags": ["finance", "audit", "revenue", "canary", "confidential"],
        "custom_fields": {"gross_revenue": "$48.2M", "operating_margin": "42.8%", "escrow_code": "FINANCE-SECRET-7392"},
        "transition_to": "APPROVED",
        "content": (
            "Corporate Finance Quarterly Audit and Revenue Report.\n\n"
            "Total gross revenues for the fiscal quarter reached $48.2 million with a net operating margin of 42.8%.\n"
            "The audited offshore financial escrow vault code is FINANCE-SECRET-7392.\n"
            "All capital expenditures exceeding $50,000 require dual signature authorization from both the VP of Finance and CFO.\n"
            "Depreciation calculations for data center hardware adhere to MACRS 5-year accelerated depreciation schedules."
        )
    },
    {
        "filename": "Capital_Expenditure_Budget_2027.pdf",
        "filetype": "pdf",
        "title": "FY2027 Capital Expenditure Budget Forecast",
        "department": "finance",
        "classification": "internal",
        "vendor": "Financial Planning & Analysis (FP&A)",
        "tags": ["finance", "budget", "capex", "forecasting"],
        "custom_fields": {"fiscal_year": 2027, "total_budget": "$12,400,000", "approved_by_board": True},
        "transition_to": "DRAFT",
        "pages": [
            "FY2027 CAPITAL EXPENDITURE (CAPEX) FORECAST\n\nPrepared by: Office of FP&A\nDate: October 2026\n\n1. OVERVIEW & STRATEGIC PRIORITIES\nThe FY2027 capital budget allocates $12,400,000 across core compute, storage, edge nodes, and disaster recovery infrastructure.\n\n2. COMPUTE & ACCELERATORS ($6,200,000)\nProcurement of next-generation tensor clusters for on-premise RAG model fine-tuning and inference pipelines.",
            "3. NETWORKING & RESILIENCE ($3,100,000)\nRedundant dark fiber interconnects and zero-latency campus fabric upgrades across North America and Europe data hubs.\n\n4. CONTINGENCY & APPROVAL LIMITS\nA 10% contingency reserve ($1,240,000) is held under CFO direct delegation authority."
        ]
    },

    # --- ENGINEERING DEPARTMENT ---
    {
        "filename": "Engineering_System_Architecture.pdf",
        "filetype": "pdf",
        "title": "Core Cloud Infrastructure Architecture",
        "department": "engineering",
        "classification": "internal",
        "vendor": "DevOps Architecture Guild",
        "tags": ["engineering", "kubernetes", "cloud", "architecture", "canary"],
        "custom_fields": {"clusters": 8, "mesh_token": "ENG-INTERNAL-4491", "regions": ["us-east-1", "eu-west-1", "ap-south-1"]},
        "transition_to": "APPROVED",
        "pages": [
            "CORE CLOUD INFRASTRUCTURE ARCHITECTURE\n\nEngineering Technical Documentation - Distributed Platform Guild.\n\n1. TOPOLOGY OVERVIEW\nOur distributed Kubernetes clusters operate across three multi-region availability zones (us-east-1, eu-west-1, ap-south-1).\nWorkload balancing is managed via Cilium eBPF service meshes with wireguard-level encryption.",
            "2. SERVICE MESH SECURITY & CANARY AUTH\nThe internal service mesh mutual TLS authentication token is ENG-INTERNAL-4491.\nDatabase read replicas are provisioned with automated failover routing with sub-second health probes.\nAll ingress traffic terminates at Envoy edge proxies enforcing mTLS certificate validation."
        ]
    },
    {
        "filename": "Engineering_Incident_Playbook.docx",
        "filetype": "docx",
        "title": "Engineering Incident Response Playbook",
        "department": "engineering",
        "classification": "internal",
        "vendor": "Site Reliability Engineering (SRE)",
        "tags": ["engineering", "sre", "playbook", "incidents"],
        "custom_fields": {"p0_sla_minutes": 15, "pagerduty_service": "sre-core-tier1", "escalation_tier": 3},
        "transition_to": "UNDER_REVIEW",
        "paragraphs": [
            "SITE RELIABILITY ENGINEERING - INCIDENT RESPONSE PLAYBOOK",
            "This playbook governs operational incident classification, war room protocols, and post-mortem review standards.",
            "1. INCIDENT CLASSIFICATION: Severity-1 indicates customer-facing downtime or data integrity risk. Severity-2 indicates degraded non-critical services. Severity-3 indicates internal tool disruption.",
            "2. WAR ROOM PROCEDURES: Severity-1 outages require an automated incident war room bridge within 5 minutes. The Incident Commander (IC) retains exclusive authority over rollback and communication directives.",
            "3. ROLLBACK & DEPLOYMENT LOCK: When latency exceeds P99 SLOs (>350ms) for consecutive 3 minutes, deployment pipelines automatically freeze. On-call engineers must follow the standard rollback pipeline checklist.",
            "4. BLAMELESS POST-MORTEM: Root Cause Analysis (RCA) documents must be drafted within 48 hours and reviewed in bi-weekly guild retrospectives."
        ]
    },
    {
        "filename": "Project_Alpha_Technical_Spec.md",
        "filetype": "md",
        "title": "Special Project Alpha Assignment",
        "department": "engineering",
        "classification": "restricted",
        "vendor": "Advanced Quantum Computing Lab",
        "tags": ["engineering", "project-alpha", "cryptography", "restricted", "canary"],
        "custom_fields": {"project_code": "ALPHA-9034", "canary_token": "ALPHA-CANARY-9034", "clearance_level": "Level 4"},
        "transition_to": "APPROVED",
        "acl_grant_email": "eng_emp@example.com",
        "content": (
            "# RESTRICTED PROJECT ALPHA DIRECTIVE & TECHNICAL SPECIFICATION\n\n"
            "**Classification**: STRICTLY RESTRICTED (Level 4 Operational Need-To-Know)\n"
            "**Lead Engineers**: Alpha Cryptography Research Cell\n\n"
            "## 1. Project Scope\n"
            "This classified project details quantum-resistant cryptographic hardware security modules (HSMs) implementing lattice-based Kyber and Dilithium algorithms.\n\n"
            "## 2. Authentication Passphrase\n"
            "The secret project alpha authorization passphrase is **ALPHA-CANARY-9034**.\n"
            "Access is strictly limited to explicitly cleared individual personnel via row-level security and document access policies.\n\n"
            "## 3. Tamper Detection\n"
            "Hardware zeroization executes automatically upon detecting physical chassis micro-switches triggers or voltage anomalies."
        )
    },
    {
        "filename": "API_Zero_Trust_Security_Guidelines.md",
        "filetype": "md",
        "title": "API Zero-Trust Architecture Guidelines",
        "department": "engineering",
        "classification": "internal",
        "vendor": "Application Security Team",
        "tags": ["engineering", "api", "zero-trust", "jwt", "mtls"],
        "custom_fields": {"auth_protocol": "OAuth 2.1 / OIDC", "token_ttl_seconds": 3600, "rate_limit_rps": 500},
        "transition_to": "APPROVED",
        "content": (
            "# API ZERO-TRUST ARCHITECTURE GUIDELINES\n\n"
            "## 1. Principles of Zero-Trust\n"
            "Every internal microservice request must be explicitly authenticated, authorized, and cryptographically verified regardless of network perimeter or origin IP.\n\n"
            "## 2. Token Standards\n"
            "- Short-lived asymmetric RSA-256 / Ed25519 signed JWT tokens with 1-hour expiration.\n"
            "- Tenant ID, Department scope, and Role claims must be validated at API gateway boundaries.\n\n"
            "## 3. Mutual TLS (mTLS)\n"
            "All inter-service gRPC and REST communications must enforce SPIFFE/SPIRE-issued x509 certificates with automated 24-hour rotation."
        )
    },
    {
        "filename": "Legacy_Software_Audit_2025.pdf",
        "filetype": "pdf",
        "title": "Legacy Monolith Decommissioning Audit 2025",
        "department": "engineering",
        "classification": "internal",
        "vendor": "Enterprise Architecture Office",
        "tags": ["engineering", "legacy", "audit", "decommissioned"],
        "custom_fields": {"decommission_year": 2025, "servers_retired": 140, "archived_by": "lead-arch@enterprise.com"},
        "transition_to": "ARCHIVED",
        "pages": [
            "LEGACY MONOLITH DECOMMISSIONING AUDIT REPORT (2025)\n\nDepartment: Engineering / Architecture\nStatus: FULLY RETIRED & ARCHIVED\n\n1. EXECUTIVE SUMMARY\nIn Q4 2025, the legacy Java monolith was completely phased out in favor of the asynchronous microservice and polyglot architecture.\nAll 140 physical blade servers across Dallas datacenter were wiped according to DoD 5220.22-M standards.",
            "2. DATA MIGRATION VERIFICATION\n100% of relational records were migrated into PostgreSQL with ACID constraints.\nAll historical attachments were ingested into distributed object storage and validated against SHA-256 checksums."
        ]
    },

    # --- GENERAL & COMPLIANCE DEPARTMENT ---
    {
        "filename": "Security_Policy.pdf",
        "filetype": "pdf",
        "title": "Corporate Information Security Policy",
        "department": "general",
        "classification": "internal",
        "vendor": "IT & SecOps Governance",
        "tags": ["security", "passwords", "mfa", "compliance"],
        "custom_fields": {"min_password_length": 14, "mfa_required": True, "password_rotation_days": 90},
        "transition_to": "DRAFT",
        "pages": [
            "CORPORATE INFORMATION SECURITY & ACCESS POLICY\n\n1. PURPOSE\nTo protect organizational data assets, customer records, and network infrastructure from unauthorized access, breach, and digital threats.\n\n2. PASSWORD REQUIREMENTS\nAll system passwords must contain a minimum of 14 characters, combining uppercase, lowercase, numbers, and special symbols. Passwords must be rotated every 90 days.",
            "3. MULTI-FACTOR AUTHENTICATION (MFA)\nHardware-backed or authenticator-app MFA is mandatory across all workstations, VPN connections, and cloud dashboards. SMS-based MFA is prohibited.\n\n4. INCIDENT REPORTING\nAny suspected security incident or lost device must be reported to sec-ops@example.com within two (2) hours of discovery."
        ]
    },
    {
        "filename": "Public_Code_of_Conduct.txt",
        "filetype": "txt",
        "title": "Public Workplace Code of Conduct",
        "department": "general",
        "classification": "public",
        "vendor": "Ethics & Compliance Committee",
        "tags": ["general", "compliance", "public", "canary"],
        "custom_fields": {"canary_token": "PUBLIC-CANARY-1001", "reporting_hotline": "1-800-ETHICS-LINE"},
        "transition_to": "APPROVED",
        "content": (
            "Enterprise Public Workplace Code of Conduct.\n\n"
            "All employees, contractors, partners, and visitors must maintain mutual respect, anti-harassment standards, and professional integrity.\n"
            "The public community engagement helpline is referenced by canary token PUBLIC-CANARY-1001.\n"
            "Workplace safety rules apply to all facilities worldwide without exception.\n"
            "Violations may be submitted anonymously to compliance-desk@enterprise.com."
        )
    },
    {
        "filename": "Vendor_Security_Evaluation.docx",
        "filetype": "docx",
        "title": "Vendor Security & Supply-Chain Evaluation",
        "department": "general",
        "classification": "internal",
        "vendor": "Cyber Risk Assessment Group",
        "tags": ["security", "vendor", "soc2", "audit"],
        "custom_fields": {"soc2_type2_required": True, "iso27001_certified": True, "cyber_insurance_min": "$5,000,000"},
        "transition_to": "DRAFT",
        "paragraphs": [
            "THIRD-PARTY VENDOR SECURITY & RISK AUDIT QUESTIONNAIRE",
            "Enterprise procurement requires all technology vendors with access to internal network perimeters or customer data to complete annual cyber hygiene assessments.",
            "1. CERTIFICATION CRITERIA: Vendors must furnish an independent SOC 2 Type II audit report less than twelve (12) months old covering Security, Availability, and Confidentiality trust principles.",
            "2. ENCRYPTION AT REST & IN TRANSIT: All data stores holding client data must utilize AES-256 encryption. Network transit must strictly use TLS 1.3.",
            "3. PENETRATION TESTING: Annual third-party penetration testing reports must be submitted, with zero unresolved High or Critical findings.",
            "4. BREACH NOTIFICATION SLA: In the event of a suspected or confirmed security breach, vendor must notify Enterprise Security Operations within twenty-four (24) hours."
        ]
    }
]


def create_physical_files():
    """Generates physical files on disk in documents/sample/"""
    print(f"[*] Generating {len(TEST_DOCUMENTS_SPEC)} test documents in '{SAMPLES_DIR}'...")
    
    for spec in TEST_DOCUMENTS_SPEC:
        filepath = os.path.join(SAMPLES_DIR, spec["filename"])
        ftype = spec["filetype"]
        
        if ftype == "pdf":
            doc = pymupdf.open()
            for page_text in spec["pages"]:
                page = doc.new_page(width=595, height=842) # A4 size
                rect = pymupdf.Rect(50, 50, 545, 792)
                page.insert_textbox(rect, page_text, fontsize=12, fontname="helv")
            doc.save(filepath)
            doc.close()
            print(f"  [PDF]  Saved '{spec['filename']}' ({len(spec['pages'])} pages)")
            
        elif ftype == "docx":
            doc = docx.Document()
            for p in spec["paragraphs"]:
                doc.add_paragraph(p)
            doc.save(filepath)
            print(f"  [DOCX] Saved '{spec['filename']}' ({len(spec['paragraphs'])} paragraphs)")
            
        elif ftype in ("txt", "md"):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(spec["content"])
            print(f"  [{ftype.upper()}]  Saved '{spec['filename']}' ({len(spec['content'])} chars)")

    print("[+] All physical test documents created successfully on disk!\n")


async def seed_documents_to_api():
    """Uploads documents to FastAPI backend with full metadata and workflow progressions."""
    print("[*] Connecting to platform API at " + API_BASE + "...")
    
    async with httpx.AsyncClient(timeout=45.0) as client:
        # 1. Login as Admin
        l_res = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "admin@example.com", "password": "AdminPass123!"}
        )
        if l_res.status_code != 200:
            print("[-] Admin login failed:", l_res.text)
            return
            
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[+] Logged in as admin@example.com")
        
        # 2. Get existing documents to avoid duplicate uploads
        docs_res = await client.get(f"{API_BASE}/documents", headers=headers)
        existing_docs = docs_res.json() if docs_res.status_code == 200 else []
        existing_titles = {d["title"]: d for d in existing_docs}
        print(f"[*] Found {len(existing_titles)} existing unique document titles in platform.\n")
        
        # 3. Look up eng_emp user ID for ACL grants if needed
        eng_emp_id = None
        for u_id in range(1, 20):
            # Probe or use known seeded ID
            pass
        # We can fetch via direct login or list
        eng_login = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "eng_emp@example.com", "password": "EngEmpPass123!"}
        )
        if eng_login.status_code == 200:
            eng_data = eng_login.json()
            eng_emp_id = eng_data.get("user_id") or eng_data.get("id")

        # 4. Upload & Progress Each Test Document
        seeded_count = 0
        for spec in TEST_DOCUMENTS_SPEC:
            title = spec["title"]
            filename = spec["filename"]
            filepath = os.path.join(SAMPLES_DIR, filename)
            
            if title in existing_titles:
                doc = existing_titles[title]
                doc_id = doc["id"]
                current_status = doc["status"]
                target_status = spec["transition_to"]
                print(f"  [EXISTS] '{title}' ({doc_id}) [Status: {current_status}]")
                
                # Advance status if needed
                if current_status == "DRAFT" and target_status in ("UNDER_REVIEW", "APPROVED", "ARCHIVED"):
                    await client.post(f"{API_BASE}/documents/{doc_id}/submit", headers=headers)
                    current_status = "UNDER_REVIEW"
                if current_status == "UNDER_REVIEW" and target_status in ("APPROVED", "ARCHIVED"):
                    await client.post(f"{API_BASE}/documents/{doc_id}/approve", headers=headers)
                    current_status = "APPROVED"
                if current_status == "APPROVED" and target_status == "ARCHIVED":
                    await client.post(f"{API_BASE}/documents/{doc_id}/archive", headers=headers)
                    current_status = "ARCHIVED"
                continue
                
            # Read file bytes
            with open(filepath, "rb") as f:
                content_bytes = f.read()
                
            mime_map = {
                "pdf": "application/pdf",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "txt": "text/plain",
                "md": "text/markdown"
            }
            mime = mime_map.get(spec["filetype"], "application/octet-stream")
            files = {"file": (filename, content_bytes, mime)}
            form_data = {
                "title": title,
                "department": spec["department"],
                "classification": spec["classification"],
                "vendor": spec["vendor"],
                "tags": json.dumps(spec["tags"]),
                "custom_fields": json.dumps(spec["custom_fields"])
            }
            
            up_res = await client.post(f"{API_BASE}/documents/upload", headers=headers, data=form_data, files=files)
            if up_res.status_code != 200:
                print(f"  [ERROR] Failed to upload '{title}': {up_res.text}")
                continue
                
            doc_data = up_res.json()
            doc_id = doc_data["id"]
            status_now = doc_data["status"]
            target_status = spec["transition_to"]
            seeded_count += 1
            print(f"  [UPLOAD] '{title}' ({filename}) -> ID: {doc_id} [{status_now}]")
            
            # Workflow transitions
            if target_status in ("UNDER_REVIEW", "APPROVED", "ARCHIVED"):
                s_res = await client.post(f"{API_BASE}/documents/{doc_id}/submit", headers=headers)
                if s_res.status_code == 200:
                    status_now = "UNDER_REVIEW"
                    
            if target_status in ("APPROVED", "ARCHIVED"):
                a_res = await client.post(f"{API_BASE}/documents/{doc_id}/approve", headers=headers)
                if a_res.status_code == 200:
                    status_now = "APPROVED"
                    
            if target_status == "ARCHIVED":
                arc_res = await client.post(f"{API_BASE}/documents/{doc_id}/archive", headers=headers)
                if arc_res.status_code == 200:
                    status_now = "ARCHIVED"
                    
            print(f"    -> Progressed to target state: [{status_now}]")
            
            # Grant explicit ACL if specified
            if spec.get("acl_grant_email") and eng_emp_id:
                share_data = {
                    "grantee_type": "USER",
                    "grantee_id": str(eng_emp_id),
                    "permission_level": "READ"
                }
                sh_res = await client.post(f"{API_BASE}/documents/{doc_id}/share", headers=headers, data=share_data)
                if sh_res.status_code == 200:
                    print(f"    -> Granted explicit ACL to user #{eng_emp_id} ({spec['acl_grant_email']})")

        print(f"\n[+] Successfully uploaded/verified {len(TEST_DOCUMENTS_SPEC)} test documents into the platform!")


def main():
    create_physical_files()
    asyncio.run(seed_documents_to_api())


if __name__ == "__main__":
    main()
