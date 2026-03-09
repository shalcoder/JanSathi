# JanSathi AWS Lambda Deployment Guide

This document outlines the steps to package and deploy the JanSathi Agentic Engine as a standalone AWS Lambda function.

## Deployment Details

- **Handler**: `lambda_handler.lambda_handler`
- **Runtime**: `Python 3.11` (or 3.12)
- **Architecture**: `x86_64`
- **Memory**: `512MB` (Recommended)
- **Timeout**: `30 seconds`

## Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_TYPE` | `dynamodb` (Required for cluster deployment) | `local` |
| `DYNAMODB_TABLE` | Name of the DynamoDB table | `JanSathiSessions` |
| `AWS_REGION` | AWS Region for DynamoDB and Bedrock | `us-east-1` |
| `NODE_ENV` | Set to `production` to enable strict validation | `development` |

## Packaging Instructions

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Install dependencies to the current folder**:
    ```bash
    pip install -r requirements-lambda.txt -t .
    ```

3.  **Create the deployment package**:
    ```bash
    # Exclude Flask, tests, and local sessions
    zip -r function.zip . -x "instance/*" "*__pycache__*" "tests/*" ".env" "sessions.json"
    ```

4.  **Upload to AWS Lambda**:
    - Via AWS Console: Upload the `function.zip`.
    - Via CLI: `aws lambda update-function-code --function-name JanSathiEngine --zip-file fileb://function.zip`

## Why this approach?
By decoupling the `lambda_handler.py` from `main.py` and `Flask`, we ensure:
- **Faster Cold Starts**: The Lambda doesn't load the Flask app context or the overhead of multiple blueprints.
- **Smaller Package**: Only the engine and its core requirements are packaged.
- **Portability**: The same engine code runs in Flask (Web) and Lambda (IVR/API).
