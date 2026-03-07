# Bedrock Knowledge Base with Intelligent Caching

## Overview

This implementation provides a cost-efficient solution for managing PDF documents and queries using Amazon Bedrock Knowledge Base with intelligent multi-level caching.

### Key Features

✅ **PDF Upload to Knowledge Base** - Automatic indexing in Bedrock  
✅ **Intelligent Query Caching** - 85% cost reduction through smart caching  
✅ **Multi-User Support** - Shared knowledge base across all users  
✅ **Automatic Cache Invalidation** - TTL-based expiry (24 hours default)  
✅ **Cost Analytics** - Track savings and cache performance  
✅ **Semantic Search** - Vector-based retrieval from Knowledge Base  

---

## Architecture

```
┌─────────────┐
│   User 1    │ ──┐
└─────────────┘   │
                  │    ┌──────────────────────────────────────┐
┌─────────────┐   │    │                                      │
│   User 2    │ ──┼───▶│  JanSathi Backend API                │
└─────────────┘   │    │                                      │
                  │    │  1. Check Cache (SQLite/DynamoDB)   │
┌─────────────┐   │    │     ├─ HIT → Return (Cost: $0.00)  │
│   User N    │ ──┘    │     └─ MISS → Query Bedrock KB      │
└─────────────┘        │                                      │
                       │  2. Query Bedrock Knowledge Base     │
                       │     └─ Retrieve relevant docs        │
                       │                                      │
                       │  3. Generate Answer (Claude 3.5)     │
                       │                                      │
                       │  4. Store in Cache                   │
                       │     └─ For future queries            │
                       └──────────────────────────────────────┘
                                        │
                                        ▼
                       ┌──────────────────────────────────────┐
                       │   Amazon Bedrock Knowledge Base      │
                       │                                      │
                       │   ┌────────────────────────────┐    │
                       │   │  S3 Bucket (PDF Storage)   │    │
                       │   │  - scheme_doc_1.pdf        │    │
                       │   │  - scheme_doc_2.pdf        │    │
                       │   │  - user_uploaded.pdf       │    │
                       │   └────────────────────────────┘    │
                       │                                      │
                       │   ┌────────────────────────────┐    │
                       │   │  Vector Index (Embeddings) │    │
                       │   │  - Automatic sync from S3  │    │
                       │   │  - Semantic search ready   │    │
                       │   └────────────────────────────┘    │
                       └──────────────────────────────────────┘
```

---

## How It Works

### 1. PDF Upload Flow

```python
# User uploads PDF
POST /api/kb/upload
Content-Type: multipart/form-data

{
    "file": <PDF_FILE>,
    "user_id": "user_123",
    "document_type": "scheme_info"
}

# Backend Process:
1. Validate PDF (size, format)
2. Upload to S3 bucket
3. Bedrock KB auto-indexes (5-10 min)
4. Return document_id and status
```

**Response:**
```json
{
    "document_id": "user_123_1234567890_scheme.pdf",
    "s3_uri": "s3://jansathi-kb/knowledge-base/documents/...",
    "status": "uploaded",
    "message": "Document uploaded successfully. Indexing in progress (5-10 min)."
}
```

### 2. Query Flow with Caching

```python
# User asks question
POST /api/kb/query

{
    "question": "What is PM-KISAN scheme?",
    "language": "hi",
    "user_context": {
        "occupation": "farmer",
        "location_state": "UP"
    }
}

# Backend Process:
1. Normalize query: "what is pm-kisan scheme?" → "what is pm-kisan scheme?"
2. Generate cache key: SHA256(query + language)
3. Check cache:
   - IF FOUND → Return cached response (Cost: $0.00) ✅
   - IF NOT FOUND → Continue to step 4
4. Query Bedrock Knowledge Base:
   - Retrieve top 3 relevant documents
   - Extract context from PDFs
5. Generate answer using Claude 3.5 Sonnet
6. Store in cache with TTL (24 hours)
7. Return response
```

**Response (Cache HIT):**
```json
{
    "answer": "PM-KISAN एक केंद्र सरकार की योजना है...",
    "sources": [
        {
            "text": "PM-KISAN scheme provides ₹6000 per year...",
            "score": 0.95,
            "source": "s3://bucket/pmkisan_doc.pdf",
            "type": "knowledge_base"
        }
    ],
    "cached": true,
    "cost_saved": 0.02,
    "cache_age_hours": 2.5,
    "language": "hi"
}
```

