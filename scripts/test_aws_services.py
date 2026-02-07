#!/usr/bin/env python3
"""
JanSathi AWS Services Test Script
Tests all AWS integrations to verify setup
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

print("🧪 JanSathi AWS Services Test")
print("=" * 50)
print()

# Test 1: Environment Variables
print("1️⃣  Testing Environment Variables...")
required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'S3_BUCKET_NAME']
missing = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        masked = value[:4] + "****" if len(value) > 4 else "****"
        print(f"   ✅ {var}: {masked}")
    else:
        print(f"   ❌ {var}: NOT SET")
        missing.append(var)

if missing:
    print(f"\n❌ Missing variables: {', '.join(missing)}")
    print("   Please configure backend/.env file")
    sys.exit(1)

print()

# Test 2: Bedrock Service
print("2️⃣  Testing AWS Bedrock (Claude 3)...")
try:
    from app.services.bedrock_service import BedrockService
    bedrock = BedrockService()
    
    if not bedrock.working:
        print("   ⚠️  Bedrock not connected (using mock mode)")
    else:
        test_query = "What is PM Kisan scheme?"
        test_context = "PM Kisan provides 6000 rupees per year to farmers in 3 installments."
        
        response = bedrock.generate_response(test_query, test_context, 'en')
        print(f"   ✅ Bedrock Response: {response[:100]}...")
        print(f"   💰 Estimated cost: ~$0.001")
except Exception as e:
    print(f"   ❌ Bedrock Error: {e}")

print()

# Test 3: Polly Service
print("3️⃣  Testing AWS Polly (Text-to-Speech)...")
try:
    from app.services.polly_service import PollyService
    polly = PollyService()
    
    if not polly.use_aws:
        print("   ⚠️  Polly not connected (using mock mode)")
    else:
        test_text = "Hello from JanSathi AI"
        audio_url = polly.synthesize(test_text, 'en')
        
        if audio_url:
            print(f"   ✅ Polly Audio URL: {audio_url[:60]}...")
            print(f"   💰 Characters used: {len(test_text)} (Free tier: 5M/month)")
        else:
            print("   ⚠️  No audio URL returned")
except Exception as e:
    print(f"   ❌ Polly Error: {e}")

print()

# Test 4: RAG Service
print("4️⃣  Testing RAG Service (Mock Data)...")
try:
    from app.services.rag_service import RagService
    rag = RagService()
    
    test_query = "PM Kisan scheme"
    results = rag.retrieve(test_query)
    
    print(f"   ✅ Retrieved {len(results)} documents")
    if results:
        print(f"   📄 Sample: {results[0][:80]}...")
    
    # Test structured sources
    sources = rag.get_structured_sources(test_query)
    print(f"   ✅ Structured sources: {len(sources)}")
    if sources:
        print(f"   📋 Scheme: {sources[0].get('title', 'N/A')}")
except Exception as e:
    print(f"   ❌ RAG Error: {e}")

print()

# Test 5: S3 Bucket Access
print("5️⃣  Testing S3 Bucket Access...")
try:
    import boto3
    s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    # Test bucket exists
    s3_client.head_bucket(Bucket=bucket_name)
    print(f"   ✅ Bucket exists: {bucket_name}")
    
    # Test write permission
    test_key = "test/health_check.txt"
    s3_client.put_object(
        Bucket=bucket_name,
        Key=test_key,
        Body=b"JanSathi Health Check"
    )
    print(f"   ✅ Write permission: OK")
    
    # Test read permission
    obj = s3_client.get_object(Bucket=bucket_name, Key=test_key)
    print(f"   ✅ Read permission: OK")
    
    # Cleanup
    s3_client.delete_object(Bucket=bucket_name, Key=test_key)
    print(f"   ✅ Delete permission: OK")
    
except Exception as e:
    print(f"   ❌ S3 Error: {e}")

print()

# Test 6: Transcribe Service (Skip actual transcription to save costs)
print("6️⃣  Testing AWS Transcribe Service...")
try:
    from app.services.transcribe_service import TranscribeService
    transcribe = TranscribeService()
    
    if not transcribe.use_aws:
        print("   ⚠️  Transcribe not connected (using mock mode)")
    else:
        print("   ✅ Transcribe client initialized")
        print("   ⚠️  Skipping actual transcription to save costs")
        print("   💰 Free tier: 60 minutes/month")
except Exception as e:
    print(f"   ❌ Transcribe Error: {e}")

print()
print("=" * 50)
print("✅ AWS Services Test Complete!")
print()
print("💡 Tips:")
print("   - Monitor costs at: https://console.aws.amazon.com/billing")
print("   - Set up budget alerts for $10/month")
print("   - Bedrock Haiku costs ~$0.25 per 1M tokens")
print("   - Keep queries under 500 tokens to minimize costs")
print()
