from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.postgres_models import AuditLog, Document
from app.schemas.schemas import AuditLogOut, AuditVerifyResponse
from app.security.jwt import get_current_user, require_role, CurrentUserContext
from app.services.audit_service import verify_audit_chain

router = APIRouter(prefix="/audit", tags=["Audit Trail & Verification"])

@router.get("/verify", response_model=AuditVerifyResponse)
async def verify_chain(
    current_user: CurrentUserContext = Depends(require_role(["ADMIN", "MANAGER"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifies the entire cryptographic SHA-256 hash chain from genesis to head.
    Detects any database tampering, altered timestamps, or forged actor operations.
    """
    result = await verify_audit_chain(db)
    return AuditVerifyResponse(**result)


@router.get("", response_model=List[AuditLogOut])
async def get_audit_logs(
    limit: int = 50,
    current_user: CurrentUserContext = Depends(require_role(["ADMIN", "MANAGER"])),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AuditLog)
        .options(selectinload(AuditLog.actor))
        .order_by(desc(AuditLog.id))
        .limit(limit)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        AuditLogOut(
            id=l.id,
            document_id=l.document_id,
            actor_id=l.actor_id,
            actor_email=l.actor.email if l.actor else "SYSTEM",
            action=l.action,
            timestamp=l.timestamp,
            metadata=l.metadata_json or {},
            previous_hash=l.previous_hash,
            current_hash=l.current_hash
        )
        for l in logs
    ]


@router.get("/{document_id}", response_model=List[AuditLogOut])
async def get_document_audit_logs(
    document_id: str,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify tenant ownership of document
    doc_stmt = select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    doc_res = await db.execute(doc_stmt)
    if not doc_res.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    stmt = (
        select(AuditLog)
        .where(AuditLog.document_id == document_id)
        .options(selectinload(AuditLog.actor))
        .order_by(AuditLog.id.asc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        AuditLogOut(
            id=l.id,
            document_id=l.document_id,
            actor_id=l.actor_id,
            actor_email=l.actor.email if l.actor else "SYSTEM",
            action=l.action,
            timestamp=l.timestamp,
            metadata=l.metadata_json or {},
            previous_hash=l.previous_hash,
            current_hash=l.current_hash
        )
        for l in logs
    ]
