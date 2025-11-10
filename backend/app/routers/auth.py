from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID

from app.database import get_db
from app.models import User, Company, RefreshToken, UserRole
from app.schemas import (
    UserRegister, UserLogin, Token, MFAVerification,
    RefreshTokenRequest, MFASetupResponse, MFAEnableRequest,
    MFADisableRequest, BackupCodesResponse, MessageResponse, UserResponse
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, verify_token, create_mfa_pending_token,
    generate_backup_codes
)
from app.utils.mfa import (
    generate_mfa_secret, get_totp_uri, generate_qr_code,
    verify_totp_code, encrypt_data, decrypt_data,
    encrypt_backup_codes, decrypt_backup_codes, verify_backup_code,
    format_secret_for_manual_entry
)
from app.utils.email import send_welcome_email, send_mfa_enabled_email, send_login_notification
from app.dependencies import get_current_active_user, log_anonymous_audit_event, log_audit_event

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new company and admin user"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if company domain already exists
    existing_company = db.query(Company).filter(Company.domain == user_data.company_domain).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company domain already registered"
        )
    
    # Create company
    company = Company(
        name=user_data.company_name,
        domain=user_data.company_domain,
        is_active=True
    )
    db.add(company)
    db.flush()  # Flush to get company.id
    
    # Create admin user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        company_id=company.id,
        role=UserRole.ADMIN,  # First user is always admin
        is_active=True,
        email_verified=True  # Auto-verify for now
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(company)
    
    # Log audit event
    await log_anonymous_audit_event(
        action="user_registered",
        company_id=company.id,
        db=db,
        request=request,
        user_id=user.id,
        metadata={"email": user.email, "role": user.role.value}
    )
    
    # Send welcome email (async, don't wait)
    try:
        await send_welcome_email(user.email, user.full_name, company.name)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=user.company_id,
        company_name=company.name,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check if MFA is enabled
    if user.mfa_enabled:
        # Return a temporary token that requires MFA verification
        mfa_token = create_mfa_pending_token(
            str(user.id),
            user.email,
            str(user.company_id),
            user.role.value
        )
        
        return Token(
            access_token=mfa_token,
            refresh_token="",
            mfa_required=True
        )
    
    # MFA not enabled - proceed with normal login
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value
        }
    )
    
    refresh_token_str, refresh_expires = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=refresh_expires
    )
    db.add(refresh_token)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log audit event
    await log_anonymous_audit_event(
        action="user_login",
        company_id=user.company_id,
        db=db,
        request=request,
        user_id=user.id,
        metadata={"email": user.email, "mfa_used": False}
    )
    
    # Send login notification (async, don't wait)
    try:
        ip_address = request.client.host if request.client else "Unknown"
        await send_login_notification(user.email, user.full_name, ip_address)
    except Exception as e:
        print(f"Failed to send login notification: {e}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        mfa_required=False
    )


@router.post("/verify-mfa", response_model=Token)
async def verify_mfa(
    mfa_data: MFAVerification,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify MFA code and complete login"""
    
    # Find user
    user = db.query(User).filter(User.email == mfa_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this account"
        )
    
    # Decrypt MFA secret
    mfa_secret = decrypt_data(user.mfa_secret)
    
    # Verify TOTP code
    is_valid_totp = verify_totp_code(mfa_secret, mfa_data.code)
    
    # If TOTP fails, try backup codes
    is_valid_backup = False
    if not is_valid_totp and user.mfa_backup_codes:
        is_valid_backup, updated_codes = verify_backup_code(
            user.mfa_backup_codes,
            mfa_data.code
        )
        if is_valid_backup:
            # Update backup codes (one was used)
            user.mfa_backup_codes = updated_codes
            db.commit()
    
    if not is_valid_totp and not is_valid_backup:
        # Log failed attempt
        await log_anonymous_audit_event(
            action="mfa_verification_failed",
            company_id=user.company_id,
            db=db,
            request=request,
            user_id=user.id,
            metadata={"email": user.email}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value
        }
    )
    
    refresh_token_str, refresh_expires = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=refresh_expires
    )
    db.add(refresh_token)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log successful login
    await log_anonymous_audit_event(
        action="user_login",
        company_id=user.company_id,
        db=db,
        request=request,
        user_id=user.id,
        metadata={
            "email": user.email,
            "mfa_used": True,
            "backup_code_used": is_valid_backup
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        mfa_required=False
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token
    try:
        payload = verify_token(token_data.refresh_token, token_type="refresh")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token exists and is not revoked
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.revoked == False
    ).first()
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token"
        )
    
    # Check if token is expired
    if stored_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == stored_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=token_data.refresh_token,  # Return same refresh token
        mfa_required=False
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    token_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user by revoking refresh token"""
    
    # Revoke the refresh token
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if stored_token:
        stored_token.revoked = True
        db.commit()
    
    return MessageResponse(message="Successfully logged out")


# ========== MFA Management Endpoints ==========

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate MFA secret and QR code for setup"""
    
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    # Generate new secret
    secret = generate_mfa_secret()
    
    # Generate provisioning URI
    uri = get_totp_uri(secret, current_user.email)
    
    # Generate QR code
    qr_code = generate_qr_code(uri)
    
    # Store encrypted secret temporarily (will be confirmed on enable)
    current_user.mfa_secret = encrypt_data(secret)
    db.commit()
    
    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        manual_entry_key=format_secret_for_manual_entry(secret)
    )


@router.post("/mfa/enable", response_model=BackupCodesResponse)
async def enable_mfa(
    mfa_request: MFAEnableRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enable MFA after verifying the code"""
    
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not initiated. Call /mfa/setup first"
        )
    
    # Decrypt secret
    secret = decrypt_data(current_user.mfa_secret)
    
    # Verify code
    if not verify_totp_code(secret, mfa_request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    # Enable MFA
    current_user.mfa_enabled = True
    current_user.mfa_backup_codes = encrypt_backup_codes(backup_codes)
    db.commit()
    
    # Log audit event
    await log_audit_event(
        action="mfa_enabled",
        user=current_user,
        db=db,
        request=request
    )
    
    # Send notification email
    try:
        await send_mfa_enabled_email(current_user.email, current_user.full_name)
    except Exception as e:
        print(f"Failed to send MFA enabled email: {e}")
    
    return BackupCodesResponse(backup_codes=backup_codes)


@router.post("/mfa/disable", response_model=MessageResponse)
async def disable_mfa(
    mfa_request: MFADisableRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable MFA"""
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify password
    if not verify_password(mfa_request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # If code provided, verify it
    if mfa_request.code:
        secret = decrypt_data(current_user.mfa_secret)
        
        # Try TOTP
        is_valid_totp = verify_totp_code(secret, mfa_request.code)
        
        # Try backup code
        is_valid_backup = False
        if not is_valid_totp:
            is_valid_backup, _ = verify_backup_code(
                current_user.mfa_backup_codes,
                mfa_request.code
            )
        
        if not is_valid_totp and not is_valid_backup:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    
    # Disable MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_backup_codes = None
    db.commit()
    
    # Log audit event
    await log_audit_event(
        action="mfa_disabled",
        user=current_user,
        db=db,
        request=request
    )
    
    return MessageResponse(message="MFA has been disabled")


@router.get("/mfa/backup-codes", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate backup codes"""
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Generate new backup codes
    backup_codes = generate_backup_codes()
    
    # Update user
    current_user.mfa_backup_codes = encrypt_backup_codes(backup_codes)
    db.commit()
    
    return BackupCodesResponse(backup_codes=backup_codes)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    
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
