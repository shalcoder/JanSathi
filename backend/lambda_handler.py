import json
import uuid
from services.bedrock_service import BedrockService
from services.rag_service import RagService
from services.transcribe_service import TranscribeService
from services.polly_service import PollyService
from utils import setup_logging, logger, normalize_query

setup_logging()
bedrock_service = BedrockService()
rag_service = RagService()
transcribe_service = TranscribeService()
polly_service = PollyService()

SUPPORTED_LANGUAGES = {"hi", "ta", "te", "bn", "en"}

def lambda_handler(event, context):
    """
    JanSathi Lambda Entry Point
    Flow:
    Parse → [Transcribe] → Normalize → Retrieve → Generate → [Optional TTS] → Respond
    """
    try:
        body = event.get("body", event)
        if isinstance(body, str):
            body = json.loads(body)

        input_type = body.get("input_type", "text")
        input_content = body.get("input_content", "")
        language = body.get("language", "hi")
        response_mode = body.get("response_mode", "text")  # 👈 IMPORTANT

        if language not in SUPPORTED_LANGUAGES:
            language = "hi"

        # STEP 1: Input handling
        if input_type == "text":
            user_query = input_content
        elif input_type == "voice":
            if not input_content.startswith("s3://"):
                return _response(400, _public_error("Voice input requires valid S3 URI"))
            user_query = transcribe_service.transcribe_audio(
                s3_uri=input_content,
                job_name=str(uuid.uuid4()),
                language=language
            )
        else:
            return _response(400, _public_error("Invalid input type"))

        # STEP 2: Normalize
        normalized_query = normalize_query(user_query)
        if not normalized_query:
            return _response(400, _public_error("No valid query found"))

        # STEP 3: Retrieve
        documents = rag_service.retrieve(normalized_query)
        context_text = "\n".join(documents)

        # STEP 4: Generate
        answer_text = bedrock_service.generate_response(
            query=normalized_query,
            context=context_text,
            language=language
        )

        # STEP 5: Optional TTS
        audio_url = None
        if response_mode == "voice":
            audio_url = polly_service.synthesize(answer_text, language)

        return _response(200, {
            "status": "success",
            "answer": {
                "text": answer_text,
                "audio": audio_url
            },
            "meta": {
                "language": language,
                "input_type": input_type,
                "response_mode": response_mode
            }
        })

    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return _response(500, _public_error())

def _public_error(message=None):
    return {"status": "error", "message": message or "Something went wrong."}

def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
