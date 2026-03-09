#!/usr/bin/env python3
"""
Diagnose IAM permission issues for Lambda deployment
"""
import boto3
from botocore.exceptions import ClientError

def diagnose_permissions():
    """Diagnose current IAM permissions and identify issues"""
    
    # Get current user info
    sts = boto3.client('sts', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        identity = sts.get_caller_identity()
        user_arn = identity['Arn']
        username = user_arn.split('/')[-1]
        account_id = identity['Account']
        
        print(f"🔍 Current user: {username}")
        print(f"Account ID: {account_id}")
        print(f"User ARN: {user_arn}")
        
        # Check attached managed policies
        print("\n📋 Attached Managed Policies:")
        response = iam.list_attached_user_policies(UserName=username)
        
        quarantine_found = False
        
        for policy in response['AttachedPolicies']:
            policy_name = policy['PolicyName']
            policy_arn = policy['PolicyArn']
            
            print(f"  📄 {policy_name}")
            print(f"     ARN: {policy_arn}")
            
            # Check if it's the quarantine policy
            if 'Quarantine' in policy_name or 'quarantine' in policy_name.lower():
                print(f"     ⚠️ THIS IS THE PROBLEM POLICY!")
                print(f"     🚫 This policy blocks Lambda operations with explicit deny")
                quarantine_found = True
        
        # Check inline policies
        print("\n📋 Inline Policies:")
        response = iam.list_user_policies(UserName=username)
        
        for policy_name in response['PolicyNames']:
            print(f"  📄 {policy_name}")
            
            # Get policy document
            try:
                policy_doc = iam.get_user_policy(UserName=username, PolicyName=policy_name)
                policy_content = str(policy_doc['PolicyDocument'])
                if 'Deny' in policy_content and 'lambda' in policy_content.lower():
                    print(f"     ⚠️ This inline policy may contain Lambda denies")
                    quarantine_found = True
            except Exception as e:
                print(f"     Error reading policy: {e}")
        
        print(f"\n💡 Diagnosis:")
        if quarantine_found:
            print(f"❌ QUARANTINE POLICY DETECTED")
            print(f"   Your AWS access keys may have been flagged as compromised.")
            print(f"   AWS has applied a quarantine policy that blocks many operations.")
            print(f"\n🔧 Solutions:")
            print(f"1. Create new IAM user with fresh credentials:")
            print(f"   python ../scripts/create_new_iam_user.py")
            print(f"2. Or remove quarantine policy via AWS Console:")
            print(f"   - Go to IAM → Users → {username} → Permissions")
            print(f"   - Detach 'AWSCompromisedKeyQuarantineV3' policy")
            print(f"3. Update your .env file with new credentials")
        else:
            print(f"✅ No obvious quarantine policies found")
            print(f"   The issue may be insufficient Lambda permissions.")
            print(f"   Try attaching 'AWSLambdaFullAccess' policy to {username}")
        
        # Check if user has Lambda permissions
        print(f"\n🔍 Testing Lambda permissions...")
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        try:
            lambda_client.list_functions()
            print(f"✅ Can list Lambda functions")
        except ClientError as e:
            print(f"❌ Cannot list Lambda functions: {e}")
            
        return quarantine_found
        
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False

if __name__ == "__main__":
    print("🚀 JanSathi IAM Permission Diagnostic")
    print("=" * 50)
    diagnose_permissions()