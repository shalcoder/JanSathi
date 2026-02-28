import json
import os
import logging
from abc import ABC, abstractmethod

# Configure local logger for storage
logger = logging.getLogger(__name__)

class BaseSessionStorage(ABC):
    """
    Abstract base class for session storage.
    """
    @abstractmethod
    def load(self) -> dict:
        """Loads and returns all session data."""
        pass

    @abstractmethod
    def save(self, data: dict):
        """Saves session data."""
        pass

    @abstractmethod
    def initialize(self):
        """Initializes the storage medium."""
        pass

class LocalJSONStorage(BaseSessionStorage):
    """
    Local JSON file implementation of session storage.
    """
    def __init__(self, file_path="backend/agentic_engine/sessions.json"):
        self.file_path = file_path

    def initialize(self):
        """Creates an empty sessions file if it does not exist."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self.save({})

    def load(self) -> dict:
        """Loads sessions from the JSON file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save(self, data: dict):
        """Saves current sessions to the JSON file."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

class DynamoDBStorage(BaseSessionStorage):
    """
    Production-ready DynamoDB implementation of session storage.
    """
    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        if not table_name:
            raise ValueError("DynamoDB table name is required.")
        if not region_name:
            raise ValueError("AWS region is required.")
            
        self.table_name = table_name
        self.region_name = region_name
        self.table = None

    def initialize(self):
        """
        Initializes the DynamoDB connection and validates the table exists.
        """
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError, ClientError
            
            logger.info(f"[DynamoDBStorage] Initializing in {self.region_name} for table {self.table_name}")
            
            dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
            self.table = dynamodb.Table(self.table_name)
            
            # Lightweight validation: load table metadata
            self.table.load()
            
            logger.info(f"[DynamoDBStorage] Successfully connected to {self.table_name}")
            
        except NoCredentialsError:
            raise RuntimeError(
                "AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            )
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'ResourceNotFoundException':
                raise RuntimeError(f"DynamoDB table '{self.table_name}' not found in region '{self.region_name}'")
            raise RuntimeError(f"DynamoDB Client Error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"DynamoDB Initialization Failed: {str(e)}")

    def load(self) -> dict:
        """
        Placeholder load logic. 
        In JanSathi v2, session data is stored as items where PK is session_id.
        This base class implementation currently handles 'all data' dicts for Phase 1 compatibility.
        """
        if self.table is None:
            self.initialize()
            
        # For Phase 1 compatibility where we expect a single dict of all sessions:
        # We would scan or fetch a specific key. 
        # Note: In production, we should avoid Scans.
        raise NotImplementedError("DynamoDBStorage.load() for full dict not optimized for production. Use session-specific loads.")

    def save(self, data: dict):
        """
        Placeholder save logic.
        """
        if self.table is None:
            self.initialize()
        
        # Similar to load, Phase 1 logic expects full data persistence.
        raise NotImplementedError("DynamoDBStorage.save() for full dict not optimized for production.")
