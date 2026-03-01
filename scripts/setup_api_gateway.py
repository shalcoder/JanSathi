#!/usr/bin/env python3
"""
Setup API Gateway for JanSathi
"""
import boto3
import json
import time
from dotenv import load_dotenv

load_dotenv('backend/.env')

def create_api_gateway():
    """Create API Gateway for JanSathi"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Create REST API
        print("🔄 Creating API Gateway...")
        
        api_response = apigateway.create_rest_api(
            name='jansathi-api',
            description='JanSathi Voice-First AI Civic Assistant API',
            endpointConfiguration={
                'types': ['REGIONAL']
            },
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "execute-api:Invoke",
                        "Resource": "*"
                    }
                ]
            })
        )
        
        api_id = api_response['id']
        print(f"SUCCESS: Created API Gateway: {api_id}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_resource_id = None
        
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create /query resource
        query_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='query'
        )
        
        query_resource_id = query_resource['id']
        print("SUCCESS: Created /query resource")
        
        # Create /health resource
        health_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='health'
        )
        
        health_resource_id = health_resource['id']
        print("SUCCESS: Created /health resource")
        
        # Add CORS for all resources
        for resource_id, path in [(query_resource_id, 'query'), (health_resource_id, 'health')]:
            # OPTIONS method for CORS
            apigateway.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            # OPTIONS integration
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            
            # OPTIONS method response
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': False,
                    'method.response.header.Access-Control-Allow-Methods': False,
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )
            
            # OPTIONS integration response
            apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
        
        # Add POST method to /query
        apigateway.put_method(
            restApiId=api_id,
            resourceId=query_resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Add GET method to /health
        apigateway.put_method(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            authorizationType='NONE'
        )
        
        print("SUCCESS: Added HTTP methods")
        
        # Create deployment
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Production deployment'
        )
        
        print("SUCCESS: Created deployment")
        
        # API Gateway URL
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        
        print(f"\n🎉 API Gateway Setup Complete!")
        print(f"API ID: {api_id}")
        print(f"API URL: {api_url}")
        print(f"Health Check: {api_url}/health")
        print(f"Query Endpoint: {api_url}/query")
        
        return api_id, api_url
        
    except Exception as e:
        print(f"ERROR: API Gateway setup failed: {e}")
        return None, None

if __name__ == "__main__":
    print("Setting up API Gateway for JanSathi...")
    create_api_gateway()