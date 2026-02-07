# ✅ JanSathi AWS Setup Checklist

## Pre-Setup (5 minutes)

- [ ] AWS Account created with $100 credits
- [ ] Credit card added (required for AWS, won't be charged if within free tier)
- [ ] AWS CLI installed (`aws --version` works)
- [ ] Git repository cloned locally

---

## Step 1: AWS CLI Configuration (5 minutes)

### 1.1 Create IAM User
- [ ] Go to AWS Console → IAM → Users
- [ ] Click "Create User"
- [ ] Username: `jansathi-app`
- [ ] Enable "Programmatic access"
- [ ] Attach policy: `PowerUserAccess` (or use custom policy from docs)
- [ ] **SAVE** Access Key ID and Secret Access Key

### 1.2 Configure AWS CLI
```bash
aws configure
```
- [ ] Enter Access Key ID
- [ ] Enter Secret Access Key
- [ ] Region: `us-east-1`
- [ ] Output format: `json`

### 1.3 Verify Configuration
```bash
aws sts get-caller-identity
```
- [ ] Should show your account ID and user ARN

---

## Step 2: Enable Bedrock Models (10 minutes)

⚠️ **CRITICAL: This must be done manually in AWS Console**

### 2.1 Request Model Access
- [ ] Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
- [ ] Click "Manage model access"
- [ ] Select these models:
  - [ ] ✅ **Anthropic Claude 3 Haiku** (anthropic.claude-3-haiku-20240307-v1:0)
  - [ ] ✅ **Anthropic Claude 3 Sonnet** (anthropic.claude-3-sonnet-20240229-v1:0)
- [ ] Click "Request model access"
- [ ] Wait 2-5 minutes for approval (usually instant)
- [ ] Refresh page and verify "Access granted" status

### 2.2 Verify Bedrock Access
```bash
aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?contains(modelId, 'claude-3')].modelId"
```
- [ ] Should list Claude 3 models

---

## Step 3: Create S3 Bucket (2 minutes)

### Option A: Automated (Recommended)
```powershell
cd scripts
.\setup_aws.ps1
```
- [ ] Script completes successfully
- [ ] Note the bucket name created

### Option B: Manual
```bash
# Create unique bucket name
$BUCKET_NAME = "jansathi-audio-bucket-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Apply lifecycle policy (auto-delete after 1 day)
aws s3api put-bucket-lifecycle-configuration \
  --bucket $BUCKET_NAME \
  --lifecycle-configuration file://backend/lifecycle.json
```
- [ ] Bucket created successfully
- [ ] Lifecycle policy applied

---

## Step 4: Configure Environment Variables (3 minutes)

### 4.1 Copy Example File
```bash
cd backend
cp .env.example .env
```

### 4.2 Edit `.env` File
Open `backend/.env` and update:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIA...           # ← Your IAM access key
AWS_SECRET_ACCESS_KEY=...           # ← Your IAM secret key
AWS_REGION=us-east-1

# S3 Bucket
S3_BUCKET_NAME=jansathi-audio-bucket-XXXXXXXX  # ← From Step 3

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Kendra (DISABLED to save costs)
KENDRA_INDEX_ID=mock-index

# Flask
SECRET_KEY=your-random-secret-key-here  # ← Generate random string
NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=sqlite:///jansathi.db
```

- [ ] All values updated
- [ ] File saved

### 4.3 Verify .env File
```bash
cat backend/.env | grep -E "AWS_ACCESS_KEY_ID|S3_BUCKET_NAME"
```
- [ ] Shows your values (not example values)

---

## Step 5: Install Dependencies (5 minutes)

### 5.1 Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```
- [ ] All packages installed successfully
- [ ] No error messages

### 5.2 Frontend Dependencies
```bash
cd frontend
npm install
```
- [ ] All packages installed successfully
- [ ] No error messages

---

## Step 6: Test AWS Services (5 minutes)

### 6.1 Run Test Script
```bash
cd scripts
python test_aws_services.py
```

Expected output:
- [ ] ✅ Environment Variables: All set
- [ ] ✅ Bedrock: Response received
- [ ] ✅ Polly: Audio URL generated
- [ ] ✅ RAG: Documents retrieved
- [ ] ✅ S3: Read/Write/Delete OK
- [ ] ✅ Transcribe: Client initialized

### 6.2 Manual Backend Test
```bash
cd backend
python main.py
```
- [ ] Server starts on port 5000
- [ ] No error messages
- [ ] Visit http://localhost:5000/health
- [ ] Should return: `{"status": "healthy"}`

---

## Step 7: Test Full Application (5 minutes)

### 7.1 Start Backend
```bash
# Terminal 1
cd backend
python main.py
```
- [ ] Backend running on http://localhost:5000

### 7.2 Start Frontend
```bash
# Terminal 2
cd frontend
npm run dev
```
- [ ] Frontend running on http://localhost:3000

### 7.3 Test Features
- [ ] Open http://localhost:3000
- [ ] Landing page loads
- [ ] Click "Start Talking" → Dashboard opens
- [ ] Type a test query: "What is PM Kisan?"
- [ ] AI responds with formatted answer
- [ ] Audio player appears (if Polly working)
- [ ] Scheme card displays
- [ ] Try voice input (click microphone)
- [ ] Upload a test image (Documents page)

---

## Step 8: Set Up Cost Monitoring (5 minutes)

### 8.1 Create Budget Alert
- [ ] Go to: https://console.aws.amazon.com/billing/home#/budgets
- [ ] Click "Create budget"
- [ ] Budget type: **Cost budget**
- [ ] Budget name: `JanSathi-Monthly`
- [ ] Period: **Monthly**
- [ ] Budgeted amount: `$10.00`
- [ ] Alert threshold: **80%** (triggers at $8)
- [ ] Email: Your email address
- [ ] Click "Create budget"

### 8.2 Enable Cost Explorer
- [ ] Go to: https://console.aws.amazon.com/cost-management/home
- [ ] Enable Cost Explorer (if not already enabled)
- [ ] Bookmark for daily checks

### 8.3 Test Cost Monitoring Script
```powershell
cd scripts
.\check_aws_costs.ps1
```
- [ ] Shows current spending
- [ ] Shows service breakdown
- [ ] No errors

---

## Step 9: Security Hardening (5 minutes)

### 9.1 Verify .gitignore
```bash
cat .gitignore | grep ".env"
```
- [ ] `.env` is listed (should NOT be committed)

### 9.2 Enable MFA (Recommended)
- [ ] Go to IAM → Users → Your User → Security Credentials
- [ ] Enable MFA device
- [ ] Use Google Authenticator or similar app

### 9.3 Review IAM Permissions
- [ ] IAM user has minimal required permissions
- [ ] No `AdministratorAccess` policy attached

---

## Step 10: Final Verification (5 minutes)

### 10.1 End-to-End Test
- [ ] Ask 5 different questions in the chat
- [ ] Upload 2 test images for analysis
- [ ] Check voice input works
- [ ] Verify audio responses play
- [ ] Check conversation history saves

### 10.2 Check AWS Console
- [ ] S3 bucket has audio files
- [ ] CloudWatch logs show Lambda invocations (if using Lambda)
- [ ] No error messages in logs

### 10.3 Cost Check
```powershell
.\scripts\check_aws_costs.ps1
```
- [ ] Current spending: < $1.00
- [ ] All services showing minimal usage

---

## 🎉 Setup Complete!

### What You Have Now:
✅ AWS Bedrock (Claude 3) for AI responses  
✅ AWS Polly for text-to-speech  
✅ AWS Transcribe for speech-to-text  
✅ S3 bucket with auto-cleanup  
✅ Cost monitoring and alerts  
✅ Full-stack application running locally  

### Expected Costs (Demo Usage):
- **First month:** $2-5 (mostly Bedrock)
- **Ongoing:** $2-5/month
- **Free tier covers:** Polly, Transcribe, S3, Lambda

### Next Steps:
1. Test thoroughly before hackathon demo
2. Monitor costs daily during development
3. Consider deploying to Vercel (frontend) + AWS Lambda (backend)
4. Prepare demo script with pre-tested queries

---

## 🆘 Troubleshooting

### Issue: "Bedrock model not accessible"
**Solution:** Wait 5-10 minutes after requesting model access, then retry

### Issue: "S3 bucket access denied"
**Solution:** Check IAM permissions include `s3:PutObject`, `s3:GetObject`

### Issue: "Transcribe job failed"
**Solution:** Verify audio file is valid WAV format, check S3 upload succeeded

### Issue: "High costs"
**Solution:** 
1. Switch to Claude Haiku (cheaper)
2. Reduce response length (max_tokens)
3. Check for infinite loops in code
4. Review CloudWatch logs for excessive calls

### Issue: "Frontend can't connect to backend"
**Solution:** 
1. Check backend is running on port 5000
2. Verify CORS settings in `backend/main.py`
3. Check `NEXT_PUBLIC_API_URL` in frontend

---

## 📞 Support Resources

- **AWS Free Tier:** https://aws.amazon.com/free/
- **Bedrock Pricing:** https://aws.amazon.com/bedrock/pricing/
- **AWS Support:** https://console.aws.amazon.com/support/
- **Project Docs:** `docs/AWS_SETUP_GUIDE.md`

---

**Estimated Total Setup Time:** 45-60 minutes

**Good luck with your hackathon! 🚀**
