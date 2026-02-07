# JanSathi AWS Cost Calculator ($100 Free Credits)

## Service Costs (Per Usage)

### 1. AWS Bedrock (Text Generation)
- **Titan Text G1**: $0.0008 per 1K tokens
- **Claude 3 Haiku**: $0.00025 per 1K tokens ⭐ CHEAPEST
- **Average query**: ~200 tokens = $0.00005 per query

### 2. AWS Polly (Text-to-Speech)
- **FREE TIER**: 5 million characters/month for 12 months
- **After free tier**: $4.00 per 1M characters
- **Your usage**: ~500K chars/month = FREE ✅

### 3. AWS Transcribe (Speech-to-Text)
- **FREE TIER**: 60 minutes/month for 12 months
- **After free tier**: $0.024 per minute
- **Your usage**: ~10 minutes/month = FREE ✅

### 4. AWS S3 (Audio Storage)
- **FREE TIER**: 5GB storage for 12 months
- **After free tier**: $0.023 per GB
- **Your usage**: ~1GB = FREE ✅

### 5. AWS Lambda (API Gateway)
- **FREE TIER**: 1M requests/month (ALWAYS FREE)
- **Your usage**: ~10K requests/month = FREE ✅

## Monthly Cost Estimate

### Demo Usage (Hackathon)
- **Queries**: 1,000 queries × $0.00005 = $0.05
- **Polly**: FREE (under 5M chars)
- **Transcribe**: FREE (under 60 min)
- **S3**: FREE (under 5GB)
- **Lambda**: FREE (under 1M requests)
- **TOTAL**: $0.05/month ✅

### Heavy Usage (Production)
- **Queries**: 10,000 queries × $0.00005 = $0.50
- **Polly**: FREE (still under limit)
- **Transcribe**: FREE (still under limit)
- **S3**: FREE (still under limit)
- **Lambda**: FREE (still under limit)
- **TOTAL**: $0.50/month ✅

### Maximum Safe Usage (Stay under $5/month)
- **Queries**: 100,000 queries × $0.00005 = $5.00
- **This equals**: ~3,300 queries per day
- **Buffer for other services**: $95 remaining

## Cost Monitoring Commands

```powershell
# Check current costs
aws ce get-cost-and-usage --time-period Start=2026-02-01,End=2026-02-08 --granularity DAILY --metrics BlendedCost

# Set up budget alert
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget file://budget.json
```

## Safety Measures

1. **Daily Limit**: Max 1,000 queries/day = $0.05/day
2. **Monthly Limit**: Max $5/month = 100,000 queries
3. **Auto-stop**: If costs exceed $10, switch to mock mode
4. **Free tier monitoring**: Track Polly/Transcribe usage

## Recommendations

1. **Use Titan Text** for 80% of queries (cheapest)
2. **Use Claude Haiku** for complex queries only
3. **Cache common responses** to reduce API calls
4. **Use browser Speech API** instead of Transcribe when possible
5. **Auto-delete S3 files** after 24 hours (lifecycle policy)

## Emergency Cost Control

If costs approach $50:
1. Switch `BEDROCK_MODEL_ID=mock` in .env
2. Use cached responses only
3. Disable audio generation temporarily
4. Review CloudWatch logs for excessive usage

Your $100 credits should last 20+ months with normal usage!