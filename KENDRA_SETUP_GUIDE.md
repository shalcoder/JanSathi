# JanSathi Kendra Setup Guide

This guide will help you enable AWS Kendra for semantic search in JanSathi, replacing the hardcoded scheme database with a powerful AI-powered search engine.

## 🎯 What Kendra Provides

- **Semantic Search**: Natural language queries like "health insurance for poor families"
- **Document Indexing**: Upload and search through government documents
- **Intelligent Ranking**: AI-powered relevance scoring
- **Multi-format Support**: PDFs, Word docs, text files, web pages

## 💰 Cost Considerations

- **Developer Edition**: 750 hours/month free tier
- **After free tier**: ~$810/month (consider for production only)
- **Alternative**: Use Enterprise Edition for $1,008/month with more features

⚠️ **Important**: Kendra can be expensive. Only enable for production or when you have sufficient AWS credits.

## 🚀 Quick Setup (Automated)

1. **Deploy Infrastructure**:
   ```bash
   cd JanSathi/scripts
   deploy_kendra.bat
   ```

2. **Verify Setup**:
   ```bash
   python test_kendra.py
   ```

3. **Restart Backend**:
   ```bash
   cd JanSathi/backend
   python main.py
   ```

## 🔧 Manual Setup

### Step 1: Deploy Kendra Infrastructure

```bash
cd JanSathi/infrastructure
cdk deploy JanSathi-Data --require-approval never
```

### Step 2: Get Kendra Index ID

After deployment, get the Kendra Index ID from CDK outputs:

```bash
aws cloudformation describe-stacks --stack-name JanSathi-Data --query "Stacks[0].Outputs[?OutputKey=='KendraIndexId'].OutputValue" --output text
```

### Step 3: Update Environment

Update `JanSathi/backend/.env`:

```env
# Replace mock-index with your actual Kendra Index ID
KENDRA_INDEX_ID=your-kendra-index-id-here
```

### Step 4: Populate Kendra

```bash
cd JanSathi/scripts
python setup_kendra.py
```

### Step 5: Test Integration

```bash
python test_kendra.py
```

## 📚 How It Works

### Before (Mock Mode)
- Hardcoded 11 government schemes
- Simple keyword matching
- Limited to predefined data

### After (Kendra Mode)
- AI-powered semantic search
- Upload and index new documents
- Natural language queries
- Intelligent result ranking

### Example Queries

**Before**: Only worked with exact scheme names
- "PM Kisan" ✅
- "farmer money scheme" ❌

**After**: Works with natural language
- "PM Kisan" ✅
- "farmer money scheme" ✅
- "financial help for agriculture" ✅
- "government support for crops" ✅

## 🔄 Switching Back to Mock Mode

If you want to disable Kendra and go back to mock mode:

1. Update `.env`:
   ```env
   KENDRA_INDEX_ID=mock-index
   ```

2. Restart backend

## 📖 Adding New Documents

### Via Upload API

```python
# Upload document via API
files = {'file': open('new_scheme.pdf', 'rb')}
response = requests.post('http://localhost:5000/upload', files=files)

# Document will be automatically indexed to Kendra
```

### Programmatically

```python
from app.services.rag_service import RagService

rag_service = RagService()
success = rag_service.index_uploaded_document(
    title="New Government Scheme",
    content="Detailed scheme information...",
    metadata={
        'ministry': 'Ministry of Example',
        'category': 'financial'
    }
)
```

## 🛠️ Troubleshooting

### "Kendra not configured" Error
- Check `KENDRA_INDEX_ID` in `.env`
- Ensure it's not set to `mock-index`
- Verify AWS credentials have Kendra permissions

### "No results found" for Known Schemes
- Wait 5-10 minutes after indexing for Kendra to process
- Check if documents were indexed successfully
- Verify Kendra index status in AWS Console

### High AWS Costs
- Monitor usage in AWS Cost Explorer
- Consider using mock mode for development
- Set up billing alerts

## 📊 Monitoring

### Check Kendra Usage
```bash
aws kendra describe-index --index-id your-index-id
```

### View Search Analytics
- AWS Console → Kendra → Your Index → Analytics
- Query patterns and performance metrics

## 🎉 Benefits After Setup

1. **Better Search**: Natural language queries work perfectly
2. **Document Upload**: Users can upload and search government documents
3. **Scalability**: Handles thousands of documents efficiently
4. **AI-Powered**: Leverages AWS machine learning for relevance

## 🔒 Security Notes

- Kendra indexes are private by default
- Documents are encrypted at rest
- Access controlled via IAM policies
- No data leaves your AWS account

---

**Ready to enable Kendra?** Run `scripts/deploy_kendra.bat` to get started!