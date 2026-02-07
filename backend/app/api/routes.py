from flask import Blueprint, request, jsonify, current_app
from app.models.models import db, Conversation
from app.services.transcribe_service import TranscribeService
from app.services.bedrock_service import BedrockService
from app.services.rag_service import RagService
from app.services.polly_service import PollyService
from app.core.utils import logger, normalize_query
import uuid
import os
import json

bp = Blueprint('api', __name__)

# Initialize services (lazy loading or global?)
# For simplicity, we'll instantiate them here or better, attached to app context in main.
# Let's instantiate normally for now to keep it simple as they were before.
try:
    transcribe_service = TranscribeService()
    bedrock_service = BedrockService()
    rag_service = RagService()
    polly_service = PollyService()
    logger.info("Services initialized in Blueprint.")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

@bp.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to JanSathi AI API (Enterprise Edition)",
        "docs": "/health, /query, /history, /analyze"
    })

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "JanSathi Enterprise Backend"})

@bp.route('/query', methods=['POST'])
def query():
    """
    Main endpoint for query processing.
    """
    try:
        user_query = ""
        user_id = None
        language = 'hi' 
        
        # 1. Handle Audio
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
        
        # 2. Handle Text
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

        # Language overrides
        if request.form and 'language' in request.form:
             language = request.form['language']
        if request.form and 'userId' in request.form:
             user_id = request.form['userId']
        if request.args.get('lang'):
            language = request.args.get('lang')

        logger.info(f"User Query: {user_query} | Language: {language}")

        # 3. Retrieve Context
        context_docs = rag_service.retrieve(user_query)
        context_text = "\n".join(context_docs)
        structured_sources = rag_service.get_structured_sources(user_query)

        # 4. Generate Answer
        answer_text = bedrock_service.generate_response(user_query, context_text, language)

        # 5. Generate Audio
        audio_url = polly_service.synthesize(answer_text, language)

        # 6. Save to History
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

        return jsonify({
            "query": user_query,
            "answer": {
                "text": answer_text,
                "audio": audio_url
            },
            "context": context_docs,
            "structured_sources": structured_sources,
            "meta": {
                "language": language,
                "id": new_conv.id if 'new_conv' in locals() else None
            }
        })

    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/history', methods=['GET'])
def get_history():
    try:
        user_id = request.args.get('userId')
        limit = request.args.get('limit', 10, type=int)
        
        # Simple approach - get all conversations and filter in Python if needed
        try:
            all_conversations = db.session.query(Conversation).order_by(Conversation.timestamp.desc()).limit(limit).all()
            
            # Filter by user_id if provided
            if user_id:
                filtered_conversations = [conv for conv in all_conversations if conv.user_id == user_id]
                return jsonify([conv.to_dict() for conv in filtered_conversations[:limit]])
            else:
                return jsonify([conv.to_dict() for conv in all_conversations])
                
        except Exception as db_error:
            logger.error(f"Database query error: {db_error}")
            # Return empty history if database issues
            return jsonify([])
            
    except Exception as e:
        logger.error(f"History Error: {str(e)}")
        # Return empty array instead of error for better UX
        return jsonify([])

@bp.route('/analyze', methods=['POST'])
def analyze():
    # ... (existing analyze code)
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        image_file = request.files['image']
        language = request.form.get('language', 'hi')
        prompt = request.form.get('prompt', 'Explain this document simply.')
        
        image_bytes = image_file.read()
        logger.info(f"Analyzing Image. Size: {len(image_bytes)} bytes. Lang: {language}")
        
        analysis_text = bedrock_service.analyze_image(image_bytes, prompt, language)
        audio_url = polly_service.synthesize(analysis_text, language)
        
        return jsonify({
            "status": "success",
            "analysis": {
                "text": analysis_text,
                "audio": audio_url
            },
            "meta": {
                "language": language,
                "model": "claude-3-sonnet"
            }
        })

    except Exception as e:
        logger.error(f"Analysis Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/market-rates', methods=['GET'])
def get_market_rates():
    """
    Mock endpoint for agricultural commodity prices.
    """
    try:
        rates = [
            {"crop": "Wheat (Gehun)", "market": "Lucknow", "price": "2450", "unit": "quintal", "change": "+12", "trend": "up"},
            {"crop": "Rice (Chawal)", "market": "Patna", "price": "3100", "unit": "quintal", "change": "-5", "trend": "down"},
            {"crop": "Potato (Aloo)", "market": "Agra", "price": "1200", "unit": "quintal", "change": "+45", "trend": "up"},
            {"crop": "Onion (Pyaz)", "market": "Nasik", "price": "2800", "unit": "quintal", "change": "+110", "trend": "up"}
        ]
        return jsonify(rates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
