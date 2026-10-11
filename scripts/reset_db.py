import asyncio
import os
import shutil
import pathlib
import httpx
from sqlalchemy import text
from app.core import database
from app.models.postgres_models import Base, Role
from app.core.config import settings

async def reset_db():
    print("Resetting PostgreSQL tables, MongoDB collections, and ChromaDB...")
    await database.init_engine()
    
    # 1. Clear PostgreSQL documents, workflow_history, audit_logs
    async with database.AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE workflow_history, audit_logs, documents CASCADE;"))
        await session.commit()
    print("  ✓ PostgreSQL tables truncated.")

    # 2. Clear MongoDB
    mongo = await database.init_mongo()
    if mongo is not None:
        await mongo.documents.delete_many({})
        if database.MONGO_BACKUP_FILE.exists():
            database.MONGO_BACKUP_FILE.unlink()
        print("  ✓ MongoDB documents collection wiped.")

    # 3. Clear ChromaDB
    try:
        chroma = database.get_chroma_client()
        try:
            chroma.delete_collection("document_chunks")
        except Exception:
            pass
        database.get_chroma_collection("document_chunks")
        print("  ✓ ChromaDB document_chunks collection recreated.")
    except Exception as e:
        print(f"  Chroma notice: {e}")

    print("Reset complete!")

if __name__ == "__main__":
    asyncio.run(reset_db())
