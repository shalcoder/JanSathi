# AWS Cost Monitoring Script for JanSathi
# Checks current month's spending and usage

Write-Host "💰 JanSathi AWS Cost Monitor" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get current month costs
Write-Host "Fetching current month costs..." -ForegroundColor Yellow
$startDate = (Get-Date -Day 1).ToString("yyyy-MM-dd")
$endDate = (Get-Date).ToString("yyyy-MM-dd")

try {
    $costs = aws ce get-cost-and-usage `
        --time-period Start=$startDate,End=$endDate `
        --granularity MONTHLY `
        --metrics "UnblendedCost" `
        --output json | ConvertFrom-Json
    
    $totalCost = [math]::Round([decimal]$costs.ResultsByTime[0].Total.UnblendedCost.Amount, 2)
    
    Write-Host "📊 Current Month Spending: `$$totalCost" -ForegroundColor Green
    Write-Host ""
    
    # Warning thresholds
    if ($totalCost -gt 50) {
        Write-Host "⚠️  WARNING: Spending is high!" -ForegroundColor Red
        Write-Host "   Consider reviewing your usage" -ForegroundColor Yellow
    } elseif ($totalCost -gt 20) {
        Write-Host "⚠️  CAUTION: Approaching budget limit" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Spending is within safe limits" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Failed to fetch cost data: $_" -ForegroundColor Red
    Write-Host "   Make sure you have billing permissions" -ForegroundColor Yellow
}

Write-Host ""

# Get service breakdown
Write-Host "Fetching service breakdown..." -ForegroundColor Yellow
try {
    $serviceBreakdown = aws ce get-cost-and-usage `
        --time-period Start=$startDate,End=$endDate `
        --granularity MONTHLY `
        --metrics "UnblendedCost" `
        --group-by Type=DIMENSION,Key=SERVICE `
        --output json | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "📋 Cost by Service:" -ForegroundColor Cyan
    Write-Host "-------------------" -ForegroundColor Cyan
    
    foreach ($group in $serviceBreakdown.ResultsByTime[0].Groups) {
        $service = $group.Keys[0]
        $cost = [math]::Round([decimal]$group.Metrics.UnblendedCost.Amount, 2)
        if ($cost -gt 0) {
            Write-Host "   $service : `$$cost" -ForegroundColor White
        }
    }
} catch {
    Write-Host "❌ Failed to fetch service breakdown" -ForegroundColor Red
}

Write-Host ""

# S3 Storage Check
Write-Host "Checking S3 storage usage..." -ForegroundColor Yellow
$bucketName = (Get-Content backend/.env | Select-String "S3_BUCKET_NAME=").ToString().Split("=")[1]

if ($bucketName) {
    try {
        $s3Size = aws s3 ls "s3://$bucketName" --recursive --summarize --human-readable | Select-String "Total Size"
        Write-Host "   S3 Bucket: $bucketName" -ForegroundColor White
        Write-Host "   $s3Size" -ForegroundColor White
    } catch {
        Write-Host "   ⚠️  Could not check S3 usage" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "💡 Cost Optimization Tips:" -ForegroundColor Cyan
Write-Host "   1. Use Claude Haiku instead of Sonnet when possible" -ForegroundColor White
Write-Host "   2. Keep responses under 500 tokens" -ForegroundColor White
Write-Host "   3. S3 files auto-delete after 1 day (lifecycle policy)" -ForegroundColor White
Write-Host "   4. Avoid Kendra (costs $810/month minimum)" -ForegroundColor White
Write-Host ""
Write-Host "📊 View detailed billing:" -ForegroundColor Cyan
Write-Host "   https://console.aws.amazon.com/billing/home" -ForegroundColor White
Write-Host ""
