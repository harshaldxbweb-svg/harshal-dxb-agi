# 🚀 AWS App Runner Deployment Guide

## What is App Runner?
AWS App Runner is a fully managed service that makes it easy to deploy containerized web applications and APIs at scale.

**Benefits:**
- No need to manage servers
- Automatic scaling
- Built-in load balancing
- HTTPS by default
- Pay only for what you use

---

## 📦 Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws configure
   ```

2. **Docker installed** (for local testing)
   ```bash
   docker --version
   ```

3. **GitHub account** (for source code deployment)

---

## 🎯 Deployment Options

### Option A: Deploy from Source Code (GitHub) - EASIEST

#### Step 1: Push Code to GitHub
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/harshal-agi.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy via AWS Console

1. **Go to App Runner Console**
   - https://console.aws.amazon.com/apprunner

2. **Create Service**
   - Click "Create service"

3. **Source Configuration**
   - Repository type: **Source code repository**
   - Connect to GitHub (first time only)
   - Select your repository: `harshal-agi`
   - Branch: `main`
   - Deployment trigger: **Automatic** (deploys on every push)

4. **Build Configuration**
   - Configuration source: **Use a configuration file**
   - Configuration file: `apprunner.yaml`
   
   OR manually configure:
   - Runtime: **Python 3**
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:8080 --workers 4 main:app`
   - Port: `8080`

5. **Service Settings**
   - Service name: `harshal-agi-service`
   - Virtual CPU: **1 vCPU**
   - Memory: **2 GB**
   - Environment variables:
     ```
     ULTRAMSG_INSTANCE_ID = instance123456
     ULTRAMSG_TOKEN = your_token
     GEMINI_API_KEY = your_gemini_key
     ADMIN_PHONE = 971XXXXXXXXX
     AWS_REGION = eu-central-1
     ENVIRONMENT = PRODUCTION
     ```

6. **Auto Scaling**
   - Min instances: **1**
   - Max instances: **5**
   - Max concurrency: **100**

7. **Health Check**
   - Path: `/health`
   - Interval: 10 seconds
   - Timeout: 5 seconds
   - Unhealthy threshold: 3

8. **Create & Deploy**
   - Click "Create & deploy"
   - Wait 5-10 minutes for deployment

9. **Get Your URL**
   - After deployment, you'll get a URL like:
   - `https://abc123xyz.eu-central-1.awsapprunner.com`
   - Your webhook URL: `https://abc123xyz.eu-central-1.awsapprunner.com/webhook`

---

### Option B: Deploy from Docker Image (ECR)

#### Step 1: Build Docker Image
```bash
# Build image
docker build -t harshal-agi .

# Test locally
docker run -p 8080:8080 \
  -e ULTRAMSG_INSTANCE_ID=xxx \
  -e ULTRAMSG_TOKEN=yyy \
  -e GEMINI_API_KEY=zzz \
  -e ADMIN_PHONE=971XXX \
  harshal-agi

# Test: curl http://localhost:8080/health
```

#### Step 2: Push to ECR
```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=eu-central-1

# Create ECR repository
aws ecr create-repository \
  --repository-name harshal-agi \
  --region $REGION

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Tag image
docker tag harshal-agi:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/harshal-agi:latest

# Push image
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/harshal-agi:latest
```

#### Step 3: Deploy to App Runner
```bash
# Create App Runner service
aws apprunner create-service \
  --service-name harshal-agi-service \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ACCOUNT_ID'.dkr.ecr.'$REGION'.amazonaws.com/harshal-agi:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": {
          "ULTRAMSG_INSTANCE_ID": "instance123456",
          "ULTRAMSG_TOKEN": "your_token",
          "GEMINI_API_KEY": "your_key",
          "ADMIN_PHONE": "971XXXXXXXXX",
          "AWS_REGION": "eu-central-1",
          "ENVIRONMENT": "PRODUCTION"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --health-check-configuration '{
    "Protocol": "HTTP",
    "Path": "/health",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 3
  }' \
  --region $REGION
```

---

## 🔧 Automated Deployment Script

