import boto3
import time
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def create_table():
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    table_name = 'JanSathiSessions'
    
    print(f"Checking if {table_name} exists...")
    try:
        dynamodb.describe_table(TableName=table_name)
        print(f"Table {table_name} already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Creating table {table_name}...")
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'session_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'session_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print("Waiting for table to be active...")
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"Table {table_name} created successfully.")
            
            print("Enabling TTL on 'expires_at' attribute...")
            dynamodb.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'expires_at'
                }
            )
            print("TTL enabled.")
        else:
            print(f"Error checking table: {e}")

if __name__ == "__main__":
    create_table()
