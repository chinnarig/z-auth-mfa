-- Migration: Add address, phone numbers, and api_key to companies table
-- Date: 2025-11-11
-- Description: Adds contact information and API key fields to companies

-- Add new columns to companies table
ALTER TABLE companies 
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS phone_number_1 VARCHAR(20),
ADD COLUMN IF NOT EXISTS phone_number_2 VARCHAR(20),
ADD COLUMN IF NOT EXISTS api_key VARCHAR(255) UNIQUE;

-- Add index on api_key for faster lookups
CREATE INDEX IF NOT EXISTS idx_companies_api_key ON companies(api_key);

-- Add comments for new columns
COMMENT ON COLUMN companies.address IS 'Company physical address';
COMMENT ON COLUMN companies.phone_number_1 IS 'Primary contact phone number';
COMMENT ON COLUMN companies.phone_number_2 IS 'Secondary contact phone number';
COMMENT ON COLUMN companies.api_key IS 'Unique API key for external integrations';

SELECT 'Migration completed: Added address, phone_number_1, phone_number_2, and api_key to companies table' as status;
