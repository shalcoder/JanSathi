import boto3
import os
import time
import mimetypes
from urllib.parse import urlparse
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'), override=False)


def _extract_api_domain() -> str | None:
    """Read API URL from env and return host part (for CloudFront origin)."""
    api_url = os.getenv("NEXT_PUBLIC_API_URL", "").strip()
    if not api_url:
        return None
    parsed = urlparse(api_url)
    return parsed.netloc or None


def _ensure_cloudfront_api_routing(cloudfront, dist_id: str, api_domain: str) -> bool:
    """Attach API Gateway as CloudFront origin and map API paths to it."""
    api_origin_id = "jansathi-api-gateway-origin"
    changed = False

    config_resp = cloudfront.get_distribution_config(Id=dist_id)
    etag = config_resp["ETag"]
    config = config_resp["DistributionConfig"]

    origins = config["Origins"]["Items"]
    origin_exists = any(o["Id"] == api_origin_id for o in origins)
    if not origin_exists:
        origins.append(
            {
                "Id": api_origin_id,
                "DomainName": api_domain,
                "OriginPath": "",
                "CustomHeaders": {"Quantity": 0},
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "https-only",
                    "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
                    "OriginReadTimeout": 30,
                    "OriginKeepaliveTimeout": 5,
                },
                "ConnectionAttempts": 3,
                "ConnectionTimeout": 10,
                "OriginShield": {"Enabled": False},
            }
        )
        config["Origins"]["Quantity"] = len(origins)
        changed = True

    existing_behaviors = config.get("CacheBehaviors", {}).get("Items", [])
    existing_patterns = {b.get("PathPattern") for b in existing_behaviors}

    api_patterns = ["/v1/*", "/health*"]
    for pattern in api_patterns:
        if pattern in existing_patterns:
            continue

        existing_behaviors.append(
            {
                "PathPattern": pattern,
                "TargetOriginId": api_origin_id,
                "TrustedSigners": {"Enabled": False, "Quantity": 0},
                "TrustedKeyGroups": {"Enabled": False, "Quantity": 0},
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 7,
                    "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
                    "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                },
                "SmoothStreaming": False,
                "Compress": True,
                "LambdaFunctionAssociations": {"Quantity": 0},
                "FunctionAssociations": {"Quantity": 0},
                "FieldLevelEncryptionId": "",
                # Disable cache for dynamic API traffic.
                "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                # Forward auth/query/cookies required by API Gateway and JWT-protected routes.
                "OriginRequestPolicyId": "b689b0a8-53d0-40ab-baf2-68738e2966ac",
                "GrpcConfig": {"Enabled": False},
            }
        )
        changed = True

    if not changed:
        print("CloudFront API routing already configured.")
        return False

    config["CacheBehaviors"] = {
        "Quantity": len(existing_behaviors),
        "Items": existing_behaviors,
    }

    cloudfront.update_distribution(
        Id=dist_id,
        IfMatch=etag,
        DistributionConfig=config,
    )
    print("Updated CloudFront distribution with API Gateway origin and API path behaviors.")
    return True

