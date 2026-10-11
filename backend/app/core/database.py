import os
import pathlib
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from motor.motor_asyncio import AsyncIOMotorClient
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.models.postgres_models import Base, Role

logger = logging.getLogger(__name__)

# Ensure data directories exist
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chromadb"
PG_DATA_DIR = DATA_DIR / "embedded_pg"
UPLOAD_DIR = DATA_DIR / "uploads"

CHROMA_DIR.mkdir(parents=True, exist_ok=True)
PG_DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# Embedded Postgres Server Manager
# -------------------------------------------------------------
_embedded_pg_server = None

def get_or_start_embedded_pg():
    global _embedded_pg_server
    if _embedded_pg_server is not None:
        return _embedded_pg_server
    try:
        from embedded_postgres import PostgresServer
        server = PostgresServer(pgdata=PG_DATA_DIR, cleanup_mode=None)
        server.ensure_postgres_running()
        _embedded_pg_server = server
        logger.info(f"Embedded PostgreSQL running with URI: {server.get_uri()}")
        # Ensure doc_intelligence database exists
        try:
            server.psql("CREATE DATABASE doc_intelligence;")
        except Exception:
            pass  # Already exists
        return _embedded_pg_server
    except Exception as e:
        logger.warning(f"Could not start embedded PostgreSQL: {e}")
        return None


# -------------------------------------------------------------
# PostgreSQL Database Engine & Session
# -------------------------------------------------------------
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = None
AsyncSessionLocal = None

async def init_engine():
    global engine, AsyncSessionLocal, db_url
    if engine is not None:
        return engine

    # First attempt: Try configured DATABASE_URL
    try:
        test_engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        engine = test_engine
        logger.info(f"Connected to PostgreSQL at {db_url}")
    except Exception as e:
        logger.info(f"Configured PostgreSQL not reachable ({e}). Trying embedded PostgreSQL...")
        server = get_or_start_embedded_pg()
        if server:
            # Embedded postgres uses unix socket
            sock_dir = str(PG_DATA_DIR)
            embedded_url = f"postgresql+asyncpg://postgres:@/doc_intelligence?host={sock_dir}"
            try:
                test_engine = create_async_engine(embedded_url, echo=False, pool_pre_ping=True)
                async with test_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                engine = test_engine
                db_url = embedded_url
                logger.info(f"Successfully connected to Embedded PostgreSQL via socket: {sock_dir}")
            except Exception as e2:
                logger.warning(f"Failed to connect to embedded postgres: {e2}")

        if engine is None:
            # Fallback to SQLite with WAL mode
            logger.warning("Using SQLite fallback for relational storage.")
            sqlite_path = DATA_DIR / "doc_intelligence.db"
            sqlite_url = f"sqlite+aiosqlite:///{sqlite_path}"
            engine = create_async_engine(sqlite_url, echo=False)
            db_url = sqlite_url

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    return engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_engine()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_postgres_db():
    """Initializes tables, pgvector extension, HNSW indexes, and seeds default roles/departments/permissions."""
    await init_engine()
    
    # 1. Ensure vector extension and create all tables
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception as e:
            logger.warning(f"Notice enabling vector extension: {e}")
            
        await conn.run_sync(Base.metadata.create_all)
        
        # Create HNSW vector index on document_chunks.embedding
        try:
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw "
                "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
            ))
        except Exception as e:
            logger.warning(f"Notice creating HNSW index: {e}")

    # 2. Seed departments, permissions, and roles
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from app.models.postgres_models import Department, Permission, RolePermission
        
        # Seed default departments
        default_depts = [
            ("general", "General organization-wide policies and public info"),
            ("finance", "Corporate finance, payroll, and invoices"),
            ("engineering", "Software architecture, infrastructure, and technical guides"),
            ("hr", "Human resources, executive compensation, and personnel"),
            ("legal", "Contracts, master services agreements, and compliance"),
        ]
        for dept_name, desc in default_depts:
            res = await session.execute(select(Department).where(Department.name == dept_name))
            if not res.scalars().first():
                session.add(Department(name=dept_name, description=desc))
        await session.flush()
        
        # Seed default permissions
        all_perms = [
            ("documents:read", "Read document metadata and content"),
            ("documents:write", "Upload and edit draft documents"),
            ("documents:delete", "Delete documents from system"),
            ("documents:approve", "Approve or reject documents in workflow"),
            ("rag:query", "Execute RAG semantic retrieval queries"),
            ("audit:read", "Inspect audit logs and cryptographic chains"),
            ("users:manage", "Manage system users and role assignments"),
            ("policies:manage", "Manage document access control policies (ACLs)"),
        ]
        perm_objs = {}
        for p_name, p_desc in all_perms:
            res = await session.execute(select(Permission).where(Permission.name == p_name))
            p = res.scalars().first()
            if not p:
                p = Permission(name=p_name, description=p_desc)
                session.add(p)
                await session.flush()
            perm_objs[p_name] = p
            
        # Seed 5 roles and link role_permissions
        for role_name, perms in settings.ROLE_PERMISSIONS.items():
            res = await session.execute(select(Role).where(Role.name == role_name))
            role = res.scalars().first()
            if not role:
                role = Role(name=role_name, permissions=perms, description=f"{role_name} system role")
                session.add(role)
                await session.flush()
            else:
                role.permissions = perms
            
            # Populate role_permissions join table
            target_perms = all_perms if "*" in perms else [(p, "") for p in perms]
            for p_tuple in target_perms:
                perm_key = p_tuple[0] if isinstance(p_tuple, tuple) else p_tuple
                if perm_key in perm_objs:
                    perm = perm_objs[perm_key]
                    rp_res = await session.execute(
                        select(RolePermission).where(
                            RolePermission.role_id == role.id,
                            RolePermission.permission_id == perm.id
                        )
                    )
                    if not rp_res.scalars().first():
                        session.add(RolePermission(role_id=role.id, permission_id=perm.id))
                        
        await session.commit()
    logger.info("Relational database initialized, pgvector HNSW index ready, and 5 RBAC roles verified.")


