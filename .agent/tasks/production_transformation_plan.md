# JanSathi Production Transformation Plan
**Status**: Draft for Review  
**Priority**: Critical  
**Estimated Duration**: 4-6 weeks (phased approach)  
**Budget**: AWS Free Tier + $50-200/month scaling budget

---

## 📊 CURRENT STATE ANALYSIS

### ✅ What We Have (MVP Baseline)
| Component | Status | Quality |
|-----------|--------|---------|
| **Backend Framework** | Flask with Bedrock integration | ⚠️ Basic |
| **Frontend** | Next.js 16 with chat interface | ⚠️ Basic |
| **AI Services** | Bedrock (Claude), Transcribe, Polly | ✅ Working |
| **RAG Implementation** | Basic Kendra integration | ⚠️ Mock mode |
| **Database** | DynamoDB + SQLAlchemy | ✅ Configured |
| **Authentication** | Clerk (demo mode) | ⚠️ Not production-ready |
| **Storage** | S3 for audio files | ✅ Working |
| **Voice Pipeline** | Transcribe service exists | ⚠️ Partial |
| **Monitoring** | Basic logging | ❌ Insufficient |
| **Infrastructure** | Manual deployment | ❌ No IaC |
| **Security** | Basic WAF/CORS | ⚠️ Needs hardening |
| **Cost Optimization** | None | ❌ Not implemented |

### ❌ Critical Gaps (vs Production Architecture)
1. **No Infrastructure as Code** (CDK/Terraform)
2. **No CI/CD Pipeline** (manual deployments)
3. **No Observability Stack** (X-Ray, structured logging, metrics)
4. **No Caching Layer** (CloudFront, DAX, API response caching)
5. **No Auto-Scaling** configuration
6. **No Multi-Region** setup
7. **No Proper Secret Management** (Secrets Manager)
8. **No Rate Limiting** (API Gateway throttling)
9. **No Cost Alarms** or budget controls
10. **No Production RAG** (Kendra in mock mode)
11. **No WhatsApp/IVR Integration**
12. **No Offline Support** (PWA)
13. **No Security Hardening** (WAF rules, GuardDuty)
14. **No Disaster Recovery** plan
15. **No Performance Testing** (load testing)

---

## 🎯 TRANSFORMATION STRATEGY

### Phased Approach (MVP → Production)

**Phase 1: Foundation** (Week 1-2) - **PRIORITY: CRITICAL**
- Infrastructure as Code (AWS CDK)
- Proper secret management
- Basic observability
- Security hardening

**Phase 2: Scale & Optimize** (Week 3-4) - **PRIORITY: HIGH**
- Caching & CDN
- Auto-scaling
- Cost optimization
- Performance tuning

**Phase 3: Advanced Features** (Week 5-6) - **PRIORITY: MEDIUM**
- Multi-modal integration (WhatsApp, IVR)
- Offline-first PWA
- Advanced AI features

**Phase 4: Production Readiness** (Ongoing) - **PRIORITY: HIGH**
- Load testing
- Security audit
- Documentation
- Runbooks

---

## 📋 DETAILED IMPLEMENTATION TASKS

## PHASE 1: FOUNDATION (CRITICAL PATH)

### Task 1.1: Infrastructure as Code (AWS CDK)
**Duration**: 3-4 days  
**Complexity**: High  
**Dependencies**: None

**Objectives**:
- Set up AWS CDK project (TypeScript)
- Define all infrastructure as code
- Enable versioned deployments
- Multi-environment support (dev/staging/prod)

**Deliverables**:
```
infrastructure/
├── bin/app.ts                  # CDK app entry point
├── lib/
│   ├── api-stack.ts           # API Gateway + Lambda
│   ├── ai-stack.ts            # Bedrock, Kendra, Transcribe, Polly
│   ├── data-stack.ts          # DynamoDB, S3, DAX (optional)
│   ├── frontend-stack.ts      # CloudFront, S3 hosting
│   ├── observability-stack.ts # CloudWatch, X-Ray, alarms
│   ├── security-stack.ts      # WAF, Secrets Manager, IAM
│   └── pipeline-stack.ts      # CI/CD pipeline
├── cdk.json
└── package.json
```

**Acceptance Criteria**:
- [ ] `cdk deploy --all` provisions entire infrastructure
- [ ] Multi-environment configuration (dev/prod)
- [ ] All resources properly tagged for cost tracking
- [ ] IAM roles follow least privilege
- [ ] Destroy/recreate works without data loss (using S3/DynamoDB backups)

