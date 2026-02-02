# JanSathi Architecture Diagram

```mermaid
graph TD
    subgraph "Layer 1: User Interaction"
        UA[User (Rural Citizen)]
        MP[Mobile App (Flutter)]
        WA[WhatsApp Chatbot]
        IVR[IVR / Toll-Free]
    end

    subgraph "Layer 2: API & Orchestration"
        APIGW[Amazon API Gateway]
        LambdaOrch[AWS Lambda Orchestrator]
    end

    subgraph "Layer 3: AI Intelligence"
        Transcribe[Amazon Transcribe (STT)]
        Bedrock[Amazon Bedrock (LLM Reasoning)]
        Polly[Amazon Polly (TTS)]
        Translate[Amazon Translate]
    end

    subgraph "Layer 4: Knowledge & Retrieval (RAG)"
        Kendra[Amazon Kendra]
        S3[Amazon S3 (Documents)]
        ExtAPI[External APIs (Mandi/Weather)]
    end

    subgraph "Layer 5: Data & State"
        Dynamo[Amazon DynamoDB (User Profile/Context)]
    end

    %% Flows
    UA -->|Voice/Text| MP & WA & IVR
    MP & WA & IVR -->|HTTPS/WSS| APIGW
    APIGW --> LambdaOrch

    %% Orchestration Logic
    LambdaOrch -->|1. Store Context| Dynamo
    LambdaOrch -->|2. Audio Stream| Transcribe
    Transcribe -->|Text| LambdaOrch
    LambdaOrch -->|3. Intent/Translation| Translate
    LambdaOrch -->|4. Retrieve Facts| Kendra
    Kendra -->|Index| S3
    Kendra -->|Live Data| ExtAPI
    LambdaOrch -->|5. Generate Answer| Bedrock
    Bedrock -->|Answer Text| LambdaOrch
    LambdaOrch -->|6. Convert to Speech| Polly
    Polly -->|Audio| LambdaOrch
    LambdaOrch -->|Response| APIGW

    %% Styling
    classDef aws fill:#FF9900,stroke:#232F3E,color:white;
    classDef client fill:#88CC88,stroke:#333333;
    class APIGW,LambdaOrch,Transcribe,Bedrock,Polly,Translate,Kendra,S3,Dynamo aws;
    class UA,MP,WA,IVR client;
```
