# 🚀 JanSathi Setup Instructions for Team Members

## 📋 Prerequisites
- Python 3.11+ (Anaconda recommended)
- Node.js 18+
- AWS Account with $100 free credits
- Git

## 🔧 Setup Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd JanSathi
```

### 2. Backend Setup
```bash
# Create conda environment
conda create -n jansathi python=3.11 -y
conda activate jansathi

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Configuration
**IMPORTANT:** You need the `.env` file from your teammate!

Copy the `.env` file to `backend/.env` (contains AWS credentials)
Copy the `.env.local` file to `frontend/.env.local`

### 5. AWS Bedrock Model Access
Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess

Enable these models:
- ✅ Anthropic Claude 3 Haiku
- ✅ Anthropic Claude 3.5 Haiku  
- ✅ Amazon Titan Text G1 - Large

### 6. Test Setup
```bash
# Test backend
cd backend
python main.py

# Test frontend (new terminal)
cd frontend  
npm run dev
```

### 7. Verify All Services
```bash
cd scripts
python test_aws_services.py
```

## 🌐 Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/health

## 💰 Cost Monitoring
- Daily limit: 1000 queries = $0.05/day
- Monthly budget: $5/month = safe usage
- Check costs: `aws ce get-cost-and-usage --time-period Start=2026-02-07,End=2026-02-08 --granularity DAILY --metrics BlendedCost`

## 🆘 Troubleshooting
1. **"Bedrock access denied"** → Enable models in AWS console
2. **"No module found"** → Check conda environment activation
3. **"Port in use"** → Kill existing processes or use different ports
4. **"CORS error"** → Check ALLOWED_ORIGINS in .env

## 📞 Contact
If you face issues, contact the team member who shared the AWS credentials.