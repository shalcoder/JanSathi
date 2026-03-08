# 🚀 Deploy Your Branch to Vercel

## 📋 Situation

- ✅ Your changes are in branch: `poornachandran`
- ✅ GitHub repo belongs to your friend
- ✅ Need to deploy your branch to Vercel
- ✅ Lambda API URL: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`

---

## 🎯 Two Options

### Option A: Update Existing Vercel Deployment (Recommended)
Change the branch that Vercel deploys from

### Option B: Create New Vercel Deployment
Deploy your branch as a new project

---

## 📱 Option A: Update Existing Vercel Deployment

### Step 1: Push Your Changes to GitHub

First, make sure all your changes are committed and pushed:

```powershell
cd D:\Documents\Hackathons\Ai_for_Bharat\JanSathi

# Check current branch
git branch

# If not on poornachandran branch, switch to it
git checkout poornachandran

# Add all changes
git add .

# Commit changes
git commit -m "Add Knowledge Base with intelligent caching and Lambda API integration"

# Push to GitHub
git push origin poornachandran
```

### Step 2: Update Vercel to Deploy Your Branch

**Via Vercel Dashboard:**

1. Go to: https://vercel.com/dashboard
2. Click on your **JanSathi** project (or jan-sathi-five)
3. Click **Settings** (top menu)
4. Click **Git** (left sidebar)
5. Under "Production Branch", you'll see the current branch (probably `main` or `master`)
6. Click **Edit** next to "Production Branch"
7. Change it to: `poornachandran`
8. Click **Save**

### Step 3: Add Environment Variable

While in Settings:

1. Click **Environment Variables** (left sidebar)
2. Add/Edit: `NEXT_PUBLIC_API_URL`
3. Value: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
4. Environment: Check **Production**
5. Click **Save**

### Step 4: Trigger Deployment

1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment
3. Or push a new commit to trigger auto-deployment

---

## 🆕 Option B: Create New Vercel Deployment

If you want to keep the existing deployment and create a new one for your branch:

### Step 1: Push Your Branch to GitHub

```powershell
cd D:\Documents\Hackathons\Ai_for_Bharat\JanSathi
git checkout poornachandran
git add .
git commit -m "Add Knowledge Base with intelligent caching and Lambda API integration"
git push origin poornachandran
```

### Step 2: Import Project to Vercel

1. Go to: https://vercel.com/new
2. Click **Import Git Repository**
3. If you don't see your friend's repo:
   - Click **Adjust GitHub App Permissions**
   - Make sure you have access to the repo
4. Select the repository
5. Click **Import**

### Step 3: Configure Project

In the import screen:

**Project Name:**
```
jansathi-poornachandran
```

**Framework Preset:**
```
Next.js
```

**Root Directory:**
```
frontend
```
(If your Next.js app is in the `frontend` folder)

**Build Command:**
```
npm run build
```

**Output Directory:**
```
out
```
(Since you're using static export)

**Environment Variables:**
Click **Add** and enter:
- Name: `NEXT_PUBLIC_API_URL`
- Value: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`

**Git Branch:**
- Change from `main` to `poornachandran`

### Step 4: Deploy

1. Click **Deploy**
2. Wait 2-3 minutes for deployment
3. You'll get a new URL like: `https://jansathi-poornachandran.vercel.app`

---

## 🔧 If You Don't Have Access to Friend's Repo

### Option 1: Ask Friend to Add You as Collaborator

Your friend needs to:

1. Go to GitHub repo
2. Settings → Collaborators
3. Add your GitHub username
4. You accept the invitation

### Option 2: Fork the Repo

1. Go to your friend's GitHub repo
2. Click **Fork** (top right)
3. This creates a copy in your GitHub account
4. Push your `poornachandran` branch to your fork
5. Deploy from your fork to Vercel

### Option 3: Friend Deploys Your Branch

Your friend can:

1. Go to their Vercel dashboard
2. Change production branch to `poornachandran`
3. Or add you as a team member in Vercel

---

## 📝 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] All changes are committed to `poornachandran` branch
- [ ] Branch is pushed to GitHub
- [ ] `.env.local` has the Lambda API URL (for reference)
- [ ] `next.config.ts` has `output: "export"` (already done)
- [ ] Frontend builds successfully locally: `npm run build`

### Test Local Build

```powershell
cd JanSathi\frontend

# Install dependencies
npm install

# Build the project
npm run build

# Check for errors
# Should create 'out' folder with static files
```

---

## 🎯 Recommended Approach

**I recommend Option A** (Update Existing Deployment) because:

1. ✅ Keeps the same Vercel URL
2. ✅ Simpler - just change the branch
3. ✅ No need to reconfigure everything
4. ✅ Existing environment variables stay