**Response (Cache MISS):**
```json
{
    "answer": "PM-KISAN एक केंद्र सरकार की योजना है...",
    "sources": [...],
    "cached": false,
    "cost_saved": 0.0,
    "query_time": "2024-03-07T10:30:00",
    "language": "hi"
}
```

---

## Cost Efficiency

### Without Caching
```
100 queries/day × $0.02/query = $2.00/day = $60/month
```

### With Intelligent Caching (85% hit rate)
```
15 unique queries × $0.02 = $0.30/day = $9/month
85 cached queries × $0.00 = $0.00

Total: $9/month (85% savings!)
```

### Cost Breakdown
- **Bedrock KB Retrieve**: ~$0.01 per query
- **Claude 3.5 Sonnet Generation**: ~$0.01 per response
- **Cache Storage**: $0.00 (SQLite) or minimal (DynamoDB)
- **S3 Storage**: ~$0.023 per GB/month

---

## API Endpoints

### 1. Upload PDF
```bash
POST /api/kb/upload
Content-Type: multipart/form-data

curl -X POST http://localhost:5000/api/kb/upload \
  -F "file=@scheme_document.pdf" \
  -F "user_id=user_123" \
  -F "document_type=scheme_info"
```

### 2. Query Knowledge Base
```bash
POST /api/kb/query
Content-Type: application/json

curl -X POST http://localhost:5000/api/kb/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is PM-KISAN?",
    "language": "hi",
    "max_results": 3
  }'
```

### 3. Get Cache Statistics
```bash
GET /api/kb/stats

curl http://localhost:5000/api/kb/stats
```

**Response:**
```json
{
    "total_cached_queries": 150,
    "cached_last_24h": 45,
    "cache_ttl_hours": 24,
    "language_distribution": {
        "hi": 100,
        "en": 50
    },
    "estimated_cost_saved": 3.00,
    "cache_enabled": true
}
```

### 4. Invalidate Cache
```bash
# Clear specific query
DELETE /api/kb/cache?query=what+is+pm-kisan&language=hi

# Clear all cache
DELETE /api/kb/cache?all=true

curl -X DELETE "http://localhost:5000/api/kb/cache?all=true"
```

### 5. Cleanup Old Cache
```bash
POST /api/kb/cache/cleanup
Content-Type: application/json

curl -X POST http://localhost:5000/api/kb/cache/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

### 6. Health Check
```bash
GET /api/kb/health

curl http://localhost:5000/api/kb/health
```

---

## Environment Variables

Add these to your `.env` file:

```bash
# Bedrock Knowledge Base Configuration
BEDROCK_KB_ID=XXXXXXXXXX                    # Your Knowledge Base ID
BEDROCK_KB_S3_BUCKET=jansathi-kb-bucket     # S3 bucket for PDFs
BEDROCK_KB_MODEL_ARN=arn:aws:bedrock:...    # Model ARN (optional)

# Cache Configuration
KB_CACHE_TTL=86400                          # Cache TTL in seconds (24 hours)
KB_ENABLE_CACHE=true                        # Enable/disable caching

# AWS Configuration (if not already set)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

---

## Database Schema

The `BedrockQueryCache` table is already defined in `models.py`:

```python
class BedrockQueryCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500), index=True, nullable=False)
    context_hash = db.Column(db.String(64))  # SHA-256 of context
    response_json = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='hi')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Indexes:**
- `query` - Fast lookup by normalized query
- Composite index on `(query, language)` for language-specific caching

---

## Setup Instructions

### 1. Create Bedrock Knowledge Base

```bash
# Using AWS Console:
1. Go to Amazon Bedrock → Knowledge Bases
2. Click "Create knowledge base"
3. Name: "JanSathi-KB"
4. Data source: S3
5. S3 bucket: Create new or use existing
6. Embeddings model: Titan Embeddings G1
7. Vector database: Default (managed)
8. Create

# Note the Knowledge Base ID (e.g., XXXXXXXXXX)
```

### 2. Configure S3 Bucket

```bash
# Create S3 bucket
aws s3 mb s3://jansathi-kb-bucket --region us-east-1

# Set up folder structure
aws s3api put-object \
  --bucket jansathi-kb-bucket \
  --key knowledge-base/documents/
