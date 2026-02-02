from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from dotenv import load_dotenv

# Load Env
load_dotenv()

# Import Services
from services.transcribe_service import TranscribeService
from services.bedrock_service import BedrockService
from services.rag_service import RagService

app = Flask(__name__)
CORS(app)

# Initialize Services
transcribe_service = TranscribeService()
bedrock_service = BedrockService()
rag_service = RagService()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "JanSathi Backend"})

@app.route('/query', methods=['POST'])
def query():
    """
    Expects:
    - 'audio_file': (Optional) Multipart file
    - 'text_query': (Optional) String
    - 'language': (Optional) 'hi' or 'en'
    """
    try:
        user_query = ""
        
        # 1. Handle Audio
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            job_id = str(uuid.uuid4())
            temp_path = f"temp_{job_id}.wav"
            audio_file.save(temp_path)
            
            print(f"Transcribing audio: {temp_path}")
            user_query = transcribe_service.transcribe_audio(temp_path, job_id)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # 2. Handle Text (Fallback or Direct)
        elif 'text_query' in request.form:
            user_query = request.form['text_query']
        elif request.json and 'text_query' in request.json:
            user_query = request.json['text_query']
            
        if not user_query:
            return jsonify({"error": "No audio or text provided"}), 400

        print(f"User Query: {user_query}")

        # 3. Retrieve Context (RAG)
        context_docs = rag_service.retrieve(user_query)
        context_text = "\n".join(context_docs)
        print(f"Retrieved Context: {context_text}")

        # 4. Generate Answer (Bedrock)
        answer = bedrock_service.generate_response(user_query, context_text)
        print(f"AI Answer: {answer}")

        return jsonify({
            "query": user_query,
            "answer": answer,
            "context": context_docs
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible by Emulator/Phone on same network
    app.run(host='0.0.0.0', port=5000, debug=True)
