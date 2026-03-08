# 🚀 Deploy Your Branch NOW

## ⚡ Super Quick Deploy (2 commands)

### Step 1: Push to GitHub

Run this script:

```powershell
.\deploy-to-vercel.ps1
```

This will:
- ✅ Commit all your changes
- ✅ Push to GitHub (poornachandran branch)
- ✅ Show you next steps

**OR manually:**

```powershell
git add .
git commit -m "Add Knowledge Base with intelligent caching and Lambda integration"
git push origin poornachandran
```

---

### Step 2: Update Vercel

**Go to:** https://vercel.com/dashboard

**Then:**

1. **Select** your JanSathi project
2. **Settings** → **Git** → Change "Production Branch" to: `poornachandran`
3. **Settings** → **Environment Variables** → Add/Edit:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://b0z0h6knui.execute-api.us-east-1.amazonaws.com`
4. **Deployments** → **Redeploy**

---

## 📊 Your Info

**GitHub Repo:**
```
https://github.com/shalcoder/JanSathi
```

**Your Branch:**
```
poornachandran
```

**Lambda API URL:**
```
https://b0z0h6knui.execute-api.us-east-1.amazonaws.com
```

**Current Status:**
- ✅ On branch: poornachandran
- ✅ Changes ready to commit
- ⏳ Need to push to GitHub
- ⏳ Need to update Vercel

---

## 🎯 What Happens Next

1. **You run:** `.\deploy-to-vercel.ps1`
2. **Script commits and pushes** your changes to GitHub
3. **You update Vercel** to deploy from `poornachandran` branch
4. **Vercel automatically deploys** your code
5. **Your site is live** with all new features!

---

## ⚠️ If Push Fails

If you get "permission denied" or "authentication failed":

**Option 1: Ask Friend to Add You**

Your friend (shalcoder) needs to:
1. Go to: https://github.com/shalcoder/JanSathi/settings/access
2. Click "Add people"
3. Add your GitHub username
4. Give you "Write" access

**Option 2: Friend Pushes Your Changes**

1. Zip your JanSathi folder
2. Send to your friend
3. Friend extracts and pushes to GitHub
4. Then you update Vercel

**Option 3: Use GitHub Desktop**

1. Download GitHub Desktop
2. Sign in with your GitHub account
3. Open the repository
4. Commit and push from the GUI

---

## ✅ Success Checklist

- [ ] Run `.\deploy-to-vercel.ps1` (or manual git commands)
- [ ] Verify push succeeded (check GitHub)
- [ ] Go to Vercel dashboard
- [ ] Change production branch to `poornachandran`
- [ ] Add environment variable `NEXT_PUBLIC_API_URL`
- [ ] Redeploy
- [ ] Test your site

---

## 🎉 After Deployment

Your site will have:
- ✅ Knowledge Base with PDF upload
- ✅ Intelligent caching (85% cost reduction)
- ✅ Connected to Lambda API
- ✅ All your new features

**Test it:**
1. Open your Vercel URL
2. Try chat feature
3. Try Knowledge Base upload
4. Check browser console (F12) for errors

---

## 📞 Need Help?

**If push fails:**
- Check if you have GitHub access
- Ask friend to add you as collaborator
- Or ask friend to push your changes

**If Vercel deployment fails:**
- Check build logs in Vercel
- Make sure environment variable is set
- Try clearing Vercel cache

**For detailed help:**
- See `DEPLOY_BRANCH_TO_VERCEL.md`
- See `START_HERE.md`

---

## 🚀 Ready? Let's Go!

```powershell
# Run this now:
.\deploy-to-vercel.ps1
```

Then follow the instructions it shows you!

---

**Last Updated:** 2026-03-08
