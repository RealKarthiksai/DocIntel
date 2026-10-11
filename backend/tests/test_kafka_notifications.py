import io
import asyncio
import pytest
import pymupdf
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.events.kafka_consumer import start_notification_consumer
from app.core.database import init_postgres_db

@pytest.fixture(autouse=True)
async def setup_notification_service():
    await init_postgres_db()
    await start_notification_consumer()
    await asyncio.sleep(0.05)

def create_sample_pdf() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Kafka and Notification microservice verification document.")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()

@pytest.mark.asyncio
async def test_kafka_event_publication_on_upload_and_transitions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Admin
        l_res = await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        admin_token = l_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Upload Document
        files = {"file": ("kafka_test_doc.pdf", create_sample_pdf(), "application/pdf")}
        data = {"title": "Kafka Verification Doc", "department": "finance"}
        up_res = await client.post("/documents/upload", headers=headers, data=data, files=files)
        assert up_res.status_code == 200
        doc_id = up_res.json()["id"]

        # Give event consumer loop brief tick to process event
        await asyncio.sleep(0.3)

        # 3. Verify notification generated for upload
        notif_res = await client.get("/notifications", headers=headers)
        assert notif_res.status_code == 200
        notifs = notif_res.json()["notifications"]
        assert any(n["document_id"] == doc_id and n["event_type"] == "DOCUMENT_UPLOADED" for n in notifs)

        # 4. Submit for review -> Triggers WORKFLOW_STATE_CHANGED
        sub_res = await client.post(f"/documents/{doc_id}/submit", headers=headers)
        assert sub_res.status_code == 200

        await asyncio.sleep(0.3)

        # 5. Verify notification generated for review
        notif_res2 = await client.get("/notifications", headers=headers)
        notifs2 = notif_res2.json()["notifications"]
        assert any(n["document_id"] == doc_id and "Review Required" in n["title"] for n in notifs2)

        # 6. Approve document -> Triggers APPROVED notification
        app_res = await client.post(f"/documents/{doc_id}/approve", headers=headers)
        assert app_res.status_code == 200

        await asyncio.sleep(0.3)

        notif_res3 = await client.get("/notifications", headers=headers)
        notifs3 = notif_res3.json()["notifications"]
        assert any(n["document_id"] == doc_id and "Approved" in n["title"] for n in notifs3)
        await client.delete(f"/documents/{doc_id}", headers=headers)


@pytest.mark.asyncio
async def test_notifications_rbac_and_tenant_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Admin, Manager, Employee, Tenant B logins
        admin_token = (await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})).json()["access_token"]
        mgr_token = (await client.post("/auth/login", json={"email": "manager@example.com", "password": "ManagerPass123!"})).json()["access_token"]
        emp_token = (await client.post("/auth/login", json={"email": "employee@example.com", "password": "EmployeePass123!"})).json()["access_token"]
        tb_token = (await client.post("/auth/login", json={"email": "tenant_b_user@example.com", "password": "TenantBPass123!"})).json()["access_token"]

        # 1. Admin uploads a confidential legal document
        files = {"file": ("confidential_legal.pdf", create_sample_pdf(), "application/pdf")}
        data = {"title": "Restricted Legal Acquisition", "department": "legal"}
        up_res = await client.post("/documents/upload", headers={"Authorization": f"Bearer {admin_token}"}, data=data, files=files)
        assert up_res.status_code == 200
        legal_doc_id = up_res.json()["id"]

        await asyncio.sleep(0.3)

        # 2. Check notifications as Employee (General only) -> Must NOT see legal notifications!
        emp_notifs = (await client.get("/notifications", headers={"Authorization": f"Bearer {emp_token}"})).json()["notifications"]
        assert all(n["department"] == "general" for n in emp_notifs)
        assert not any(n["document_id"] == legal_doc_id for n in emp_notifs)

        # 3. Check notifications as Manager (Finance & General only) -> Must NOT see legal notifications!
        mgr_notifs = (await client.get("/notifications", headers={"Authorization": f"Bearer {mgr_token}"})).json()["notifications"]
        assert all(n["department"] in ("finance", "general") for n in mgr_notifs)
        assert not any(n["document_id"] == legal_doc_id for n in mgr_notifs)

        # 4. Check notifications as Admin -> Can see legal notifications!
        admin_notifs = (await client.get("/notifications", headers={"Authorization": f"Bearer {admin_token}"})).json()["notifications"]
        assert any(n["document_id"] == legal_doc_id for n in admin_notifs)

        # 5. Check Tenant B -> 0 notifications from tenant-default
        tb_notifs = (await client.get("/notifications", headers={"Authorization": f"Bearer {tb_token}"})).json()["notifications"]
        assert len(tb_notifs) == 0

        # Clean up
        await client.delete(f"/documents/{legal_doc_id}", headers={"Authorization": f"Bearer {admin_token}"})


@pytest.mark.asyncio
async def test_mark_notifications_as_read():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_token = (await client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})).json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Get unread count
        initial_unread = (await client.get("/notifications/unread-count", headers=headers)).json()["unread_count"]
        assert initial_unread >= 0

        # Mark all as read
        read_all_res = await client.post("/notifications/read-all", headers=headers)
        assert read_all_res.status_code == 200

        # Verify unread count is now 0
        final_unread = (await client.get("/notifications/unread-count", headers=headers)).json()["unread_count"]
        assert final_unread == 0
