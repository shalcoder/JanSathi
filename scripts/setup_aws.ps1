# JanSathi AWS Setup Script (PowerShell)
# This script automates AWS resource creation for the hackathon

Write-Host "🚀 JanSathi AWS Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is installed
Write-Host "Checking AWS CLI installation..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   Download from: https://awscli.amazonaws.com/AWSCLIV2.msi" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "⚠️  IMPORTANT: This script will create AWS resources." -ForegroundColor Yellow
Write-Host "   Estimated cost: $2-5/month for demo usage" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Setup cancelled." -ForegroundColor Red
    exit 0
}

# Check AWS credentials
Write-Host ""
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "✅ Authenticated as: $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured." -ForegroundColor Red
    Write-Host "   Run: aws configure" -ForegroundColor Yellow
    exit 1
}

# Set region
$region = "us-east-1"
Write-Host ""
Write-Host "Using AWS Region: $region" -ForegroundColor Cyan

# Create S3 Bucket
Write-Host ""
Write-Host "Creating S3 bucket for audio files..." -ForegroundColor Yellow
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$bucketName = "jansathi-audio-bucket-$timestamp"

try {
    aws s3 mb "s3://$bucketName" --region $region
    Write-Host "✅ S3 Bucket created: $bucketName" -ForegroundColor Green
    
    # Apply lifecycle policy
    Write-Host "   Applying lifecycle policy (auto-delete after 1 day)..." -ForegroundColor Yellow
    aws s3api put-bucket-lifecycle-configuration `
        --bucket $bucketName `
        --lifecycle-configuration file://backend/lifecycle.json
    Write-Host "   ✅ Lifecycle policy applied" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create S3 bucket: $_" -ForegroundColor Red
    exit 1
}

# Check Bedrock model access
Write-Host ""
Write-Host "Checking Bedrock model access..." -ForegroundColor Yellow
Write-Host "⚠️  You need to manually enable Bedrock models:" -ForegroundColor Yellow
Write-Host "   1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess" -ForegroundColor Cyan
Write-Host "   2. Request access to:" -ForegroundColor Cyan
Write-Host "      - Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0)" -ForegroundColor Cyan
Write-Host "      - Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0)" -ForegroundColor Cyan
Write-Host ""
$bedrockConfirm = Read-Host "Have you enabled Bedrock models? (yes/no)"
if ($bedrockConfirm -ne "yes") {
    Write-Host "⚠️  Please enable Bedrock models before continuing." -ForegroundColor Yellow
}

# Create .env file
Write-Host ""
Write-Host "Creating .env file..." -ForegroundColor Yellow
$envContent = @"
# AWS Configuration
AWS_ACCESS_KEY_ID=$($env:AWS_ACCESS_KEY_ID)
AWS_SECRET_ACCESS_KEY=$($env:AWS_SECRET_ACCESS_KEY)
AWS_REGION=$region

# S3 Bucket
S3_BUCKET_NAME=$bucketName

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Kendra (DISABLED - Using Mock)
KENDRA_INDEX_ID=mock-index

# Flask Configuration
SECRET_KEY=$(New-Guid)
NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=sqlite:///jansathi.db

# Port
PORT=5000
"@

$envPath = "backend/.env"
$envContent | Out-File -FilePath $envPath -Encoding UTF8
Write-Host "✅ .env file created at: $envPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ AWS Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   S3 Bucket: $bucketName" -ForegroundColor White
Write-Host "   Region: $region" -ForegroundColor White
Write-Host "   Config: backend/.env" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Verify Bedrock model access in AWS Console" -ForegroundColor White
Write-Host "   2. cd backend && pip install -r requirements.txt" -ForegroundColor White
Write-Host "   3. python main.py" -ForegroundColor White
Write-Host "   4. Test at http://localhost:5000/health" -ForegroundColor White
Write-Host ""
Write-Host "💰 Cost Monitoring:" -ForegroundColor Yellow
Write-Host "   Set up billing alerts at: https://console.aws.amazon.com/billing/home#/budgets" -ForegroundColor White
Write-Host "   Recommended: $10/month budget with 80% alert" -ForegroundColor White
Write-Host ""
