# 📱 Step-by-Step: Update Vercel Environment Variable

## Your Lambda API URL:
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

---

## 🎯 Visual Guide

### Step 1: Open Vercel Dashboard

1. Go to: **https://vercel.com/dashboard**
2. You should see your projects list

### Step 2: Select Your Project

1. Look for your project (might be named `JanSathi` or `jan-sathi-five`)
2. Click on the project name

### Step 3: Go to Settings

1. At the top of the page, you'll see tabs: **Overview**, **Deployments**, **Analytics**, **Settings**
2. Click on **Settings**

### Step 4: Open Environment Variables

1. On the left sidebar, you'll see:
   - General
   - Domains
   - **Environment Variables** ← Click this
   - Git
   - Functions
   - etc.

### Step 5: Find or Add NEXT_PUBLIC_API_URL

**If the variable already exists:**

1. Look for `NEXT_PUBLIC_API_URL` in the list
2. Click the **Edit** button (pencil icon) next to it
3. Change the value to: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
4. Make sure **Production** is checked
5. Click **Save**

**If the variable doesn't exist:**

1. Click the **Add New** button (top right)
2. In the popup:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
   - **Environment:** Check **Production** (and optionally Preview, Development)
3. Click **Save**

### Step 6: Redeploy Your Site

1. Click on **Deployments** tab (top menu)
2. You'll see a list of your deployments
3. Find the most recent one (at the top)
4. Click the **⋯** (three dots) button on the right side
5. Click **Redeploy**
6. A popup will appear - click **Redeploy** again to confirm
7. Wait 1-2 minutes for the deployment to complete

### Step 7: Verify Deployment

1. Once deployment is complete, you'll see a green checkmark
2. Click **Visit** to open your site
3. Or go directly to: https://jan-sathi-five.vercel.app

---

## ✅ How to Verify It's Working

### Method 1: Browser DevTools

1. Open your Vercel site
2. Press **F12** to open DevTools
3. Click the **Network** tab
4. Try using the chat feature (type a question)
5. Look at the network requests:
   - ✅ Good: You see requests to `b0z0h6knui.execute-api.us-east-1.amazonaws.com`
   - ❌ Bad: You see requests to `localhost:5010` or errors

### Method 2: Check Console

1. In DevTools, click the **Console** tab
2. Look for any errors:
   - ✅ Good: No CORS errors, no "Failed to fetch" errors
   - ❌ Bad: Red error messages about CORS or network

### Method 3: Test Features

1. Try the chat feature - does it respond?
2. Try uploading a PDF to Knowledge Base
3. Try querying the Knowledge Base
4. All should work without errors

---

## 🔧 If It's Not Working

### Issue 1: Still seeing localhost in Network tab

**Solution:** Clear browser cache

1. Press **Ctrl + Shift + Delete**
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh the page with **Ctrl + Shift + R**

### Issue 2: CORS Error in Console

**Solution:** Update Lambda CORS settings

```powershell
aws lambda update-function-configuration `
  --function-name jansathi-backend `
  --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" `
  --region us-east-1
```

Wait 30 seconds, then refresh your site.

### Issue 3: 502 Bad Gateway

**Solution:** Check Lambda logs

```powershell
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

Look for error messages. Common issues:
- Missing dependencies
- Lambda timeout (increase to 60s)
- Memory too low (increase to 1024 MB)

### Issue 4: Environment variable not updating

**Solution:** Make sure you:

1. Saved the environment variable
2. Redeployed (not just saved)
3. Waited for deployment to complete
4. Cleared browser cache

---

## 📋 Quick Checklist

Before asking for help, verify:

- [ ] Environment variable is saved in Vercel
- [ ] Environment is set to "Production"
- [ ] Site has been redeployed after saving
- [ ] Deployment completed successfully (green checkmark)
- [ ] Browser cache has been cleared
- [ ] Lambda CORS has been updated
- [ ] Waited at least 30 seconds after Lambda update

---

## 🎉 Success!

You'll know everything is working when:

1. ✅ Chat responds with answers
2. ✅ Network tab shows API calls to Lambda (not localhost)
3. ✅ No CORS errors in console
4. ✅ Knowledge Base features work
5. ✅ All features respond quickly

---

## 📞 Still Stuck?

Run this diagnostic and share the output:

```powershell
# Check Vercel deployment
vercel env ls

# Check Lambda status
aws lambda get-function-configuration --function-name jansathi-backend --region us-east-1 --query 'Environment.Variables' --output json

# Test API directly
curl https://b0z0h6knui.execute-api.us-east-1.amazonaws.com/query -X POST -H "Content-Type: application/json" -d '{\"text_query\": \"test\", \"language\": \"hi\"}'
```

---

**Remember:** Your API URL is:
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

Copy this exactly into Vercel!