async def reset_dev_database(force: bool = False):
    """
    Safely resets only the local development database doc_intelligence.
    Drops all public tables, recreates tables, extensions, and re-initializes baseline data.
    """
    await init_engine()
    if "doc_intelligence" not in str(db_url) and not force:
        raise RuntimeError(f"Safety check failed: database URL does not contain 'doc_intelligence': {db_url}")
        
    logger.warning("Performing safe reset of local development database...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    
    await init_postgres_db()
    logger.info("Local development database cleanly reset and re-initialized.")



# -------------------------------------------------------------
# MongoDB Connection (with auto-fallback to mongomock-motor)
# -------------------------------------------------------------
mongo_client = None
mongo_db = None
_is_mongo_mock = False
MONGO_BACKUP_FILE = DATA_DIR / "mongo_documents.json"

async def save_mongo_mock_backup():
    """Saves mock mongo collections to disk for persistence across server restarts."""
    global mongo_db, _is_mongo_mock
    if not _is_mongo_mock or mongo_db is None:
        return
    try:
        docs = await mongo_db.documents.find({}).to_list(10000)
        serializable = []
        for d in docs:
            item = dict(d)
            if "_id" in item:
                del item["_id"]
            if "created_at" in item and hasattr(item["created_at"], "isoformat"):
                item["created_at"] = item["created_at"].isoformat()
            serializable.append(item)
        with open(MONGO_BACKUP_FILE, "w", encoding="utf-8") as f:
            import json
            json.dump(serializable, f, indent=2)
        logger.debug(f"Saved {len(serializable)} documents to mongo backup {MONGO_BACKUP_FILE}")
    except Exception as e:
        logger.warning(f"Failed to backup mongomock: {e}")

async def init_mongo():
    global mongo_client, mongo_db, _is_mongo_mock
    if mongo_client is not None:
        return mongo_db

    try:
        real_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=1000
        )
        await real_client.admin.command("ping")
        mongo_client = real_client
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
        _is_mongo_mock = False
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
    except Exception as e:
        logger.info(f"MongoDB at {settings.MONGODB_URL} not reachable ({e}). Using mongomock-motor.")
        from mongomock_motor import AsyncMongoMockClient
        mongo_client = AsyncMongoMockClient()
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
        _is_mongo_mock = True

        # Restore from disk backup if available
        if MONGO_BACKUP_FILE.exists():
            try:
                import json
                import datetime
                with open(MONGO_BACKUP_FILE, "r", encoding="utf-8") as f:
                    saved_docs = json.load(f)
                if saved_docs:
                    for doc in saved_docs:
                        if "_id" in doc:
                            del doc["_id"]
                        if "created_at" in doc and isinstance(doc["created_at"], str):
                            try:
                                doc["created_at"] = datetime.datetime.fromisoformat(doc["created_at"])
                            except Exception:
                                pass
                    await mongo_db.documents.insert_many(saved_docs)
                    logger.info(f"Restored {len(saved_docs)} documents from {MONGO_BACKUP_FILE} into mongomock.")
            except Exception as ex:
                logger.warning(f"Could not restore mongo backup: {ex}")

    return mongo_db

def get_mongo_client():
    global mongo_client
    return mongo_client

def get_mongo_db():
    global mongo_db
    return mongo_db


# -------------------------------------------------------------
# ChromaDB Client
# -------------------------------------------------------------
_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client

    try:
        if settings.CHROMA_HOST and settings.CHROMA_HOST not in ("localhost", "127.0.0.1"):
            client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            client.heartbeat()
            _chroma_client = client
            logger.info(f"Connected to ChromaDB HTTP Server at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
            return _chroma_client
    except Exception as e:
        logger.info(f"ChromaDB HTTP Server not reachable ({e}), using PersistentClient.")

    _chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    logger.info(f"Using ChromaDB PersistentClient at {CHROMA_DIR}")
    return _chroma_client


def get_chroma_collection(collection_name: str = "document_chunks"):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
