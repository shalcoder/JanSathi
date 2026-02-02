import boto3
import json
import os

class BedrockService:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime', 
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        # Using Claude 3 Sonnet (or Haiku for speed)
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0" 

    def generate_response(self, query, context_text, language='hi'):
        prompt = f"""
        Human: You are JanSathi, an intelligent assistant for Indian farmers.
        
        Here is the retrieved context (FACTS):
        {context_text}
        
        User Question: {query}
        
        Instructions:
        1. Answer the question based ONLY on the context provided.
        2. If the answer is not in the context, say "I don't have that information."
        3. Respond in the language: {language} (Hindi if 'hi').
        4. Keep the answer concise (under 50 words).
        5. Be polite.
        
        Assistant:
        """

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body, 
                modelId=self.model_id, 
                accept='application/json', 
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']

        except Exception as e:
            print(f"Bedrock Error: {e}")
            return "Unable to connect to AI Brain. (Check AWS Credentials)"
