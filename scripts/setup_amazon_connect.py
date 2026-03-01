#!/usr/bin/env python3
"""
Setup Amazon Connect for JanSathi voice interface
"""
import boto3
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')

def create_connect_instance():
    """Create Amazon Connect instance"""
    
    connect = boto3.client('connect', region_name='us-east-1')
    
    try:
        print("🔄 Creating Amazon Connect instance...")
        
        # Note: Connect instance creation requires manual setup
        # This script provides the configuration
        
        instance_config = {
            'InstanceAlias': 'jansathi-voice-assistant',
            'IdentityManagementType': 'CONNECT_MANAGED',
            'InboundCallsEnabled': True,
            'OutboundCallsEnabled': False,
            'DirectoryId': None,
            'ClientToken': 'jansathi-connect-2024'
        }
        
        print("WARNING: Amazon Connect instance must be created manually:")
        print("1. Go to AWS Console → Amazon Connect")
        print("2. Create instance with these settings:")
        print(f"   - Instance Alias: {instance_config['InstanceAlias']}")
        print(f"   - Identity Management: {instance_config['IdentityManagementType']}")
        print(f"   - Inbound Calls: {instance_config['InboundCallsEnabled']}")
        print(f"   - Outbound Calls: {instance_config['OutboundCallsEnabled']}")
        
        # Create contact flow configuration
        contact_flow = {
            "Version": "2019-10-30",
            "StartAction": "12345678-1234-1234-1234-123456789012",
            "Actions": [
                {
                    "Identifier": "12345678-1234-1234-1234-123456789012",
                    "Type": "MessageParticipant",
                    "Parameters": {
                        "Text": "नमस्कार! मैं जनसाथी हूं, आपका AI सहायक। मैं सरकारी योजनाओं के बारे में जानकारी दे सकता हूं।"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789013"
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789013",
                    "Type": "GetUserInput",
                    "Parameters": {
                        "Text": "कृपया अपना प्रश्न पूछें या जिस योजना के बारे में जानना चाहते हैं उसका नाम बताएं।",
                        "MaxDigits": 0,
                        "Timeout": "8",
                        "TimeoutAudio": "Beep.wav",
                        "InputTimeLimitSeconds": "30"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789014",
                        "Errors": [
                            {
                                "ErrorType": "NoMatchingError",
                                "NextAction": "12345678-1234-1234-1234-123456789015"
                            }
                        ]
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789014",
                    "Type": "InvokeExternalResource",
                    "Parameters": {
                        "FunctionArn": "arn:aws:lambda:us-east-1:YOUR_ACCOUNT:function:jansathi-connect-handler",
                        "TimeLimit": "8"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789016"
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789015",
                    "Type": "MessageParticipant",
                    "Parameters": {
                        "Text": "क्षमा करें, मैं आपको समझ नहीं पाया। कृपया फिर से कोशिश करें।"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789013"
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789016",
                    "Type": "MessageParticipant",
                    "Parameters": {
                        "Text": "$.External.response_text"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789017"
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789017",
                    "Type": "MessageParticipant",
                    "Parameters": {
                        "Text": "क्या आपका कोई और प्रश्न है? हां के लिए 1 दबाएं, नहीं के लिए 2 दबाएं।"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789018"
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789018",
                    "Type": "GetUserInput",
                    "Parameters": {
                        "Text": "",
                        "MaxDigits": 1,
                        "Timeout": "5"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789019",
                        "Conditions": [
                            {
                                "NextAction": "12345678-1234-1234-1234-123456789013",
                                "Condition": {
                                    "Operator": "Equals",
                                    "Operands": ["1"]
                                }
                            }
                        ]
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789019",
                    "Type": "MessageParticipant",
                    "Parameters": {
                        "Text": "धन्यवाद! जनसाथी का उपयोग करने के लिए आपका शुक्रिया। नमस्कार!"
                    },
                    "Transitions": {
                        "NextAction": "12345678-1234-1234-1234-123456789020"
                    }
                },
                {
                    "Identifier": "12345678-1234-1234-1234-123456789020",
                    "Type": "DisconnectParticipant",
                    "Parameters": {}
                }
            ]
        }
        
        # Save contact flow to file
        with open('JanSathi-vishal/scripts/connect_contact_flow.json', 'w') as f:
            json.dump(contact_flow, f, indent=2)
        
        print("SUCCESS: Contact flow configuration saved to connect_contact_flow.json")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Amazon Connect setup failed: {e}")
        return False

def create_connect_lambda():
    """Create Lambda function for Connect integration"""
    
    lambda_code = '''
import json
import boto3
import requests
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function to handle Amazon Connect calls
    """
    
    # Extract user input from Connect
    user_input = event.get('Details', {}).get('Parameters', {}).get('user_input', '')
    contact_id = event.get('Details', {}).get('ContactData', {}).get('ContactId', '')
    
    # Call JanSathi API
    try:
        api_url = "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod"
        
        payload = {
            "text_query": user_input,
            "language": "hi",
            "userId": f"connect_{contact_id}",
            "source": "amazon_connect"
        }
        
        response = requests.post(f"{api_url}/query", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('answer', {}).get('text', 'क्षमा करें, मैं आपकी सहायता नहीं कर पा रहा।')
        else:
            response_text = "क्षमा करें, तकनीकी समस्या के कारण मैं आपकी सहायता नहीं कर पा रहा।"
    
    except Exception as e:
        print(f"Error calling JanSathi API: {e}")
        response_text = "क्षमा करें, सेवा अस्थायी रूप से अनुपलब्ध है।"
    
    # Return response for Connect
    return {
        'response_text': response_text,
        'timestamp': datetime.utcnow().isoformat(),
        'contact_id': contact_id
    }
'''
    
    # Save Lambda function code
    with open('JanSathi-vishal/scripts/connect_lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    print("SUCCESS: Connect Lambda function code saved")

def create_connect_service():
    """Create Connect service integration"""
    
    service_code = '''
import boto3
import json
from typing import Dict, Any, Optional

class ConnectService:
    """Amazon Connect integration for JanSathi"""
    
    def __init__(self):
        self.connect = boto3.client('connect', region_name='us-east-1')
        self.instance_id = None  # Set after Connect instance is created
    
    def set_instance_id(self, instance_id: str):
        """Set Connect instance ID"""
        self.instance_id = instance_id
    
    def start_outbound_voice_contact(self, phone_number: str, message: str) -> Optional[str]:
        """Start outbound voice contact"""
        
        if not self.instance_id:
            print("Connect instance ID not set")
            return None
        
        try:
            response = self.connect.start_outbound_voice_contact(
                DestinationPhoneNumber=phone_number,
                ContactFlowId='your-contact-flow-id',
                InstanceId=self.instance_id,
                Attributes={
                    'message': message,
                    'source': 'jansathi'
                }
            )
            
            return response['ContactId']
            
        except Exception as e:
            print(f"Error starting outbound contact: {e}")
            return None
    
    def get_contact_attributes(self, contact_id: str) -> Dict[str, Any]:
        """Get contact attributes"""
        
        if not self.instance_id:
            return {}
        
        try:
            response = self.connect.get_contact_attributes(
                InstanceId=self.instance_id,
                InitialContactId=contact_id
            )
            
            return response.get('Attributes', {})
            
        except Exception as e:
            print(f"Error getting contact attributes: {e}")
            return {}
    
    def update_contact_attributes(self, contact_id: str, attributes: Dict[str, str]) -> bool:
        """Update contact attributes"""
        
        if not self.instance_id:
            return False
        
        try:
            self.connect.update_contact_attributes(
                InitialContactId=contact_id,
                InstanceId=self.instance_id,
                Attributes=attributes
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating contact attributes: {e}")
            return False
'''
    
    # Write Connect service to file
    with open('JanSathi-vishal/backend/app/services/connect_service.py', 'w') as f:
        f.write(service_code)
    
    print("SUCCESS: Created Connect service integration")

if __name__ == "__main__":
    print("Setting up Amazon Connect integration...")
    
    if create_connect_instance():
        create_connect_lambda()
        create_connect_service()
        print("\n🎉 Amazon Connect setup complete!")
        print("\n📋 Next steps:")
        print("1. Create Connect instance manually in AWS Console")
        print("2. Upload contact flow from connect_contact_flow.json")
        print("3. Deploy Lambda function from connect_lambda_function.py")
        print("4. Configure phone number and routing")
    else:
        print("\nERROR: Amazon Connect setup failed!")