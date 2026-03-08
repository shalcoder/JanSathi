# 🎯 Your JanSathi API Connection Info

## ✅ Found Your Lambda API Gateway!

```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

---

## 📋 Next Steps to Connect Vercel to Lambda

### Step 1: Update Vercel Environment Variable

**Go to Vercel Dashboard:**

1. Open: https://vercel.com/dashboard
2. Click on your **JanSathi** project (or jan-sathi-five)
3. Click **Settings** in the top menu
4. Click **Environment Variables** in the left sidebar
5. Find or add `NEXT_PUBLIC_API_URL`:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
   - **Environment:** Production (check the box)
6. Click **Save**

### Step 2: Redeploy Vercel

1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the **⋯** (three dots) button
4. Click **Redeploy**
5. Wait 1-2 minutes for deployment to complete

---

## ⚠️ Important: Fix Lambda CORS

Your Lambda needs to allow requests from Vercel. Run this command:

```powershell
aws lambda update-function-configuration `
  --function-name jansathi-backend `
  --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" `
  --region us-east-1
```

**Or if you have a different Vercel domain, update it:**

```powershell
aws lambda update-function-configuration `
  --function-name jansathi-backend `
  --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://YOUR-VERCEL-DOMAIN.vercel.app,http://localhost:3000}" `
  --region us-east-1
```

---

## 🧪 Test Your Connection

After updating Vercel and Lambda CORS:

### Test 1: Open Your Vercel Site

```
https://jan-sathi-five.vercel.app
```

### Test 2: Check Browser Console

1. Press **F12** to open DevTools
2. Go to **Network** tab
3. Try using the chat feature
4. Look for API calls to `b0z0h6knui.execute-api.us-east-1.amazonaws.com`
5. Check if they return 200 status (not 500 or CORS errors)

### Test 3: Direct API Test

```powershell
# Test query endpoint
curl -X POST https://b0z0h6knui.execute-api.us-east-1.amazonaws.com/query `
  -H "Content-Type: application/json" `
  -d '{\"text_query\": \"pradhan mantri awas yojana\", \"language\": \"hi\"}'
```

---

## 🔍 Current Status

- ✅ Lambda Function: `jansathi-backend` (Active)
- ✅ API Gateway: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
- ✅ Runtime: Python 3.11
- ✅ Last Updated: 2026-03-08 06:25:38 UTC
- ⚠️ Health endpoint returns error (might be normal if route not configured)
- ❌ Frontend still pointing to localhost (needs update)

---

## 🐛 Troubleshooting

### If you get CORS errors:

Make sure you ran the CORS update command above and wait 30 seconds for Lambda to update.

### If you get 502 Bad Gateway:

Check Lambda logs:

```powershell
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

### If Vercel still uses localhost:

1. Make sure you saved the environment variable in Vercel
2. Make sure you redeployed (not just saved)
3. Clear browser cache and hard refresh (Ctrl+Shift+R)

### If Knowledge Base doesn't work:

Make sure Lambda has Bedrock permissions:

1. Go to: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/jansathi-backend
2. Click **Configuration** → **Permissions**
3. Click on the execution role name
4. Click **Add permissions** → **Attach policies**
5. Search for `AmazonBedrockFullAccess` and attach it

---

## 📝 Summary of Changes Needed

### In Vercel Dashboard:
- [ ] Set `NEXT_PUBLIC_API_URL` = `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
- [ ] Redeploy the site

### In AWS Lambda:
- [ ] Update CORS to allow your Vercel domain
- [ ] Verify Bedrock permissions are attached

### Testing:
- [ ] Open Vercel site and test chat
- [ ] Check browser console for API calls
- [ ] Verify no CORS errors
- [ ] Test Knowledge Base features

---

## 🎉 Success Criteria

You'll know it's working when:

1. ✅ Chat feature responds with answers
2. ✅ Browser console shows API calls to `b0z0h6knui.execute-api.us-east-1.amazonaws.com`
3. ✅ No CORS errors in console
4. ✅ Knowledge Base upload and query work
5. ✅ No "localhost" references in Network tab

---

## 📞 Need More Help?

If you're stuck, share:

1. Screenshot of Vercel environment variables
2. Screenshot of browser console errors
3. Output of Lambda logs command

---

**Your API URL (copy this):**
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

**Last Updated:** 2026-03-08
