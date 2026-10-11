from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Document Intelligence & Workflow Automation Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = ""

    # Database URLs
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/doc_intelligence",
        validation_alias="DATABASE_URL"
    )
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "doc_intelligence"

    # MongoDB
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        validation_alias="MONGODB_URL"
    )
    MONGODB_DB_NAME: str = "doc_intelligence"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8002
    CHROMA_PERSIST_DIRECTORY: str = "./data/chromadb"

    # Security & Auth
    JWT_SECRET: str = "super-secret-enterprise-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # LLM & RAG
    LLM_PROVIDER: str = "ollama"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Document Processing & Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]

    # RBAC Default Permissions for 5 Roles
    ROLE_PERMISSIONS: Dict[str, List[str]] = {
        "SUPER_ADMIN": ["*"],
        "ADMIN": ["documents:read", "documents:write", "documents:delete", "documents:approve", "rag:query", "audit:read", "users:manage", "policies:manage"],
        "MANAGER": ["documents:read", "documents:write", "documents:approve", "rag:query"],
        "EMPLOYEE": ["documents:read", "documents:write", "rag:query"],
        "VIEWER": ["documents:read", "rag:query"]
    }

    # Kafka & Event-Driven Messaging
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_WORKFLOW_EVENTS: str = "document.workflow.events"
    KAFKA_GROUP_ID: str = "enterprise-notification-service"
    KAFKA_ENABLED: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