---

## 📋 Step-by-Step: Option A (Detailed)

### 1. Commit and Push Your Changes

```powershell
cd D:\Documents\Hackathons\Ai_for_Bharat\JanSathi

# Check status
git status

# Check current branch
git branch

# Switch to poornachandran if needed
git checkout poornachandran

# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add Bedrock Knowledge Base with 85% cost reduction via intelligent caching

- Implemented Knowledge Base service with PDF upload
- Added intelligent caching layer (85% cost reduction)
- Created frontend components for KB upload and query
- Integrated with AWS Lambda API Gateway
- Updated API client with KB functions
- Added cache statistics and analytics"

# Push to GitHub
git push origin poornachandran
```

### 2. Verify Push on GitHub

1. Go to your friend's GitHub repo
2. Click on the branch dropdown (usually says "main")
3. Select `poornachandran` branch
4. Verify your latest commit is there

### 3. Update Vercel Branch

1. **Go to:** https://vercel.com/dashboard
2. **Click:** Your JanSathi project
3. **Click:** Settings (top menu)
4. **Click:** Git (left sidebar)
5. **Find:** "Production Branch" section
6. **Click:** Edit button
7. **Change to:** `poornachandran`
8. **Click:** Save

### 4. Add Environment Variable

1. **Click:** Environment Variables (left sidebar)
2. **Look for:** `NEXT_PUBLIC_API_URL`
   
   **If it exists:**
   - Click Edit (pencil icon)
   - Change value to: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
   - Make sure "Production" is checked
   - Click Save
   
   **If it doesn't exist:**
   - Click "Add New" button
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
   - Check "Production"
   - Click Save

### 5. Trigger Deployment

**Option 1: Redeploy**
1. Click **Deployments** tab
2. Find latest deployment
3. Click **⋯** (three dots)
4. Click **Redeploy**

**Option 2: Push New Commit**
```powershell
# Make a small change (like updating a comment)
git commit --allow-empty -m "trigger deployment"
git push origin poornachandran
```

### 6. Monitor Deployment

1. Go to **Deployments** tab
2. Watch the deployment progress
3. Should take 2-3 minutes
4. Look for green checkmark ✅

### 7. Test Your Deployment

1. Click **Visit** or go to your Vercel URL
2. Press **F12** → Network tab
3. Try the chat feature
4. Verify API calls go to Lambda (not localhost)
5. Test Knowledge Base upload and query

---

## 🐛 Troubleshooting

### "Branch not found"

**Solution:** Make sure you pushed the branch to GitHub

```powershell
git push origin poornachandran
```

### "Build failed"

**Solution:** Check build logs in Vercel

Common issues:
- Missing dependencies: Run `npm install` locally
- TypeScript errors: Run `npm run build` locally to check
- Environment variables: Make sure they're set in Vercel

### "Still deploying old code"

**Solution:** Clear Vercel cache

1. Settings → General
2. Scroll to "Build & Development Settings"
3. Click "Clear Cache"
4. Redeploy

### "Can't access friend's repo in Vercel"

**Solution:** Ask friend to:
1. Add you as collaborator on GitHub
2. Or add you as team member in Vercel
3. Or deploy your branch themselves

---

## ✅ Success Checklist

- [ ] Branch `poornachandran` pushed to GitHub
- [ ] Vercel production branch changed to `poornachandran`
- [ ] Environment variable `NEXT_PUBLIC_API_URL` set
- [ ] Deployment triggered and completed
- [ ] Site loads without errors
- [ ] API calls go to Lambda (check Network tab)
- [ ] Chat feature works
- [ ] Knowledge Base features work

---

## 🎉 After Successful Deployment

Your site will be live at:
```
https://jan-sathi-five.vercel.app
```
(or whatever your Vercel URL is)

With:
- ✅ Your `poornachandran` branch code
- ✅ Connected to Lambda API
- ✅ Knowledge Base with intelligent caching
- ✅ All new features working

---

## 📞 Need Help?

If you get stuck:

1. Share the error message from Vercel build logs
2. Share your GitHub repo URL
3. Share your Vercel project URL
4. Let me know which option you chose (A or B)

---

**Quick Commands Reference:**

```powershell
# Push your branch
git checkout poornachandran
git add .
git commit -m "your message"
git push origin poornachandran

# Test local build
cd JanSathi\frontend
npm run build

# Update Lambda CORS
aws lambda update-function-configuration --function-name jansathi-backend --environment Variables="{USE_DYNAMODB=true,NODE_ENV=production,ALLOWED_ORIGINS=https://jan-sathi-five.vercel.app,http://localhost:3000}" --region us-east-1
```

---

**Last Updated:** 2026-03-08
