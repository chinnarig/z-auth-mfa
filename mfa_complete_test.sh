#!/bin/bash

# Complete MFA Test Flow Script
# Tests the entire MFA setup and login flow

BASE_URL="http://localhost:8000"
EMAIL="admin@startupxyz.com"
PASSWORD="SecurePass123!"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================="
echo "🔐 Complete MFA Test Flow"
echo "========================================="
echo ""

# Step 1: Initial Login (No MFA)
echo -e "${BLUE}Step 1: Initial Login (No MFA)${NC}"
echo "--------------------------------------"
LOGIN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo "$LOGIN" | jq -r '.access_token')
MFA_REQUIRED=$(echo "$LOGIN" | jq -r '.mfa_required')

if [ "$ACCESS_TOKEN" != "null" ] && [ "$ACCESS_TOKEN" != "" ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "  MFA Required: $MFA_REQUIRED"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN" | jq .
    exit 1
fi
echo ""

# Step 2: Check Profile
echo -e "${BLUE}Step 2: Check User Profile & MFA Status${NC}"
echo "--------------------------------------"
PROFILE=$(curl -s -X GET "$BASE_URL/api/users/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

MFA_ENABLED=$(echo "$PROFILE" | jq -r '.mfa_enabled')
USER_EMAIL=$(echo "$PROFILE" | jq -r '.email')
USER_NAME=$(echo "$PROFILE" | jq -r '.full_name')
USER_ROLE=$(echo "$PROFILE" | jq -r '.role')

if [ "$USER_EMAIL" != "null" ]; then
    echo -e "${GREEN}✓ Profile retrieved${NC}"
    echo "  Name: $USER_NAME"
    echo "  Email: $USER_EMAIL"
    echo "  Role: $USER_ROLE"
    echo "  MFA Enabled: $MFA_ENABLED"
else
    echo -e "${RED}✗ Failed to retrieve profile${NC}"
    echo "$PROFILE" | jq .
fi
echo ""

# Step 3: Setup MFA
echo -e "${BLUE}Step 3: Setup MFA${NC}"
echo "--------------------------------------"
MFA_SETUP=$(curl -s -X POST "$BASE_URL/api/auth/mfa/setup" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

SECRET=$(echo "$MFA_SETUP" | jq -r '.secret')
MANUAL_KEY=$(echo "$MFA_SETUP" | jq -r '.manual_entry_key')
QR_CODE=$(echo "$MFA_SETUP" | jq -r '.qr_code')

if [ "$SECRET" != "null" ] && [ "$SECRET" != "" ]; then
    echo -e "${GREEN}✓ MFA Setup Complete!${NC}"
    echo ""
    echo -e "${YELLOW}================================================${NC}"
    echo -e "${YELLOW}  ADD THIS TO MICROSOFT AUTHENTICATOR${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo ""
    echo -e "  ${BLUE}Account Name:${NC} $EMAIL"
    echo -e "  ${BLUE}Secret Key:${NC}   $SECRET"
    echo -e "  ${BLUE}Manual Entry:${NC} $MANUAL_KEY"
    echo -e "  ${BLUE}Type:${NC}         Time based"
    echo ""
    echo -e "${YELLOW}Steps to add:${NC}"
    echo "  1. Open Microsoft Authenticator on your phone"
    echo "  2. Tap '+' to add account"
    echo "  3. Select 'Other account (Google, Facebook, etc.)'"
    echo "  4. Choose 'Enter code manually'"
    echo "  5. Enter:"
    echo "     - Account name: $EMAIL"
    echo "     - Your key: $SECRET"
    echo "     - Account type: Time based"
    echo "  6. Tap 'Finish'"
    echo ""
    
    # Save QR code to file
    echo "$QR_CODE" > /tmp/mfa_qr_data.txt
    
    # Create HTML file for QR code
    cat > /tmp/mfa_qr_code.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>MFA QR Code</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            margin: 0 auto;
        }
        img { 
            width: 300px; 
            height: 300px; 
            border: 3px solid #667eea;
            border-radius: 10px;
            padding: 10px;
            background: white;
        }
        h1 { 
            color: #333; 
            margin-top: 0;
        }
        .account { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
            border-left: 4px solid #667eea;
        }
        .account strong {
            color: #667eea;
        }
        .instructions {
            text-align: left;
            margin-top: 20px;
            padding: 20px;
            background: #e8f4fd;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
        }
        .instructions h3 {
            margin-top: 0;
            color: #2196F3;
        }
        .instructions li {
            margin: 10px 0;
            line-height: 1.6;
        }
        .secret {
            font-family: 'Courier New', monospace;
            background: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 16px;
            letter-spacing: 2px;
            border: 1px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 MFA Setup</h1>
        <p style="color: #666;">Scan this QR Code with Microsoft Authenticator</p>
        
        <img src="$QR_CODE" alt="MFA QR Code">
        
        <div class="account">
            <strong>Account:</strong> $EMAIL<br>
            <strong>Issuer:</strong> Z-Auth MFA Platform
        </div>
        
        <div class="secret">
            <strong>Manual Entry Key:</strong><br>
            $MANUAL_KEY
        </div>
        
        <div class="instructions">
            <h3>📱 Setup Instructions:</h3>
            <ol>
                <li>Open <strong>Microsoft Authenticator</strong></li>
                <li>Tap <strong>"+"</strong> (top right)</li>
                <li>Select <strong>"Other account"</strong></li>
                <li>Choose <strong>"Scan a QR code"</strong> OR <strong>"Enter code manually"</strong></li>
                <li>Scan the QR above or enter the key manually</li>
                <li>Done! You'll see 6-digit codes updating every 30 seconds</li>
            </ol>
        </div>
    </div>
</body>
</html>
EOF
    
    echo -e "${YELLOW}QR Code saved to: /tmp/mfa_qr_code.html${NC}"
    echo -e "${YELLOW}Opening in browser...${NC}"
    open /tmp/mfa_qr_code.html 2>/dev/null || echo "  (Please open /tmp/mfa_qr_code.html manually)"
    echo ""
    
else
    echo -e "${RED}✗ MFA Setup failed${NC}"
    echo "$MFA_SETUP" | jq .
    exit 1
fi

# Step 4: Enable MFA
echo -e "${BLUE}Step 4: Enable MFA${NC}"
echo "--------------------------------------"
echo -e "${YELLOW}Please add the account to Microsoft Authenticator first!${NC}"
echo ""
read -p "Enter the 6-digit code from Microsoft Authenticator: " MFA_CODE

if [ -z "$MFA_CODE" ]; then
    echo -e "${RED}✗ No code entered. Exiting.${NC}"
    exit 1
fi

ENABLE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/mfa/enable" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"$MFA_CODE\"}")

if echo "$ENABLE_RESPONSE" | jq -e '.backup_codes' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MFA Enabled Successfully!${NC}"
    echo ""
    echo -e "${YELLOW}================================================${NC}"
    echo -e "${YELLOW}  BACKUP CODES - SAVE THESE SECURELY!${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo ""
    echo "$ENABLE_RESPONSE" | jq -r '.backup_codes[]' | while read code; do
        echo "  📝 $code"
    done
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC}"
    echo "  - Each code can only be used ONCE"
    echo "  - Store them in a password manager"
    echo "  - Use them if you lose your phone"
    echo ""
    
    # Save backup codes to file
    echo "$ENABLE_RESPONSE" | jq -r '.backup_codes[]' > /tmp/mfa_backup_codes.txt
    echo -e "${GREEN}Backup codes saved to: /tmp/mfa_backup_codes.txt${NC}"
    echo ""
else
    echo -e "${RED}✗ MFA Enable Failed!${NC}"
    echo "$ENABLE_RESPONSE" | jq .
    echo ""
    echo -e "${YELLOW}Possible reasons:${NC}"
    echo "  - Invalid code (codes expire every 30 seconds)"
    echo "  - Phone time not synchronized"
    echo "  - MFA already enabled"
    exit 1
fi

# Step 5: Test MFA Login
echo -e "${BLUE}Step 5: Test Login WITH MFA${NC}"
echo "--------------------------------------"
echo "Logging out and testing MFA login flow..."
echo ""

echo "5a. Logging in with password..."
MFA_LOGIN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

MFA_REQUIRED_LOGIN=$(echo "$MFA_LOGIN" | jq -r '.mfa_required')

if [ "$MFA_REQUIRED_LOGIN" == "true" ]; then
    echo -e "${GREEN}✓ MFA is now required for login${NC}"
    echo ""
else
    echo -e "${RED}✗ MFA should be required but isn't${NC}"
    exit 1
fi

read -p "5b. Enter the CURRENT 6-digit code from Microsoft Authenticator: " MFA_CODE2

if [ -z "$MFA_CODE2" ]; then
    echo -e "${RED}✗ No code entered. Exiting.${NC}"
    exit 1
fi

MFA_VERIFY=$(curl -s -X POST "$BASE_URL/api/auth/verify-mfa" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"code\":\"$MFA_CODE2\"}")

NEW_ACCESS_TOKEN=$(echo "$MFA_VERIFY" | jq -r '.access_token')

if [ "$NEW_ACCESS_TOKEN" != "null" ] && [ "$NEW_ACCESS_TOKEN" != "" ]; then
    echo -e "${GREEN}✓ Successfully logged in with MFA!${NC}"
    echo "  Access token received"
    echo "  MFA verification successful"
else
    echo -e "${RED}✗ MFA Verification Failed!${NC}"
    echo "$MFA_VERIFY" | jq .
    exit 1
fi
echo ""

# Step 6: Verify profile with new token
echo -e "${BLUE}Step 6: Verify Profile After MFA Login${NC}"
echo "--------------------------------------"
NEW_PROFILE=$(curl -s -X GET "$BASE_URL/api/users/me" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN")

if echo "$NEW_PROFILE" | jq -e '.email' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Profile access with MFA token successful${NC}"
    echo "  MFA Enabled: $(echo "$NEW_PROFILE" | jq -r '.mfa_enabled')"
else
    echo -e "${RED}✗ Failed to access profile${NC}"
fi
echo ""

# Step 7: Test backup code (optional)
echo -e "${BLUE}Step 7: Test Backup Code (Optional)${NC}"
echo "--------------------------------------"
read -p "Do you want to test a backup code? (y/n): " TEST_BACKUP

if [ "$TEST_BACKUP" == "y" ] || [ "$TEST_BACKUP" == "Y" ]; then
    echo ""
    echo "Available backup codes are in: /tmp/mfa_backup_codes.txt"
    read -p "Enter one of your backup codes: " BACKUP_CODE
    
    # Login again
    LOGIN_FOR_BACKUP=$(curl -s -X POST "$BASE_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
    
    # Verify with backup code
    BACKUP_VERIFY=$(curl -s -X POST "$BASE_URL/api/auth/verify-mfa" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"$EMAIL\",\"code\":\"$BACKUP_CODE\"}")
    
    if echo "$BACKUP_VERIFY" | jq -e '.access_token' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backup code login successful!${NC}"
        echo "  ⚠️  This backup code is now used and cannot be used again"
    else
        echo -e "${RED}✗ Backup code verification failed${NC}"
        echo "$BACKUP_VERIFY" | jq .
    fi
    echo ""
fi

# Summary
echo ""
echo "========================================="
echo "🎉 MFA Test Flow Complete!"
echo "========================================="
echo ""
echo -e "${GREEN}Summary:${NC}"
echo "  ✓ Initial login successful"
echo "  ✓ MFA setup completed"
echo "  ✓ QR code generated and displayed"
echo "  ✓ MFA enabled with Microsoft Authenticator"
echo "  ✓ Backup codes generated and saved"
echo "  ✓ MFA login flow tested successfully"
echo "  ✓ Profile access verified"
echo ""
echo -e "${YELLOW}Files created:${NC}"
echo "  📄 /tmp/mfa_qr_code.html - QR code for scanning"
echo "  📄 /tmp/mfa_backup_codes.txt - Your backup codes"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Save your backup codes in a secure location"
echo "  2. Test logging in with Microsoft Authenticator"
echo "  3. Keep your phone time synchronized"
echo ""
echo -e "${GREEN}Your account ($EMAIL) is now protected with MFA!${NC}"
echo ""