def deploy_frontend():
    region = 'us-east-1'
    sts = boto3.client('sts', region_name=region)
    s3 = boto3.client('s3', region_name=region)
    cloudfront = boto3.client('cloudfront', region_name=region)

    # 1. Bucket Setup
    try:
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        print(f"Logged in as: {identity['Arn']}")
    except Exception as e:
        print(f"Failed to get AWS identity. Check your credentials: {e}")
        return

    # Use a stable bucket name by default; override with existing CloudFront origin bucket when available.
    bucket_name = f"jansathi-frontend-{account_id}-prod"

    existing_dist_id = None
    existing_cf_domain = None
    try:
        dists = cloudfront.list_distributions().get('DistributionList', {}).get('Items', [])
        for d in dists:
            if 'JanSathi' in d.get('Comment', ''):
                existing_dist_id = d['Id']
                existing_cf_domain = d['DomainName']
                cfg = cloudfront.get_distribution(Id=existing_dist_id)['Distribution']['DistributionConfig']
                origin_domain = cfg['Origins']['Items'][0]['DomainName']
                if '.s3-website-' in origin_domain:
                    bucket_name = origin_domain.split('.s3-website-')[0]
                elif '.s3.' in origin_domain:
                    bucket_name = origin_domain.split('.s3.')[0]
                print(f"Found existing distribution: {existing_dist_id} ({existing_cf_domain})")
                print(f"Using CloudFront origin bucket: {bucket_name}")
                break
    except ClientError as e:
        print(f"Could not inspect CloudFront distribution origin (AccessDenied). Using default bucket {bucket_name}.")
    
    print(f"Targeting S3 Bucket: {bucket_name}...")
    
    # Try to create bucket (might fail due to permissions, which is fine if it exists)
    try:
        s3.create_bucket(Bucket=bucket_name)
        print("Successfully created bucket.")
    except ClientError as e:
        code = e.response['Error']['Code']
        if code in ('BucketAlreadyOwnedByYou', 'BucketAlreadyExists'):
            print("Bucket already exists.")
        elif code == 'AccessDenied':
            print("AccessDenied for CreateBucket. Verifying bucket exists...")
            try:
                s3.head_bucket(Bucket=bucket_name)
                print("Bucket confirmed to exist and is accessible.")
            except ClientError as head_err:
                head_code = head_err.response['Error']['Code']
                if head_code in ('404', 'NoSuchBucket', 'NoSuchKey'):
                    print(f"\nERROR: Bucket '{bucket_name}' does not exist and could not be created (AccessDenied).")
                    print("Fix one of the following:")
                    print("  1. Attach 's3:CreateBucket' permission to the jansathi-app IAM user, OR")
                    print("  2. Create the bucket manually via AWS CLI:")
                    print(f"       aws s3 mb s3://{bucket_name} --region {region}")
                    return
                else:
                    print(f"  Warning: Could not verify bucket ({head_code}). Proceeding anyway...")
        else:
            print(f"S3 Error: {e}")

    # Best-effort bucket configuration
    configs = [
        ("Public Access Block", lambda: s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False, 'IgnorePublicAcls': False,
                'BlockPublicPolicy': False, 'RestrictPublicBuckets': False
            }
        )),
        ("Website Hosting", lambda: s3.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'ErrorDocument': {'Key': 'index.html'},
                'IndexDocument': {'Suffix': 'index.html'}
            }
        )),
        ("Public Read Policy", lambda: s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy='''{
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::%s/*"
                }]
            }''' % bucket_name
        ))
    ]

    for name, func in configs:
        try:
            print(f"Configuring {name}...")
            func()
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print(f"  Skipped {name} (AccessDenied).")
            else:
                print(f"  Failed {name}: {e}")

    # 2. Upload Files
    build_dir = "out"
    if not os.path.exists(build_dir):
        print(f"Error: '{build_dir}' directory not found. Please run 'npm run build' first.")
        return
        
    print(f"Uploading files from '{build_dir}' to S3...")
    upload_count = 0
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_path, build_dir).replace('\\', '/')
            
            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                if s3_key.endswith('.css'): content_type = 'text/css'
                elif s3_key.endswith('.js'): content_type = 'application/javascript'
                elif s3_key.endswith('.html'): content_type = 'text/html'
                else: content_type = 'binary/octet-stream'
            
            try:
                s3.upload_file(
                    local_path, bucket_name, s3_key,
                    ExtraArgs={'ContentType': content_type}
                )
                upload_count += 1
            except Exception as e:
                print(f"  Failed to upload {s3_key}: {e}")

    print(f"Successfully uploaded {upload_count} files.")
    website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"

    # 3. CloudFront Check/Update
    print("\nChecking for existing CloudFront distributions...")
    dist_id = existing_dist_id
    cf_domain = existing_cf_domain
    
    try:
        if not dist_id:
            dists = cloudfront.list_distributions().get('DistributionList', {}).get('Items', [])
            for d in dists:
                if 'JanSathi' in d.get('Comment', ''):
                    dist_id = d['Id']
                    cf_domain = d['DomainName']
                    print(f"Found existing distribution: {dist_id} ({cf_domain})")
                    break
    except ClientError as e:
        print(f"Could not list distributions (AccessDenied). Proceeding with S3 URL.")

    if not dist_id:
        print("No existing JanSathi distribution found. You may need to create one manually if permissions are limited.")
    else:
        api_domain = _extract_api_domain()
        if api_domain:
            try:
                _ensure_cloudfront_api_routing(cloudfront, dist_id, api_domain)
            except Exception as e:
                print(f"CloudFront API routing update failed: {e}")
        else:
            print("NEXT_PUBLIC_API_URL not set; skipping CloudFront API routing setup.")

        # Optionally invalidate cache
        try:
            print(f"Invalidating CloudFront cache for {dist_id}...")
            cloudfront.create_invalidation(
                DistributionId=dist_id,
                InvalidationBatch={
                    'Paths': {'Quantity': 1, 'Items': ['/*']},
                    'CallerReference': str(time.time())
                }
            )
            print("Invalidation submitted.")
        except Exception as e:
            print(f"Invalidation failed: {e}")

    print("\n" + "="*50)
    print("DEPLOYMENT ATTEMPT COMPLETE")
    print(f"S3 Endpoint: {website_url}")
    if cf_domain:
        print(f"CloudFront:  https://{cf_domain}")
    print("="*50)

if __name__ == "__main__":
    deploy_frontend()
