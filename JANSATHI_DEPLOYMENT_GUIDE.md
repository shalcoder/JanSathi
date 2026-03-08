# JanSathi - Complete AWS Deployment Guide

Complete guide to deploy JanSathi backend (Lambda + API Gateway) and frontend (S3 + CloudFront) on AWS.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Lambda + API Gateway)](#backend-deployment)
3. [Frontend Deployment (S3 + CloudFront)](#frontend-deployment)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required:
- ✅ AWS Account with valid payment method
- ✅ AWS CLI installed and configured
- ✅ Python 3.11 (Anaconda recommended)
- ✅ Node.js 18+ and npm
- ✅ Git

### Check Prerequisites:
```bash
# Check AWS CLI
aws --version
aws sts get-caller-identity

# Check Python
python --version

# Check Node.js
node --version
npm --version
```

---

## Backend Deployment

### Step 1: Prepare Backend Package

**In Anaconda Prompt:**

```cmd
cd JanSathi\backend
python create_minimal_package.py
```

This creates `function-minimal.zip` (~19 MB).

### Step 2: Upload to AWS Lambda

**Option A: Via CloudShell (Recommended)**

1. Go to AWS CloudShell: https://console.aws.amazon.com/cloudshell
2. Click "Actions" → "Upload file"
3. Select `function-minimal.zip`
4. Run:

```bash
# Upload to S3
aws s3 mb s3://jansathi-lambda-deploy-$(aws sts get-caller-identity --query Account --output text) --region us-east-1
aws s3 cp function-minimal.zip s3://jansathi-lambda-deploy-$(aws sts get-caller-identity --query Account --output text)/

# Deploy to Lambda
aws lambda update-function-code \
  --function-name jansathi-backend \
  --s3-bucket jansathi-lambda-deploy-$(aws sts get-caller-identity --query Account --output text) \
  --s3-key function-minimal.zip \
  --region us-east-1
```

**Option B: Via Local AWS CLI**

```cmd
cd JanSathi\backend
aws s3 cp function-minimal.zip s3://jansathi-lambda-deploy-YOUR_ACCOUNT_ID/
aws lambda update-function-code --function-name jansathi-backend --s3-bucket jansathi-lambda-deploy-YOUR_ACCOUNT_ID --s3-key function-minimal.zip --region us-east-1
```

### Step 3: Configure Lambda

```bash
# Set environment variables
aws lambda update-function-configuration \
  --function-name jansathi-backend \
  --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production}" \
  --region us-east-1

# Update timeout and memory
aws lambda update-function-configuration \
  --function-name jansathi-backend \
  --timeout 60 \
  --memory-size 1024 \
  --region us-east-1
```

### Step 4: Create API Gateway

```bash
# Create HTTP API
API_ID=$(aws apigatewayv2 create-api \
  --name jansathi-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:jansathi-backend \
  --region us-east-1 \
  --query 'ApiId' \
  --output text)

# Give API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name jansathi-backend \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:YOUR_ACCOUNT_ID:${API_ID}/*/*" \
  --region us-east-1

# Get API endpoint
aws apigatewayv2 get-api --api-id $API_ID --region us-east-1 --query 'ApiEndpoint' --output text
```

**Save the API endpoint URL!** You'll need it for the frontend.

### Step 5: Test Backend

```bash
# Test the API
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com \
  -H 'Content-Type: application/json' \
  -d '{"text_query": "pradhan mantri awas yojana", "language": "hi"}'
```

Should return JSON with Hindi response.

---

## Frontend Deployment

### Step 1: Update Frontend Configuration

**Edit `JanSathi/frontend/.env.local`:**

```env
NEXT_PUBLIC_API_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com
NEXT_PUBLIC_ENV=production
```

Replace `YOUR_API_ID` with your actual API Gateway ID.

### Step 2: Build Frontend

```cmd
cd JanSathi\frontend
npm install
npm run build
```

This creates the `out` folder with static files.

### Step 3: Create S3 Bucket

**In CloudShell or AWS CLI:**

```bash
# Create bucket (use unique name)
BUCKET_NAME="jansathi-frontend-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Enable static website hosting
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document 404.html

# Make bucket public
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::'$BUCKET_NAME'/*"
  }]
}'

echo "Bucket created: $BUCKET_NAME"
echo "Website URL: http://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"
```

### Step 4: Upload Frontend to S3

**Option A: Via AWS CLI (Local)**

```cmd
cd JanSathi\frontend
aws s3 sync out\ s3://YOUR_BUCKET_NAME --delete
```

**Option B: Via CloudShell**

1. Zip the `out` folder locally:
   ```cmd
   cd JanSathi\frontend
   powershell -Command "Compress-Archive -Path out\* -DestinationPath frontend.zip -Force"
   ```

2. Upload `frontend.zip` to CloudShell

3. In CloudShell:
   ```bash
   unzip frontend.zip -d frontend-files
   aws s3 sync frontend-files/ s3://YOUR_BUCKET_NAME --delete
   ```

### Step 5: Create CloudFront Distribution (Optional but Recommended)

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name YOUR_BUCKET_NAME.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html \
  --query 'Distribution.DomainName' \
  --output text
```

This gives you a CloudFront URL (e.g., `d1234567890.cloudfront.net`) with HTTPS support.

---

## Configuration

### Backend Environment Variables

Set in Lambda Configuration → Environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `USE_DYNAMODB` | `true` | Yes |
| `NODE_ENV` | `production` | Yes |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-haiku-20240307-v1:0` | Optional |

### Frontend Environment Variables

Set in `.env.local`:

| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_API_URL` | Your API Gateway URL | Yes |
| `NEXT_PUBLIC_ENV` | `production` | Yes |

---

## Testing

### Test Backend API

```bash
# Test health
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/health

# Test query
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com \
  -H 'Content-Type: application/json' \
  -d '{"text_query": "test", "language": "hi"}'
```

### Test Frontend

1. Open S3 website URL: `http://YOUR_BUCKET_NAME.s3-website-us-east-1.amazonaws.com`
2. Or CloudFront URL: `https://YOUR_CLOUDFRONT_ID.cloudfront.net`
3. Try asking a question in the chat interface

---

## Troubleshooting

### Backend Issues

**Lambda returns "No query provided":**
- Check API Gateway integration
- Verify payload format: `{"text_query": "...", "language": "hi"}`

**Bedrock AccessDeniedException:**
- Add payment method to AWS account
- Attach `AmazonBedrockFullAccess` policy to Lambda role
- Enable Claude models in Bedrock console

**Lambda timeout:**
- Increase timeout: Configuration → General → Timeout (60s recommended)
- Increase memory: Configuration → General → Memory (1024 MB recommended)

**Package too large:**
- Use minimal requirements: `requirements-minimal.txt`
- Remove unused dependencies
- Deploy via S3 (not direct upload)

### Frontend Issues

**API calls fail (CORS):**
- Check API Gateway CORS settings
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check browser console for errors

**S3 bucket not accessible:**
- Verify bucket policy allows public read
- Check bucket name is correct
- Ensure static website hosting is enabled

**CloudFront not updating:**
- Create invalidation: `aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"`
- Wait 5-10 minutes for propagation

---

## Architecture Overview

```
User Browser
    ↓
CloudFront (CDN)
    ↓
S3 Bucket (Frontend - Next.js static files)
    ↓
API Gateway (HTTPS endpoint)
    ↓
Lambda Function (Backend - Python Flask)
    ↓
├─ Bedrock (AI - Claude)
├─ DynamoDB (Database)
└─ Kendra (Search - optional)
```

---

## Cost Estimate

**Free Tier (First 12 months):**
- Lambda: 1M requests/month free
- API Gateway: 1M requests/month free
- S3: 5GB storage free
- CloudFront: 1TB transfer free

**After Free Tier:**
- Lambda: ~$0.20 per 1M requests
- API Gateway: ~$1.00 per 1M requests
- S3: ~$0.023 per GB/month
- CloudFront: ~$0.085 per GB transfer
- Bedrock: Pay per token (varies by model)

**Estimated monthly cost for 10K users:** $5-20

---

## Quick Reference

### Important URLs

| Service | URL |
|---------|-----|
| Lambda Console | https://console.aws.amazon.com/lambda/home?region=us-east-1 |
| API Gateway Console | https://console.aws.amazon.com/apigateway/home?region=us-east-1 |
| S3 Console | https://console.aws.amazon.com/s3 |
| CloudFront Console | https://console.aws.amazon.com/cloudfront |
| CloudShell | https://console.aws.amazon.com/cloudshell |

### Key Commands

```bash
# Redeploy backend
cd JanSathi/backend
python create_minimal_package.py
aws s3 cp function-minimal.zip s3://jansathi-lambda-deploy-ACCOUNT_ID/
aws lambda update-function-code --function-name jansathi-backend --s3-bucket jansathi-lambda-deploy-ACCOUNT_ID --s3-key function-minimal.zip --region us-east-1

# Redeploy frontend
cd JanSathi/frontend
npm run build
aws s3 sync out/ s3://YOUR_BUCKET_NAME --delete

# View Lambda logs
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1

# Test API
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com -H 'Content-Type: application/json' -d '{"text_query": "test", "language": "hi"}'
```

---

## Support

For issues or questions:
1. Check CloudWatch logs: `/aws/lambda/jansathi-backend`
2. Review this guide's troubleshooting section
3. Check AWS service health: https://status.aws.amazon.com/

---

**Last Updated:** 2026-03-07
**Version:** 1.0
