#!/bin/bash

# 🚀 Automated AWS App Runner Deployment Script

set -e

echo "🚀 Starting AWS App Runner Deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SERVICE_NAME="harshal-agi-service"
REGION="eu-central-1"
REPO_NAME="harshal-agi"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed. Install it first:${NC}"
    echo "https://docs.docker.com/get-docker/"
    exit 1
fi

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not installed. Install it first:${NC}"
    echo "https://aws.amazon.com/cli/"
    exit 1
fi

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS Account: $ACCOUNT_ID${NC}"

# Step 1: Create ECR repository
echo -e "${YELLOW}[1/6] Creating ECR repository...${NC}"
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION 2>/dev/null || \
  aws ecr create-repository --repository-name $REPO_NAME --region $REGION --output text > /dev/null

echo -e "${GREEN}✅ ECR repository ready${NC}"

# Step 2: Build Docker image
echo -e "${YELLOW}[2/6] Building Docker image...${NC}"
docker build -t $REPO_NAME . --quiet

echo -e "${GREEN}✅ Docker image built${NC}"

# Step 3: Login to ECR
echo -e "${YELLOW}[3/6] Logging into ECR...${NC}"
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com 2>/dev/null

echo -e "${GREEN}✅ Logged into ECR${NC}"

# Step 4: Tag and push image
echo -e "${YELLOW}[4/6] Pushing image to ECR...${NC}"
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest"
docker tag $REPO_NAME:latest $IMAGE_URI
docker push $IMAGE_URI --quiet

echo -e "${GREEN}✅ Image pushed: $IMAGE_URI${NC}"

# Step 5: Create or update App Runner service
echo -e "${YELLOW}[5/6] Deploying to App Runner...${NC}"

# Check if service exists
SERVICE_ARN=$(aws apprunner list-services --region $REGION \
  --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" \
  --output text 2>/dev/null || echo "")

if [ -z "$SERVICE_ARN" ]; then
    echo "Creating new App Runner service..."
    
    # Create IAM role for App Runner
    ROLE_NAME="AppRunnerECRAccessRole"
    
    # Check if role exists
    aws iam get-role --role-name $ROLE_NAME 2>/dev/null || {
        echo "Creating IAM role..."
        
        # Trust policy
        cat > /tmp/trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
        
        aws iam create-role \
          --role-name $ROLE_NAME \
          --assume-role-policy-document file:///tmp/trust-policy.json \
          --output text > /dev/null
        
        aws iam attach-role-policy \
          --role-name $ROLE_NAME \
          --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
        
        echo "Waiting for role to propagate..."
        sleep 10
    }
    
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    
    # Create service
    SERVICE_ARN=$(aws apprunner create-service \
      --service-name $SERVICE_NAME \
      --source-configuration "{
        \"ImageRepository\": {
          \"ImageIdentifier\": \"$IMAGE_URI\",
          \"ImageRepositoryType\": \"ECR\",
          \"ImageConfiguration\": {
            \"Port\": \"8080\",
            \"RuntimeEnvironmentVariables\": {
              \"AWS_REGION\": \"$REGION\",
              \"ENVIRONMENT\": \"PRODUCTION\"
            }
          }
        },
        \"AutoDeploymentsEnabled\": true,
        \"AuthenticationConfiguration\": {
          \"AccessRoleArn\": \"$ROLE_ARN\"
        }
      }" \
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
      --region $REGION \
      --query 'Service.ServiceArn' \
      --output text)
    
    echo "Service created: $SERVICE_ARN"
else
    echo "Service exists, updating..."
    aws apprunner update-service \
      --service-arn $SERVICE_ARN \
      --source-configuration "{
        \"ImageRepository\": {
          \"ImageIdentifier\": \"$IMAGE_URI\",
          \"ImageRepositoryType\": \"ECR\"
        }
      }" \
      --region $REGION \
      --output text > /dev/null
fi

echo -e "${GREEN}✅ App Runner service deployed${NC}"

# Step 6: Wait for deployment
echo -e "${YELLOW}[6/6] Waiting for service to be ready...${NC}"

for i in {1..60}; do
    STATUS=$(aws apprunner describe-service \
      --service-arn $SERVICE_ARN \
      --region $REGION \
      --query 'Service.Status' \
      --output text)
    
    if [ "$STATUS" == "RUNNING" ]; then
        break
    fi
    
    echo "Status: $STATUS (waiting...)"
    sleep 10
done

# Get service URL
SERVICE_URL=$(aws apprunner describe-service \
  --service-arn $SERVICE_ARN \
  --region $REGION \
  --query 'Service.ServiceUrl' \
  --output text)

echo ""
echo "=========================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "📋 Service Details:"
echo "   • Name: $SERVICE_NAME"
echo "   • Status: $STATUS"
echo "   • Region: $REGION"
echo ""
echo "🔗 Your Service URL:"
echo -e "${GREEN}https://$SERVICE_URL${NC}"
echo ""
echo "🔗 Your Webhook URL:"
echo -e "${GREEN}https://$SERVICE_URL/webhook${NC}"
echo ""
echo "⚠️  IMPORTANT: Set environment variables in App Runner Console:"
echo "   1. Go to: https://console.aws.amazon.com/apprunner"
echo "   2. Select service: $SERVICE_NAME"
echo "   3. Configuration → Environment variables → Edit"
echo "   4. Add:"
echo "      ULTRAMSG_INSTANCE_ID = your_instance_id"
echo "      ULTRAMSG_TOKEN = your_token"
echo "      GEMINI_API_KEY = your_gemini_key"
echo "      ADMIN_PHONE = 971XXXXXXXXX"
echo ""
echo "📱 Next Steps:"
echo "   1. Set environment variables (see above)"
echo "   2. Go to UltraMsg Dashboard"
echo "   3. Set webhook URL: https://$SERVICE_URL/webhook"
echo "   4. Enable 'on.message' event"
echo "   5. Send test WhatsApp message"
echo ""
echo "🔍 Monitor Logs:"
echo "   aws logs tail /aws/apprunner/$SERVICE_ARN/service --follow --region $REGION"
echo ""
echo "🚀 Your AGI is LIVE on App Runner!"

# Save webhook URL
echo "https://$SERVICE_URL/webhook" > webhook-url.txt
echo "Webhook URL saved to: webhook-url.txt"
