from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from dotenv import load_dotenv

# Import Services
from services.transcribe_service import TranscribeService
from services.bedrock_service import BedrockService
from services.rag_service import RagService
from services.polly_service import PollyService
from utils import setup_logging, logger, normalize_query

# Load Env
load_dotenv()
setup_logging()

app = Flask(__name__)
CORS(app)

# Initialize Services
try:
    transcribe_service = TranscribeService()
    bedrock_service = BedrockService()
    rag_service = RagService()
    polly_service = PollyService()
    logger.info("Services initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "JanSathi Backend (AWS Stack)"})

@app.route('/query', methods=['POST'])
def query():
    """
    Main endpoint for query processing.
    """
    try:
        user_query = ""
        # Default language to Hindi
        language = 'hi' 
        
        # 1. Handle Audio
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            job_id = str(uuid.uuid4())
            temp_path = f"temp_{job_id}.wav"
            
            try:
                # Read bytes to check header
                audio_bytes = audio_file.read()
                
                # Check for RIFF header (WAV)
                if not audio_bytes.startswith(b'RIFF'):
                    logger.info("Detected Raw PCM. Adding WAV header (44.1kHz, Mono, 16-bit).")
                    import io
                    import wave
                    
                    buffer = io.BytesIO()
                    # Assume Flutter 'record' default: 16-bit PCM, 44100Hz, Mono
                    with wave.open(buffer, 'wb') as wf:
                        wf.setnchannels(1) 
                        wf.setsampwidth(2) # 2 bytes = 16 bit
                        wf.setframerate(44100)
                        wf.writeframes(audio_bytes)
                    
                    audio_bytes = buffer.getvalue()

                # Write finalized bytes to disk
                with open(temp_path, 'wb') as f:
                    f.write(audio_bytes)

                logger.info(f"Processing audio: {temp_path}")
                # For audio input, we could potentially detect language, but defaulting to 'hi' or request param
                raw_query = transcribe_service.transcribe_audio(temp_path, job_id)
                user_query = normalize_query(raw_query)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info(f"Cleaned up temp file: {temp_path}")
        
        # 2. Handle Text
        elif 'text_query' in request.form:
            raw_query = request.form['text_query']
            user_query = normalize_query(raw_query)
        elif request.json:
            data = request.json
            if 'text_query' in data:
                raw_query = data['text_query']
                user_query = normalize_query(raw_query)
            # Safe extraction of language
            if 'language' in data:
                language = data['language']
            
        if not user_query:
            return jsonify({"error": "No audio or text provided"}), 400

        # Handle Language override from Form or Query Param if not found in JSON
        if request.form and 'language' in request.form:
             language = request.form['language']
        
        # Check query param as fallback
        if request.args.get('lang'):
            language = request.args.get('lang')

        logger.info(f"User Query: {user_query} | Language: {language}")

        # 3. Retrieve Context (Kendra/Mock)
        context_docs = rag_service.retrieve(user_query)
        context_text = "\n".join(context_docs)
        logger.info(f"Retrieved Context Length: {len(context_text)}")

        # 4. Generate Answer (Bedrock)
        answer_text = bedrock_service.generate_response(user_query, context_text, language)
        logger.info(f"Generated Answer: {answer_text}")

        # 5. Generate Audio (Polly)
        audio_url = polly_service.synthesize(answer_text, language)

        return jsonify({
            "query": user_query,
            "answer": {
                "text": answer_text,
                "audio": audio_url
            },
            "context": context_docs,
            "meta": {
                "language": language
            }
        })

    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
