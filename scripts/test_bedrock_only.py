#!/usr/bin/env python3
"""
Test only Bedrock access
"""
import boto3
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')

def test_bedrock():
    """Test Bedrock model access"""
    print("🤖 Testing Bedrock access...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with a simple prompt
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Bedrock is working!' in one sentence."
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(payload)
        )
        
        result = json.loads(response['body'].read())
        print(f"✅ SUCCESS! Bedrock response: {result['content'][0]['text']}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        
        if "AWSCompromisedKeyQuarantineV3" in str(e):
            print("\n💡 The quarantine policy is still attached!")
            print("   Go to AWS Console → IAM → Users → jansathi-app")
            print("   Remove AWSCompromisedKeyQuarantineV3 policy")
        elif "AccessDenied" in str(e):
            print("\n💡 Need to add Bedrock permissions!")
            print("   Go to AWS Console → IAM → Users → jansathi-app")
            print("   Add AmazonBedrockFullAccess policy")
        
        return False

if __name__ == "__main__":
    test_bedrock()