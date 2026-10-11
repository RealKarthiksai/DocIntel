from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.postgres_models import Notification
from app.schemas.schemas import NotificationOut, NotificationListResponse
from app.security.jwt import get_current_user, CurrentUserContext

router = APIRouter(prefix="/notifications", tags=["Kafka Event Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    limit: int = 50,
    unread_only: bool = False,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves notifications tailored to the authenticated user's tenant, role, and department scope.
    """
    stmt = (
        select(Notification)
        .where(Notification.tenant_id == current_user.tenant_id)
        .order_by(desc(Notification.created_at))
    )

    if unread_only:
        stmt = stmt.where(Notification.is_read == False)

    result = await db.execute(stmt)
    all_notifs = result.scalars().all()

    # Filter according to user's department scope and role
    filtered_notifs = []
    unread_count = 0

    for n in all_notifs:
        # Department authorization check
        if not current_user.can_access_department(n.department):
            continue

        # Role filtering check
        if n.recipient_role == "MANAGER" and not current_user.is_admin and current_user.role != "MANAGER":
            continue

        filtered_notifs.append(n)
        if not n.is_read:
            unread_count += 1

    limited_notifs = filtered_notifs[:limit]

    return NotificationListResponse(
        unread_count=unread_count,
        total_count=len(filtered_notifs),
        notifications=limited_notifs
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns the total number of unread notifications for the user."""
    stmt = (
        select(Notification)
        .where(
            Notification.tenant_id == current_user.tenant_id,
            Notification.is_read == False
        )
    )
    result = await db.execute(stmt)
    unreads = result.scalars().all()

    count = 0
    for n in unreads:
        if current_user.can_access_department(n.department):
            if n.recipient_role == "MANAGER" and not current_user.is_admin and current_user.role != "MANAGER":
                continue
            count += 1

    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marks a single notification as read."""
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    notif = result.scalars().first()

    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notif.is_read = True
    await db.commit()
    return {"message": "Notification marked as read", "id": notification_id}


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marks all notifications accessible to the user as read."""
    stmt = select(Notification).where(
        Notification.tenant_id == current_user.tenant_id,
        Notification.is_read == False
    )
    result = await db.execute(stmt)
    unreads = result.scalars().all()

    updated = 0
    for n in unreads:
        if current_user.can_access_department(n.department):
            if n.recipient_role == "MANAGER" and not current_user.is_admin and current_user.role != "MANAGER":
                continue
            n.is_read = True
            updated += 1

    await db.commit()
    return {"message": f"Marked {updated} notifications as read", "updated_count": updated}