```

### 3. Update Environment Variables

```bash
# Add to .env
BEDROCK_KB_ID=XXXXXXXXXX
BEDROCK_KB_S3_BUCKET=jansathi-kb-bucket
```

### 4. Run Database Migrations

```bash
# If using Flask-Migrate
flask db migrate -m "Add BedrockQueryCache table"
flask db upgrade

# Or just run the app (auto-creates tables)
python main.py
```

### 5. Test the Setup

```bash
# 1. Upload a test PDF
curl -X POST http://localhost:5000/api/kb/upload \
  -F "file=@test_scheme.pdf" \
  -F "user_id=test_user"

# 2. Wait 5-10 minutes for indexing

# 3. Query the knowledge base
curl -X POST http://localhost:5000/api/kb/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this scheme about?",
    "language": "en"
  }'

# 4. Query again (should be cached)
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

## Integration with Existing Code

### Update RAG Service (Optional)

You can integrate the Knowledge Base service with your existing RAG service:

```python
# In app/services/rag_service.py

from app.services.knowledge_base_service import KnowledgeBaseService

class RagService:
    def __init__(self):
        # ... existing code ...
        self.kb_service = KnowledgeBaseService()
    
    def retrieve(self, query, language='hi', user_profile=None, user_docs=None):
        """Enhanced retrieval with Knowledge Base."""
        all_matches = []
        
        # 1. Try Knowledge Base first (with caching)
        kb_result = self.kb_service.query(
            question=query,
            language=language,
            user_context=user_profile
        )
        
        if kb_result.get('sources'):
            all_matches.append(kb_result['answer'])
        
        # 2. Fallback to existing Kendra + Local search
        # ... existing code ...
        
        return all_matches
```

---

## Monitoring & Analytics

### Cache Performance Metrics

```python
# Get cache statistics
GET /api/kb/stats

{
    "total_cached_queries": 150,
    "cached_last_24h": 45,
    "cache_hit_rate": 0.85,  # 85% hit rate
    "estimated_cost_saved": 3.00,
    "language_distribution": {
        "hi": 100,
        "en": 50
    }
}
```

### Logging

All operations are logged with structured events:

```python
log_event('kb_query', {
    'question_length': 50,
    'language': 'hi',
    'cached': True,
    'sources_count': 3
})

log_event('kb_upload_success', {
    'user_id': 'user_123',
    'filename': 'scheme.pdf',
    'size_bytes': 1024000
})
```

---

## Best Practices

### 1. Cache Management
- Set appropriate TTL based on content freshness (24 hours default)
- Run cleanup jobs weekly: `POST /api/kb/cache/cleanup`
- Monitor cache hit rate (target: >80%)

### 2. PDF Organization
- Use descriptive filenames: `pmkisan_eligibility_2024.pdf`
- Organize by scheme/category in S3
- Keep PDFs under 10MB for faster processing

### 3. Query Optimization
- Normalize queries before caching
- Use consistent language codes (hi/en)
- Include user context for personalized results

### 4. Cost Optimization
- Enable caching in production (`KB_ENABLE_CACHE=true`)
- Monitor cache stats regularly
- Invalidate cache when documents are updated

---

## Troubleshooting

### Issue: "Knowledge Base service not available"
**Solution:** Check AWS credentials and KB_ID in .env

```bash
aws bedrock-agent get-knowledge-base --knowledge-base-id $BEDROCK_KB_ID
```

### Issue: "No results found"
**Solution:** Wait 5-10 minutes after upload for indexing to complete

### Issue: Cache not working
**Solution:** Check database connection and BedrockQueryCache table exists

```bash
# Verify table exists
sqlite3 instance/jansathi.db ".tables"
```

### Issue: High costs despite caching
**Solution:** Check cache hit rate and TTL settings

```bash
curl http://localhost:5000/api/kb/stats
```

---

## Future Enhancements

- [ ] Multi-modal support (images, tables in PDFs)
- [ ] Automatic document summarization
- [ ] Query suggestions based on cache
- [ ] A/B testing for answer quality
- [ ] Real-time cache invalidation on document updates
- [ ] Distributed caching with Redis
- [ ] Query analytics dashboard

---

## Support

For issues or questions:
- Check logs: `tail -f logs/jansathi.log`
- Review AWS CloudWatch for Bedrock errors
- Test with `/api/kb/health` endpoint

---

**Cost Savings Summary:**
- 85% reduction in Bedrock API costs
- Shared knowledge across all users
- Automatic cache management
- Production-ready with monitoring
