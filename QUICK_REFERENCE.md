# 🎯 Quick Reference Card

## 🔑 Your Key Information

```
Lambda API URL:
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com

Vercel Site:
https://jan-sathi-five.vercel.app

Lambda Function:
jansathi-backend

Region:
us-east-1
```

---

## ⚡ Quick Commands

### Get API URL
```powershell
aws apigatewayv2 get-apis --region us-east-1 --query "Items[?Name=='jansathi-api'].ApiEndpoint" --output text
```

### Update Lambda CORS
```powershell
aws lambda update-function-configuration --function-name jansathi-backend --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" --region us-east-1
```

### View Lambda Logs
```powershell
aws logs tail /aws/lambda/jansathi-backend --follow --region us-east-1
```

### Test API
```powershell
curl https://b0z0h6knui.execute-api.us-east-1.amazonaws.com/query -X POST -H "Content-Type: application/json" -d '{\"text_query\": \"test\", \"language\": \"hi\"}'
```

---

## 📋 3-Step Connection

### 1. Update Vercel
- Go to: https://vercel.com/dashboard
- Settings → Environment Variables
- Set: `NEXT_PUBLIC_API_URL` = `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
- Deployments → Redeploy

### 2. Update Lambda CORS
```powershell
aws lambda update-function-configuration --function-name jansathi-backend --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" --region us-east-1
```

### 3. Test
- Open: https://jan-sathi-five.vercel.app
- Press F12 → Network tab
- Try chat feature
- Verify API calls go to Lambda

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| CORS Error | Run Lambda CORS update command |
| 502 Bad Gateway | Check Lambda logs |
| Still using localhost | Clear browser cache (Ctrl+Shift+Delete) |
| Env var not updating | Redeploy Vercel after saving |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `CONNECTION_SUMMARY.md` | Overview of everything |
| `QUICK_START_CONNECTION.md` | Simple 3-step guide |
| `VERCEL_UPDATE_STEPS.md` | Detailed Vercel instructions |
| `YOUR_API_CONNECTION_INFO.md` | Your specific API info |
| `ARCHITECTURE_DIAGRAM.md` | System architecture |
| `CONNECT_VERCEL_TO_LAMBDA.md` | Complete technical guide |

---

## ✅ Success Checklist

- [ ] Vercel env var updated
- [ ] Vercel redeployed
- [ ] Lambda CORS updated
- [ ] Site tested
- [ ] No CORS errors
- [ ] Chat works
- [ ] Knowledge Base works

---

## 🎯 Expected Results

✅ Chat responds with AI answers
✅ Network tab shows Lambda URL
✅ No CORS errors
✅ Knowledge Base works
✅ Fast responses

---

**Copy This URL:**
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

**Paste It In:**
Vercel → Settings → Environment Variables → NEXT_PUBLIC_API_URL