**Implementation Notes**:
- Use CDK constructs for common patterns (API + Lambda, S3 + CloudFront)
- Parameterize all config (region, bucket names, etc.)
- Enable CDK context for environment-specific values

---

### Task 1.2: Secrets Management (Secrets Manager)
**Duration**: 1 day  
**Complexity**: Medium  
**Dependencies**: Task 1.1 (CDK setup)

**Objectives**:
- Migrate all secrets from `.env` to AWS Secrets Manager
- Enable automatic rotation
- Update Lambda to retrieve secrets dynamically

**Secrets to Migrate**:
```json
{
  "AWS_ACCESS_KEY_ID": "...",
  "AWS_SECRET_ACCESS_KEY": "...",
  "BEDROCK_MODEL_ID": "...",
  "DATABASE_URL": "...",
  "CLERK_SECRET_KEY": "...",
  "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "..."
}
```

**Deliverables**:
- CDK stack for Secrets Manager
- Lambda environment variables reference secret ARNs
- Automatic rotation policy (30 days)
- No hardcoded secrets in codebase

**Acceptance Criteria**:
- [ ] All secrets stored in Secrets Manager
- [ ] Lambda retrieves secrets via boto3
- [ ] KMS customer-managed key for encryption
- [ ] Audit trail via CloudTrail

---

### Task 1.3: Observability Stack (CloudWatch + X-Ray)
**Duration**: 2-3 days  
**Complexity**: High  
**Dependencies**: Task 1.1

**Objectives**:
- Implement structured logging
- Enable X-Ray distributed tracing
- Create CloudWatch dashboards
- Set up alarms for critical metrics

**Components**:

#### A. Structured Logging
```python
# backend/app/utils/logging.py
import structlog
import json

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

# Usage
logger = structlog.get_logger()
logger.info(
    "bedrock_query",
    user_id="user123",
    query="PM Kisan scheme",
    latency_ms=450,
    tokens=1200
)
```

#### B. X-Ray Instrumentation
```python
# backend/app/api/routes.py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_recorder.configure(service='JanSathi-API')
XRayMiddleware(app, xray_recorder)

@xray_recorder.capture('query_bedrock')
def query_bedrock(prompt):
    xray_recorder.put_annotation('model', 'claude-3-5-haiku')
    # ... bedrock call
```

#### C. CloudWatch Dashboards
- **API Metrics**: Request count, latency (P50, P95, P99), error rate
- **AI Metrics**: Bedrock tokens used, cache hit ratio, response time
- **Cost Metrics**: Daily spend by service
- **User Metrics**: Active users, queries per user

#### D. Alarms
| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | >1% | SNS → Email alert |
| P95 Latency | >2000ms | Auto-scale Lambda |
| Daily Cost | >$10 | SNS → Email alert |
| Bedrock Throttles | >10/min | Switch to fallback model |

**Deliverables**:
- Structured logging across all services
- X-Ray traces for all API calls
- CloudWatch dashboard (single pane of glass)
- 5-10 critical alarms configured

**Acceptance Criteria**:
- [ ] 100% of requests have X-Ray traces
- [ ] All logs in JSON format
- [ ] Dashboard loads in <2 seconds
- [ ] Alarms tested (manually trigger conditions)

---

### Task 1.4: Security Hardening
**Duration**: 2 days  
**Complexity**: Medium  
**Dependencies**: Task 1.1

**Objectives**:
- Implement WAF rules
- Enable GuardDuty
- Harden IAM policies
- Enable encryption at rest & in transit

**Sub-tasks**:

#### A. WAF Rules (API Gateway)
```typescript
// infrastructure/lib/security-stack.ts
const wafRules = [
  // Rate limiting
  {
    name: 'RateLimitRule',
    priority: 1,
    statement: {
      rateBasedStatement: {
        limit: 100, // 100 req/5min per IP
        aggregateKeyType: 'IP'
      }
    },
    action: { block: {} }
  },
  // SQL injection
  {
    name: 'SQLiRule',
    priority: 2,
    statement: {
      sqliMatchStatement: {
        fieldToMatch: { body: {} },
        textTransformations: [{ priority: 0, type: 'URL_DECODE' }]
      }
    },
    action: { block: {} }
  },
  // XSS
  {
    name: 'XSSRule',
    priority: 3,
    statement: {
      xssMatchStatement: {
        fieldToMatch: { body: {} },
        textTransformations: [{ priority: 0, type: 'HTML_ENTITY_DECODE' }]
      }
    },
    action: { block: {} }
  }
];
```

