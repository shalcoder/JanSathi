@echo off
echo ========================================
echo   JanSathi - AWS Frontend Deployment
echo ========================================
echo.

cd frontend

echo Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm ci
) else (
    echo Dependencies already installed
)

echo.
echo Testing build...
call npm run build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed! Please fix errors and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Successful!
echo ========================================
echo.
echo Next Steps:
echo   1. Push your code to GitHub:
echo      git add .
echo      git commit -m "Deploy to AWS"
echo      git push origin main
echo.
echo   2. Go to AWS Amplify Console:
echo      https://console.aws.amazon.com/amplify/
echo.
echo   3. Click "New app" - "Host web app"
echo.
echo   4. Connect your GitHub repository
echo.
echo   5. Configure and deploy!
echo.
echo See DEPLOY_TO_AWS.md for detailed instructions.
echo.
pause
