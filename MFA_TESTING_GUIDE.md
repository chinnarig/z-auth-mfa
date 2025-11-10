# MFA Testing - Quick Start Guide

## ✅ All Issues Fixed!

The backend API is now fully functional. Here's how to test everything:

---

## 🚀 Quick Start

### 1. Make sure the backend server is running:

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### 2. Choose Your Testing Method:

#### Option A: **Manual Entry (RECOMMENDED - QR scanning issues)**

```bash
./test_mfa_manual.sh
```

This script will:
- ✅ Login automatically
- ✅ Generate MFA secret
- ✅ Show you exactly what to enter in Microsoft Authenticator
- ✅ Guide you step-by-step
- ✅ Test the full MFA flow
- ✅ Save your backup codes

**Perfect if:** QR code scanning doesn't work

---

#### Option B: **Complete Flow (with QR code)**

```bash
./mfa_complete_test.sh
```

This script will:
- ✅ Test all API endpoints
- ✅ Generate QR code and open in browser
- ✅ Enable MFA
- ✅ Test login with MFA
- ✅ Test backup codes

**Perfect if:** You want to see the full flow including QR code

---

## 📱 Adding to Microsoft Authenticator

### If QR Code Doesn't Scan:

1. **Open Microsoft Authenticator**
2. Tap **"+"** (top right corner)
3. Select **"Other account"**
4. Choose **"or enter code manually"** (small link at bottom)
5. Enter:
   - **Account name:** `admin@startupxyz.com`
   - **Key:** The secret from the script (e.g., `773JMPNKW5TFS35E...`)
   - **Type:** **Time based** (important!)
6. Tap **"Done"**

### Common Issues:

❌ **"Invalid code"**
- ✅ Make sure phone time is synchronized (Settings > Date & Time > Automatic)
- ✅ Wait for a fresh code (they expire every 30 seconds)
- ✅ Try again with the next code

❌ **QR code won't scan**
- ✅ Use manual entry instead (it's actually easier!)
- ✅ Make sure you copy the full secret without spaces

❌ **Can't find "enter code manually"**
- ✅ It's usually a small link at the bottom of the QR scanner
- ✅ Some versions say "Can't scan?" or "Enter key"

---

## 🧪 Test Accounts

All test accounts use password: **`SecurePass123!`**

| Email | Role | Company | MFA Status |
|-------|------|---------|------------|
| `admin@techcorp.com` | Admin | TechCorp | Not enabled |
| `manager@techcorp.com` | Manager | TechCorp | Not enabled |
| `user@techcorp.com` | User | TechCorp | Not enabled |
| `admin@startupxyz.com` | Admin | StartupXYZ | Not enabled |
| `user@startupxyz.com` | User | StartupXYZ | Not enabled |

---

## 📚 Documentation

Detailed guides available:

1. **`MFA_MANUAL_SETUP.md`** - Step-by-step manual entry guide
2. **`MFA_TEST_FLOW.md`** - Complete test flow documentation
3. **`API_TESTS.md`** - All API endpoint tests
4. **`API_DOCUMENTATION.md`** - Full API reference

---

## 🔍 Manual Testing (Command Line)

### Step 1: Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }' | jq .
```

Save the `access_token` from the response.

### Step 2: Setup MFA

```bash
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/auth/mfa/setup \
  -H "Authorization: Bearer $TOKEN" | jq .
```

Copy the `secret` value.

### Step 3: Add to Microsoft Authenticator

- Account name: `admin@startupxyz.com`
- Key: Your secret (no spaces)
- Type: Time based

### Step 4: Enable MFA

```bash
# Replace 123456 with code from authenticator
curl -X POST http://localhost:8000/api/auth/mfa/enable \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}' | jq .
```

### Step 5: Test MFA Login

```bash
# Step 5a: Login with password
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "password": "SecurePass123!"
  }' | jq .

# You'll get mfa_required: true

# Step 5b: Verify with MFA code
curl -X POST http://localhost:8000/api/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@startupxyz.com",
    "code": "123456"
  }' | jq .
```

---

## ✨ What's Working

✅ Database connection to GCP PostgreSQL  
✅ User authentication  
✅ JWT token generation  
✅ MFA secret generation  
✅ QR code generation  
✅ Microsoft Authenticator compatibility  
✅ Backup codes generation  
✅ MFA verification  
✅ All API endpoints  
✅ Row-Level Security (RLS)  
✅ Audit logging  

---

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Start server
cd backend
uvicorn app.main:app --reload
```

### Database connection issues

Check your `.env` file:
```bash
cd backend
cat .env
```

Should contain:
```
DATABASE_URL=postgresql://postgres:Admin%40011235@35.232.108.201:5432/mfa
```

### MFA codes not working

1. **Sync phone time:**
   - iPhone: Settings > General > Date & Time > Set Automatically (ON)
   - Android: Settings > System > Date & time > Automatic (ON)

2. **Wait for fresh code:**
   - Codes change every 30 seconds
   - Don't reuse old codes

3. **Verify secret:**
   - Make sure you entered the full secret
   - No spaces in the secret when entering manually

### Can't install dependencies

```bash
cd backend

# Upgrade pip
python3 -m pip install --upgrade pip

# Install requirements
pip3 install -r requirements.txt
```

---

## 📞 Support

If you're still having issues:

1. **Check backend logs** - Look for error messages when calling APIs
2. **Test with curl** - Try manual commands to isolate the issue
3. **Verify database** - Make sure users exist and passwords are correct
4. **Check .env file** - Ensure all environment variables are set

---

## 🎯 Next Steps

Once MFA is working:

1. ✅ Test all user roles (admin, manager, user)
2. ✅ Test backup codes
3. ✅ Test token refresh
4. ✅ Test logout
5. ✅ Review audit logs in database
6. ✅ Test with frontend application

---

## 📝 Quick Reference

### Start Backend:
```bash
cd backend && uvicorn app.main:app --reload
```

### Run MFA Test:
```bash
./test_mfa_manual.sh
```

### Check Database:
```bash
PGPASSWORD='Admin@011235' psql -h 35.232.108.201 -p 5432 -U postgres -d mfa \
  -c "SELECT email, mfa_enabled FROM users;"
```

### Reset MFA (if needed):
```bash
PGPASSWORD='Admin@011235' psql -h 35.232.108.201 -p 5432 -U postgres -d mfa \
  -c "UPDATE users SET mfa_enabled = false, mfa_secret = NULL, mfa_backup_codes = NULL WHERE email = 'admin@startupxyz.com';"
```

---

**🎉 Everything is ready! Run `./test_mfa_manual.sh` to get started!**
