@echo off
REM PhishGuard Database Setup Script for Windows
REM Run this script and enter your PostgreSQL password when prompted

SET PGPATH="C:\Program Files\PostgreSQL\17\bin\psql.exe"

echo ========================================
echo PhishGuard Database Setup
echo ========================================
echo.
echo This will:
echo 1. Create 'phishguard' database
echo 2. Create 'phishguard_user' user
echo 3. Grant necessary privileges
echo.
echo Please enter your PostgreSQL 'postgres' user password when prompted.
echo.

%PGPATH% -U postgres -f setup_database.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Database created.
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Update backend/.env with DATABASE_URL
    echo 2. Run migrations: %PGPATH% -U phishguard_user -d phishguard -f backend/migrations/2025-10-10-000001_create_user_analytics/up.sql
    echo 3. Restart the API
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Database setup failed
    echo ========================================
    echo.
    echo Common issues:
    echo - Wrong password for 'postgres' user
    echo - PostgreSQL service not running
    echo - Port 5432 already in use
    echo.
    echo To start PostgreSQL service:
    echo - Open Services (services.msc)
    echo - Find "postgresql-x64-17"
    echo - Click "Start"
    echo.
)

pause