#### B. GuardDuty
```typescript
new guardduty.CfnDetector(this, 'GuardDuty', {
  enable: true,
  findingPublishingFrequency: 'FIFTEEN_MINUTES'
});
```

#### C. IAM Hardening
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel"
    ],
    "Resource": [
      "arn:aws:bedrock:*::model/anthropic.claude-3-5-haiku*"
    ],
    "Condition": {
      "StringEquals": {
        "aws:RequestedRegion": "us-east-1"
      }
    }
  }]
}
```

**Deliverables**:
- WAF WebACL attached to API Gateway
- GuardDuty enabled in all regions
- IAM policies audited (no wildcards)
- Encryption enabled (S3, DynamoDB, Secrets Manager)

**Acceptance Criteria**:
- [ ] WAF blocks malicious requests (test with OWASP payloads)
- [ ] GuardDuty findings routed to SNS
- [ ] All IAM roles have <10 permissions
- [ ] 100% of data encrypted at rest

---

### Task 1.5: Update Backend Dependencies
**Duration**: 1 day  
**Complexity**: Low  
**Dependencies**: None

**Objectives**:
- Add missing production dependencies
- Version lock all packages
- Add security scanning

**New requirements.txt**:
```
# Core
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0

# AWS
boto3==1.34.0
botocore==1.34.0
aws-xray-sdk==2.12.0

# Database
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.0

# Security
flask-talisman==1.1.0
flask-limiter==3.5.0
cryptography==42.0.0

# Logging
structlog==24.1.0
python-json-logger==2.0.7

# AI/ML
# (Bedrock via boto3)

# Utilities
requests==2.31.0
pydantic==2.5.0
```

**Deliverables**:
- Updated `requirements.txt`
- `requirements-dev.txt` (pytest, black, mypy)
- Dependency vulnerability scan (pip-audit)

**Acceptance Criteria**:
- [ ] No known vulnerabilities (pip-audit passes)
- [ ] All versions locked
- [ ] Docker build succeeds

---

## PHASE 2: SCALE & OPTIMIZE

### Task 2.1: Caching Layer (CloudFront + DAX)
**Duration**: 2-3 days  
**Complexity**: Medium  
**Dependencies**: Task 1.1

**Objectives**:
- Deploy CloudFront for static assets
- Implement API Gateway caching
- Add DAX for DynamoDB (optional, $$$)
- Cache Bedrock responses

**Components**:

#### A. CloudFront Distribution
```typescript
const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: new origins.S3Origin(frontendBucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED
  },
  additionalBehaviors: {
    '/api/*': {
      origin: new origins.HttpOrigin(apiDomain),
      cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED, // API not cached at CDN
      originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER
    }
  },
  priceClass: cloudfront.PriceClass.PRICE_CLASS_100, // US, EU, India
  enableLogging: true,
  logBucket: logsBucket
});
```

#### B. API Gateway Caching
```typescript
const api = new apigateway.RestApi(this, 'API', {
  deployOptions: {
    cachingEnabled: true,
    cacheClusterSize: '0.5', // Smallest (Free Tier may not cover)
    cacheTtl: cdk.Duration.minutes(5),
    cacheDataEncrypted: true
  }
});
```

#### C. Bedrock Response Caching (Application Level)
```python
# backend/app/services/cache_service.py
import hashlib
import json
from datetime import datetime, timedelta

class BedrockCache:
    def __init__(self, dynamodb_table):
        self.table = dynamodb_table
        self.ttl_seconds = 3600  # 1 hour
    
    def get(self, query: str, language: str):
        cache_key = self._hash_key(query, language)
        response = self.table.get_item(Key={'cache_key': cache_key})
        
        if 'Item' in response:
            if datetime.now().timestamp() < response['Item']['ttl']:
                return response['Item']['response']
        return None
    
    def set(self, query: str, language: str, response: str):
        cache_key = self._hash_key(query, language)
        ttl = int((datetime.now() + timedelta(seconds=self.ttl_seconds)).timestamp())
        
        self.table.put_item(Item={
            'cache_key': cache_key,
            'query': query,
            'language': language,
            'response': response,
            'ttl': ttl
        })
    
    def _hash_key(self, query, language):
        return hashlib.sha256(f"{query}:{language}".encode()).hexdigest()
