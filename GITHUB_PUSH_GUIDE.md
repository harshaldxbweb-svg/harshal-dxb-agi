# 📤 GitHub Push Guide - Step by Step

## 🎯 Push Code to GitHub: https://github.com/harshaldxbweb-svg/harshal-dxb-agi

Follow these exact steps:

---

## Step 1: Open Terminal/Command Prompt

**Windows:**
```powershell
# Open PowerShell
cd C:\Users\harsh\AppData\Local\Temp\aws-toolkit-vscode\lambda\eu-central-1\harshal-dxb-agi
```

**Mac/Linux:**
```bash
cd /path/to/harshal-dxb-agi
```

---

## Step 2: Initialize Git (if not already)

```bash
# Check if git is initialized
git status

# If error "not a git repository", then initialize:
git init
```

---

## Step 3: Add Remote Repository

```bash
# Add your GitHub repository
git remote add origin https://github.com/harshaldxbweb-svg/harshal-dxb-agi.git

# Verify remote
git remote -v
```

**If remote already exists:**
```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/harshaldxbweb-svg/harshal-dxb-agi.git
```

---

## Step 4: Stage All Files

```bash
# Add all files
git add .

# Check what will be committed
git status
```

**You should see:**
- ✅ All .py files
- ✅ Dockerfile
- ✅ apprunner.yaml
- ✅ requirements.txt
- ✅ README.md
- ✅ All deployment guides
- ❌ .env (should be ignored)
- ❌ __pycache__ (should be ignored)

---

## Step 5: Commit Changes

```bash
# Commit with message
git commit -m "Initial commit: Harshal DXB AGI WhatsApp Bot"
```

---

## Step 6: Set Branch to Main

```bash
# Rename branch to main (if needed)
git branch -M main
```

---

## Step 7: Push to GitHub

```bash
# Push to GitHub
git push -u origin main
```

**If prompted for credentials:**
- Username: `harshaldxbweb-svg`
- Password: Use **Personal Access Token** (not your GitHub password)

---

## 🔑 Create GitHub Personal Access Token (if needed)

1. **Go to GitHub Settings**
   - https://github.com/settings/tokens

2. **Generate New Token**
   - Click "Generate new token (classic)"
   - Note: "Harshal AGI Deployment"
   - Expiration: 90 days
   - Scopes: Select `repo` (all)
   - Click "Generate token"

3. **Copy Token**
   - Copy the token (starts with `ghp_...`)
   - Save it somewhere safe

4. **Use Token as Password**
   ```bash
   Username: harshaldxbweb-svg
   Password: ghp_your_token_here
   ```

---

## Step 8: Verify Push

```bash
# Check if pushed successfully
git log --oneline

# Visit GitHub repository
# https://github.com/harshaldxbweb-svg/harshal-dxb-agi
```

---

## 🚨 Common Issues & Fixes

### Issue 1: "Permission denied"
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/harshaldxbweb-svg/harshal-dxb-agi.git
```

### Issue 2: "Repository not found"
```bash
# Check if repository exists on GitHub
# Create it first: https://github.com/new
# Then retry push
```

### Issue 3: "Failed to push some refs"
```bash
# Pull first, then push
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Issue 4: "Large files detected"
```bash
# Remove large files from git
git rm --cached lambda-deployment.zip
git commit -m "Remove large files"
git push
```

---

## ✅ Verification Checklist

After pushing, verify on GitHub:

- [ ] All Python files visible
- [ ] Dockerfile present
- [ ] apprunner.yaml present
- [ ] requirements.txt present
- [ ] README.md showing properly
- [ ] Documentation files present
- [ ] .env file NOT visible (should be ignored)
- [ ] No __pycache__ folders

---

## 🚀 After GitHub Push - Deploy to App Runner

### Option 1: Deploy from GitHub (Easiest)

1. **Go to App Runner Console**
   - https://console.aws.amazon.com/apprunner

2. **Create Service**
   - Source: **Source code repository**
   - Connect to GitHub
   - Select repository: `harshaldxbweb-svg/harshal-dxb-agi`
   - Branch: `main`

3. **Build Settings**
   - Configuration: Use `apprunner.yaml`
   - Or manually:
     - Runtime: Python 3
     - Build: `pip install -r requirements.txt`
     - Start: `gunicorn --bind 0.0.0.0:8080 main:app`

4. **Environment Variables**
   ```
   ULTRAMSG_INSTANCE_ID = instance123456
   ULTRAMSG_TOKEN = your_token
   GEMINI_API_KEY = your_key
   ADMIN_PHONE = 971XXXXXXXXX
   AWS_REGION = eu-central-1
   ENVIRONMENT = PRODUCTION
   ```

5. **Deploy**
   - Click "Create & deploy"
   - Wait 5-10 minutes
   - Get webhook URL

### Option 2: Deploy from Docker (Alternative)

```bash
# Run deployment script
./deploy-apprunner.sh
```

---

## 📱 Final Steps

1. **Get Webhook URL from App Runner**
   - Example: `https://abc123.eu-central-1.awsapprunner.com/webhook`

2. **Configure UltraMsg**
   - Login: https://ultramsg.com
   - Webhooks → Set URL
   - Enable `on.message`

3. **Test**
   - Send WhatsApp: "Hi"
   - Response should come!

---

## 🎯 Quick Commands Summary

```bash
# Complete push sequence
cd C:\Users\harsh\AppData\Local\Temp\aws-toolkit-vscode\lambda\eu-central-1\harshal-dxb-agi
git init
git remote add origin https://github.com/harshaldxbweb-svg/harshal-dxb-agi.git
git add .
git commit -m "Initial commit: Harshal DXB AGI"
git branch -M main
git push -u origin main
```

---

## 💡 Pro Tips

1. **Always check .gitignore before pushing**
   - Never commit .env files
   - Never commit credentials

2. **Use meaningful commit messages**
   ```bash
   git commit -m "Add: Feature description"
   git commit -m "Fix: Bug description"
   git commit -m "Update: What changed"
   ```

3. **Pull before push (if working with team)**
   ```bash
   git pull origin main
   git push origin main
   ```

4. **Check repository after push**
   - Visit GitHub URL
   - Verify all files are there
   - Check README renders properly

---

**🚀 Ready to push? Run the commands above!**
