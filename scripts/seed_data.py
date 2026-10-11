import os
import json
import httpx
import asyncio

API_BASE = "http://localhost:8000"
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "documents", "sample")

SEEDED_DOCS = [
    {
        "filename": "Vendor_Agreement.pdf",
        "title": "Vendor Master Services Agreement",
        "department": "legal",
        "classification": "internal",
        "vendor": "ABC Technologies",
        "tags": ["contract", "vendor"],
        "custom_fields": {"renewal_period": "12 months", "risk_level": "medium"},
        "transition_to": "APPROVED"
    },
    {
        "filename": "Employee_Policy.pdf",
        "title": "Global Employee Workplace Policy",
        "department": "general",
        "classification": "internal",
        "vendor": "HR Department",
        "tags": ["hr", "policy"],
        "custom_fields": {"effective_date": "2026-10-01", "pto_days": 20},
        "transition_to": "APPROVED"
    },
    {
        "filename": "Finance_Invoice.pdf",
        "title": "Q3 Enterprise Infrastructure Invoice",
        "department": "finance",
        "classification": "internal",
        "vendor": "CloudScale Infrastructure Corp",
        "tags": ["invoice", "finance", "q3"],
        "custom_fields": {"amount": "$148,500.00", "payment_terms": "Net 45"},
        "transition_to": "UNDER_REVIEW"
    },
    {
        "filename": "Security_Policy.pdf",
        "title": "Corporate Information Security Policy",
        "department": "general",
        "classification": "internal",
        "vendor": "IT & SecOps",
        "tags": ["security", "it", "compliance"],
        "custom_fields": {"min_password_length": 14, "mfa_required": True},
        "transition_to": "DRAFT"
    },
    {
        "filename": "Executive_Contract.pdf",
        "title": "Executive Employment Agreement - Confidential",
        "department": "legal",
        "classification": "confidential",
        "vendor": "Board Compensation Committee",
        "tags": ["executive", "contract", "confidential"],
        "custom_fields": {"severance_months": 18, "equity_acceleration": True, "risk_level": "critical"},
        "transition_to": "UNDER_REVIEW"
    }
]

async def seed():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login as Admin
        login_res = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "admin@example.com", "password": "AdminPass123!"}
        )
        if login_res.status_code != 200:
            print("Admin login failed:", login_res.text)
            return
        
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Logged in as admin@example.com")

        # 2. Upload Each Document
        for item in SEEDED_DOCS:
            filepath = os.path.join(SAMPLES_DIR, item["filename"])
            if not os.path.exists(filepath):
                print(f"Skipping {item['filename']}, not found.")
                continue

            with open(filepath, "rb") as f:
                file_bytes = f.read()

            files = {"file": (item["filename"], file_bytes, "application/pdf")}
            data = {
                "title": item["title"],
                "department": item["department"],
                "classification": item["classification"],
                "vendor": item["vendor"],
                "tags": json.dumps(item["tags"]),
                "custom_fields": json.dumps(item["custom_fields"])
            }

            upload_res = await client.post(
                f"{API_BASE}/documents/upload",
                headers=headers,
                data=data,
                files=files
            )

            if upload_res.status_code != 200:
                print(f"Upload failed for {item['filename']}:", upload_res.text)
                continue

            doc = upload_res.json()
            doc_id = doc["id"]
            print(f"Uploaded: {item['filename']} -> ID: {doc_id} (DRAFT)")

            # Handle Workflow Progression
            target_status = item.get("transition_to", "DRAFT")
            if target_status in ("UNDER_REVIEW", "APPROVED"):
                sub_res = await client.post(f"{API_BASE}/documents/{doc_id}/submit", headers=headers)
                print(f"  -> Submitted for review: {sub_res.status_code}")
                if target_status == "APPROVED":
                    app_res = await client.post(f"{API_BASE}/documents/{doc_id}/approve", headers=headers)
                    print(f"  -> Approved: {app_res.status_code}")

    print("\nData seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
