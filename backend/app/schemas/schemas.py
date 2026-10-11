import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# -------------------------------------------------------------
# Auth Schemas
# -------------------------------------------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role_name: str = "EMPLOYEE"  # SUPER_ADMIN, ADMIN, MANAGER, EMPLOYEE, VIEWER
    department: str = "general"
    tenant_id: str = "tenant-default"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str
    department: Optional[str] = "general"
    tenant_id: str
    permissions: List[str]

class UserOut(BaseModel):
    id: int
    email: str
    role_name: str
    department: Optional[str] = "general"
    tenant_id: str
    permissions: List[str]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentAccessPolicyCreate(BaseModel):
    grantee_type: str = "USER"  # USER, ROLE, DEPARTMENT
    grantee_id: str
    permission_level: str = "READ"  # READ, WRITE, ADMIN

class DocumentAccessPolicyOut(BaseModel):
    id: int
    document_id: str
    grantee_type: str
    grantee_id: str
    permission_level: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Document Schemas
# -------------------------------------------------------------
class DocumentMetadataMongo(BaseModel):
    document_id: str
    title: str
    department: str
    classification: str = "internal"  # public, internal, confidential, restricted
    vendor: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    created_at: Optional[datetime.datetime] = None

class DocumentOut(BaseModel):
    id: str
    mongo_document_id: str
    title: str
    status: str
    tenant_id: str
    created_by: int
    department: Optional[str] = None
    classification: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentDetailOut(DocumentOut):
    metadata: Optional[Dict[str, Any]] = None
    creator_email: Optional[str] = None
    workflow_history: List[Dict[str, Any]] = []
    available_actions: List[str] = []


# -------------------------------------------------------------
# Workflow Schemas
# -------------------------------------------------------------
class WorkflowTransitionRequest(BaseModel):
    comment: Optional[str] = None

class WorkflowHistoryOut(BaseModel):
    id: int
    document_id: str
    from_state: str
    to_state: str
    actor_id: int
    actor_email: Optional[str] = None
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Audit Schemas
# -------------------------------------------------------------
class AuditLogOut(BaseModel):
    id: int
    document_id: Optional[str] = None
    actor_id: Optional[int] = None
    actor_email: Optional[str] = None
    action: str
    timestamp: datetime.datetime
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata")
    previous_hash: str
    current_hash: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AuditVerifyResponse(BaseModel):
    total_records: int
    is_valid: bool
    verified_at: datetime.datetime
    details: str
    broken_at_id: Optional[int] = None


# -------------------------------------------------------------
# RAG Schemas
# -------------------------------------------------------------
class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 4

class RAGSource(BaseModel):
    document_id: str
    document_title: str
    page: int
    chunk_id: str
    department: Optional[str] = None
    classification: Optional[str] = None
    relevance_score: Optional[float] = None

class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[RAGSource]
    query: str
    user_department_scope: List[str]
    retrieved_chunk_count: int


# -------------------------------------------------------------
# Health Schemas
# -------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    postgres: str
    mongodb: str
    chromadb: str
    llm_provider: str
    timestamp: datetime.datetime


# -------------------------------------------------------------
# Notification Schemas
# -------------------------------------------------------------
class NotificationOut(BaseModel):
    id: str
    tenant_id: str
    recipient_role: Optional[str] = None
    department: str
    document_id: Optional[str] = None
    event_type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    unread_count: int
    total_count: int
    notifications: List[NotificationOut]
