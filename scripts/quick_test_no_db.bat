@echo off
REM Quick Test Without Database - PhishGuard
echo ========================================
echo PhishGuard - Quick Test (No Database)
echo ========================================
echo.

echo Step 1: Check if API port is available...
netstat -ano | findstr :8080 > nul
if %errorlevel% == 0 (
    echo WARNING: Port 8080 is already in use!
    echo Please stop the service or choose a different port.
    pause
    exit /b 1
) else (
    echo OK: Port 8080 is available
)

echo.
echo Step 2: Starting Rust API (without database)...
echo This may take 2-3 minutes to compile...
echo.

cd backend
start "PhishGuard API" cargo run --release

echo.
echo Waiting for API to start (30 seconds)...
timeout /t 30 /nobreak > nul

echo.
echo Step 3: Testing API health...
curl -s http://localhost:8080/health

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo SUCCESS! API is running
    echo ========================================
    echo.
    echo Next Steps:
    echo 1. Load extension in Chrome: chrome://extensions/
    echo 2. Enable Developer Mode
    echo 3. Click "Load unpacked" and select Extension folder
    echo 4. Visit any website to test!
    echo.
    echo Note: Analytics won't be saved without database.
    echo To set up database, see MANUAL_TESTING_GUIDE.md
    echo ========================================
) else (
    echo.
    echo ========================================
    echo WARNING: API may not be ready yet
    echo ========================================
    echo Check the API terminal window for errors.
    echo If you see PostgreSQL errors, follow these steps:
    echo.
    echo Option 1: Install PostgreSQL and run setup_database.sql
    echo Option 2: Continue without database (analytics disabled)
    echo.
    echo See MANUAL_TESTING_GUIDE.md for full instructions
    echo ========================================
)

echo.
pause
