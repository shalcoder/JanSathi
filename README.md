JanSathi (जनसाथी)
Voice-First AI Civic Assistant for India
1. Project Overview

JanSathi is a voice-first, AI-powered civic assistant designed to help Indian citizens—especially rural and semi-urban users—access government schemes, certificates, and public services in simple language using voice or text.

The core philosophy is:

Meet citizens where they are — voice first, low bandwidth, minimal UI, high reliability.

JanSathi is built to work even in:

Low-bandwidth environments

Intermittent connectivity

Users unfamiliar with complex apps

It supports:

🎙️ Voice queries

⌨️ Text queries

🌐 Web (primary)

📴 Offline fallback (cached FAQs)

2. Problem Statement

Many Indian government services are:

Fragmented across portals

Hard to understand due to complex language

Inaccessible to users without digital literacy

Citizens often struggle with:

How to apply for certificates (income, caste, residence)

Understanding eligibility for schemes

Knowing required documents and steps

JanSathi solves this by acting as a conversational layer over government knowledge.

3. High-Level Solution

JanSathi provides:

Voice/Text Interface for user queries

Backend AI pipeline to:

Transcribe speech

Retrieve relevant context

Generate clear, human-friendly answers

Graceful fallback when AI services are unavailable

4. Tech Stack
Frontend (Website)

Next.js (React)

TypeScript

Tailwind CSS

Web Speech API – browser-based Speech-to-Text

HTML5 <audio> – audio playback

Progressive Web–friendly design (low bandwidth aware)

The frontend is optimized for low-end devices, slow networks, and voice-first interaction.

Backend

Python (Flask)

Modular service architecture

AWS-ready (but not hard-dependent)

AI / Cloud (Optional / Future)

AWS Transcribe (Speech-to-Text)

AWS Bedrock (LLM generation)

AWS Polly (Text-to-Speech – optional)

⚠️ The system is intentionally designed to work without AWS credentials for hackathon demos.

5. Repository Structure
JanSathi/
├── backend/
│   ├── server.py                # Flask API
│   ├── lambda_handler.py        # Lambda compatibility
│   ├── requirements.txt
│   ├── utils.py                 # Logging, helpers
│   └── services/
│       ├── transcribe_service.py
│       ├── bedrock_service.py
│       ├── rag_service.py
│       └── polly_service.py     # (Optional)
│
├── frontend/
│   ├── app/                     # Next.js App Router
│   │   └── page.tsx             # Home screen
│   ├── components/
│   ├── services/
│   │   ├── api.ts               # Backend API calls
│   │   └── offline.ts           # Offline FAQ fallback
│   ├── styles/
│   └── tailwind.config.ts
│
├── docs/
│   ├── architecture.md
│   ├── failure_mode_analysis.md
│   └── pitch_narration.md
│
└── README.md

6. Backend Architecture
API Endpoints
Endpoint	Method	Purpose
/health	GET	Backend health check
/query	POST	Main query endpoint (text or audio)
/query Input Formats

Text (JSON):

{ "text_query": "How to apply for income certificate" }


Audio (multipart/form-data):

audio_file: <wav/pcm bytes>

/query Output Format
{
  "query": "...",
  "answer": "Human-readable response",
  "context": []
}

7. Backend Internal Flow
Diagram
flowchart TD
    A[Client Request] --> B[Flask /query]
    B --> C{Audio or Text?}
    C -->|Audio| D[TranscribeService]
    C -->|Text| E[Normalize Query]
    D --> E
    E --> F[RagService]
    F --> G[BedrockService]
    G --> H[Response JSON]

Design Principles

No infinite loops

All temp files cleaned via finally

Bounded polling for AWS calls

Graceful mock fallback when AWS unavailable

8. Frontend Architecture (Web)
Key Screens

Single Home Page (Voice-First UX)

Frontend Responsibilities

Handle microphone permissions via browser

Capture voice using Web Speech API

Send text queries to backend

Play audio responses using HTML5 audio

Display readable, minimal UI responses

Handle offline fallback

9. Frontend → Backend Interaction
Diagram
sequenceDiagram
    participant User
    participant WebApp
    participant FlaskAPI

    User->>WebApp: Speak / Type Query
    WebApp->>FlaskAPI: POST /query
    FlaskAPI-->>WebApp: JSON Response
    WebApp-->>User: Display / Play Answer

10. User Flow
Diagram
flowchart LR
    U[User] --> Q{Voice or Text?}
    Q -->|Voice| V[Browser Mic Input]
    Q -->|Text| T[Text Input]
    V --> S[Send Query]
    T --> S
    S --> A[AI Response]
    A --> D[Display / Audio Output]

11. Offline Mode

When internet is unavailable:

Web app detects offline state

Searches cached FAQ keywords

Returns best matching local answer

This ensures:

No blank screen

No crashes

Honest UX messaging

12. Current Project Status (✅ COMPLETED)
Backend

✅ Stable Flask server

✅ No resource leaks

✅ No infinite loops

✅ AWS-optional design

✅ Production-safe error handling

Frontend (Web)

✅ Next.js + TypeScript setup

✅ Voice input via browser

✅ Audio playback supported

✅ Backend contract aligned

✅ No runtime crashes

13. Known Non-Blocking Risks
Browser Speech API Limitations

Depends on browser support (best on Chrome/Edge)

Requires internet connection

Impact:

Voice input may be unavailable on some browsers

Text input always remains available

14. What Is Pending (Future Work)
AI Enhancements

🔲 Enable real AWS credentials

🔲 Improve RAG knowledge base

🔲 Add multilingual support

UX Enhancements

🔲 Conversation history

🔲 Scheme deep-linking

🔲 Better audio voices

Production Readiness

🔲 Authentication (if needed)

🔲 Rate limiting

🔲 Deployment (Vercel / EC2 / Lambda)

15. How to Run Locally
Backend
cd backend
pip install -r requirements.txt
python server.py

Frontend (Web)
cd frontend
npm install
npm run dev

16. Project Vision

JanSathi is not just a hackathon demo.
It is designed as a foundational civic AI layer that can:

Scale across states

Support multiple dialects

Integrate with official data sources

Goal: Make government services understandable, accessible, and human.

17. Authors & Contributors

Poornachandran (Primary Developer)

Team JanSathi

18. License

To be decided (Hackathon / Open Source).
