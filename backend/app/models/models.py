import os
import sys
# Add current directory to path for local module resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=True) # For future auth integration
    query = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='hi')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "query": self.query,
            "answer": self.answer,
            "language": self.language,
            "timestamp": self.timestamp.isoformat()
        }
