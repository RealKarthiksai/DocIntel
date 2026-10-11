import io
import asyncio
import pytest
import pymupdf
from httpx import AsyncClient, ASGITransport
from app.main import app

def create_sample_pdf() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Workflow validation test document.")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()

@pytest.mark.asyncio
async def test_workflow_valid_transitions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Admin login
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Upload Document (State: DRAFT)
        files = {"file": ("workflow_doc.pdf", create_sample_pdf(), "application/pdf")}
        data = {"title": "State Progression Doc", "department": "general"}
        up_res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert up_res.status_code == 200
        doc_id = up_res.json()["id"]
        assert up_res.json()["status"] == "DRAFT"

        # 2. Transition: DRAFT -> UNDER_REVIEW
        sub_res = await client.post(f"/documents/{doc_id}/submit", headers=headers)
        assert sub_res.status_code == 200
        assert sub_res.json()["status"] == "UNDER_REVIEW"

        # 3. Transition: UNDER_REVIEW -> APPROVED
        app_res = await client.post(f"/documents/{doc_id}/approve", headers=headers)
        assert app_res.status_code == 200
        assert app_res.json()["status"] == "APPROVED"

        # 4. Transition: APPROVED -> ARCHIVED
        arc_res = await client.post(f"/documents/{doc_id}/archive", headers=headers)
        assert arc_res.status_code == 200
        assert arc_res.json()["status"] == "ARCHIVED"

        # 5. Verify History
        hist_res = await client.get(f"/documents/{doc_id}/history", headers=headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) == 3
        assert history[0]["from_state"] == "DRAFT" and history[0]["to_state"] == "UNDER_REVIEW"
        assert history[1]["from_state"] == "UNDER_REVIEW" and history[1]["to_state"] == "APPROVED"
        assert history[2]["from_state"] == "APPROVED" and history[2]["to_state"] == "ARCHIVED"
        await client.delete(f"/documents/{doc_id}", headers=headers)

@pytest.mark.asyncio
async def test_workflow_invalid_transition_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload Document in DRAFT status
        files = {"file": ("invalid_trans.pdf", create_sample_pdf(), "application/pdf")}
        data = {"title": "Invalid Transition Test", "department": "general"}
        up_res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        doc_id = up_res.json()["id"]

        # Attempt illegal transition: DRAFT -> APPROVED (must be rejected!)
        illegal_res = await client.post(f"/documents/{doc_id}/approve", headers=headers)
        assert illegal_res.status_code == 400
        assert "invalid transition" in illegal_res.json()["detail"].lower()
        await client.delete(f"/documents/{doc_id}", headers=headers)

@pytest.mark.asyncio
async def test_concurrent_workflow_approval_protection():
    """
    Test concurrency protection: two managers attempt to approve the same document simultaneously.
    Row locking ensures exactly one succeeds and the other receives 409 Conflict.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Admin login & upload
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        admin_token = l_res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        files = {"file": ("concurrent_doc.pdf", create_sample_pdf(), "application/pdf")}
        data = {"title": "Concurrency Protection Doc", "department": "general"}
        up_res = await client.post("/documents/upload", headers=admin_headers, data=data, files=files)
        doc_id = up_res.json()["id"]

        # Submit to UNDER_REVIEW
        await client.post(f"/documents/{doc_id}/submit", headers=admin_headers)

        # 2. Login two separate actors: Manager A and Manager B (or Admin & Manager)
        mgr_res = await client.post("/auth/login", json={"email": "manager@example.com", "password": "ManagerPass123!"})
        mgr_token = mgr_res.json()["access_token"]
        mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

        # 3. Fire concurrent approval requests simultaneously
        req1 = client.post(f"/documents/{doc_id}/approve", headers=admin_headers)
        req2 = client.post(f"/documents/{doc_id}/approve", headers=mgr_headers)

        resp1, resp2 = await asyncio.gather(req1, req2)

        status_codes = [resp1.status_code, resp2.status_code]
        # Exactly one must succeed with 200, and the other must be rejected with 409 Conflict
        assert 200 in status_codes
        assert 409 in status_codes
        
        # Verify final document status remains consistent
        check_res = await client.get(f"/documents/{doc_id}", headers=admin_headers)
        assert check_res.json()["status"] == "APPROVED"
        await client.delete(f"/documents/{doc_id}", headers=admin_headers)
