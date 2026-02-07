# 🤖 AI Assistant Setup Prompt for JanSathi Project

## Context for AI Assistant

You are helping a developer set up the **JanSathi** project - a voice-first AI assistant for government services in rural India. This is a full-stack application built for the AI Bharat Hackathon 2026.

## 🏗️ Project Architecture

**JanSathi** is a comprehensive government services AI assistant with:

### Backend (Python Flask)
- **AWS Bedrock** integration with Claude 3 Haiku for text generation
- **AWS Polly** for neural text-to-speech in multiple languages
- **AWS Transcribe** for speech-to-text conversion
- **AWS S3** for audio file storage with lifecycle policies
- **RAG (Retrieval Augmented Generation)** system for government scheme information
- **SQLite database** for conversation history
- **Multi-language support** (Hindi, English, Kannada, Tamil)

### Frontend (Next.js 16 with TypeScript)
- **Voice input/output** interface
- **Document analysis** with Claude 3 Vision
- **Real-time chat** with AI responses
- **Government scheme cards** with structured information
- **Audio playback** for AI responses
- **Multi-language switching**

### AWS Services Integration
- **Bedrock**: Claude 3 Haiku ($0.25 per 1M tokens) - CHEAPEST option
- **Polly**: FREE tier (5M characters/month for 12 months)
- **Transcribe**: FREE tier (60 minutes/month for 12 months)
- **S3**: FREE tier (5GB storage for 12 months)
- **Total monthly cost**: ~$1-5 for normal usage (well within $100 free credits)

## 🎯 What the Application Does

1. **Voice-First Government Assistant**: Users can speak questions about government schemes
2. **Multi-Modal Interaction**: Text, voice, and document analysis
3. **Government Scheme Expertise**: PM Kisan, Ayushman Bharat, Ujjwala Yojana, etc.
4. **Document Analysis**: Upload government forms/notices for AI analysis
5. **Audio Responses**: Every answer includes neural voice synthesis
6. **Cost-Optimized**: Designed to work within AWS free tier limits

## 🔧 Technical Setup Requirements

### Prerequisites
- **Python 3.11+** (Anaconda recommended)
- **Node.js 18+**
- **AWS Account** with $100 free credits
- **Git**
- **Windows/Linux/Mac** (tested on Windows)

### AWS Services Setup Required
1. **AWS CLI** configured with credentials
2. **Bedrock model access** enabled for:
   - Anthropic Claude 3 Haiku (text generation)
   - Anthropic Claude 3.5 Haiku (vision analysis)
3. **S3 bucket** created for audio storage
4. **IAM permissions** for Bedrock, Polly, Transcribe, S3

## 📁 Project Structure
```
JanSathi/
├── backend/                 # Python Flask API
│   ├── app/
│   │   ├── api/routes.py   # Main API endpoints
│   │   ├── services/       # AWS service integrations
│   │   ├── models/         # Database models
│   │   └── core/           # Utilities
│   ├── main.py             # Flask app entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env               # AWS credentials (SENSITIVE)
├── frontend/               # Next.js React app
│   ├── src/
│   │   ├── app/           # Next.js 16 app router
│   │   ├── components/    # React components
│   │   └── services/      # API client
│   ├── package.json       # Node dependencies
│   └── .env.local        # Frontend config (SENSITIVE)
├── scripts/               # Utility scripts
│   ├── test_aws_services.py  # AWS services test
│   └── setup_aws.ps1     # AWS setup automation
└── docs/                  # Documentation
```

## 🚀 Setup Instructions for Developer

### Step 1: Clone and Navigate
```bash
git clone [repository-url]
cd JanSathi
```

### Step 2: Backend Setup
```bash
# Create conda environment
conda create -n jansathi python=3.11 -y
conda activate jansathi

# Install Python dependencies
cd backend
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
```

### Step 4: Environment Configuration
**CRITICAL**: The developer needs these environment files (sent separately):

**backend/.env** (contains AWS credentials)
**frontend/.env.local** (contains API configuration)

### Step 5: AWS Bedrock Model Access
1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
2. Click "Manage model access"
3. Enable:
   - ✅ Anthropic Claude 3 Haiku
   - ✅ Anthropic Claude 3.5 Haiku
4. Wait for "Access granted" status

### Step 6: Test Setup
```bash
# Test AWS services
cd scripts
python test_aws_services.py

# Start backend (Terminal 1)
cd backend
python main.py

# Start frontend (Terminal 2)
cd frontend
npm run dev
```

### Step 7: Verify Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 🧪 Testing the Application

### API Tests
```bash
# Test PM Kisan scheme query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"text_query": "What is PM Kisan scheme?", "language": "en", "userId": "test_user"}'

# Test conversation history
curl http://localhost:5000/history?userId=test_user&limit=5

# Test market rates
curl http://localhost:5000/market-rates
```

### Frontend Features to Test
1. **Chat Interface**: Ask about government schemes
2. **Voice Input**: Click microphone, speak questions
3. **Document Analysis**: Upload government documents via camera icon
4. **Audio Playback**: Listen to AI responses
5. **Language Switching**: Try Hindi, English, Kannada, Tamil

## 💰 Cost Management

### Current Configuration (Cost-Optimized)
- **Bedrock Model**: Claude 3 Haiku (cheapest at $0.25/1M tokens)
- **Daily Safe Limit**: 1,000 queries = $0.05/day
- **Monthly Budget**: $5/month = 100,000 queries
- **Free Tier Services**: Polly, Transcribe, S3, Lambda

### Cost Monitoring
```bash
# Check AWS costs
aws ce get-cost-and-usage --time-period Start=2026-02-07,End=2026-02-08 --granularity DAILY --metrics BlendedCost
```

## 🔍 Troubleshooting Common Issues

### "Bedrock access denied"
- Enable models in AWS Bedrock console
- Wait 5-10 minutes for access approval
- Verify IAM permissions

### "No module found" errors
- Ensure conda environment is activated: `conda activate jansathi`
- Reinstall requirements: `pip install -r requirements.txt`

### "Port already in use"
- Kill existing processes: `taskkill /F /IM python.exe` (Windows)
- Use different ports in configuration

### "CORS errors"
- Check `ALLOWED_ORIGINS` in backend/.env
- Ensure frontend URL matches backend CORS settings

## 🎯 Expected Functionality

After successful setup, the application should:

1. **Respond to government scheme queries** with structured information
2. **Generate audio responses** using AWS Polly neural voices
3. **Accept voice input** and convert to text queries
4. **Analyze uploaded documents** using Claude 3 Vision
5. **Display scheme cards** with benefits, links, and logos
6. **Support multiple languages** with automatic translation
7. **Maintain conversation history** in SQLite database
8. **Handle non-government queries** gracefully with appropriate redirects

## 📊 Success Metrics

- ✅ All AWS services responding without errors
- ✅ Audio files generated and playable
- ✅ Voice input working in browser
- ✅ Document analysis returning meaningful results
- ✅ Multi-language responses working
- ✅ Conversation history saving and retrieving
- ✅ Daily costs under $0.10 for testing

## 🆘 Support

If issues persist:
1. Check AWS service status and quotas
2. Verify all environment variables are set correctly
3. Test individual AWS services using the test script
4. Monitor AWS CloudWatch logs for detailed error messages
5. Contact the original developer for AWS credential verification

This application represents a production-ready government services AI assistant optimized for cost-efficiency and scalability within AWS free tier limits.