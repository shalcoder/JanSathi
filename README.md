# JanSathi (जनसाथी)
## Voice-First AI Civic Assistant for India

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Version](https://img.shields.io/badge/Version-2.0-blue)
![Mobile](https://img.shields.io/badge/Mobile-Optimized-success)

---

## 🌟 Project Overview

**JanSathi** is a voice-first, AI-powered civic assistant designed to help Indian citizens—especially rural and semi-urban users—access government schemes, certificates, and public services in simple language using voice or text.

### Core Philosophy
> **Meet citizens where they are** — voice first, low bandwidth, minimal UI, high reliability.

JanSathi works seamlessly in:
- 📶 Low-bandwidth environments
- 🔌 Intermittent connectivity
- 👥 For users unfamiliar with complex apps

### Scenario Highlights
- 🎙️ **Voice queries** (Speech-to-Text)
- 🖥️ **Vision AI** (Extract Scheme info from Ration/Caste cards)

---

## 📐 System Design & Diagrams

### 🏗️ Architecture diagram of the proposed solution:
```mermaid
%%{init: {'theme': 'default', 'themeVariables': { 'mainBkg': '#ffffff', 'background': '#ffffff' }}}%%
graph TD
    %% Styling
    classDef user fill:#f97316,stroke:#fff,stroke-width:2px,color:#fff
    classDef fe fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff
    classDef be fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff
    classDef ai fill:#6366f1,stroke:#fff,stroke-width:2px,color:#fff
    classDef trust fill:#ef4444,stroke:#fff,stroke-width:2px,color:#fff
    classDef db fill:#f59e0b,stroke:#fff,stroke-width:2px,color:#fff

    User((fa:fa-user Citizen)):::user -- "fa:fa-microphone Voice/Text Query" --> Frontend[fa:fa-laptop Next.js 15 UI]:::fe
    
    subgraph "🔐 Privacy & Edge (FL)"
        Frontend -- "fa:fa-puzzle-piece Model Updates" --> FL[fa:fa-project-diagram Federated Learning - Flower]:::ai
    end

    subgraph "🌐 Access Layer"
        Frontend -- "fa:fa-wifi API Req" --> Flask[fa:fa-server Flask Backend]:::be
        Flask -- "fa:fa-key Auth" --> Clerk[fa:fa-lock Clerk Security]:::be
    end

    subgraph "🤖 Multi-Agent Orchestration"
        Flask -- "fa:fa-cogs Step Functions" --> Agents[fa:fa-robot Bedrock Agents / LangGraph]:::ai
        Agents -- "fa:fa-search RAG" --> Kendra[fa:fa-book AWS Kendra]:::ai
        Agents -- "fa:fa-brain Reasoning" --> Bedrock[fa:fa-cloud Claude 3.5 Sonnet]:::ai
    end

    subgraph "🛡️ Explainable AI (XAI)"
        Bedrock -- "fa:fa-search-plus Provenance" --> XAI[fa:fa-balance-scale SageMaker Clarify / Audit]:::trust
        XAI -- "fa:fa-file-alt Cite" --> Flask
    end

    subgraph "💾 Persistence"
        Flask -- "fa:fa-save Save" --> DB[(fa:fa-database PostgreSQL / SQLite)]:::db
        DB -- "fa:fa-history History" --> Flask
    end

    Flask -- "fa:fa-envelope Response" --> Frontend
    Frontend -- "fa:fa-volume-up Voice" --> User
```

### 🔄 Process flow diagram or Use-case diagram:
```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#ffffff', 'mainBkg': '#ffffff', 'clusterBkg': '#ffffff', 'nodeBorder': '#333333', 'clusterBorder': '#333333', 'lineColor': '#333333', 'fontFamily': 'arial', 'fontSize': '14px'}}}%%
graph LR
    %% Styles
    classDef start fill:#dcfce7,stroke:#166534,stroke-width:2px,color:#000
    classDef process fill:#dbeafe,stroke:#1e40af,stroke-width:2px,color:#000
    classDef decision fill:#ffedd5,stroke:#c2410c,stroke-width:2px,color:#000,shape:rhombus
    classDef ai fill:#f3e8ff,stroke:#6b21a8,stroke-width:2px,color:#000
    classDef storage fill:#fef9c3,stroke:#a16207,stroke-width:2px,color:#000
    classDef endnode fill:#fee2e2,stroke:#b91c1c,stroke-width:2px,color:#000

    %% Nodes
    A[👤 Citizen Login / Dashboard]:::start
    B[🎙️ Voice Query / Upload]:::start
    C[🌐 Speech-to-Text]:::process
    D{Intent Analysis?}:::decision
    
    %% Semantic Search Flow
    E[📚 Kendra Retrieval]:::ai
    F[🧠 Bedrock LLM Reasoner]:::ai
    G[🔊 Polly TTS]:::process
    
    %% Eligibility Flow
    H[📄 Vision OCR]:::ai
    I{Document Valid?}:::decision
    J[🧮 Criteria Matching]:::process
    K[🌸 Federated Learning Update]:::ai
    L[⚖️ XAI Explanation]:::process

    %% Database
    DB[(�️ User History)]:::storage
    
    %% Connections
    A --> B
    B --> C
    C --> D
    
    %% Branch 1: Search
    D -- "General Query" --> E
    E --> F
    F --> G
    
    %% Branch 2: Eligibility Check
    D -- "Check Eligibility" --> H
    H --> I
    I -- "Yes" --> J
    I -- "No" --> B
    J --> K
    J --> L
    L --> F
    
    %% Final Output
    G --> End[📱 App Response]:::endnode
    F --> DB
```

### 🛠️ Advanced Tech Stack Taxonomy:
| **🛸 Orchestration & FL** | **⚖️ Trust & XAI** | **🏗️ Core Services** |
| :---: | :---: | :---: |
| ![Flower](https://img.shields.io/badge/Flower-Federated_Learning-f47721?style=flat-square&logo=flower&logoColor=white) | ![SageMaker](https://img.shields.io/badge/Amazon-SageMaker_Clarify-232F3E?style=flat-square&logo=amazon-aws&logoColor=white) | ![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=next.js&logoColor=white) |
| ![StepFunctions](https://img.shields.io/badge/AWS-Step_Functions-E7157B?style=flat-square&logo=amazon-aws&logoColor=white) | ![BedrockTrace](https://img.shields.io/badge/Amazon-Bedrock_Trace-232F3E?style=flat-square&logo=amazon-aws&logoColor=white) | ![Flask](https://img.shields.io/badge/Python-Flask-000000?style=flat-square&logo=flask&logoColor=white) |
| ![LangGraph](https://img.shields.io/badge/LangGraph-Agents-1C1C1C?style=flat-square&logo=python&logoColor=white) | ![Provenance](https://img.shields.io/badge/JanSathi-Provenance_Engine-10b981?style=flat-square) | ![Bedrock](https://img.shields.io/badge/AWS-Bedrock-232F3E?style=flat-square&logo=amazon-aws&logoColor=white) |

---

## 🎯 Problem Statement

Many Indian government services are:
- **Fragmented** across multiple portals
- **Complex** with difficult-to-understand language
- **Inaccessible** to users without digital literacy

Citizens struggle with:
- ❓ How to apply for certificates (income, caste, residence)
- ❓ Understanding eligibility for schemes
- ❓ Knowing required documents and steps

**JanSathi solves this** by acting as a conversational layer over government knowledge.

---

## 🚀 Tech Stack

### Frontend (Website)
- **Framework**: ![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js) **Next.js 16** (React, TypeScript)
- **Styling**: ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white) **Tailwind CSS**
- **UI/UX**: ✨ **Glassmorphism**, Aurora gradients, Premium animations
- **Speech**: 🎙️ **Web Speech API** (browser-based STT)
- **Audio**: 🔊 **HTML5 Audio** for playback
- **State**: 🔄 **React Hooks + localStorage**
- **Mobile**: 📱 **Fully responsive** (320px - 4K)

### Backend
- **Framework**: ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) **Python Flask**
- **Architecture**: 🏛️ **Clean Architecture** (API → Services → Core)
- **Database**: ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) **SQLAlchemy ORM**
- **Server**: ⚡ **Gunicorn** with async workers
- **Security**: 🛡️ **Talisman, CORS, Rate Limiting**
- **Logging**: 📝 **Structured JSON Logging**

### AI / Cloud Services
- **AWS Services**: ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white) **Bedrock (Claude 3.5), Kendra (RAG), Polly (TTS)**
- **Security**: 🛡️ **Prompt Injection Guards**, PII Anonymization, Content Moderation
- **Observability**: 📊 **Request Tracing**, AI Quality Metrics
- **Fallback**: 🔄 **Intelligent Hybrid RAG** with Local Edge Caching

---

## 📁 Repository Structure

```
JanSathi/
├── backend/
│   ├── main.py                     # Production entry point
│   ├── app/
│   │   ├── api/                    # Flask Blueprints (routes.py)
│   │   ├── services/               # Business logic (AWS integrations)
│   │   ├── models/                 # SQLAlchemy models
│   │   └── core/                   # Config, utils, logging
│   ├── Dockerfile                  # Production container
│   ├── requirements.txt
│   └── lambda_handler.py           # AWS Lambda entry point
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── sign-in/           # Authentication pages
│   │   │   ├── sign-up/
│   │   │   └── dashboard/         # Main dashboard
│   │   ├── components/
│   │   │   ├── features/
│   │   │   │   ├── chat/          # Chat interface + Voice input
│   │   │   │   └── dashboard/     # Documents, Profile, Settings
│   │   │   ├── layout/            # Sidebar, Telemetry, Header
│   │   │   └── ui/                # Reusable components
│   │   ├── services/              # API client (Axios)
│   │   ├── hooks/                 # Custom React hooks (useAuth, useSettings)
│   │   └── styles/                # Global CSS
│   ├── public/                     # Static assets
│   ├── Dockerfile                  # Production Next.js container
│   └── package.json
│
├── docs/                           # Consolidated Documentation & Guides
│   ├── AUTHENTICATION_GUIDE.md    # Auth integration guide
│   ├── HACKATHON_SUBMISSION.md    # Hackathon-ready project overview
│   ├── AWS_SETUP_GUIDE.md         # AWS infrastructure setup guide
│   ├── KENDRA_SETUP_GUIDE.md      # Detailed Kendra RAG integration
│   ├── design.md                  # Detailed system design & schemas
│   └── requirements.md            # Business & technical requirements
│
├── infrastructure/                 # Infrastructure-as-Code (AWS CDK)
├── scripts/                        # Setup, Monitoring & Testing utilities
└── README.md                       # Main Entry Point
```

---

### 🏗️ JanSathi Ecosystem & Technical Flow

```mermaid
flowchart TD
    %% Node Definitions
    START([<b>Citizen Access</b><br/>Login / Voice ID])
    DASH[<b>JanSathi Pulse</b><br/>Main Dashboard]
    
    subgraph Discovery ["<b>Knowledge Discovery Loop</b>"]
        direction TB
        BROWSE[Browse Benefit Universe]
        ONLINE[Online Inquiry<br/>RAG Enabled]
        OFFLINE[Offline Fallback<br/>Edge Cached]
        COMP[Query Composition]
    end

    subgraph AI_Core ["<b>Intelligence Layer (AWS Bedrock)</b>"]
        direction TB
        SUBMIT{Submit Query}
        VISION[<b>Bedrock Vision</b><br/>OCR & Analysis]
        TEXT[<b>Bedrock NLP</b><br/>Semantic Q&A]
        SAN[Response Sanitizer<br/>PII Masking]
    end

    subgraph Stakeholder ["<b>Stakeholder Management</b>"]
        direction TB
        GOVT[<b>JanSathi Pulse</b><br/>Admin View]
        MON[Benefit Gap<br/>Analytics]
        OUT[Outreach Engine<br/>IVR / WhatsApp]
    end

    %% Connections
    START --> DASH
    DASH --> BROWSE
    BROWSE --> ONLINE & OFFLINE
    ONLINE & OFFLINE --> COMP
    COMP --> SUBMIT
    
    SUBMIT -- "Document Upload" --> VISION
    SUBMIT -- "Voice / Text" --> TEXT
    
    VISION & TEXT --> SAN
    SAN --> FEEDBACK[Personalized Benefit Guide]
    
    FEEDBACK --> PROFILE[Citizen Record<br/>DynamoDB]
    PROFILE --> MON
    MON --> GOVT
    GOVT --> OUT
    OUT -->|Closing the loop| START

    %% Styling (Premium Aesthetics)
    style START fill:#f97316,stroke:#fff,stroke-width:2px,color:#fff
    style DASH fill:#4f46e5,stroke:#fff,stroke-width:2px,color:#fff
    style SUBMIT fill:#0ea5e9,stroke:#fff,stroke-width:4px,color:#fff
    style FEEDBACK fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff
    style GOVT fill:#6366f1,stroke:#fff,stroke-width:2px,color:#fff
    
    classDef layer fill:#f8fafc,stroke:#e2e8f0,stroke-width:1px,color:#64748b,stroke-dasharray: 5 5
    class Discovery,AI_Core,Stakeholder layer
```

### Technical Infrastructure Details
> **Implementation Note**: The following diagrams represent the transition towards the full [AWS Production Architecture](docs/AWS_PRODUCTION_ARCHITECTURE.md) implemented in v2.5.

#### **Backend Production Pipeline**
```mermaid
flowchart TD
    A[Client Request] --> B[API Gateway / Flask]
    B --> SEC[Security Layer: Prompt Injection & PII Filter]
    SEC --> C{Query Type?}
    C -->|Audio| D[AWS Transcribe]
    C -->|Text| E[Query Normalization]
    D --> E
    E --> F[RAG Service - Kendra Retrieval]
    F --> G[Bedrock Service - Claude 3.5 Haiku]
    G --> MON[Observability: X-Ray & Quality Monitor]
    MON --> SAN[Response Sanitizer]
    SAN --> H[AWS Polly - TTS Optional]
    H --> I[Response JSON + Provenance]
```

#### **AWS Cloud Stack**
```mermaid
flowchart TB
    subgraph Edge ["Edge & Security"]
        CF[CloudFront CDN]
        WAF[AWS WAF / Rate Limiter]
    end

    subgraph App ["Compute Layer"]
        API[API Gateway / Flask]
        VAL[Validators & Security]
    end

    subgraph AI ["Intelligence Layer"]
        BED[AWS Bedrock]
        KEN[AWS Kendra RAG]
        TRA[AWS Transcribe]
        POL[AWS Polly]
    end

    subgraph Data ["Persistence"]
        DB[(DynamoDB)]
        S3[(S3 Assets)]
    end

    subgraph Obs ["Observability"]
        XR(AWS X-Ray Tracing)
        CW(CloudWatch Metrics)
        QM(AI Quality Monitor)
    end

    CF --> WAF --> API
    API --> VAL
    VAL --> AI
    AI <--> Data
    AI --> Obs
```

---

## 🎨 UI/UX Features (v2.0 - Latest Updates)

### ✅ Completed Features

#### **Landing Page**
- ✨ Modern hero section with animated gradients
- ✨ Feature showcase grid (Voice AI, Document Analysis, Multilingual)
- ✨ Tech stack section with AWS branding
- ✨ **Mobile-optimized**: Responsive text sizing and layouts
- ✨ **Fixed typo**: "Government" (was "Govenment")
- ✨ Sign In/Sign Up buttons in navbar

#### **Authentication System (NEW!)**
- 🔐 **Sign In Page** (`/sign-in`)
  - Email & password login
  - Google Sign In button (demo)
  - Remember me checkbox
  - Forgot password link
  - Modern glassmorphism UI
  - Form validation & error handling

- 🔐 **Sign Up Page** (`/sign-up`)
  - Full registration form (name, email, password)
  - Password confirmation & strength validation
  - Terms & conditions acceptance
  - Google Sign Up option
  - Comprehensive client-side validation

- 🔐 **Authentication Features**
  - Demo mode using localStorage (ready for production auth)
  - Sign Out functionality
  - useAuth hook for state management
  - Supports Clerk, NextAuth, Firebase, Supabase integration

#### **Chat Interface**
- 💬 Typewriter effect for AI responses
- 💬 Voice input with visual feedback
- 💬 Image analysis integration
- 💬 Government scheme cards with benefits
- 💬 Session management
- 💬 **Mobile-optimized**: Message bubbles adapt to screen size
- 💬 **Improved spacing**: Better padding on mobile devices

#### **Dashboard Pages**
- 📄 **Documents Page**: Official guidelines + upload for AI analysis
- 📊 **Market Rates**: Live Mandi prices (demo data)
- 👤 **Profile Page**: User stats, badges, preferences
- ⚙️ **Settings Page**: Language, theme, voice preferences
- 📡 **Telemetry Panel**: AWS service status (desktop only)

#### **Production Security (NEW!)**
- 🛡️ **Prompt Injection Defense**: Multi-pattern regex & length validation to block jailbreaks.
- 🛡️ **PII Anonymization**: Automatic HMAC-SHA256 hashing for Aadhaar and masking for phone/email.
- 🛡️ **Content Moderation**: Simulated keyword safety checks (ready for AWS Comprehend).
- 🛡️ **Response Sanitization**: Automated removal of internal PII and system markers from AI output.

#### **Observability & Ops**
- 📡 **X-Ray Tracing**: Full request lifecycle visibility with simulated distributed tracing.
- 📡 **AI Quality Monitor**: Drift detection and confidence-based human-audit flagging.
- 📡 **Structured Logging**: CloudWatch-ready JSON logging for all system events.

#### **Stakeholder Differentiators**
- 📞 **Voice-First IVR**: Simulated citizen outreach via phone channels (AWS Connect flow).
- 💬 **WhatsApp Outreach**: Citizen engagement simulator for high-accessibility channels.
- 👥 **Community Moderation**: Human-in-the-loop interface for auditing flagged AI responses.

#### **Mobile Responsiveness (MAJOR UPDATE)**
- ✅ **All pages fully responsive** (320px → 4K displays)
- ✅ **Vertical alignment fixed** across all pages
- ✅ **Adaptive layouts**: Grids stack on mobile
- ✅ **Touch-friendly**: Buttons sized for mobile interaction
- ✅ **Viewport meta tag**: Proper mobile scaling
- ✅ **Responsive text**: Scales from sm → lg → xl
- ✅ **Horizontal scroll**: Tables adapt on small screens

#### **Design System**
- 🎨 Custom glassmorphism effects
- 🎨 Aurora gradient background
- 🎨 Consistent color palette (Blue, Purple, Emerald accents)
- 🎨 Modern typography (Geist Sans font family)
- 🎨 Smooth animations and transitions
- 🎨 Dark mode optimized

---

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Backend health check |
| `/query` | POST | Main query endpoint (text or audio) |
| `/history` | GET | Retrieve past queries (optional) |

### `/query` Input Formats

**Text (JSON):**
```json
{
  "text_query": "How to apply for income certificate",
  "language": "en"
}
```

**Audio (multipart/form-data):**
```
audio_file: <wav/pcm bytes>
```

### `/query` Output Format

```json
{
  "query": "User query text",
  "answer": "Human-readable response",
  "audio_url": "https://...",
  "context": ["source1", "source2"],
  "structured_sources": [...]
}
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **npm** or **pnpm** (package manager)

### Quick Start

#### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs on `http://localhost:5000`

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:3000`

#### 3. Environment Variables

**Frontend (`.env.local`):**
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:5000

# Authentication (Optional - currently in demo mode)
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
# CLERK_SECRET_KEY=sk_test_...
```

**Backend (`.env` or environment):**
```bash
# AWS Credentials (Optional - has mock fallback)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1

# Flask Config
FLASK_ENV=development
```

---

## 📱 Mobile Optimization Highlights

### Responsive Breakpoints
- **Mobile**: `< 640px` (base styles)
- **Tablet**: `sm: >= 640px`
- **Laptop**: `md: >= 768px`
- **Desktop**: `lg: >= 1024px`
- **Large**: `xl: >= 1280px`

### Key Improvements
1. **Landing Page**: Hero text scales from `text-4xl` → `text-8xl`
2. **Chat Interface**: Message bubbles use 95% width on mobile
3. **Documents Grid**: 1 column mobile → 3 columns desktop
4. **Input Controls**: Touch-friendly button sizes
5. **Tables**: Horizontal scroll on mobile
6. **Navigation**: Hamburger menu for mobile sidebar

---

## 🔐 Authentication & Security

### Current Implementation (Demo Mode)
- Uses **localStorage** for demo purposes
- No backend authentication required
- Perfect for testing and prototyping

### Production Ready Options
Refer to `docs/AUTHENTICATION_GUIDE.md` for detailed integration guides:
- **Clerk** (Recommended - easiest setup)
- **NextAuth.js** (Free, open-source)
- **Firebase Auth** (Google's solution)
- **Supabase Auth** (Open-source alternative)

### Sign Out Flow
1. User clicks "Sign Out" in sidebar
2. localStorage cleared
3. Redirect to `/sign-in`
4. All sessions terminated

---


---

## ✅ Production Readiness Checklist

### Backend
- ✅ Clean Architecture (API, Services, Core layers)
- ✅ Modular Flask Blueprints
- ✅ Docker containerization (Gunicorn + async workers)
- ✅ Enterprise security (Talisman, CORS, Rate Limiting)
- ✅ Structured JSON logging (CloudWatch ready)
- ✅ AWS integration with graceful fallbacks
- ✅ Health check endpoints

### Frontend
- ✅ Next.js 16 with App Router
- ✅ TypeScript for type safety
- ✅ Responsive design (mobile-first)
- ✅ Error boundaries for stability
- ✅ Authentication system (demo + integration ready)
- ✅ Optimized production build
- ✅ Docker multi-stage builds
- ✅ SEO-friendly meta tags
- ✅ Accessibility considerations

### UI/UX
- ✅ Premium glassmorphism design
- ✅ Multilingual support (4+ languages)
- ✅ Voice input/output
- ✅ Session management
- ✅ Loading states and animations
- ✅ Error handling with user-friendly messages
- ✅ Mobile-optimized layouts
- ✅ Touch-friendly interactions

---

### v2.5 - Production Hardening (Current)
1. 🛡️ **Advanced Security Suite**
   - **Shield**: Multi-layer Prompt Injection defense patterns
   - **Privacy**: Automated PII masking & HMAC anonymization for Aadhaar/Phone
   - **Safety**: Content moderation logic for government service compliance
2. 📡 **Enterprise Observability**
   - **Tracing**: End-to-end request lifecycle visibility
   - **Quality**: AI confidence scoring and human-in-the-loop flagging
   - **Audit**: Local auditing system for AI explainability
3. 📊 **JanSathi Pulse (Stakeholder Layer)**
   - **Analytics**: Benefit Gap analysis for government admins
   - **Outreach**: Simulated IVR and WhatsApp citizen engagement flows
   - **Moderation**: Dedicated dashboard for auditing flagged AI responses
4. 🎨 **Premium Aesthetic Polish**
   - **Design**: High-fidelity glassmorphism and aurora gradient refactor
   - **Visuals**: High-density Mermaid ecosystem workflows
   - **UX**: Dynamic initials-based profile loading and zero-state optimizations

---

## 📚 Documentation

- **`docs/AUTHENTICATION_GUIDE.md`** - How to integrate real authentication providers
- **`docs/HACKATHON_SUBMISSION.md`** - Hackathon-ready project overview
- **`docs/AWS_SETUP_GUIDE.md`** - AWS infrastructure setup guide
- **`docs/KENDRA_SETUP_GUIDE.md`** - Detailed Kendra RAG integration
- **`docs/COST_OPTIMIZATION.md`** - Strategy for $0/mo development
- **`docs/failure_mode_analysis.md`** - Resilience and error handling strategy

---

## 🎬 Demo Scenarios

### Scenario 1: Applying for Income Certificate
```
User: "मुझे आय प्रमाण पत्र कैसे मिलेगा?"
(How do I get an income certificate?)

JanSathi: Provides step-by-step guidance in Hindi, 
including required documents, online portal link, 
and expected processing time.
```

### Scenario 2: Checking Mandi Rates
```
User: "What are today's wheat prices?"

JanSathi: Returns live/demo mandi rates for wheat
across different markets with comparative analysis.
```

### Scenario 3: Document Analysis
```
User: Uploads ration card image

JanSathi: Analyzes document using Vision AI,
extracts key information, and suggests relevant
schemes based on family composition.
```

---

## 🐛 Known Issues & Limitations

### Non-Blocking
- ⚠️ Browser Speech API performance varies on non-Chromium browsers
- ⚠️ AWS services require credentials (has mock fallback)
- ⚠️ Demo authentication uses localStorage (not for production)

### Future Enhancements
- 🔲 Password reset functionality
- 🔲 Email verification flow
- 🔲 Real-time mandi price updates
- 🔲 PDF export for scheme details
- 🔲 Push notifications for scheme updates
- 🔲 Offline PWA support

---

## 🚧 Next Steps

### Immediate
1. Integrate production authentication provider
2. Connect to real government data APIs
3. Add unit and integration tests
4. Set up CI/CD pipeline

### Short-term
1. Implement acoustic fine-tuning for rural accents
2. Add multimodal PDF processing
3. Expand language support (10+ languages)
4. Mobile app (React Native/Flutter)

### Long-term
1. WhatsApp bot integration
2. SMS fallback for feature phones
3. State-specific customization
4. Integration with official government portals

---

## 📄 License

MIT License (Open Source)

---

## 🙏 Acknowledgments

- Government of India's Digital India initiative
- AWS for cloud infrastructure
- Open-source community for tools and libraries

---

## 📞 Support

For questions or support:
- 📧 Email: support@jansathi.ai (placeholder)
- 💬 WhatsApp: +91-1234567890 (demo)
- 🌐 Website: https://jansathi.ai (coming soon)

---

**Built with ❤️ for Digital India**

![India](https://img.shields.io/badge/Made%20in-India-orange)
![Open Source](https://img.shields.io/badge/Open-Source-green)
![AI Powered](https://img.shields.io/badge/AI-Powered-blue)
