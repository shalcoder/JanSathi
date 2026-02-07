# 🛠️ JanSathi Setup Scripts

Automated scripts to help you set up and monitor AWS services.

---

## 📁 Available Scripts

### 1. `setup_aws.ps1` - Automated AWS Setup
**Purpose:** Creates S3 bucket, applies lifecycle policy, generates .env file

**Usage:**
```powershell
.\setup_aws.ps1
```

**What it does:**
- ✅ Verifies AWS CLI installation
- ✅ Checks AWS credentials
- ✅ Creates S3 bucket with unique name
- ✅ Applies lifecycle policy (auto-delete after 1 day)
- ✅ Generates `backend/.env` file with your settings
- ✅ Provides setup summary

**Requirements:**
- AWS CLI installed
- AWS credentials configured (`aws configure`)
- Bedrock models enabled (manual step)

**Time:** ~2 minutes

---

### 2. `test_aws_services.py` - Service Verification
**Purpose:** Tests all AWS integrations to verify setup

**Usage:**
```bash
python test_aws_services.py
```

**What it tests:**
- ✅ Environment variables
- ✅ AWS Bedrock (Claude 3)
- ✅ AWS Polly (Text-to-Speech)
- ✅ RAG Service (Mock data)
- ✅ S3 Bucket access (read/write/delete)
- ✅ AWS Transcribe client

**Output:**
```
🧪 JanSathi AWS Services Test
==================================================

1️⃣  Testing Environment Variables...
   ✅ AWS_ACCESS_KEY_ID: AKIA****
   ✅ AWS_SECRET_ACCESS_KEY: ****
   ✅ AWS_REGION: us-east-1
   ✅ S3_BUCKET_NAME: jansathi-audio-bucket-****

2️⃣  Testing AWS Bedrock (Claude 3)...
   ✅ Bedrock Response: ✅ **What this is**: (Demo Mode)...
   💰 Estimated cost: ~$0.001

3️⃣  Testing AWS Polly (Text-to-Speech)...
   ✅ Polly Audio URL: https://jansathi-audio-bucket...
   💰 Characters used: 23 (Free tier: 5M/month)

... (more tests)
```

**Time:** ~30 seconds

---

### 3. `check_aws_costs.ps1` - Cost Monitoring
**Purpose:** Monitors AWS spending and usage

**Usage:**
```powershell
.\check_aws_costs.ps1
```

**What it shows:**
- 💰 Current month total spending
- 📊 Cost breakdown by service
- 💾 S3 storage usage
- ⚠️ Warning if costs are high

**Output:**
```
💰 JanSathi AWS Cost Monitor
================================

📊 Current Month Spending: $2.34
✅ Spending is within safe limits

📋 Cost by Service:
-------------------
   Amazon Bedrock : $1.89
   Amazon Polly : $0.00
   Amazon S3 : $0.45

   S3 Bucket: jansathi-audio-bucket-1234567890
   Total Size: 234.5 MiB
```

**Recommended:** Run daily during development

**Time:** ~10 seconds

---

## 🚀 Quick Setup Flow

### First Time Setup:
```powershell
# 1. Configure AWS CLI
aws configure

# 2. Run automated setup
.\setup_aws.ps1

# 3. Install dependencies
cd ..\backend
pip install -r requirements.txt

# 4. Test services
cd ..\scripts
python test_aws_services.py

# 5. Check costs
.\check_aws_costs.ps1
```

### Daily Development:
```powershell
# Check costs before starting work
.\check_aws_costs.ps1

# ... do your development ...

# Check costs after testing
.\check_aws_costs.ps1
```

---

## 📋 Prerequisites

### For PowerShell Scripts (.ps1):
- Windows PowerShell 5.1+ or PowerShell Core 7+
- AWS CLI installed and configured
- Execution policy allows scripts:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### For Python Scripts (.py):
- Python 3.8+
- Dependencies installed:
  ```bash
  pip install boto3 python-dotenv
  ```
- Backend `.env` file configured

---

## 🔧 Troubleshooting

### "AWS CLI not found"
**Fix:**
```powershell
# Install AWS CLI
winget install Amazon.AWSCLI

# Or download from:
# https://awscli.amazonaws.com/AWSCLIV2.msi
```

### "AWS credentials not configured"
**Fix:**
```bash
aws configure
# Enter your Access Key ID and Secret Access Key
```

### "Permission denied" (PowerShell)
**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found" (Python)
**Fix:**
```bash
cd backend
pip install -r requirements.txt
```

### "S3 bucket already exists"
**Fix:** The script generates unique bucket names. If this happens, delete the old bucket:
```bash
aws s3 rb s3://old-bucket-name --force
```

---

## 💡 Tips

1. **Run cost check daily** to catch unexpected charges early
2. **Test services after any AWS configuration change**
3. **Keep scripts updated** if you modify AWS resources
4. **Save script output** for troubleshooting later

---

## 🆘 Emergency Commands

### Stop All AWS Services:
```powershell
# Delete S3 bucket (stops storage costs)
aws s3 rb s3://your-bucket-name --force

# Disable Lambda (if deployed)
aws lambda delete-function --function-name JanSathiAPI
```

### Check What's Running:
```bash
# List S3 buckets
aws s3 ls

# List Lambda functions
aws lambda list-functions

# Check Bedrock usage
aws bedrock list-model-invocation-jobs --region us-east-1
```

---

## 📞 Support

If scripts fail:
1. Check AWS credentials: `aws sts get-caller-identity`
2. Verify IAM permissions
3. Check AWS Service Health: https://status.aws.amazon.com/
4. Review script output for specific errors

---

**Need more help?** See `../docs/AWS_SETUP_GUIDE.md`
