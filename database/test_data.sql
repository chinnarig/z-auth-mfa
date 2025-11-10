-- Test Data for Voice Agent Platform
-- This script creates sample companies and users for testing
-- Password for all test users: SecurePass123!

-- Clean up existing test data (optional - comment out if you want to keep existing data)
-- DELETE FROM audit_logs WHERE company_id IN (SELECT id FROM companies WHERE domain IN ('techcorp.com', 'startupxyz.com'));
-- DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@techcorp.com' OR email LIKE '%@startupxyz.com');
-- DELETE FROM users WHERE company_id IN (SELECT id FROM companies WHERE domain IN ('techcorp.com', 'startupxyz.com'));
-- DELETE FROM companies WHERE domain IN ('techcorp.com', 'startupxyz.com');

-- ============================================
-- Company 1: TechCorp
-- ============================================

INSERT INTO companies (id, name, domain, is_active, created_at)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'TechCorp', 'techcorp.com', true, NOW())
ON CONFLICT (domain) DO NOTHING;

-- Users for TechCorp
-- Password: SecurePass123! (hashed with bcrypt)
-- Hash generated with: from passlib.context import CryptContext; pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto"); pwd_context.hash("SecurePass123!")

INSERT INTO users (id, company_id, email, hashed_password, full_name, role, is_active, email_verified, mfa_enabled, created_at)
VALUES 
    -- Admin user
    (
        '11111111-1111-1111-1111-111111111112',
        '11111111-1111-1111-1111-111111111111',
        'admin@techcorp.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7YvkV4fZLq', -- SecurePass123!
        'Admin User',
        'admin',
        true,
        true,
        false,
        NOW()
    ),
    -- Manager user
    (
        '11111111-1111-1111-1111-111111111113',
        '11111111-1111-1111-1111-111111111111',
        'manager@techcorp.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7YvkV4fZLq', -- SecurePass123!
        'Manager User',
        'manager',
        true,
        true,
        false,
        NOW()
    ),
    -- Regular user
    (
        '11111111-1111-1111-1111-111111111114',
        '11111111-1111-1111-1111-111111111111',
        'user@techcorp.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7YvkV4fZLq', -- SecurePass123!
        'Regular User',
        'user',
        true,
        true,
        false,
        NOW()
    )
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- Company 2: StartupXYZ
-- ============================================

INSERT INTO companies (id, name, domain, is_active, created_at)
VALUES 
    ('22222222-2222-2222-2222-222222222222', 'StartupXYZ', 'startupxyz.com', true, NOW())
ON CONFLICT (domain) DO NOTHING;

-- Users for StartupXYZ
INSERT INTO users (id, company_id, email, hashed_password, full_name, role, is_active, email_verified, mfa_enabled, created_at)
VALUES 
    -- Admin user with MFA enabled (for testing)
    (
        '22222222-2222-2222-2222-222222222223',
        '22222222-2222-2222-2222-222222222222',
        'admin@startupxyz.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7YvkV4fZLq', -- SecurePass123!
        'Startup Admin',
        'admin',
        true,
        true,
        false, -- Set to false initially; user will set up MFA through the app
        NOW()
    ),
    -- Regular user
    (
        '22222222-2222-2222-2222-222222222224',
        '22222222-2222-2222-2222-222222222222',
        'user@startupxyz.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7YvkV4fZLq', -- SecurePass123!
        'Startup User',
        'user',
        true,
        true,
        false,
        NOW()
    )
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- Sample Audit Logs
-- ============================================

INSERT INTO audit_logs (company_id, user_id, action, ip_address, metadata, created_at)
VALUES 
    (
        '11111111-1111-1111-1111-111111111111',
        '11111111-1111-1111-1111-111111111112',
        'user_login',
        '192.168.1.100',
        '{"email": "admin@techcorp.com", "mfa_used": false}',
        NOW() - INTERVAL '2 hours'
    ),
    (
        '11111111-1111-1111-1111-111111111111',
        '11111111-1111-1111-1111-111111111113',
        'user_login',
        '192.168.1.101',
        '{"email": "manager@techcorp.com", "mfa_used": false}',
        NOW() - INTERVAL '1 hour'
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        '22222222-2222-2222-2222-222222222223',
        'user_registered',
        '192.168.1.102',
        '{"email": "admin@startupxyz.com", "role": "admin"}',
        NOW() - INTERVAL '3 days'
    );

-- ============================================
-- Verification Queries
-- ============================================

SELECT 'Test data loaded successfully!' as status;

SELECT 
    'Companies' as table_name,
    COUNT(*) as record_count
FROM companies
WHERE domain IN ('techcorp.com', 'startupxyz.com')

UNION ALL

SELECT 
    'Users' as table_name,
    COUNT(*) as record_count
FROM users
WHERE email LIKE '%@techcorp.com' OR email LIKE '%@startupxyz.com'

UNION ALL

SELECT 
    'Audit Logs' as table_name,
    COUNT(*) as record_count
FROM audit_logs
WHERE company_id IN (
    SELECT id FROM companies 
    WHERE domain IN ('techcorp.com', 'startupxyz.com')
);

-- Display created users
SELECT 
    c.name as company_name,
    u.full_name,
    u.email,
    u.role,
    u.mfa_enabled,
    u.is_active
FROM users u
JOIN companies c ON u.company_id = c.id
WHERE c.domain IN ('techcorp.com', 'startupxyz.com')
ORDER BY c.name, u.role;

-- ============================================
-- Test Credentials Summary
-- ============================================

SELECT '
========================================
TEST CREDENTIALS
========================================

Company 1: TechCorp (techcorp.com)
-----------------------------------
Admin:
  Email: admin@techcorp.com
  Password: SecurePass123!
  Role: admin

Manager:
  Email: manager@techcorp.com
  Password: SecurePass123!
  Role: manager

User:
  Email: user@techcorp.com
  Password: SecurePass123!
  Role: user


Company 2: StartupXYZ (startupxyz.com)
---------------------------------------
Admin:
  Email: admin@startupxyz.com
  Password: SecurePass123!
  Role: admin

User:
  Email: user@startupxyz.com
  Password: SecurePass123!
  Role: user

========================================
NOTES:
- All users have email_verified = true
- MFA is disabled by default (enable via app)
- All users are active
========================================
' as test_credentials;
