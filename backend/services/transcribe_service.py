import boto3
import time
import os
import json
import urllib.request
from botocore.exceptions import ClientError, NoCredentialsError
from utils import logger, retry_aws

class TranscribeService:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'jansathi-audio-demo-bucket')
        
        try:
            self.transcribe_client = boto3.client('transcribe', region_name=self.region)
            self.s3_client = boto3.client('s3', region_name=self.region)
            self.use_aws = True
        except NoCredentialsError:
            logger.warning("Transcribe Init Failed: No Credentials. Using Mock.")
            self.use_aws = False
        except Exception as e:
            logger.error(f"Transcribe Init Error: {e}")
            self.use_aws = False

    @retry_aws()
    def transcribe_audio(self, file_path=None, job_name=None, s3_uri=None):
        """
        Transcribes audio. 
        - If file_path is provided: Uploads to S3 -> Transcribes.
        - If s3_uri is provided: Directly Transcribes (Lambda flow).
        """
        if not self.use_aws:
            return self._mock_fallback()

        try:
            file_uri = s3_uri

            # 1. Upload file to S3 (Only if local path provided)
            if file_path and not s3_uri:
                object_name = f"audio/{job_name}.wav"
                logger.info(f"Uploading {file_path} to s3://{self.bucket_name}/{object_name}")
                self.s3_client.upload_file(file_path, self.bucket_name, object_name)
                file_uri = f"s3://{self.bucket_name}/{object_name}"
            
            if not file_uri:
                raise ValueError("Neither file_path nor s3_uri provided")

            # 2. Start Job
            logger.info(f"Starting Transcribe job: {job_name}")
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': file_uri},
                MediaFormat='wav', # simplistic assumption for demo
                LanguageCode='hi-IN' 
            )

            # 3. Poll for completion
            # 3. Poll for completion (Max wait: 60 seconds)
            max_retries = 30 
            retries = 0
            while retries < max_retries:
                status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                
                retries += 1
                time.sleep(2) # Wait 2 seconds before retry
            else:
                logger.error(f"Transcription Job {job_name} Timed Out")
                return self._mock_fallback()

            if job_status == 'COMPLETED':
                transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                with urllib.request.urlopen(transcript_uri) as response:
                    data = json.loads(response.read())
                    text = data['results']['transcripts'][0]['transcript']
                    logger.info(f"Transcription result: {text}")
                    return text
            else:
                logger.error(f"Transcription Failed: {status}")
                return self._mock_fallback()

        except ClientError as e:
            logger.error(f"AWS Transcribe/S3 Error: {e}")
            return self._mock_fallback()
        except Exception as e:
            logger.error(f"Unexpected Transcribe Error: {e}")
            return self._mock_fallback()

    def _mock_fallback(self):
        logger.info("Using Mock Transcription Fallback")
        return "मुझे प्रधान मंत्री आवास योजना के बारे में बताइए" # "Tell me about PM Housing Scheme"
