import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory resilient async event queue fallback (shared if Kafka broker is unavailable)
_resilient_event_queue: asyncio.Queue = asyncio.Queue()

# Global Kafka Producer instance
_kafka_producer = None
_kafka_available = None  # None: not checked yet; True: connected; False: fallback mode


async def is_kafka_broker_reachable(bootstrap_servers: str, timeout: float = 0.2) -> bool:
    """Fast non-blocking TCP socket check to determine if Kafka is active."""
    try:
        server = bootstrap_servers.split(",")[0].strip()
        if ":" in server:
            host, port_str = server.split(":", 1)
            port = int(port_str)
        else:
            host, port = server, 9092
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def get_kafka_producer():
    """Initializes and returns the AIOKafkaProducer if broker is reachable."""
    global _kafka_producer, _kafka_available

    if _kafka_available is False:
        return None

    if _kafka_producer is not None:
        return _kafka_producer

    if not settings.KAFKA_ENABLED:
        _kafka_available = False
        logger.info("Kafka disabled via configuration. Using resilient in-memory event bus.")
        return None

    # Fast TCP probe first to avoid hanging or noisy connection errors
    reachable = await is_kafka_broker_reachable(settings.KAFKA_BOOTSTRAP_SERVERS)
    if not reachable:
        _kafka_available = False
        logger.info(f"Kafka broker at {settings.KAFKA_BOOTSTRAP_SERVERS} not reachable. Using resilient event bus.")
        return None

    try:
        from aiokafka import AIOKafkaProducer

        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=2000,
            retry_backoff_ms=500
        )
        await asyncio.wait_for(producer.start(), timeout=2.0)
        _kafka_producer = producer
        _kafka_available = True
        logger.info(f"Connected to Apache Kafka broker at {settings.KAFKA_BOOTSTRAP_SERVERS}")
        return _kafka_producer
    except Exception as e:
        logger.info(f"Kafka producer start failed ({e}). Using resilient event bus fallback.")
        _kafka_available = False
        _kafka_producer = None
        return None


async def stop_kafka_producer():
    global _kafka_producer, _kafka_available
    if _kafka_producer is not None:
        try:
            await _kafka_producer.stop()
            logger.info("Kafka producer stopped successfully.")
        except Exception as e:
            logger.warning(f"Error stopping Kafka producer: {e}")
        finally:
            _kafka_producer = None
            _kafka_available = None


async def publish_workflow_event(
    event_type: str,
    document_id: str,
    document_title: str,
    department: str,
    from_status: Optional[str],
    to_status: str,
    actor_id: int,
    tenant_id: str,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs and publishes a structured workflow event to Kafka topic or resilient bus.
    """
    event_payload = {
        "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
        "event_type": event_type,
        "document_id": document_id,
        "document_title": document_title,
        "department": department.lower(),
        "from_status": from_status,
        "to_status": to_status,
        "actor_id": actor_id,
        "tenant_id": tenant_id,
        "comment": comment or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": settings.KAFKA_TOPIC_WORKFLOW_EVENTS
    }

    producer = await get_kafka_producer()
    if producer and _kafka_available:
        try:
            await producer.send_and_wait(settings.KAFKA_TOPIC_WORKFLOW_EVENTS, event_payload)
            logger.info(f"[Kafka Producer] Published event {event_payload['event_id']} to topic '{settings.KAFKA_TOPIC_WORKFLOW_EVENTS}'")
            return event_payload
        except Exception as e:
            logger.warning(f"Failed to publish to Kafka ({e}), falling back to in-memory event bus.")

    # Resilient fallback: publish to in-memory queue
    await _resilient_event_queue.put(event_payload)
    logger.info(f"[EventBus Producer] Enqueued event {event_payload['event_id']} to resilient event queue ({event_type})")
    return event_payload


def get_resilient_event_queue() -> asyncio.Queue:
    return _resilient_event_queue