```

**Deliverables**:
- CloudFront distribution for frontend
- API Gateway cache (if budget allows)
- DynamoDB table for Bedrock response cache
- Cache hit ratio dashboard

**Acceptance Criteria**:
- [ ] >80% cache hit ratio for static assets
- [ ] >50% cache hit ratio for common queries
- [ ] P95 latency reduced by 40%

---

### Task 2.2: Auto-Scaling Configuration
**Duration**: 1-2 days  
**Complexity**: Medium  
**Dependencies**: Task 1.1, Task 1.3 (monitoring)

**Objectives**:
- Configure Lambda reserved/provisioned concurrency
- Set up DynamoDB auto-scaling
- Implement API Gateway throttling

**Components**:

#### A. Lambda Auto-Scaling
```typescript
const queryFunction = new lambda.Function(this, 'QueryHandler', {
  // ... existing config
  reservedConcurrentExecutions: 100, // Max limit
  
  // Provisioned concurrency (eliminates cold starts)
  currentVersionOptions: {
    provisionedConcurrentExecutions: 2, // Warm instances
    maxEventAge: cdk.Duration.hours(1),
    retryAttempts: 2
  }
});

// Auto-scaling for provisioned concurrency
const target = new applicationautoscaling.ScalableTarget(this, 'ScalableTarget', {
  serviceNamespace: applicationautoscaling.ServiceNamespace.LAMBDA,
  scalableDimension: 'lambda:function:ProvisionedConcurrentExecutions',
  resourceId: `function:${queryFunction.functionName}:${version.version}`,
  minCapacity: 2,
  maxCapacity: 10
});

target.scaleOnSchedule('ScaleUpMorning', {
  schedule: applicationautoscaling.Schedule.cron({ hour: '6', minute: '0' }),
  minCapacity: 5
});
```

#### B. DynamoDB Auto-Scaling
```typescript
const table = new dynamodb.Table(this, 'ChatHistory', {
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // On-demand (or...)
  
  // Or provisioned with auto-scaling
  // billingMode: dynamodb.BillingMode.PROVISIONED,
  // readCapacity: 5,
  // writeCapacity: 5
});

// Auto-scaling (if provisioned)
table.autoScaleReadCapacity({ minCapacity: 5, maxCapacity: 100 })
  .scaleOnUtilization({ targetUtilizationPercent: 70 });
```

**Deliverables**:
- Lambda concurrency limits configured
- DynamoDB auto-scaling policies
- API Gateway throttling (100 req/sec burst, 50 steady)

**Acceptance Criteria**:
- [ ] No Lambda throttling errors under 10K RPM load
- [ ] DynamoDB scales up/down based on traffic
- [ ] API Gateway throttles abusive clients

---

### Task 2.3: Cost Optimization
**Duration**: 2 days  
**Complexity**: Medium  
**Dependencies**: Task 1.3 (monitoring)

**Objectives**:
- Implement cost tracking & tagging
- Set up AWS Budgets
- Optimize Lambda memory allocation
- Implement S3 lifecycle policies

**Sub-tasks**:

#### A. Cost Allocation Tags
```typescript
// Apply to all resources
cdk.Tags.of(this).add('Project', 'JanSathi');
cdk.Tags.of(this).add('Environment', 'Production');
cdk.Tags.of(this).add('CostCenter', 'AI-Services');
```

#### B. AWS Budgets
```typescript
new budgets.CfnBudget(this, 'MonthlyBudget', {
  budget: {
    budgetName: 'JanSathi-Monthly',
    budgetLimit: {
      amount: 100, // $100/month
      unit: 'USD'
    },
    budgetType: 'COST',
    timeUnit: 'MONTHLY'
  },
  notificationsWithSubscribers: [{
    notification: {
      notificationType: 'ACTUAL',
      comparisonOperator: 'GREATER_THAN',
      threshold: 80, // Alert at 80%
      thresholdType: 'PERCENTAGE'
    },
    subscribers: [{
      subscriptionType: 'EMAIL',
      address: 'alerts@example.com'
    }]
  }]
});
```

#### C. Lambda Right-Sizing
```python
# Test different memory configurations
# Current: 1024MB → Optimize to 512MB (if CPU not bottleneck)

