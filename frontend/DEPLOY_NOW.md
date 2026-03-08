# 🚀 Deploy Frontend to S3 - Quick Guide

## ✅ Ready to Deploy!

**Bucket Name**: `frontend-jansathi`  
**ZIP File**: `frontend-jansathi.zip` (0.74 MB) ✅  
**Location**: `D:\Documents\Hackathons\Ai_for_Bharat\JanSathi\frontend\frontend-jansathi.zip`

---

## 📋 Deployment Steps (5 minutes)

### 1️⃣ Create S3 Bucket
- Go to: https://console.aws.amazon.com/s3/
- Click **Create bucket**
- Name: `frontend-jansathi`
- Region: `US East (N. Virginia)`
- **UNCHECK** "Block all public access" ⚠️
- Click **Create bucket**

### 2️⃣ Enable Website Hosting
- Click bucket → **Properties** tab
- Scroll to **Static website hosting** → **Edit**
- Enable it
- Index: `index.html`
- Error: `404.html`
- **Save** and note the endpoint URL

### 3️⃣ Upload ZIP
- Go to **Objects** tab
- Click **Upload** → **Add files**
- Select `frontend-jansathi.zip`
- Click **Upload**

### 4️⃣ Extract in CloudShell
Click CloudShell icon (top right), then run:

```bash
aws s3 cp s3://frontend-jansathi/frontend-jansathi.zip .
mkdir temp && cd temp
unzip ../frontend-jansathi.zip
aws s3 sync . s3://frontend-jansathi/ --delete
cd .. && rm -rf temp frontend-jansathi.zip
aws s3 rm s3://frontend-jansathi/frontend-jansathi.zip
```

### 5️⃣ Make Public
- Go to **Permissions** tab
- Click **Bucket policy** → **Edit**
- Paste this (already has your bucket name):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::frontend-jansathi/*"
    }
  ]
}
```

- Click **Save**

### 6️⃣ Visit Your Site! 🎉
```
http://frontend-jansathi.s3-website-us-east-1.amazonaws.com
```

---

## 🧪 Test These Pages

- ✅ Homepage: `/`
- ✅ Chat: `/chat.html`
- ✅ Dashboard: `/dashboard.html`
- ✅ Knowledge Base: `/knowledge-base.html`
- ✅ Admin: `/admin/dashboard.html`

---

## 💰 Cost
Less than **$1/month** for moderate traffic

---

## 🔧 Need Help?

**403 Forbidden?**
- Check bucket policy is applied
- Verify "Block Public Access" is OFF

**404 Not Found?**
- Verify website hosting is enabled
- Check files are in bucket root (not in subfolder)

**CloudShell issues?**
- Make sure you're in us-east-1 region
- Verify AWS permissions

---

## 📚 Full Guide
See `S3_CONSOLE_DEPLOYMENT.md` for detailed instructions

---

## ⏭️ After Deployment

1. Test all pages work
2. Deploy backend to AWS
3. Update API URL in frontend
4. Optional: Add CloudFront for HTTPS

Let me know when it's live! 🚀
