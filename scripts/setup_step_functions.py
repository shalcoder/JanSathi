#!/usr/bin/env python3
"""
Setup Step Functions for JanSathi workflow orchestration
"""
import boto3
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')

def create_step_function():
    """Create Step Functions state machine for JanSathi workflow"""
    
    stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    # Step Functions state machine definition
    state_machine_definition = {
        "Comment": "JanSathi Query Processing Workflow",
        "StartAt": "ProcessQuery",
        "States": {
            "ProcessQuery": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "Parameters": {
                    "FunctionName": "jansathi-query-processor",
                    "Payload.$": "$"
                },
                "Next": "CheckConfidence",
                "Retry": [
                    {
                        "ErrorEquals": ["States.TaskFailed"],
                        "IntervalSeconds": 2,
                        "MaxAttempts": 3,
                        "BackoffRate": 2.0
                    }
                ]
            },
            "CheckConfidence": {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": "$.confidence",
                        "NumericLessThan": 0.7,
                        "Next": "SendForHumanReview"
                    },
                    {
                        "Variable": "$.requires_review",
                        "BooleanEquals": True,
                        "Next": "SendForHumanReview"
                    }
                ],
                "Default": "GenerateResponse"
            },
            "SendForHumanReview": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sqs:sendMessage",
                "Parameters": {
                    "QueueUrl": "https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/jansathi-hitl-requests",
                    "MessageBody.$": "$"
                },
                "Next": "WaitForHumanReview"
            },
            "WaitForHumanReview": {
                "Type": "Wait",
                "Seconds": 300,
                "Next": "CheckHumanResponse"
            },
            "CheckHumanResponse": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "Parameters": {
                    "FunctionName": "jansathi-check-human-response",
                    "Payload.$": "$"
                },
                "Next": "HumanResponseChoice"
            },
            "HumanResponseChoice": {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": "$.human_response_available",
                        "BooleanEquals": True,
                        "Next": "UseHumanResponse"
                    }
                ],
                "Default": "GenerateResponse"
            },
            "UseHumanResponse": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "Parameters": {
                    "FunctionName": "jansathi-format-human-response",
                    "Payload.$": "$"
                },
                "Next": "GenerateAudio"
            },
            "GenerateResponse": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "Parameters": {
                    "FunctionName": "jansathi-response-generator",
                    "Payload.$": "$"
                },
                "Next": "GenerateAudio",
                "Retry": [
                    {
                        "ErrorEquals": ["States.TaskFailed"],
                        "IntervalSeconds": 1,
                        "MaxAttempts": 2,
                        "BackoffRate": 2.0
                    }
                ]
            },
            "GenerateAudio": {
                "Type": "Parallel",
                "Branches": [
                    {
                        "StartAt": "TextToSpeech",
                        "States": {
                            "TextToSpeech": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::aws-sdk:polly:synthesizeSpeech",
                                "Parameters": {
                                    "Text.$": "$.response_text",
                                    "OutputFormat": "mp3",
                                    "VoiceId": "Joanna",
                                    "Engine": "neural"
                                },
                                "End": True
                            }
                        }
                    },
                    {
                        "StartAt": "SaveToDatabase",
                        "States": {
                            "SaveToDatabase": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::dynamodb:putItem",
                                "Parameters": {
                                    "TableName": "jansathi-conversations",
                                    "Item": {
                                        "user_id": {"S.$": "$.user_id"},
                                        "timestamp": {"S.$": "$.timestamp"},
                                        "query": {"S.$": "$.query"},
                                        "response": {"S.$": "$.response_text"},
                                        "confidence": {"N.$": "$.confidence"}
                                    }
                                },
                                "End": True
                            }
                        }
                    }
                ],
                "Next": "SendNotification"
            },
            "SendNotification": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sns:publish",
                "Parameters": {
                    "TopicArn": "arn:aws:sns:us-east-1:YOUR_ACCOUNT:jansathi-notifications",
                    "Message.$": "$.response_text",
                    "Subject": "JanSathi Query Processed"
                },
                "Next": "Success"
            },
            "Success": {
                "Type": "Succeed"
            }
        }
    }
    
    try:
        print("🔄 Creating IAM role for Step Functions...")
        
        # Create IAM role for Step Functions
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "states.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            role_response = iam.create_role(
                RoleName='JanSathiStepFunctionsRole',
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description='Role for JanSathi Step Functions'
            )
            role_arn = role_response['Role']['Arn']
            print(f"SUCCESS: Created IAM role: {role_arn}")
        except iam.exceptions.EntityAlreadyExistsException:
            role_response = iam.get_role(RoleName='JanSathiStepFunctionsRole')
            role_arn = role_response['Role']['Arn']
            print(f"SUCCESS: Using existing IAM role: {role_arn}")
        
        # Attach policies to role
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
            'arn:aws:iam::aws:policy/AmazonSQSFullAccess',
            'arn:aws:iam::aws:policy/AmazonSNSFullAccess',
            'arn:aws:iam::aws:policy/AmazonPollyFullAccess'
        ]
        
        for policy_arn in policies:
            try:
                iam.attach_role_policy(
                    RoleName='JanSathiStepFunctionsRole',
                    PolicyArn=policy_arn
                )
            except Exception:
                pass  # Policy might already be attached
        
        print("SUCCESS: Attached policies to role")
        
        # Create Step Functions state machine
        print("🔄 Creating Step Functions state machine...")
        
        response = stepfunctions.create_state_machine(
            name='JanSathiWorkflow',
            definition=json.dumps(state_machine_definition),
            roleArn=role_arn,
            type='STANDARD',
            loggingConfiguration={
                'level': 'ERROR',
                'includeExecutionData': False,
                'destinations': [
                    {
                        'cloudWatchLogsLogGroup': {
                            'logGroupArn': 'arn:aws:logs:us-east-1:YOUR_ACCOUNT:log-group:/aws/stepfunctions/JanSathiWorkflow'
                        }
                    }
                ]
            }
        )
        
        state_machine_arn = response['stateMachineArn']
        
        print(f"SUCCESS: Created Step Functions state machine!")
        print(f"State Machine ARN: {state_machine_arn}")
        
        return state_machine_arn
        
    except Exception as e:
        print(f"ERROR: Step Functions setup failed: {e}")
        return None