# Use AWS Lambda Power Tuning Tool
# https://github.com/alexcasalboni/aws-lambda-power-tuning
```

#### D. S3 Lifecycle Policies
```typescript
bucket.addLifecycleRule({
  id: 'ArchiveOldAudio',
  enabled: true,
  transitions: [
    {
      storageClass: s3.StorageClass.INTELLIGENT_TIERING,
      transitionAfter: cdk.Duration.days(7)
    },
    {
      storageClass: s3.StorageClass.GLACIER,
      transitionAfter: cdk.Duration.days(30)
    }
  ],
  expiration: cdk.Duration.days(90)
});
```

**Deliverables**:
- Cost dashboard in CloudWatch
- Budget alarm configured
- Lambda memory optimized (25-40% cost reduction)
- S3 lifecycle policies (80% storage cost reduction)

**Acceptance Criteria**:
- [ ] All resources tagged
- [ ] Cost per user calculated ($0.002/user target)
- [ ] Budget alarm triggers at $80 spend
- [ ] S3 auto-archives old files

---

## PHASE 3: ADVANCED FEATURES

### Task 3.1: Production RAG (Kendra Integration)
**Duration**: 3-4 days  
**Complexity**: High  
**Dependencies**: Task 1.1

**Objectives**:
- Deploy Kendra Enterprise Edition (Free Tier: 750 hours)
- Ingest government scheme documents
- Implement hybrid retrieval (Kendra + Bedrock)
- Set up daily sync from government portals

**Components**:

#### A. Kendra Index Creation
```typescript
const kendraIndex = new kendra.CfnIndex(this, 'SchemeIndex', {
  name: 'JanSathi-Schemes',
  edition: 'ENTERPRISE_EDITION', // or DEVELOPER_EDITION (cheaper)
  roleArn: kendraRole.roleArn,
  documentMetadataConfigurations: [
    {
      name: 'scheme_name',
      type: 'STRING_VALUE',
      search: { displayable: true, facetable: true, searchable: true }
    },
    {
      name: 'ministry',
      type: 'STRING_VALUE',
      search: { facetable: true }
    },
    {
      name: 'last_updated',
      type: 'DATE_VALUE',
      relevance: { freshness: true, importance: 5 }
    }
  ]
});
```

#### B. Data Source (S3 Connector)
```typescript
new kendra.CfnDataSource(this, 'S3DataSource', {
  indexId: kendraIndex.attrId,
  name: 'Government-Schemes-PDF',
  type: 'S3',
  dataSourceConfiguration: {
    s3Configuration: {
      bucketName: documentsBucket.bucketName,
      inclusionPrefixes: ['schemes/']
    }
  },
  roleArn: kendraRole.roleArn,
  schedule: 'cron(0 2 * * ? *)', // Daily at 2 AM
  description: 'Government scheme PDFs'
});
```

#### C. RAG Pipeline Integration
```python
# backend/app/services/rag_service.py (update existing)
import boto3

class KendraRAGService:
    def __init__(self):
        self.kendra = boto3.client('kendra')
        self.index_id = os.getenv('KENDRA_INDEX_ID')
    
    def retrieve_context(self, query: str, top_k: int = 5):
        """Query Kendra for relevant documents"""
        response = self.kendra.query(
            IndexId=self.index_id,
            QueryText=query,
            AttributeFilter={
                'EqualsTo': {
                    'Key': 'language',
                    'Value': {'StringValue': 'hindi'}
                }
            },
            PageSize=top_k
        )
        
        contexts = []
        for item in response['ResultItems']:
            if item['Type'] == 'DOCUMENT':
                contexts.append({
                    'text': item['DocumentExcerpt']['Text'],
                    'title': item['DocumentTitle']['Text'],
                    'uri': item['DocumentURI'],
                    'score': item['ScoreAttributes']['ScoreConfidence']
                })
        
        return contexts
    
    def format_context_for_bedrock(self, contexts):
        """Format Kendra results for Bedrock prompt"""
        formatted = []
        for ctx in contexts:
            formatted.append(
                f"[Source: {ctx['title']}]\n"
                f"{ctx['text']}\n"
                f"URL: {ctx['uri']}\n"
            )
        return "\n\n".join(formatted)
