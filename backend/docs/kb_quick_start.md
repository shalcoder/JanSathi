# Knowledge Base Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Create Bedrock Knowledge Base (AWS Console)

1. Go to **Amazon Bedrock** → **Knowledge Bases**
2. Click **Create knowledge base**
3. Configure:
   - Name: `JanSathi-KB`
   - Data source: **Amazon S3**
   - Create new S3 bucket: `jansathi-kb-bucket`
   - Embeddings: **Titan Embeddings G1**
   - Vector store: **Default (managed)**
4. Click **Create**
5. Copy the **Knowledge Base ID** (e.g., `XXXXXXXXXX`)

### Step 2: Update Environment Variables

```bash
# Add to backend/.env
BEDROCK_KB_ID=XXXXXXXXXX
BEDROCK_KB_S3_BUCKET=jansathi-kb-bucket
KB_ENABLE_CACHE=true
KB_CACHE_TTL=86400
```

### Step 3: Start Backend

```bash
cd backend
python main.py
```

### Step 4: Test Upload & Query

```bash
# Upload PDF
curl -X POST http://localhost:5000/api/kb/upload \
  -F "file=@your_scheme.pdf" \
  -F "user_id=test_user"

# Wait 5-10 minutes for indexing...

# Query (First time - Cache MISS)
curl -X POST http://localhost:5000/api/kb/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this scheme about?",
    "language": "en"
  }'

# Query again (Cache HIT - Cost: $0.00)
curl -X POST http://localhost:5000/api/kb/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this scheme about?",
    "language": "en"
  }'

# Check cache stats
curl http://localhost:5000/api/kb/stats
```

---

## 📊 How Caching Works

```
User Query: "What is PM-KISAN?"
                │
                ▼
        ┌───────────────┐
        │ Check Cache   │
        └───────┬───────┘
                │
        ┌───────┴────────┐
        │                │
    ✅ FOUND         ❌ NOT FOUND
        │                │
        │                ▼
        │        ┌──────────────┐
        │        │ Query Bedrock│
        │        │ Knowledge Base│
        │        └──────┬───────┘
        │               │
        │               ▼
        │        ┌──────────────┐
        │        │ Generate     │
        │        │ Answer       │
        │        └──────┬───────┘
        │               │
        │               ▼
        │        ┌──────────────┐
        │        │ Store in     │
        │        │ Cache        │
        │        └──────┬───────┘
        │               │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Return Answer │
        └───────────────┘

Cost: $0.00        Cost: $0.02
```

---

## 💰 Cost Comparison

### Scenario: 1000 queries/month

**Without Caching:**
```
1000 queries × $0.02 = $20/month
```

**With 85% Cache Hit Rate:**
```
150 unique queries × $0.02 = $3/month
850 cached queries × $0.00 = $0/month
Total: $3/month (85% savings!)
```

---

## 🔧 Common Use Cases

### 1. Upload Government Scheme PDFs
```python
import requests

files = {'file': open('pmkisan_guidelines.pdf', 'rb')}
data = {'user_id': 'admin', 'document_type': 'scheme'}

response = requests.post(
    'http://localhost:5000/api/kb/upload',
    files=files,
    data=data
)
print(response.json())
```

### 2. Query in Multiple Languages
```python
# English
response = requests.post('http://localhost:5000/api/kb/query', json={
    "question": "What is PM-KISAN?",
    "language": "en"
})

# Hindi
response = requests.post('http://localhost:5000/api/kb/query', json={
    "question": "PM-KISAN क्या है?",
    "language": "hi"
})
```

### 3. Personalized Queries
```python
response = requests.post('http://localhost:5000/api/kb/query', json={
    "question": "Am I eligible for this scheme?",
    "language": "en",
    "user_context": {
        "occupation": "farmer",
        "location_state": "UP",
        "annual_income": 50000,
        "land_holding_acres": 2.5
    }
})
```

---

## 📈 Monitoring

### Check Cache Performance
```bash
curl http://localhost:5000/api/kb/stats
```

**Response:**
```json
{
    "total_cached_queries": 150,
    "cached_last_24h": 45,
    "cache_ttl_hours": 24,
    "estimated_cost_saved": 3.00,
    "language_distribution": {
        "hi": 100,
        "en": 50
    }
}
```

### Clear Cache When Documents Updated
```bash
# Clear all cache
curl -X DELETE "http://localhost:5000/api/kb/cache?all=true"

# Clear specific query
curl -X DELETE "http://localhost:5000/api/kb/cache?query=what+is+pm-kisan&language=en"
```

---

## 🐛 Troubleshooting

### "Knowledge Base service not available"
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify KB exists
aws bedrock-agent get-knowledge-base --knowledge-base-id $BEDROCK_KB_ID
```

### "No results found"
- Wait 5-10 minutes after upload for indexing
- Check S3 bucket has the PDF
- Verify KB sync status in AWS Console

### Cache not working
```bash
# Check database
sqlite3 instance/jansathi.db "SELECT COUNT(*) FROM bedrock_query_cache;"

# Verify cache is enabled
curl http://localhost:5000/api/kb/health
```

---

## 🎯 Best Practices

1. **Upload PDFs with clear names**: `pmkisan_eligibility_2024.pdf`
2. **Set appropriate cache TTL**: 24 hours for static content, 1 hour for dynamic
3. **Monitor cache hit rate**: Target >80% for cost efficiency
4. **Clean up old cache**: Run weekly cleanup job
5. **Invalidate cache**: When documents are updated

---

## 📚 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/kb/upload` | POST | Upload PDF to Knowledge Base |
| `/api/kb/query` | POST | Query with intelligent caching |
| `/api/kb/stats` | GET | Get cache statistics |
| `/api/kb/cache` | DELETE | Invalidate cache entries |
| `/api/kb/cache/cleanup` | POST | Remove old cache entries |
| `/api/kb/health` | GET | Service health check |

---

## 🚀 Next Steps

1. Upload your first PDF document
2. Test queries and verify caching works
3. Monitor cache statistics
4. Integrate with frontend UI
5. Set up automated cache cleanup

For detailed documentation, see: `docs/knowledge_base_caching.md`
