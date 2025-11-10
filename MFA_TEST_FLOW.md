# MFA Test Flow - Complete Guide

This guide shows the complete flow of setting up and using MFA with Microsoft Authenticator.

## Prerequisites
- Backend server running on http://localhost:8000
- Microsoft Authenticator app installed on your phone
- Test user: `admin@startupxyz.com` / `SecurePass123!`

---

## Step 1: Login WITHOUT MFA (Initial State)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "refresh_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "mfa_required": false
}
```

**✓ MFA is NOT required yet** - Save the `access_token` for next steps.

---

## Step 2: Get User Profile (Verify MFA Status)

```bash
export ACCESS_TOKEN="<paste_your_access_token_here>"

curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": "uuid",
  "email": "admin@startupxyz.com",
  "full_name": "Startup Admin",
  "role": "admin",
  "company_id": "uuid",
  "company_name": "StartupXYZ",
  "is_active": true,
  "mfa_enabled": false,    ← MFA is currently disabled
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-10T10:30:00Z"
}
```

---

## Step 3: Setup MFA (Generate QR Code and Secret)

```bash
curl -X POST http://localhost:8000/api/auth/mfa/setup \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "manual_entry_key": "JBSW Y3DP EHPK 3PXP"
}
```

**Important Fields:**
- `secret`: The raw TOTP secret (base32 encoded)
- `qr_code`: Base64 encoded QR code image (can be displayed in browser)
- `manual_entry_key`: Formatted secret for manual entry (with spaces)

---

## Step 4: Add to Microsoft Authenticator

### Method A: Scan QR Code

1. Save the QR code to an HTML file:

```bash
cat > /tmp/qr_code.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>MFA QR Code</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        img { 
            width: 300px; 
            height: 300px; 
            border: 2px solid #ddd;
            border-radius: 10px;
        }
        h1 { color: #333; }
        .account { 
            background: #f0f0f0; 
            padding: 10px; 
            border-radius: 5px;
            margin: 20px 0;
            font-size: 16px;
        }
        .instructions {
            text-align: left;
            margin-top: 20px;
            padding: 20px;
            background: #e8f4fd;
            border-radius: 5px;
        }
        .instructions li {
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 MFA Setup</h1>
        <p>Scan this QR Code with Microsoft Authenticator</p>
        
        <!-- PASTE QR CODE DATA BELOW -->
        <img src="data:image/png;base64,iVBORw0KGgo..." alt="MFA QR Code">
        
        <div class="account">
            <strong>Account:</strong> admin@startupxyz.com<br>
            <strong>Issuer:</strong> Z-Auth MFA Platform
        </div>
        
        <div class="instructions">
            <h3>Steps:</h3>
            <ol>
                <li>Open <strong>Microsoft Authenticator</strong> on your phone</li>
                <li>Tap the <strong>"+"</strong> button</li>
                <li>Select <strong>"Other account (Google, Facebook, etc.)"</strong></li>
                <li>Choose <strong>"Scan a QR code"</strong></li>
                <li>Point your camera at the QR code above</li>
                <li>The account will be added automatically!</li>
            </ol>
        </div>
    </div>
</body>
</html>
EOF

open /tmp/qr_code.html
```

2. Open Microsoft Authenticator
3. Tap "+" → "Other account" → "Scan QR code"
4. Scan the QR code from the browser

### Method B: Manual Entry

1. Open Microsoft Authenticator
2. Tap "+" → "Other account" → "Or enter code manually"
3. **Account name:** `admin@startupxyz.com`
4. **Your key:** `JBSWY3DPEHPK3PXP` (remove spaces from manual_entry_key)
5. **Type of account:** Time based
6. Tap "Finish"

**✓ You should now see a 6-digit code updating every 30 seconds!**

---

## Step 5: Enable MFA (Verify the Code)

Get the current 6-digit code from Microsoft Authenticator and use it:

```bash
# Replace 123456 with the actual code from your app
curl -X POST http://localhost:8000/api/auth/mfa/enable \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "123456"
  }'
```

**Expected Response:**
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

**⚠️ CRITICAL: Save these backup codes!**
- Store them in a secure password manager
- Print them and keep in a safe place
- You'll need them if you lose your phone

**✓ MFA is now enabled!**

---

## Step 6: Test Login WITH MFA

### Step 6a: Initial Login (Password Only)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "temporary_mfa_pending_token",
  "refresh_token": "",
  "token_type": "bearer",
  "mfa_required": true    ← MFA is now required!
}
```

**Notice:** You get a temporary token but `mfa_required: true`

### Step 6b: Verify MFA Code

Get the current code from Microsoft Authenticator:

```bash
# Replace 123456 with current code from authenticator
curl -X POST http://localhost:8000/api/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "code": "123456"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "refresh_token": "eyJ0eXAiOiJKV1Qi...",
  "token_type": "bearer",
  "mfa_required": false
}
```

**✓ Successfully logged in with MFA!**

---

## Step 7: Test Backup Code Login

If you lose your phone, you can use a backup code:

```bash
# Step 1: Login with password
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }'

# Step 2: Use backup code instead of authenticator code
curl -X POST http://localhost:8000/api/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "code": "A1B2-C3D4"
  }'
```

**Expected Response:** Same as Step 6b

**⚠️ Note:** Each backup code can only be used ONCE!

---

## Step 8: Regenerate Backup Codes

If you've used some backup codes, generate new ones:

```bash
export ACCESS_TOKEN="<your_access_token>"

curl -X GET http://localhost:8000/api/auth/mfa/backup-codes \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "backup_codes": [
    "X9Y8-Z7W6",
    "V5U4-T3S2",
    "R1Q0-P9O8",
    "N7M6-L5K4",
    "J3I2-H1G0",
    "F9E8-D7C6",
    "B5A4-Z3Y2",
    "X1W0-V9U8"
  ]
}
```

**✓ New backup codes generated!** Old ones are now invalid.

---

## Step 9: Disable MFA (Optional)

```bash
# Get current code from Microsoft Authenticator or use a backup code
curl -X POST http://localhost:8000/api/auth/mfa/disable \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "SecurePass123!",
    "code": "123456"
  }'
```

**Expected Response:**
```json
{
  "message": "MFA has been disabled"
}
```

**✓ MFA is now disabled** - You can remove the account from Microsoft Authenticator

---

## Complete Test Sequence

Here's a complete bash script that tests the entire flow:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
EMAIL="admin@startupxyz.com"
PASSWORD="SecurePass123!"

echo "========================================="
echo "Complete MFA Test Flow"
echo "========================================="
echo ""

# Step 1: Login without MFA
echo "Step 1: Initial Login (No MFA)..."
LOGIN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo $LOGIN | jq -r '.access_token')
echo "✓ Logged in. MFA Required: $(echo $LOGIN | jq -r '.mfa_required')"
echo ""

