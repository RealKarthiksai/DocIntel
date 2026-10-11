import datetime
import uuid
from typing import Optional, Any, List
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, func, Index
)
from sqlalchemy.orm import declarative_base, relationship, foreign
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # finance, engineering, hr, legal, general
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("User", back_populates="department_rel")
    documents = relationship("Document", back_populates="department_rel")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # SUPER_ADMIN, ADMIN, MANAGER, EMPLOYEE, VIEWER
    description = Column(String(255), nullable=True)
    permissions = Column(JSON, nullable=False, default=list)  # list of strings: ["*"], ["documents:read", "rag:query"], etc.

    users = relationship("User", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    department = Column(String(100), nullable=False, default="general", index=True)
    tenant_id = Column(String(100), nullable=False, default="tenant-default", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    role = relationship("Role", back_populates="users")
    department_rel = relationship("Department", back_populates="users")
    documents = relationship("Document", back_populates="creator")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True, index=True)  # e.g., "DOC-001" or UUID
    mongo_document_id = Column(String(100), unique=True, nullable=True, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)  # DRAFT, UNDER_REVIEW, APPROVED, REJECTED, ARCHIVED
    tenant_id = Column(String(100), nullable=False, default="tenant-default", index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    department = Column(String(100), nullable=False, default="general", index=True)
    classification = Column(String(50), nullable=False, default="internal", index=True)  # public, internal, confidential, restricted
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    creator = relationship("User", back_populates="documents")
    department_rel = relationship("Department", back_populates="documents")
    workflow_history = relationship("WorkflowHistory", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship(
        "AuditLog",
        primaryjoin="Document.id == foreign(AuditLog.document_id)",
        back_populates="document",
        passive_deletes="all",
        cascade="none"
    )
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    access_policies = relationship("DocumentAccessPolicy", back_populates="document", cascade="all, delete-orphan")


class DocumentAccessPolicy(Base):
    """
    Explicit document-level access control list (ACL) for sharing specific documents
    with individual users, roles, or departments.
    """
    __tablename__ = "document_access_policies"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    grantee_type = Column(String(50), nullable=False)  # "USER", "ROLE", "DEPARTMENT"
    grantee_id = Column(String(100), nullable=False, index=True)  # str(user.id), role.name, or department.name
    permission_level = Column(String(50), nullable=False, default="READ")  # "READ", "WRITE", "ADMIN"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="access_policies")


class DocumentChunk(Base):
    """
    PostgreSQL vector store for document chunks and 384-dimensional dense embeddings
    using pgvector with HNSW cosine index and full-text search tsvector.
    """
    __tablename__ = "document_chunks"

    id = Column(String(100), primary_key=True, index=True)  # e.g., "DOC-XXXX-P1-1"
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_seq = Column(Integer, nullable=False)
    page = Column(Integer, nullable=False, default=1)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # 384 dimensions matching all-MiniLM-L6-v2
    tsv = Column(TSVECTOR, nullable=True)  # Full-Text Search vector for hybrid retrieval
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("idx_document_chunks_doc_seq", "document_id", "chunk_seq"),
    )


class WorkflowHistory(Base):
    __tablename__ = "workflow_history"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(50), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(String(50), nullable=False)
    to_state = Column(String(50), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="workflow_history")
    actor = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(50), nullable=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False, index=True)

    document = relationship("Document", primaryjoin="Document.id == foreign(AuditLog.document_id)", back_populates="audit_logs")
    actor = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    tenant_id = Column(String(100), nullable=False, index=True)
    recipient_role = Column(String(50), nullable=True, index=True)
    department = Column(String(100), nullable=False, default="general", index=True)
    document_id = Column(String(50), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
