# Quick Start: Connect Vercel to Lambda

## 🎯 Goal
Connect your Vercel frontend to your AWS Lambda backend in 3 simple steps.

---

## Step 1: Get Lambda API URL

Run this PowerShell script:

```powershell
cd D:\Documents\Hackathons\Ai_for_Bharat\JanSathi
.\get-lambda-url.ps1
```

This will:
- ✅ Find your API Gateway URL
- ✅ Test if it's working
- ✅ Create API Gateway if missing
- ✅ Show you the URL to use

**Copy the URL** that looks like: `https://abc123xyz.execute-api.us-east-1.amazonaws.com`

---

## Step 2: Update Vercel Environment Variable

### Option A: Vercel Dashboard (Easiest)

1. Go to: https://vercel.com/dashboard
2. Click on your **JanSathi** project
3. Click **Settings** (top menu)
4. Click **Environment Variables** (left sidebar)
5. Look for `NEXT_PUBLIC_API_URL`:
   - If it exists: Click **Edit** → Paste your Lambda URL → **Save**
   - If it doesn't exist: Click **Add New** → Name: `NEXT_PUBLIC_API_URL` → Value: Your Lambda URL → **Save**
6. Go to **Deployments** tab
7. Click the **⋯** (three dots) on the latest deployment
8. Click **Redeploy** → **Redeploy**

### Option B: Vercel CLI (Alternative)

```powershell
cd JanSathi\frontend

# Install Vercel CLI (if not installed)
npm i -g vercel

# Login to Vercel
vercel login

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production
# When prompted, paste your Lambda URL

# Redeploy
vercel --prod
```

---

## Step 3: Test Your Site

1. Wait 1-2 minutes for Vercel to redeploy
2. Open your site: https://jan-sathi-five.vercel.app
3. Try the chat feature
4. Check if it's working!

### How to verify it's connected:

1. Open browser DevTools (Press F12)
2. Go to **Network** tab
3. Use the chat feature
4. Look for API calls - they should go to your Lambda URL (not localhost)

---

## 🔧 Troubleshooting

### Issue: "Network Error" or "Failed to fetch"

**Cause:** CORS not configured on Lambda

**Fix:** Update Lambda CORS settings

```powershell
aws lambda update-function-configuration `
  --function-name jansathi-backend `
  --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" `
  --region us-east-1
```

### Issue: "502 Bad Gateway"

**Cause:** Lambda function issue

**Fix:** Check Lambda logs

```powershell
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

### Issue: Script says "API Gateway not found"

**Fix:** The script will automatically create it for you! Just run it again.

### Issue: Script says "Lambda function not found"

**Fix:** Deploy your Lambda function first:

```powershell
cd JanSathi\backend
python create_minimal_package.py
# Then follow the upload instructions in JANSATHI_DEPLOYMENT_GUIDE.md
```

---

## 📊 Verify Everything is Working

Run these tests:

```powershell
# Test 1: Health check
curl https://YOUR_API_URL/health

# Test 2: Query endpoint
curl -X POST https://YOUR_API_URL/query `
  -H "Content-Type: application/json" `
  -d '{"text_query": "pradhan mantri awas yojana", "language": "hi"}'

# Test 3: Knowledge Base health
curl https://YOUR_API_URL/api/kb/health
```

All should return JSON responses (not errors).

---

## 🎉 Success Checklist

- [ ] Ran `get-lambda-url.ps1` and got API URL
- [ ] Updated `NEXT_PUBLIC_API_URL` in Vercel
- [ ] Redeployed Vercel site
- [ ] Tested chat feature on live site
- [ ] Verified API calls go to Lambda (not localhost)
- [ ] Knowledge Base features work

---

## 📚 More Help

- **Detailed Guide:** See `CONNECT_VERCEL_TO_LAMBDA.md`
- **Full Deployment:** See `JANSATHI_DEPLOYMENT_GUIDE.md`
- **Knowledge Base:** See `backend/KNOWLEDGE_BASE_IMPLEMENTATION.md`

---

## 🚀 What's Next?

After successful connection:

1. Test all features thoroughly
2. Monitor Lambda logs for errors
3. Set up CloudWatch alarms
4. Configure custom domain (optional)
5. Enable Lambda function URL for direct access (optional)

---

**Last Updated:** 2026-03-08
