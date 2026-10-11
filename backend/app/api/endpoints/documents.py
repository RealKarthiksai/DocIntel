import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_mongo_db, get_chroma_collection, save_mongo_mock_backup
from app.models.postgres_models import Document, WorkflowHistory, AuditLog
from app.schemas.schemas import DocumentOut, DocumentDetailOut
from app.security.jwt import get_current_user, CurrentUserContext
from app.services.document_service import ingest_document
from app.services.audit_service import log_audit_event
from app.workflow.state_machine import VALID_TRANSITIONS

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentDetailOut)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    department: str = Form("general"),
    classification: str = Form("internal"),
    vendor: Optional[str] = Form(""),
    tags: Optional[str] = Form("[]"),
    custom_fields: Optional[str] = Form("{}"),
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.is_viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers have read-only access and cannot upload documents."
        )

    doc_title = title or file.filename or "Untitled Document"
    content = await file.read()
    
    # Parse tags & custom_fields from JSON form fields
    try:
        parsed_tags = json.loads(tags) if tags else []
    except Exception:
        parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]
        
    try:
        parsed_custom = json.loads(custom_fields) if custom_fields else {}
    except Exception:
        parsed_custom = {}

    try:
        pg_doc, mongo_record = await ingest_document(
            filename=file.filename,
            content=content,
            title=doc_title,
            department=department,
            classification=classification,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            vendor=vendor or "",
            tags=parsed_tags,
            custom_fields=parsed_custom,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion failed: {e}")

    # Remove internal MongoDB _id before returning
    if mongo_record and "_id" in mongo_record:
        del mongo_record["_id"]

    return DocumentDetailOut(
        id=pg_doc.id,
        mongo_document_id=pg_doc.mongo_document_id,
        title=pg_doc.title,
        status=pg_doc.status,
        tenant_id=pg_doc.tenant_id,
        created_by=pg_doc.created_by,
        department=department,
        classification=classification,
        created_at=pg_doc.created_at,
        updated_at=pg_doc.updated_at,
        metadata=mongo_record,
        creator_email=current_user.email,
        workflow_history=[],
        available_actions=VALID_TRANSITIONS.get(pg_doc.status, [])
    )


@router.get("", response_model=List[DocumentOut])
async def list_documents(
    department: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Enforce Tenant Isolation
    stmt = (
        select(Document)
        .where(Document.tenant_id == current_user.tenant_id)
        .order_by(desc(Document.created_at))
    )
    if status_filter:
        stmt = stmt.where(Document.status == status_filter.upper())
        
    result = await db.execute(stmt)
    docs = result.scalars().all()
    
    mongo_db = get_mongo_db()
    output_docs = []
    
    for d in docs:
        mongo_meta = None
        if mongo_db is not None:
            mongo_meta = await mongo_db.documents.find_one({"document_id": d.id})
            
        doc_dept = getattr(d, "department", None) or (mongo_meta.get("department") if mongo_meta else None) or "general"
        doc_class = getattr(d, "classification", None) or (mongo_meta.get("classification") if mongo_meta else None) or "internal"
        
        # RBAC Check: Ensure user has permission to view this department
        if not current_user.can_access_department(doc_dept):
            continue
            
        if department and doc_dept.lower() != department.lower():
            continue

        output_docs.append(DocumentOut(
            id=d.id,
            mongo_document_id=d.mongo_document_id,
            title=d.title,
            status=d.status,
            tenant_id=d.tenant_id,
            created_by=d.created_by,
            department=doc_dept,
            classification=doc_class,
            created_at=d.created_at,
            updated_at=d.updated_at
        ))
        
    return output_docs


@router.get("/{document_id}", response_model=DocumentDetailOut)
async def get_document(
    document_id: str,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Document)
        .where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
        .options(selectinload(Document.workflow_history), selectinload(Document.creator))
    )
    result = await db.execute(stmt)
    doc = result.scalars().first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied."
        )

    # Fetch MongoDB flexible metadata
    mongo_db = get_mongo_db()
    mongo_meta = None
    if mongo_db is not None:
        mongo_meta = await mongo_db.documents.find_one({"document_id": doc.id})
        if mongo_meta and "_id" in mongo_meta:
            del mongo_meta["_id"]

    dept = getattr(doc, "department", None) or (mongo_meta.get("department") if mongo_meta else None) or "general"
    classification = getattr(doc, "classification", None) or (mongo_meta.get("classification") if mongo_meta else None) or "internal"

    # Enforce RBAC
    is_public = (classification.lower() == "public")
    has_dept_access = current_user.can_access_department(dept)
    if current_user.is_employee and classification.lower() in ["confidential", "restricted"]:
        has_dept_access = False  # Employees cannot view confidential docs by default
    if current_user.is_viewer and not is_public:
        has_dept_access = False  # Viewers can only view public docs

    # Check explicit ACL
    from app.models.postgres_models import DocumentAccessPolicy
    acl_stmt = select(DocumentAccessPolicy).where(
        DocumentAccessPolicy.document_id == document_id,
        (
            (DocumentAccessPolicy.grantee_type == "USER") & (DocumentAccessPolicy.grantee_id == str(current_user.id)) |
            (DocumentAccessPolicy.grantee_type == "ROLE") & (DocumentAccessPolicy.grantee_id == current_user.role) |
            (DocumentAccessPolicy.grantee_type == "DEPARTMENT") & (DocumentAccessPolicy.grantee_id == current_user.department)
        )
    )
    acl_res = await db.execute(acl_stmt)
    has_acl_access = acl_res.scalars().first() is not None

    if not current_user.is_admin and not is_public and not has_dept_access and not has_acl_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. You do not have permission to view '{doc.title}' ({dept}, {classification})."
        )

    history_list = [
        {
            "id": h.id,
            "from_state": h.from_state,
            "to_state": h.to_state,
            "actor_id": h.actor_id,
            "timestamp": h.timestamp.isoformat()
        }
        for h in sorted(doc.workflow_history, key=lambda x: x.timestamp)
    ]

    return DocumentDetailOut(
        id=doc.id,
        mongo_document_id=doc.mongo_document_id,
        title=doc.title,
        status=doc.status,
        tenant_id=doc.tenant_id,
        created_by=doc.created_by,
        department=dept,
        classification=classification,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        metadata=mongo_meta or {},
        creator_email=doc.creator.email if doc.creator else None,
        workflow_history=history_list,
        available_actions=VALID_TRANSITIONS.get(doc.status, [])
    )


