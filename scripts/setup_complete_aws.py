#!/usr/bin/env python3
"""
Complete AWS infrastructure setup for JanSathi
Implements all missing services
"""
import boto3
import json
import time
import subprocess
import sys
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

def main():
    """Run complete AWS setup"""
    
    print("JanSathi Complete AWS Infrastructure Setup")
    print("=" * 60)
    
    setup_scripts = [
        ("API Gateway", "setup_api_gateway.py"),
        ("CloudWatch Dashboard", "setup_cloudwatch.py"),
        ("SQS for HITL", "setup_sqs_hitl.py"),
        ("Step Functions", "setup_step_functions.py"),
        ("Amazon Connect", "setup_amazon_connect.py")
    ]
    
    print("Services to be implemented:")
    for i, (name, _) in enumerate(setup_scripts, 1):
        print(f"  {i}. {name}")
    
    print("\nIMPORTANT NOTES:")
    print("- This will create AWS resources that may incur costs")
    print("- Some services require manual configuration")
    print("- Ensure you have proper IAM permissions")
    
    response = input("\nProceed with setup? (y/N): ")
    
    if response.lower() != 'y':
        print("Setup cancelled.")
        return
    
    results = []
    
    for service_name, script_name in setup_scripts:
        print(f"\n{'='*20} {service_name} {'='*20}")
        
        try:
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"SUCCESS: {service_name} setup completed")
                results.append((service_name, True))
            else:
                print(f"FAILED: {service_name} setup failed")
                print(f"Error: {result.stderr}")
                results.append((service_name, False))
                
        except Exception as e:
            print(f"ERROR: {service_name} setup error: {e}")
            results.append((service_name, False))
    
    # Final summary
    print("\n" + "=" * 60)
    print("Complete Setup Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for service_name, result in results:
        status = "SUCCESS" if result else "FAILED"
        print(f"  {status} {service_name}")
    
    print(f"\nOverall: {passed}/{total} services implemented")
    
    if passed == total:
        print("\nAll AWS services implemented successfully!")
        print("\nArchitecture Summary:")
        print("Core Services:")
        print("  - DynamoDB (conversations, schemes, users)")
        print("  - S3 (audio storage)")
        print("  - Polly (text-to-speech)")
        print("  - Bedrock (AI responses)")
        print("\nProduction Services:")
        print("  - API Gateway (REST API)")
        print("  - CloudWatch (monitoring & alarms)")
        print("  - SQS (human-in-the-loop)")
        print("  - Step Functions (workflow orchestration)")
        print("  - Amazon Connect (voice interface)")
        print("\nYour JanSathi is now enterprise-ready!")
        
    else:
        print(f"\n{total - passed} services need attention.")
        print("Check the error messages above and retry failed services.")
    
    print(f"\nCost Monitoring:")
    print("- Set up billing alerts in AWS Console")
    print("- Monitor usage in CloudWatch dashboard")
    print("- Most services have free tier limits")

if __name__ == "__main__":
    main()