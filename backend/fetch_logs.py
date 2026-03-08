import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_logs():
    client = boto3.client('logs', region_name='us-east-1')
    log_group = '/aws/lambda/jansathi-backend'
    
    # Get the latest log stream
    try:
        streams = client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not streams['logStreams']:
            print("No log streams found.")
            return
            
        stream_name = streams['logStreams'][0]['logStreamName']
        print(f"Latest log stream: {stream_name}\n")
        
        # Get log events
        response = client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            startFromHead=True
        )
        
        for event in response['events']:
            print(event['message'].strip())
            
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == "__main__":
    get_logs()
