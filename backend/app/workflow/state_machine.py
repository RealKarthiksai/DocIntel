import datetime
import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres_models import Document, WorkflowHistory
from app.services.audit_service import log_audit_event

logger = logging.getLogger(__name__)

# Valid workflow transitions mapping
VALID_TRANSITIONS = {
    "DRAFT": ["UNDER_REVIEW"],
    "UNDER_REVIEW": ["APPROVED", "REJECTED"],
    "APPROVED": ["ARCHIVED"],
    "REJECTED": [],
    "ARCHIVED": []
}

async def execute_transition(
    db: AsyncSession,
    document_id: str,
    target_state: str,
    actor_id: int,
    tenant_id: str,
    comment: Optional[str] = None,
    user: Optional[Any] = None
) -> Document:
    """
    Executes a state transition with row-level concurrency protection.
    If another actor transitioned the document concurrently, raises HTTP 409 Conflict.
    """
    # 1. Row-level lock: SELECT ... FOR UPDATE ensures strict serializability
    stmt = (
        select(Document)
        .where(Document.id == document_id, Document.tenant_id == tenant_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    doc = result.scalars().first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in your tenant."
        )

    # Department & Role RBAC check
    if user is not None:
        if getattr(user, "is_viewer", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Viewers have read-only access and cannot transition documents."
            )
        if hasattr(user, "can_access_department"):
            doc_dept = getattr(doc, "department", "general")
            if not user.can_access_department(doc_dept):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. You do not have permission to transition '{doc_dept}' documents."
                )

    current_state = doc.status
    allowed_next_states = VALID_TRANSITIONS.get(current_state, [])

    # Check if target state is valid from current state
    if target_state not in allowed_next_states:
        # Check if already in target state (concurrent duplicate execution)
        if current_state == target_state:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document is already in state '{target_state}'. Concurrent operation detected."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{current_state}' to '{target_state}'. Allowed: {allowed_next_states}"
        )

    # 2. Update Document Status
    doc.status = target_state
    doc.updated_at = datetime.datetime.now(datetime.timezone.utc)

    # 3. Create Workflow History Record
    history_entry = WorkflowHistory(
        document_id=doc.id,
        from_state=current_state,
        to_state=target_state,
        actor_id=actor_id
    )
    db.add(history_entry)

    # 4. Create Audit Log Record
    action_map = {
        "UNDER_REVIEW": "SUBMITTED_FOR_REVIEW",
        "APPROVED": "APPROVED",
        "REJECTED": "REJECTED",
        "ARCHIVED": "ARCHIVED"
    }
    audit_action = action_map.get(target_state, f"TRANSITION_TO_{target_state}")

    await log_audit_event(
        db,
        action=audit_action,
        actor_id=actor_id,
        document_id=doc.id,
        metadata_info={
            "from_state": current_state,
            "to_state": target_state,
            "comment": comment or ""
        }
    )

    await db.commit()
    await db.refresh(doc)
    logger.info(f"Document {doc.id} transitioned: {current_state} -> {target_state} by user {actor_id}")

    # 5. Publish Event to Kafka / Event Bus
    try:
        from app.events.kafka_producer import publish_workflow_event
        await publish_workflow_event(
            event_type="WORKFLOW_STATE_CHANGED",
            document_id=doc.id,
            document_title=doc.title,
            department=getattr(doc, "department", "general"),
            from_status=current_state,
            to_status=target_state,
            actor_id=actor_id,
            tenant_id=tenant_id,
            comment=comment
        )
    except Exception as e:
        logger.warning(f"Notice: Failed to publish workflow event to Kafka: {e}")

    return doc
