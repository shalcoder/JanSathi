# JanSathi Architecture Diagram (AWS Stack)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#ffffff', 'mainBkg': '#ffffff', 'clusterBkg': '#ffffff', 'nodeBorder': '#000000', 'clusterBorder': '#000000', 'lineColor': '#000000'}}}%%
graph TD
    subgraph "Layer 1: User Interaction"
        UA[User (Rural Citizen)]
        MP[Mobile App (Flutter)]
        WA[WhatsApp Chatbot (Cloud API)]
        IVR[Amazon Connect (Phone)]
    end

    subgraph "Layer 2: API & Orchestration (Serverless)"
        APIGW[AWS API Gateway]
        Lambda[AWS Lambda (Orchestrator)]
    end

    subgraph "Layer 3: AI Intelligence (Amazon Bedrock)"
        Bedrock[Amazon Bedrock (Claude 3 / Llama 3)]
        Transcribe[AWS Transcribe (STT)]
        Polly[Amazon Polly (TTS)]
        Translate[Amazon Translate]
    end

    subgraph "Layer 4: Knowledge & Retrieval (RAG)"
        Kendra[Amazon Kendra]
        S3[Amazon S3 (Documents)]
    end

    subgraph "Layer 5: Data & State"
        Dynamo[Amazon DynamoDB (Profiles/History)]
    end

    %% Flows
    UA -->|Voice/Text| MP & WA & IVR
    MP & WA & IVR -->|HTTPS/Webhook| APIGW
    APIGW --> Lambda

    %% Orchestration Logic
    Lambda -->|1. Store Context| Dynamo
    Lambda -->|2. Voice Stream| Transcribe
    Transcribe -->|Text| Lambda
    Lambda -->|3. Detect/Translate| Translate
    Lambda -->|4. Retrieve Facts| Kendra
    Kendra -->|Query Index| S3
    Kendra -->|Relevant Excerpts| Lambda
    Lambda -->|5. Generate Answer| Bedrock
    Bedrock -->|Response Text| Lambda
    Lambda -->|6. Translate Back| Translate
    Lambda -->|7. Convert to Speech| Polly
    Polly -->|Audio| Lambda
    Lambda -->|Response| APIGW
    
    %% Styling
    classDef aws fill:#FF9900,stroke:#232F3E,color:white;
    classDef client fill:#88CC88,stroke:#333333;
    class APIGW,Lambda,Transcribe,Bedrock,Polly,Translate,Kendra,S3,Dynamo aws;
    class UA,MP,WA,IVR client;
```

## Stack Decisions
- **Frontend**: **Flutter** (Single codebase, offline support).
- **Orchestration**: **AWS Lambda** (Serverless, scalable).
- **LLM**: **Amazon Bedrock** (Managed, secure, multilingual).
- **RAG**: **Amazon Kendra** (Enterprise search for government docs).
- **Voice**: **AWS Transcribe** & **Polly** (Indian languages support).
- **Storage**: **DynamoDB** (Fast user state) and **S3** (Document lake).
- **Offline**: **On-Device Cache** (Flutter SQLite/Hive) for top FAQs.
