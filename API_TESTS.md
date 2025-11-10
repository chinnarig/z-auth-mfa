# API Testing Guide

## Test Credentials
- **Email**: `admin@startupxyz.com`
- **Password**: `SecurePass123!`

## Base URL
```
http://localhost:8000
```

---

## Test 1: Register New User (Optional - if you want a fresh account)

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@mycompany.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "company_name": "My Test Company",
    "company_domain": "mycompany.com"
  }'
```

**Expected Response**: 201 Created with user details

---

## Test 2: Login (Without MFA)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response**: 200 OK
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "mfa_required": false
}
```

**Save the `access_token` for next tests!**

---

## Test 3: Get My Profile

Replace `YOUR_ACCESS_TOKEN` with the token from Test 2:

```bash
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response**: 200 OK with user profile

---

## Test 4: Setup MFA

```bash
curl -X POST http://localhost:8000/api/auth/mfa/setup \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response**: 200 OK
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgo...",
  "manual_entry_key": "JBSW Y3DP EHPK 3PXP"
}
```

**Instructions**:
1. Open Microsoft Authenticator app on your phone
2. Tap "+" to add account
3. Select "Other account (Google, Facebook, etc.)"
4. Choose "Scan QR code" or "Enter code manually"
5. If scanning: Use the `qr_code` (save it as an HTML file to view)
6. If manual: Enter the `manual_entry_key` (remove spaces)
7. Account name: Your email (admin@startupxyz.com)
8. The app will start generating 6-digit codes

---

## Test 5: Enable MFA

Get the 6-digit code from Microsoft Authenticator and use it:

```bash
curl -X POST http://localhost:8000/api/auth/mfa/enable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "123456"
  }'
```

Replace `123456` with the actual code from your authenticator app.

**Expected Response**: 200 OK with backup codes
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

**IMPORTANT**: Save these backup codes in a secure place! You can use them if you lose access to your authenticator app.

---

## Test 6: Login with MFA

Now that MFA is enabled, logout and login again:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response**: 200 OK
```json
{
  "access_token": "temporary_mfa_pending_token",
  "refresh_token": "",
  "token_type": "bearer",
  "mfa_required": true
}
```

Notice `mfa_required: true` - You need to verify MFA code now.

---

## Test 7: Verify MFA Code

Get the current code from Microsoft Authenticator:

```bash
curl -X POST http://localhost:8000/api/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "code": "123456"
  }'
```

Replace `123456` with the current code from your app.

**Expected Response**: 200 OK
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "mfa_required": false
}
```

Now you have full access!

---

## Test 8: Test Backup Code (Optional)

You can also login with a backup code instead of the authenticator:

```bash
# Step 1: Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }'

# Step 2: Use backup code for MFA verification
curl -X POST http://localhost:8000/api/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "code": "A1B2-C3D4"
  }'
```

Replace with one of your actual backup codes.

**Note**: Each backup code can only be used once!

---

## Test 9: Regenerate Backup Codes

```bash
curl -X GET http://localhost:8000/api/auth/mfa/backup-codes \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response**: New set of 8 backup codes

---

## Test 10: Disable MFA

```bash
curl -X POST http://localhost:8000/api/auth/mfa/disable \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "SecurePass123!",
    "code": "123456"
  }'
```

Use current code from Microsoft Authenticator or a backup code.

**Expected Response**: 200 OK
```json
{
  "message": "MFA has been disabled"
}
```

---

## Test 11: Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response**: New access token

---

## Test 12: List Company Users (Admin/Manager only)

```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response**: Array of users in your company

---

## Test 13: Update Profile

```bash
curl -X PUT http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'
```

**Expected Response**: Updated user profile

---

## Test 14: Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response**: 200 OK

---

## Quick QR Code Viewer

To view the QR code from the MFA setup response, create an HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>MFA QR Code</title>
</head>
<body>
    <h1>Scan this QR Code with Microsoft Authenticator</h1>
    <img src="PASTE_QR_CODE_DATA_HERE" alt="MFA QR Code" style="width: 300px; height: 300px;">
    <p>Or enter this code manually:</p>
    <h2>PASTE_MANUAL_ENTRY_KEY_HERE</h2>
</body>
</html>
```

Replace `PASTE_QR_CODE_DATA_HERE` with the full `qr_code` value from Test 4.

---

## Troubleshooting

### 401 Unauthorized
- Check if your access token is valid
- Token might have expired (default: 30 minutes)
- Use refresh token to get a new access token

### 403 Forbidden
- You don't have permission for this endpoint
- Some endpoints require Admin or Manager role

### MFA Code Invalid
- Make sure your phone's time is synchronized (very important!)
- TOTP codes are time-based (30-second window)
- Wait for a new code and try again
- Try using a backup code instead

### 500 Internal Server Error
- Check backend logs for details
- Verify database connection
- Check if all required environment variables are set

---

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://postgres:Admin%40011235@35.232.108.201:5432/mfa
SECRET_KEY=your-secret-key-min-32-chars-long-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MFA_ISSUER_NAME=Z-Auth MFA Platform

# Email settings (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com
```

