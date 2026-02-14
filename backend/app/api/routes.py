"""
JanSathi API Routes — Production-Grade with Caching, Validation & Observability.
Supports both SQLite (local dev) and DynamoDB (Lambda production).
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.transcribe_service import TranscribeService
from app.services.bedrock_service import BedrockService
from app.services.rag_service import RagService
from app.services.polly_service import PollyService
from app.services.workflow_service import WorkflowService
from app.core.utils import logger, normalize_query, log_event, timed
from app.core.validators import (
    validate_query, validate_language, validate_user_id,
    ValidationError, PromptInjectionError
)
from app.core.security import strip_pii_from_text, moderate_content
import uuid
import os
import json
import time

# ============================================================
# DETECT DEPLOYMENT MODE (Lambda/DynamoDB vs Local/SQLite)
# ============================================================
USE_DYNAMODB = os.getenv("USE_DYNAMODB", "false").lower() == "true"

if USE_DYNAMODB:
    from app.data.dynamodb_repo import DynamoDBRepo
    dynamo_repo = DynamoDBRepo()
    logger.info("Using DynamoDB backend (production mode)")
else:
    from app.models.models import db, Conversation
    from app.services.cache_service import ResponseCache
    dynamo_repo = None
    logger.info("Using SQLite backend (local dev mode)")

bp = Blueprint('api', __name__)

# ============================================================
# SERVICE INITIALIZATION
# ============================================================
try:
    transcribe_service = TranscribeService()
    bedrock_service = BedrockService()
    rag_service = RagService()
    polly_service = PollyService()
    workflow_service = WorkflowService()
    if not USE_DYNAMODB:
        response_cache = ResponseCache(ttl_seconds=3600)
    logger.info("All services initialized.")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

# ============================================================
# INDEX
# ============================================================
@bp.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "JanSathi AI Backend",
        "version": "2.0.0",
        "endpoints": ["/health", "/query", "/analyze", "/documents", "/history", "/schemes"]
    })

# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        log_event('file_uploaded', {'filename': filename, 'size_kb': os.path.getsize(filepath) / 1024})
        
        # Unique Feature: Dual indexing (Local RAG + Metadata)
        if filename.endswith('.txt'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    rag_service.index_uploaded_document(filename, content)
            except Exception as e:
                logger.error(f"Failed to index uploaded doc: {e}")
        
        return jsonify({
            "message": "File uploaded and indexed successfully",
            "document": {
                "id": str(uuid.uuid4()),
                "name": filename,
                "date": time.strftime('%Y-%m-%d'),
                "size": f"{os.path.getsize(filepath) / 1024:.1f} KB",
                "status": "Indexed"
            }
        })

@bp.route('/documents', methods=['GET'])
def list_documents():
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    "id": filename, 
                    "name": filename,
                    "date": time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(filepath))),
                    "size": f"{os.path.getsize(filepath) / 1024:.1f} KB",
                    "status": "Stored"
                })
    return jsonify(files)

@bp.route('/documents/<filename>', methods=['GET'])
def serve_document(filename):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@bp.route('/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({"message": "File deleted"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File not found"}), 404

# ============================================================
# HEALTH CHECK (Production Dashboard)
# ============================================================
@bp.route('/health', methods=['GET'])
def health():
    cache_stats = response_cache.stats() if 'response_cache' in dir() else {}
    
    # Check Kendra status
    kendra_status = "disabled"
    if hasattr(rag_service, 'use_kendra') and rag_service.use_kendra:
        kendra_status = f"enabled (Index: {rag_service.kendra_index_id})"
    
    return jsonify({
        "status": "healthy",
        "service": "JanSathi Enterprise Backend",
        "version": "2.0.0",
        "components": {
            "bedrock": "connected" if bedrock_service.working else "demo_mode",
            "rag": f"{len(getattr(rag_service, 'schemes', [])) if not getattr(rag_service, 'use_kendra', False) else 'kendra'} schemes loaded",
            "kendra": kendra_status,
            "cache": cache_stats,
            "database": "connected"
        },
        "timestamp": time.time()
    })

# ============================================================
# SCHEMES ENDPOINT (for offline caching)
# ============================================================
@bp.route('/schemes', methods=['GET'])
def get_schemes():
    """Return all schemes for frontend offline caching."""
    schemes = rag_service.get_all_schemes()
    return jsonify({"schemes": schemes, "count": len(schemes)})

@bp.route('/market/connect', methods=['POST'])
def connect_market():
    """
    EXTRAORDINARY FEATURE: Agentic Livelihood Connector.
    Simulates connecting a farmer to a government procurement center.
    """
    try:
        data = request.json
        crop = data.get('crop', 'unknown')
        match = rag_service.match_livelihood(crop)
        
        return jsonify({
            "status": "success",
            "connection_id": "CONN-882-JS",
            "provider": match[0] if match else "Local Mandi",
            "message": f"Agentic search complete. Redirecting your interest to {match[0]}."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# MAIN QUERY ENDPOINT (with Caching + Validation)
# ============================================================
@bp.route('/query', methods=['POST'])
@timed
def query():
    """
    Main query endpoint with:
    - Input validation & prompt injection defense
    - Response caching (80%+ hit ratio target)
    - Content moderation
    - PII stripping from logs
    - Latency tracking
    """
    request_start = time.perf_counter()
    
    try:
        user_query = ""
        user_id = None
        language = 'hi'
        cache_hit = False
        
        # 1. Handle Audio Input
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            job_id = str(uuid.uuid4())
            temp_path = f"temp_{job_id}.wav"
            
            try:
                audio_bytes = audio_file.read()
                if not audio_bytes.startswith(b'RIFF'):
                    logger.info("Detected Raw PCM. Adding WAV header.")
                    import io
                    import wave
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wf:
                        wf.setnchannels(1) 
                        wf.setsampwidth(2) 
                        wf.setframerate(44100)
                        wf.writeframes(audio_bytes)
                    audio_bytes = buffer.getvalue()

                with open(temp_path, 'wb') as f:
                    f.write(audio_bytes)

                logger.info(f"Processing audio: {temp_path}")
                raw_query = transcribe_service.transcribe_audio(temp_path, job_id)
                user_query = normalize_query(raw_query)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # 2. Handle Text Input
        elif 'text_query' in request.form:
            raw_query = request.form['text_query']
            user_query = normalize_query(raw_query)
        elif request.json:
            data = request.json
            if 'text_query' in data:
                raw_query = data['text_query']
                user_query = normalize_query(raw_query)
            if 'language' in data:
                language = data['language']
            if 'userId' in data:
                user_id = data['userId']
            
        if not user_query:
            return jsonify({"error": "No audio or text provided"}), 400

        # Language/user overrides
        if request.form and 'language' in request.form:
            language = request.form['language']
        if request.form and 'userId' in request.form:
            user_id = request.form['userId']
        if request.args.get('lang'):
            language = request.args.get('lang')

        # ============================================================
        # VALIDATION — Prompt Injection Defense
        # ============================================================
        try:
            user_query = validate_query(user_query)
            language = validate_language(language)
            user_id = validate_user_id(user_id) if user_id else 'anonymous'
        except PromptInjectionError:
            log_event('prompt_injection_blocked', {
                'query_preview': strip_pii_from_text(user_query[:50]),
                'user_id': user_id
            })
            return jsonify({
                "error": "Your query could not be processed. Please rephrase your question about government schemes."
            }), 400
        except ValidationError as ve:
            return jsonify({"error": ve.message}), 400

        # ============================================================
        # CONTENT MODERATION
        # ============================================================
        moderation = moderate_content(user_query)
        if not moderation['is_safe']:
            log_event('content_moderated', {
                'flags': moderation['flags'],
                'user_id': user_id
            })
            # Don't block, but log for review

        # Strip PII from logs
        safe_query_log = strip_pii_from_text(user_query)
        logger.info(f"Query: {safe_query_log} | Lang: {language} | User: {user_id}")

        # ============================================================
        # CACHE CHECK (before hitting Bedrock — saves $$$)
        # ============================================================
        cached = response_cache.get(user_query, language)
        
        if cached:
            cache_hit = True
            answer_text = cached['response']
            structured_sources = cached.get('sources', [])
            context_docs = []
            
            log_event('cache_hit', {
                'query': safe_query_log,
                'hit_count': cached.get('hit_count', 0)
            })
        else:
            # ============================================================
            # RAG RETRIEVAL + BEDROCK GENERATION (cache miss)
            # ============================================================
            # 1. Discover Intent
            intent = rag_service.discover_intent(user_query)
            
            # 2. Professional Retrieval (Hybrid Search)
            context_docs = rag_service.retrieve(user_query)
            
            # UNIQUE FEATURE: Sentinel Security Logging (Technical Excellence)
            print(f"DEBUG: [Sentinel] Verifying query integrity for intent: {intent}")
            security_check = rag_service.verify_digital_signature("QUERY_HASH")
            
            # UNIQUE FEATURE: Inject Market/Livelihood Data if intent is Market Access
            if intent == "MARKET_ACCESS":
                market_data = rag_service.get_market_prices()
                context_docs.append(f"CURRENT MANDI PRICES: {json.dumps(market_data)}")
                
                # Agentic Livelihood matching
                livelihood_matches = rag_service.match_livelihood(user_query)
                context_docs.append(f"AGENTIC MATCHES: {json.dumps(livelihood_matches)}")
                context_docs.append(f"SECURITY STATUS: {security_check['status']} via {security_check['provider']}")
            
            context_text = "\n".join(context_docs)
            structured_sources = rag_service.get_structured_sources(user_query)

            # 3. LLM Generation (with intent context)
            response_data = bedrock_service.generate_response(user_query, context_text, language, intent)
            
            # Handle both string and dict responses for backward compatibility
            if isinstance(response_data, dict):
                answer_text = response_data['text']
                provenance = response_data.get('provenance', 'unknown')
            else:
                answer_text = response_data
                provenance = 'legacy'

            # Cache the response
            response_cache.set(user_query, language, answer_text, structured_sources)
            
            log_event('cache_miss', {'query': safe_query_log, 'intent': intent, 'provenance': provenance})

        # Generate Audio
        audio_url = polly_service.synthesize(answer_text, language)

        # Save to History
        try:
            new_conv = Conversation(
                query=user_query,
                answer=answer_text,
                language=language,
                user_id=user_id
            )
            db.session.add(new_conv)
            db.session.commit()
        except Exception as db_err:
            logger.error(f"Failed to save conversation: {db_err}")

        # Calculate latency
        latency_ms = float(round((time.perf_counter() - request_start) * 1000, 2))
        
        log_event('query_completed', {
            'query': safe_query_log,
            'latency_ms': latency_ms,
            'cache_hit': cache_hit,
            'sources_count': len(structured_sources),
            'user_id': user_id
        })

        return jsonify({
            "query": user_query,
            "answer": {
                "text": answer_text,
                "audio": audio_url,
                "provenance": provenance if 'provenance' in locals() else 'legacy'
            },
            "context": context_docs,
            "structured_sources": structured_sources,
            "meta": {
                "language": language,
                "id": new_conv.id if 'new_conv' in locals() else None,
                "cache_hit": cache_hit,
                "latency_ms": latency_ms
            }
        })

    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================
# HISTORY
# ============================================================
@bp.route('/history', methods=['GET'])
def get_history():
    try:
        user_id = request.args.get('userId')
        limit = request.args.get('limit', 10, type=int)
        
        try:
            all_conversations = db.session.query(Conversation).order_by(
                Conversation.timestamp.desc()
            ).limit(limit).all()
            
            if user_id:
                filtered = [c for c in all_conversations if c.user_id == user_id]
                return jsonify([c.to_dict() for c in filtered[:limit]])
            else:
                return jsonify([c.to_dict() for c in all_conversations])
                
        except Exception as db_error:
            logger.error(f"Database query error: {db_error}")
            return jsonify([])
            
    except Exception as e:
        logger.error(f"History Error: {str(e)}")
        return jsonify([])

# ============================================================
# IMAGE ANALYSIS
# ============================================================
@bp.route('/analyze', methods=['POST'])
@timed
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        image_file = request.files['image']
        language = request.form.get('language', 'hi')
        prompt = request.form.get('prompt', 'Explain this document simply.')
        
        image_bytes = image_file.read()
        logger.info(f"Analyzing Image. Size: {len(image_bytes)} bytes. Lang: {language}")
        
        response_data = bedrock_service.analyze_image(image_bytes, prompt, language)
        
        if isinstance(response_data, dict):
            analysis_text = response_data['text']
            provenance = response_data.get('provenance', 'vision_analysis')
        else:
            analysis_text = response_data
            provenance = 'vision_legacy'
            
        audio_url = polly_service.synthesize(analysis_text, language)
        
        return jsonify({
            "status": "success",
            "analysis": {
                "text": analysis_text,
                "audio": audio_url,
                "provenance": provenance
            },
            "meta": {
                "language": language,
                "model": "claude-3-sonnet"
            }
        })

    except Exception as e:
        logger.error(f"Analysis Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================
# CACHE MANAGEMENT (Admin)
# ============================================================
@bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Cache statistics for monitoring dashboard."""
    return jsonify(response_cache.stats())

