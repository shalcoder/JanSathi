# AWS Setup Guide for JanSathi (Free Tier Optimized)
## Budget: $100 Credits - Stay Within Free Tier

---

## 🎯 Cost-Saving Strategy

### Services We'll Use (Free Tier Eligible):
1. **AWS Bedrock** - Pay per token (cheapest model: Claude Haiku)
2. **AWS Polly** - 5M characters/month free (first 12 months)
3. **AWS Transcribe** - 60 minutes/month free (first 12 months)
4. **AWS S3** - 5GB storage free (first 12 months)
5. **AWS Lambda** - 1M requests/month free (always free)
6. **AWS Kendra** - ⚠️ EXPENSIVE ($810/month) - We'll use MOCK DATA instead

### ⚠️ CRITICAL: Skip Kendra to Save Money
Kendra costs $810/month minimum. Instead, we'll use the enhanced mock RAG system already in your code.

---

## 📋 Prerequisites

1. AWS Account with $100 credits
2. AWS CLI installed
3. IAM User with programmatic access

---

## Step 1: Install AWS CLI (if not installed)

### Windows:
```powershell
# Download and install from: https://awscli.amazonaws.com/AWSCLIV2.msi
# Or use winget:
winget install Amazon.AWSCLI
```

### Verify Installation:
```bash
aws --version
```

---

## Step 2: Create IAM User with Minimal Permissions

### Go to AWS Console → IAM → Users → Create User

**User Name:** `jansathi-app`

**Attach Policies:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "polly:SynthesizeSpeech"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "transcribe:StartTranscriptionJob",
        "transcribe:GetTranscriptionJob"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::jansathi-audio-bucket-*/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::jansathi-audio-bucket-*"
    }
  ]
}
```

**Save the Access Key ID and Secret Access Key!**

---

## Step 3: Configure AWS CLI

```bash
aws configure
```

Enter:
- **AWS Access Key ID:** [Your Key]
- **AWS Secret Access Key:** [Your Secret]
- **Default region name:** `us-east-1` (Bedrock available here)
- **Default output format:** `json`

---

## Step 4: Enable Bedrock Models

### Go to AWS Console → Bedrock → Model Access

**Request Access to:**
1. ✅ **Claude 3 Haiku** (Cheapest - $0.25/1M input tokens)
2. ✅ **Claude 3 Sonnet** (For Vision - $3/1M input tokens)

**Cost Estimate:**
- 1000 queries with Haiku: ~$0.50
- 100 image analyses with Sonnet: ~$1.00

---

## Step 5: Create S3 Bucket for Audio Files

```bash
# Create bucket (use unique name)
aws s3 mb s3://jansathi-audio-bucket-$(date +%s) --region us-east-1

# Note the bucket name for later
```

**Set Lifecycle Policy to Auto-Delete After 1 Day:**
```bash
# Create lifecycle.json file (see below)
aws s3api put-bucket-lifecycle-configuration \
  --bucket YOUR_BUCKET_NAME \
  --lifecycle-configuration file://lifecycle.json
```

---

## Step 6: Set Environment Variables

Create `.env` file in `backend/` directory:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# S3 Bucket (from Step 5)
S3_BUCKET_NAME=jansathi-audio-bucket-XXXXXXXX

# Bedrock Models
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Kendra (DISABLED - Using Mock)
KENDRA_INDEX_ID=mock-index

# App Config
SECRET_KEY=YOUR_FLASK_SECRET_KEY
NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# Database
DATABASE_URL=sqlite:///jansathi.db
```

---

## Step 7: Test AWS Services Locally

### Test Script:
```bash
cd backend
python -c "
from app.services.bedrock_service import BedrockService
from app.services.polly_service import PollyService

# Test Bedrock
bedrock = BedrockService()
response = bedrock.generate_response('What is PM Kisan?', 'PM Kisan provides 6000 rupees per year', 'en')
print('Bedrock Response:', response[:100])

# Test Polly
polly = PollyService()
audio_url = polly.synthesize('Hello from JanSathi', 'en')
print('Polly Audio URL:', audio_url)
"
```

---

## Step 8: Deploy to AWS Lambda (Optional - For Production)

### Create Lambda Deployment Package:

```bash
cd backend

# Install dependencies in a folder
pip install -r requirements.txt -t package/

# Copy your code
cp -r app package/
cp lambda_handler.py package/

# Create ZIP
cd package
zip -r ../jansathi-lambda.zip .
cd ..
```

### Create Lambda Function:

```bash
aws lambda create-function \
  --function-name JanSathiAPI \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://jansathi-lambda.zip \
  --timeout 60 \
  --memory-size 512 \
  --environment Variables="{AWS_REGION=us-east-1,S3_BUCKET_NAME=your-bucket-name}"
```

---

## 💰 Cost Monitoring

### Set Up Billing Alerts:

1. Go to **AWS Billing Console**
2. Create Budget:
   - **Budget Type:** Cost Budget
   - **Amount:** $10/month
   - **Alert Threshold:** 80% ($8)

### Expected Monthly Costs (Hackathon Demo):
- **Bedrock (Haiku):** $2-5 (1000-2000 queries)
- **Polly:** FREE (under 5M chars)
- **Transcribe:** FREE (under 60 mins)
- **S3:** FREE (under 5GB)
- **Lambda:** FREE (under 1M requests)

**Total: $2-5/month** ✅

---

## 🚀 Quick Start Commands

### Start Backend Locally:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Start Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Test Full Flow:
```bash
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Open: http://localhost:3000
```

---

## 🔒 Security Best Practices

1. ✅ Never commit `.env` file to Git
2. ✅ Use IAM roles with minimal permissions
3. ✅ Enable MFA on AWS account
4. ✅ Rotate access keys every 90 days
5. ✅ Set up CloudWatch alarms for unusual activity

---

## 📊 Monitoring Dashboard

### Check Usage:
```bash
# Bedrock usage
aws bedrock list-model-invocation-jobs --region us-east-1

# S3 storage
aws s3 ls s3://your-bucket-name --summarize --human-readable --recursive
```

---

## ⚠️ Emergency: Stop All Services

If costs spike:

```bash
# Delete S3 bucket
aws s3 rb s3://your-bucket-name --force

# Delete Lambda function
aws lambda delete-function --function-name JanSathiAPI

# Revoke Bedrock access (Console only)
```

---

## 🎓 Free Tier Limits Summary

| Service | Free Tier | After Free Tier |
|---------|-----------|-----------------|
| Bedrock | None | $0.25-$3 per 1M tokens |
| Polly | 5M chars/month (12 months) | $4 per 1M chars |
| Transcribe | 60 mins/month (12 months) | $0.024 per minute |
| S3 | 5GB (12 months) | $0.023 per GB |
| Lambda | 1M requests/month (always) | $0.20 per 1M requests |

---

## 📞 Support

If you encounter issues:
1. Check CloudWatch Logs
2. Verify IAM permissions
3. Check AWS Service Health Dashboard
4. Review billing dashboard

---

**Next Steps:** Run the setup script below to automate configuration!
