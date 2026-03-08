import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def deploy_lambda():
    print("Starting deployment via boto3...")
    
    region = 'us-east-1'
    # Initialize clients
    sts = boto3.client('sts', region_name=region)
    s3 = boto3.client('s3', region_name=region)
    lambda_client = boto3.client('lambda', region_name=region)
    apigw = boto3.client('apigatewayv2', region_name=region)
    
    # 1. Get Account ID and Setup Bucket
    try:
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        print(f"Logged in as Account: {account_id}")
    except Exception as e:
        print(f"Failed to get AWS credentials: {e}")
        return

    bucket_name = f"jansathi-lambda-deploy-{account_id}"
    
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"Creating bucket {bucket_name}...")
            # For us-east-1, LocationConstraint is not needed/allowed
            s3.create_bucket(Bucket=bucket_name)
        else:
            print(f"Error checking bucket: {e}")

    # 2. Upload ZIP to S3
    zip_file = "function-minimal.zip"
    if not os.path.exists(zip_file):
        print(f"Error: {zip_file} not found. Run create_minimal_package.py first.")
        return
        
    print(f"Uploading {zip_file} to s3://{bucket_name}/{zip_file}...")
    s3.upload_file(zip_file, bucket_name, zip_file)
    print("Upload complete.")

    # 3. Update or Create Lambda Function
    function_name = "jansathi-backend"
    
    try:
        lambda_client.get_function(FunctionName=function_name)
        func_exists = True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            func_exists = False
        else:
            print(f"Error checking function: {e}")
            return

    if func_exists:
        print(f"Updating existing Lambda function {function_name} code...")
        lambda_client.update_function_code(
            FunctionName=function_name,
            S3Bucket=bucket_name,
            S3Key=zip_file
        )
        print("Waiting for function update to complete...")
        waiter = lambda_client.get_waiter('function_updated_v2')
        waiter.wait(FunctionName=function_name)
        
        print("Updating Lambda configuration...")
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': {'USE_DYNAMODB': 'true', 'NODE_ENV': 'production', 'STORAGE_TYPE': 'dynamodb'}},
            Timeout=60,
            MemorySize=1024
        )
    else:
        print(f"Function {function_name} does not exist. Please create an IAM role first, or the guide assumed it was pre-created.")
        # We could try to create it, but we need an IAM role ARN.
        # Let's see if there is an existing role we can use. Give up if not
        iam = boto3.client('iam')
        try:
            roles = iam.list_roles()['Roles']
            # Look for a role name with lambda or jansathi
            role_arn = None
            for r in roles:
                if 'jansathi' in r['RoleName'].lower() or 'lambda' in r['RoleName'].lower():
                    role_arn = r['Arn']
                    break
            if not role_arn:
                print("Could not find suitable execution role for Lambda. Cannot create function.")
                return
            
            print(f"Creating new Lambda function {function_name} with role {role_arn}...")
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=role_arn,
                Handler='lambda_handler.lambda_handler',
                Code={'S3Bucket': bucket_name, 'S3Key': zip_file},
                Timeout=60,
                MemorySize=1024,
                Environment={'Variables': {'USE_DYNAMODB': 'true', 'NODE_ENV': 'production', 'STORAGE_TYPE': 'dynamodb'}}
            )
        except Exception as e:
            print(f"Failed to create function: {e}")
            return
            
    # 4. API Gateway Setup
    print("Checking for existing API Gateway...")
    apis = apigw.get_apis()['Items']
    api_id = None
    for api in apis:
        if api['Name'] == 'jansathi-api':
            api_id = api['ApiId']
            break
            
    if api_id:
        print(f"Found existing API Gateway: {api_id}")
    else:
        print("Creating new HTTP API Gateway...")
        func_info = lambda_client.get_function(FunctionName=function_name)
        func_arn = func_info['Configuration']['FunctionArn']
        
        response = apigw.create_api(
            Name='jansathi-api',
            ProtocolType='HTTP',
            Target=func_arn
        )
        api_id = response['ApiId']
        print(f"Created new API Gateway: {api_id}")
        
        print("Adding permission to Lambda...")
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='apigateway-invoke-deploy',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*"
            )
        except ClientError as e:
            if 'ResourceConflictException' not in str(e):
                print(f"Error adding permission: {e}")

    api_endpoint = f"https://{api_id}.execute-api.{region}.amazonaws.com"
    print("\n" + "="*50)
    print(f"DEPLOYMENT SUCCESSFUL")
    print(f"API Endpoint: {api_endpoint}")
    print("="*50 + "\n")

    # Update frontend env
    frontend_env = os.path.join("..", "frontend", ".env.local")
    if os.path.exists(frontend_env):
        with open(frontend_env, "r") as f:
            lines = f.readlines()
        with open(frontend_env, "w") as f:
            for line in lines:
                if line.startswith("NEXT_PUBLIC_API_URL="):
                    f.write(f"NEXT_PUBLIC_API_URL={api_endpoint}\n")
                else:
                    f.write(line)
        print(f"Updated {frontend_env} with new API URL")

if __name__ == "__main__":
    deploy_lambda()
