# AI Assistant Handoff Prompt for JanSathi Project

## 🎯 Quick Context
You are now working on **JanSathi**, a voice-first AI assistant for Indian citizens to access government schemes. The project has been enhanced with improved RAG capabilities and AWS Kendra integration.

## 📍 Current State
- **Branch**: `kv2` (contains all latest changes)
- **Status**: Enhanced RAG system working in mock mode, Kendra integration ready
- **Backend**: Flask + AWS (Bedrock, Polly, Transcribe, S3) running on port 5000
- **Frontend**: Next.js PWA (not currently active in this session)

## 🔧 Key Changes Made
1. **Smart Query Classification**: System now distinguishes government vs general questions
2. **AWS Kendra Integration**: Semantic search ready (currently in mock mode)
3. **Improved Response System**: Different prompts for different query types
4. **Document Upload Ready**: Can index uploaded documents to Kendra
5. **Production Infrastructure**: CDK code for Kendra deployment

## 📁 Critical Files to Understand
```
backend/app/services/rag_service.py     # Core RAG logic with Kendra integration
backend/app/services/bedrock_service.py # AI response generation with dual prompts
backend/app/api/routes.py               # API endpoints with health status
infrastructure/stacks/data_stack.py    # Kendra infrastructure code
scripts/setup_kendra.py                # Kendra population script
KENDRA_SETUP_GUIDE.md                  # Complete setup documentation
```

## 🧪 Current Testing Status
**Working Queries**:
- `"PM Kisan scheme benefits"` → Returns detailed scheme info
- `"How to start small business?"` → Returns MUDRA loan + Skill India
- `"health insurance for poor"` → Returns Ayushman Bharat

**General Queries (Non-Government)**:
- `"What is 2 plus 2?"` → Returns general guidance response
- `"Recipe for chocolate cake?"` → Returns general guidance response

**Edge Cases (Some Issues)**:
- `"Who is Prime Minister?"` → False positive (matches "Pradhan Mantri")
- `"How does machine learning work?"` → False positive (matches "learning")

## 🚨 Known Issues
1. **Hindi Encoding**: PowerShell shows `?????` for Hindi text (use Postman instead)
2. **False Positives**: Some non-government queries match schemes due to common words
3. **Module Reloading**: Need to restart backend after code changes
4. **Kendra Costs**: $810/month after free tier (currently using mock mode)

## 🔍 Quick Diagnostic Commands
```bash
# Check system health
curl http://localhost:5000/health

# Test government query
curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"text_query": "PM Kisan scheme", "language": "en"}'

# Test general query  
curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"text_query": "What is the weather?", "language": "en"}'

# Check backend logs
# Look at terminal running: python main.py
```

## 🎯 Immediate Tasks if Continuing
1. **Fix Hindi encoding** in PowerShell testing
2. **Improve false positive filtering** for edge cases
3. **Test Kendra deployment** (optional, costs money)
4. **Add more test cases** for query classification

## 🔧 Environment Setup (If Starting Fresh)
```bash
# Clone and switch branch
git clone https://github.com/shalcoder/JanSathi.git
cd JanSathi
git checkout kv2

# Backend setup
cd backend
conda activate jansathi  # or create new env
pip install -r requirements.txt
python main.py  # Should start on port 5000

# Test basic functionality
curl http://localhost:5000/health
```

## 📊 System Architecture
```
User Query → API Routes → RAG Service → Bedrock Service → Response
                ↓              ↓           ↓
            Query Classification → Kendra/Local Search → AI Generation
```

## 🎯 Success Criteria
- [ ] Government queries return relevant scheme information
- [ ] General queries return appropriate general responses  
- [ ] No crashes or errors in basic functionality
- [ ] Health endpoint shows system status correctly
- [ ] Hindi queries work (encoding issues aside)

## 🚀 Optional Advanced Tasks
- [ ] Deploy Kendra infrastructure (`scripts/deploy_kendra.bat`)
- [ ] Test document upload and indexing
- [ ] Improve query classification accuracy
- [ ] Add more government schemes to knowledge base

## 💡 Key Insights for AI Assistant
- The system is **production-ready** but currently in **mock mode** for cost reasons
- **Kendra integration** is complete but not deployed (would cost $810/month)
- **Query classification** is the key innovation - it determines response type
- **Bedrock service** uses different prompts based on query classification
- **All AWS services** are working (Bedrock, Polly, Transcribe, S3)

## 🔗 Quick Reference
- **Health Check**: `GET /health` shows Kendra status and component health
- **Main Query**: `POST /query` with `{"text_query": "...", "language": "en"}`
- **Backend Port**: 5000
- **Environment**: `.env` file in backend folder
- **Logs**: Terminal running `python main.py`

---
**Handoff Date**: February 14, 2026  
**Previous AI**: Completed enhanced RAG system with Kendra integration  
**Status**: Ready for continued development or production deployment