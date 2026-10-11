import asyncio
import httpx
import json

API_BASE = "http://localhost:8000"

USERS = [
    {"email": "admin@example.com", "password": "AdminPass123!", "expected_role": "ADMIN", "expected_scope": ["*"]},
    {"email": "manager@example.com", "password": "ManagerPass123!", "expected_role": "MANAGER", "expected_scope": ["finance", "general"]},
    {"email": "employee@example.com", "password": "EmployeePass123!", "expected_role": "EMPLOYEE", "expected_scope": ["general"]},
    {"email": "tenant_b_user@example.com", "password": "TenantBPass123!", "expected_role": "EMPLOYEE", "expected_scope": ["general"]}
]

async def run_verification():
    print("==================================================================")
    print(" SYSTEM-WIDE ZERO-TRUST VERIFICATION: ROLES, TEST DATA & PIPELINES")
    print("==================================================================")

    tokens = {}
    async with httpx.AsyncClient(timeout=20.0) as client:
        # ----------------------------------------------------
        # 1. VERIFY USER ACCOUNTS & JWT CLAIMS
        # ----------------------------------------------------
        print("\n[Step 1] Verifying User Authentication & Claims...")
        for u in USERS:
            res = await client.post(f"{API_BASE}/auth/login", json={"email": u["email"], "password": u["password"]})
            assert res.status_code == 200, f"Failed login for {u['email']}: {res.text}"
            data = res.json()
            tokens[u["email"]] = data["access_token"]
            print(f"  ✓ {u['email']:<25}: Role={data['role']:<9} Tenant={data['tenant_id']:<15} Permissions={data['permissions']}")
            assert data["role"] == u["expected_role"]
            assert data["permissions"] == u["expected_scope"]

        # ----------------------------------------------------
        # 2. VERIFY DOCUMENT VISIBILITY PER ROLE (RBAC & TENANT)
        # ----------------------------------------------------
        print("\n[Step 2] Verifying Document Visibility per Role (RBAC & Tenant Isolation)...")
        # Admin: All 5 documents in tenant-default
        admin_docs = (await client.get(f"{API_BASE}/documents", headers={"Authorization": f"Bearer {tokens['admin@example.com']}"})).json()
        print(f"  ✓ Admin sees {len(admin_docs)} documents:")
        for d in admin_docs:
            print(f"      • [{d['id']}] {d['title']} ({d['department']}) -> Status: {d['status']}")
        assert len(admin_docs) == 5, f"Admin should see 5 documents, got {len(admin_docs)}"

        # Manager: Finance + General only (Must see 3 documents, 0 legal)
        mgr_docs = (await client.get(f"{API_BASE}/documents", headers={"Authorization": f"Bearer {tokens['manager@example.com']}"})).json()
        mgr_depts = set(d["department"] for d in mgr_docs)
        print(f"  ✓ Manager sees {len(mgr_docs)} documents (Departments: {mgr_depts})")
        assert len(mgr_docs) == 3, f"Manager should see 3 documents, got {len(mgr_docs)}"
        assert "legal" not in mgr_depts, f"Manager must not see legal documents, found: {mgr_depts}"

        # Employee: General only (Must see 2 documents, 0 finance, 0 legal)
        emp_docs = (await client.get(f"{API_BASE}/documents", headers={"Authorization": f"Bearer {tokens['employee@example.com']}"})).json()
        emp_depts = set(d["department"] for d in emp_docs)
        print(f"  ✓ Employee sees {len(emp_docs)} documents (Departments: {emp_depts})")
        assert len(emp_docs) == 2, f"Employee should see 2 documents, got {len(emp_docs)}"
        assert all(d["department"] == "general" for d in emp_docs), f"Employee must only see general, found: {emp_depts}"

        # Tenant B: Must see 0 documents from tenant-default
        tb_docs = (await client.get(f"{API_BASE}/documents", headers={"Authorization": f"Bearer {tokens['tenant_b_user@example.com']}"})).json()
        print(f"  ✓ Tenant B user sees {len(tb_docs)} documents (Cross-tenant isolation enforced)")
        assert len(tb_docs) == 0, f"Tenant B must see 0 tenant-default documents, got {len(tb_docs)}"

        # ----------------------------------------------------
        # 3. VERIFY WORKFLOW PERMISSIONS & DEPARTMENT RESTRICTIONS
        # ----------------------------------------------------
        print("\n[Step 3] Verifying Workflow Permission & Department Enforcement...")
        legal_review_doc = next(d for d in admin_docs if d["department"] == "legal" and d["status"] == "UNDER_REVIEW")
        finance_review_doc = next(d for d in admin_docs if d["department"] == "finance" and d["status"] == "UNDER_REVIEW")

        # 3a. Employee tries to approve legal doc -> 403 Forbidden
        emp_app_legal = await client.post(
            f"{API_BASE}/documents/{legal_review_doc['id']}/approve",
            headers={"Authorization": f"Bearer {tokens['employee@example.com']}"}
        )
        print(f"  ✓ Employee approval attempt on Legal doc: HTTP {emp_app_legal.status_code} (Expected 403 Forbidden)")
        assert emp_app_legal.status_code == 403

        # 3b. Manager tries to approve legal doc -> 403 Forbidden (no legal permission)
        mgr_app_legal = await client.post(
            f"{API_BASE}/documents/{legal_review_doc['id']}/approve",
            headers={"Authorization": f"Bearer {tokens['manager@example.com']}"}
        )
        print(f"  ✓ Manager approval attempt on Legal doc: HTTP {mgr_app_legal.status_code} (Expected 403 Forbidden)")
        assert mgr_app_legal.status_code == 403

        # 3c. Employee tries to approve finance doc -> 403 Forbidden
        emp_app_fin = await client.post(
            f"{API_BASE}/documents/{finance_review_doc['id']}/approve",
            headers={"Authorization": f"Bearer {tokens['employee@example.com']}"}
        )
        print(f"  ✓ Employee approval attempt on Finance doc: HTTP {emp_app_fin.status_code} (Expected 403 Forbidden)")
        assert emp_app_fin.status_code == 403

        # 3d. Manager approves finance doc -> 200 OK (authorized)
        mgr_app_fin = await client.post(
            f"{API_BASE}/documents/{finance_review_doc['id']}/approve",
            headers={"Authorization": f"Bearer {tokens['manager@example.com']}"},
            json={"comment": "Approved by Finance Manager"}
        )
        print(f"  ✓ Manager approval on Finance doc: HTTP {mgr_app_fin.status_code} (Expected 200 OK, Status: {mgr_app_fin.json().get('status')})")
        assert mgr_app_fin.status_code == 200

        # ----------------------------------------------------
        # 4. VERIFY ACCESS-AWARE RAG RETRIEVAL PER ROLE
        # ----------------------------------------------------
        print("\n[Step 4] Verifying Access-Aware RAG Engine (Zero Leakage Across Roles & Tenants)...")
        
        # Test Case A: Legal Executive Contract (Confidential)
        legal_query = "What are the termination conditions in the executive contract?"
        print(f"\n  Query A (Confidential Legal): '{legal_query}'")
        
        emp_rag_a = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['employee@example.com']}"}, json={"query": legal_query})).json()
        print(f"    • Employee : '{emp_rag_a['answer']}' (Sources: {len(emp_rag_a['sources'])})")
        assert emp_rag_a["answer"] == "No authorized information was found for this question."
        assert len(emp_rag_a["sources"]) == 0

        mgr_rag_a = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['manager@example.com']}"}, json={"query": legal_query})).json()
        print(f"    • Manager  : '{mgr_rag_a['answer']}' (Sources: {len(mgr_rag_a['sources'])})")
        assert mgr_rag_a["answer"] == "No authorized information was found for this question."
        assert len(mgr_rag_a["sources"]) == 0

        adm_rag_a = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['admin@example.com']}"}, json={"query": legal_query})).json()
        print(f"    • Admin    : '{adm_rag_a['answer'][:110]}...' (Sources: {len(adm_rag_a['sources'])})")
        assert len(adm_rag_a["sources"]) > 0
        assert any("executive" in s["document_title"].lower() for s in adm_rag_a["sources"])

        # Test Case B: Finance Invoice ($148,500.00)
        fin_query = "What is the total amount due in the cloud infrastructure invoice?"
        print(f"\n  Query B (Finance): '{fin_query}'")
        
        emp_rag_b = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['employee@example.com']}"}, json={"query": fin_query})).json()
        print(f"    • Employee : '{emp_rag_b['answer']}' (Sources: {len(emp_rag_b['sources'])})")
        assert emp_rag_b["answer"] == "No authorized information was found for this question."
        assert len(emp_rag_b["sources"]) == 0

        mgr_rag_b = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['manager@example.com']}"}, json={"query": fin_query})).json()
        print(f"    • Manager  : '{mgr_rag_b['answer'][:110]}...' (Sources: {len(mgr_rag_b['sources'])})")
        assert len(mgr_rag_b["sources"]) > 0
        assert "$148,500" in mgr_rag_b["answer"] or "cloudscale" in mgr_rag_b["answer"].lower()

        adm_rag_b = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['admin@example.com']}"}, json={"query": fin_query})).json()
        print(f"    • Admin    : '{adm_rag_b['answer'][:110]}...' (Sources: {len(adm_rag_b['sources'])})")
        assert len(adm_rag_b["sources"]) > 0

        # Test Case C: General Employee Policy (All tenant users can access)
        gen_query = "What is the policy for paid time off and remote work?"
        print(f"\n  Query C (General Policy): '{gen_query}'")
        
        emp_rag_c = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['employee@example.com']}"}, json={"query": gen_query})).json()
        print(f"    • Employee : '{emp_rag_c['answer'][:110]}...' (Sources: {len(emp_rag_c['sources'])})")
        assert len(emp_rag_c["sources"]) > 0

        # Test Case D: Cross-tenant isolation in RAG
        print(f"\n  Query D (Cross-Tenant): '{gen_query}' from Tenant B User")
        tb_rag = (await client.post(f"{API_BASE}/rag/query", headers={"Authorization": f"Bearer {tokens['tenant_b_user@example.com']}"}, json={"query": gen_query})).json()
        print(f"    • Tenant B : '{tb_rag['answer']}' (Sources: {len(tb_rag['sources'])})")
        assert tb_rag["answer"] == "No authorized information was found for this question."
        assert len(tb_rag["sources"]) == 0

        # ----------------------------------------------------
        # 5. VERIFY CRYPTOGRAPHIC AUDIT CHAIN
        # ----------------------------------------------------
        print("\n[Step 5] Verifying SHA-256 Cryptographic Audit Chain...")
        audit_res = (await client.get(
            f"{API_BASE}/audit/verify",
            headers={"Authorization": f"Bearer {tokens['admin@example.com']}"}
        )).json()
        print(f"  ✓ Cryptographic Chain Integrity: {audit_res['is_valid']}")
        print(f"  ✓ Total Blocks Verified: {audit_res['total_records']}")
        print(f"  ✓ Verification Details: {audit_res['details']}")
        assert audit_res["is_valid"] is True
        assert audit_res["total_records"] > 0

        # ----------------------------------------------------
        # 6. VERIFY KAFKA EVENT NOTIFICATIONS & RBAC SCOPE
        # ----------------------------------------------------
        print("\n[Step 6] Verifying Kafka Notifications & Microservice Delivery...")
        # Admin notifications
        adm_notif = (await client.get(f"{API_BASE}/notifications", headers={"Authorization": f"Bearer {tokens['admin@example.com']}"})).json()
        print(f"  ✓ Admin received {adm_notif['total_count']} notifications across all departments")
        assert adm_notif["total_count"] > 0

        # Manager notifications (finance & general only)
        mgr_notif = (await client.get(f"{API_BASE}/notifications", headers={"Authorization": f"Bearer {tokens['manager@example.com']}"})).json()
        mgr_notif_depts = set(n["department"] for n in mgr_notif["notifications"])
        print(f"  ✓ Manager received {mgr_notif['total_count']} notifications (Departments: {mgr_notif_depts})")
        assert "legal" not in mgr_notif_depts, f"Manager should never receive legal notifications, got {mgr_notif_depts}"

        # Employee notifications (general only)
        emp_notif = (await client.get(f"{API_BASE}/notifications", headers={"Authorization": f"Bearer {tokens['employee@example.com']}"})).json()
        emp_notif_depts = set(n["department"] for n in emp_notif["notifications"])
        print(f"  ✓ Employee received {emp_notif['total_count']} notifications (Departments: {emp_notif_depts})")
        assert all(d == "general" for d in emp_notif_depts)

        # Tenant B isolation
        tb_notif = (await client.get(f"{API_BASE}/notifications", headers={"Authorization": f"Bearer {tokens['tenant_b_user@example.com']}"})).json()
        print(f"  ✓ Tenant B received {tb_notif['total_count']} notifications (Cross-tenant isolation enforced)")
        assert tb_notif["total_count"] == 0

        # Mark all read
        mark_res = (await client.post(f"{API_BASE}/notifications/read-all", headers={"Authorization": f"Bearer {tokens['admin@example.com']}"})).json()
        print(f"  ✓ Admin mark-all-read action: {mark_res['message']}")
        unread_cnt = (await client.get(f"{API_BASE}/notifications/unread-count", headers={"Authorization": f"Bearer {tokens['admin@example.com']}"})).json()["unread_count"]
        print(f"  ✓ Admin unread count after marking read: {unread_cnt}")
        assert unread_cnt == 0

    print("\n==================================================================")
    print(" ALL SYSTEM VERIFICATIONS PASSED: 100% CORRECT & ROBUST")
    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
