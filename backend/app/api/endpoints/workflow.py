from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.postgres_models import Document, WorkflowHistory
from app.schemas.schemas import DocumentDetailOut, WorkflowTransitionRequest, WorkflowHistoryOut
from app.security.jwt import get_current_user, require_role, CurrentUserContext
from app.workflow.state_machine import execute_transition

router = APIRouter(prefix="/documents", tags=["Workflow Automation"])

@router.post("/{document_id}/submit")
async def submit_for_review(
    document_id: str,
    body: Optional[WorkflowTransitionRequest] = None,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    comment = body.comment if body else None
    doc = await execute_transition(
        db=db,
        document_id=document_id,
        target_state="UNDER_REVIEW",
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        comment=comment,
        user=current_user
    )
    return {"message": "Document successfully submitted for review", "status": doc.status}


@router.post("/{document_id}/approve")
async def approve_document(
    document_id: str,
    body: Optional[WorkflowTransitionRequest] = None,
    current_user: CurrentUserContext = Depends(require_role(["ADMIN", "MANAGER"])),
    db: AsyncSession = Depends(get_db)
):
    comment = body.comment if body else None
    doc = await execute_transition(
        db=db,
        document_id=document_id,
        target_state="APPROVED",
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        comment=comment,
        user=current_user
    )
    return {"message": "Document successfully approved", "status": doc.status}


@router.post("/{document_id}/reject")
async def reject_document(
    document_id: str,
    body: Optional[WorkflowTransitionRequest] = None,
    current_user: CurrentUserContext = Depends(require_role(["ADMIN", "MANAGER"])),
    db: AsyncSession = Depends(get_db)
):
    comment = body.comment if body else None
    doc = await execute_transition(
        db=db,
        document_id=document_id,
        target_state="REJECTED",
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        comment=comment,
        user=current_user
    )
    return {"message": "Document successfully rejected", "status": doc.status}


@router.post("/{document_id}/archive")
async def archive_document(
    document_id: str,
    body: Optional[WorkflowTransitionRequest] = None,
    current_user: CurrentUserContext = Depends(require_role(["ADMIN", "MANAGER"])),
    db: AsyncSession = Depends(get_db)
):
    comment = body.comment if body else None
    doc = await execute_transition(
        db=db,
        document_id=document_id,
        target_state="ARCHIVED",
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        comment=comment,
        user=current_user
    )
    return {"message": "Document successfully archived", "status": doc.status}


@router.get("/{document_id}/history", response_model=List[WorkflowHistoryOut])
async def get_workflow_history(
    document_id: str,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(WorkflowHistory)
        .join(Document, Document.id == WorkflowHistory.document_id)
        .where(WorkflowHistory.document_id == document_id, Document.tenant_id == current_user.tenant_id)
        .options(selectinload(WorkflowHistory.actor))
        .order_by(WorkflowHistory.timestamp.asc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    
    return [
        WorkflowHistoryOut(
            id=r.id,
            document_id=r.document_id,
            from_state=r.from_state,
            to_state=r.to_state,
            actor_id=r.actor_id,
            actor_email=r.actor.email if r.actor else None,
            timestamp=r.timestamp
        )
        for r in records
    ]
