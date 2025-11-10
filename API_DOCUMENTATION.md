# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require authentication using JWT tokens. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register New User
Create a new company and admin user.

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "admin@company.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "company_name": "My Company",
  "company_domain": "mycompany.com"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "admin@company.com",
  "full_name": "John Doe",
  "role": "admin",
  "company_id": "uuid",
  "company_name": "My Company",
  "is_active": true,
  "mfa_enabled": false,
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": null
}
```

---

### Login
Login with email and password.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "admin@techcorp.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "mfa_required": false
}
```

**If MFA is enabled:**
```json
{
  "access_token": "temporary_token",
  "refresh_token": "",
  "token_type": "bearer",
  "mfa_required": true
}
```

---

### Verify MFA
Complete login with MFA code.

**Endpoint:** `POST /api/auth/verify-mfa`

**Request Body:**
```json
{
  "email": "admin@techcorp.com",
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "mfa_required": false
}
```

---

### Refresh Token
Get a new access token using refresh token.

**Endpoint:** `POST /api/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "mfa_required": false
}
```

---

### Logout
Revoke refresh token.

**Endpoint:** `POST /api/auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

## MFA Management Endpoints

### Setup MFA
Generate MFA secret and QR code.

**Endpoint:** `POST /api/auth/mfa/setup`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgo...",
  "manual_entry_key": "JBSW Y3DP EHPK 3PXP"
}
```

---

### Enable MFA
Enable MFA after verifying code.

**Endpoint:** `POST /api/auth/mfa/enable`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "backup_codes": [
    "A1B2-C3D4",
    "E5F6-G7H8",
    "I9J0-K1L2",
    "M3N4-O5P6",
    "Q7R8-S9T0",
    "U1V2-W3X4",
    "Y5Z6-A7B8",
    "C9D0-E1F2"
  ]
}
```

---

### Disable MFA
Disable MFA on account.

**Endpoint:** `POST /api/auth/mfa/disable`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "password": "SecurePass123!",
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "message": "MFA has been disabled"
}
```

---

### Get Backup Codes
Regenerate MFA backup codes.

**Endpoint:** `GET /api/auth/mfa/backup-codes`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "backup_codes": [
    "A1B2-C3D4",
    "E5F6-G7H8",
    // ... 8 codes total
  ]
}
```

---

## User Management Endpoints

### Get My Profile
Get current user's profile.

**Endpoint:** `GET /api/users/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "admin@techcorp.com",
  "full_name": "Admin User",
  "role": "admin",
  "company_id": "uuid",
  "company_name": "TechCorp",
  "is_active": true,
  "mfa_enabled": true,
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-10T10:30:00Z"
}
```

---

### Update My Profile
Update current user's profile.

**Endpoint:** `PUT /api/users/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "New Name",
  "email": "newemail@techcorp.com"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "newemail@techcorp.com",
  "full_name": "New Name",
  // ... rest of user data
}
```

---

### List Company Users
List all users in the company (Admin/Manager only).

**Endpoint:** `GET /api/users/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "email": "admin@techcorp.com",
    "full_name": "Admin User",
    "role": "admin",
    // ... user data
  },
  {
    "id": "uuid",
    "email": "user@techcorp.com",
    "full_name": "Regular User",
    "role": "user",
    // ... user data
  }
]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation Error",
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 422 Validation Error
```json
{
  "error": "Validation Error",
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limiting
- Login attempts: 5 per minute
- MFA verification: 3 per minute
- API calls: 100 per minute

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "company_name": "Test Company",
    "company_domain": "testco.com"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@techcorp.com",
    "password": "SecurePass123!"
  }'
```

### Get Profile
```bash
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
