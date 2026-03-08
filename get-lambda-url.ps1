# Get Lambda API Gateway URL
# Run this script to find your Lambda API endpoint

Write-Host "🔍 Finding your Lambda API Gateway URL..." -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is configured
try {
    $accountId = aws sts get-caller-identity --query Account --output text 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ AWS CLI not configured. Please run: aws configure" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ AWS Account ID: $accountId" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📡 Checking for API Gateway..." -ForegroundColor Cyan

# Try to find the API Gateway
$apiEndpoint = aws apigatewayv2 get-apis --region us-east-1 --query "Items[?Name=='jansathi-api'].ApiEndpoint" --output text 2>$null

if ($apiEndpoint -and $apiEndpoint -ne "") {
    Write-Host "✅ Found API Gateway!" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "Your Lambda API URL:" -ForegroundColor Yellow
    Write-Host $apiEndpoint -ForegroundColor White
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host ""
    
    # Test the endpoint
    Write-Host "🧪 Testing API endpoint..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "$apiEndpoint/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API is working!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  API endpoint exists but health check failed" -ForegroundColor Yellow
        Write-Host "   This might be normal if /health route is not configured" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Copy the API URL above" -ForegroundColor White
    Write-Host "2. Go to Vercel Dashboard: https://vercel.com/dashboard" -ForegroundColor White
    Write-Host "3. Select your JanSathi project" -ForegroundColor White
    Write-Host "4. Go to Settings → Environment Variables" -ForegroundColor White
    Write-Host "5. Set NEXT_PUBLIC_API_URL to the API URL" -ForegroundColor White
    Write-Host "6. Redeploy your site" -ForegroundColor White
    
} else {
    Write-Host "❌ API Gateway 'jansathi-api' not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Let me check if Lambda function exists..." -ForegroundColor Cyan
    
    $lambdaExists = aws lambda get-function --function-name jansathi-backend --region us-east-1 --query 'Configuration.FunctionName' --output text 2>$null
    
    if ($lambdaExists -eq "jansathi-backend") {
        Write-Host "✅ Lambda function 'jansathi-backend' exists" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  But API Gateway is missing. Creating it now..." -ForegroundColor Yellow
        Write-Host ""
        
        # Create API Gateway
        Write-Host "Creating API Gateway..." -ForegroundColor Cyan
        $apiId = aws apigatewayv2 create-api `
            --name jansathi-api `
            --protocol-type HTTP `
            --target "arn:aws:lambda:us-east-1:${accountId}:function:jansathi-backend" `
            --region us-east-1 `
            --query 'ApiId' `
            --output text
        
        if ($apiId) {
            Write-Host "✅ API Gateway created with ID: $apiId" -ForegroundColor Green
            
            # Add permission
            Write-Host "Adding Lambda invoke permission..." -ForegroundColor Cyan
            aws lambda add-permission `
                --function-name jansathi-backend `
                --statement-id apigateway-invoke `
                --action lambda:InvokeFunction `
                --principal apigateway.amazonaws.com `
                --source-arn "arn:aws:execute-api:us-east-1:${accountId}:${apiId}/*/*" `
                --region us-east-1 2>$null
            
            # Get the endpoint
            $newEndpoint = aws apigatewayv2 get-api --api-id $apiId --region us-east-1 --query 'ApiEndpoint' --output text
            
            Write-Host ""
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
            Write-Host "Your NEW Lambda API URL:" -ForegroundColor Yellow
            Write-Host $newEndpoint -ForegroundColor White
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "✅ API Gateway setup complete!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create API Gateway" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Lambda function 'jansathi-backend' not found" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please deploy your Lambda function first:" -ForegroundColor Yellow
        Write-Host "1. cd JanSathi\backend" -ForegroundColor White
        Write-Host "2. python create_minimal_package.py" -ForegroundColor White
        Write-Host "3. Follow the deployment guide in JANSATHI_DEPLOYMENT_GUIDE.md" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "For detailed instructions, see: CONNECT_VERCEL_TO_LAMBDA.md" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
