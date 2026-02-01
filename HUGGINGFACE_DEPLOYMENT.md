# Deploying ClaimFlow AI to Hugging Face Spaces

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

The following files are already set up for deployment:
- ✅ `app.py` - Entry point for Hugging Face Spaces
- ✅ `requirements.txt` - Updated with Gradio 6.5+
- ✅ `SPACE_README.md` - Space description with metadata

### 2. Create a Hugging Face Account

1. Go to https://huggingface.co/join
2. Sign up for a free account
3. Verify your email

### 3. Create a New Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in the details:
   - **Space name**: `claimflow-ai` (or your preferred name)
   - **License**: MIT
   - **Select SDK**: Gradio
   - **SDK version**: 6.5.1
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public or Private (your choice)

### 4. Upload Your Files

**Option A: Using Git (Recommended)**

```bash
# Clone the newly created space
git clone https://huggingface.co/spaces/abhireds/claimflow-ai
cd claimflow-ai

# Copy all project files
cp -r C:/Users/abhir/claimflow-ai/* .

# Remove local files not needed for deployment
rm -rf .venv __pycache__ .pytest_cache .git

# Rename SPACE_README.md to README.md
mv SPACE_README.md README.md

# Commit and push
git add .
git commit -m "Initial deployment of ClaimFlow AI"
git push
```

**Option B: Using Web Interface**

1. Click on **"Files"** tab in your Space
2. Click **"Add file"** → **"Upload files"**
3. Upload these key files:
   - `app.py`
   - `requirements.txt`
   - `SPACE_README.md` (rename to `README.md`)
   - All folders: `agent/`, `database/`, `ui/`, `config/`, `data/`, `policies/`

### 5. Configure Environment Variables (CRITICAL)

1. Go to your Space settings (⚙️ icon)
2. Scroll to **"Repository secrets"**
3. Click **"New secret"**
4. Add:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key (sk-...)
5. Click **"Add secret"**

### 6. Initialize Database & Vector Store

Since Hugging Face Spaces may not persist data, you need to initialize on startup. Modify `app.py`:

```python
"""
ClaimFlow AI - Hugging Face Spaces Entry Point
"""
import sys
import os
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database and vector store on first run
if not os.path.exists("data/claimflow.db"):
    print("Initializing database...")
    subprocess.run(["python", "scripts/init_database.py"])
    
if not os.path.exists("data/chroma_db"):
    print("Initializing vector store...")
    subprocess.run(["python", "scripts/ingest_policies.py"])

# Import and run the simple app
from ui.simple_app import demo

if __name__ == "__main__":
    demo.launch()
```

### 7. Monitor Deployment

1. After pushing, go to your Space URL: `https://huggingface.co/spaces/abhireds/claimflow-ai`
2. Watch the **"Build logs"** - it takes 3-5 minutes
3. Look for: `Running on public URL: https://...`
4. Your app is live! 🎉

### 8. Test Your Live Application

1. Open the Space URL
2. Test a claim: "Hi, my car got damaged in a parking lot"
3. Verify all features work:
   - Conversation flow ✓
   - Auto-detection ✓
   - 9-step processing ✓
   - Clear button ✓

## Troubleshooting

**Build fails?**
- Check `requirements.txt` has all dependencies
- Ensure Python version compatibility (3.10+)

**OpenAI errors?**
- Verify `OPENAI_API_KEY` secret is set correctly
- Check API key has credits

**Database/RAG not working?**
- Ensure initialization scripts run on startup
- Check `data/` folder is included in upload

**App loads but crashes?**
- Check Space logs for errors
- May need to increase hardware tier (CPU basic → CPU upgrade)

## Space Configuration Files

**README.md** (space description):
```yaml
---
title: ClaimFlow AI
emoji: 🛡️
sdk: gradio
sdk_version: 6.5.1
app_file: app.py
---
```

## Cost Considerations

- **Hugging Face Spaces**: FREE for public spaces with CPU basic
- **OpenAI API**: ~$0.01-0.05 per claim (GPT-4o pricing)
- **Tip**: Monitor your OpenAI usage dashboard

## Updating Your Space

```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push

# Space will rebuild automatically
```

## Making it Private

1. Go to Space settings
2. Change **Visibility** from Public to Private
3. Only you can access the URL

## Custom Domain (Optional)

1. Upgrade to Pro ($9/month)
2. Go to Space settings → Domains
3. Add your custom domain

## Next Steps

- Share your Space URL in your portfolio/resume
- Add demo video/GIF to Space README
- Monitor usage in Hugging Face dashboard
- Consider adding authentication for production use

---

**Author**: Abhishyant Reddy
**Project**: ClaimFlow AI
**GitHub**: https://github.com/abhishyantreddy
