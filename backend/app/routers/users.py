from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import User, Company, UserRole
from app.schemas import UserResponse, UserUpdate, MessageResponse
from app.dependencies import (
    get_current_active_user,
    require_admin,
    require_admin_or_manager,
    log_audit_event
)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        company_id=current_user.company_id,
        company_name=company.name if company else "",
        is_active=current_user.is_active,
        mfa_enabled=current_user.mfa_enabled,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Check if email is already taken
        existing = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        current_user.email = user_update.email
        current_user.email_verified = False  # Require re-verification
    
    db.commit()
    db.refresh(current_user)
    
    # Log audit event
    await log_audit_event(
        action="user_updated",
        user=current_user,
        db=db,
        request=request,
        resource_type="user",
        resource_id=current_user.id
    )
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        company_id=current_user.company_id,
        company_name=company.name if company else "",
        is_active=current_user.is_active,
        mfa_enabled=current_user.mfa_enabled,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.get("/", response_model=List[UserResponse])
async def list_company_users(
    current_user: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db)
):
    """List all users in the company (Admin/Manager only)"""
    
    users = db.query(User).filter(
        User.company_id == current_user.company_id
    ).all()
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            company_id=user.company_id,
            company_name=company.name if company else "",
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin_or_manager),
    db: Session = Depends(get_db)
):
    """Get user details (Admin/Manager only)"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id  # Same company only
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    company = db.query(Company).filter(Company.id == user.company_id).first()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=user.company_id,
        company_name=company.name if company else "",
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (Admin only)"""
    
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log before deletion
    await log_audit_event(
        action="user_deleted",
        user=current_user,
        db=db,
        request=request,
        resource_type="user",
        resource_id=user.id,
        extra_data={"deleted_user_email": user.email}
    )
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message=f"User {user.email} deleted successfully")


@router.post("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Deactivate a user (Admin only)"""
    
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    # Log audit event
    await log_audit_event(
        action="user_deactivated",
        user=current_user,
        db=db,
        request=request,
        resource_type="user",
        resource_id=user.id
    )
    
    return MessageResponse(message=f"User {user.email} deactivated successfully")


@router.post("/{user_id}/activate", response_model=MessageResponse)
async def activate_user(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate a user (Admin only)"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    # Log audit event
    await log_audit_event(
        action="user_activated",
        user=current_user,
        db=db,
        request=request,
        resource_type="user",
        resource_id=user.id
    )
    
    return MessageResponse(message=f"User {user.email} activated successfully")
