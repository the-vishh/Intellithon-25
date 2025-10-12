@echo off
echo ================================================================================
echo 🚀 STARTING PYTHON ML SERVICE
echo ================================================================================
echo.

cd ml-service

echo Starting Python ML Service on port 8000...
echo.

python3 -m uvicorn app:app --host 0.0.0.0 --port 8000

pause
