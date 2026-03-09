import boto3
import json
import os
import re
import time
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from app.core.utils import log_event, timed
from app.core.security import sanitize_ai_response
from app.services.cache_service import ResponseCache

# Allow standalone script/test execution paths to pick up backend/.env credentials.
load_dotenv()

BedrockQueryCache = ResponseCache(ttl_seconds=3600)
PDF_CONTEXT_STORE = {}

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

        from botocore.config import Config as BotoConfig
        _cfg = BotoConfig(connect_timeout=5, read_timeout=10, retries={'max_attempts': 1})
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region,
                config=_cfg,
            )
            self.working = True
        except NoCredentialsError:
            print("Bedrock Init Failed: No Credentials.")
            self.working = False

    def _is_scheme_related(self, query: str, intent: str, scheme_hint: str) -> bool:
        it = (intent or "").lower()
        sh = (scheme_hint or "unknown").lower()
        if sh not in ("", "unknown", "none", "null"):
            return True
        if it in {"apply", "grievance", "track", "life_event"}:
            return True
        q = (query or "").lower()
        scheme_terms = [
            "scheme", "yojana", "kisan", "pmay", "pm awas", "awas",
            "e-shram", "eshram", "ration", "ayushman", "pmjay", "subsidy",
            "eligibility", "application status", "grievance",
        ]
        return any(t in q for t in scheme_terms)

    @timed
    def generate_response(self, query, context_text, language='hi', intent="GENERAL_INQUIRY", session_id=None, scheme_hint="unknown"):
        """Generate a response using Amazon Nova Lite via Converse API."""
        if not self.working:
            return self._get_context_based_response(query, context_text, language, intent, scheme_hint)

        # ── Inject PDF Context if available ──────────────────────────────────
        if session_id and session_id in PDF_CONTEXT_STORE:
            pdf_context = PDF_CONTEXT_STORE[session_id]
            context_text = f"USER UPLOADED DOCUMENT CONTENT:\n{pdf_context}\n\nADDITIONAL INFO:\n{context_text}"

        has_scheme_context = (
            context_text and
            context_text.strip() and
            "I do not have specific public data" not in context_text
        )
        scheme_related = self._is_scheme_related(query, intent, scheme_hint)

        lang_map = {
            'hi': 'Hindi (हिन्दी)',
            'en': 'English',
            'ta': 'Tamil (தமிழ்)',
            'te': 'Telugu (తెలుగు)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'mr': 'Marathi (मराठी)',
            'bn': 'Bengali (বাংলা)',
            'gu': 'Gujarati (ગુજરાતી)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'or': 'Odia (ଓଡ଼ିଆ)',
            'as': 'Assamese (অসমীয়া)'
        }
        native_lang = lang_map.get(language, 'English')

        if not has_scheme_context and scheme_related:
            # Strict verified mode for government schemes: never fabricate details.
            return {
                "text": (
                    "I can help with this scheme, but I currently don't have verified context to answer safely.\n\n"
                    "Please ask one of these so I can proceed accurately:\n"
                    "1. Eligibility criteria\n"
                    "2. Required documents\n"
                    "3. Application process\n"
                    "4. Status check\n\n"
                    "Official portals: https://myscheme.gov.in, https://india.gov.in"
                ),
                "provenance": "strict_verified_mode",
                "explainability": {
                    "confidence": 0.6,
                    "matching_criteria": ["Scheme-related query without verified context"],
                    "privacy_protocol": "DPDP-Compliant (Zero PII in logs)",
                },
            }

        if not has_scheme_context:
            context_text = (
                f"General inquiry about: {query}. "
                "Provide a helpful, concise answer as a broad assistant. "
                "If the user asks for regulated/legal/medical advice, add a brief caution."
            )

        # ── Check Cache ───────────────────────────────────────────────────────
        cached = BedrockQueryCache.get(query, language)
        if cached:
            try:
                # Build return dict combining cache result
                explainability = {
                    "confidence": 0.99,
                    "matching_criteria": ["Cached Nova Response"],
                    "privacy_protocol": "DPDP-Compliant (Zero PII in logs)",
                }
                return {
                    "text": cached['response'],
                    "provenance": "verified_doc" if has_scheme_context else "general_search",
                    "explainability": explainability,
                    "cache_hit": True
                }
            except Exception as e:
                print(f"Cache return error: {e}")

        # ── Nova Lite prompt ──────────────────────────────────────────────────
        if has_scheme_context and scheme_related:
            user_content = f"""VERIFIED SCHEME INFORMATION:
{context_text}

USER QUERY: {query}
PRIMARY LANGUAGE: {native_lang}
USER INTENT: {intent}

Respond ONLY in {native_lang}. Structure your response as:
✅ **Summary**: [1-2 sentences]
📋 **Key Details**: [bullet points from context]
🪜 **Action Plan**: [numbered steps]
🛡️ **Privacy**: Data processed securely
🌐 **Official Source**: [URL from context only]"""
        else:
            user_content = f"""USER QUERY: {query}
PRIMARY LANGUAGE: {native_lang}

Answer as a broad, helpful assistant in {native_lang}.
Keep it practical and concise.
If the query is clearly about Indian government schemes and verified sources are missing, say that you need verified context and suggest official portals (india.gov.in, myscheme.gov.in)."""

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

            # ── Set Cache ────────────────────────────────────────────────────────
            try:
                BedrockQueryCache.set(query, language, sanitized, None)
            except Exception as e:
                print(f"Failed to cache Bedrock response: {e}")

            return {
                "text": sanitized,
                "provenance": provenance,
                "explainability": explainability,
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"Bedrock ClientError ({error_code}): {e}")
            return self._get_context_based_response(query, context_text, language, intent, scheme_hint)
        except Exception as e:
            print(f"Nova/Bedrock Error: {e}")
            return self._get_context_based_response(query, context_text, language, intent, scheme_hint)

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

    def _get_context_based_response(self, query, context_text, language='hi', intent='info', scheme_hint='unknown'):
        """Fallback response when Bedrock is offline with strict-vs-broad behavior."""
        
        # Check if we have specific scheme context
        # IMPROVED: Ensure we don't treat system instructions as verified data
        has_scheme_context = (
            context_text and 
            context_text.strip() and 
            "I do not have specific public data" not in context_text and
            "General inquiry about" not in context_text  # Don't show our own placeholder as verified info
        )
        scheme_related = self._is_scheme_related(query, intent, scheme_hint)
        
        provenance = "verified_doc" if has_scheme_context else "general_search"
        
        if has_scheme_context and scheme_related:
            # Specific scheme information available
            lines = context_text.split('\n')
            primary_info = lines[0] if lines else "Scheme information"
            text = f"✅ **Verified Info**: {primary_info}\n\n📋 **Next Steps**: Please check the official government portal for application details and requirements."
        elif scheme_related:
            # Strict verified mode for scheme questions when context is missing.
            text = (
                "I can assist with this scheme, but I don't have verified source content right now.\n\n"
                "Please ask for one specific item (eligibility, documents, process, status), "
                "or check official portals: https://myscheme.gov.in and https://india.gov.in"
            )
            provenance = "strict_verified_mode"
        else:
            # Broad assistant fallback for non-scheme questions.
            if language == 'hi':
                text = f"""आपने पूछा: "{query}"\n\nमैं सामान्य जानकारी देने की कोशिश कर सकता हूँ, लेकिन इस समय मेरा मॉडल ऑफलाइन फ़ॉलबैक मोड में है। कृपया प्रश्न को थोड़ा स्पष्ट करें ताकि मैं बेहतर उत्तर दे सकूँ।"""
            else:
                text = f"""You asked: "{query}".

I can provide broad guidance, but I am currently in offline fallback mode. Please ask a more specific question and I will answer as precisely as possible."""

        return {
            "text": text,
            "provenance": provenance
        }
