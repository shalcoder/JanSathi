import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def setup_cognito():
    region = 'us-east-1'
    cognito = boto3.client('cognito-idp', region_name=region)
    pool_name = 'jansathi_users'
    
    # 1. Check if pool exists
    existing_pools = cognito.list_user_pools(MaxResults=50)
    pool_id = None
    for pool in existing_pools.get('UserPools', []):
        if pool['Name'] == pool_name:
            pool_id = pool['Id']
            print(f"Found existing User Pool: {pool_id}")
            break
            
    # 2. Create pool if it doesn't exist
    if not pool_id:
        print(f"Creating new User Pool: {pool_name}...")
        response = cognito.create_user_pool(
            PoolName=pool_name,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': False
                }
            },
            AutoVerifiedAttributes=['email'],
            UsernameAttributes=['email'],
            MfaConfiguration='OFF'
        )
        pool_id = response['UserPool']['Id']
        print(f"Created User Pool: {pool_id}")

    # 3. Create App Client
    client_name = 'jansathi_web_client'
    existing_clients = cognito.list_user_pool_clients(UserPoolId=pool_id, MaxResults=50)
    client_id = None
    for client in existing_clients.get('UserPoolClients', []):
        if client['ClientName'] == client_name:
            client_id = client['ClientId']
            print(f"Found existing App Client: {client_id}")
            break
            
    if not client_id:
        print(f"Creating new App Client: {client_name}...")
        response = cognito.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName=client_name,
            GenerateSecret=False, # Web clients cannot use secrets
            ExplicitAuthFlows=[
                'ALLOW_USER_SRP_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
                'ALLOW_USER_PASSWORD_AUTH'
            ],
            PreventUserExistenceErrors='ENABLED'
        )
        client_id = response['UserPoolClient']['ClientId']
        print(f"Created App Client: {client_id}")

    # 4. Save to .env.local
    env_file = '.env.local'
    env_content = ""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
            
    new_vars = {
        'NEXT_PUBLIC_COGNITO_USER_POOL_ID': pool_id,
        'NEXT_PUBLIC_COGNITO_CLIENT_ID': client_id,
        'NEXT_PUBLIC_AWS_REGION': region
    }
    
    # Update or append
    lines = env_content.splitlines()
    final_lines = []
    
    for line in lines:
        assigned = False
        for key in new_vars.keys():
            if line.startswith(f"{key}="):
                final_lines.append(f"{key}={new_vars[key]}")
                assigned = True
                break
        if not assigned:
            final_lines.append(line)
            
    for key, val in new_vars.items():
        if not any(l.startswith(f"{key}=") for l in final_lines):
            final_lines.append(f"{key}={val}")
            
    with open(env_file, 'w') as f:
        f.write('\n'.join(final_lines) + '\n')
        
    print(f"\nSuccessfully stored Cognito Config in {env_file}")
    print(f"User Pool ID: {pool_id}")
    print(f"Client ID: {client_id}")

if __name__ == "__main__":
    setup_cognito()
