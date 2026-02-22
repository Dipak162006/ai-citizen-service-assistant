from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=True) # Nullable for Google OAuth users
    oauth_provider = db.Column(db.String(50), nullable=True) # e.g., 'google'
    oauth_id = db.Column(db.String(255), nullable=True, unique=True)
    profile_photo = db.Column(db.Text, nullable=True) # Base64 encoded image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to profile
    profile = db.relationship('UserProfile', backref='user', uselist=False)

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    occupation = db.Column(db.String(100))
    income_range = db.Column(db.String(50))
    education = db.Column(db.String(100))
    age_group = db.Column(db.String(50))
    location = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Scheme(db.Model):
    __tablename__ = 'schemes'

    id = db.Column(db.Integer, primary_key=True)
    scheme_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    benefits = db.Column(db.Text, nullable=False)  # Description of benefits
    eligibility = db.Column(JSONB, nullable=False)  # {"income_limit": "2 lakh", ...}
    documents = db.Column(JSONB, nullable=False)  # ["Aadhaar", "Pan Card"]
    category = db.Column(db.String(100), nullable=False)
    target_group = db.Column(db.String(100))
    state = db.Column(db.String(100), default="All India")
    official_link = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.scheme_name,
            'description': self.description,
            'benefits': self.benefits,
            'eligibility': self.eligibility,
            'documents': self.documents,
            'category': self.category,
            'target_group': self.target_group,
            'state': self.state,
            'official_link': self.official_link
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_data = db.Column(JSONB, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to messages
    messages = db.relationship('ChatMessage', backref='session', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user_sessions.session_id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