Save this as `deploy-apprunner.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Deploying to AWS App Runner..."

# Configuration
SERVICE_NAME="harshal-agi-service"
REGION="eu-central-1"
REPO_NAME="harshal-agi"

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS Account: $ACCOUNT_ID"

# Create ECR repository if not exists
echo "📦 Creating ECR repository..."
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION 2>/dev/null || \
  aws ecr create-repository --repository-name $REPO_NAME --region $REGION

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $REPO_NAME .

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Tag and push
echo "📤 Pushing image to ECR..."
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest

echo "✅ Image pushed successfully!"
echo ""
echo "🌐 Your image: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest"
echo ""
echo "📋 Next steps:"
echo "1. Go to App Runner Console: https://console.aws.amazon.com/apprunner"
echo "2. Create service from this ECR image"
echo "3. Set environment variables"
echo "4. Deploy!"
```

Run it:
```bash
chmod +x deploy-apprunner.sh
./deploy-apprunner.sh
```

---

## 🔗 Configure UltraMsg Webhook

After deployment:

1. **Get your App Runner URL**
   ```bash
   aws apprunner list-services --region eu-central-1
   # Or check App Runner Console
   ```

2. **Your webhook URL will be:**
   ```
   https://YOUR_SERVICE_ID.eu-central-1.awsapprunner.com/webhook
   ```

3. **Set in UltraMsg:**
   - Login to https://ultramsg.com
   - Dashboard → Webhooks
   - Paste webhook URL
   - Enable `on.message`
   - Save

---

## 📊 Monitor Your Service

### View Logs
```bash
# Get service ARN
SERVICE_ARN=$(aws apprunner list-services --region eu-central-1 \
  --query "ServiceSummaryList[?ServiceName=='harshal-agi-service'].ServiceArn" \
  --output text)

# View logs (via CloudWatch)
aws logs tail /aws/apprunner/$SERVICE_ARN/service --follow --region eu-central-1
```

### Check Service Status
```bash
aws apprunner describe-service \
  --service-arn $SERVICE_ARN \
  --region eu-central-1 \
  --query 'Service.Status'
```

### Update Environment Variables
```bash
aws apprunner update-service \
  --service-arn $SERVICE_ARN \
  --source-configuration '{
    "ImageRepository": {
      "ImageConfiguration": {
        "RuntimeEnvironmentVariables": {
          "ULTRAMSG_TOKEN": "new_token_here"
        }
      }
    }
  }' \
  --region eu-central-1
```

---

## 🚨 Troubleshooting

### Issue: Build fails with "pip not found"
**Fix:** Use the Dockerfile I provided. It properly sets up Python.

### Issue: Service unhealthy
**Fix:** Check health endpoint:
```bash
curl https://YOUR_SERVICE_URL/health
# Should return: {"status":"ALIVE"...}
```

### Issue: Environment variables not set
**Fix:** Update via Console or CLI (see above)

### Issue: Port binding error
**Fix:** Ensure your app listens on port 8080 (App Runner default)

---

## 💰 App Runner Pricing

**Compute:**
- 1 vCPU, 2 GB RAM: ~$0.064/hour = ~$46/month
- Includes automatic scaling

**Data Transfer:**
- First 100 GB/month: Free
- After: $0.09/GB

**Estimated Cost:**
- Low traffic (1000 msgs/day): ~$50/month
- Medium traffic (10K msgs/day): ~$60/month

---

## ✅ Deployment Checklist

- [ ] Dockerfile created
- [ ] apprunner.yaml created
- [ ] Code pushed to GitHub OR Docker image built
- [ ] App Runner service created
- [ ] Environment variables set
- [ ] Service deployed successfully
- [ ] Health check passing
- [ ] Webhook URL obtained
- [ ] UltraMsg webhook configured
- [ ] Test message sent & received

---

## 🎯 Quick Commands

```bash
# Deploy from Docker
./deploy-apprunner.sh

# Check service status
aws apprunner list-services --region eu-central-1

# View logs
aws logs tail /aws/apprunner/SERVICE_ARN/service --follow

# Update service
aws apprunner start-deployment --service-arn SERVICE_ARN

# Delete service
aws apprunner delete-service --service-arn SERVICE_ARN
```

---

**🚀 Your AGI is now running on App Runner!**
