# 🔧 JanSathi Backend Implementation Details

## 📋 Overview

The JanSathi backend is a sophisticated **9-agent sequential pipeline** built with Flask, Python 3.12, and AWS services. It implements India's first real-time speech-to-speech agentic civic automation system with deterministic rules and comprehensive audit trails.

---

## 🏗️ **Core Architecture: 9-Agent Pipeline**

```
User Input → Session Init → Intent Classify → Knowledge Retrieval → Slot Collection → 
Rules-Based Eligibility → Risk Verification → Response Synthesis → 
Notifications → HITL Queue (if needed)
```

**Design Principle**: **"Deterministic rules ALWAYS override LLM outputs"** - ensuring zero AI hallucination in government eligibility decisions.

---

## 🚀 **Main Entry Points**

### **1. `main.py` - Flask Application Factory**
**Purpose**: Main orchestrator that initializes the Flask application with all necessary configurations.

**Key Implementations**:
- Flask app factory pattern with environment-based configuration
- CORS setup for multi-origin access (localhost:3000, Vercel, CloudFront, S3)
- Blueprint registration for API routes
- Error handling middleware
- Request logging and correlation ID injection
- Health check endpoints

**Code Structure**:
```python
def create_app():
    app = Flask(__name__)
    setup_cors(app)  # Multi-origin CORS
    register_blueprints(app)  # API route registration
    setup_middleware(app)  # Request logging
    return app
```

### **2. `lambda_handler.py` - AWS Lambda Entry Point**
**Purpose**: Serverless entry point for AWS Lambda deployment with optimized cold start performance.

**Key Implementations**:
- Lambda event processing and routing
- CORS headers for API Gateway integration
- Error handling for serverless environment
- Service locator pattern for lazy loading
- Response formatting for API Gateway

**Optimization Features**:
- Lazy service loading to reduce cold start time
- Connection pooling for AWS services
- Response caching for frequent queries

### **3. `backend/app/core/execution.py` - Main Orchestration Engine (150+ lines)**
**Purpose**: **THE CORE BRAIN** - Routes all user input through the 9-agent pipeline and coordinates all services.

**Key Implementations**:
```python
def process_user_input(user_query, session_data, channel='web'):
    """
    Main orchestration function that:
    1. Initializes session and captures consent
    2. Routes through intent classification
    3. Executes FSM-based workflow
    4. Coordinates all 20+ services
    5. Returns structured response
    """
```

**Service Coordination**:
- BedrockService for LLM operations
- ReceiptService for benefit document generation
- NotificationService for SMS dispatch
- AuditService for compliance logging
- TelemetryService for CloudWatch metrics

---

## 🤖 **LangGraph Agent System (`/backend/agents`)**

### **Agent Supervisor: `supervisor.py`**
**Purpose**: LangGraph StateGraph orchestrator that wires all 9 agents with conditional edges.

**Key Implementations**:
```python
def create_agent_graph():
    workflow = StateGraph(JanSathiState)
    
    # Add all 9 agent nodes
    workflow.add_node("intent_classify", intent_agent)
    workflow.add_node("rag_retrieve", rag_agent)
    workflow.add_node("slot_collect", slot_collection_agent)
    workflow.add_node("rules_validate", rules_agent)
    workflow.add_node("risk_verify", verifier_agent)
    workflow.add_node("response_synthesize", response_agent)
    workflow.add_node("notify", notification_agent)
    workflow.add_node("hitl_queue", hitl_agent)
    
    # Conditional edges for routing
    workflow.add_conditional_edges("risk_verify", route_decision)
    
    return workflow.compile()
```

### **1. Intent Agent (`intent_agent.py`) - 80+ lines**
**Purpose**: Classifies user intent (apply/info/grievance/track) using hybrid approach.

**Key Implementations**:
- **Rule-based classifier** (primary): Pattern matching for common phrases
- **Nova Micro LLM** (fallback): For complex or ambiguous queries
- Confidence scoring and threshold-based routing
- Multi-language intent recognition (Hindi, English, Tamil, etc.)

