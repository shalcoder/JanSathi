# 🔐 Environment Files for JanSathi Setup

## ⚠️ SECURITY WARNING
These files contain sensitive AWS credentials. Share only via secure channels (encrypted email, secure messaging, etc.). Never commit to public repositories.

## 📁 File 1: backend/.env
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIARODGW73MZFXZGXGY
AWS_SECRET_ACCESS_KEY=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
AWS_REGION=us-east-1

# S3 Bucket
S3_BUCKET_NAME=jansathi-audio-bucket-1770462916

# Bedrock Configuration - Using cheapest model for cost efficiency
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Kendra (DISABLED - Using Mock)
KENDRA_INDEX_ID=mock-index

# Flask Configuration
SECRET_KEY=87e0ecaf-c1dd-4c81-9564-069d8a24865b
NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=sqlite:///jansathi.db

# Port
PORT=5000
```

## 📁 File 2: frontend/.env.local
```env
# JanSathi Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=test_example_key
```

## 📋 Setup Instructions for Team Member

1. **Save File 1** as `backend/.env` in the JanSathi project
2. **Save File 2** as `frontend/.env.local` in the JanSathi project
3. **Never commit these files** - they're already in .gitignore
4. **Follow the main setup instructions** in SETUP_INSTRUCTIONS.md

## 🔒 Security Notes

- These credentials provide access to AWS services
- Monthly cost limit: ~$5 for normal usage
- AWS free tier covers most services (Polly, Transcribe, S3)
- Monitor costs daily during development
- Rotate credentials if accidentally exposed

## 💰 Cost Information

- **Current usage**: ~$0.001 (practically free)
- **Safe daily limit**: 1000 queries = $0.05/day
- **Monthly projection**: $1.50/month for normal development
- **AWS free tier**: Covers Polly (5M chars), Transcribe (60 min), S3 (5GB)
- **Bedrock**: Only paid service, but very cheap with Haiku model

## 🧪 Test After Setup

Run this command to verify everything works:
```bash
cd scripts
python test_aws_services.py
```

Expected output should show all services as ✅ working.