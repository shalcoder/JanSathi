"""
AWS Amplify setup script.
Creates an Amplify app connected to your GitHub repo.

Usage:
    python setup_amplify.py --repo https://github.com/YOUR_USER/YOUR_REPO --token ghp_YOUR_GITHUB_TOKEN
"""
import argparse
import json
import os
import sys
import boto3
from dotenv import load_dotenv

load_dotenv("backend/.env")

REGION = os.getenv("AWS_REGION", "us-east-1")
APP_NAME = "jansathi"

ENV_VARS = {
    "NEXT_PUBLIC_API_URL":                "https://b0z0h6knui.execute-api.us-east-1.amazonaws.com",
    "NEXT_PUBLIC_COGNITO_USER_POOL_ID":   os.getenv("NEXT_PUBLIC_COGNITO_USER_POOL_ID", "us-east-1_1pTnubRdF"),
    "NEXT_PUBLIC_COGNITO_CLIENT_ID":      os.getenv("NEXT_PUBLIC_COGNITO_CLIENT_ID", "55v7jr26s29o947tdj5292q4sp"),
    "NEXT_PUBLIC_AWS_REGION":             "us-east-1",
}


def main():
    parser = argparse.ArgumentParser(description="Set up AWS Amplify for JanSathi frontend")
    parser.add_argument("--repo",  required=True, help="GitHub repo URL, e.g. https://github.com/user/repo")
    parser.add_argument("--token", required=True, help="GitHub personal access token (needs repo scope)")
    parser.add_argument("--branch", default="main", help="Branch to deploy (default: main)")
    args = parser.parse_args()

    client = boto3.client("amplify", region_name=REGION)

    # ── 1. Create the Amplify app ──────────────────────────────────────────────
    print(f"Creating Amplify app '{APP_NAME}'...")
    app = client.create_app(
        name=APP_NAME,
        repository=args.repo,
        accessToken=args.token,
        platform="WEB_COMPUTE",           # SSR / Next.js
        buildSpec=open("amplify.yml").read(),
        environmentVariables=ENV_VARS,
        enableBranchAutoBuild=True,
        enableBranchAutoDeletion=False,
    )
    app_id   = app["app"]["appId"]
    app_url  = app["app"]["defaultDomain"]
    print(f"  App ID : {app_id}")
    print(f"  Domain : https://{args.branch}.{app_url}")

    # ── 2. Create the branch ───────────────────────────────────────────────────
    print(f"Creating branch '{args.branch}'...")
    client.create_branch(
        appId=app_id,
        branchName=args.branch,
        framework="Next.js - SSR",
        stage="PRODUCTION",
        enableAutoBuild=True,
        environmentVariables=ENV_VARS,
    )

    # ── 3. Trigger first build ─────────────────────────────────────────────────
    print("Triggering first build...")
    job = client.start_job(appId=app_id, branchName=args.branch, jobType="RELEASE")
    print(f"  Job ID : {job['jobSummary']['jobId']} (status: {job['jobSummary']['status']})")

    print()
    print("Done! Your CI/CD pipeline is live:")
    print(f"  GitHub push → Amplify auto-build → https://{args.branch}.{app_url}")
    print()
    print("Check build progress:")
    print(f"  https://{REGION}.console.aws.amazon.com/amplify/home#/{app_id}/{args.branch}")


if __name__ == "__main__":
    main()
