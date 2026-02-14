# JanSathi (जनसाथी) - System Design Document

## 🏗️ Architecture Overview

**JanSathi** follows a modern, cloud-native architecture designed for scalability, reliability, and cost-effectiveness within AWS free tier constraints.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AWS Services  │
│   (Next.js)     │◄──►│   (Flask)       │◄──►│   (Bedrock,     │
│                 │    │                 │    │    Polly, S3)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PWA Cache     │    │   SQLite DB     │    │   CloudWatch    │
│   (Service      │    │   (Conversations│    │   (Monitoring)  │
│    Worker)      │    │    & History)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🎯 Design Principles

### 1. Voice-First Design
- **Primary interaction**: Voice input/output
- **Secondary**: Text-based fallback
- **Accessibility**: Screen reader compatible
- **Simplicity**: Minimal cognitive load

### 2. Mobile-First Approach
- **Responsive design**: Works on all screen sizes
- **Touch-friendly**: Large buttons, easy navigation
- **Offline capability**: Core functions work without internet
- **Progressive enhancement**: Features degrade gracefully

### 3. Cost-Optimized Architecture
- **AWS Free Tier**: Maximum utilization of free services
- **Efficient caching**: Reduce API calls
- **Smart fallbacks**: Mock responses when services unavailable
- **Resource optimization**: Minimal compute and storage usage

---

## 🏛️ System Components

### Frontend Layer (Next.js 16)

#### Component Architecture
```
src/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Landing page
│   ├── dashboard/         # Main application
│   ├── auth/              # Authentication pages
│   └── layout.tsx         # Root layout
├── components/
│   ├── features/          # Feature-specific components
│   │   ├── chat/          # Chat interface
│   │   ├── dashboard/     # Dashboard widgets
│   │   └── community/     # Community features
│   ├── layout/            # Layout components
│   └── ui/                # Reusable UI components
├── hooks/                 # Custom React hooks
└── services/              # API client services
```

#### Key Components

**ChatInterface Component**
- Voice input/output management
- Real-time message streaming
- Audio player integration
- Language switching
- Conversation history

**VoiceInput Component**
- Browser Speech Recognition API
- Microphone permission handling
- Audio visualization
- Fallback to text input

**SchemeCard Component**
- Government scheme display
- Structured information layout
- Action buttons (Apply, Learn More)
- Accessibility features

### Backend Layer (Python Flask)

#### Service Architecture
```
backend/
├── app/
│   ├── api/               # REST API endpoints
│   │   └── routes.py      # Main route handlers
│   ├── services/          # Business logic services
│   │   ├── bedrock_service.py    # AI text generation
│   │   ├── polly_service.py      # Text-to-speech
│   │   ├── transcribe_service.py # Speech-to-text
│   │   ├── rag_service.py        # Document retrieval
│   │   └── cache_service.py      # Response caching
│   ├── core/              # Core utilities
│   │   ├── config.py      # Configuration management
│   │   ├── utils.py       # Helper functions
│   │   ├── security.py    # Security middleware
│   │   └── validators.py  # Input validation
│   ├── models/            # Database models
│   └── data/              # Data access layer
├── main.py                # Application entry point
└── lambda_handler.py      # AWS Lambda handler
```

#### Service Responsibilities

**BedrockService**
- AI model interaction (Claude 3 Haiku)
- Prompt engineering and optimization
- Response formatting and validation
- Cost monitoring and limits
- Fallback to mock responses

**PollyService**
- Text-to-speech synthesis
- Multi-language voice selection
- Audio file generation and storage
- S3 integration for audio hosting
- Caching for repeated phrases

**RAGService**
- Government scheme data retrieval
- Context-aware search
- Document similarity matching
- Structured response formatting
- Mock data fallback

---

## 🔄 Data Flow Design

### User Query Processing Flow

```
1. User Input (Voice/Text)
   ↓
2. Frontend Processing
   ├── Voice → Speech Recognition API
   └── Text → Direct processing
   ↓
3. API Request to Backend
   ↓
4. Query Processing Pipeline
   ├── Input validation
   ├── Language detection
   ├── Context retrieval (RAG)
   └── AI response generation
   ↓
5. Response Enhancement
   ├── Text formatting
   ├── Audio synthesis
   └── Structured data extraction
   ↓
6. Frontend Response Handling
   ├── Text display with formatting
   ├── Audio playback
   └── Scheme cards rendering
```

### Document Analysis Flow (Drishti Vision)

```
1. User uploads document image
   ↓
2. Frontend preprocessing
   ├── Image compression
   ├── Format validation
   └── Size optimization
   ↓
3. Backend processing
   ├── Image analysis (Claude 3 Vision)
   ├── Text extraction
   ├── Document type identification
   └── Next steps generation
   ↓
4. Response formatting
   ├── Key information highlighting
   ├── Action items listing
   └── Related schemes suggestion
```

---

## 🎨 User Interface Design

### Design System