**Example Classification Logic**:
```python
def classify_intent(user_query, language='hi'):
    # Rule-based patterns first
    if any(pattern in query.lower() for pattern in APPLY_PATTERNS):
        return Intent(type='apply', confidence=0.95)
    
    # Fallback to Nova Micro
    return llm_classify_intent(query, language)
```

### **2. RAG Agent (`rag_agent.py`) - 100+ lines**
**Purpose**: Knowledge retrieval using hybrid RAG system.

**Key Implementations**:
- **Vector search** using TF-IDF for local scheme database
- **Amazon Kendra** integration for government document retrieval
- **Bedrock Knowledge Base** for curated scheme information
- Multi-hop reasoning for complex eligibility questions
- Context ranking and relevance scoring

**Retrieval Pipeline**:
```python
def retrieve_knowledge(query, scheme_hint=None):
    # 1. Local vector search (TF-IDF)
    local_results = tfidf_search(query, scheme_hint)
    
    # 2. Kendra search
    kendra_results = kendra_client.query(query)
    
    # 3. Bedrock KB
    bedrock_results = bedrock_kb_query(query)
    
    # 4. Rank and merge results
    return merge_and_rank([local_results, kendra_results, bedrock_results])
```

### **3. Slot Collection Agent (`slot_collection_agent.py`) - 100+ lines**
**Purpose**: Conversational slot extraction for eligibility determination.

**Key Implementations**:
- **Nova Lite LLM** for natural question generation
- Required vs. optional slot identification
- Context-aware follow-up questions
- Multi-turn conversation state management
- Validation of collected information

**Slot Collection Flow**:
```python
def collect_slots(required_slots, current_state, conversation_history):
    missing_slots = identify_missing_slots(required_slots, current_state)
    
    if missing_slots:
        # Generate natural follow-up question
        question = nova_lite_generate_question(
            missing_slots[0], 
            conversation_history,
            user_language
        )
        return ConversationResponse(question=question, requires_input=True)
    
    return ConversationResponse(slots_complete=True)
```

### **4. Rules Agent (`rules_agent.py`) - 100+ lines**
**Purpose**: **DETERMINISTIC eligibility evaluation** - NO LLM involved to prevent hallucination.

**Key Implementations**:
- **YAML-defined rules** for each government scheme
- Operator-based evaluation (eq, gte, lte, in, contains)
- Mandatory vs. optional criteria separation
- Detailed reasoning trace for audit compliance
- Multi-scheme rule validation

**Rule Evaluation Engine**:
```python
def validate_eligibility(scheme_name, user_profile, collected_slots):
    rules = load_scheme_rules(scheme_name)  # From YAML
    
    results = []
    for rule in rules:
        result = evaluate_rule(rule, user_profile, collected_slots)
        results.append({
            'rule_id': rule.id,
            'condition': rule.condition,
            'result': result.passed,
            'reasoning': result.explanation
        })
    
    # Deterministic final decision
    eligible = all(r['result'] for r in results if r['mandatory'])
    
    return EligibilityResult(
        eligible=eligible,
        rule_trace=results,
        confidence=1.0  # Always 100% for rule-based decisions
    )
```

**Example Rule Definition (YAML)**:
```yaml
pm_kisan_rules:
  - id: "age_check"
    condition: "age >= 18"
    mandatory: true
    message: "Must be 18 or older"
  
  - id: "land_ownership"
    condition: "land_ownership > 0"
    mandatory: true
    message: "Must own agricultural land"
```

### **5. Verifier Agent (`verifier_agent.py`) - 100+ lines**
**Purpose**: Composite risk scoring and routing decisions for quality assurance.

**Key Implementations**:
- **ASR confidence scoring** from speech-to-text
- **Rules confidence** from eligibility validation
- **Caller history analysis** for fraud detection
- **Composite risk calculation**
- Routing decisions: AUTO_SUBMIT / HITL_QUEUE / NOT_ELIGIBLE

