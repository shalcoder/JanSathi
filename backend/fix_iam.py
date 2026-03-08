import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

def attach_dynamo_policy():
    iam = boto3.client('iam', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')

    function_name = 'jansathi-backend'
    try:
        config = lambda_client.get_function_configuration(FunctionName=function_name)
        role_arn = config['Role']
        role_name = role_arn.split('/')[-1]
        print(f"Role Name: {role_name}")
        
        policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
        print(f"Attaching {policy_arn} to role {role_name}...")
        
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    attach_dynamo_policy()