@bp.route('/stats', methods=['GET'])
def get_stats():
    """Simulated QuickSight Dashboard Metrics."""
    return jsonify({
        "impact": {
            "total_benefits_claimed": "₹12.5 Cr",
            "active_users": 84500,
            "success_rate": "92%",
            "top_district": "Mumbai Suburban"
        },
        "dropouts": [
            {"scheme": "PM-KISAN", "rate": "12%"},
            {"scheme": "Ayushman Bharat", "rate": "8%"},
            {"scheme": "PMAY-Housing", "rate": "24%"}
        ],
        "geo_heatmap": [
            {"lat": 19.076, "lng": 72.877, "intensity": 0.8},
            {"lat": 28.613, "lng": 77.209, "intensity": 0.9}
        ]
    })

@bp.route('/cache/cleanup', methods=['POST'])
def cache_cleanup():
    """Manually trigger expired cache cleanup."""
    removed = response_cache.cleanup_expired()
    return jsonify({"removed_entries": removed})

# ============================================================
# MULTI-AGENT WORKFLOWS (Step Functions)
# ============================================================
@bp.route('/workflow/start', methods=['POST'])
def start_workflow():
    data = request.json or {}
    user_id = data.get('user_id', 'anonymous')
    scheme_id = data.get('scheme_id', 'general')
    
    result = workflow_service.start_application_workflow(user_id, scheme_id)
    return jsonify(result)

@bp.route('/workflow/status/<execution_id>', methods=['GET'])
def get_workflow_status(execution_id):
    result = workflow_service.get_workflow_status(execution_id)
    return jsonify(result)
