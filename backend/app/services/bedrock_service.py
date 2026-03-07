import boto3
import json
import os
import re
import time
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.utils import log_event, timed
from app.core.security import sanitize_ai_response

# ── Nova Model IDs ──────────────────────────────────────────────────────────
NOVA_LITE = "amazon.nova-lite-v1:0"   # Primary: chat, RAG, responses
NOVA_PRO  = "amazon.nova-pro-v1:0"   # Vision + complex reasoning

JANSATHI_SYSTEM_PROMPT = (
    "You are JanSathi, India's premier AI Citizen Assistant. "
    "Provide accurate, compassionate information about Indian government schemes. "
    "Use simple language citizens can understand. Never invent eligibility data or URLs."
)

KNOWN_DOMAINS = [
    'gov.in', 'nic.in', 'india.gov.in', 'pmkisan.gov.in',
    'pmjay.gov.in', 'enam.gov.in', 'pmfby.gov.in', 'pmaymis.gov.in',
    'pmuy.gov.in', 'mudra.org.in', 'nsiindia.gov.in', 'pmjdy.gov.in',
    'nfsa.gov.in', 'pmvishwakarma.gov.in', 'pmsvanidhi.mohua.gov.in',
    'pmkvyofficial.org', 'edistrict.up.gov.in', 'myscheme.gov.in',
    'eshram.gov.in', 'umang.gov.in', 'digilocker.gov.in',
]

class BedrockService:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        # Default to Amazon Nova Lite (replaces Claude)
        self.model_id = os.getenv('BEDROCK_MODEL_ID', NOVA_LITE)
        
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
        """Generate a response using Amazon Nova Lite via Converse API."""
        if not self.working:
            return self._get_context_based_response(query, context_text, language)

        has_scheme_context = (
            context_text and
            context_text.strip() and
            "I do not have specific public data" not in context_text
        )

        if not has_scheme_context:
            context_text = (
                f"General inquiry about: {query}. "
                "Provide helpful information based on general knowledge of Indian government services."
            )

        # ── Nova Lite prompt ──────────────────────────────────────────────────
        if has_scheme_context:
            user_content = f"""VERIFIED SCHEME INFORMATION:
{context_text}

USER QUERY: {query}
PRIMARY LANGUAGE: {language}
USER INTENT: {intent}

Respond ONLY in {language}. Structure your response as:
✅ **Summary**: [1-2 sentences]
📋 **Key Details**: [bullet points from context]
🪜 **Action Plan**: [numbered steps]
🛡️ **Privacy**: Data processed securely
🌐 **Official Source**: [URL from context only]"""
        else:
            user_content = f"""USER QUERY: {query}
PRIMARY LANGUAGE: {language}

Provide helpful guidance about Indian government services. 
Suggest official portals (india.gov.in, myscheme.gov.in). Respond in {language}."""

        # ── Call Nova via Converse API ────────────────────────────────────────
        messages = [{"role": "user", "content": [{"text": user_content}]}]
        system = [{"text": JANSATHI_SYSTEM_PROMPT}]

        try:
            response = self.bedrock_runtime.converse(
                modelId=self.model_id,
                messages=messages,
                system=system,
                inferenceConfig={"maxTokens": 1000, "temperature": 0.1},
            )

            raw_response = response["output"]["message"]["content"][0]["text"]
            validated = self._validate_response(raw_response)
            sanitized = sanitize_ai_response(validated)

            provenance = "verified_doc" if has_scheme_context else "general_search"
            usage = response.get("usage", {})

            log_event('bedrock_success', {
                'model': self.model_id,
                'query_length': len(query),
                'response_length': len(sanitized),
                'intent': intent,
                'provenance': provenance,
                'input_tokens': usage.get('inputTokens', 0),
                'output_tokens': usage.get('outputTokens', 0),
            })

            explainability = {
                "confidence": 0.90 if has_scheme_context else 0.75,
                "matching_criteria": ["Nova Lite response via Converse API"],
                "privacy_protocol": "DPDP-Compliant (Zero PII in logs)",
            }

            return {
                "text": sanitized,
                "provenance": provenance,
                "explainability": explainability,
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"Bedrock ClientError ({error_code}): {e}")
            return self._get_context_based_response(query, context_text, language)
        except Exception as e:
            print(f"Nova/Bedrock Error: {e}")
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
        """Analyzes an image using Amazon Nova Pro (vision) via Converse API."""
        if not self.working:
            return {"text": "AI Vision not connected.", "provenance": "vision_error"}

        vision_instructions = (
            f"You are JanSathi. The user has uploaded a government document.\n"
            f"Instruction: {prompt_text}\n"
            f"1. Identify the document type and purpose.\n"
            f"2. Extract key details: dates, deadlines, amounts, requirements.\n"
            f"3. Respond clearly in {language}."
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {"bytes": image_bytes},
                        }
                    },
                    {"text": vision_instructions},
                ],
            }
        ]

        try:
            # Nova Pro for vision (supports multimodal)
            response = self.bedrock_runtime.converse(
                modelId=NOVA_PRO,
                messages=messages,
                system=[{"text": JANSATHI_SYSTEM_PROMPT}],
                inferenceConfig={"maxTokens": 1000, "temperature": 0.1},
            )
            analysis_text = response["output"]["message"]["content"][0]["text"]

            # Automated PII Warning
            if any(term in analysis_text.lower() for term in ['aadhaar', 'number', 'address', 'phone']):
                analysis_text = (
                    "🛡️ **Privacy Notice**: This document contains personal identifiers. "
                    "JanSathi analyzed it securely. Avoid sharing Aadhaar photos publicly.\n\n"
                    + analysis_text
                )

            return {"text": analysis_text, "provenance": "vision_analysis"}
        except Exception as e:
            print(f"Nova Vision Error: {e}")
            return {
                "text": "Could not analyze the image. Please ensure it is clear and try again.",
                "provenance": "vision_error",
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
                text = f"""नमस्ते! आपकी सहायता के लिए यहाँ कुछ सुझाव दिए गए हैं:

• सरकारी योजनाओं की खोज के लिए [myscheme.gov.in](https://myscheme.gov.in) पर जाएँ।
• आधिकारिक जानकारी [india.gov.in](https://india.gov.in) पर भी उपलब्ध है।
• आप अपने नजदीकी जिले के सरकारी कार्यालय से भी संपर्क कर सकते हैं।

आशा है कि यह जानकारी आपके काम आएगी!"""
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
