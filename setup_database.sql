-- PhishGuard Database Setup Script
-- Run this with: psql -U postgres -f setup_database.sql

-- Create database
CREATE DATABASE phishguard;

-- Create user
CREATE USER phishguard_user WITH PASSWORD 'phishguard123';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE phishguard TO phishguard_user;

-- Connect to the database
\c phishguard

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO phishguard_user;

-- Verify setup
\dt
\du

-- Success message
SELECT 'Database setup complete! Run migrations next.' AS status;
