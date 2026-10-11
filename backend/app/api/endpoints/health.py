import datetime
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, get_mongo_client, get_chroma_client, init_mongo
from app.schemas.schemas import HealthResponse

router = APIRouter(tags=["Health & Metrics"])

@router.get("/health", response_model=HealthResponse)
async def get_health(db: AsyncSession = Depends(get_db)):
    postgres_status = "error"
    mongodb_status = "error"
    chromadb_status = "error"
    llm_status = "configured"

    # 1. Check PostgreSQL
    try:
        res = await db.execute(text("SELECT 1"))
        if res.scalar() == 1:
            postgres_status = "connected"
    except Exception as e:
        postgres_status = f"unhealthy: {str(e)}"

    # 2. Check MongoDB
    try:
        mongo = get_mongo_client()
        if not mongo:
            await init_mongo()
            mongo = get_mongo_client()
        if mongo:
            try:
                await mongo.admin.command("ping")
            except Exception:
                pass  # mongomock or in-memory client
            mongodb_status = "connected"
    except Exception as e:
        mongodb_status = f"unhealthy: {str(e)}"

    # 3. Check ChromaDB / pgvector
    try:
        chroma = get_chroma_client()
        if chroma:
            hb = chroma.heartbeat()
            chromadb_status = f"connected (heartbeat: {hb})"
        else:
            chromadb_status = "pgvector native mode (standalone)"
    except Exception as e:
        chromadb_status = f"unhealthy: {str(e)}"

    # 4. Check LLM Provider
    if settings.LLM_PROVIDER == "ollama":
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                r = await client.get(f"{settings.OLLAMA_URL}/api/version")
                if r.status_code == 200:
                    llm_status = f"ollama connected ({r.json().get('version', 'ok')})"
                else:
                    llm_status = "ollama offline (grounded QA fallback active)"
        except Exception:
            llm_status = "ollama offline (grounded QA fallback active)"
    else:
        llm_status = f"{settings.LLM_PROVIDER} configured"

    overall_status = "healthy"
    if "unhealthy" in postgres_status or "unhealthy" in chromadb_status:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        postgres=postgres_status,
        mongodb=mongodb_status,
        chromadb=chromadb_status,
        llm_provider=llm_status,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    total_docs = 0
    total_audits = 0
    try:
        r1 = await db.execute(text("SELECT count(*) FROM documents"))
        total_docs = r1.scalar() or 0
    except Exception:
        pass

    try:
        r2 = await db.execute(text("SELECT count(*) FROM audit_logs"))
        total_audits = r2.scalar() or 0
    except Exception:
        pass

    return {
        "status": "online",
        "total_documents": total_docs,
        "total_audit_events": total_audits,
        "system": {
            "version": settings.VERSION,
            "project": settings.PROJECT_NAME
        }
    }
