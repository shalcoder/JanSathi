@echo off
echo ========================================
echo   Deploying JanSathi to S3
echo ========================================
echo.

REM Set your bucket name here
set BUCKET_NAME=jansathi-frontend-dell

echo Building application...
set STATIC_EXPORT=true
call npm run build

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Uploading to S3...
aws s3 sync out/ s3://%BUCKET_NAME%/ --delete

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your site: http://%BUCKET_NAME%.s3-website-us-east-1.amazonaws.com
echo.
pause