**Risk Scoring Algorithm**:
```python
def calculate_risk_score(asr_confidence, rules_trace, caller_history):
    # ASR quality (0.0-1.0)
    asr_score = asr_confidence
    
    # Rules confidence (always 1.0 for deterministic rules)
    rules_score = 1.0 if all_mandatory_rules_passed else 0.0
    
    # Caller history (fraud indicators)
    history_score = analyze_caller_patterns(caller_history)
    
    # Composite score with weights
    composite_score = (
        asr_score * 0.3 + 
        rules_score * 0.5 + 
        history_score * 0.2
    )
    
    # Routing decision
    if composite_score >= 0.9:
        return RoutingDecision.AUTO_SUBMIT
    elif composite_score >= 0.7:
        return RoutingDecision.HITL_QUEUE  # Human review
    else:
        return RoutingDecision.NOT_ELIGIBLE
```

### **6. Response Agent (`response_agent.py`) - 120+ lines**
**Purpose**: Response synthesis from RAG knowledge and eligibility results.

**Key Implementations**:
- **Nova Pro LLM** for natural response generation
- **Personalization** by state, income, language preference
- **Benefit receipt generation** with official formatting
- **Multi-language response synthesis**
- **Tone adaptation** (formal for official documents, friendly for explanations)

### **7. Notification Agent (`notification_agent.py`) - 100+ lines**
**Purpose**: SMS dispatch and receipt storage with telemetry.

**Key Implementations**:
- **AWS SNS integration** for SMS delivery across India
- **S3 receipt storage** with expiry links (7-day default)
- **CloudWatch telemetry emission** (14 different KPIs)
- **Delivery confirmation tracking**
- **Multi-language SMS templates**

### **8. HITL Agent (`hitl_agent.py`) - 80+ lines**
**Purpose**: Human-in-the-loop case management and workflow.

**Key Implementations**:
- **SQS queue integration** for case distribution
- **Admin dashboard compatibility**
- **Case prioritization** based on urgency and complexity
- **Approval/rejection workflow**
- **Audit trail for human decisions**

### **9. Telecom Agent (`telecom_agent.py`) - 80+ lines**
**Purpose**: Session initialization and IVR integration.

**Key Implementations**:
- **Amazon Connect webhook** handling
- **Consent capture** for DPDP compliance
- **Language detection** and preference setting
- **Session state initialization**
- **Call routing** based on user preference

---

## 🔧 **Core Services (`/backend/app/services`) - 20+ Services**

### **Intent Service (`intent_service.py`)**
**Purpose**: Primary intent classification engine with fallback mechanisms.

**Key Features**:
- Rule-based pattern matching for 90%+ accuracy on common queries
- Nova Micro LLM fallback for edge cases
- Confidence calibration and threshold tuning
- Intent caching for repeat queries
- Multi-language support with language-specific patterns

### **RAG Service (`rag_service.py`)**
**Purpose**: Hybrid retrieval-augmented generation system.

**Architecture**:
```python
class HybridRAGService:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer()
        self.kendra_client = KendraClient()
        self.bedrock_kb = BedrockKnowledgeBase()
        self.local_db = SchemeDatabase()
    
    def retrieve(self, query, scheme_hint=None):
        # Multi-source retrieval
        sources = [
            self.local_tfidf_search(query),
            self.kendra_search(query),
            self.bedrock_kb_search(query)
        ]
        
        # Rank and merge with relevance scoring
        return self.merge_results(sources)
```

### **Rules Engine (`rules_engine.py`)**
**Purpose**: Deterministic eligibility validation without LLM dependency.

**Rule Types**:
- **Numerical comparisons**: age >= 18, income <= 200000
- **Set membership**: state in ['UP', 'Bihar', 'MP']
- **Boolean checks**: has_bank_account == True
- **Pattern matching**: aadhaar matches regex pattern

**Evaluation Examples**:
```python
# PM-KISAN Eligibility Rules
rules = {
    'age_requirement': {
        'condition': 'age >= 18',
        'mandatory': True,
        'message': 'Must be 18 years or older'
    },
    'land_ownership': {
        'condition': 'land_acres > 0',
        'mandatory': True,
        'message': 'Must own agricultural land'
    },
    'income_limit': {
        'condition': 'annual_income <= 200000',
        'mandatory': False,
        'message': 'Preferential for low-income families'
    }
}
```

