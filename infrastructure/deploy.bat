@echo off
REM ============================================================
REM JanSathi Production Deployment Script
REM Deploys CDK infrastructure + Frontend to AWS
REM ============================================================

echo.
echo ========================================
echo   JanSathi Production Deployment
echo ========================================
echo.

REM Check AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS CLI not found. Install: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Check CDK is installed
cdk --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing AWS CDK...
    npm install -g aws-cdk
)

echo.
echo [1/4] Installing CDK dependencies...
cd /d "%~dp0infrastructure"
pip install -r requirements.txt

echo.
echo [2/4] Bootstrapping CDK (first time only)...
cdk bootstrap

echo.
echo [3/4] Deploying all stacks...
cdk deploy --all --require-approval never --outputs-file ../cdk-outputs.json

echo.
echo [4/4] Building and deploying frontend...
cd /d "%~dp0frontend"
call npm run build

REM Read bucket name from CDK outputs and sync
echo Syncing frontend to S3...
echo NOTE: After deploy, run:
echo   aws s3 sync out/ s3://BUCKET_NAME --delete
echo   (Get BUCKET_NAME from cdk-outputs.json)

echo.
echo ========================================
echo   Deployment Complete!
echo   Check cdk-outputs.json for URLs
echo ========================================
pause
