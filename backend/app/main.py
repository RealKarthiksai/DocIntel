import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_postgres_db, init_mongo, get_mongo_client, get_chroma_client
from app.api.endpoints import health, auth, documents, workflow, audit, rag, notifications
from app.api.endpoints.auth import seed_default_users
from app.events.kafka_consumer import start_notification_consumer, stop_notification_consumer
from app.events.kafka_producer import stop_kafka_producer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("enterprise_doc_intelligence")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Enterprise Document Intelligence & Workflow Automation Platform...")
    try:
        await init_postgres_db()
        logger.info("PostgreSQL database initialized successfully.")
    except Exception as e:
        logger.error(f"PostgreSQL initialization failed: {e}")

    try:
        await init_mongo()
        logger.info("MongoDB initialized successfully.")
    except Exception as e:
        logger.error(f"MongoDB initialization failed: {e}")

    try:
        chroma = get_chroma_client()
        logger.info(f"ChromaDB client heartbeat: {chroma.heartbeat()}")
    except Exception as e:
        logger.warning(f"ChromaDB initialization notice: {e}")

    # Seed default users
    try:
        import app.core.database as db_module
        if db_module.AsyncSessionLocal is not None:
            async with db_module.AsyncSessionLocal() as session:
                await seed_default_users(session)
                logger.info("Default enterprise users seeded successfully.")
    except Exception as e:
        logger.warning(f"Notice during user seeding: {e}")

    # Start Kafka / Event Notification Consumer
    try:
        await start_notification_consumer()
        logger.info("Kafka/Notification consumer started.")
    except Exception as e:
        logger.warning(f"Notice during notification consumer startup: {e}")

    yield

    logger.info("Shutting down Enterprise Document Intelligence services...")
    try:
        await stop_notification_consumer()
        await stop_kafka_producer()
    except Exception as e:
        logger.warning(f"Notice during Kafka shutdown: {e}")

    try:
        mongo = get_mongo_client()
        if mongo:
            mongo.close()
            logger.info("MongoDB connection closed.")
    except Exception as e:
        logger.warning(f"Error closing MongoDB connection: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Document Intelligence & Workflow Automation Platform API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f'{request.method} {request.url.path} status={response.status_code} duration_ms={duration_ms}'
    )
    return response

# Register all Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(workflow.router)
app.include_router(audit.router)
app.include_router(rag.router)
app.include_router(notifications.router)

@app.get("/")
async def root():
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/health"
    }
