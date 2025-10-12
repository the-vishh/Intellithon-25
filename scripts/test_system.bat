@echo off
REM 🧪 PhishGuard AI - End-to-End Testing Script (Windows)

echo ========================================
echo    PhishGuard AI - Complete System Test
echo ========================================
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

REM ==========================================
REM TEST 1: Check Rust API Gateway
REM ==========================================
echo [Test 1] Rust API Gateway
curl -s -o nul -w "%%{http_code}" http://localhost:8080/health > temp_response.txt 2>nul
set /p API_RESPONSE=<temp_response.txt
if "%API_RESPONSE%"=="200" (
    echo [PASS] Rust API is running on port 8080
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Rust API not responding - Start with: cd backend ^&^& cargo run
    set /a TESTS_FAILED+=1
)
del temp_response.txt 2>nul
echo.

REM ==========================================
REM TEST 2: Check Python ML Service
REM ==========================================
echo [Test 2] Python ML Service
curl -s -o nul -w "%%{http_code}" http://localhost:5000/health > temp_response.txt 2>nul
set /p ML_RESPONSE=<temp_response.txt
if "%ML_RESPONSE%"=="200" (
    echo [PASS] Python ML service is running on port 5000
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Python ML service not responding - Start with: python ml_model/api_server.py
    set /a TESTS_FAILED+=1
)
del temp_response.txt 2>nul
echo.

REM ==========================================
REM TEST 3: Test URL Check API
REM ==========================================
echo [Test 3] URL Check Endpoint
curl -s -X POST http://localhost:8080/api/check-url -H "Content-Type: application/json" -d "{\"url\":\"https://google.com\",\"sensitivity_mode\":\"balanced\"}" > temp_result.txt 2>nul
findstr /C:"is_phishing" temp_result.txt >nul
if %ERRORLEVEL%==0 (
    echo [PASS] URL check endpoint responding
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] URL check endpoint not working
    set /a TESTS_FAILED+=1
)
del temp_result.txt 2>nul
echo.

REM ==========================================
REM TEST 4: Check Extension Files
REM ==========================================
echo [Test 4] Extension Files
if exist "manifest.json" (
    echo [PASS] Found manifest.json
    set /a TESTS_PASSED+=1

    findstr /C:"popup-enhanced.html" manifest.json >nul
    if %ERRORLEVEL%==0 (
        echo [PASS] manifest.json uses popup-enhanced.html
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] manifest.json not updated
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Missing manifest.json
    set /a TESTS_FAILED+=1
)

if exist "background.js" (
    echo [PASS] Found background.js
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Missing background.js
    set /a TESTS_FAILED+=1
)

if exist "popup-enhanced.html" (
    echo [PASS] Found popup-enhanced.html
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Missing popup-enhanced.html
    set /a TESTS_FAILED+=1
)

if exist "popup-enhanced.js" (
    echo [PASS] Found popup-enhanced.js
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Missing popup-enhanced.js
    set /a TESTS_FAILED+=1
)

if exist "popup-enhanced.css" (
    echo [PASS] Found popup-enhanced.css
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Missing popup-enhanced.css
    set /a TESTS_FAILED+=1
)
echo.

REM ==========================================
REM TEST 5: Backend Compilation
REM ==========================================
echo [Test 5] Backend Compilation
cd backend 2>nul
if %ERRORLEVEL%==0 (
    cargo check --quiet >nul 2>&1
    if %ERRORLEVEL%==0 (
        echo [PASS] Backend compiles successfully
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Backend has compilation errors
        set /a TESTS_FAILED+=1
    )
    cd ..
) else (
    echo [WARN] Backend directory not found
)
echo.

REM ==========================================
REM SUMMARY
REM ==========================================
echo ==========================================
echo            TEST SUMMARY
echo ==========================================
echo Passed: %TESTS_PASSED%
echo Failed: %TESTS_FAILED%
echo.

if %TESTS_FAILED%==0 (
    echo [SUCCESS] ALL TESTS PASSED! System is ready!
    echo.
    echo Next steps:
    echo 1. Load extension in Chrome ^(chrome://extensions/^)
    echo 2. Enable Developer mode
    echo 3. Click "Load unpacked" and select Extension folder
    echo 4. Visit a website to test
    echo 5. Open extension popup to see real-time analytics
    echo.
    pause
    exit /b 0
) else (
    echo [WARNING] SOME TESTS FAILED
    echo.
    echo To fix:
    echo - Start Rust API: cd backend ^&^& cargo run
    echo - Start Python ML: cd ml_model ^&^& python api_server.py
    echo - Start PostgreSQL and Redis if needed
    echo.
    pause
    exit /b 1
)
