from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import RAGQueryRequest, RAGQueryResponse
from app.security.jwt import get_current_user, CurrentUserContext
from app.rag.engine import execute_access_aware_rag
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/rag", tags=["Access-Aware RAG"])

@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(
    req: RAGQueryRequest,
    current_user: CurrentUserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await execute_access_aware_rag(
        query=req.query,
        user=current_user,
        top_k=req.top_k,
        db=db
    )

    # Log RAG query audit event
    await log_audit_event(
        db=db,
        action="RAG_QUERY",
        actor_id=current_user.id,
        metadata_info={
            "query": req.query,
            "department_scope": current_user.permissions,
            "chunks_retrieved": result.retrieved_chunk_count,
            "sources_count": len(result.sources)
        }
    )

    return result
