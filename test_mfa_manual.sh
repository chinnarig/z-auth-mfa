#!/bin/bash

# Simple MFA Manual Entry Test
# For when QR code scanning doesn't work

EMAIL="admin@startupxyz.com"
PASSWORD="SecurePass123!"
BASE_URL="http://localhost:8000"

echo ""
echo "================================================"
echo "🔐 MFA Manual Setup (No QR Code Needed)"
echo "================================================"
echo ""

# Step 1: Login
echo "Step 1: Logging in..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "✗ Login failed! Is the server running?"
    echo "Start server with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

echo "✓ Login successful"
echo ""

# Step 2: Setup MFA
echo "Step 2: Getting MFA secret..."
MFA_SETUP=$(curl -s -X POST "$BASE_URL/api/auth/mfa/setup" \
  -H "Authorization: Bearer $TOKEN")

SECRET=$(echo "$MFA_SETUP" | jq -r '.secret')
MANUAL_KEY=$(echo "$MFA_SETUP" | jq -r '.manual_entry_key')

if [ "$SECRET" == "null" ] || [ -z "$SECRET" ]; then
    echo "✗ Failed to setup MFA"
    echo "$MFA_SETUP" | jq .
    exit 1
fi

echo "✓ MFA secret generated"
echo ""

# Display setup information
echo "================================================"
echo "ADD TO MICROSOFT AUTHENTICATOR"
echo "================================================"
echo ""
echo "Open Microsoft Authenticator on your phone and:"
echo ""
echo "1. Tap '+' (top right)"
echo "2. Select 'Other account'"
echo "3. Choose 'or enter code manually' (at bottom)"
echo "4. Enter these details:"
echo ""
echo "   Account name:"
echo "   └─> $EMAIL"
echo ""
echo "   Key (copy this exactly, NO SPACES):"
echo "   ┌────────────────────────────────┐"
echo "   │ $SECRET │"
echo "   └────────────────────────────────┘"
echo ""
echo "   Or with spaces (easier to read):"
echo "   └─> $MANUAL_KEY"
echo ""
echo "   Type of password:"
echo "   └─> Time based"
echo ""
echo "5. Tap 'Done'"
echo ""
echo "================================================"
echo ""

read -p "Have you added it to Microsoft Authenticator? (y/n): " ADDED

if [ "$ADDED" != "y" ] && [ "$ADDED" != "Y" ]; then
    echo ""
    echo "Please add the account first, then run this script again."
    echo "Your secret key is: $SECRET"
    exit 0
fi

echo ""
echo "Step 3: Testing the code..."
echo ""

# Try to enable MFA
for i in 1 2 3; do
    echo "Attempt $i of 3:"
    read -p "Enter the 6-digit code from Microsoft Authenticator: " MFA_CODE
    
    if [ -z "$MFA_CODE" ]; then
        echo "✗ No code entered"
        continue
    fi
    
    echo "Verifying..."
    ENABLE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/mfa/enable" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"code\":\"$MFA_CODE\"}")
    
    if echo "$ENABLE_RESPONSE" | jq -e '.backup_codes' > /dev/null 2>&1; then
        echo ""
        echo "================================================"
        echo "✅ SUCCESS! MFA IS NOW ENABLED!"
        echo "================================================"
        echo ""
        echo "🔑 BACKUP CODES (SAVE THESE SECURELY!):"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$ENABLE_RESPONSE" | jq -r '.backup_codes[]' | while read code; do
            echo "   $code"
        done
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "⚠️  Important:"
        echo "   - Save these codes in a password manager"
        echo "   - Each code can only be used once"
        echo "   - Use them if you lose your phone"
        echo ""
        echo "Backup codes saved to: /tmp/mfa_backup_codes.txt"
        echo "$ENABLE_RESPONSE" | jq -r '.backup_codes[]' > /tmp/mfa_backup_codes.txt
        echo ""
        
        # Test the MFA login
        echo "Step 4: Testing MFA login..."
        echo ""
        
        read -p "Do you want to test the full MFA login flow? (y/n): " TEST_LOGIN
        
        if [ "$TEST_LOGIN" == "y" ] || [ "$TEST_LOGIN" == "Y" ]; then
            echo ""
            echo "Logging in with password..."
            LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
              -H "Content-Type: application/json" \
              -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
            
            MFA_REQUIRED=$(echo "$LOGIN_RESPONSE" | jq -r '.mfa_required')
            
            if [ "$MFA_REQUIRED" == "true" ]; then
                echo "✓ MFA is now required for login"
                echo ""
                read -p "Enter current code from Microsoft Authenticator: " TEST_CODE
                
                echo "Verifying MFA code..."
                VERIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/verify-mfa" \
                  -H "Content-Type: application/json" \
                  -d "{\"email\":\"$EMAIL\",\"code\":\"$TEST_CODE\"}")
                
                if echo "$VERIFY_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
                    echo ""
                    echo "✅ MFA LOGIN SUCCESSFUL!"
                    echo ""
                    echo "Your account is now fully protected with MFA!"
                else
                    echo ""
                    echo "✗ MFA verification failed, but MFA is enabled."
                    echo "Try again with a fresh code."
                fi
            fi
        fi
        
        echo ""
        echo "================================================"
        echo "🎉 Setup Complete!"
        echo "================================================"
        echo ""
        echo "Next time you login:"
        echo "1. Enter email and password"
        echo "2. Open Microsoft Authenticator"
        echo "3. Enter the 6-digit code"
        echo "4. You're in!"
        echo ""
        
        exit 0
    else
        ERROR_MSG=$(echo "$ENABLE_RESPONSE" | jq -r '.detail // .message // "Unknown error"')
        echo "✗ Failed: $ERROR_MSG"
        echo ""
        
        if [ $i -lt 3 ]; then
            echo "Troubleshooting tips:"
            echo "  - Make sure your phone's time is synchronized"
            echo "  - Wait for a fresh code (codes change every 30 seconds)"
            echo "  - Check that you entered the secret correctly"
            echo ""
        fi
    fi
done

echo ""
echo "================================================"
echo "❌ Failed to enable MFA after 3 attempts"
echo "================================================"
echo ""
echo "Possible issues:"
echo ""
echo "1. Phone time not synchronized:"
echo "   iPhone: Settings > General > Date & Time > Set Automatically"
echo "   Android: Settings > System > Date & time > Automatic date & time"
echo ""
echo "2. Secret entered incorrectly:"
echo "   Your secret: $SECRET"
echo "   Make sure there are NO SPACES when entering"
echo ""
echo "3. Using wrong account type:"
echo "   Must be 'Time based' not 'Counter based'"
echo ""
echo "4. Code expired:"
echo "   Wait for a fresh code before entering"
echo ""
echo "Try again by running: ./test_mfa_manual.sh"
echo ""
