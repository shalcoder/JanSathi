import boto3
import json
import os
import time
from botocore.exceptions import ClientError, NoCredentialsError

class BedrockService:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-haiku-20240307-v1:0")
        
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime', 
                region_name=self.region
            )
            self.working = True
        except NoCredentialsError:
            print("Bedrock Init Failed: No Credentials.")
            self.working = False

    def generate_response(self, query, context_text, language='hi'):
        if not self.working:
            return "AI Brain not connected (Check AWS Credentials)."

        prompt = f"""
        Human: You are JanSathi, a helpful and empathetic government assistant for rural India.
        Your goal is to explain government schemes, prices, and rules simply.
        
        CONTEXT (Relevant Documents):
        {context_text}
        
        USER QUESTION: {query}
        
        INSTRUCTIONS:
        1. Answer ONLY based on the CONTEXT provided. If the answer is missing, state: "I do not have official information on this."
        2. Keep the language simple and direct.
        3. Reply in the requested language: {language} (or English if not specified).
        4. If the user asks about crops/health, be supportive but factual.
        5. Do NOT make up numbers or dates.
        
        Assistant:
        """

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 400,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "top_p": 0.9
        })

        retries = 2
        for attempt in range(retries + 1):
            try:
                response = self.bedrock_runtime.invoke_model(
                    body=body, 
                    modelId=self.model_id, 
                    accept='application/json', 
                    contentType='application/json'
                )
                
                response_body = json.loads(response.get('body').read())
                return response_body['content'][0]['text']

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException':
                    if attempt < retries:
                        time.sleep(1 * (attempt + 1)) # Simple backoff
                        continue
                    else:
                        return "System is busy. Please try again later."
                else:
                    print(f"Bedrock Error: {e}")
                    return "Sorry, I encountered a technical issue."
            except Exception as e:
                print(f"Unknown Error: {e}")
                return "An unexpected error occurred."

    def analyze_image(self, image_bytes, prompt_text="Explain this document.", language='hi'):
        """
        Analyzes an image (Document/Scene) using Claude 3 Vision.
        """
        if not self.working:
            return "AI Vision not connected."

        import base64
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        vision_prompt = f"""
        You are JanSathi. The user has uploaded an image of a government document, notice, or agricultural scene.
        
        USER INSTRUCTION: {prompt_text}
        TARGET LANGUAGE: {language}
        
        TASK:
        1. Identify the key purpose of the document/image.
        2. Explain the critical details (Dates, Deadlines, Amounts, Requirements) simply.
        3. Do NOT translate word-for-word. Summarize for a rural user.
        4. If it's a form, tell them what documents they need to attach.
        5. Output directly in {language}.
        """

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": encoded_image
                            }
                        },
                        {
                            "type": "text",
                            "text": vision_prompt
                        }
                    ]
                }
            ],
            "temperature": 0.1
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="anthropic.claude-3-sonnet-20240229-v1:0", # Use Sonnet/Haiku for Vision
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
        except Exception as e:
            print(f"Vision Error: {e}")
            return "Could not analyze the image. Please ensure it is clear."
