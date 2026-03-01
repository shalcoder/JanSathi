#!/usr/bin/env python3
"""
Simple AWS credentials test
"""
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from backend folder
load_dotenv('backend/.env')

print("🔍 Testing AWS Credentials...")
print(f"Access Key: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT SET')}")
print(f"Secret Key: {os.getenv('AWS_SECRET_ACCESS_KEY', 'NOT SET')[:10]}...")
print(f"Region: {os.getenv('AWS_REGION', 'NOT SET')}")

try:
    # Test with STS
    sts = boto3.client('sts', region_name='us-east-1')
    identity = sts.get_caller_identity()
    
    print(f"\n✅ SUCCESS!")
    print(f"Account: {identity['Account']}")
    print(f"User ARN: {identity['Arn']}")
    print(f"User ID: {identity['UserId']}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    print("\n💡 Possible issues:")
    print("  1. Access Key ID is incorrect")
    print("  2. Secret Access Key is incorrect") 
    print("  3. Keys are expired or deactivated")
    print("  4. User doesn't have proper permissions")
    print("\n🔧 To fix:")
    print("  1. Go to AWS Console → IAM → Users → jansathi-app")
    print("  2. Security credentials tab")
    print("  3. Create new access key if needed")
    print("  4. Update .env file with correct values")