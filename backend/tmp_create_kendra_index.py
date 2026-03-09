import json
import os

import boto3
from dotenv import load_dotenv


def find_existing_index(kendra_client, index_name: str):
    next_token = None
    while True:
        kwargs = {"MaxResults": 100}
        if next_token:
            kwargs["NextToken"] = next_token
        resp = kendra_client.list_indices(**kwargs)
        for item in resp.get("IndexConfigurationSummaryItems", []):
            if item.get("Name") == index_name and item.get("Status") != "DELETING":
                return item
        next_token = resp.get("NextToken")
        if not next_token:
            return None


def ensure_kendra_role(iam_client):
    roles = iam_client.list_roles(MaxItems=1000).get("Roles", [])
    for role in roles:
        trust = json.dumps(role.get("AssumeRolePolicyDocument", {}))
        if "kendra.amazonaws.com" in trust:
            return role["Arn"], role["RoleName"], False

    role_name = "JanSathiKendraServiceRole"
    assume = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "kendra.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    created = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume),
        Description="Service role for JanSathi Kendra index",
    )

    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
    )

    s3_read_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": ["arn:aws:s3:::*", "arn:aws:s3:::*/*"],
            }
        ],
    }
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName="JanSathiKendraS3Read",
        PolicyDocument=json.dumps(s3_read_policy),
    )

    return created["Role"]["Arn"], role_name, True


def main():
    load_dotenv()
    region = os.getenv("AWS_REGION", "us-east-1")
    index_name = "JanSathi-GovernmentSchemes"

    sts = boto3.client("sts", region_name=region)
    ident = sts.get_caller_identity()

    iam = boto3.client("iam", region_name=region)
    kendra = boto3.client("kendra", region_name=region)

    existing = find_existing_index(kendra, index_name)
    if existing:
        print(
            json.dumps(
                {
                    "action": "reuse",
                    "region": region,
                    "account": ident["Account"],
                    "index_name": index_name,
                    "index_id": existing["Id"],
                    "status": existing.get("Status"),
                }
            )
        )
        return

    role_arn, role_name, role_created = ensure_kendra_role(iam)

    created = kendra.create_index(
        Name=index_name,
        Description="Search index for JanSathi government schemes",
        RoleArn=role_arn,
        Edition="DEVELOPER_EDITION",
    )

    print(
        json.dumps(
            {
                "action": "create",
                "region": region,
                "account": ident["Account"],
                "index_name": index_name,
                "index_id": created["Id"],
                "status": "CREATING",
                "role_arn": role_arn,
                "role_name": role_name,
                "role_created": role_created,
            }
        )
    )


if __name__ == "__main__":
    main()