# Step 2: Check profile
echo "Step 2: Check MFA Status..."
PROFILE=$(curl -s -X GET "$BASE_URL/api/users/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "MFA Enabled: $(echo $PROFILE | jq -r '.mfa_enabled')"
echo ""

# Step 3: Setup MFA
echo "Step 3: Setup MFA..."
MFA_SETUP=$(curl -s -X POST "$BASE_URL/api/auth/mfa/setup" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

SECRET=$(echo $MFA_SETUP | jq -r '.secret')
MANUAL_KEY=$(echo $MFA_SETUP | jq -r '.manual_entry_key')

echo "✓ MFA Setup Complete!"
echo "Secret: $SECRET"
echo "Manual Entry Key: $MANUAL_KEY"
echo ""
echo "⚠️  ADD THIS TO MICROSOFT AUTHENTICATOR:"
echo "   Account: $EMAIL"
echo "   Key: $SECRET"
echo ""

# Step 4: Enable MFA
read -p "Enter the 6-digit code from Microsoft Authenticator: " MFA_CODE

echo ""
echo "Step 4: Enabling MFA..."
ENABLE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/mfa/enable" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"$MFA_CODE\"}")

if echo "$ENABLE_RESPONSE" | jq -e '.backup_codes' > /dev/null; then
    echo "✓ MFA Enabled Successfully!"
    echo ""
    echo "⚠️  BACKUP CODES (Save these!):"
    echo "$ENABLE_RESPONSE" | jq -r '.backup_codes[]'
    echo ""
else
    echo "✗ MFA Enable Failed!"
    echo "$ENABLE_RESPONSE" | jq .
    exit 1
fi

# Step 5: Test MFA Login
echo "Step 5: Testing Login with MFA..."
echo "Logging in with password..."
MFA_LOGIN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "MFA Required: $(echo $MFA_LOGIN | jq -r '.mfa_required')"
echo ""

read -p "Enter the current 6-digit code from Microsoft Authenticator: " MFA_CODE2

echo ""
echo "Verifying MFA code..."
MFA_VERIFY=$(curl -s -X POST "$BASE_URL/api/auth/verify-mfa" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"code\":\"$MFA_CODE2\"}")

if echo "$MFA_VERIFY" | jq -e '.access_token' > /dev/null; then
    echo "✓ Successfully logged in with MFA!"
    echo "MFA Required: $(echo $MFA_VERIFY | jq -r '.mfa_required')"
else
    echo "✗ MFA Verification Failed!"
    echo "$MFA_VERIFY" | jq .
fi

echo ""
echo "========================================="
echo "MFA Test Flow Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "- ✓ MFA setup completed"
echo "- ✓ Microsoft Authenticator configured"
echo "- ✓ Backup codes generated"
echo "- ✓ MFA login tested successfully"
echo ""
```

Save this as `mfa_complete_test.sh` and run it!

---

## Troubleshooting

### "Invalid MFA code"
- ✓ Make sure your phone's time is synchronized (Settings > General > Date & Time > Set Automatically)
- ✓ TOTP codes are time-based and expire every 30 seconds
- ✓ Wait for a fresh code and try again
- ✓ Try using a backup code instead

### "MFA already enabled"
- The user already has MFA enabled
- Disable it first if you want to reconfigure

### Microsoft Authenticator doesn't show codes
- Make sure you selected "Time based" not "Counter based"
- Delete and re-add the account
- Check that the secret was entered correctly

### Lost phone / Can't access authenticator
- Use one of your backup codes
- Contact admin to disable MFA on your account

---

## Security Best Practices

1. **Save Backup Codes Securely**
   - Use a password manager (1Password, LastPass, Bitwarden)
   - Print and store in a safe
   - Never share them

2. **Sync Your Phone's Time**
   - TOTP requires accurate time
   - Enable automatic time sync

3. **Test Backup Codes**
   - Test at least one backup code to ensure they work
   - Regenerate after using several

4. **Multiple Devices**
   - You can add the same account to multiple authenticator apps
   - Use the same secret/QR code on each device

5. **Regular Review**
   - Periodically regenerate backup codes
   - Review MFA status in audit logs

---

## Database Verification

Check MFA status directly in the database:

```bash
PGPASSWORD='Admin@011235' psql -h 35.232.108.201 -p 5432 -U postgres -d mfa \
  -c "SELECT email, mfa_enabled, mfa_secret IS NOT NULL as has_secret FROM users WHERE email = 'admin@startupxyz.com';"
```

Expected output after enabling MFA:
```
        email         | mfa_enabled | has_secret 
----------------------+-------------+------------
 admin@startupxyz.com | t           | t
```

---

## API Endpoints Summary

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/auth/login` | POST | No | Initial login with email/password |
| `/api/auth/verify-mfa` | POST | No | Verify MFA code after login |
| `/api/auth/mfa/setup` | POST | Yes | Generate MFA secret and QR code |
| `/api/auth/mfa/enable` | POST | Yes | Enable MFA with verification code |
| `/api/auth/mfa/disable` | POST | Yes | Disable MFA |
| `/api/auth/mfa/backup-codes` | GET | Yes | Regenerate backup codes |
| `/api/users/me` | GET | Yes | Get current user profile |

---

**🎉 You're all set! Your MFA with Microsoft Authenticator is now fully functional!**
