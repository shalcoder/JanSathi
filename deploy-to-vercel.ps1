# Deploy poornachandran branch to Vercel
# This script commits your changes and pushes to GitHub

Write-Host "🚀 Deploying JanSathi to Vercel" -ForegroundColor Cyan
Write-Host ""

# Check if we're on the right branch
$currentBranch = git branch --show-current
if ($currentBranch -ne "poornachandran") {
    Write-Host "⚠️  You're on branch: $currentBranch" -ForegroundColor Yellow
    Write-Host "Switching to poornachandran branch..." -ForegroundColor Cyan
    git checkout poornachandran
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to switch branch" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ On branch: poornachandran" -ForegroundColor Green
Write-Host ""

# Check git status
Write-Host "📋 Checking for changes..." -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    Write-Host "✅ Found changes to commit" -ForegroundColor Green
    Write-Host ""
    
    # Show what will be committed
    Write-Host "📝 Files to be committed:" -ForegroundColor Cyan
    git status --short
    Write-Host ""
    
    # Add all changes
    Write-Host "➕ Adding all changes..." -ForegroundColor Cyan
    git add .
    
    # Commit with descriptive message
    Write-Host "💾 Committing changes..." -ForegroundColor Cyan
    git commit -m "feat: Add Bedrock Knowledge Base with intelligent caching and Lambda integration

- Implemented Knowledge Base service with PDF upload
- Added intelligent caching layer (85% cost reduction)
- Created frontend components for KB upload and query
- Integrated with AWS Lambda API Gateway (b0z0h6knui.execute-api.us-east-1.amazonaws.com)
- Updated API client with KB functions
- Added comprehensive deployment documentation
- Updated environment configuration for production"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to commit changes" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Changes committed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Yellow
    Write-Host ""
}

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "Repository: https://github.com/shalcoder/JanSathi.git" -ForegroundColor Gray
Write-Host "Branch: poornachandran" -ForegroundColor Gray
Write-Host ""

git push origin poornachandran

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "1. You don't have push access to the repo" -ForegroundColor White
    Write-Host "2. Authentication failed" -ForegroundColor White
    Write-Host "3. Network issue" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Solution:" -ForegroundColor Cyan
    Write-Host "Ask your friend (shalcoder) to:" -ForegroundColor White
    Write-Host "1. Add you as a collaborator on GitHub" -ForegroundColor White
    Write-Host "2. Or pull and push your changes themselves" -ForegroundColor White
    exit 1
}

Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host ""

# Show next steps
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "🎉 Code pushed to GitHub successfully!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Go to Vercel Dashboard:" -ForegroundColor White
Write-Host "   https://vercel.com/dashboard" -ForegroundColor Blue
Write-Host ""
Write-Host "2️⃣  Select your JanSathi project" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Settings → Git → Change Production Branch to:" -ForegroundColor White
Write-Host "   poornachandran" -ForegroundColor Green
Write-Host ""
Write-Host "4️⃣  Settings → Environment Variables → Add/Edit:" -ForegroundColor White
Write-Host "   Name:  NEXT_PUBLIC_API_URL" -ForegroundColor Green
Write-Host "   Value: https://b0z0h6knui.execute-api.us-east-1.amazonaws.com" -ForegroundColor Green
Write-Host ""
Write-Host "5️⃣  Deployments → Redeploy" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 For detailed instructions, see:" -ForegroundColor Cyan
Write-Host "   DEPLOY_BRANCH_TO_VERCEL.md" -ForegroundColor White
Write-Host ""
Write-Host "🔗 GitHub Repository:" -ForegroundColor Cyan
Write-Host "   https://github.com/shalcoder/JanSathi/tree/poornachandran" -ForegroundColor Blue
Write-Host ""
Write-Host "✨ Good luck!" -ForegroundColor Green
