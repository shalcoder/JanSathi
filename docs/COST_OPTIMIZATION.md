# 💰 JanSathi Cost Optimization Guide

## Goal: Stay Under $5/month During Hackathon Demo

---

## 📊 Cost Breakdown by Service

### 1. AWS Bedrock (Highest Cost)

**Claude 3 Haiku Pricing:**
- Input: $0.25 per 1M tokens (~750K words)
- Output: $1.25 per 1M tokens

**Claude 3 Sonnet Pricing (Vision):**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Optimization Strategies:**

✅ **Use Haiku for Text Queries**
```python
# In backend/app/core/config.py
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"  # ← Cheapest
```

✅ **Limit Response Length**
```python
# In bedrock_service.py
"max_tokens": 400  # ← Keep this low (currently set)
```

✅ **Reduce Context Size**
```python
# In rag_service.py - retrieve() method
return final_results[:3]  # ← Limit to 3 docs instead of 5
```

✅ **Cache Common Queries**
```python
# Add simple in-memory cache
QUERY_CACHE = {}

def generate_response(self, query, context, language):
    cache_key = f"{query}_{language}"
    if cache_key in QUERY_CACHE:
        return QUERY_CACHE[cache_key]
    
    # ... existing code ...
    QUERY_CACHE[cache_key] = response
    return response
```

**Cost Estimate:**
- 100 queries/day × 30 days = 3,000 queries
- Average: 200 input tokens + 300 output tokens per query
- Cost: (3000 × 200 × $0.25/1M) + (3000 × 300 × $1.25/1M) = **$1.27/month**

---

### 2. AWS Polly (FREE in First Year)

**Free Tier:**
- 5 million characters/month for 12 months
- Neural voices included

**Optimization Strategies:**

✅ **Only Generate Audio When Requested**
```python
# In routes.py
response_mode = request.json.get('response_mode', 'text')  # Default to text-only
if response_mode == 'voice':
    audio_url = polly_service.synthesize(answer_text, language)
```

✅ **Limit Audio Length**
```python
# In polly_service.py
def synthesize(self, text: str, language: str = "hi"):
    # Truncate long responses
    if len(text) > 1000:
        text = text[:1000] + "..."
```

**Cost Estimate:**
- FREE (under 5M chars/month)
- After free tier: ~$0.50/month for typical usage

---

### 3. AWS Transcribe (FREE in First Year)

**Free Tier:**
- 60 minutes/month for 12 months

**Optimization Strategies:**

✅ **Use Browser Speech API First**
```javascript
// In VoiceInput.tsx - Already implemented!
// Browser does transcription locally (FREE)
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
```

✅ **Only Use AWS Transcribe for Fallback**
```python
# Only use Transcribe when browser API unavailable
# Current implementation already uses browser API
```

✅ **Limit Audio Duration**
```python
# In transcribe_service.py
MAX_AUDIO_DURATION = 30  # seconds
```

**Cost Estimate:**
- FREE (browser handles most transcription)
- AWS Transcribe: 0-10 minutes/month = **$0.00**

---

### 4. AWS S3 (FREE in First Year)

**Free Tier:**
- 5 GB storage
- 20,000 GET requests
- 2,000 PUT requests

**Optimization Strategies:**

✅ **Auto-Delete Old Files (Already Implemented)**
```json
// lifecycle.json - Files deleted after 1 day
{
  "Expiration": { "Days": 1 }
}
```

✅ **Use Presigned URLs (Already Implemented)**
```python
# In polly_service.py
url = self.s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": self.bucket_name, "Key": key},
    ExpiresIn=3600  # 1 hour
)
```

**Cost Estimate:**
- FREE (under 5GB, auto-cleanup enabled)

---

### 5. AWS Lambda (Always FREE)

**Free Tier (Permanent):**
- 1 million requests/month
- 400,000 GB-seconds compute time

**Optimization Strategies:**

✅ **Use Minimal Memory**
```bash
# Lambda configuration
--memory-size 512  # MB (minimum for our use case)
--timeout 60       # seconds
```

✅ **Cold Start Optimization**
```python
# In lambda_handler.py - Already implemented
# Services initialized at module level (reused across invocations)
bedrock_service = BedrockService()
rag_service = RagService()
```

**Cost Estimate:**
- FREE (under 1M requests/month)

---

## 🚫 Services We're NOT Using (To Save Money)

### ❌ AWS Kendra
**Why:** Costs $810/month minimum (Developer Edition)  
**Alternative:** Mock RAG with structured data (already implemented)

### ❌ AWS DynamoDB
**Why:** Costs add up with high read/write  
**Alternative:** SQLite for local dev, PostgreSQL for production

### ❌ AWS CloudFront
**Why:** Not needed for hackathon demo  
**Alternative:** Direct S3 presigned URLs

---

## 📈 Real-Time Cost Monitoring

### Daily Check Script
```powershell
# Run this daily during development
.\scripts\check_aws_costs.ps1
```

