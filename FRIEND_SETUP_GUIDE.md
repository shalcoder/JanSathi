# 🚀 JanSathi Setup Guide for Team Member

## 📋 What You're Setting Up

**JanSathi** is a voice-first AI assistant for government services in rural India, built for AI Bharat Hackathon 2026. It integrates multiple AWS services and provides multi-modal interaction (text, voice, vision).

## 🎯 Quick Overview
- **Backend**: Python Flask with AWS Bedrock, Polly, Transcribe, S3
- **Frontend**: Next.js 16 with TypeScript, voice input/output
- **AI**: Claude 3 Haiku for text, Claude 3.5 Haiku for vision
- **Cost**: ~$1-5/month (well within $100 AWS free credits)
- **Languages**: Hindi, English, Kannada, Tamil

## 🔧 Prerequisites Installation

### 1. Install Python (Anaconda)
```bash
# Download from: https://www.anaconda.com/download
# Or use existing Python 3.11+
python --version  # Should be 3.11+
```

### 2. Install Node.js
```bash
# Download from: https://nodejs.org (LTS version)
node --version  # Should be 18+
npm --version
```

### 3. Install Git
```bash
# Download from: https://git-scm.com
git --version
```

## 📦 Project Setup

### Step 1: Clone Repository
```bash
git clone [YOUR_REPOSITORY_URL]
cd JanSathi
```

### Step 2: Create Environment Files
**IMPORTANT**: Your teammate will send you 2 environment files separately (they contain AWS credentials).

Create these files with the content provided:
- `backend/.env` (AWS credentials and configuration)
- `frontend/.env.local` (Frontend configuration)

### Step 3: Backend Setup
```bash
# Create conda environment
conda create -n jansathi python=3.11 -y
conda activate jansathi

# Navigate to backend and install dependencies
cd backend
pip install -r requirements.txt
```

### Step 4: Frontend Setup
```bash
# Navigate to frontend and install dependencies
cd frontend
npm install
```

### Step 5: AWS Bedrock Model Access
1. **Open AWS Console**: https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
2. **Click**: "Manage model access" or "Request model access"
3. **Enable these models**:
   - ✅ **Anthropic Claude 3 Haiku** (for text generation)
   - ✅ **Anthropic Claude 3.5 Haiku** (for document analysis)
4. **Click**: "Request model access"
5. **Wait**: 2-5 minutes for approval (usually instant)
6. **Verify**: Status shows "Access granted"

## 🧪 Testing Setup

### Test 1: AWS Services
```bash
cd scripts
python test_aws_services.py
```
**Expected**: All services show ✅ (green checkmarks)

### Test 2: Backend API
```bash
# Terminal 1: Start backend
cd backend
python main.py
# Should show: Running on http://127.0.0.1:5000
```

### Test 3: Frontend
```bash
# Terminal 2: Start frontend
cd frontend
npm run dev
# Should show: Ready on http://localhost:3000
```

### Test 4: API Functionality
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test AI query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"text_query": "What is PM Kisan scheme?", "language": "en", "userId": "test_user"}'
```

## 🌐 Using the Application

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

### Features to Test
1. **Chat Interface**: 
   - Go to http://localhost:3000
   - Click "Start Talking" or navigate to Dashboard
   - Ask: "What is PM Kisan scheme?"

2. **Voice Input**:
   - Click microphone icon
   - Speak your question
   - AI will convert speech to text and respond

3. **Document Analysis**:
   - Click camera icon
   - Upload government document/form
   - AI will analyze and explain

4. **Audio Responses**:
   - Every AI response includes audio
   - Click play button to hear neural voice

5. **Multi-language**:
   - Switch between Hindi, English, Kannada, Tamil
   - Try: "प्रधानमंत्री आवास योजना क्या है?"

## 💰 Cost Management

### Current Setup (Cost-Optimized)
- **Bedrock**: Claude 3 Haiku ($0.25 per 1M tokens) - cheapest option
- **Polly**: FREE (5M characters/month for 12 months)
- **Transcribe**: FREE (60 minutes/month for 12 months)
- **S3**: FREE (5GB storage for 12 months)

### Safe Usage Limits
- **Daily**: 1,000 queries = $0.05/day
- **Monthly**: $5/month = 100,000 queries
- **Current usage**: ~$0.001 (practically free)

### Monitor Costs
```bash
aws ce get-cost-and-usage --time-period Start=2026-02-07,End=2026-02-08 --granularity DAILY --metrics BlendedCost
```

## 🔍 Troubleshooting

### "Bedrock access denied"
- **Solution**: Enable models in AWS Bedrock console (Step 5 above)
- **Wait**: 5-10 minutes after requesting access
- **Verify**: Check "Access granted" status

### "No module found" errors
- **Solution**: Activate conda environment
```bash
conda activate jansathi
cd backend
pip install -r requirements.txt
```

### "Port already in use"
- **Windows**: `taskkill /F /IM python.exe`
- **Mac/Linux**: `pkill -f python`
- **Or**: Use different ports in configuration

### "CORS errors"
- **Check**: `ALLOWED_ORIGINS` in backend/.env matches frontend URL
- **Default**: Should be `http://localhost:3000`

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## ✅ Success Checklist

After setup, verify these work:
- [ ] Backend starts without errors (port 5000)
- [ ] Frontend starts without errors (port 3000)
- [ ] AWS services test passes (all ✅)
- [ ] Chat interface responds to queries
- [ ] Audio responses play correctly
- [ ] Voice input converts speech to text
- [ ] Document upload analyzes images
- [ ] Multi-language switching works
- [ ] Conversation history saves

## 🎯 Expected Results

### Successful Query Response Should Include:
```json
{
  "query": "What is PM Kisan scheme?",
  "answer": {
    "text": "✅ **What this is**: PM-KISAN provides ₹6,000 per year...",
    "audio": "https://jansathi-audio-bucket-xxx.s3.amazonaws.com/tts/xxx.mp3"
  },
  "structured_sources": [
    {
      "title": "PM-KISAN Samman Nidhi",
      "benefit": "₹6,000/year Income Support",
      "link": "https://pmkisan.gov.in"
    }
  ]
}
```

### Frontend Should Display:
- Formatted AI response with emojis and structure
- Audio player with playable response
- Government scheme cards with logos and links
- Voice input button (microphone)
- Document upload button (camera)
- Language selector dropdown

## 📞 Support

If you encounter issues:
1. **Check AWS service status**: https://status.aws.amazon.com/
2. **Verify environment files**: Ensure both .env files are correctly placed
3. **Test individual components**: Use the test scripts provided
4. **Check logs**: Look at terminal output for specific error messages
5. **Contact teammate**: For AWS credential or configuration issues

## 🚀 Development Tips

1. **Keep conda environment activated**: `conda activate jansathi`
2. **Monitor costs daily** during development
3. **Use test queries** to avoid excessive API calls
4. **Cache responses** for repeated testing
5. **Check AWS CloudWatch** for detailed service logs

## 📊 Project Status

This is a **production-ready** application with:
- ✅ Complete AWS integration
- ✅ Multi-modal interaction (text, voice, vision)
- ✅ Cost-optimized configuration
- ✅ Error handling and fallbacks
- ✅ Multi-language support
- ✅ Government scheme expertise
- ✅ Conversation history
- ✅ Audio generation and playback

**You're working with a fully functional AI assistant ready for hackathon demonstration!**