```

**Deliverables**:
- Kendra index with 1000+ government scheme documents
- Daily sync from myscheme.gov.in (RSS feed)
- RAG pipeline integrated with Bedrock
- Accuracy >90% (vs mock responses)

**Acceptance Criteria**:
- [ ] Kendra returns relevant docs for 90% of queries
- [ ] Bedrock responses cite Kendra sources
- [ ] Hallucination rate <5% (down from 43%)
- [ ] Daily sync completes in <1 hour

---

### Task 3.2: WhatsApp Bot Integration
**Duration**: 2-3 days  
**Complexity**: Medium  
**Dependencies**: Task 1.1

**Objectives**:
- Integrate Twilio WhatsApp API
- Support voice notes (audio upload)
- Support image upload (Aadhaar/document OCR)
- Handle asynchronous responses

**Architecture**:
```
WhatsApp User → Twilio → API Gateway Webhook → Lambda → Bedrock → Polly → Twilio → User
```

**Components**:

#### A. Webhook Handler
```python
# backend/app/api/whatsapp_webhook.py
from flask import request
from twilio.twiml.messaging_response import MessagingResponse

@app.route('/webhooks/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', None)
    
    # Process query
    if media_url:
        # Image OCR via Textract
        response_text = process_image(media_url)
    else:
        # Text query
        response_text = query_bedrock(incoming_msg)
    
    # Generate audio response
    audio_url = generate_polly_audio(response_text)
    
    # Send via Twilio
    resp = MessagingResponse()
    resp.message(response_text).media(audio_url)
    
    return str(resp)
```

**Deliverables**:
- WhatsApp webhook endpoint
- Support for text, voice notes, images
- Async processing (long-running queries)

**Acceptance Criteria**:
- [ ] WhatsApp bot responds in <5 seconds (95% of queries)
- [ ] Voice notes transcribed correctly (>85% accuracy)
- [ ] Images processed via Textract OCR

---

### Task 3.3: Offline-First PWA
**Duration**: 2-3 days  
**Complexity**: Medium  
**Dependencies**: Task 2.1 (CloudFront)

**Objectives**:
- Convert frontend to PWA
- Cache top 100 schemes offline
- Service worker for offline detection
- Background sync when online

**Components**:

#### A. Service Worker
```javascript
// frontend/public/sw.js
const CACHE_NAME = 'jansathi-v1';
const OFFLINE_SCHEMES = '/api/schemes/popular?limit=100';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        '/',
        '/offline',
        '/manifest.json',
        OFFLINE_SCHEMES
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).catch(() => {
        // Offline fallback
        return caches.match('/offline');
      });
    })
  );
});
```

#### B. Offline Detection UI
```tsx
// frontend/src/components/OfflineNotice.tsx
'use client';

import { useEffect, useState } from 'react';

export default function OfflineNotice() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-black p-2 text-center z-50">
      ⚠️ You're offline. Showing cached results only.
    </div>
  );
}
```

**Deliverables**:
- PWA manifest
- Service worker with caching strategy
- Offline UI notice
- Background sync when reconnected

**Acceptance Criteria**:
- [ ] App works offline for 100 most common queries
- [ ] Lighthouse PWA score >90
- [ ] Install prompt appears on mobile

---

## PHASE 4: PRODUCTION READINESS

### Task 4.1: CI/CD Pipeline (GitHub Actions + CDK)
**Duration**: 2-3 days  
**Complexity**: High  
**Dependencies**: Task 1.1

**Objectives**:
- Automated testing (unit, integration, e2e)
- Blue-green deployments
- Canary releases with automatic rollback
- Multi-environment promotion (dev → staging → prod)

**Pipeline**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Backend tests
      - name: Run Python tests
        run: |
          cd backend
          pip install -r requirements-dev.txt
          pytest --cov=app --cov-report=xml
          
      # Frontend tests
      - name: Run Next.js tests
        run: |
          cd frontend
          npm install
          npm run test
          npm run build
      
      # Security scan
      - name: Security scan
        run: |
          pip install pip-audit
          pip-audit
          npm audit

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ap-south-1
      
      - name: CDK Deploy (Staging)
        run: |
          cd infrastructure
          npm install
          npx cdk deploy --all --context env=staging --require-approval never

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://jansathi.ai
    steps:
      # ... similar to staging but with manual approval
      
      - name: CDK Deploy (Production - Canary)
        run: |
          npx cdk deploy --all --context env=prod --context deploymentType=canary
```

