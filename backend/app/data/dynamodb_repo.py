"""
JanSathi DynamoDB Repository — Production Data Layer
Replaces SQLite for conversations and cache when deployed to AWS.

Usage:
    repo = DynamoDBRepo()
    
    # Save conversation
    repo.save_conversation(user_id, query, answer, language)
    
    # Get history
    conversations = repo.get_history(user_id, limit=10)
    
    # Cache operations
    repo.cache_set(query_hash, response_data, ttl_seconds=3600)
    cached = repo.cache_get(query_hash)
"""
import os
import time
import uuid
import hashlib
import json
import boto3
from botocore.exceptions import ClientError
from app.core.utils import log_event, logger


class DynamoDBRepo:
    """
    DynamoDB data layer for JanSathi.
    Manages Conversations table and Cache table.
    """

    def __init__(self):
        self.region = os.getenv("AWS_REGION_NAME", os.getenv("AWS_REGION", "us-east-1"))
        self.conversations_table_name = os.getenv("DYNAMODB_CONVERSATIONS_TABLE", "JanSathi-Conversations")
        self.cache_table_name = os.getenv("DYNAMODB_CACHE_TABLE", "JanSathi-Cache")

        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.conversations_table = self.dynamodb.Table(self.conversations_table_name)
        self.cache_table = self.dynamodb.Table(self.cache_table_name)

        logger.info(f"DynamoDB initialized: {self.conversations_table_name}, {self.cache_table_name}")

    # ============================================================
    # CONVERSATIONS
    # ============================================================
    def save_conversation(self, user_id: str, query: str, answer: str, language: str = "hi") -> dict:
        """Save a conversation to DynamoDB."""
        conversation_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        ttl = int(time.time()) + (90 * 24 * 3600)  # 90-day TTL

        item = {
            "UserId": user_id or "anonymous",
            "Timestamp": timestamp,
            "ConversationId": conversation_id,
            "Query": query,
            "Answer": answer,
            "Language": language,
            "ttl": ttl,
        }

        try:
            self.conversations_table.put_item(Item=item)
            log_event("conversation_saved", {
                "conversation_id": conversation_id,
                "user_id": user_id,
            })
            return item
        except ClientError as e:
            logger.error(f"DynamoDB save error: {e}")
            return {}

    def get_history(self, user_id: str, limit: int = 10) -> list:
        """Get conversation history for a user, sorted by timestamp (newest first)."""
        try:
            response = self.conversations_table.query(
                KeyConditionExpression="UserId = :uid",
                ExpressionAttributeValues={":uid": user_id or "anonymous"},
                ScanIndexForward=False,  # Newest first
                Limit=limit,
            )
            return [
                {
                    "id": item.get("ConversationId"),
                    "query": item.get("Query"),
                    "answer": item.get("Answer"),
                    "language": item.get("Language"),
                    "timestamp": item.get("Timestamp"),
                }
                for item in response.get("Items", [])
            ]
        except ClientError as e:
            logger.error(f"DynamoDB query error: {e}")
            return []

    # ============================================================
    # CACHE (Response Caching via DynamoDB)
    # ============================================================
    @staticmethod
    def _cache_key(query: str, language: str = "hi") -> str:
        """Generate a deterministic cache key from query + language."""
        normalized = query.strip().lower()
        return hashlib.sha256(f"{normalized}:{language}".encode()).hexdigest()[:32]

    def cache_get(self, query: str, language: str = "hi") -> dict | None:
        """Get a cached response. Returns None if expired or not found."""
        key = self._cache_key(query, language)
        try:
            response = self.cache_table.get_item(Key={"QueryHash": key})
            item = response.get("Item")

            if not item:
                return None

            # Check if TTL has passed (DynamoDB TTL is eventually consistent)
            if item.get("ttl", 0) < int(time.time()):
                return None

            log_event("dynamodb_cache_hit", {"key": key[:8]})

            return {
                "response": item.get("Response", ""),
                "sources": json.loads(item.get("Sources", "[]")),
                "hit_count": int(item.get("HitCount", 0)),
            }
        except ClientError as e:
            logger.error(f"DynamoDB cache get error: {e}")
            return None

    def cache_set(
        self,
        query: str,
        language: str,
        response_text: str,
        sources: list = None,
        ttl_seconds: int = 3600,
    ) -> None:
        """Cache a response in DynamoDB with TTL."""
        key = self._cache_key(query, language)
        try:
            self.cache_table.put_item(
                Item={
                    "QueryHash": key,
                    "Query": query[:200],  # Store truncated query for debugging
                    "Language": language,
                    "Response": response_text,
                    "Sources": json.dumps(sources or []),
                    "HitCount": 0,
                    "ttl": int(time.time()) + ttl_seconds,
                    "CreatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
            log_event("dynamodb_cache_set", {"key": key[:8]})
        except ClientError as e:
            logger.error(f"DynamoDB cache set error: {e}")

    def cache_stats(self) -> dict:
        """Get basic cache statistics (scan — use sparingly)."""
        try:
            response = self.cache_table.scan(
                Select="COUNT",
            )
            return {
                "total_entries": response.get("Count", 0),
                "table": self.cache_table_name,
                "backend": "dynamodb",
            }
        except ClientError:
            return {"total_entries": 0, "backend": "dynamodb"}
