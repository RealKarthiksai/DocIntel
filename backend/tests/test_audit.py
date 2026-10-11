import io
import pytest
import pymupdf
from httpx import AsyncClient, ASGITransport
from app.main import app

def create_sample_pdf() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Audit testing document content.")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()

@pytest.mark.asyncio
async def test_audit_logging_and_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Admin
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload document to generate audit events
        files = {"file": ("audit_doc.pdf", create_sample_pdf(), "application/pdf")}
        data = {"title": "Audit Test Document", "department": "general"}
        up_res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert up_res.status_code == 200
        doc_id = up_res.json()["id"]

        # 3. Transition document
        await client.post(f"/documents/{doc_id}/submit", headers=headers)

        # 4. Run RAG query to trigger RAG_QUERY audit
        await client.post("/rag/query", headers=headers, json={"query": "Testing audit generation."})

        # 5. Fetch audit logs for this document
        doc_audit_res = await client.get(f"/audit/{doc_id}", headers=headers)
        assert doc_audit_res.status_code == 200
        doc_logs = doc_audit_res.json()
        assert len(doc_logs) >= 2
        actions = [l["action"] for l in doc_logs]
        assert "DOCUMENT_UPLOADED" in actions
        assert "SUBMITTED_FOR_REVIEW" in actions

        # 6. Verify cryptographic chain
        verify_res = await client.get("/audit/verify", headers=headers)
        assert verify_res.status_code == 200
        v_data = verify_res.json()
        assert v_data["is_valid"] is True
        assert v_data["broken_at_id"] is None
        assert v_data["total_records"] > 0
        await client.delete(f"/documents/{doc_id}", headers=headers)