**Deliverables**:
- GitHub Actions workflow
- Separate environments (dev/staging/prod)
- Automated rollback on errors
- Deployment notifications (Slack)

**Acceptance Criteria**:
- [ ] PR builds run tests automatically
- [ ] Main branch deploys to prod after approval
- [ ] Failed deployments auto-rollback
- [ ] Deployment time <10 minutes

---

### Task 4.2: Load Testing (Locust)
**Duration**: 2 days  
**Complexity**: Medium  
**Dependencies**: Task 2.2 (auto-scaling)

**Objectives**:
- Simulate 10K concurrent users
- Identify bottlenecks
- Validate auto-scaling
- Measure P95/P99 latency under load

**Load Test Script**:
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class JanSathiUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def query_scheme(self):
        self.client.post("/api/query", json={
            "text_query": "PM Kisan Samman Nidhi eligibility",
            "language": "hi",
            "userId": "load-test-user"
        })
    
    @task(1)
    def upload_voice(self):
        with open("test_audio.wav", "rb") as f:
            self.client.post("/api/voice", files={"audio": f})
    
    @task(1)
    def get_history(self):
        self.client.get("/api/history")
```

**Run Test**:
```bash
locust -f tests/load/locustfile.py --host=https://api.jansathi.ai --users=10000 --spawn-rate=100
```

**Deliverables**:
- Locust test suite
- Performance report (HTML)
- Bottleneck analysis
- Capacity planning recommendations

**Acceptance Criteria**:
- [ ] System handles 10K concurrent users
- [ ] P95 latency <2 seconds at peak load
- [ ] No 5xx errors
- [ ] Auto-scaling triggers correctly

---

### Task 4.3: Security Audit & Penetration Testing
**Duration**: 3-4 days  
**Complexity**: High  
**Dependencies**: Task 1.4 (security hardening)

**Objectives**:
- OWASP Top 10 vulnerability scan
- Penetration testing (simulated attacks)
- Compliance check (GDPR, data residency)
- Security documentation

**Sub-tasks**:

#### A. OWASP ZAP Scan
```bash
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://api.jansathi.ai \
  -r security-report.html
```

#### B. Penetration Testing Scenarios
1. **Prompt Injection**: Try to bypass RAG context
2. **SQL Injection**: Test DynamoDB query sanitization
3. **XSS**: Inject scripts in chat messages
4. **CSRF**: Test API protection
5. **Rate Limit Bypass**: Attempt to overwhelm API

#### C. Compliance Documentation
- Data flow diagram (where PII flows)
- Encryption audit (all data at rest/in transit)
- Access control matrix (who can access what)
- Incident response plan

**Deliverables**:
- Security audit report
- Penetration test findings (with fixes)
- Compliance documentation
- Security runbook

**Acceptance Criteria**:
- [ ] Zero critical vulnerabilities
- [ ] All OWASP Top 10 mitigated
- [ ] Penetration test passed
- [ ] Incident response plan tested

---

### Task 4.4: Documentation & Runbooks
**Duration**: 2-3 days  
**Complexity**: Low  
**Dependencies**: All tasks

**Objectives**:
- Complete README
- API documentation (OpenAPI)
- Architecture diagrams
- Operational runbooks

**Deliverables**:

#### A. README.md
```markdown
# JanSathi - AI-Powered Government Services Platform

## Quick Start
```bash
# Deploy infrastructure
cd infrastructure
cdk deploy --all

# Run locally
docker-compose up
```

## Architecture
[Link to AWS_PRODUCTION_ARCHITECTURE.md]

## API Documentation
[Link to Swagger UI]

## Monitoring
- CloudWatch Dashboard: [URL]
- X-Ray Service Map: [URL]
```

#### B. OpenAPI Spec
```yaml
# docs/api-spec.yaml
openapi: 3.0.0
info:
  title: JanSathi API
  version: 1.0.0
paths:
  /api/query:
    post:
      summary: Query government schemes
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                text_query:
                  type: string
                language:
                  type: string
                  enum: [hi, en, kn, ta]
```

#### C. Runbooks
```markdown
# docs/runbooks/high-latency.md

## Incident: High API Latency (P95 > 2s)

### Detection
CloudWatch Alarm: `JanSathi-HighLatency`

### Diagnosis
1. Check X-Ray service map: Which component is slow?
2. Check Bedrock throttles: Are we being rate-limited?
3. Check DynamoDB metrics: Hot partition?