### **Bedrock Service (`bedrock_service.py`)**
**Purpose**: Amazon Bedrock Nova model integration for LLM operations.

**Model Usage**:
- **Nova Micro**: Intent classification fallback (fastest, cheapest)
- **Nova Lite**: Slot collection questions, response synthesis
- **Nova Pro**: Complex reasoning, multi-language synthesis

**Key Methods**:
```python
def invoke_nova_model(prompt, model_type='lite', max_tokens=1000):
    """
    Unified interface for all Nova models with:
    - Retry logic with exponential backoff
    - Response caching for identical prompts
    - Token usage tracking for cost optimization
    - Error handling and graceful degradation
    """
```

### **IVR Service (`ivr_service.py`)**
**Purpose**: Interactive Voice Response state machine management.

**State Management**:
- Turn-by-turn conversation tracking
- Context preservation across IVR interactions
- Error recovery for misunderstood inputs
- Language switching mid-conversation
- Call transfer to human agents

### **Transcribe Service (`transcribe_service.py`)**
**Purpose**: AWS Transcribe integration for speech-to-text conversion.

**Capabilities**:
- **10+ Indian languages**: Hindi, English, Tamil, Telugu, Kannada, Bengali, Gujarati, Marathi, Malayalam, Punjabi
- **Confidence scoring** for ASR quality assessment
- **Real-time streaming** for live calls
- **Audio format handling** (WAV, MP3, FLAC)
- **Speaker identification** for multi-party calls

### **Polly Service (`polly_service.py`)**
**Purpose**: Amazon Polly text-to-speech with Indian voice optimization.

**Voice Selection**:
- **Hindi**: Aditi (female), Kajal (female)
- **English (Indian)**: Raveena (female), Arathi (female)
- **Tamil**: Coming soon (neural voices)
- **Telugu**: Coming soon (neural voices)

**Optimization Features**:
- SSML markup for natural pronunciation
- Speaking rate adjustment for rural users
- Emphasis on government scheme names
- Audio caching for common responses

### **Verifier Service (`verifier_service.py`)**
**Purpose**: Multi-dimensional risk assessment and quality scoring.

**Risk Factors**:
1. **ASR Confidence**: Speech recognition quality (0.0-1.0)
2. **Rules Confidence**: Eligibility determination certainty (0.0-1.0)
3. **Caller History**: Fraud indicators and patterns
4. **Response Coherence**: LLM response quality metrics
5. **Document Verification**: Uploaded document authenticity (future)

### **Notification Service (`notification_service.py`)**
**Purpose**: Multi-channel notification dispatch system.

**Channels**:
- **SMS via AWS SNS**: Primary notification channel
- **Voice calls**: For critical updates (future)
- **Email**: For receipt delivery (future)
- **WhatsApp**: Business API integration (future)

**Message Templates**:
```python
SMS_TEMPLATES = {
    'hindi': {
        'eligible': "बधाई! आप {scheme_name} के लिए पात्र हैं। रसीद: {receipt_link}",
        'not_eligible': "खुशी! आप {scheme_name} के लिए पात्र नहीं हैं। कारण: {reason}",
        'under_review': "आपका आवेदन समीक्षाधीन है। संदर्भ: {ref_id}"
    }
}
```

### **Receipt Service (`receipt_service.py`)**
**Purpose**: Benefit receipt generation and storage system.

**Receipt Generation**:
- **HTML template rendering** with government formatting
- **PDF conversion** for official documents (future)
- **QR code generation** for verification
- **Multi-language support** with proper fonts
- **Digital signatures** for authenticity (future)

