#!/usr/bin/env python3
"""
Setup CloudWatch Dashboard for JanSathi monitoring
"""
import boto3
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')

def create_cloudwatch_dashboard():
    """Create CloudWatch dashboard for JanSathi"""
    
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "jansathi-conversations"],
                        [".", "ConsumedWriteCapacityUnits", ".", "."],
                        [".", "ConsumedReadCapacityUnits", "TableName", "jansathi-schemes"],
                        [".", "ConsumedWriteCapacityUnits", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "DynamoDB Usage",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/S3", "BucketSizeBytes", "BucketName", "jansathi-audio-bucket-1770462916", "StorageType", "StandardStorage"],
                        [".", "NumberOfObjects", ".", ".", ".", "AllStorageTypes"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "S3 Storage Usage",
                    "period": 86400
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Polly", "RequestCharacters", "Operation", "SynthesizeSpeech"],
                        [".", "ResponseTime", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "Polly Text-to-Speech Usage",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Bedrock", "Invocations", "ModelId", "anthropic.claude-3-haiku-20240307-v1:0"],
                        [".", "InputTokens", ".", "."],
                        [".", "OutputTokens", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "Bedrock AI Usage",
                    "period": 300
                }
            },
            {
                "type": "log",
                "x": 0,
                "y": 12,
                "width": 24,
                "height": 6,
                "properties": {
                    "query": "SOURCE '/aws/lambda/jansathi-backend'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 100",
                    "region": "us-east-1",
                    "title": "Error Logs",
                    "view": "table"
                }
            }
        ]
    }
    
    try:
        print("🔄 Creating CloudWatch Dashboard...")
        
        response = cloudwatch.put_dashboard(
            DashboardName='JanSathi-Monitoring',
            DashboardBody=json.dumps(dashboard_body)
        )
        
        dashboard_url = f"https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=JanSathi-Monitoring"
        
        print("SUCCESS: CloudWatch Dashboard created successfully!")
        print(f"Dashboard URL: {dashboard_url}")
        
        return dashboard_url
        
    except Exception as e:
        print(f"ERROR: CloudWatch Dashboard setup failed: {e}")
        return None

def create_cloudwatch_alarms():
    """Create CloudWatch alarms for monitoring"""
    
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    
    alarms = [
        {
            'AlarmName': 'JanSathi-DynamoDB-HighReadCapacity',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 2,
            'MetricName': 'ConsumedReadCapacityUnits',
            'Namespace': 'AWS/DynamoDB',
            'Period': 300,
            'Statistic': 'Sum',
            'Threshold': 100.0,
            'ActionsEnabled': True,
            'AlarmDescription': 'High DynamoDB read capacity usage',
            'Dimensions': [
                {
                    'Name': 'TableName',
                    'Value': 'jansathi-conversations'
                }
            ]
        },
        {
            'AlarmName': 'JanSathi-S3-HighStorageUsage',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 1,
            'MetricName': 'BucketSizeBytes',
            'Namespace': 'AWS/S3',
            'Period': 86400,
            'Statistic': 'Average',
            'Threshold': 1000000000.0,  # 1GB
            'ActionsEnabled': True,
            'AlarmDescription': 'High S3 storage usage (>1GB)',
            'Dimensions': [
                {
                    'Name': 'BucketName',
                    'Value': 'jansathi-audio-bucket-1770462916'
                },
                {
                    'Name': 'StorageType',
                    'Value': 'StandardStorage'
                }
            ]
        }
    ]
    
    try:
        print("🔄 Creating CloudWatch Alarms...")
        
        for alarm in alarms:
            cloudwatch.put_metric_alarm(**alarm)
            print(f"SUCCESS: Created alarm: {alarm['AlarmName']}")
        
        print("SUCCESS: All CloudWatch alarms created!")
        
    except Exception as e:
        print(f"ERROR: CloudWatch alarms setup failed: {e}")

if __name__ == "__main__":
    print("Setting up CloudWatch Dashboard and Alarms...")
    create_cloudwatch_dashboard()
    create_cloudwatch_alarms()