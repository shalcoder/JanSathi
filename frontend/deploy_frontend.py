import boto3
import os
import time
import mimetypes
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def deploy_frontend():
    region = 'us-east-1'
    sts = boto3.client('sts', region_name=region)
    s3 = boto3.client('s3', region_name=region)
    cloudfront = boto3.client('cloudfront', region_name=region)

    # 1. Bucket Setup
    account_id = sts.get_caller_identity()['Account']
    # Use a unique bucket name that includes the timestamp or account ID
    bucket_name = f"jansathi-frontend-{account_id}-{int(time.time())}"
    
    print(f"Creating S3 Bucket: {bucket_name}...")
    try:
        s3.create_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Failed to create bucket: {e}")
        return

    # Disable Block Public Access to allow the public read policy
    print("Disabling Block Public Access...")
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )

    # Enable Static Website Hosting
    print("Enabling static website hosting...")
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'ErrorDocument': {'Key': 'index.html'},
            'IndexDocument': {'Suffix': 'index.html'}
        }
    )

    # Apply Public Read Policy
    print("Applying public read policy...")
    policy = '''{
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::%s/*"
        }]
    }''' % bucket_name
    
    time.sleep(2) # brief wait for block public access to apply
    s3.put_bucket_policy(Bucket=bucket_name, Policy=policy)

    # 2. Upload Files
    build_dir = "out"
    if not os.path.exists(build_dir):
        print("Error: 'out' directory not found. Did the build fail?")
        return
        
    print("Uploading files to S3...")
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            local_path = os.path.join(root, file)
            # relative path for S3 key
            s3_key = os.path.relpath(local_path, build_dir).replace('\\', '/')
            
            # Guess content type
            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                if s3_key.endswith('.css'):
                    content_type = 'text/css'
                elif s3_key.endswith('.js'):
                    content_type = 'application/javascript'
                elif s3_key.endswith('.html'):
                    content_type = 'text/html'
                else:
                    content_type = 'binary/octet-stream'
                    
            print(f"  Uploading {s3_key}...")
            s3.upload_file(
                local_path, 
                bucket_name, 
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )

    website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
    print(f"\nS3 Website Endpoint: {website_url}")

    # 3. Create CloudFront Distribution
    print("\nCreating CloudFront Distribution...")
    origin_id = f"S3-{bucket_name}"
    origin_domain = f"{bucket_name}.s3-website-{region}.amazonaws.com"
    
    distribution_config = {
        'CallerReference': str(time.time()),
        'Origins': {
            'Quantity': 1,
            'Items': [{
                'Id': origin_id,
                'DomainName': origin_domain,
                'CustomOriginConfig': {
                    'HTTPPort': 80,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'http-only',
                    'OriginSslProtocols': {'Quantity': 1, 'Items': ['TLSv1.2']}
                }
            }]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': origin_id,
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {'Quantity': 2, 'Items': ['HEAD', 'GET'], 'CachedMethods': {'Quantity': 2, 'Items': ['HEAD', 'GET']}},
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'MinTTL': 0,
            'DefaultTTL': 86400,
            'MaxTTL': 31536000
        },
        'CustomErrorResponses': {
            'Quantity': 2,
            'Items': [
                {
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 0
                },
                {
                    'ErrorCode': 403,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 0
                }
            ]
        },
        'Comment': 'JanSathi Frontend Distribution',
        'Enabled': True,
        'DefaultRootObject': 'index.html'
    }
    
    try:
        cf_response = cloudfront.create_distribution(DistributionConfig=distribution_config)
        cf_domain = cf_response['Distribution']['DomainName']
        print(f"\nCloudFront Domain: https://{cf_domain}")
    except Exception as e:
        print(f"Failed to create CloudFront distribution: {e}")

    print("\n" + "="*50)
    print("DEPLOYMENT SUCCESSFUL")
    print(f"S3 URL: {website_url}")
    print("="*50)

if __name__ == "__main__":
    deploy_frontend()
