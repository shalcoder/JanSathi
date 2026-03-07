# Extract static files from .next/server/app to out folder for S3 deployment

Write-Host "Extracting static files for S3 deployment..." -ForegroundColor Green

# Create out directory
$outDir = "out"
if (Test-Path $outDir) {
    Remove-Item -Recurse -Force $outDir
}
New-Item -ItemType Directory -Path $outDir | Out-Null

# Copy HTML files from .next/server/app
Write-Host "Copying HTML files..." -ForegroundColor Yellow
Get-ChildItem -Path ".next/server/app" -Filter "*.html" -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Replace((Get-Location).Path + "\.next\server\app\", "")
    $targetPath = Join-Path $outDir $relativePath
    $targetDir = Split-Path $targetPath -Parent
    
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    
    Copy-Item $_.FullName $targetPath -Force
    Write-Host "  Copied: $relativePath" -ForegroundColor Gray
}

# Rename index.html to root
if (Test-Path "out/index.html") {
    # Keep it as is - this is the homepage
}

# Copy static assets
Write-Host "Copying static assets..." -ForegroundColor Yellow
if (Test-Path ".next/static") {
    Copy-Item -Path ".next/static" -Destination "out/_next/static" -Recurse -Force
    Write-Host "  Copied: _next/static" -ForegroundColor Gray
}

# Copy public folder
Write-Host "Copying public assets..." -ForegroundColor Yellow
if (Test-Path "public") {
    Get-ChildItem -Path "public" -Recurse | ForEach-Object {
        $relativePath = $_.FullName.Replace((Get-Location).Path + "\public\", "")
        $targetPath = Join-Path $outDir $relativePath
        
        if ($_.PSIsContainer) {
            if (-not (Test-Path $targetPath)) {
                New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
            }
        } else {
            $targetDir = Split-Path $targetPath -Parent
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            Copy-Item $_.FullName $targetPath -Force
            Write-Host "  Copied: $relativePath" -ForegroundColor Gray
        }
    }
}

# Create 404.html from _not-found.html
if (Test-Path "out/_not-found.html") {
    Copy-Item "out/_not-found.html" "out/404.html" -Force
    Write-Host "  Created: 404.html" -ForegroundColor Gray
}

Write-Host "`nStatic export complete!" -ForegroundColor Green
Write-Host "Files are ready in the 'out' folder for S3 deployment." -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Choose a unique S3 bucket name (e.g., jansathi-frontend-yourname)" -ForegroundColor White
Write-Host "2. Create bucket: aws s3 mb s3://BUCKET_NAME --region us-east-1" -ForegroundColor White
Write-Host "3. Enable website: aws s3 website s3://BUCKET_NAME --index-document index.html --error-document 404.html" -ForegroundColor White
Write-Host "4. Update bucket-policy.json with your bucket name" -ForegroundColor White
Write-Host "5. Apply policy: aws s3api put-bucket-policy --bucket BUCKET_NAME --policy file://bucket-policy.json" -ForegroundColor White
Write-Host "6. Upload: aws s3 sync out/ s3://BUCKET_NAME/ --delete" -ForegroundColor White
