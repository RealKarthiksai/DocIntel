import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.postgres_models import User, Role
from app.schemas.schemas import UserLogin, UserRegister, TokenResponse, UserOut
from app.security.jwt import get_password_hash, verify_password, create_access_token, get_current_user, CurrentUserContext
from app.services.audit_service import log_audit_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

DEFAULT_DEMO_USERS = [
    {
        "email": "superadmin@example.com",
        "password": "SuperAdminPass123!",
        "role_name": "SUPER_ADMIN",
        "department": "general",
        "tenant_id": "tenant-default"
    },
    {
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "role_name": "ADMIN",
        "department": "general",
        "tenant_id": "tenant-default"
    },
    {
        "email": "finance_manager@example.com",
        "password": "FinManagerPass123!",
        "role_name": "MANAGER",
        "department": "finance",
        "tenant_id": "tenant-default"
    },
    {
        "email": "eng_manager@example.com",
        "password": "EngManagerPass123!",
        "role_name": "MANAGER",
        "department": "engineering",
        "tenant_id": "tenant-default"
    },
    {
        "email": "finance_emp@example.com",
        "password": "FinEmpPass123!",
        "role_name": "EMPLOYEE",
        "department": "finance",
        "tenant_id": "tenant-default"
    },
    {
        "email": "eng_emp@example.com",
        "password": "EngEmpPass123!",
        "role_name": "EMPLOYEE",
        "department": "engineering",
        "tenant_id": "tenant-default"
    },
    {
        "email": "viewer@example.com",
        "password": "ViewerPass123!",
        "role_name": "VIEWER",
        "department": "general",
        "tenant_id": "tenant-default"
    },
    # Backward compatibility aliases
    {
        "email": "manager@example.com",
        "password": "ManagerPass123!",
        "role_name": "MANAGER",
        "department": "finance",
        "tenant_id": "tenant-default"
    },
    {
        "email": "employee@example.com",
        "password": "EmployeePass123!",
        "role_name": "EMPLOYEE",
        "department": "general",
        "tenant_id": "tenant-default"
    },
    {
        "email": "tenant_b_user@example.com",
        "password": "TenantBPass123!",
        "role_name": "EMPLOYEE",
        "department": "general",
        "tenant_id": "tenant-b"
    }
]

async def seed_default_users(db: AsyncSession):
    from app.models.postgres_models import Department
    for udata in DEFAULT_DEMO_USERS:
        stmt = select(User).where(User.email == udata["email"])
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user:
            role_stmt = select(Role).where(Role.name == udata["role_name"])
            role_res = await db.execute(role_stmt)
            role = role_res.scalars().first()
            
            dept_name = udata.get("department", "general").lower()
            dept_res = await db.execute(select(Department).where(Department.name == dept_name))
            dept = dept_res.scalars().first()
            dept_id = dept.id if dept else None

            if role:
                new_user = User(
                    email=udata["email"],
                    password_hash=get_password_hash(udata["password"]),
                    role_id=role.id,
                    department_id=dept_id,
                    department=dept_name,
                    tenant_id=udata["tenant_id"]
                )
                db.add(new_user)
                await db.commit()
                logger.info(f"Seeded demo user: {udata['email']} with role {udata['role_name']} in dept {dept_name}")

@router.post("/register", response_model=UserOut)
async def register(req: UserRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    role_stmt = select(Role).where(Role.name == req.role_name.upper())
    role_res = await db.execute(role_stmt)
    role = role_res.scalars().first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{req.role_name}' does not exist"
        )
    
    new_user = User(
        email=req.email,
        password_hash=get_password_hash(req.password),
        role_id=role.id,
        tenant_id=req.tenant_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await log_audit_event(
        db,
        action="USER_REGISTERED",
        actor_id=new_user.id,
        metadata_info={"email": new_user.email, "role": role.name, "tenant": new_user.tenant_id}
    )

    return UserOut(
        id=new_user.id,
        email=new_user.email,
        role_name=role.name,
        tenant_id=new_user.tenant_id,
        permissions=role.permissions,
        created_at=new_user.created_at
    )

@router.post("/login", response_model=TokenResponse)
async def login(req: UserLogin, db: AsyncSession = Depends(get_db)):
    # Auto-seed demo users on first login attempt if empty
    await seed_default_users(db)

    stmt = select(User).where(User.email == req.email).options(selectinload(User.role))
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    role_name = user.role.name if user.role else "EMPLOYEE"
    permissions = user.role.permissions if user.role and user.role.permissions else ["general"]
    
    token = create_access_token(data={
        "user_id": user.id,
        "email": user.email,
        "role": role_name,
        "tenant_id": user.tenant_id,
        "permissions": permissions
    })

    await log_audit_event(
        db,
        action="LOGIN",
        actor_id=user.id,
        metadata_info={"email": user.email, "tenant": user.tenant_id, "role": role_name}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=role_name,
        department=user.department,
        tenant_id=user.tenant_id,
        permissions=permissions
    )

@router.get("/me", response_model=UserOut)
async def get_me(current_user: CurrentUserContext = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        role_name=current_user.role,
        department=current_user.department,
        tenant_id=current_user.tenant_id,
        permissions=current_user.permissions,
        created_at=current_user.raw_user.created_at
    )
