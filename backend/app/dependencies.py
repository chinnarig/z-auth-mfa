from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Optional
from uuid import UUID

from app.database import get_db, set_company_context
from app.models import User, UserRole, Company
from app.auth import verify_token
from app.schemas import TokenData
import json
from datetime import datetime

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token, token_type="access")
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if MFA is pending
        if payload.get("mfa_required", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MFA verification required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(
            user_id=UUID(user_id),
            email=payload.get("email"),
            company_id=UUID(payload.get("company_id")),
            role=payload.get("role")
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Set company context for Row-Level Security
    set_company_context(db, str(user.company_id))
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """Dependency to check if user has required role"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return role_checker


# Specific role dependencies
async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_admin_or_manager(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin or manager role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager access required"
        )
    return current_user


async def log_audit_event(
    action: str,
    user: User,
    db: Session,
    request: Request,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    extra_data: Optional[dict] = None
):
    """Log an audit event"""
    from app.models import AuditLog
    
    # Get IP address
    ip_address = request.client.host if request.client else None
    
    # Get user agent
    user_agent = request.headers.get("user-agent", "")
    
    # Create audit log
    audit_log = AuditLog(
        company_id=user.company_id,
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=json.dumps(extra_data) if extra_data else None
    )
    
    db.add(audit_log)
    db.commit()


async def log_anonymous_audit_event(
    action: str,
    company_id: UUID,
    db: Session,
    request: Request,
    user_id: Optional[UUID] = None,
    extra_data: Optional[dict] = None
):
    """Log an audit event without requiring authenticated user"""
    from app.models import AuditLog
    
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    
    audit_log = AuditLog(
        company_id=company_id,
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=json.dumps(extra_data) if extra_data else None
    )
    
    db.add(audit_log)
    db.commit()
