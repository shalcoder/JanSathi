# JanSathi AI: Hackathon Submission Details

## 🚀 Problem Statement & Solution Overview

### Problem
Communities in India, especially rural farmers and non-English speakers, struggle to access critical government schemes due to:
- **Language Barriers**: Most information is in English.
- **Complex Portals**: Sites like PM-KISAN are hard to navigate.
- **Low Digital Literacy**: Typing is difficult for many.

### Solution: JanSathi
A "Voice-First" AI Assistant that bridges this gap. It allows users to ask questions in their native language (Hindi, Tamil, Kannada) and receive immediate, actionable answers with direct links to schemes. It transforms a complex government portal into a simple conversation.

---

## 💡 Key Features & Differentiators

| **Intelligence** | Text-based chatbot | **Multimodal "Drishti" Vision (Analyze Documents via Camera)** |
| **Transparency** | Black-box operation | **Live Telemetry (Real-time AWS Performance Metrics)** |
| **Accuracy** | Keyword Search | **RAG-based Semantic Search (Kendra + Bedrock)** |

---

## 🛠️ Technical Excellence: AWS Architecture

This solution leverages the power of the AWS Cloud for scalability and intelligence:

1.  **Frontend**: Next.js (React) hosted on Vercel/Amplify.
2.  **API Layer**: Python Flask on AWS Lambda / EC2.
3.  **Voice Processing**:
    -   **Input**: Browser Speech API -> **AWS Transcribe** (for robust accents).
    -   **Output**: **AWS Polly** (Neural Engine) for natural-sounding local languages.
4.  **Intelligence Engine**:
    -   **Knowledge Retrieval**: **AWS Kendra** (Index of Gov PDFs/Sites).
    -   **Reasoning**: **Amazon Bedrock (Claude / Titan)** generates the simplified answer.
5.  **Storage**: **AWS RDS / DynamoDB** for conversation history.

---

## 🌍 Market Opportunity & Viability

### Target Audience
-   **800 Million+** internet users in India (mostly mobile-first).
-   **100 Million+** Farmers eligible for PM-KISAN.
-   **Public Service Centers (CSCs)**: Can use JanSathi as an assisted-mode tool.

### Business Model
1.  **B2G (Business to Government)**: Licensing to State Govts for citizen engagement.
2.  **Freemium API**: Developers building "India Stack" apps can use our "Scheme Intelligence API".
3.  **Assisted Commerce**: Affiliate integrations with Agri-marketplaces (e.g., buying seeds after asking about crops).

---

## 🔮 Future Roadmap

-   **Phase 1 (Production Baseline)**: Clean Architecture + Voice Q&A for Central Schemes. (Completed ✅)
-   **Phase 2 (Visual Intelligence)**: "Drishti" Multimodal analysis for scanning physical notices. (Completed ✅)
-   **Phase 3**: WhatsApp Integration & Agri-Marketplace lead generation. (Next 🚀)
-   **Phase 4**: "Fill for Me" - AI Agent that auto-fills gov forms via voice commands. (Future 🔮)
