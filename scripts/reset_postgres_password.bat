@echo off
REM PostgreSQL Password Reset - Windows Batch Version
REM Run this as Administrator

echo ========================================
echo PostgreSQL Password Reset
echo ========================================
echo.
echo IMPORTANT: You must run this as Administrator!
echo Right-click this file and select "Run as Administrator"
echo.
pause

SET PG_DATA=C:\Program Files\PostgreSQL\17\data
SET PG_HBA=%PG_DATA%\pg_hba.conf
SET PG_HBA_BACKUP=%PG_HBA%.backup
SET PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"

echo Step 1: Backing up configuration...
copy "%PG_HBA%" "%PG_HBA_BACKUP%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cannot backup file. Are you running as Administrator?
    pause
    exit /b 1
)
echo Done!
echo.

echo Step 2: Modifying authentication...
powershell -Command "(gc '%PG_HBA%') -replace 'scram-sha-256', 'trust' -replace 'md5', 'trust' | Out-File -encoding ASCII '%PG_HBA%'"
echo Done!
echo.

echo Step 3: Restarting PostgreSQL...
net stop postgresql-x64-17
timeout /t 3 /nobreak >nul
net start postgresql-x64-17
timeout /t 3 /nobreak >nul
echo Done!
echo.

echo Step 4: Enter new password (or press Enter for 'postgres123'):
set /p NEW_PASSWORD=
if "%NEW_PASSWORD%"=="" set NEW_PASSWORD=postgres123

echo.
echo Step 5: Setting new password...
%PSQL% -U postgres -c "ALTER USER postgres WITH PASSWORD '%NEW_PASSWORD%';"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not set password
    copy "%PG_HBA_BACKUP%" "%PG_HBA%" >nul
    net stop postgresql-x64-17 >nul
    net start postgresql-x64-17 >nul
    pause
    exit /b 1
)
echo Done!
echo.

echo Step 6: Restoring security settings...
copy "%PG_HBA_BACKUP%" "%PG_HBA%" >nul
echo Done!
echo.

echo Step 7: Final restart...
net stop postgresql-x64-17
timeout /t 3 /nobreak >nul
net start postgresql-x64-17
timeout /t 3 /nobreak >nul
echo Done!
echo.

echo ========================================
echo SUCCESS! Password has been reset.
echo ========================================
echo.
echo Your new postgres password is: %NEW_PASSWORD%
echo.
echo Save this password!
echo.
echo Next: Run setup_db.bat to create database
echo.
pause
