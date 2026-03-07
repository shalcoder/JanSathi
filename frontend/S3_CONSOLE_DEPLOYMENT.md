# S3 Deployment via AWS Console + CloudShell

## Bucket Name: `frontend-jansathi`

## Method: Upload ZIP → Extract in CloudShell → Deploy

This method is easier than CLI and works great for initial deployment!

---

## Step 1: Create ZIP File (On Your Computer)

Run this PowerShell command in the frontend folder:

```powershell
Compress-Archive -Path out\* -DestinationPath frontend-jansathi.zip -Force
```

This creates `frontend-jansathi.zip` with all your static files.

---

## Step 2: Create S3 Bucket (AWS Console)

1. Go to AWS Console: https://console.aws.amazon.com/s3/
2. Click **"Create bucket"**
3. Settings:
   - **Bucket name**: `frontend-jansathi`
   - **Region**: `US East (N. Virginia) us-east-1`
   - **Block Public Access**: UNCHECK "Block all public access" ⚠️
   - Check the acknowledgment box
   - Leave other settings as default
4. Click **"Create bucket"**

---

## Step 3: Enable Static Website Hosting

1. Click on your bucket `frontend-jansathi`
2. Go to **Properties** tab
3. Scroll down to **Static website hosting**
4. Click **Edit**
5. Settings:
   - **Static website hosting**: Enable
   - **Hosting type**: Host a static website
   - **Index document**: `index.html`
   - **Error document**: `404.html`
6. Click **Save changes**
7. **Note the website endpoint** (you'll see it at the bottom):
   ```
   http://frontend-jansathi.s3-website-us-east-1.amazonaws.com
   ```

---

## Step 4: Upload ZIP to S3

1. Stay in your bucket `frontend-jansathi`
2. Go to **Objects** tab
3. Click **Upload**
4. Click **Add files**
5. Select `frontend-jansathi.zip` from your computer
6. Click **Upload**
7. Wait for upload to complete

---

## Step 5: Extract ZIP in CloudShell

1. In AWS Console, click the **CloudShell icon** (terminal icon in top right)
2. Wait for CloudShell to start
3. Run these commands:

```bash
# Download the ZIP from S3
aws s3 cp s3://frontend-jansathi/frontend-jansathi.zip .

# Create a temp directory
mkdir temp-extract
cd temp-extract

# Extract the ZIP
unzip ../frontend-jansathi.zip

# Upload all files back to S3 root (not in a folder)
aws s3 sync . s3://frontend-jansathi/ --delete

# Go back and clean up
cd ..
rm -rf temp-extract frontend-jansathi.zip

# Remove the ZIP from S3 (we don't need it anymore)
aws s3 rm s3://frontend-jansathi/frontend-jansathi.zip

# Verify files are there
aws s3 ls s3://frontend-jansathi/
```

You should see output like:
```
2026-03-07 12:34:56       1234 404.html
2026-03-07 12:34:56       5678 index.html
2026-03-07 12:34:56       2345 chat.html
...
```

---

## Step 6: Set Bucket Policy (Make it Public)

1. In your bucket, go to **Permissions** tab
2. Scroll to **Bucket policy**
3. Click **Edit**
4. Paste this policy:

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

5. Click **Save changes**

---

## Step 7: Test Your Website! 🎉

Visit your website at:
```
http://frontend-jansathi.s3-website-us-east-1.amazonaws.com
```

Test these pages:
- Homepage: `/`
- Chat: `/chat.html`
- Dashboard: `/dashboard.html`
- Knowledge Base: `/knowledge-base.html` ✨
- Admin: `/admin/dashboard.html`

---

## Alternative: Direct Upload (No ZIP)

If you prefer, you can also:

1. Go to S3 bucket → Objects → Upload
2. Click **Add files** or **Add folder**
3. Select ALL files from the `out/` folder
4. Make sure to preserve folder structure (admin/, auth/, icons/, _next/)
5. Click Upload

This works but takes longer for many files.

---

## Updating Your Site Later

When you make changes:

1. Rebuild: `npm run build`
2. Extract static: `.\extract-static.ps1`
3. Create new ZIP: `Compress-Archive -Path out\* -DestinationPath frontend-jansathi.zip -Force`
4. Upload ZIP to S3
5. In CloudShell:
   ```bash
   aws s3 cp s3://frontend-jansathi/frontend-jansathi.zip .
   mkdir temp && cd temp
   unzip ../frontend-jansathi.zip
   aws s3 sync . s3://frontend-jansathi/ --delete
   cd .. && rm -rf temp frontend-jansathi.zip
   aws s3 rm s3://frontend-jansathi/frontend-jansathi.zip
   ```

---

## Cost Estimate

- **S3 Storage**: ~$0.023 per GB/month (your site is ~10-20 MB = $0.001/month)
- **S3 Requests**: ~$0.0004 per 1,000 requests
- **Data Transfer**: First 1 GB free/month

**Expected cost: Less than $1/month** for moderate traffic

---

## Troubleshooting

### Website shows 403 Forbidden
- Check bucket policy is applied correctly
- Verify "Block Public Access" is OFF
- Make sure files are in bucket root (not in a subfolder)

### Website shows 404 Not Found
- Verify `index.html` exists in bucket root
- Check static website hosting is enabled
- Try accessing directly: `http://frontend-jansathi.s3-website-us-east-1.amazonaws.com/index.html`

### Files are in wrong location
- Files should be in bucket root: `s3://frontend-jansathi/index.html`
- NOT in a subfolder: `s3://frontend-jansathi/out/index.html` ❌

### CloudShell commands fail
- Make sure you're in the correct region (us-east-1)
- Verify your AWS user has S3 permissions
- Check bucket name is spelled correctly

---

## Next Steps After Frontend Deployment

Once your frontend is live:

1. ✅ Test all pages work
2. ✅ Verify Knowledge Base page loads
3. 🔄 Deploy backend to AWS (Lambda + API Gateway or EC2)
4. 🔄 Update frontend API URL to point to AWS backend
5. 🔄 Set up CloudFront for HTTPS + custom domain (optional)

Let me know when frontend is live and we'll move to backend deployment!
