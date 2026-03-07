# 🚀 Complete AWS Deployment Guide - JanSathi

Step-by-step guide to deploy the entire JanSathi application to AWS.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Frontend Deployment (AWS Amplify)](#frontend-deployment)
3. [Backend Deployment (Coming Next)](#backend-deployment)
4. [Database Setup](#database-setup)
5. [Domain Configuration](#domain-configuration)
6. [Monitoring & Logging](#monitoring)

---

## ✅ Prerequisites

### 1. AWS Account
- Create account at: https://aws.amazon.com
- Enable billing alerts
- Set up MFA for security

### 2. AWS CLI
```bash
# Install AWS CLI
# Windows (PowerShell):
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Mac:
brew install awscli

# Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

### 3. Configure AWS Credentials
```bash
aws configure

# Enter:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region: us-east-1
# Default output format: json
```

### 4. Git Repository
```bash
# Ensure code is in Git
cd JanSathi
git init
git add .
git commit -m "Initial commit"

# Push to GitHub (if not already)
git remote add origin https://github.com/yourusername/JanSathi.git
git push -u origin main
```

---

## 🎨 Frontend Deployment (AWS Amplify)

### Method 1: Via AWS Console (Easiest)

#### Step 1: Open AWS Amplify Console

1. Go to: https://console.aws.amazon.com/amplify/
2. Click **"New app"** → **"Host web app"**

#### Step 2: Connect Repository

1. **Select Git provider:** GitHub
2. **Authorize AWS Amplify** to access your repositories
3. **Select repository:** `JanSathi`
4. **Select branch:** `main`
5. Click **"Next"**

#### Step 3: Configure Build Settings

Amplify auto-detects Next.js. Verify settings:

**App name:** `jansathi-frontend`

**Build settings:** (Auto-detected, but verify)
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

**Root directory:** `frontend`

Click **"Next"**

#### Step 4: Add Environment Variables

Click **"Advanced settings"** → **"Add environment variable"**

Add these variables:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-api.com` (update later) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Your Clerk key |
| `NODE_ENV` | `production` |

Click **"Next"**

#### Step 5: Review and Deploy

1. Review all settings
2. Click **"Save and deploy"**
3. Wait for deployment (5-10 minutes)

#### Step 6: Get Your URL

Once deployed, you'll get a URL like:
```
https://main.d1234567890.amplifyapp.com
```

Test it in your browser!

### Method 2: Via AWS CLI

```bash
# Run the deployment script
cd frontend
chmod +x deploy-amplify.sh
./deploy-amplify.sh

# Follow the instructions printed by the script
```

---

## 🔧 Configure Custom Domain (Optional)

### Step 1: In Amplify Console

1. Go to your app in Amplify Console
2. Click **"Domain management"** in left sidebar
3. Click **"Add domain"**

### Step 2: Add Your Domain

1. Enter domain: `jansathi.com`
2. Amplify will show DNS records to add
3. Click **"Configure domain"**

### Step 3: Update DNS

In your domain registrar (GoDaddy, Namecheap, etc.):

Add these records:
```
Type: CNAME
Name: www
Value: main.d1234567890.amplifyapp.com

Type: CNAME  
Name: @
Value: main.d1234567890.amplifyapp.com
```

### Step 4: Wait for SSL

- SSL certificate auto-provisions (5-10 minutes)
- Your site will be available at: `https://jansathi.com`

---

## 🔄 Continuous Deployment

### Automatic Deployments

Every time you push to `main` branch:
```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Amplify automatically:
1. Detects the push
2. Runs build
3. Deploys new version
4. Updates live site

### Manual Deployment

In Amplify Console:
1. Click **"Redeploy this version"**
2. Or trigger from CLI:
```bash
aws amplify start-job \
  --app-id d1234567890 \
  --branch-name main \
  --job-type RELEASE
```

---

## 📊 Monitoring

### View Build Logs

1. Go to Amplify Console
2. Click on your app
3. Click on latest build
4. View detailed logs

### View Access Logs

1. Amplify Console → **Monitoring**
2. View:
   - Requests
   - Data transfer
   - Errors
   - Performance

---

## 💰 Cost Estimate

### AWS Amplify Pricing

**Free Tier (First 12 months):**
- 1,000 build minutes/month
- 15 GB served/month
- 5 GB stored/month

**After Free Tier:**
- Build minutes: $0.01/minute
- Data transfer: $0.15/GB
- Storage: $0.023/GB/month

**Estimated Monthly Cost:**
- Low traffic: $0-5
- Medium traffic: $5-15
- High traffic: $15-30

---

## 🐛 Troubleshooting

### Build Fails

**Check build logs:**
1. Amplify Console → Your app → Build
2. Click on failed build
3. Expand logs to see error

**Common issues:**
- Missing environment variables
- Node version mismatch
- Build command errors

**Fix:**
```bash
# Test build locally first
cd frontend
npm ci
npm run build

# If it works locally, check Amplify settings
```

### Site Not Loading

**Check:**
1. Build completed successfully
2. Environment variables set correctly
3. API URL is correct
4. No CORS errors in browser console

### Custom Domain Not Working

**Check:**
1. DNS records added correctly
2. Wait 24-48 hours for DNS propagation
3. SSL certificate status in Amplify Console

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to Git
- [ ] Environment variables ready
- [ ] AWS account set up
- [ ] AWS CLI configured

### Deployment
- [ ] Amplify app created
- [ ] Repository connected
- [ ] Build settings configured
- [ ] Environment variables added
- [ ] First deployment successful

### Post-Deployment
- [ ] Site accessible via Amplify URL
- [ ] All pages loading correctly
- [ ] API connection working (once backend deployed)
- [ ] Authentication working
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active

### Testing
- [ ] Homepage loads
- [ ] Navigation works
- [ ] Chat interface accessible
- [ ] Knowledge Base page works
- [ ] Dashboard accessible
- [ ] Mobile responsive

---

## 🎯 Next Steps

After frontend deployment:

1. ✅ **Frontend Deployed** (You are here!)
2. ⏭️ **Deploy Backend** (Next step)
   - Lambda functions
   - API Gateway
   - DynamoDB
3. ⏭️ **Configure Services**
   - Bedrock Knowledge Base
   - S3 buckets
   - CloudWatch logs
4. ⏭️ **Connect Frontend to Backend**
   - Update API URL in Amplify
   - Test end-to-end flow
5. ⏭️ **Production Optimization**
   - Enable caching
   - Set up monitoring
   - Configure alerts

---

## 📞 Support

### AWS Support
- Documentation: https://docs.aws.amazon.com/amplify/
- Forums: https://forums.aws.amazon.com/
- Support: https://console.aws.amazon.com/support/

### Quick Commands

```bash
# View Amplify apps
aws amplify list-apps

# Get app details
aws amplify get-app --app-id d1234567890

# View branches
aws amplify list-branches --app-id d1234567890

# Trigger deployment
aws amplify start-job \
  --app-id d1234567890 \
  --branch-name main \
  --job-type RELEASE
```

---

## 🎉 Success!

Your frontend is now deployed to AWS Amplify!

**Your app is live at:**
```
https://main.d1234567890.amplifyapp.com
```

**Next:** Deploy the backend to complete your AWS infrastructure.

---

**Deployment Date:** $(date)  
**Status:** ✅ Frontend Deployed  
**Platform:** AWS Amplify  
**Region:** us-east-1
