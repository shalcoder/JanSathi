#!/usr/bin/env python3
"""
Setup SQS for Human-in-the-Loop (HITL) processing
"""
import boto3
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')

def create_sqs_queues():
    """Create SQS queues for HITL workflow"""
    
    sqs = boto3.client('sqs', region_name='us-east-1')
    
    queues_config = [
        {
            'name': 'jansathi-hitl-requests',
            'attributes': {
                'DelaySeconds': '0',
                'MaxReceiveCount': '3',
                'MessageRetentionPeriod': '1209600',  # 14 days
                'VisibilityTimeoutSeconds': '300'
            },
            'description': 'Queue for requests requiring human review'
        },
        {
            'name': 'jansathi-hitl-responses',
            'attributes': {
                'DelaySeconds': '0',
                'MaxReceiveCount': '3',
                'MessageRetentionPeriod': '1209600',  # 14 days
                'VisibilityTimeoutSeconds': '60'
            },
            'description': 'Queue for human-reviewed responses'
        },
        {
            'name': 'jansathi-feedback',
            'attributes': {
                'DelaySeconds': '0',
                'MaxReceiveCount': '5',
                'MessageRetentionPeriod': '1209600',  # 14 days
                'VisibilityTimeoutSeconds': '30'
            },
            'description': 'Queue for user feedback and ratings'
        }
    ]
    
    created_queues = {}
    
    try:
        print("🔄 Creating SQS queues for HITL...")
        
        for queue_config in queues_config:
            queue_name = queue_config['name']
            
            # Create dead letter queue first
            dlq_name = f"{queue_name}-dlq"
            
            dlq_response = sqs.create_queue(
                QueueName=dlq_name,
                Attributes={
                    'MessageRetentionPeriod': '1209600'
                }
            )
            
            dlq_url = dlq_response['QueueUrl']
            
            # Get DLQ ARN
            dlq_attributes = sqs.get_queue_attributes(
                QueueUrl=dlq_url,
                AttributeNames=['QueueArn']
            )
            dlq_arn = dlq_attributes['Attributes']['QueueArn']
            
            # Create main queue with DLQ
            redrive_policy = {
                'deadLetterTargetArn': dlq_arn,
                'maxReceiveCount': queue_config['attributes']['MaxReceiveCount']
            }
            
            queue_attributes = {
                'DelaySeconds': queue_config['attributes']['DelaySeconds'],
                'MessageRetentionPeriod': queue_config['attributes']['MessageRetentionPeriod'],
                'VisibilityTimeoutSeconds': queue_config['attributes']['VisibilityTimeoutSeconds'],
                'RedrivePolicy': json.dumps(redrive_policy)
            }
            
            response = sqs.create_queue(
                QueueName=queue_name,
                Attributes=queue_attributes
            )
            
            queue_url = response['QueueUrl']
            created_queues[queue_name] = queue_url
            
            print(f"SUCCESS: Created queue: {queue_name}")
            print(f"   URL: {queue_url}")
            print(f"   DLQ: {dlq_url}")
        
        print(f"\nSUCCESS: Created {len(created_queues)} SQS queues successfully!")
        
        return created_queues
        
    except Exception as e:
        print(f"ERROR: SQS setup failed: {e}")
        return {}

def create_hitl_service():
    """Create HITL service integration"""
    
    service_code = '''
import boto3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class HITLService:
    """Human-in-the-Loop service for JanSathi"""
    
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name='us-east-1')
        self.queues = {
            'requests': 'https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/jansathi-hitl-requests',
            'responses': 'https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/jansathi-hitl-responses',
            'feedback': 'https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/jansathi-feedback'
        }
    
    def requires_human_review(self, query: str, confidence: float) -> bool:
        """Determine if query requires human review"""
        
        # Low confidence threshold
        if confidence < 0.7:
            return True
        
        # Sensitive topics
        sensitive_keywords = [
            'complaint', 'grievance', 'corruption', 'bribe',
            'legal', 'court', 'police', 'emergency'
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in sensitive_keywords):
            return True
        
        # Complex queries
        if len(query.split()) > 20:
            return True
        
        return False
    
    def send_for_review(self, query_data: Dict[str, Any]) -> str:
        """Send query for human review"""
        
        review_id = str(uuid.uuid4())
        
        message = {
            'review_id': review_id,
            'timestamp': datetime.utcnow().isoformat(),
            'query': query_data.get('query'),
            'user_id': query_data.get('user_id'),
            'confidence': query_data.get('confidence', 0.0),
            'ai_response': query_data.get('ai_response'),
            'context': query_data.get('context', {}),
            'priority': self._get_priority(query_data)
        }
        
        try:
            self.sqs.send_message(
                QueueUrl=self.queues['requests'],
                MessageBody=json.dumps(message),
                MessageAttributes={
                    'Priority': {
                        'StringValue': message['priority'],
                        'DataType': 'String'
                    },
                    'ReviewId': {
                        'StringValue': review_id,
                        'DataType': 'String'
                    }
                }
            )
            
            return review_id
            
        except Exception as e:
            print(f"Error sending for review: {e}")
            return None
    
    def get_reviewed_response(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get human-reviewed response"""
        
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queues['responses'],
                MessageAttributeNames=['ReviewId'],
                MaxNumberOfMessages=10,
                WaitTimeSeconds=1
            )
            
            if 'Messages' in response:
                for message in response['Messages']:
                    attrs = message.get('MessageAttributes', {})
                    if attrs.get('ReviewId', {}).get('StringValue') == review_id:
                        
                        # Delete message from queue
                        self.sqs.delete_message(
                            QueueUrl=self.queues['responses'],
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        
                        return json.loads(message['Body'])
            
            return None
            
        except Exception as e:
            print(f"Error getting reviewed response: {e}")
            return None
    
    def send_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Send user feedback"""
        
        message = {
            'feedback_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': feedback_data.get('user_id'),
            'query_id': feedback_data.get('query_id'),
            'rating': feedback_data.get('rating'),
            'feedback_text': feedback_data.get('feedback_text'),
            'response_helpful': feedback_data.get('response_helpful'),
            'suggestions': feedback_data.get('suggestions')
        }
        
        try:
            self.sqs.send_message(
                QueueUrl=self.queues['feedback'],
                MessageBody=json.dumps(message)
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending feedback: {e}")
            return False
    
    def _get_priority(self, query_data: Dict[str, Any]) -> str:
        """Determine priority level"""
        
        query = query_data.get('query', '').lower()
        
        # High priority keywords
        high_priority = ['emergency', 'urgent', 'complaint', 'grievance']
        if any(keyword in query for keyword in high_priority):
            return 'HIGH'
        
        # Low confidence = medium priority
        if query_data.get('confidence', 1.0) < 0.5:
            return 'MEDIUM'
        
        return 'LOW'
'''
    
    # Write HITL service to file
    with open('JanSathi-vishal/backend/app/services/hitl_service.py', 'w') as f:
        f.write(service_code)
    
    print("SUCCESS: Created HITL service integration")

if __name__ == "__main__":
    print("Setting up SQS for Human-in-the-Loop...")
    queues = create_sqs_queues()
    
    if queues:
        create_hitl_service()
        print("\n🎉 HITL setup complete!")
        print("\n📋 Queue URLs:")
        for name, url in queues.items():
            print(f"  {name}: {url}")
    else:
        print("\nERROR: HITL setup failed!")