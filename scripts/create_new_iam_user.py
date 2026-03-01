#!/usr/bin/env python3
"""
Create a new IAM user for JanSathi with proper permissions
"""
import boto3
import json
from botocore.exceptions import ClientError

def create_iam_user():
    """Create new IAM user with Bedrock permissions"""
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    username = 'jansathi-bedrock-user'
    
    try:
        # Create user
        print(f"🔄 Creating IAM user: {username}")
        iam.create_user(UserName=username)
        print(f"✅ Created user: {username}")
        
        # Attach policies
        policies = [
            'AmazonBedrockFullAccess',
            'AmazonPollyFullAccess', 
            'AmazonTranscribeFullAccess',
            'AmazonS3FullAccess',
            'AmazonDynamoDBFullAccess'
        ]
        
        for policy in policies:
            try:
                iam.attach_user_policy(
                    UserName=username,
                    PolicyArn=f'arn:aws:iam::aws:policy/{policy}'
                )
                print(f"✅ Attached policy: {policy}")
            except Exception as e:
                print(f"⚠️ Could not attach {policy}: {e}")
        
        # Create access key
        print("🔄 Creating access keys...")
        response = iam.create_access_key(UserName=username)
        
        access_key = response['AccessKey']
        
        print("\n🎉 New IAM User Created Successfully!")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Access Key ID: {access_key['AccessKeyId']}")
        print(f"Secret Access Key: {access_key['SecretAccessKey']}")
        print("=" * 50)
        
        print("\n📝 Update your .env file:")
        print(f"AWS_ACCESS_KEY_ID={access_key['AccessKeyId']}")
        print(f"AWS_SECRET_ACCESS_KEY={access_key['SecretAccessKey']}")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"✅ User {username} already exists")
            return True
        else:
            print(f"❌ Error creating user: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Creating New IAM User for Bedrock Access")
    print("=" * 50)
    
    if create_iam_user():
        print("\n✅ Setup complete! Update your .env file with the new credentials.")
    else:
        print("\n❌ Setup failed!")