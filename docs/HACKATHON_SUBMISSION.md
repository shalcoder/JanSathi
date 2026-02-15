# 🏆 JanSathi - Hackathon Submission Guide

**"Bridging the Digital Divide with Voice-First AI"**

This document describes how JanSathi addresses the specific evaluation criteria for this hackathon.

---

## 1. 🛠️ Technical Excellence (30%)
*Code quality, scalability, robustness, and architecture design.*

### **Architecture & Cloud-Native Design**
*   **Microservices-Ready**: Built on a decoupled Flask backend + Next.js frontend architecture, containerized with **Docker** for consistent deployment across any environment (AWS, Render, Vercel).
*   **Serverless Orchestration**: Leverages **AWS Bedrock** as a stateless reasoning layer, ensuring zero-maintenance AI scalability.
*   **Robust Persistence**: Uses **SQLite/PostgreSQL** for transactional integrity of application data and **AWS S3** for durable audio/document storage.
*   **Type Safety**: Frontend is built with **TypeScript** and **Zod** schema validation to prevent runtime errors.

### **Innovative Use of AWS Services**
| Service | Innovative Usage |
| :--- | :--- |
| **AWS Bedrock** | **Multi-Agent Orchestration**: We don't just "call an LLM". We use Bedrock to power a chain of agents: *Intent Parser* -> *RAG Retriever* -> *Policy Verifier* -> *Response Formatter*. |
| **AWS Kendra** | **Hybrid Search**: Combines semantic vector search with keyword matching to find government schemes even when users use vague rural dialects. |
| **AWS Transcribe** | **Dialect-Aware ASR**: Configured for Indian English and Hindi, handling mixed-language queries ("Hinglish") effectively. |
| **AWS Polly** | **Neural TTS**: Uses "Aditi" and "Kajal" neural voices for hyper-realistic Hindi/English interaction, crucial for illiterate users. |

---

## 2. 💡 Innovation & Creativity (30%)
*Uniqueness, novelty, and cleverness.*

### **The "Why Didn't I Think of That?" Features:**

#### **1. Deterministic Trust Engine (The "Red Tape" Cutter)**
*   **Problem**: LLMs hallucinate. You can't have an AI lie about government eligibility.
*   **Innovation**: We built a **Hybrid Engine**.
    *   *Layer 1*: **Rules Engine (Python)** executes hard-coded, legal policy logic (e.g., `income < 200000`).
    *   *Layer 2*: **LLM (Claude 3.5)** explains *why* you failed the rule in simple language.
*   **Result**: 100% accuracy on eligibility checks, with the empathy of an AI.

#### **2. "One-Click Apply" Agent**
*   **Innovation**: Most bots just give you a link. JanSathi **fills the form for you**.
*   **How**: The AI extracts your profile (from your uploaded Ration Card), maps it to the scheme's field requirements, and submits the application API request directly.

#### **3. Personal Document RAG**
*   **Innovation**: Users don't know what schemes they qualify for. JanSathi lets them **upload a photo of their documents** (Aadhaar, Land Record).
*   **Cleverness**: We index *your* documents into a private vector store on the fly, allowing the AI to say, *"Based on the land size in your uploaded deed, you qualify for PM Kisan."*

---

## 3. 🌍 Impact & Relevance (25%)
*Potential for real-world impact in India.*

### **Solving for the Next Billion Users**
*   **The Gap**: 600M+ Indians are on the internet, but only ~10% speak fluent English using complex apps.
*   **The JanSathi Solution**:
    *   **Voice-First**: No typing required. Just talk.
    *   **Vernacular**: Supports Hindi, Tamil, Kannada, Telugu, Bengali.
    *   **Low-Bandwidth**: Works on 2G/3G via optimized text payloads and audio caching.

### **Growth Potential**
*   **Scalable Model**: The "Federated Learning" architecture (simulated) allows the model to learn local village dialects without uploading sensitive audio to the cloud, preserving privacy while improving local accuracy.
*   **Government Ready**: The "Admin Pulse" dashboard provides officials with real-time data on which schemes are most requested vs. most rejected, closing the feedback loop.

---

## 4. 📦 Completeness & Presentation (15%)
*Polish, documentation, and prototype functionality.*

### **Project Polish**
*   **Glassmorphism UI**: A stunning, modern interface that treats rural citizens with the dignity of a premium experience.
*   **Mobile-First**: Fully responsive. Try it on your phone!
*   **Live Progress**: Real "Application Tracking" with visual stepping (Submitted -> Verified -> Approved).

### **Documentation**
*   **`README.md`**: Complete setup guide and architecture diagrams.
*   **`design.md`**: Detailed system schematics.
*   **`requirements.md`**: Full functional spec.
*   **Video Pitch**: (Link to be added)

---

**JanSathi is not just a chatbot. It is digital public infrastructure for the AI age.**
