@echo off
REM Deploy Kendra infrastructure and setup initial data

echo 🚀 Deploying JanSathi Kendra Infrastructure
echo ============================================

REM Navigate to infrastructure directory
cd /d "%~dp0\..\infrastructure"

echo 📦 Installing CDK dependencies...
pip install -r requirements.txt

echo 🏗️ Deploying Data Stack (includes Kendra)...
cdk deploy JanSathi-Data --require-approval never

if %ERRORLEVEL% NEQ 0 (
    echo ❌ CDK deployment failed!
    pause
    exit /b 1
)

echo ✅ Infrastructure deployed successfully!

REM Get Kendra Index ID from stack outputs
echo 📋 Getting Kendra Index ID...
for /f "tokens=2 delims==" %%i in ('cdk list --long 2^>nul ^| findstr "KendraIndexId"') do set KENDRA_INDEX_ID=%%i

if "%KENDRA_INDEX_ID%"=="" (
    echo ❌ Could not retrieve Kendra Index ID from stack outputs
    echo Please check the CDK deployment and get the KendraIndexId manually
    pause
    exit /b 1
)

echo 🔑 Kendra Index ID: %KENDRA_INDEX_ID%

REM Update environment file
echo 📝 Updating backend environment file...
cd /d "%~dp0\..\backend"

REM Backup original .env
copy .env .env.backup

REM Update KENDRA_INDEX_ID in .env file
powershell -Command "(Get-Content .env) -replace 'KENDRA_INDEX_ID=mock-index', 'KENDRA_INDEX_ID=%KENDRA_INDEX_ID%' | Set-Content .env"

echo ✅ Environment updated with Kendra Index ID

REM Setup Kendra with initial data
echo 📚 Populating Kendra with government schemes...
cd /d "%~dp0"
python setup_kendra.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Kendra setup failed!
    pause
    exit /b 1
)

echo 🎉 Kendra deployment and setup complete!
echo 💡 Your backend will now use Kendra for semantic search
echo 📖 Restart your backend server to use the new Kendra integration

pause