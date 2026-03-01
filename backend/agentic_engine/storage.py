import json
import os
import time
import logging
from abc import ABC, abstractmethod

# Configure local logger for storage
logger = logging.getLogger(__name__)

# TTL for sessions: 24 hours by default (configurable via env)
_SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", str(60 * 60 * 24)))

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

    DynamoDB Table Schema:
      - PK: session_id (String) — partition key
      - expires_at (Number)    — TTL attribute (set in DynamoDB table settings)
      - data (Map)             — full session payload

    TTL Configuration:
      Enable TTL on the table with attribute name: expires_at
      Sessions auto-delete after SESSION_TTL_SECONDS (default: 86400 = 24h)
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

    def put_session(self, session_id: str, session_data: dict):
        """
        Write a single session item to DynamoDB with TTL.
        The expires_at field enables automatic cleanup via DynamoDB TTL.
        """
        if self.table is None:
            self.initialize()
        expires_at = int(time.time()) + _SESSION_TTL_SECONDS
        self.table.put_item(Item={
            "session_id": session_id,
            "data": session_data,
            "expires_at": expires_at,  # DynamoDB TTL attribute
        })
        logger.debug(f"[DynamoDBStorage] Session {session_id} written, TTL={expires_at}")

    def get_session(self, session_id: str) -> dict:
        """
        Read a single session item from DynamoDB.
        Returns None if not found or expired.
        """
        if self.table is None:
            self.initialize()
        response = self.table.get_item(Key={"session_id": session_id})
        item = response.get("Item")
        if not item:
            return None
        # Guard: local expiry check (DynamoDB TTL can lag up to 48h)
        expires_at = item.get("expires_at", 0)
        if expires_at and int(time.time()) > expires_at:
            logger.info(f"[DynamoDBStorage] Session {session_id} locally expired (TTL={expires_at})")
            return None
        return item.get("data", {})

    def load(self) -> dict:
        """
        Full-table load — intentionally NOT supported in production.
        Use get_session(session_id) for per-session access.
        """
        raise NotImplementedError(
            "DynamoDBStorage.load() for full dict not optimized for production. "
            "Use get_session(session_id) instead."
        )

    def save(self, data: dict):
        """
        Full-table save — intentionally NOT supported in production.
        Use put_session(session_id, data) instead.
        """
        raise NotImplementedError(
            "DynamoDBStorage.save() for full dict not optimized for production. "
            "Use put_session(session_id, data) instead."
        )
