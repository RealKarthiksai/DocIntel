"""
Standalone Notification Microservice
Subscribes to Kafka topic 'document.workflow.events', routes targeted notifications,
and serves notifications via HTTP REST on port 8001.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.core.database import init_postgres_db, init_mongo, get_mongo_client
from app.events.kafka_consumer import start_notification_consumer, stop_notification_consumer
from app.api.endpoints.notifications import router as notifications_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Notification-Microservice] %(name)s: %(message)s"
)
logger = logging.getLogger("notification_microservice")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Notification Microservice...")
    await init_postgres_db()
    await start_notification_consumer()
    logger.info("Notification Microservice initialized and listening to Kafka topic.")
    yield
    logger.info("Shutting down Notification Microservice...")
    await stop_notification_consumer()


app = FastAPI(
    title="Enterprise Notification Microservice",
    version="1.0.0",
    description="Event-Driven Kafka Notification Microservice for Document Intelligence Platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications_router)


@app.get("/health")
async def health():
    return {
        "service": "notification-microservice",
        "status": "healthy",
        "kafka_topic": settings.KAFKA_TOPIC_WORKFLOW_EVENTS
    }


if __name__ == "__main__":
    uvicorn.run("app.services.notification_service:app", host="0.0.0.0", port=8001, reload=True)
