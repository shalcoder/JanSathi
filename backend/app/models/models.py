import os
import sys
# Add current directory to path for local module resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), index=True) 
    query = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='hi')
    provenance = db.Column(db.JSON) # Store AI explainability data
    confidence = db.Column(db.Float) # For JanSathi Pulse metrics
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query": self.query,
            "answer": self.answer,
            "language": self.language,
            "provenance": self.provenance,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }

class UserProfile(db.Model):
    """Anonymized citizen profile for benefit gap analysis."""
    id = db.Column(db.String(100), primary_key=True) # Clerk User ID
    location_state = db.Column(db.String(50))
    location_district = db.Column(db.String(50))
    occupation = db.Column(db.String(100))
    income_bracket = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "location_state": self.location_state,
            "location_district": self.location_district,
            "occupation": self.occupation,
            "income_bracket": self.income_bracket,
            "created_at": self.created_at.isoformat()
        }

class AuditLog(db.Model):
    """Human-in-the-loop audit data."""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    admin_id = db.Column(db.String(100))
    action = db.Column(db.String(50)) # 'approved', 'flagged', 'edited'
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "admin_id": self.admin_id,
            "action": self.action,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat()
        }

class SchemeApplication(db.Model):
    """Tracks status of simulated/real applications."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), index=True)
    scheme_name = db.Column(db.String(200))
    status = db.Column(db.String(50)) # 'pending', 'verified', 'completed'
    execution_id = db.Column(db.String(50)) # For tracking simulation progress
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scheme_name": self.scheme_name,
            "status": self.status,
            "execution_id": self.execution_id,
            "updated_at": self.updated_at.isoformat()
        }

class Scheme(db.Model):
    """Government Scheme Data"""
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    benefit = db.Column(db.String(200))
    ministry = db.Column(db.String(200))
    link = db.Column(db.String(500))
    keywords = db.Column(db.JSON) # List of strings
    category = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "benefit": self.benefit,
            "ministry": self.ministry,
            "link": self.link,
            "keywords": self.keywords,
            "category": self.category
        }

class UserDocument(db.Model):
    """User Uploaded Documents"""
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(100), index=True)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100)) # e.g., Aadhaar, Income Cert
    verification_status = db.Column(db.String(50), default='pending') # pending, verified, rejected
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "type": self.document_type,
            "status": self.verification_status,
            "date": self.uploaded_at.isoformat()
        }

class CommunityPost(db.Model):
    """Local Forum Posts"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default='Anonymous')
    author_role = db.Column(db.String(100)) # e.g., Sarpanch, Farmer
    location = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "author_role": self.author_role,
            "location": self.location,
            "likes": self.likes,
            "comments": self.comments_count,
            "time": self.timestamp.strftime("%Y-%m-%d %H:%M")
        }
