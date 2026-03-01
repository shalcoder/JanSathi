#!/usr/bin/env python3
"""
Complete AWS infrastructure setup for JanSathi from terminal
"""
import boto3
import json
import time
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from backend folder
load_dotenv('backend/.env')

def setup_iam_permissions():
    """Check and setup IAM permissions"""
    print("🔐 Checking IAM permissions...")
    
    try:
        sts = boto3.client('sts', region_name='us-east-1')
        identity = sts.get_caller_identity()
        print(f"✅ Connected as: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"❌ IAM Error: {e}")
        return False

def setup_s3_bucket():
    """Create S3 bucket for audio storage"""
    print("\n📦 Setting up S3 bucket...")
    
    bucket_name = os.getenv('S3_BUCKET_NAME', 'jansathi-audio-bucket-2024')
    region = 'us-east-1'
    
    s3 = boto3.client('s3', region_name=region)
    
    try:
        # Create bucket
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created bucket: {bucket_name}")
        
        # Set public read policy for audio files
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
        print("✅ Set public read policy for audio files")
        
        # Set CORS
        cors_config = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST'],
                    'AllowedOrigins': ['*'],
                    'MaxAgeSeconds': 3600
                }
            ]
        }
        
        s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
        print("✅ Configured CORS for audio playback")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"✅ Bucket {bucket_name} already exists")
            return True
        else:
            print(f"❌ S3 Error: {e}")
            return False

def setup_dynamodb_tables():
    """Create DynamoDB tables"""
    print("\n🗄️ Setting up DynamoDB tables...")
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    tables_config = [
        {
            'TableName': 'jansathi-conversations',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'jansathi-schemes',
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'jansathi-users',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    created_tables = []
    
    for table_config in tables_config:
        table_name = table_config['TableName']
        
        try:
            # Check if table exists
            table = dynamodb.Table(table_name)
            table.load()
            print(f"✅ Table {table_name} already exists")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                print(f"🔄 Creating table {table_name}...")
                
                table = dynamodb.create_table(**table_config)
                created_tables.append(table)
                print(f"✅ Created table: {table_name}")
            else:
                print(f"❌ Error with table {table_name}: {e}")
                return False
    
    # Wait for tables to be active
    if created_tables:
        print("⏳ Waiting for tables to become active...")
        for table in created_tables:
            table.wait_until_exists()
        print("✅ All tables are active")
    
    return True

def populate_schemes_table():
    """Add sample data to schemes table"""
    print("\n📋 Populating schemes table with sample data...")
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('jansathi-schemes')
    
    sample_schemes = [
        {
            'id': 'pm-kisan',
            'title': 'PM-KISAN Samman Nidhi',
            'text': 'Provides ₹6,000 per year in three installments to small and marginal farmers.',
            'keywords': ['farmer', 'agriculture', 'income', 'support'],
            'link': 'https://pmkisan.gov.in/',
            'benefit': '₹6,000/year Income Support',
            'ministry': 'Agriculture',
            'category': 'agriculture'
        },
        {
            'id': 'ayushman-bharat',
            'title': 'Ayushman Bharat - PMJAY',
            'text': 'Provides health insurance coverage of ₹5 Lakh per family per year.',
            'keywords': ['health', 'insurance', 'medical', 'treatment'],
            'link': 'https://pmjay.gov.in',
            'benefit': '₹5 Lakh Free Treatment',
            'ministry': 'Health',
            'category': 'healthcare'
        },
        {
            'id': 'fasal-bima',
            'title': 'PM Fasal Bima Yojana',
            'text': 'Crop insurance scheme for farmers suffering crop loss.',
            'keywords': ['crop', 'insurance', 'farmer', 'loss'],
            'link': 'https://pmfby.gov.in',
            'benefit': 'Crop Loss Insurance',
            'ministry': 'Agriculture',
            'category': 'agriculture'
        }
    ]
    
    for scheme in sample_schemes:
        try:
            table.put_item(Item=scheme)
            print(f"✅ Added: {scheme['title']}")
        except Exception as e:
            print(f"❌ Error adding {scheme['title']}: {e}")
    
    return True

def test_bedrock_access():
    """Test Bedrock model access"""
    print("\n🤖 Testing Bedrock access...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with a simple prompt
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, respond with just 'Bedrock working!'"
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(payload)
        )
        
        result = json.loads(response['body'].read())
        print(f"✅ Bedrock response: {result['content'][0]['text']}")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock Error: {e}")
        return False

def test_polly_access():
    """Test Polly text-to-speech"""
    print("\n🗣️ Testing Polly access...")
    
    try:
        polly = boto3.client('polly', region_name='us-east-1')
        
        # Test synthesis
        response = polly.synthesize_speech(
            Text='JanSathi is working!',
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
        
        print("✅ Polly synthesis successful")
        return True
        
    except Exception as e:
        print(f"❌ Polly Error: {e}")
        return False

def main():
    """Run complete AWS setup"""
    print("🚀 JanSathi Complete AWS Setup")
    print("=" * 50)
    
    setup_steps = [
        ("IAM Permissions", setup_iam_permissions),
        ("S3 Bucket", setup_s3_bucket),
        ("DynamoDB Tables", setup_dynamodb_tables),
        ("Sample Data", populate_schemes_table),
        ("Bedrock Access", test_bedrock_access),
        ("Polly Access", test_polly_access)
    ]
    
    results = []
    
    for step_name, step_func in setup_steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            result = step_func()
            results.append((step_name, result))
            
            if result:
                print(f"✅ {step_name} completed successfully")
            else:
                print(f"❌ {step_name} failed")
                
        except Exception as e:
            print(f"❌ {step_name} error: {e}")
            results.append((step_name, False))
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 Setup Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"  {status} {step_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} steps completed")
    
    if passed == total:
        print("\n🎉 JanSathi AWS infrastructure is ready!")
        print("\n📝 Next steps:")
        print("  1. Update your .env with the created resources")
        print("  2. Test your application: python backend/main.py")
        print("  3. Monitor costs at: https://console.aws.amazon.com/billing")
    else:
        print("\n⚠️ Some steps failed. Check the errors above.")

if __name__ == "__main__":
    main()