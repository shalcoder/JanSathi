# AWS Bedrock Integration Guide – JanSathi

## 1. Current System Architecture

The JanSathi intent classification system is built using a **Strategy Pattern** to ensure modularity and ease of integration for future AI services.

- **IntentService**: The main entry point for classification. It delegates the actual work to a specific classifier strategy.
- **RuleBasedIntentClassifier**: The currently active default strategy. It uses keyword-based matching for immediate functionality.
- **BedrockIntentClassifier**: A placeholder class designed for future AWS Bedrock integration.
- **INTENT_CLASSIFIER**: An environment variable that determines which classifier strategy to instantiate at startup.

## 2. What Must Be Implemented

To complete the Bedrock integration, the `BedrockIntentClassifier` class in `backend/app/services/intent_service.py` must be fully implemented.

- **Inheritance**: Must inherit from `BaseIntentClassifier`.
- **Method**: Must implement `classify(self, query: str) -> dict`.
- **Structured Output**: Must return a dictionary with the following contract:
    ```json
    {
        "intent": "string",
        "confidence": 0.0 to 1.0 (float)
    }
    ```
- **Intent Consistency**: The returned `intent` string must strictly match one of the values in `VALID_INTENTS` (e.g., `scheme_lookup`, `eligibility_check`, `document_required`, `general_query`, `fallback`).

## 3. Required Environment Variables

The following environment variables are necessary for the AWS SDK (boto3) and the IntentService:

- **AWS_REGION**: The AWS region where Bedrock is available (e.g., `us-east-1`). Default is usually set in the core config.
- **BEDROCK_MODEL_ID**: The specific model to invoke (e.g., `anthropic.claude-3-haiku-20240307-v1:0`).
- **INTENT_CLASSIFIER**: Must be set to `bedrock` to enable the legacy-to-AI switch.

## 4. Required Python Packages

Ensure the following dependencies are installed in the backend environment:

- `boto3`: The AWS SDK for Python.
- `botocore`: The low-level companion library used by boto3.

## 5. Required IAM Permissions

The IAM role or user running the backend requires the following permission:

- `bedrock:InvokeModel`: Specifically for the `BEDROCK_MODEL_ID` being used.
- Ensure the region used has Bedrock enabled.

## 6. Required AWS Account Setup

- **Model Access**: You must manually request and be granted access to the specific Anthropic Claude models in the AWS Bedrock console.
- **Anthropic Claude 3 Haiku**: Recommended for its balance of speed and cost-efficiency for classification tasks.

## 7. Safe Activation Procedure

1. **Implement logic**: Fully code the `invoke_model` logic inside `BedrockIntentClassifier`.
2. **Remove Startup Guard**: Remove the `RuntimeError` currently present in `IntentService.__init__` for the `bedrock` case.
3. **Configure Environment**: Set `INTENT_CLASSIFIER=bedrock` in your `.env` or CI/CD environment.
4. **Restart Server**: Restart the Flask application.
5. **Verify Logs**: Check for the log entry: `[IntentService] Using classifier: bedrock` to confirm successful activation.

## 8. Failure Modes

Current considerations for robust implementation:

- **NoCredentialsError**: Handled if AWS credentials are not configured on the host.
- **AccessDeniedException**: Occurs if the IAM role lacks `InvokeModel` permissions.
- **Validation Fallback**: If Bedrock returns an unexpected intent string or malformed response, the `IntentService` centralized validation will automatically catch it and return a safe `fallback` intent with `0.0` confidence.
- **Invalid Region**: Ensure the `boto3` client is initialized with a region that supports the selected model.
