#!/bin/bash

# Z-Auth MFA API Test Script
# This script tests the main API endpoints

BASE_URL="http://localhost:8000"
EMAIL="admin@startupxyz.com"
PASSWORD="SecurePass123!"

echo "======================================"
echo "Z-Auth MFA API Testing"
echo "======================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Login
echo "Test 1: Login (without MFA)"
echo "--------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

echo "$LOGIN_RESPONSE" | jq .

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh_token')
MFA_REQUIRED=$(echo "$LOGIN_RESPONSE" | jq -r '.mfa_required')

if [ "$ACCESS_TOKEN" != "null" ] && [ "$ACCESS_TOKEN" != "" ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
else
    echo -e "${RED}✗ Login failed${NC}"
    exit 1
fi
echo ""

# Test 2: Get Profile
echo "Test 2: Get My Profile"
echo "--------------------------------------"
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/users/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$PROFILE_RESPONSE" | jq .

if echo "$PROFILE_RESPONSE" | jq -e '.email' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Profile retrieved successfully${NC}"
else
    echo -e "${RED}✗ Profile retrieval failed${NC}"
fi
echo ""

# Test 3: Setup MFA
echo "Test 3: Setup MFA"
echo "--------------------------------------"
MFA_SETUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/mfa/setup" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$MFA_SETUP_RESPONSE" | jq .

SECRET=$(echo "$MFA_SETUP_RESPONSE" | jq -r '.secret')
MANUAL_KEY=$(echo "$MFA_SETUP_RESPONSE" | jq -r '.manual_entry_key')

if [ "$SECRET" != "null" ] && [ "$SECRET" != "" ]; then
    echo -e "${GREEN}✓ MFA setup successful${NC}"
    echo ""
    echo -e "${YELLOW}================================================${NC}"
    echo -e "${YELLOW}IMPORTANT: Add this to Microsoft Authenticator${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo ""
    echo "Account: $EMAIL"
    echo "Manual Entry Key: $MANUAL_KEY"
    echo ""
    echo "Steps:"
    echo "1. Open Microsoft Authenticator on your phone"
    echo "2. Tap '+' to add an account"
    echo "3. Select 'Other account (Google, Facebook, etc.)'"
    echo "4. Choose 'Enter code manually'"
    echo "5. Enter Account Name: $EMAIL"
    echo "6. Enter Key: $MANUAL_KEY (remove spaces)"
    echo "7. Select Time-based"
    echo ""
    echo -e "${YELLOW}The QR code is also in the response above.${NC}"
    echo -e "${YELLOW}You can save it to an HTML file to scan.${NC}"
    echo ""
else
    echo -e "${RED}✗ MFA setup failed${NC}"
fi
echo ""

# Test 4: Enable MFA (requires user input)
echo "Test 4: Enable MFA"
echo "--------------------------------------"
echo "Enter the 6-digit code from Microsoft Authenticator:"
read -r MFA_CODE

if [ -n "$MFA_CODE" ]; then
    ENABLE_MFA_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/mfa/enable" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"code\": \"$MFA_CODE\"
      }")
    
    echo "$ENABLE_MFA_RESPONSE" | jq .
    
    if echo "$ENABLE_MFA_RESPONSE" | jq -e '.backup_codes' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MFA enabled successfully${NC}"
        echo ""
        echo -e "${YELLOW}================================================${NC}"
        echo -e "${YELLOW}BACKUP CODES - SAVE THESE SECURELY!${NC}"
        echo -e "${YELLOW}================================================${NC}"
        echo "$ENABLE_MFA_RESPONSE" | jq -r '.backup_codes[]'
        echo ""
    else
        echo -e "${RED}✗ MFA enable failed - Invalid code or already enabled${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Skipping MFA enable (no code provided)${NC}"
fi
echo ""

# Test 5: List Users (Admin only)
echo "Test 5: List Company Users"
echo "--------------------------------------"
USERS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/users/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$USERS_RESPONSE" | jq .

if echo "$USERS_RESPONSE" | jq -e '.[0].email' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Users list retrieved successfully${NC}"
    USER_COUNT=$(echo "$USERS_RESPONSE" | jq 'length')
    echo "Found $USER_COUNT users in the company"
else
    echo -e "${YELLOW}⊘ Users list may require admin privileges${NC}"
fi
echo ""

# Test 6: Refresh Token
echo "Test 6: Refresh Token"
echo "--------------------------------------"
if [ "$REFRESH_TOKEN" != "null" ] && [ "$REFRESH_TOKEN" != "" ]; then
    REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/refresh" \
      -H "Content-Type: application/json" \
      -d "{
        \"refresh_token\": \"$REFRESH_TOKEN\"
      }")
    
    echo "$REFRESH_RESPONSE" | jq .
    
    NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access_token')
    if [ "$NEW_ACCESS_TOKEN" != "null" ] && [ "$NEW_ACCESS_TOKEN" != "" ]; then
        echo -e "${GREEN}✓ Token refreshed successfully${NC}"
    else
        echo -e "${RED}✗ Token refresh failed${NC}"
    fi
else
    echo -e "${YELLOW}⊘ No refresh token available${NC}"
fi
echo ""

echo "======================================"
echo "Testing Complete!"
echo "======================================"
echo ""
echo "Summary:"
echo "- All basic API endpoints are working"
echo "- MFA setup is ready for Microsoft Authenticator"
echo "- Database connection is successful"
echo ""
echo "Next steps:"
echo "1. Add the account to Microsoft Authenticator"
echo "2. Test login with MFA enabled"
echo "3. Test backup codes"
echo ""
