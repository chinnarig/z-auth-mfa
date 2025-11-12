from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models import UserRole


# ============ Auth Schemas ============

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    company_name: str = Field(..., min_length=2, max_length=255)
    company_domain: str = Field(..., min_length=2, max_length=255)
    company_address: Optional[str] = None
    company_phone_1: Optional[str] = None
    company_phone_2: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class MFAVerification(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    mfa_required: bool = False


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    company_id: Optional[UUID] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ============ MFA Schemas ============

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str  # Base64 encoded QR code image
    manual_entry_key: str


class MFAEnableRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class MFADisableRequest(BaseModel):
    password: str
    code: Optional[str] = None  # Can use backup code instead


class BackupCodesResponse(BaseModel):
    backup_codes: List[str]


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str
    company_id: UUID


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    id: UUID
    company_id: UUID
    is_active: bool
    email_verified: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    company_id: UUID
    company_name: str
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# ============ Company Schemas ============

class CompanyBase(BaseModel):
    name: str
    domain: str
    address: Optional[str] = None
    phone_number_1: Optional[str] = None
    phone_number_2: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    address: Optional[str] = None
    phone_number_1: Optional[str] = None
    phone_number_2: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: UUID
    api_key: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Audit Log Schemas ============

class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    ip_address: Optional[str]
    user_email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Generic Response Schemas ============

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