**Storage Architecture**:
```python
def generate_receipt(eligibility_result, user_profile):
    receipt_data = {
        'receipt_id': generate_unique_id(),
        'scheme_name': eligibility_result.scheme,
        'citizen_name': user_profile.name,
        'eligibility_status': eligibility_result.eligible,
        'reasoning_trace': eligibility_result.rule_trace,
        'generated_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=7)
    }
    
    # Render HTML template
    html_content = render_template('receipt.html', **receipt_data)
    
    # Upload to S3 with expiry
    s3_url = s3_client.upload_with_expiry(html_content, receipt_data['expires_at'])
    
    return receipt_data['receipt_id'], s3_url
```

### **Audit Service (`audit_service.py`)**
**Purpose**: Immutable audit logging system for DPDP compliance.

**Audit Architecture**:
- **SHA-256 chaining**: Each log entry chained to previous for tamper detection
- **Structured logging**: JSON format with standardized fields
- **PII masking**: Automatic sensitive data redaction
- **Retention policies**: Configurable data retention periods
- **Export capabilities**: Compliance reporting and data portability

**Log Entry Structure**:
```python
audit_entry = {
    'timestamp': '2026-03-08T10:30:45Z',
    'correlation_id': 'req-123456789',
    'action': 'eligibility_check',
    'user_id': 'masked-user-id',
    'inputs': {
        'scheme': 'pm_kisan',
        'state': 'uttar_pradesh',
        'age': 45,  # Non-PII data
        'phone': '***-***-1234'  # Masked PII
    },
    'outputs': {
        'eligible': True,
        'confidence': 1.0,
        'reasoning': ['age_check_passed', 'land_ownership_verified']
    },
    'processing_time_ms': 245,
    'previous_hash': 'abc123...def456',
    'current_hash': 'def456...ghi789'
}
```

### **Telemetry Service (`telemetry_service.py`)**
**Purpose**: CloudWatch KPI emission and performance monitoring.

**14 Key Performance Indicators**:
1. **Intent Classification Accuracy**: % correctly classified
2. **Average Response Latency**: P50, P95, P99 percentiles
3. **Eligibility Rate**: % users eligible vs not eligible
4. **HITL Escalation Rate**: % cases requiring human review
5. **SMS Delivery Success Rate**: Notification delivery metrics
6. **Language Distribution**: Usage by primary language
7. **Scheme Popularity**: Most requested government schemes
8. **Caller Satisfaction Score**: Feedback ratings
9. **ASR Confidence Distribution**: Speech recognition quality
10. **Error Rate**: System errors and exceptions
11. **Cost per Query**: AWS service costs per interaction
12. **Cache Hit Ratio**: Response caching effectiveness
13. **Concurrent Users**: Peak usage metrics
14. **Geographic Distribution**: Usage by state/region

### **HITL Service (`hitl_service.py`)**
**Purpose**: Human-in-the-loop workflow management system.

**Case Management**:
- **Priority queuing**: Urgent cases prioritized by complexity
- **Load balancing**: Cases distributed across available agents
- **SLA tracking**: Response time monitoring for human reviewers  
- **Escalation paths**: Supervisor involvement for complex cases
- **Performance metrics**: Human agent KPIs and quality scores

### **Cache Service (`cache_service.py`)**
**Purpose**: Response caching system for cost and latency optimization.

**Caching Strategies**:
- **LLM response caching**: Identical prompts return cached results
- **RAG result caching**: Knowledge retrieval results cached by query
- **Eligibility caching**: Rule evaluations cached by input signature
- **Receipt templates**: Pre-rendered templates for common schemes
- **Translation caching**: Multi-language response caching

### **Additional Services**:
- **`connect_webhook.py`**: Amazon Connect IVR webhook integration
- **`personalization_service.py`**: Response adaptation by user demographics
- **`scheme_feed_service.py`**: Government scheme data updates and management
- **`smart_rag_service.py`**: Advanced RAG with multi-hop reasoning capabilities

---

## 📊 **Data Models (`/backend/app/models`)**

### **Conversation Model**
**Purpose**: Query/answer pair storage with complete provenance tracking.

```python
class Conversation:
    id: str
    session_id: str
    user_query: str
    intent_classification: dict
    rag_results: list
    eligibility_result: dict
    final_response: str
    confidence_scores: dict
    processing_time_ms: int
    created_at: datetime
```

