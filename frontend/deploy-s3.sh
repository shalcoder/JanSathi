#!/bin/bash
set -e

# Configuration
BUCKET_NAME="${S3_BUCKET_NAME:-jansathi-frontend}"
REGION="${AWS_REGION:-us-east-1}"
DISTRIBUTION_ID="${CLOUDFRONT_DISTRIBUTION_ID:-}"

echo "🚀 Deploying JanSathi Frontend to S3 + CloudFront"
echo "=================================================="
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"
echo ""

# Ensure we're in the frontend directory
cd "$(dirname "$0")"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run:"
    echo "   aws configure"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build the application
echo ""
echo "🔨 Building application..."
npm run build

# Check if build was successful
if [ ! -d "out" ]; then
    echo "❌ Build failed - 'out' directory not found"
    echo "   Make sure next.config.ts has: output: 'export'"
    exit 1
fi

# Check if bucket exists, create if not
echo ""
echo "🪣 Checking S3 bucket..."
if ! aws s3 ls "s3://$BUCKET_NAME" 2>&1 > /dev/null; then
    echo "Creating bucket: $BUCKET_NAME"
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
    
    # Enable static website hosting
    aws s3 website "s3://$BUCKET_NAME" \
        --index-document index.html \
        --error-document 404.html
    
    # Set bucket policy for public access
    cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket "$BUCKET_NAME" \
        --policy file:///tmp/bucket-policy.json
    
    rm /tmp/bucket-policy.json
    
    echo "✅ Bucket created and configured"
else
    echo "✅ Bucket exists"
fi

# Upload files to S3
echo ""
echo "📤 Uploading files to S3..."

# Upload static assets with long cache
echo "   Uploading static assets (1 year cache)..."
aws s3 sync out/ "s3://$BUCKET_NAME/" \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --exclude "*.html" \
    --exclude "*.json" \
    --exclude "*.txt" \
    --quiet

# Upload HTML/JSON with short cache
echo "   Uploading HTML/JSON (no cache)..."
aws s3 sync out/ "s3://$BUCKET_NAME/" \
    --delete \
    --cache-control "public, max-age=0, must-revalidate" \
    --exclude "*" \
    --include "*.html" \
    --include "*.json" \
    --include "*.txt" \
    --quiet

echo "✅ Upload complete!"

# Invalidate CloudFront cache if distribution ID is provided
if [ -n "$DISTRIBUTION_ID" ]; then
    echo ""
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text
    echo "✅ Cache invalidation started"
fi

# Get website URL
WEBSITE_URL=$(aws s3api get-bucket-website --bucket "$BUCKET_NAME" --query 'WebsiteConfiguration.IndexDocument.Suffix' --output text 2>/dev/null || echo "")

echo ""
echo "✅ Deployment Complete!"
echo "=================================================="
echo "S3 Website URL: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

if [ -n "$DISTRIBUTION_ID" ]; then
    CLOUDFRONT_URL=$(aws cloudfront get-distribution --id "$DISTRIBUTION_ID" --query 'Distribution.DomainName' --output text 2>/dev/null || echo "")
    if [ -n "$CLOUDFRONT_URL" ]; then
        echo "CloudFront URL: https://$CLOUDFRONT_URL"
    fi
fi

echo ""
echo "📋 Next Steps:"
echo "   1. Test your deployment"
echo "   2. Configure custom domain (optional)"
echo "   3. Set up CloudFront for HTTPS (recommended)"
echo ""
