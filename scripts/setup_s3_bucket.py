#!/usr/bin/env python3
"""
Create S3 bucket for JanSathi audio storage
"""
import boto3
import os
from botocore.exceptions import ClientError

def create_s3_bucket():
    """Create S3 bucket for audio storage"""
    
    bucket_name = os.getenv('S3_BUCKET_NAME', 'jansathi-audio-bucket-2024')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket {bucket_name} already exists")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == '404':
            # Bucket doesn't exist, create it
            print(f"🔄 Creating S3 bucket: {bucket_name}")
            
            try:
                if region == 'us-east-1':
                    # us-east-1 doesn't need LocationConstraint
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                
                # Set CORS for audio playback
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
                
                s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
                
                print(f"✅ S3 bucket {bucket_name} created successfully!")
                print(f"✅ CORS configured for audio playback")
                return True
                
            except ClientError as create_error:
                print(f"❌ Failed to create bucket: {create_error}")
                return False
        else:
            print(f"❌ Error checking bucket: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Setting up S3 bucket for JanSathi...")
    
    if create_s3_bucket():
        print("\n✅ S3 setup completed!")
    else:
        print("\n❌ S3 setup failed!")