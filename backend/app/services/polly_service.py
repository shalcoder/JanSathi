import sys
import os
import uuid
import boto3
from botocore.exceptions import NoCredentialsError

# Add parent directory to path to resolve local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.utils import logger, retry_aws

# Language → Polly configuration (Optimized for Neural quality)
VOICE_MAP = {
    "hi": {"voice": "Kajal", "engine": "neural"}, # Hindi (Neural)
    "en": {"voice": "Kajal", "engine": "neural"}, # Indian English (Neural)
    "ta": {"voice": "Arathi", "engine": "standard"}, # Tamil
    "te": {"voice": "Shruti", "engine": "standard"}, # Telugu (Fallback to Shruti, Arathi doesn't support TE natively but AWS Polly added Shruti as TE/KN fallback historically, actually AWS Polly has 'Shruti' for Telugu and 'Aditi' for Hindi. Wait, let's use Shruti)
    "kn": {"voice": "Shruti", "engine": "standard"}, # Kannada
    "ml": {"voice": "Kajal", "engine": "neural"}, # Malayalam (Fallback to Hindi/English neural)
    "mr": {"voice": "Kajal", "engine": "neural"}, # Marathi (Fallback to Hindi neural)
    "gu": {"voice": "Kajal", "engine": "neural"}, # Gujarati (Fallback to Hindi neural)
    "bn": {"voice": "Kajal", "engine": "neural"}, # Bengali (Fallback to Hindi neural)
    "pa": {"voice": "Kajal", "engine": "neural"}, # Punjabi (Fallback to Hindi neural)
    "or": {"voice": "Kajal", "engine": "neural"}, # Odia (Fallback to Hindi neural)
    "as": {"voice": "Kajal", "engine": "neural"}  # Assamese (Fallback to Hindi neural)
}

class PollyService:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

        try:
            self.polly_client = boto3.client("polly", region_name=self.region)
            self.s3_client = boto3.client("s3", region_name=self.region)
            self.use_aws = True
        except NoCredentialsError:
            logger.warning("Polly Init Failed: No AWS credentials. Using mock.")
            self.use_aws = False

    @retry_aws()
    def synthesize(self, text: str, language: str = "hi"):
        """
        Convert text to speech, store MP3 in S3, return presigned URL.
        """
        if not self.use_aws:
            return self._mock_fallback()

        if not text:
            return None

        try:
            cfg = VOICE_MAP.get(language, VOICE_MAP["hi"])
            voice_id = cfg["voice"]
            engine = cfg["engine"]

            # 1️⃣ Synthesize speech
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine=engine
            )

            if "AudioStream" not in response:
                logger.error("Polly response missing AudioStream")
                return None

            # 2️⃣ Save to S3
            if not self.bucket_name:
                logger.warning("S3_BUCKET_NAME not set")
                return None

            key = f"tts/{uuid.uuid4()}.mp3"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=response["AudioStream"].read(),
                ContentType="audio/mpeg"
            )

            # 3️⃣ Generate presigned URL
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=3600
            )

            logger.info("Generated Polly audio successfully")
            return url

        except Exception as e:
            logger.error(f"Polly synthesis error: {e}")
            return self._mock_fallback()

    def _mock_fallback(self):
        # Return None to avoid playing random music
        logger.warning("Polly unavailable. Returning no audio.")
        return None
