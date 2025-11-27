# Deployment Guide for BhagavadGPT

This guide covers deploying BhagavadGPT to various platforms.

## Table of Contents
1. [Vercel Deployment (Recommended)](#vercel-deployment-recommended)
2. [Heroku Deployment](#heroku-deployment)
3. [Railway Deployment](#railway-deployment)
4. [Local Development](#local-development)

---

## Vercel Deployment (Recommended)

Vercel provides serverless deployment with native Python support and excellent performance.

### Prerequisites
- GitHub account with repository pushed
- Vercel account (free tier available)
- Node.js and npm installed

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Prepare Your Repository

Ensure your repository has:
- ✅ `vercel.json` - Configuration file
- ✅ `api/index.py` - Serverless function
- ✅ `public/` - Frontend files (index.html, style.css, script.js)
- ✅ `requirements.txt` - Python dependencies
- ✅ `bhagavad_gita_dataset_expanded.json` - Verse database

**Current structure:**
```
Gitabot-2/
├── api/index.py
├── public/index.html
├── vercel.json
├── requirements.txt
├── bhagavad_gita_dataset_expanded.json
└── README.md
```

### Step 3: Configure vercel.json

Already configured. Key settings:
```json
{
  "version": 2,
  "functions": {
    "api/index.py": {
      "runtime": "python3.11",
      "memory": 1024,
      "maxDuration": 30
    }
  }
}
```

### Step 4: Deploy to Vercel

Option A: Deploy via CLI
```bash
cd /Users/parthsharma/Downloads/Gbot
vercel login        # Authenticate
vercel              # Deploy
```

Option B: Deploy via GitHub (Recommended)
1. Go to https://vercel.com
2. Click "New Project"
3. Import GitHub repository
4. Vercel auto-detects Python
5. Click Deploy

### Step 5: Configure Environment (if needed)

In Vercel Dashboard:
1. Go to Settings → Environment Variables
2. Add variables:
   ```
   PYTHONUNBUFFERED=1
   ```

### Step 6: Access Your App

```
https://your-project.vercel.app
```

### Troubleshooting Vercel

**Issue: "Module not found" errors**
- Solution: Ensure `requirements.txt` is at project root
- Vercel runs: `pip install -r requirements.txt`

**Issue: 502 Bad Gateway**
- Solution: Check Vercel logs: `vercel logs`
- Ensure `api/index.py` exports `app` as Flask application

**Issue: Slow cold start**
- Vercel caches dependencies between deployments
- First deployment takes longer (2-3 minutes)
- Subsequent deploys are instant

**Large model download timeout**
- Increase `maxDuration` in `vercel.json` to 60 seconds
- Consider pre-downloading embeddings

---

## Heroku Deployment

### Prerequisites
- Heroku account (free tier limited)
- Heroku CLI installed
- Git repository

### Step 1: Create Heroku App

```bash
heroku login
heroku create your-app-name
```

### Step 2: Add Buildpacks

```bash
heroku buildpacks:add heroku/python
```

### Step 3: Create Procfile

```bash
cat > Procfile << EOF
web: gunicorn app:app
EOF
```

### Step 4: Update requirements.txt

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 5: Deploy

```bash
git push heroku main
```

### Step 6: View Logs

```bash
heroku logs --tail
```

### Access Your App

```
https://your-app-name.herokuapp.com
```

---

## Railway Deployment

Railway offers easy deployment with GitHub integration.

### Step 1: Connect GitHub

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access GitHub
5. Select your repository

### Step 2: Configure

Railway auto-detects Python and creates deployment config.

### Step 3: Deploy

Click "Deploy" - Railway handles everything!

### Access Your App

Railway provides a `.railway.app` domain automatically.

---

## Local Development

### Setup

```bash
# Clone and navigate
git clone https://github.com/parth-sharma-963/Gitabot-2.git
cd Gitabot-2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate dataset (if not present)
jupyter notebook code.ipynb
# Run first two cells to generate bhagavad_gita_dataset_expanded.json
```

### Run Development Server

```bash
python app.py
```

Server runs at: `http://localhost:5000`

### Debug Mode

Edit `app.py` and set `debug=True`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## Performance Optimization

### Model Caching
The embedding model is cached in memory:
- First request: ~5-10 seconds (model download + embedding generation)
- Subsequent requests: <100ms

### Dataset Loading
- Pre-loads `bhagavad_gita_dataset_expanded.json` on startup
- 100+ verses embedded upfront

### Cold Start Times

| Platform | Cold Start | Warm Start |
|----------|-----------|-----------|
| Vercel | 3-5s | <100ms |
| Heroku | 10-15s | <200ms |
| Railway | 5-8s | <100ms |
| Local | 5s | <100ms |

---

## Monitoring & Logs

### Vercel
```bash
vercel logs                    # Recent logs
vercel logs --follow          # Stream logs
```

### Heroku
```bash
heroku logs --tail            # Stream logs
heroku logs -n 50             # Last 50 lines
```

### Railway
Logs available in Railway dashboard (real-time)

---

## Common Issues & Solutions

### Issue: Dataset file not found
**Solution:** Ensure `bhagavad_gita_dataset_expanded.json` is:
- In project root
- Committed to git
- Not in `.gitignore`

### Issue: Out of memory
**Solution:** 
- Vercel: Increase function memory in `vercel.json`
- Heroku: Upgrade to paid dyno

### Issue: Slow embeddings
**Solution:**
- Use lighter model: `distiluse-base-multilingual-cased-v2`
- Cache embeddings in database

### Issue: CORS errors
**Solution:**
- Flask-CORS is configured in `app.py`
- Vercel routes are configured in `vercel.json`

---

## Next Steps

After deployment:

1. **Test the API**
   ```bash
   curl -X POST https://your-app.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "I feel anxious"}'
   ```

2. **Set up monitoring**
   - Sentry for error tracking
   - LogRocket for user session replay

3. **Enable caching**
   - Add Redis for response caching
   - Cache embeddings in database

4. **Scale to multiple regions**
   - Vercel: Automatic global distribution
   - Heroku: Add multiple dynos

---

## Support

For deployment issues:
- Check Vercel/Heroku logs first
- Review this guide again
- Open GitHub issue with error details

**Last Updated**: November 27, 2025
