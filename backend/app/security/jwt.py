import datetime
import bcrypt
import jwt
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.postgres_models import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

class CurrentUserContext:
    def __init__(self, user: User):
        self.id = user.id
        self.email = user.email
        self.tenant_id = user.tenant_id
        self.role_id = user.role_id
        self.role = user.role.name if user.role else "EMPLOYEE"
        self.department = user.department.lower() if user.department else "general"
        self.permissions: List[str] = user.role.permissions if user.role and user.role.permissions else ["documents:read", "rag:query"]
        self.raw_user = user

    @property
    def is_super_admin(self) -> bool:
        return self.role == "SUPER_ADMIN"

    @property
    def is_admin(self) -> bool:
        return self.role in ["SUPER_ADMIN", "ADMIN"]

    @property
    def is_manager(self) -> bool:
        return self.role == "MANAGER"

    @property
    def is_employee(self) -> bool:
        return self.role == "EMPLOYEE"

    @property
    def is_viewer(self) -> bool:
        return self.role == "VIEWER"

    def has_permission(self, permission: str) -> bool:
        if "*" in self.permissions or self.is_super_admin:
            return True
        return permission in self.permissions

    def can_access_department(self, department: str) -> bool:
        if self.is_super_admin:
            return True
        if self.is_admin:
            return True
        dept_clean = department.lower()
        if dept_clean == "general":
            return True
        return dept_clean == self.department

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> CurrentUserContext:
    payload = decode_access_token(token)
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    stmt = select(User).where(User.id == user_id).options(selectinload(User.role))
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentUserContext(user)

def require_role(roles: List[str]):
    def role_checker(current_user: CurrentUserContext = Depends(get_current_user)) -> CurrentUserContext:
        if current_user.role not in roles and not current_user.is_super_admin and current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {roles}"
            )
        return current_user
    return role_checker

def require_permission(permission: str):
    def perm_checker(current_user: CurrentUserContext = Depends(get_current_user)) -> CurrentUserContext:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required permission: {permission}"
            )
        return current_user
    return perm_checker