@router.post("/{document_id}/share")
async def share_document(
    document_id: str,
    grantee_type: str = Form("USER"),  # USER, ROLE, DEPARTMENT
    grantee_id: str = Form(...),
    permission_level: str = Form("READ"),
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if not current_user.is_admin and doc.created_by != current_user.id and not current_user.has_permission("policies:manage"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. Only document owners or administrators can share documents."
        )

    from app.models.postgres_models import DocumentAccessPolicy
    policy = DocumentAccessPolicy(
        document_id=document_id,
        grantee_type=grantee_type.upper(),
        grantee_id=str(grantee_id),
        permission_level=permission_level.upper()
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    await log_audit_event(
        db,
        action="DOCUMENT_ACCESS_GRANTED",
        actor_id=current_user.id,
        document_id=document_id,
        metadata_info={"grantee_type": grantee_type, "grantee_id": grantee_id, "level": permission_level}
    )

    return {"message": "Access policy granted successfully", "policy_id": policy.id}


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    doc = result.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Authorization: Only admins or creators with delete permission can delete
    if not current_user.is_admin and not current_user.has_permission("documents:delete") and doc.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. You do not have permission to delete this document."
        )

    # 1. Delete ChromaDB vectors
    try:
        col = get_chroma_collection("document_chunks")
        if col:
            col.delete(where={"document_id": document_id})
    except Exception as e:
        pass

    # 2. Delete MongoDB metadata
    mongo_db = get_mongo_db()
    if mongo_db is not None:
        await mongo_db.documents.delete_many({"document_id": document_id})
        await save_mongo_mock_backup()

    # 3. Log cryptographic audit event
    await log_audit_event(
        db,
        action="DOCUMENT_DELETED",
        actor_id=current_user.id,
        document_id=document_id,
        metadata_info={"title": doc.title}
    )

    # 4. Delete PostgreSQL record (cascades to chunks & access_policies)
    await db.delete(doc)
    await db.commit()

    return {"message": f"Document '{document_id}' successfully deleted."}
