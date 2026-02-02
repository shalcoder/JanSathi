# JanSathi (जनसाथी)

**JanSathi** is a voice-first, AI-powered rural assistant aimed at bridging the digital divide for Indian citizens. It leverages a serverless architecture to provide accurate, hyper-local information (like Mandi prices, schemes) in native dialects.

## Architecture
- **Frontend**: Flutter (Mobile App)
- **Backend**: Python (Flask / AWS Lambda)
- **AI Stack**: 
  - AWS Transcribe (STT)
  - AWS Bedrock (Claude - Reasoning)
  - AWS Kendra / FAISS (RAG - Knowledge)
  - AWS Polly (TTS)

## Getting Started

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Setup `.env` with AWS Credentials.
4. `python server.py`

### Frontend
1. `cd frontend`
2. `flutter pub get`
3. `flutter run`

## License
MIT
