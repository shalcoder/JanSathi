import json
import os
from abc import ABC, abstractmethod

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
    Placeholder implementation for DynamoDB session storage.
    """
    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        self.table_name = table_name
        self.region_name = region_name

    def initialize(self):
        """Placeholder for DynamoDB initialization."""
        raise NotImplementedError("DynamoDBStorage not implemented. AWS configuration required.")

    def load(self) -> dict:
        """Placeholder for DynamoDB load."""
        raise NotImplementedError("DynamoDBStorage not implemented. AWS configuration required.")

    def save(self, data: dict):
        """Placeholder for DynamoDB save."""
        raise NotImplementedError("DynamoDBStorage not implemented. AWS configuration required.")
