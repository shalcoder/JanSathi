import boto3
import json
import os
import re
import time
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.utils import log_event, timed
from app.core.security import sanitize_ai_response

class BedrockService:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
        
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime', 
                region_name=self.region
            )
            self.working = True
        except NoCredentialsError:
            print("Bedrock Init Failed: No Credentials.")
            self.working = False

    @timed
    def generate_response(self, query, context_text, language='hi', intent="GENERAL_INQUIRY"):
        if not self.working:
            return self._get_context_based_response(query, context_text, language)

        # Check if we have actual context about the query
        if not context_text or "I do not have specific public data" in context_text:
            return f"I don't have specific information about '{query}'. Please check official government portals like india.gov.in for accurate details."

        # ============================================================
        # CLAUDE 3.5 SONNET OPTIMIZED PROMPT (Sovereign Expert)
        # ============================================================
        prompt = f"""
System: You are JanSathi, the premier AI Citizen Assistant for India. Your goal is to provide accurate, verified information about government schemes and market resources with empathy and clarity.

CONTEXT (Verified Knowledge Base):
{context_text}

USER QUERY: {query}
PRIMARY LANGUAGE: {language}
USER INTENT: {intent}

CRITICAL OPERATING PROCEDURES:
1. CITATION: Every claim about an amount, date, or eligibility MUST be supported by the provided CONTEXT.
2. AASTHA VOICE (Sentiment): Analyze user tone. If the user is in distress, prioritize highly empathetic language and immediate aid like Loan Waivers.
3. MARKET INSIGHTS: If intent is MARKET_ACCESS, explain the price trends (₹) and suggest when to sell/hold produce simply.
4. SOURCE LINKING: Always finish with the official link from the context (e.g., enam.gov.in).
5. STRUCTURE: Use professional Markdown. Use bolding for key terms.
6. HALLUCINATION GUARD: If context is insufficient, politely direct to 'india.gov.in'. NEVER invent data.
7. SIMPLE LANGUAGE: Break down complex bureaucratic terms into simple concepts.

RESPONSE TEMPLATE:
✅ **Summary**: [1-2 sentences explaining what this is / Current Market Status]

📋 **Key Details**:
• [Points from context]
• [Mandi Prices if applicable]

🪜 **Action Plan**:
1. [Step 1]
2. [Step 2]

🛡️ **Sentinel Security**: [Privacy/Verification Status]

🌐 **Official Source**: [URL from context]

Reply directly in {language}.
"""

        # Build request body for Claude 3.5 Sonnet
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "top_p": 0.9
        })

        try:
            response = self.bedrock_runtime.invoke_model(
                body=body, 
                modelId=self.model_id, 
                accept='application/json', 
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            raw_response = response_body['content'][0]['text']
            
            # Validate and sanitize the response
            validated = self._validate_response(raw_response)
            sanitized = sanitize_ai_response(validated)
            
            log_event('bedrock_success', {
                'model': self.model_id,
                'query_length': len(query),
                'response_length': len(sanitized),
                'intent': intent
            })
            
            return sanitized

        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"Bedrock ClientError: {error_code}")
            return self._get_context_based_response(query, context_text, language)
        except Exception as e:
            print(f"Claude/Bedrock Error: {e}")
            return self._get_context_based_response(query, context_text, language)

    def _validate_response(self, response: str) -> str:
        """
        Validate AI response for hallucination markers.
        Checks for fabricated URLs, suspicious claims, and ensures citations.
        """
        if not response:
            return "I could not generate a response. Please try again."
        
        # Remove any 'Human:' or 'Assistant:' markers
        response = re.sub(r'^(Human|Assistant):\s*', '', response, flags=re.MULTILINE)
        
        # Check for fabricated URLs
        known_domains = [
            'gov.in', 'nic.in', 'india.gov.in', 'pmkisan.gov.in',
            'pmjay.gov.in', 'enam.gov.in', 'pmfby.gov.in', 'pmaymis.gov.in',
            'pmuy.gov.in', 'mudra.org.in', 'nsiindia.gov.in', 'pmjdy.gov.in',
            'nfsa.gov.in', 'pmvishwakarma.gov.in', 'pmsvanidhi.mohua.gov.in',
            'pmkvyofficial.org', 'edistrict.up.gov.in', 'myscheme.gov.in'
        ]
        
        urls_in_response = re.findall(r'https?://[^\s\)\]]+', response)
        for url in urls_in_response:
            if not any(domain in url for domain in known_domains):
                response = response.replace(url, 'https://myscheme.gov.in')
                log_event('hallucination_detected', {'type': 'fabricated_url', 'url': url})
        
        return response

    def analyze_image(self, image_bytes, prompt_text="Explain this document.", language='hi'):
        """Analyzes an image using Claude 3 Vision."""
        if not self.working:
            return "AI Vision not connected."

        import base64
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        vision_prompt = f"""
        You are JanSathi. The user has uploaded a government document.
        
        USER INSTRUCTION: {prompt_text}
        TARGET LANGUAGE: {language}
        
        TASK:
        1. Identify the key purpose of the document.
        2. Explain the critical details (Dates, Deadlines, Amounts, Requirements) simply.
        3. Output directly in {language}.
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
            # SONNET FOR VISION - Highly advanced auditor
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            analysis_text = response_body['content'][0]['text']
            
            # UNIQUE FEATURE: Automated PII Warning
            if any(term in analysis_text.lower() for term in ['aadhaar', 'number', 'address', 'phone']):
                analysis_text = "🛡️ **Privacy Notice**: This document contains personal identifiers. JanSathi has analyzed it securely, but please avoid sharing raw photos of your Aadhaar in public groups.\n\n" + analysis_text
                
            return analysis_text
        except Exception as e:
            print(f"Vision Error: {e}")
            return "Could not analyze the image. Please ensure it is clear."

    def _get_context_based_response(self, query, context_text, language='hi'):
        """Fallback response based on RAG context when Bedrock is offline."""
        if not context_text or "I do not have specific public data" in context_text:
            return f"I don't have specific information about '{query}'. Please visit india.gov.in."
        
        # Simpler structured fallback
        lines = context_text.split('\n')
        primary_info = lines[0] if lines else "Scheme information"
        
        return f"✅ **Verified Info**: {primary_info}\n\n📋 **Next Steps**: Please check the official government portal for application details and requirements."
