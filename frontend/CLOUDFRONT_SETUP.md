# CloudFront Setup for Full Next.js Routing

## Why CloudFront?

S3 alone doesn't support client-side routing (SPA behavior). CloudFront adds:
- ✅ Client-side routing support (no more 404s)
- ✅ HTTPS/SSL support
- ✅ Custom domain support
- ✅ Better performance (CDN caching)
- ✅ Lower costs (caching reduces S3 requests)

---

## Step 1: Create CloudFront Distribution

### Via AWS Console:

1. Go to **CloudFront** in AWS Console
2. Click **Create Distribution**

### Origin Settings:
- **Origin Domain**: Select your S3 bucket `frontend-jansathi` from dropdown
  - OR manually enter: `frontend-jansathi.s3-website-us-east-1.amazonaws.com`
- **Protocol**: HTTP only (S3 website endpoint uses HTTP)
- **Name**: `frontend-jansathi-origin`

### Default Cache Behavior:
- **Viewer Protocol Policy**: Redirect HTTP to HTTPS
- **Allowed HTTP Methods**: GET, HEAD, OPTIONS
- **Cache Policy**: CachingOptimized
- **Origin Request Policy**: CORS-S3Origin

### Settings:
- **Price Class**: Use all edge locations (or choose based on your region)
- **Alternate Domain Names (CNAMEs)**: Leave empty for now (add custom domain later)
- **Default Root Object**: `index.html`

### Custom Error Responses (CRITICAL for SPA routing):

Add these error responses:

**Error 1:**
- HTTP Error Code: `403`
- Customize Error Response: Yes
- Response Page Path: `/index.html`
- HTTP Response Code: `200`

**Error 2:**
- HTTP Error Code: `404`
- Customize Error Response: Yes
- Response Page Path: `/index.html`
- HTTP Response Code: `200`

3. Click **Create Distribution**
4. Wait 5-10 minutes for deployment (Status: "Deploying" → "Enabled")
5. **Copy the Distribution Domain Name** (e.g., `d1234abcd.cloudfront.net`)

---

## Step 2: Test Your CloudFront URL

Visit: `https://YOUR-DISTRIBUTION-ID.cloudfront.net`

Now test:
- Homepage: `https://YOUR-DISTRIBUTION-ID.cloudfront.net/`
- Click "Start Chat" - should work! ✅
- Dashboard: `https://YOUR-DISTRIBUTION-ID.cloudfront.net/dashboard`
- Knowledge Base: `https://YOUR-DISTRIBUTION-ID.cloudfront.net/knowledge-base`

All routes should work without `.html` extensions!

---

## Step 3: Update S3 Bucket Policy (If Needed)

If you get access denied errors, update your bucket policy:

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

---

## Step 4: Invalidate Cache (When You Update Files)

After uploading new files to S3, clear CloudFront cache:

### Via AWS Console:
1. Go to CloudFront → Your Distribution
2. Click **Invalidations** tab
3. Click **Create Invalidation**
4. Enter: `/*` (invalidates everything)
5. Click **Create**

### Via AWS CLI:
```bash
aws cloudfront create-invalidation --distribution-id YOUR-DIST-ID --paths "/*"
```

---

## Cost Estimate

**CloudFront Pricing:**
- First 10 TB/month: $0.085 per GB
- First 10 million requests: $0.0075 per 10,000 requests
- SSL certificate: FREE (AWS Certificate Manager)

**For moderate traffic (100 GB, 1M requests/month):**
- Data transfer: $8.50
- Requests: $0.75
- **Total: ~$9-10/month**

**For low traffic (10 GB, 100K requests/month):**
- Data transfer: $0.85
- Requests: $0.08
- **Total: ~$1-2/month**

---

## Optional: Add Custom Domain

### Step 1: Get SSL Certificate
1. Go to **AWS Certificate Manager** (ACM)
2. Request certificate for your domain (e.g., `jansathi.com`)
3. Verify domain ownership (DNS or email)

### Step 2: Update CloudFront
1. Edit your distribution
2. Add **Alternate Domain Name**: `jansathi.com`
3. Select your **SSL Certificate** from ACM
4. Save changes

### Step 3: Update DNS
Add CNAME record in your domain registrar:
```
Type: CNAME
Name: www (or @)
Value: d1234abcd.cloudfront.net
```

---

## Troubleshooting

### Routes still show 404:
- Check Custom Error Responses are configured correctly
- Verify both 403 and 404 redirect to `/index.html` with 200 status
- Wait for CloudFront deployment to complete

### Access Denied errors:
- Check S3 bucket policy allows public read
- Verify "Block Public Access" is OFF

### Old content showing:
- Create CloudFront invalidation for `/*`
- Wait 2-3 minutes for cache to clear

### HTTPS not working:
- Check Viewer Protocol Policy is "Redirect HTTP to HTTPS"
- Verify SSL certificate is attached (for custom domains)

---

## Quick Setup Commands

If you prefer CLI setup, here's the complete script:

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name frontend-jansathi.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html \
  --custom-error-responses \
    ErrorCode=403,ResponsePagePath=/index.html,ResponseCode=200 \
    ErrorCode=404,ResponsePagePath=/index.html,ResponseCode=200

# Get distribution ID from output, then invalidate cache
aws cloudfront create-invalidation \
  --distribution-id YOUR-DIST-ID \
  --paths "/*"
```

---

## Summary

✅ CloudFront enables full SPA routing  
✅ All Next.js features work (navigation, dynamic routes)  
✅ HTTPS enabled by default  
✅ Better performance with CDN caching  
✅ Ready for custom domain  

After CloudFront setup, your app will work exactly like it does on Vercel!
