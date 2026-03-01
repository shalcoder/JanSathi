import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

def test_bedrock():
    print("--- Testing Bedrock Invocation ---")
    region = os.getenv('AWS_REGION', 'us-east-1')
    model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-haiku-20240307-v1:0")
    
    print(f"Region: {region}")
    print(f"Model ID: {model_id}")
    
    client = boto3.client('bedrock-runtime', region_name=region)
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Hello, are you working?"
            }
        ],
        "temperature": 0.1
    })

    try:
        print("Invoking model...")
        response = client.invoke_model(
            body=body, 
            modelId=model_id, 
            accept='application/json', 
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        print("✅ Success! Response:")
        print(response_body['content'][0]['text'])
        
    except Exception as e:
        print("\n❌ Invocation FAILED")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        
        if "AccessDeniedException" in str(e):
            print("\n💡 TIP: Ensure your IAM user has 'bedrock:InvokeModel' permission.")
            print("💡 TIP: Ensure the model is ENABLED in the AWS Console > Bedrock > Model access.")

if __name__ == "__main__":
    test_bedrock()
