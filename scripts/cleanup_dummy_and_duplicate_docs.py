#!/usr/bin/env python3
"""
Prunes dummy test stubs and duplicate documents from the platform.
Leaves only the clean, fully-documented, role-aware enterprise documents.
"""

import sys
import json
import httpx
from collections import defaultdict

API_BASE = "http://localhost:8000"

DUMMY_TITLES_TO_PURGE = {
    "Audit Test Document",
    "Concurrency Protection Doc",
    "Invalid Transition Test",
    "State Progression Doc",
    "Kafka Verification Doc",
    "Restricted Legal Acquisition",
    "Vendor Testing Agreement",
    "Onboarding Guidelines",
    "Button Test Financial Audit Memo"
}

# Protected IDs that specific tests check for
PROTECTED_DOC_IDS = {"DOC-8C199448"}


def main():
    print("======================================================================")
    print("  Enterprise Document Intelligence - Repository & DB Pruning Tool")
    print("======================================================================\n")

    with httpx.Client(base_url=API_BASE, timeout=30.0) as client:
        # 1. Admin Login
        login_res = client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
        if login_res.status_code != 200:
            print("[-] Admin login failed:", login_res.text)
            sys.exit(1)

        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[+] Logged in as admin@example.com")

        # 2. Fetch all existing documents
        docs_res = client.get("/documents", headers=headers)
        if docs_res.status_code != 200:
            print("[-] Failed to list documents:", docs_res.text)
            sys.exit(1)

        all_docs = docs_res.json()
        print(f"[*] Found {len(all_docs)} total documents in PostgreSQL before pruning.\n")

        # 3. Classify documents to delete vs keep
        docs_to_delete = []
        docs_to_keep = []

        by_title = defaultdict(list)
        for doc in all_docs:
            by_title[doc["title"]].append(doc)

        for title, doc_list in by_title.items():
            # If it's a dummy test stub, delete ALL copies
            if title in DUMMY_TITLES_TO_PURGE:
                for doc in doc_list:
                    docs_to_delete.append((doc["id"], title, "DUMMY_TEST_STUB"))
            else:
                # Legitimate title: Keep only 1 clean copy (prefer protected ID or highest ID)
                # Sort to ensure protected ID is first if present
                doc_list.sort(key=lambda d: (d["id"] in PROTECTED_DOC_IDS, d["created_at"]), reverse=True)
                primary_doc = doc_list[0]
                docs_to_keep.append(primary_doc)

                # Mark any duplicates for deletion
                for dup in doc_list[1:]:
                    docs_to_delete.append((dup["id"], title, "DUPLICATE_SEED"))

        print(f"[*] Identified {len(docs_to_delete)} documents to prune:")
        print(f"    - Dummy test stubs: {sum(1 for d in docs_to_delete if d[2] == 'DUMMY_TEST_STUB')}")
        print(f"    - Duplicate copies: {sum(1 for d in docs_to_delete if d[2] == 'DUPLICATE_SEED')}")
        print(f"[*] Target clean documents to retain: {len(docs_to_keep)}\n")

        # 4. Perform Cascade Deletion via REST API
        print("[*] Commencing cascade deletion across PostgreSQL, MongoDB, and ChromaDB...")
        deleted_count = 0
        error_count = 0

        for doc_id, doc_title, reason in docs_to_delete:
            del_res = client.delete(f"/documents/{doc_id}", headers=headers)
            if del_res.status_code == 200:
                deleted_count += 1
                # print snippet occasionally
                if deleted_count % 10 == 0 or deleted_count == len(docs_to_delete):
                    print(f"  [DELETED {deleted_count}/{len(docs_to_delete)}] {doc_id} ('{doc_title[:35]}...')")
            else:
                error_count += 1
                print(f"  [ERROR] Could not delete {doc_id}: {del_res.status_code} - {del_res.text}")

        print(f"\n[+] Successfully purged {deleted_count} documents (Errors: {error_count}).\n")

        # 5. Fetch updated documents list
        verify_res = client.get("/documents", headers=headers)
        final_docs = verify_res.json()
        print(f"======================================================================")
        print(f"  FINAL CLEAN DOCUMENT REPOSITORY ({len(final_docs)} Documents Retained)")
        print(f"======================================================================")
        print(f"{'ID':<14} | {'Department':<12} | {'Class':<12} | {'Status':<12} | {'Title'}")
        print("-" * 80)
        for d in sorted(final_docs, key=lambda x: (x['department'], x['title'])):
            print(f"{d['id']:<14} | {d['department']:<12} | {d['classification']:<12} | {d['status']:<12} | {d['title']}")
        print("=" * 80)


if __name__ == "__main__":
    main()
