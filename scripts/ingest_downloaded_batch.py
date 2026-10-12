#!/usr/bin/env python3
"""
Batch Ingest Script for DocIntel Platform
Ingests all 15 downloaded files into:
- PostgreSQL (Documents + DocumentChunk with pgvector embeddings)
- MongoDB (Flexible metadata, character counts, tags)
- ChromaDB (Vector collection)
- Cryptographic SHA-256 Audit Ledger
- Real-time notification event bus
"""

import os
import json
import requests

BASE_URL = "http://localhost:8000"
BATCH_DIR = "/home/vhanghar/Coding/enterprise-doc-intelligence/documents/downloaded_batch"

DOC_CONFIGS = [
    {
        "filename": "Q1_2027_SaaS_Revenue_Forecast.txt",
        "title": "Q1 2027 SaaS Revenue & Margin Forecast",
        "department": "finance",
        "classification": "confidential",
        "vendor": "Strategic FP&A",
        "tags": ["forecast", "revenue", "saas", "cogs"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Q4_Vendor_Procurement_Invoices.txt",
        "title": "Q4 Vendor Procurement & Technology Invoices Batch",
        "department": "finance",
        "classification": "internal",
        "vendor": "Databricks / Snowflake / CrowdStrike",
        "tags": ["procurement", "invoice", "vendor", "payments"],
        "target_status": "UNDER_REVIEW"
    },
    {
        "filename": "Capital_Asset_Depreciation_Schedule.txt",
        "title": "Capital Asset Depreciation & Tax Amortization Schedule",
        "department": "finance",
        "classification": "internal",
        "vendor": "Ernst & Young LLP",
        "tags": ["assets", "depreciation", "tax", "accounting"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Master_Services_Agreement_CloudScale.txt",
        "title": "Master Services Agreement - CloudScale Technologies",
        "department": "legal",
        "classification": "confidential",
        "vendor": "CloudScale Networks LLC",
        "tags": ["msa", "contract", "sla", "liability"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Mutual_Non_Disclosure_Agreement_Tier1.txt",
        "title": "Standard Mutual Non-Disclosure Agreement (MNDA)",
        "department": "legal",
        "classification": "internal",
        "vendor": "Legal Corporate Affairs",
        "tags": ["nda", "confidentiality", "legal", "compliance"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Patent_Assignment_and_IP_Transfer.txt",
        "title": "Employee Patent Assignment & Proprietary Inventions Transfer",
        "department": "legal",
        "classification": "restricted",
        "vendor": "US Patent & Trademark Office",
        "tags": ["patent", "ip", "invention", "assignment"],
        "target_status": "APPROVED"
    },
    {
        "filename": "2027_Comprehensive_Employee_Handbook.txt",
        "title": "Global Employee Handbook & Workplace Guidelines 2027",
        "department": "hr",
        "classification": "internal",
        "vendor": "Global People Operations",
        "tags": ["handbook", "policies", "pto", "benefits"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Executive_Compensation_and_Equity_Framework.txt",
        "title": "Executive Compensation & Performance Equity Incentive Plan",
        "department": "hr",
        "classification": "restricted",
        "vendor": "Board Compensation Committee",
        "tags": ["executive", "equity", "compensation", "bonus"],
        "target_status": "UNDER_REVIEW"
    },
    {
        "filename": "Remote_Work_Security_and_Equipment_Policy.txt",
        "title": "Remote Work Security & Asset Protection Standards",
        "department": "hr",
        "classification": "public",
        "vendor": "IT Infrastructure & HR",
        "tags": ["remote_work", "security", "hardware", "policy"],
        "target_status": "APPROVED"
    },
    {
        "filename": "System_Architecture_Distributed_RAG.txt",
        "title": "Distributed Multi-Model RAG Architecture Specification",
        "department": "engineering",
        "classification": "internal",
        "vendor": "Core Systems Architecture",
        "tags": ["architecture", "rag", "vector", "database"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Zero_Trust_API_Gateway_Security_Playbook.txt",
        "title": "Zero-Trust API Gateway Security & Threat Mitigation",
        "department": "engineering",
        "classification": "confidential",
        "vendor": "Platform Security Engineering",
        "tags": ["zero_trust", "gateway", "tls", "api"],
        "target_status": "APPROVED"
    },
    {
        "filename": "SRE_Incident_Response_and_On_Call_Runbook.txt",
        "title": "SRE Incident Management & Escalation Runbook",
        "department": "engineering",
        "classification": "internal",
        "vendor": "Site Reliability Engineering",
        "tags": ["sre", "runbook", "incident", "on_call"],
        "target_status": "APPROVED"
    },
    {
        "filename": "SOC2_Type_II_Compliance_Audit_Report.txt",
        "title": "SOC-2 Type II Independent Service Auditor Report",
        "department": "general",
        "classification": "confidential",
        "vendor": "PricewaterhouseCoopers LLP (PwC)",
        "tags": ["soc2", "audit", "compliance", "security"],
        "target_status": "APPROVED"
    },
    {
        "filename": "Vendor_Third_Party_Risk_Assessment.txt",
        "title": "Third-Party Vendor Cybersecurity Risk Assessment",
        "department": "general",
        "classification": "internal",
        "vendor": "CISO Office",
        "tags": ["risk_assessment", "vendor", "nist", "supply_chain"],
        "target_status": "UNDER_REVIEW"
    },
    {
        "filename": "Data_Retention_and_Right_To_Be_Forgotten_Policy.txt",
        "title": "GDPR & CCPA Data Retention and Erasure Policy",
        "department": "general",
        "classification": "public",
        "vendor": "Global Data Privacy Office",
        "tags": ["gdpr", "ccpa", "privacy", "retention"],
        "target_status": "APPROVED"
    }
]

def main():
    print("=" * 70)
    print("  DocIntel Batch Ingestion Engine - Ingesting Downloaded Zip Files")
    print("=" * 70)

    # 1. Login as Admin
    login_res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": "AdminPass123!"}
    )
    if login_res.status_code != 200:
        print(f"[ERROR] Failed to log in as admin: {login_res.text}")
        return

    admin_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Authenticated as System Administrator (admin@example.com)\n")

    ingested_count = 0

    for cfg in DOC_CONFIGS:
        file_path = os.path.join(BATCH_DIR, cfg["filename"])
        if not os.path.exists(file_path):
            print(f"[SKIP] File not found: {cfg['filename']}")
            continue

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        files = {
            "file": (cfg["filename"], file_bytes, "text/plain")
        }
        data = {
            "title": cfg["title"],
            "department": cfg["department"],
            "classification": cfg["classification"],
            "vendor": cfg["vendor"],
            "tags": json.dumps(cfg["tags"])
        }

        upload_res = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, data=data)
        if upload_res.status_code not in [200, 201]:
            print(f"[FAIL] Upload failed for {cfg['filename']}: {upload_res.text}")
            continue

        doc_data = upload_res.json()
        doc_id = doc_data["id"]
        ingested_count += 1
        print(f"[*] Ingested {doc_id}: '{cfg['title']}' ({cfg['department']} / {cfg['classification']})")

        # Advance workflow to target status if specified
        target = cfg.get("target_status", "DRAFT")
        if target in ["UNDER_REVIEW", "APPROVED"]:
            # Submit for review
            sub_res = requests.post(
                f"{BASE_URL}/documents/{doc_id}/submit",
                headers=headers,
                json={"comment": "Auto-submitted via corporate ingestion pipeline"}
            )
            if target == "APPROVED" and sub_res.status_code == 200:
                # Approve
                app_res = requests.post(
                    f"{BASE_URL}/documents/{doc_id}/approve",
                    headers=headers,
                    json={"comment": "Approved and certified for enterprise vector search"}
                )
                if app_res.status_code == 200:
                    print(f"    └── Status advanced: DRAFT -> UNDER_REVIEW -> APPROVED")
            elif target == "UNDER_REVIEW" and sub_res.status_code == 200:
                print(f"    └── Status advanced: DRAFT -> UNDER_REVIEW")

    print("\n" + "=" * 70)
    print(f"[COMPLETED] Successfully ingested {ingested_count} documents across all stores:")
    print("  • PostgreSQL (Tables, Chunks & pgvector embeddings)")
    print("  • MongoDB (Flexible metadata, character counts, tags)")
    print("  • ChromaDB (Persistent vector index)")
    print("  • Cryptographic SHA-256 Ledger (Chained hash blocks)")
    print("  • Event Bus (Real-time notification events)")
    print("=" * 70)

if __name__ == "__main__":
    main()
