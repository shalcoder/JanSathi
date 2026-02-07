# 🚀 JanSathi - Quick Start Guide

## For Team Member Setting Up AWS

---

## ⏱️ Time Required: 45-60 minutes

---

## 📋 What You'll Set Up

✅ AWS Bedrock (Claude 3 AI)  
✅ AWS Polly (Text-to-Speech)  
✅ AWS Transcribe (Speech-to-Text)  
✅ AWS S3 (Audio Storage)  
✅ Cost Monitoring & Alerts  

**Budget:** Stay under $5/month with $100 credits

---

## 🎯 Step-by-Step Setup

### Step 1: Install AWS CLI (5 min)

**Windows:**
```powershell
# Download and install
# https://awscli.amazonaws.com/AWSCLIV2.msi

# Or use winget
winget install Amazon.AWSCLI

# Verify
aws --version
```

---

### Step 2: Configure AWS Credentials (10 min)

1. **Create IAM User:**
   - Go to: https://console.aws.amazon.com/iam/home#/users
   - Click "Create User"
   - Name: `jansathi-app`
   - Enable "Programmatic access"
   - Attach policy: `PowerUserAccess`
   - **SAVE** Access Key ID and Secret Key

2. **Configure CLI:**
   ```bash
   aws configure
   ```
   - Access Key ID: [paste your key]
   - Secret Access Key: [paste your secret]
   - Region: `us-east-1`
   - Output: `json`

3. **Verify:**
   ```bash
   aws sts get-caller-identity
   ```

---

### Step 3: Enable Bedrock Models (10 min)

⚠️ **MUST DO MANUALLY IN AWS CONSOLE**

1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
2. Click "Manage model access"
3. Select:
   - ✅ **Claude 3 Haiku** (cheap, for text)
   - ✅ **Claude 3 Sonnet** (for image analysis)
4. Click "Request model access"
5. Wait 2-5 minutes (usually instant)
6. Refresh and verify "Access granted"

---

### Step 4: Run Automated Setup (5 min)

```powershell
# Navigate to project
cd "C:\Users\keert\Ai Bharat\JanSathi"

# Run setup script
.\scripts\setup_aws.ps1
```

**This script will:**
- ✅ Create S3 bucket
- ✅ Apply lifecycle policy (auto-delete after 1 day)
- ✅ Generate `.env` file
- ✅ Verify AWS connection

**Note the S3 bucket name** - you'll need it!

---

### Step 5: Install Dependencies (5 min)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

### Step 6: Test AWS Services (5 min)

```bash
cd scripts
python test_aws_services.py
```

**Expected output:**
```
✅ Environment Variables: All set
✅ Bedrock: Response received
✅ Polly: Audio URL generated
✅ RAG: Documents retrieved
✅ S3: Read/Write/Delete OK
```

If all ✅, you're good to go!

---

### Step 7: Start Application (2 min)

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Should see: `Running on http://127.0.0.1:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Should see: `Ready on http://localhost:3000`

---

### Step 8: Test Full Application (5 min)

1. Open: http://localhost:3000
2. Click "Start Talking"
3. Type: "What is PM Kisan scheme?"
4. Verify:
   - ✅ AI responds with formatted answer
   - ✅ Scheme card appears
   - ✅ Audio player shows (if Polly working)
5. Try voice input (click microphone)
6. Upload test image (Documents page)

---

### Step 9: Set Up Cost Monitoring (5 min)

1. **Create Budget Alert:**
   - Go to: https://console.aws.amazon.com/billing/home#/budgets
   - Create budget: $10/month
   - Alert at 80% ($8)

2. **Test Cost Monitor:**
   ```powershell
   .\scripts\check_aws_costs.ps1
   ```

---

## ✅ Setup Complete!

### What's Working:
- 🤖 AI chat with Claude 3
- 🎤 Voice input (browser-based)
- 🔊 Text-to-speech responses
- 📄 Document analysis with Vision AI
- 💰 Cost monitoring

### Expected Costs:
- **Demo usage:** $2-5/month
- **Free tier covers:** Polly, Transcribe, S3, Lambda

---

## 🆘 Troubleshooting

### "Bedrock model not accessible"
**Fix:** Wait 5-10 minutes after requesting access, then retry

### "S3 access denied"
**Fix:** Check IAM user has S3 permissions

### "Frontend can't connect to backend"
**Fix:** 
1. Verify backend running on port 5000
2. Check `NEXT_PUBLIC_API_URL` in frontend/.env

### "High costs"
**Fix:**
1. Check `.\scripts\check_aws_costs.ps1`
2. Switch to Claude Haiku (cheaper)
3. Review CloudWatch logs for excessive calls

---

## 📚 Additional Resources

- **Full Setup Guide:** `docs/AWS_SETUP_GUIDE.md`
- **Detailed Checklist:** `AWS_SETUP_CHECKLIST.md`
- **Cost Optimization:** `docs/COST_OPTIMIZATION.md`
- **Architecture:** `docs/architecture.md`

---

## 💡 Pro Tips

1. **Test with mock data first** (set `BEDROCK_MODEL_ID=mock` in .env)
2. **Monitor costs daily** during development
3. **Use browser Speech API** (free) instead of AWS Transcribe
4. **Cache common queries** to reduce API calls
5. **Pre-test demo queries** before hackathon presentation

---

## 🎯 Next Steps

1. ✅ Complete this setup
2. Test all features thoroughly
3. Prepare 5-10 demo queries
4. Practice hackathon presentation
5. Monitor costs daily

---

## 📞 Need Help?

- **AWS Console:** https://console.aws.amazon.com/
- **Billing Dashboard:** https://console.aws.amazon.com/billing/
- **Cost Explorer:** https://console.aws.amazon.com/cost-management/

---

**Good luck with your hackathon! 🚀**

**Estimated Total Time:** 45-60 minutes  
**Estimated Monthly Cost:** $2-5
