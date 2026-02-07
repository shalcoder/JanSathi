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
            return self._get_context_based_response(query, context_text, language)

        # Check if we have actual context about the query
        if not context_text or "I do not have specific public data" in context_text:
            return f"I don't have specific information about '{query}'. Please check official government portals like india.gov.in for accurate details."

        prompt = f"""
        Human: You are JanSathi, a helpful government assistant for rural India.
        
        CONTEXT (Official Government Information):
        {context_text}
        
        USER QUESTION: {query}
        LANGUAGE: {language}
        
        CRITICAL INSTRUCTIONS:
        1. Answer ONLY using the CONTEXT provided above. Do NOT make up information.
        2. If the context contains information about the user's question, use it to provide a helpful answer.
        3. Structure your response clearly with the scheme/service name and key details.
        4. Keep language simple and practical.
        5. Reply in {language} if possible, otherwise English.
        
        Format your answer like this:
        ✅ **What this is**: [Brief explanation based on context]
        
        📋 **Key Details**:
        • [Detail 1 from context]
        • [Detail 2 from context]
        
        🌐 **More Information**: [Website from context if available]
        
        Assistant:
        """

        # Check if using Titan or Claude
        if "titan" in self.model_id.lower():
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 400,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            })
        else:
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
                
                # Parse response based on model type
                if "titan" in self.model_id.lower():
                    return response_body['results'][0]['outputText']
                else:
                    return response_body['content'][0]['text']

            except ClientError as e:
                error_code = e.response['Error']['Code']
                print(f"Bedrock ClientError: {error_code} - {e}")
                if error_code == 'ThrottlingException':
                    if attempt < retries:
                        time.sleep(1 * (attempt + 1)) # Simple backoff
                        continue
                    else:
                        return "System is busy. Please try again later."
                elif error_code == 'AccessDeniedException':
                    print("Access denied - using context-based response")
                    return self._get_context_based_response(query, context_text, language)
                else:
                    print(f"Bedrock Error: {e}")
                    return self._get_context_based_response(query, context_text, language)
            except Exception as e:
                print(f"Unknown Bedrock Error: {e}")
                return self._get_context_based_response(query, context_text, language)

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

    def _get_context_based_response(self, query, context_text, language='hi'):
        """Generate a response based on the RAG context when Bedrock is not available"""
        if not context_text or "I do not have specific public data" in context_text:
            return f"I don't have specific information about '{query}'. Please check official government portals like india.gov.in for accurate details."
        
        # Extract key information from context
        lines = context_text.split('\n')
        scheme_info = []
        website = ""
        
        for line in lines:
            if line.strip():
                if "https://" in line:
                    # Extract website
                    import re
                    urls = re.findall(r'https://[^\s\]]+', line)
                    if urls:
                        website = urls[0]
                
                # Clean up the line
                clean_line = line.replace('[Source:', '').replace(']', '').strip()
                if clean_line and not clean_line.startswith('http'):
                    scheme_info.append(clean_line)
        
        # Generate structured response
        if scheme_info:
            main_info = scheme_info[0] if scheme_info else "Government scheme information"
            
            response = f"✅ **What this is**: {main_info}\n\n"
            
            if len(scheme_info) > 1:
                response += "📋 **Key Details**:\n"
                for info in scheme_info[1:3]:  # Limit to 2 additional details
                    response += f"• {info}\n"
                response += "\n"
            
            if website:
                response += f"🌐 **More Information**: {website}\n\n"
            
            response += "💡 **Note**: This information is from official government sources. For the latest updates and application procedures, please visit the official website."
            
            return response
        
        return self._get_demo_response()

    def _get_demo_response(self):
        return """✅ **What this is**: (Demo Mode) The Income Certificate is an official statement provided to the citizen by the state government confirming their annual income.

📋 **Eligibility**:
• Citizen of India.
• Resident of the respective state.

🧾 **Required Documents**:
• Identity Proof (Aadhaar Card, Voter ID).
• Address Proof (Ration Card, Electricity Bill).
• Self-declaration of income.

🪜 **Steps to Apply**:
1. Visit your state's e-District portal.
2. Select 'Income Certificate' service.
3. Fill the application form and upload documents.
4. Pay the nominal fee.

🌐 **Where to Apply**: Online via e-District Portal or nearest Common Service Centre (CSC)."""
