@echo off
echo ======================================
echo    JanSathi Frontend Deployment
echo ======================================
echo.

REM Navigate to frontend directory
cd /d "E:\JanSathi\frontend"

REM Check if build exists
if not exist "out" (
    echo ❌ Error: 'out' directory not found!
    echo Please run 'npm run build' first to generate static files.
    echo.
    pause
    exit /b 1
)

echo ✅ Build directory found: out\
echo.

REM Check AWS credentials
echo 🔍 Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: AWS credentials not configured!
    echo Please run: aws configure
    echo.
    pause
    exit /b 1
)

echo ✅ AWS credentials configured
echo.

REM Deploy frontend
echo 🚀 Starting frontend deployment...
echo.
python deploy_frontend.py

echo.
if %errorlevel% equ 0 (
    echo ✅ Frontend deployment completed successfully!
    echo.
    echo 📱 Your JanSathi frontend should now be live on AWS S3.
    echo Check the output above for the website URL.
) else (
    echo ❌ Deployment failed with error code %errorlevel%
    echo Check the error messages above for details.
)

echo.
pause