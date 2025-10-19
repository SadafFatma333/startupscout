# Deploy StartupScout UI to Vercel

## 🚀 Quick Deployment Steps

### Step 1: Go to Vercel
1. Visit https://vercel.com
2. Sign in with your GitHub account

### Step 2: Import Project
1. Click "New Project"
2. Select your `startupscout` repository
3. Click "Import"

### Step 3: Configure Deployment
1. **Framework Preset:** Vite
2. **Root Directory:** `ui`
3. **Build Command:** `npm run build` (auto-detected)
4. **Output Directory:** `dist` (auto-detected)

### Step 4: Environment Variables
Add this environment variable:
- **Name:** `VITE_API_BASE_URL`
- **Value:** `https://startupscout-production.up.railway.app`

### Step 5: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Get your UI URL (e.g., `https://startupscout-ui.vercel.app`)

## 🔗 Your URLs After Deployment

- **API Backend:** https://startupscout-production.up.railway.app
- **UI Frontend:** https://your-ui-name.vercel.app
- **API Docs:** https://startupscout-production.up.railway.app/docs

## 🎯 What You'll Get

- ✅ Modern React UI with Tailwind CSS
- ✅ Chat interface for asking questions
- ✅ Search functionality
- ✅ Responsive design
- ✅ Fast loading with Vercel's CDN

## 🔧 Troubleshooting

If deployment fails:
1. Check that `ui/package.json` has all dependencies
2. Ensure `ui/vercel.json` is in the root of the `ui` folder
3. Verify environment variables are set correctly

## 📱 Features Available

- **Ask Questions:** Chat interface with the RAG system
- **Search:** Find relevant startup content
- **Authentication:** User login/registration (when backend features are added)
- **Responsive:** Works on desktop and mobile