### Remediation
- If Bedrock throttling: Switch to fallback model
- If DynamoDB: Enable auto-scaling or add DAX
- If Lambda cold starts: Increase provisioned concurrency
```

**Acceptance Criteria**:
- [ ] README has complete setup instructions
- [ ] API fully documented (Swagger UI)
- [ ] 5+ runbooks (incidents, deployments, backups)
- [ ] Architecture diagrams up-to-date

---

## 🚀 DEPLOYMENT CHECKLIST

### Pre-Production (Staging)
- [ ] All Phase 1 tasks complete (foundation)
- [ ] All Phase 2 tasks complete (scale & optimize)
- [ ] Load testing passed (10K users)
- [ ] Security audit passed
- [ ] Monitoring/alerting tested
- [ ] Runbooks validated
- [ ] Disaster recovery tested (restore from backup)

### Production Launch
- [ ] DNS configured (jansathi.ai → CloudFront)
- [ ] SSL certificate installed (ACM)
- [ ] Multi-region failover tested
- [ ] Cost alarms configured
- [ ] On-call rotation established
- [ ] Marketing assets ready (demo video, screenshots)

### Post-Launch (Week 1)
- [ ] Monitor error rates (target: <0.1%)
- [ ] Monitor costs (target: <$0.002/user)
- [ ] User feedback collection
- [ ] Performance optimization (based on real traffic)

---

## 📊 SUCCESS METRICS (6-Month Goals)

| Metric | Baseline (MVP) | Target (Production) | Measurement |
|--------|----------------|---------------------|-------------|
| **Users** | 1K | 100K MAU | CloudWatch RUM |
| **Latency (P95)** | 3-5s | <2s | X-Ray |
| **Uptime** | 95% | 99.9% | CloudWatch Synthetics |
| **Cost/User** | Unknown | <$0.002 | Cost Explorer |
| **Accuracy** | ~70% | >90% | Manual audits |
| **Cache Hit** | 0% | >80% | CloudFront metrics |

---

## 💰 BUDGET ESTIMATE

### Phase 1 (Foundation)
- **Dev Time**: 40 hours × $0 (self) = $0
- **AWS Costs**: ~$50/month (Secrets Manager, X-Ray traces, CloudWatch Logs)

### Phase 2 (Scale & Optimize)
- **Dev Time**: 30 hours
- **AWS Costs**: ~$100/month (CloudFront, API Gateway cache, Kendra)

### Phase 3 (Advanced Features)
- **Dev Time**: 40 hours
- **AWS Costs**: ~$150/month (Kendra data sources, Twilio WhatsApp)

### Phase 4 (Production Readiness)
- **Dev Time**: 30 hours
- **AWS Costs**: ~$50/month (load testing, security tools)

**Total**: 140 hours dev time, $50-200/month AWS (scales with usage)

---

## 🎯 NEXT STEPS (Immediate Actions)

1. **Review This Plan** (30 min)
   - Approve scope
   - Prioritize tasks
   - Assign owners

2. **Set Up CDK Project** (2 hours) - **START HERE**
   - Initialize infrastructure/ folder
   - Create first stack (api-stack.ts)
   - Deploy to dev account

3. **Migrate Secrets** (1 hour)
   - Create Secrets Manager secrets
   - Update Lambda to fetch from Secrets Manager
   - Remove .env files

4. **Enable X-Ray** (30 min)
   - Add X-Ray middleware to Flask
   - Deploy and verify traces

5. **Set Up Monitoring** (1 hour)
   - Create CloudWatch dashboard
   - Configure 3-5 critical alarms
   - Test alarm notifications

**Week 1 Goal**: Complete Task 1.1 (CDK) + Task 1.2 (Secrets) + Task 1.3 (Observability)

---

## ❓ QUESTIONS FOR REVIEW

1. **Budget**: Is $50-200/month acceptable? (Free Tier covers most, but Kendra costs extra)
2. **Timeline**: Is 4-6 weeks realistic for your availability?
3. **Scope**: Should we skip any Phase 3 features (WhatsApp, PWA) for faster MVP?
4. **Regions**: Start with single region (Mumbai) or multi-region from day 1?
5. **Kendra**: Use Enterprise Edition ($$) or Developer Edition (cheaper but limited)?

---

**Status**: ✅ Ready for Review  
**Last Updated**: 2026-02-14  
**Next Review**: After user approval
