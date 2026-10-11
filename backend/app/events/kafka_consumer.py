import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.core import database
from app.models.postgres_models import Notification
from app.events.kafka_producer import get_resilient_event_queue

logger = logging.getLogger(__name__)

_consumer_running = False
_consumer_task: Optional[asyncio.Task] = None


async def handle_workflow_event(event: Dict[str, Any]):
    """
    Parses a consumed workflow event from Kafka and persists targeted notifications.
    """
    event_type = event.get("event_type", "UNKNOWN")
    doc_id = event.get("document_id", "")
    doc_title = event.get("document_title", "Document")
    department = event.get("department", "general")
    tenant_id = event.get("tenant_id", "tenant-default")
    to_status = event.get("to_status", "")
    comment = event.get("comment", "")

    # Build title and message based on event type / status
    if event_type == "DOCUMENT_UPLOADED":
        title = f"New Document: {doc_title}"
        message = f"Document '{doc_title}' ({doc_id}) was uploaded to the {department.upper()} department in DRAFT status."
        recipient_role = "ALL"
    elif event_type == "WORKFLOW_STATE_CHANGED":
        if to_status == "UNDER_REVIEW":
            title = f"Review Required: {doc_title}"
            message = f"Document '{doc_title}' ({doc_id}) has been submitted for review. Requires approval from {department.upper()} managers."
            recipient_role = "MANAGER"
        elif to_status == "APPROVED":
            title = f"Document Approved: {doc_title}"
            msg_suffix = f" Comment: {comment}" if comment else ""
            message = f"Document '{doc_title}' ({doc_id}) has been approved.{msg_suffix}"
            recipient_role = "ALL"
        elif to_status == "REJECTED":
            title = f"Document Rejected: {doc_title}"
            msg_suffix = f" Reason: {comment}" if comment else ""
            message = f"Document '{doc_title}' ({doc_id}) was rejected.{msg_suffix}"
            recipient_role = "ALL"
        elif to_status == "ARCHIVED":
            title = f"Document Archived: {doc_title}"
            message = f"Document '{doc_title}' ({doc_id}) has been moved to archival storage."
            recipient_role = "ALL"
        else:
            title = f"Workflow Update: {doc_title}"
            message = f"Document '{doc_title}' transitioned to state {to_status}."
            recipient_role = "ALL"
    else:
        title = f"Event: {event_type}"
        message = f"System event {event_type} on document {doc_id}."
        recipient_role = "ALL"

    # Persist notification in PostgreSQL
    notif_id = f"NTF-{uuid.uuid4().hex[:8].upper()}"
    try:
        if database.AsyncSessionLocal is None:
            await database.init_engine()

        async with database.AsyncSessionLocal() as session:
            notif = Notification(
                id=notif_id,
                tenant_id=tenant_id,
                recipient_role=recipient_role,
                department=department.lower(),
                document_id=doc_id,
                event_type=event_type,
                title=title,
                message=message,
                is_read=False
            )
            session.add(notif)
            await session.commit()
            logger.info(f"[Notification Worker] Saved notification {notif_id}: '{title}' for dept={department}, role={recipient_role}")
    except Exception as e:
        logger.error(f"[Notification Worker] Failed to save notification: {e}")


async def _run_kafka_consumer():
    """Consumes events from real Kafka broker if available."""
    from aiokafka import AIOKafkaConsumer

    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_WORKFLOW_EVENTS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        request_timeout_ms=3000
    )
    await consumer.start()
    logger.info(f"Apache Kafka Consumer started on topic '{settings.KAFKA_TOPIC_WORKFLOW_EVENTS}'")
    try:
        async for msg in consumer:
            if not _consumer_running:
                break
            event = msg.value
            logger.info(f"[Kafka Consumer] Consumed event {event.get('event_id')} from partition {msg.partition}")
            await handle_workflow_event(event)
    finally:
        await consumer.stop()


async def _run_resilient_event_bus_consumer():
    """Consumes events from the in-memory fallback queue."""
    queue = get_resilient_event_queue()
    logger.info("Resilient Event Bus Consumer started (listening for in-memory events)")
    while _consumer_running:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=1.0)
            logger.info(f"[EventBus Consumer] Consumed event {event.get('event_id')}: {event.get('event_type')}")
            await handle_workflow_event(event)
            queue.task_done()
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            logger.warning(f"Error in resilient event consumer loop: {e}")
            await asyncio.sleep(0.5)


async def start_notification_consumer():
    """
    Main consumer runner: attempts real Kafka first; if unreachable, runs resilient consumer.
    """
    global _consumer_running, _consumer_task
    if _consumer_running:
        return

    _consumer_running = True

    async def consumer_worker():
        # First check if Kafka is reachable with fast socket check
        if settings.KAFKA_ENABLED:
            from app.events.kafka_producer import is_kafka_broker_reachable
            reachable = await is_kafka_broker_reachable(settings.KAFKA_BOOTSTRAP_SERVERS)
            if reachable:
                try:
                    await _run_kafka_consumer()
                    return
                except Exception as e:
                    logger.info(f"Kafka consumer failed ({e}), using resilient in-memory consumer loop.")

        # Run resilient event bus consumer loop
        await _run_resilient_event_bus_consumer()

    _consumer_task = asyncio.create_task(consumer_worker())
    logger.info("Notification consumer task spawned in background.")


async def stop_notification_consumer():
    global _consumer_running, _consumer_task
    _consumer_running = False
    if _consumer_task and not _consumer_task.done():
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
    logger.info("Notification consumer stopped.")
