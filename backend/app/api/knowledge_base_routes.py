"""
Knowledge Base API Routes
=========================
Endpoints for PDF upload and intelligent querying with caching.

Routes:
- POST /api/kb/upload - Upload PDF to Knowledge Base
- POST /api/kb/query - Query with caching
- GET /api/kb/stats - Cache statistics
- DELETE /api/kb/cache - Invalidate cache
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

from app.services.knowledge_base_service import KnowledgeBaseService
from app.core.utils import log_event, logger

kb_bp = Blueprint('knowledge_base', __name__, url_prefix='/api/kb')

# Initialize service
kb_service = KnowledgeBaseService()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@kb_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Upload PDF to Bedrock Knowledge Base.
    
    Request:
        - file: PDF file (multipart/form-data)
        - user_id: User identifier (optional)
        - document_type: Type of document (optional)
    
    Response:
        {
            "document_id": "user_123_1234567890_document.pdf",
            "s3_uri": "s3://bucket/path/to/document.pdf",
            "status": "uploaded",
            "message": "Document uploaded successfully"
        }
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Get user context
        user_id = request.form.get('user_id', 'anonymous')
        document_type = request.form.get('document_type', 'general')
        
        # Read file bytes
        file_bytes = file.read()
        
        # Validate file size (max 10MB)
        if len(file_bytes) > 10 * 1024 * 1024:
            return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Upload to Knowledge Base
        result = kb_service.upload_pdf(file_bytes, filename, user_id)
        
        if result.get('status') == 'failed':
            return jsonify(result), 500
        
        log_event('kb_upload_success', {
            'user_id': user_id,
            'filename': filename,
            'document_type': document_type,
            'size_bytes': len(file_bytes)
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e), 'status': 'failed'}), 500


@kb_bp.route('/query', methods=['POST'])
def query_knowledge_base():
    """
    Query Knowledge Base with intelligent caching.
    
    Request:
        {
            "question": "What is PM-KISAN scheme?",
            "language": "hi",
            "user_context": {
                "occupation": "farmer",
                "location_state": "UP"
            },
            "max_results": 3
        }
    
    Response:
        {
            "answer": "PM-KISAN is...",
            "sources": [
                {
                    "text": "Source excerpt...",
                    "score": 0.95,
                    "source": "s3://bucket/doc.pdf",
                    "type": "knowledge_base"
                }
            ],
            "cached": false,
            "cost_saved": 0.0,
            "query_time": "2024-03-07T10:30:00",
            "language": "hi"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        language = data.get('language', 'hi')
        user_context = data.get('user_context')
        max_results = data.get('max_results', 3)
        
        # Query with caching
        result = kb_service.query(
            question=question,
            language=language,
            user_context=user_context,
            max_results=max_results
        )
        
        log_event('kb_query', {
            'question_length': len(question),
            'language': language,
            'cached': result.get('cached', False),
            'sources_count': len(result.get('sources', []))
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({'error': str(e)}), 500


@kb_bp.route('/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache performance statistics.
    
    Response:
        {
            "total_cached_queries": 150,
            "cached_last_24h": 45,
            "cache_ttl_hours": 24,
            "language_distribution": {
                "hi": 100,
                "en": 50
            },
            "estimated_cost_saved": 3.00,
            "cache_enabled": true
        }
    """
    try:
        stats = kb_service.get_cache_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500


@kb_bp.route('/cache', methods=['DELETE'])
def invalidate_cache():
    """
    Invalidate cache entries.
    
    Query Parameters:
        - query: Specific query to invalidate (optional)
        - language: Specific language to invalidate (optional)
        - all: Set to 'true' to clear all cache
    
    Response:
        {
            "deleted": 10,
            "status": "success"
        }
    """
    try:
        query = request.args.get('query')
        language = request.args.get('language')
        clear_all = request.args.get('all', 'false').lower() == 'true'
        
        if clear_all:
            result = kb_service.invalidate_cache()
        else:
            result = kb_service.invalidate_cache(query=query, language=language)
        
        log_event('kb_cache_invalidated', {
            'query': query,
            'language': language,
            'clear_all': clear_all,
            'deleted': result.get('deleted', 0)
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        return jsonify({'error': str(e)}), 500


@kb_bp.route('/cache/cleanup', methods=['POST'])
def cleanup_old_cache():
    """
    Remove old cache entries.
    
    Request:
        {
            "days": 30
        }
    
    Response:
        {
            "deleted": 25,
            "cutoff_days": 30,
            "status": "success"
        }
    """
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        result = kb_service.cleanup_old_cache(days=days)
        
        log_event('kb_cache_cleanup', {
            'days': days,
            'deleted': result.get('deleted', 0)
        })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'error': str(e)}), 500


@kb_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check Knowledge Base service health.
    
    Response:
        {
            "status": "healthy",
            "kb_id": "XXXXX",
            "cache_enabled": true,
            "working": true
        }
    """
    return jsonify({
        'status': 'healthy' if kb_service.working else 'degraded',
        'kb_id': kb_service.kb_id,
        'cache_enabled': kb_service.enable_cache,
        'working': kb_service.working,
        's3_bucket': kb_service.s3_bucket
    }), 200