def create_workflow_integration():
    """Create workflow integration service"""
    
    service_code = '''
import boto3
import json
import uuid
from datetime import datetime
from typing import Dict, Any

class WorkflowService:
    """Step Functions workflow orchestration for JanSathi"""
    
    def __init__(self):
        self.stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')
        self.state_machine_arn = 'arn:aws:states:us-east-1:YOUR_ACCOUNT:stateMachine:JanSathiWorkflow'
    
    def start_query_workflow(self, query_data: Dict[str, Any]) -> str:
        """Start Step Functions workflow for query processing"""
        
        execution_name = f"jansathi-query-{uuid.uuid4()}"
        
        workflow_input = {
            'execution_id': execution_name,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': query_data.get('user_id'),
            'query': query_data.get('query'),
            'language': query_data.get('language', 'en'),
            'confidence': query_data.get('confidence', 0.0),
            'requires_review': query_data.get('requires_review', False),
            'context': query_data.get('context', {})
        }
        
        try:
            response = self.stepfunctions.start_execution(
                stateMachineArn=self.state_machine_arn,
                name=execution_name,
                input=json.dumps(workflow_input)
            )
            
            return response['executionArn']
            
        except Exception as e:
            print(f"Error starting workflow: {e}")
            return None
    
    def get_execution_status(self, execution_arn: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        
        try:
            response = self.stepfunctions.describe_execution(
                executionArn=execution_arn
            )
            
            return {
                'status': response['status'],
                'start_date': response['startDate'].isoformat(),
                'stop_date': response.get('stopDate', {}).isoformat() if response.get('stopDate') else None,
                'input': json.loads(response['input']),
                'output': json.loads(response.get('output', '{}'))
            }
            
        except Exception as e:
            print(f"Error getting execution status: {e}")
            return {'status': 'UNKNOWN'}
    
    def stop_execution(self, execution_arn: str, reason: str = "User requested") -> bool:
        """Stop workflow execution"""
        
        try:
            self.stepfunctions.stop_execution(
                executionArn=execution_arn,
                error='UserRequested',
                cause=reason
            )
            
            return True
            
        except Exception as e:
            print(f"Error stopping execution: {e}")
            return False
'''
    
    # Write workflow service to file
    with open('JanSathi-vishal/backend/app/services/workflow_service.py', 'w') as f:
        f.write(service_code)
    
    print("SUCCESS: Created workflow service integration")

if __name__ == "__main__":
    print("Setting up Step Functions workflow...")
    state_machine_arn = create_step_function()
    
    if state_machine_arn:
        create_workflow_integration()
        print("\nStep Functions setup complete!")
    else:
        print("\nERROR: Step Functions setup failed!")