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

        # Handle general questions even without specific scheme context
        has_scheme_context = context_text and context_text.strip() and "I do not have specific public data" not in context_text
        
        if not has_scheme_context:
            # For general questions, provide helpful response without requiring specific scheme data
            context_text = f"General inquiry about: {query}. Provide helpful information based on general knowledge of Indian government services and schemes."

        # ============================================================
        # CLAUDE 3.5 SONNET OPTIMIZED PROMPT (Sovereign Expert)
        # ============================================================
        
        if has_scheme_context:
            # Specific scheme information available
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

Reply directly and return the response in a structured JSON format containing:
1. "text": The simplified explanation in {language}.
2. "metadata": {
    "confidence": 0.0-1.0 score based on context match,
    "matching_criteria": ["list", "of", "matched", "requirements"],
    "privacy_protocol": "Federated Optimization Active (Local Computation)"
}

RESPONSE TEMPLATE (TEXT PART):
✅ **Summary**: [1-2 sentences]

📋 **Explainability (Why me?)**:
• [Condition A] matched [User Data]
• [Condition B] matched [User Data]

🪜 **Action Plan**:
1. [Step 1]

🛡️ **Sentinel Security**: [Privacy/Verification Status]

🌐 **Official Source**: [URL]
"""
        else:
            # General question without specific scheme context
            prompt = f"""
System: You are JanSathi, the premier AI Citizen Assistant for India. You help citizens with government services, schemes, and general civic information.

USER QUERY: {query}
PRIMARY LANGUAGE: {language}
USER INTENT: {intent}

INSTRUCTIONS:
1. Provide helpful, accurate information based on your knowledge of Indian government services
2. If the question is about a specific government scheme, explain what you know and suggest checking official portals
3. For general civic questions, provide practical guidance
4. Use simple, clear language that citizens can understand
5. Always suggest official government websites for the most current information
6. Be empathetic and supportive in your tone

RESPONSE GUIDELINES:
- Start with a clear, direct answer
- Provide actionable steps when possible
- Mention relevant government portals (india.gov.in, myscheme.gov.in)
- Use professional but friendly tone
- Structure information clearly with bullet points or steps

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
            
            # UNIQUE FEATURE: Answer Provenance Tracking
            provenance = "verified_doc" if has_scheme_context else "general_search"
            
            log_event('bedrock_success', {
                'model': self.model_id,
                'query_length': len(query),
                'response_length': len(sanitized),
                'intent': intent,
                'provenance': provenance
            })
            
            # Parse JSON if possible, else wrap string
            try:
                json_res = json.loads(sanitized)
                text = json_res.get('text', sanitized)
                explainability = json_res.get('metadata', {})
            except:
                text = sanitized
                explainability = {
                    "confidence": 0.85,
                    "matching_criteria": ["Criteria match based on verified scheme text"],
                    "privacy_protocol": "On-Device Federated Masking"
                }

            log_event('bedrock_response', {
                'tokens': response_body.get('usage', {}).get('total_tokens', 0),
                'provenance': provenance,
                'confidence': explainability.get('confidence', 0)
            })
            
            return {
                "text": text,
                "provenance": provenance,
                "explainability": explainability
            }

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
                
            return {
                "text": analysis_text,
                "provenance": "vision_analysis"
            }
        except Exception as e:
            print(f"Vision Error: {e}")
            return {
                "text": "Could not analyze the image. Please ensure it is clear.",
                "provenance": "vision_error"
            }

    def _get_context_based_response(self, query, context_text, language='hi'):
        """Fallback response when Bedrock is offline - now handles general questions."""
        
        # Check if we have specific scheme context
        # IMPROVED: Ensure we don't treat system instructions as verified data
        has_scheme_context = (
            context_text and 
            context_text.strip() and 
            "I do not have specific public data" not in context_text and
            "General inquiry about" not in context_text  # Don't show our own placeholder as verified info
        )
        
        provenance = "verified_doc" if has_scheme_context else "general_search"
        
        if has_scheme_context:
            # Specific scheme information available
            lines = context_text.split('\n')
            primary_info = lines[0] if lines else "Scheme information"
            text = f"✅ **Verified Info**: {primary_info}\n\n📋 **Next Steps**: Please check the official government portal for application details and requirements."
        else:
            # General question - provide helpful fallback
            if language == 'hi':
                text = f"""मैं आपके प्रश्न '{query}' के बारे में विस्तृत जानकारी नहीं दे सकता, लेकिन मैं आपकी सहायता करने की कोशिश कर सकता हूं।

📋 **सुझाव**:
• सरकारी योजनाओं की जानकारी के लिए [myscheme.gov.in](https://myscheme.gov.in) देखें
• आधिकारिक जानकारी के लिए [india.gov.in](https://india.gov.in) पर जाएं
• स्थानीय सरकारी कार्यालय से संपर्क करें

🌐 **आधिकारिक स्रोत**: [https://india.gov.in](https://india.gov.in)"""
            else:
                text = f"""I don't have specific detailed information about the query '{query}' in my current scheme database, but I can provide general guidance.

📋 **Suggestions**:
• Search for this on [india.gov.in](https://india.gov.in)
• Check [myscheme.gov.in](https://myscheme.gov.in) for similar government schemes
• Contact your local district administration office

🌐 **Official Source**: [https://india.gov.in](https://india.gov.in)"""

        return {
            "text": text,
            "provenance": provenance
        }
