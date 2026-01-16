# 🤖 Harshal DXB AGI - WhatsApp Real Estate Bot

AI-powered WhatsApp bot for Dubai real estate using AWS App Runner, DynamoDB, and Google Gemini.

## 🚀 Features

- **WhatsApp Integration** via UltraMsg API
- **AI Brain** powered by Google Gemini 2.0
- **Property Search** with intelligent matching
- **Agent Marketplace** with lead auction system
- **Multi-language Support** (English, Hindi, Arabic)
- **Inventory Management** with verification
- **Admin Control Panel** via WhatsApp commands
- **100% Secure** - No direct contact between clients and agents

## 📋 Architecture

```
WhatsApp User → UltraMsg → AWS App Runner → DynamoDB
                                ↓
                         Google Gemini AI
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask
- **AI**: Google Gemini 2.0-flash
- **Database**: AWS DynamoDB
- **Hosting**: AWS App Runner
- **WhatsApp API**: UltraMsg
- **Container**: Docker

## 📦 Quick Deploy

### Prerequisites
- AWS Account
- Docker installed
- AWS CLI configured
- UltraMsg account
- Google Gemini API key

### Deploy to AWS App Runner

1. **Clone the repository**
   ```bash
   git clone https://github.com/harshaldxbweb-svg/harshal-dxb-agi.git
   cd harshal-dxb-agi
   ```

2. **Deploy using script**
   ```bash
   chmod +x deploy-apprunner.sh
   ./deploy-apprunner.sh
   ```

3. **Set environment variables in App Runner Console**
   - `ULTRAMSG_INSTANCE_ID`
   - `ULTRAMSG_TOKEN`
   - `GEMINI_API_KEY`
   - `ADMIN_PHONE`

4. **Configure UltraMsg webhook**
   - Set webhook URL to your App Runner URL + `/webhook`
   - Enable `on.message` event

5. **Test!**
   - Send WhatsApp message to your bot number
   - Response should arrive in 3-5 seconds

## 📚 Documentation

- [App Runner Deployment Guide](APPRUNNER_DEPLOYMENT.md)
- [Lambda Deployment Guide](LAMBDA_DEPLOYMENT.md)
- [UltraMsg Setup](ULTRAMSG_SETUP.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [System Flow](SYSTEM_FLOW.md)

## 🔧 Configuration

Create `.env` file (for local testing):
```env
ULTRAMSG_INSTANCE_ID=instance123456
ULTRAMSG_TOKEN=your_token
GEMINI_API_KEY=your_gemini_key
ADMIN_PHONE=971XXXXXXXXX
AWS_REGION=eu-central-1
ENVIRONMENT=PRODUCTION
```

## 🏗️ Project Structure

```
harshal-dxb-agi/
├── main.py                      # Main Flask application
├── lambda_handler.py            # AWS Lambda handler
├── database_manager.py          # DynamoDB operations
├── ai_brain.py                  # Google Gemini integration
├── cognitive_engine.py          # Message processing
├── visual_engine.py             # Response formatting
├── lead_auction_engine.py       # Agent marketplace
├── inventory_verifier.py        # Property verification
├── language_engine.py           # Multi-language support
├── property_listing_engine.py   # Property listings
├── async_lead_engine.py         # Async notifications
├── agent_registration.py        # Agent onboarding
├── client_intake.py             # Client management
├── commission_engine.py         # Commission tracking
├── Dockerfile                   # Docker configuration
├── apprunner.yaml              # App Runner config
├── requirements.txt            # Python dependencies
└── deploy-apprunner.sh         # Deployment script
```

## 🎯 Key Components

### 1. AGI Master Executive
Main controller that orchestrates all operations:
- Message filtering and sanitization
- Intent detection
- Admin commands
- Response generation

### 2. Database Manager
DynamoDB operations for:
- Client profiles
- Agent/Partner management
- Property inventory
- Deal tracking
- Audit logs

### 3. AI Brain
Google Gemini integration for:
- Natural language understanding
- Context-aware responses
- Multi-turn conversations

### 4. Lead Auction Engine
Marketplace system where:
- Clients post requirements
- Agents compete to respond
- Fastest verified response wins

## 🔐 Security Features

- Group message filtering
- Bypass attempt detection
- Phone number protection
- Admin control mode
- Audit logging
- Rate limiting

## 💰 Cost Estimate

**AWS App Runner:**
- ~$50/month for 1000 messages/day
- Includes auto-scaling and load balancing

**DynamoDB:**
- Free tier: 25GB storage
- Pay-per-request pricing

**Total:** ~$50-60/month for moderate traffic

## 🧪 Testing

### Local Testing
```bash
# Run locally
docker build -t harshal-agi .
docker run -p 8080:8080 --env-file .env harshal-agi

# Test health endpoint
curl http://localhost:8080/health
```

### Production Testing
```bash
# Test webhook
curl -X POST https://YOUR_APP_URL/webhook \
  -H "Content-Type: application/json" \
  -d '{"from":"test@c.us","body":"test","type":"chat"}'
```

## 📊 Monitoring

### View Logs
```bash
aws logs tail /aws/apprunner/SERVICE_ARN/service --follow
```

### Check Status
```bash
aws apprunner describe-service --service-arn SERVICE_ARN
```

## 🤝 Contributing

This is a private project. For access, contact the repository owner.

## 📄 License

Proprietary - All rights reserved

## 👨‍💻 Author

**Harshal DXB**
- GitHub: [@harshaldxbweb-svg](https://github.com/harshaldxbweb-svg)

## 🆘 Support

For issues or questions:
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Documentation](APPRUNNER_DEPLOYMENT.md)
3. Contact repository owner

## 🎉 Acknowledgments

- AWS App Runner for serverless hosting
- Google Gemini for AI capabilities
- UltraMsg for WhatsApp API
- DynamoDB for scalable storage

---

**🚀 Built with ❤️ for Dubai Real Estate Market**