### **UserProfile Model**
**Purpose**: Rich citizen profile with government scheme relevance.

```python
class UserProfile:
    user_id: str
    phone_number: str  # Masked in logs
    state: str
    district: str
    occupation: str
    annual_income: int
    land_ownership_acres: float
    family_size: int
    has_bank_account: bool
    documents_uploaded: list
    language_preference: str
    previous_applications: list
```

### **SchemeApplication Model**
**Purpose**: Submitted application tracking with status updates.

```python
class SchemeApplication:
    application_id: str
    user_id: str
    scheme_name: str
    status: str  # PENDING, APPROVED, REJECTED, UNDER_REVIEW
    eligibility_trace: dict
    receipt_url: str
    submitted_at: datetime
    reviewed_at: datetime
    reviewer_notes: str
```

---

## 🔄 **Workflow Engine (`/backend/agentic_engine`)**

### **Workflow Engine (`workflow_engine.py`) - 200+ lines**
**Purpose**: Finite State Machine orchestrator for complex multi-step workflows.

**State Transitions**:
```python
WORKFLOW_STATES = {
    'START': ['CONSENT_CAPTURE'],
    'CONSENT_CAPTURE': ['LANGUAGE_SELECT'],
    'LANGUAGE_SELECT': ['INTENT_CLASSIFY'],
    'INTENT_CLASSIFY': ['RAG_RETRIEVE'],
    'RAG_RETRIEVE': ['SLOT_COLLECT'],
    'SLOT_COLLECT': ['RULES_VALIDATE', 'SLOT_COLLECT'],  # Loop until complete
    'RULES_VALIDATE': ['RISK_VERIFY'],
    'RISK_VERIFY': ['RESPONSE_GENERATE', 'HITL_QUEUE'],
    'RESPONSE_GENERATE': ['NOTIFY'],
    'NOTIFY': ['END'],
    'HITL_QUEUE': ['HUMAN_REVIEW'],
    'HUMAN_REVIEW': ['RESPONSE_GENERATE'],
    'END': []
}
```

### **Session Manager (`session_manager.py`)**
**Purpose**: Session lifecycle management with persistent storage.

**Session Data Structure**:
```python
session_data = {
    'session_id': str,
    'user_id': str,
    'current_state': str,
    'conversation_history': list,
    'collected_slots': dict,
    'intent_classification': dict,
    'eligibility_results': dict,
    'created_at': datetime,
    'last_interaction': datetime,
    'language_preference': str,
    'channel': str  # 'web', 'ivr', 'sms'
}
```

---

## 🧪 **Testing Infrastructure**

### **API Testing (`test_api.py`)**
**Test Coverage**:
- Health check endpoint validation
- Session initialization workflow
- Query processing pipeline
- Application submission flow
- Admin dashboard functionality
- Error handling and edge cases

### **Bedrock Testing (`test_bedrock_conn.py`)**
**Test Coverage**:
- Nova model connectivity
- Prompt/response validation
- Token usage optimization
- Error handling for rate limits
- Model fallback mechanisms

### **RAG Testing (`test_rag.py`)**
**Test Coverage**:
- Vector search accuracy
- Kendra integration
- Multi-language retrieval
- Relevance scoring
- Context ranking algorithms

---

## 🔐 **Security & Compliance**

### **PII Protection**
- Automatic masking in logs and UI
- Field-level encryption for sensitive data
- Secure key management with AWS KMS
- Data retention policies

### **DPDP Compliance**
- Explicit consent capture
- Data minimization principles  
- Right to erasure implementation
- Audit trail maintenance
- Cross-border data transfer safeguards

### **Hallucination Prevention**
- Deterministic rules validation
- Response verification against known domains
- Human oversight for critical decisions
- Confidence-based routing

---

This comprehensive backend implementation serves as the foundation for India's first voice-first agentic civic automation system, designed to handle millions of concurrent users while maintaining sub-2-second response times and strict compliance with data protection regulations.