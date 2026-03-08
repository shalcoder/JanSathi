@echo off
echo Creating function-minimal.zip...

REM Navigate to backend directory
cd /d "E:\JanSathi\backend"

REM Create temporary directory
if exist temp_pkg rmdir /s /q temp_pkg
mkdir temp_pkg

REM Copy essential files
copy lambda_handler.py temp_pkg\ >nul 2>&1
if exist .env copy .env temp_pkg\ >nul 2>&1

REM Copy directories (exclude pycache)
if exist app xcopy app temp_pkg\app /s /e /q >nul 2>&1
if exist agentcore xcopy agentcore temp_pkg\agentcore /s /e /q >nul 2>&1  
if exist agents xcopy agents temp_pkg\agents /s /e /q >nul 2>&1
if exist agentic_engine xcopy agentic_engine temp_pkg\agentic_engine /s /e /q >nul 2>&1

REM Remove pycache directories
for /r temp_pkg %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d"

REM Create zip using PowerShell 
powershell -command "Compress-Archive -Path temp_pkg\* -DestinationPath function-minimal.zip -Force"

REM Cleanup
rmdir /s /q temp_pkg

echo.
if exist function-minimal.zip (
    echo ✓ function-minimal.zip created successfully!
    for %%F in (function-minimal.zip) do echo   Size: %%~zF bytes
    echo.
    echo Ready to deploy! You can now run: python deploy_backend.py
) else (
    echo ✗ Failed to create zip file
)

pause