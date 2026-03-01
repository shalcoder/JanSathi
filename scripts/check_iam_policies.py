#!/usr/bin/env python3
"""
Check current IAM policies for jansathi-app user
"""
import boto3
from dotenv import load_dotenv

load_dotenv('backend/.env')

def check_user_policies():
    """Check what policies are attached to the user"""
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    # Get current user info
    sts = boto3.client('sts', region_name='us-east-1')
    identity = sts.get_caller_identity()
    
    # Extract username from ARN
    user_arn = identity['Arn']
    username = user_arn.split('/')[-1]
    
    print(f"🔍 Checking policies for user: {username}")
    print(f"User ARN: {user_arn}")
    
    try:
        # List attached managed policies
        print("\n📋 Attached Managed Policies:")
        response = iam.list_attached_user_policies(UserName=username)
        
        for policy in response['AttachedPolicies']:
            policy_name = policy['PolicyName']
            policy_arn = policy['PolicyArn']
            
            print(f"  📄 {policy_name}")
            print(f"     ARN: {policy_arn}")
            
            # Check if it's the quarantine policy
            if 'Quarantine' in policy_name:
                print(f"     ⚠️ THIS IS THE PROBLEM POLICY!")
                print(f"     🔧 Remove this policy to fix Bedrock access")
        
        # List inline policies
        print("\n📋 Inline Policies:")
        response = iam.list_user_policies(UserName=username)
        
        for policy_name in response['PolicyNames']:
            print(f"  📄 {policy_name}")
        
        print(f"\n💡 To fix Bedrock access:")
        print(f"1. Go to AWS Console → IAM → Users → {username}")
        print(f"2. Permissions tab")
        print(f"3. Find 'AWSCompromisedKeyQuarantineV3' policy")
        print(f"4. Click 'Detach' to remove it")
        print(f"5. Test Bedrock again")
        
    except Exception as e:
        print(f"❌ Error checking policies: {e}")

if __name__ == "__main__":
    check_user_policies()