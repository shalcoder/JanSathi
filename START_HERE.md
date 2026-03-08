# 🚀 START HERE - Connect Your Frontend to Backend

## 👋 Welcome!

Your JanSathi backend is already deployed on AWS Lambda, and your frontend is on Vercel. You just need to connect them!

---

## ⚡ Super Quick Start (5 minutes)

### Your Lambda API URL:
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

### What to do:

1. **Go to Vercel:** https://vercel.com/dashboard
2. **Select your project** (JanSathi or jan-sathi-five)
3. **Settings → Environment Variables**
4. **Add/Edit:** `NEXT_PUBLIC_API_URL` = `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
5. **Deployments → Redeploy**
6. **Done!** Test your site

---

## 📚 Documentation Guide

Choose based on your needs:

### 🎯 Just Want to Connect? (Recommended)
→ Read: **`QUICK_REFERENCE.md`** (1 page, all commands)

### 📱 Need Step-by-Step Vercel Instructions?
→ Read: **`VERCEL_UPDATE_STEPS.md`** (detailed with screenshots guide)

### 🔍 Want to Understand Everything?
→ Read: **`CONNECTION_SUMMARY.md`** (complete overview)

### 🏗️ Want to See the Architecture?
→ Read: **`ARCHITECTURE_DIAGRAM.md`** (visual diagrams)

### 🛠️ Need Technical Details?
→ Read: **`CONNECT_VERCEL_TO_LAMBDA.md`** (full technical guide)

### 📋 Your Specific Info?
→ Read: **`YOUR_API_CONNECTION_INFO.md`** (your API URL + troubleshooting)

### 📖 Complete Deployment Guide?
→ Read: **`JANSATHI_DEPLOYMENT_GUIDE.md`** (full AWS deployment)

---

## 🎯 What You're Doing

```
Current State:
Vercel Frontend → localhost:5010 ❌ (doesn't work)

Target State:
Vercel Frontend → Lambda API ✅ (works!)
```

---

## ⚡ Quick Commands

### Update Lambda CORS (copy-paste this):
```powershell
aws lambda update-function-configuration --function-name jansathi-backend --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" --region us-east-1
```

### View Lambda Logs:
```powershell
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

### Test API:
```powershell
curl https://b0z0h6knui.execute-api.us-east-1.amazonaws.com/query -X POST -H "Content-Type: application/json" -d '{\"text_query\": \"test\", \"language\": \"hi\"}'
```

---

## ✅ Success Checklist

After updating Vercel and Lambda:

- [ ] Open https://jan-sathi-five.vercel.app
- [ ] Press F12 → Network tab
- [ ] Try chat feature
- [ ] See API calls to `b0z0h6knui.execute-api.us-east-1.amazonaws.com`
- [ ] No CORS errors in console
- [ ] Chat responds with answers
- [ ] Knowledge Base works

---

## 🐛 Common Issues

### "CORS Error"
→ Run the Lambda CORS update command above

### "502 Bad Gateway"
→ Check Lambda logs (command above)

### "Still using localhost"
→ Clear browser cache: Ctrl+Shift+Delete

### "Environment variable not updating"
→ Make sure you redeployed Vercel after saving

---

## 📞 Need Help?

1. Check **`QUICK_REFERENCE.md`** for quick commands
2. Check **`YOUR_API_CONNECTION_INFO.md`** for troubleshooting
3. Check Lambda logs for errors
4. Share error messages from browser console

---

## 🎉 What You'll Get

Once connected:

- ✅ Working chat with AI responses
- ✅ Knowledge Base with PDF upload
- ✅ 85% cost reduction with intelligent caching
- ✅ Production-ready deployment
- ✅ Scalable architecture

---

## 📋 File Index

| File | What It Does |
|------|--------------|
| **START_HERE.md** | This file - your starting point |
| **QUICK_REFERENCE.md** | One-page quick reference |
| **CONNECTION_SUMMARY.md** | Complete overview |
| **VERCEL_UPDATE_STEPS.md** | Step-by-step Vercel guide |
| **YOUR_API_CONNECTION_INFO.md** | Your specific API info |
| **ARCHITECTURE_DIAGRAM.md** | System architecture |
| **CONNECT_VERCEL_TO_LAMBDA.md** | Technical guide |
| **JANSATHI_DEPLOYMENT_GUIDE.md** | Full deployment guide |
| **get-lambda-url.ps1** | PowerShell script to find API URL |

---

## 🚀 Ready? Let's Go!

1. Copy your API URL: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
2. Go to Vercel: https://vercel.com/dashboard
3. Update environment variable
4. Redeploy
5. Test!

**Estimated Time:** 5 minutes

---

**Your Lambda API URL (copy this):**
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

**Good luck! 🎉**
