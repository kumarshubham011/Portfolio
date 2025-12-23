# 🚀 Deployment Guide

This guide walks you through deploying your portfolio for **FREE** on various platforms.

---

## Quick Comparison

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Render** | Easiest setup, auto-deploy | 15min sleep on free tier | Getting started |
| **Fly.io** | Fast, great free tier | Requires CLI | Performance |
| **Railway** | Modern UI, simple | Limited free credits | Quick deploys |

---

## Option 1: Render (Recommended for Beginners)

Render is the easiest platform for deploying Python apps.

### Step 1: Prepare Your Code

1. Create a GitHub repository
2. Push your portfolio code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/portfolio.git
   git push -u origin main
   ```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest)

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `portfolio` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

In the Render dashboard, add these environment variables:

| Variable | Value |
|----------|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | Click "Generate" for a random value |
| `ADMIN_USERNAME` | Your choice (e.g., `admin`) |
| `ADMIN_PASSWORD` | A strong password |
| `SITE_NAME` | Your Name |
| `SITE_TAGLINE` | Your tagline |
| `GITHUB_URL` | Your GitHub profile URL |
| `LINKEDIN_URL` | Your LinkedIn profile URL |
| `EMAIL` | Your email address |

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (2-3 minutes)
3. Visit your URL: `https://your-app-name.onrender.com`

### Step 6: Initialize Database

The database initializes automatically on first request. Visit `/health` to trigger it.

### Free Tier Notes

- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 free hours/month (enough for always-on)
- SQLite database included

---

## Option 2: Fly.io

Fly.io offers faster response times and better free tier.

### Step 1: Install CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### Step 2: Login

```bash
fly auth signup  # New account
# or
fly auth login   # Existing account
```

### Step 3: Launch App

```bash
cd portfolio
fly launch
```

Answer the prompts:
- App name: `your-portfolio-name`
- Region: Choose closest to you
- Would you like to set up a Postgresql database? **No**
- Would you like to deploy now? **Yes**

### Step 4: Set Secrets

```bash
fly secrets set \
  SECRET_KEY=$(openssl rand -hex 32) \
  ADMIN_USERNAME=admin \
  ADMIN_PASSWORD=your-secure-password \
  SITE_NAME="Your Name" \
  SITE_TAGLINE="Your Tagline" \
  DEBUG=False
```

### Step 5: Deploy

```bash
fly deploy
```

### Free Tier Notes

- 3 shared-cpu VMs with 256MB RAM
- 3GB persistent storage
- 160GB outbound bandwidth
- No sleep timeout!

---

## Option 3: Railway

Railway has a modern interface and simple deployment.

### Step 1: Create Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your portfolio repository

### Step 3: Configure

1. Railway auto-detects Python
2. Add environment variables:
   - Click on your service
   - Go to **"Variables"** tab
   - Add all the environment variables (same as Render)

### Step 4: Deploy

Railway deploys automatically when you push to GitHub.

### Free Tier Notes

- $5 free credits per month
- ~500 hours of runtime
- May need to add payment method for verification

---

## Post-Deployment Checklist

After deploying, verify everything works:

- [ ] Home page loads
- [ ] Navigate to /about, /projects, /blog, /contact
- [ ] Login at /auth/login with your credentials
- [ ] Create a test blog post
- [ ] Create a test project
- [ ] Verify public pages show content
- [ ] Test Focus Mode (Shift + F)
- [ ] Check mobile responsiveness

---

## Custom Domain (Optional)

All platforms support custom domains for free:

### Render
1. Go to Settings → Custom Domains
2. Add your domain
3. Update DNS with provided records

### Fly.io
```bash
fly certs create yourdomain.com
```
Then update your DNS.

### Railway
1. Settings → Domains
2. Add custom domain
3. Update DNS records

---

## Troubleshooting

### "Application Error" on first visit
- Wait 30 seconds and refresh (service was sleeping)
- Check logs in deployment dashboard

### Login not working
- Verify ADMIN_USERNAME and ADMIN_PASSWORD are set correctly
- Check for extra spaces in environment variables

### CSS not loading
- Verify static files are being served
- Check browser console for 404 errors
- Clear browser cache

### Database issues
- SQLite file is created automatically
- For persistence on Fly.io, use volumes:
  ```bash
  fly volumes create portfolio_data --size 1
  ```

---

## Updating Your Site

### With Auto-Deploy (Recommended)
Simply push to GitHub:
```bash
git add .
git commit -m "Update content"
git push
```

### Manual Deploy
```bash
# Fly.io
fly deploy

# Railway/Render
# Auto-deploys on push
```

---

## Security Reminders

1. **Never commit `.env` file** - It's in .gitignore
2. **Use strong passwords** - At least 12 characters
3. **Keep SECRET_KEY secret** - Generate unique per deployment
4. **Regularly update dependencies** - `pip list --outdated`

---

## Need Help?

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [Railway Docs](https://docs.railway.app)

Happy deploying! 🎉
