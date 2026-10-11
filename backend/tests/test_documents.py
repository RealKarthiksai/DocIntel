import io
import json
import pytest
import pymupdf
import docx
from httpx import AsyncClient, ASGITransport
from app.main import app

def create_dummy_pdf(text: str = "Test PDF Document Content") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()

def create_dummy_docx(text: str = "Test DOCX Document Content") -> bytes:
    doc = docx.Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

@pytest.mark.asyncio
async def test_upload_valid_pdf_and_metadata():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as Admin
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        pdf_bytes = create_dummy_pdf("Company Vendor Agreement for technical services.")
        files = {"file": ("agreement.pdf", pdf_bytes, "application/pdf")}
        data = {
            "title": "Vendor Testing Agreement",
            "department": "legal",
            "classification": "internal",
            "vendor": "Alpha Tech",
            "tags": json.dumps(["testing", "pdf"]),
            "custom_fields": json.dumps({"audit_interval": "6 months", "level": 3})
        }

        res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert res.status_code == 200
        doc = res.json()
        assert doc["id"].startswith("DOC-")
        assert doc["status"] == "DRAFT"
        assert doc["department"] == "legal"
        assert doc["metadata"]["custom_fields"]["audit_interval"] == "6 months"
        await client.delete(f"/documents/{doc['id']}", headers=headers)

@pytest.mark.asyncio
async def test_upload_valid_docx():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        docx_bytes = create_dummy_docx("Standard Employee Onboarding Guidelines.")
        files = {"file": ("guidelines.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {
            "title": "Onboarding Guidelines",
            "department": "general",
            "classification": "internal"
        }

        res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert res.status_code == 200
        doc = res.json()
        assert doc["id"].startswith("DOC-")
        assert doc["department"] == "general"
        await client.delete(f"/documents/{doc['id']}", headers=headers)

@pytest.mark.asyncio
async def test_reject_empty_document():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        files = {"file": ("empty.pdf", b"", "application/pdf")}
        data = {"title": "Empty Document", "department": "general"}

        res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert res.status_code == 400
        assert "empty" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_reject_invalid_mime_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        files = {"file": ("script.exe", b"binarycontent", "application/x-msdownload")}
        data = {"title": "Malicious Executable", "department": "general"}

        res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert res.status_code == 400
        assert "invalid file type" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_rbac_department_filtering():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Employee has only 'general' department permissions
        e_res = await client.post("/auth/login", json={"email": "employee@example.com", "password": "EmployeePass123!"})
        e_token = e_res.json()["access_token"]

        res = await client.get("/documents", headers={"Authorization": f"Bearer {e_token}"})
        assert res.status_code == 200
        docs = res.json()
        # All visible documents must be in 'general' department
        for d in docs:
            assert d["department"].lower() == "general"