### Manual Check
```bash
# Get current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-02-01,End=2024-02-07 \
  --granularity DAILY \
  --metrics "UnblendedCost"
```

### Set Up Alerts
1. **Budget Alert at $8** (80% of $10 budget)
2. **Budget Alert at $10** (100% of budget)
3. **Anomaly Detection** (AWS Cost Anomaly Detection)

---

## 🎯 Hackathon Demo Strategy

### Pre-Demo Preparation (Save Costs)

1. **Test with Mock Data First**
   ```python
   # In bedrock_service.py
   self.working = False  # Force mock mode for testing
   ```

2. **Cache Demo Responses**
   ```python
   # Pre-generate responses for demo queries
   DEMO_QUERIES = {
       "What is PM Kisan?": "cached_response_1.txt",
       "Ayushman Bharat eligibility": "cached_response_2.txt"
   }
   ```

3. **Use Pre-Recorded Audio**
   ```python
   # Store demo audio files locally instead of generating
   DEMO_AUDIO = {
       "query1": "static/audio/demo1.mp3"
   }
   ```

### During Demo (Minimize Costs)

1. **Limit Live Queries**
   - Use 3-5 pre-tested queries
   - Show cached responses for repeated questions

2. **Disable Audio for Most Demos**
   - Only enable for 1-2 "wow" moments
   - Use text responses primarily

3. **Use Browser Speech API**
   - Avoid AWS Transcribe during demo
   - Browser API is free and instant

---

## 💡 Cost-Saving Code Snippets

### 1. Query Caching
```python
# Add to bedrock_service.py
import hashlib
import json
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_response_cached(self, query_hash, context_hash, language):
    # Actual API call here
    pass

def generate_response(self, query, context, language):
    query_hash = hashlib.md5(query.encode()).hexdigest()
    context_hash = hashlib.md5(context.encode()).hexdigest()
    return self.generate_response_cached(query_hash, context_hash, language)
```

### 2. Rate Limiting
```python
# Add to routes.py
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["100 per day", "10 per minute"]
)

@bp.route('/query', methods=['POST'])
@limiter.limit("50 per day")  # Limit expensive queries
def query():
    # ... existing code ...
```

### 3. Token Counting
```python
# Add to bedrock_service.py
def count_tokens(text):
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4

def generate_response(self, query, context, language):
    input_tokens = count_tokens(query + context)
    print(f"💰 Estimated cost: ${input_tokens * 0.25 / 1_000_000:.6f}")
    # ... existing code ...
```

---

## 📊 Expected Monthly Costs (Hackathon Usage)

| Service | Usage | Cost |
|---------|-------|------|
| Bedrock (Haiku) | 3,000 queries | $1.27 |
| Bedrock (Sonnet) | 100 image analyses | $0.90 |
| Polly | 500K characters | FREE |
| Transcribe | 10 minutes | FREE |
| S3 | 1 GB storage | FREE |
| Lambda | 10K requests | FREE |
| **TOTAL** | | **$2.17/month** |

### With Heavy Usage (5,000 queries/month):
- Bedrock: $3.50
- Other services: FREE
- **Total: $3.50/month**

---

## 🚨 Emergency Cost Controls

### If Costs Spike Above $10:

1. **Immediate Actions:**
   ```bash
   # Disable Bedrock temporarily
   export BEDROCK_MODEL_ID="mock"
   
   # Stop all services
   aws lambda update-function-configuration \
     --function-name JanSathiAPI \
     --environment Variables={BEDROCK_MODEL_ID=mock}
   ```

2. **Check for Issues:**
   ```bash
   # Look for infinite loops or excessive calls
   aws logs tail /aws/lambda/JanSathiAPI --follow
   ```

3. **Delete Expensive Resources:**
   ```bash
   # Delete S3 bucket if needed
   aws s3 rb s3://your-bucket-name --force
   ```

---

## ✅ Cost Optimization Checklist

- [ ] Using Claude Haiku (not Sonnet) for text queries
- [ ] max_tokens set to 400 or less
- [ ] Browser Speech API enabled (not AWS Transcribe)
- [ ] S3 lifecycle policy active (1-day deletion)
- [ ] Query caching implemented
- [ ] Rate limiting enabled
- [ ] Budget alerts set ($8 and $10)
- [ ] Daily cost monitoring script scheduled
- [ ] Demo queries pre-tested and cached
- [ ] Kendra disabled (using mock RAG)

---

## 📞 Cost Support

**If you need help:**
1. Check AWS Cost Explorer daily
2. Review CloudWatch logs for unusual patterns
3. Contact AWS Support (included with account)
4. Use AWS Cost Anomaly Detection

**Emergency Contact:**
- AWS Support: https://console.aws.amazon.com/support/

---

**Remember:** The goal is to showcase your AI capabilities, not to spend money. Use mock data for testing, real AWS for the final demo! 🎯