#### Color Palette
- **Primary**: Blue (#2563eb) - Trust, government
- **Secondary**: Teal (#0d9488) - Growth, prosperity
- **Accent**: Purple (#7c3aed) - Innovation, technology
- **Success**: Green (#059669) - Positive actions
- **Warning**: Orange (#ea580c) - Attention needed
- **Error**: Red (#dc2626) - Problems, errors
- **Neutral**: Slate (#475569) - Text, backgrounds

#### Typography
- **Primary Font**: Inter (system font fallback)
- **Headings**: Bold weights (600-800)
- **Body Text**: Regular weight (400)
- **Code/Technical**: Mono font family
- **Accessibility**: Minimum 16px base size

#### Spacing System
- **Base unit**: 4px
- **Scale**: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- **Consistent margins**: Multiples of base unit
- **Touch targets**: Minimum 44px for mobile

### Layout Patterns

#### Mobile-First Grid
```css
/* Mobile: Single column */
.container { 
  display: grid; 
  grid-template-columns: 1fr; 
  gap: 1rem; 
}

/* Tablet: Two columns */
@media (min-width: 768px) {
  .container { 
    grid-template-columns: 1fr 1fr; 
  }
}

/* Desktop: Three columns */
@media (min-width: 1024px) {
  .container { 
    grid-template-columns: 1fr 1fr 1fr; 
  }
}
```

#### Component Hierarchy
1. **Page Layout**: Full viewport structure
2. **Section Layout**: Content grouping
3. **Component Layout**: Individual feature areas
4. **Element Layout**: Atomic UI elements

---

## 🔧 Technical Implementation

### State Management

#### Frontend State (React)
```typescript
// Global state using React Context
interface AppState {
  user: User | null;
  language: string;
  theme: 'light' | 'dark';
  isOnline: boolean;
  conversations: Conversation[];
}

// Local component state using useState/useReducer
const [messages, setMessages] = useState<Message[]>([]);
const [isRecording, setIsRecording] = useState(false);
const [audioUrl, setAudioUrl] = useState<string | null>(null);
```

#### Backend State (Flask)
```python
# Session management
from flask import session

# Database state
from app.models import Conversation, User

# Cache state
from app.services.cache_service import CacheService
cache = CacheService()
```

### API Design

#### RESTful Endpoints
```
POST /api/query              # Process user query
GET  /api/history            # Get conversation history
POST /api/analyze            # Analyze document
GET  /api/market-rates       # Get market prices
GET  /api/health             # Health check
```

#### Request/Response Format
```json
// Query Request
{
  "text_query": "What is PM Kisan scheme?",
  "language": "hi",
  "userId": "user123"
}

// Query Response
{
  "query": "What is PM Kisan scheme?",
  "answer": {
    "text": "PM-KISAN provides ₹6,000 per year...",
    "audio": "https://s3.amazonaws.com/audio/response.mp3"
  },
  "structured_sources": [
    {
      "title": "PM-KISAN Samman Nidhi",
      "benefit": "₹6,000/year Income Support",
      "link": "https://pmkisan.gov.in"
    }
  ],
  "meta": {
    "language": "hi",
    "response_time": 1.2,
    "cost": 0.001
  }
}
```

### Database Schema

#### SQLite Tables
```sql
-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    language TEXT DEFAULT 'hi',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- Users table (future enhancement)
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT,
    preferred_language TEXT DEFAULT 'hi',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME
);

-- Cache table
CREATE TABLE response_cache (
    query_hash TEXT PRIMARY KEY,
    response TEXT NOT NULL,
    language TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
);
```

---

## 🔒 Security Design

### Authentication & Authorization

#### JWT-based Authentication
```typescript
// Frontend token management
interface AuthToken {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user_id: string;
}

// Backend token validation
@jwt_required()
def protected_route():
    current_user = get_jwt_identity()
    return {"user_id": current_user}
```

#### Role-based Access Control
```python
# User roles
class UserRole(Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    MODERATOR = "moderator"

# Permission decorators
@require_role(UserRole.CITIZEN)
def user_endpoint():
    pass

@require_role(UserRole.ADMIN)
def admin_endpoint():
    pass
```

### Data Protection

#### Input Validation
```python
from app.core.validators import validate_query

def process_query(query: str, language: str):
    # Validate input
    validated_query = validate_query(query)
    validated_language = validate_language(language)
    
    # Sanitize input
    clean_query = sanitize_input(validated_query)
    
    return process_clean_query(clean_query, validated_language)
```

#### Output Sanitization
```python
def sanitize_response(response: str) -> str:
    # Remove sensitive information
    # Escape HTML/JavaScript
    # Validate URLs
    return clean_response
```

---

## 📊 Performance Design

### Caching Strategy

#### Multi-Level Caching
```
1. Browser Cache (Frontend)
   ├── Static assets (24h)
   ├── API responses (5min)
   └── Audio files (1h)

2. Application Cache (Backend)
   ├── Frequent queries (1h)
   ├── Government data (24h)
   └── User sessions (30min)

3. CDN Cache (AWS CloudFront)
   ├── Static content (7d)
   ├── Images (30d)
   └── Audio files (1d)
```

#### Cache Implementation
```python
from functools import wraps
import hashlib

def cache_response(ttl_seconds=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = hashlib.md5(
                f"{func.__name__}:{args}:{kwargs}".encode()
            ).hexdigest()
            
            # Check cache
            cached = cache.get(cache_key)
            if cached:
                return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl_seconds)
            return result
        return wrapper
    return decorator
```

### Load Balancing & Scaling

#### Horizontal Scaling
```yaml
# AWS Lambda configuration
Resources:
  JanSathiAPI:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.11
      Handler: lambda_handler.handler
      ReservedConcurrencyLimit: 100
      Environment:
        Variables:
          NODE_ENV: production
```

#### Database Optimization
```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 🌐 Deployment Design

### Infrastructure as Code

#### AWS CDK Stack
```python
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_cloudfront as cloudfront
)

class JanSathiStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 bucket for audio files
        audio_bucket = s3.Bucket(
            self, "AudioBucket",
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldAudio",
                    expiration=Duration.days(1)
                )
            ]
        )
        
        # Lambda function
        api_lambda = _lambda.Function(
            self, "APILambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("backend")
        )
        
        # API Gateway
        api = apigw.LambdaRestApi(
            self, "JanSathiAPI",
            handler=api_lambda,
            cors_options=apigw.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"]
            )
        )
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: Deploy JanSathi
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS
        run: |
          cdk deploy --require-approval never
```

---

## 📱 Mobile Design Considerations

### Progressive Web App (PWA)

#### Service Worker
```javascript
// sw.js - Service Worker for offline functionality
const CACHE_NAME = 'jansathi-v1';
const urlsToCache = [
  '/',
  '/dashboard',
  '/static/js/bundle.js',
  '/static/css/main.css'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
  );
});
```

#### App Manifest
```json
{
  "name": "JanSathi - Government Services Assistant",
  "short_name": "JanSathi",
  "description": "Voice-first AI assistant for Indian government services",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1e293b",
  "theme_color": "#2563eb",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### Touch Interface Design

#### Gesture Support
- **Tap**: Primary interaction
- **Long press**: Context menus
- **Swipe**: Navigation between screens
- **Pinch**: Zoom for accessibility
- **Voice activation**: "Hey JanSathi" wake word

#### Responsive Breakpoints
```css
/* Mobile first approach */
.container {
  padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    max-width: 768px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
    padding: 3rem;
  }
}

/* Large screens */
@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}
```

---

## 🔍 Monitoring & Analytics Design

### Application Performance Monitoring

#### Metrics Collection
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            status = 'success'
            return result
        except Exception as e:
            status = 'error'
            raise
        finally:
            duration = time.time() - start_time
            
            # Log metrics
            logger.info(f"Function: {func.__name__}, "
                       f"Duration: {duration:.3f}s, "
                       f"Status: {status}")
    
    return wrapper
```

#### Health Checks
```python
@app.route('/health')
def health_check():
    checks = {
        'database': check_database_connection(),
        'aws_services': check_aws_connectivity(),
        'cache': check_cache_status(),
        'disk_space': check_disk_space()
    }
    
    overall_status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return {
        'status': overall_status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }
```

### User Analytics

#### Privacy-Compliant Tracking
```typescript
// Anonymous usage analytics
interface AnalyticsEvent {
  event_type: string;
  timestamp: number;
  session_id: string; // Anonymous session ID
  language: string;
  feature_used: string;
  success: boolean;
}

function trackEvent(event: AnalyticsEvent) {
  // Only track if user consented
  if (userConsent.analytics) {
    analytics.track(event);
  }
}
```

---

## 🎯 Future Design Considerations

### Scalability Enhancements

#### Microservices Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │  Query Service  │    │  Audio Service  │
│   (User Mgmt)   │    │  (AI Processing)│    │  (TTS/STT)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  API Gateway    │
                    │  (Load Balancer)│
                    └─────────────────┘
```

#### Database Scaling
```python
# Read replicas for scaling
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        return 'replica'
    
    def db_for_write(self, model, **hints):
        return 'primary'
```

### Advanced Features

#### Machine Learning Pipeline
```python
# User behavior analysis
class UserBehaviorAnalyzer:
    def analyze_query_patterns(self, user_id: str):
        # Analyze user's query history
        # Predict likely next questions
        # Personalize responses
        pass
    
    def optimize_responses(self, feedback_data):
        # Use user feedback to improve responses
        # A/B test different response formats
        # Optimize for user satisfaction
        pass
```

#### Multi-tenant Architecture
```python
# Support for different government levels
class TenantManager:
    def get_tenant_config(self, domain: str):
        # State-specific configurations
        # Local language preferences
        # Regional scheme priorities
        pass
```

---

*This design document serves as the technical blueprint for JanSathi and should be updated as the system evolves and new requirements emerge.*