import hashlib
import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.postgres_models import AuditLog

GENESIS_HASH = "0" * 64

def calculate_audit_hash(timestamp_str: str, actor_id: str, action: str, document_id: str, previous_hash: str) -> str:
    raw = f"{timestamp_str}|{actor_id}|{action}|{document_id}|{previous_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

async def log_audit_event(
    db: AsyncSession,
    action: str,
    actor_id: Optional[int],
    document_id: Optional[str] = None,
    metadata_info: Optional[Dict[str, Any]] = None
) -> AuditLog:
    # 1. Fetch latest audit record to get previous_hash
    stmt = select(AuditLog).order_by(desc(AuditLog.id)).limit(1)
    result = await db.execute(stmt)
    latest_record = result.scalars().first()
    
    previous_hash = latest_record.current_hash if latest_record else GENESIS_HASH
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_str = now_utc.isoformat()
    
    actor_str = str(actor_id) if actor_id is not None else "SYSTEM"
    doc_str = str(document_id) if document_id is not None else "NONE"
    
    current_hash = calculate_audit_hash(now_str, actor_str, action, doc_str, previous_hash)
    
    audit_entry = AuditLog(
        document_id=document_id,
        actor_id=actor_id,
        action=action,
        timestamp=now_utc,
        metadata_json=metadata_info or {},
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(audit_entry)
    return audit_entry

async def verify_audit_chain(db: AsyncSession) -> Dict[str, Any]:
    stmt = select(AuditLog).order_by(AuditLog.id.asc())
    result = await db.execute(stmt)
    records = result.scalars().all()
    
    if not records:
        return {
            "total_records": 0,
            "is_valid": True,
            "verified_at": datetime.datetime.now(datetime.timezone.utc),
            "details": "Audit log is empty. Cryptographic chain intact (genesis).",
            "broken_at_id": None
        }
    
    expected_previous_hash = GENESIS_HASH
    for r in records:
        if r.previous_hash != expected_previous_hash:
            return {
                "total_records": len(records),
                "is_valid": False,
                "verified_at": datetime.datetime.now(datetime.timezone.utc),
                "details": f"Broken chain at record ID {r.id}: expected prev hash {expected_previous_hash[:12]}..., got {r.previous_hash[:12]}...",
                "broken_at_id": r.id
            }
        
        now_str = r.timestamp.isoformat()
        actor_str = str(r.actor_id) if r.actor_id is not None else "SYSTEM"
        doc_str = str(r.document_id) if r.document_id is not None else "NONE"
        computed_hash = calculate_audit_hash(now_str, actor_str, r.action, doc_str, r.previous_hash)
        
        if computed_hash != r.current_hash:
            return {
                "total_records": len(records),
                "is_valid": False,
                "verified_at": datetime.datetime.now(datetime.timezone.utc),
                "details": f"Hash mismatch at record ID {r.id}: data has been tampered with.",
                "broken_at_id": r.id
            }
        expected_previous_hash = r.current_hash
        
    return {
        "total_records": len(records),
        "is_valid": True,
        "verified_at": datetime.datetime.now(datetime.timezone.utc),
        "details": f"All {len(records)} records cryptographically verified. Hash chain unbroken.",
        "broken_at_id": None
    }
