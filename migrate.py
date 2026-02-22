import os
from flask import Flask
from backend.config import Config
from backend.models import db
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        # Check if oauth_provider column exists
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='oauth_provider';"))
        row = result.fetchone()
        if not row:
            db.session.execute(text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50);"))
            db.session.execute(text("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255);"))
            db.session.execute(text("ALTER TABLE users ADD CONSTRAINT unique_oauth_id UNIQUE (oauth_id);"))
            db.session.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"))
            db.session.commit()
            print("Successfully migrated users table for OAuth.")
        else:
            print("OAuth columns already exist.")
    except Exception as e:
        print(f"Error executing migration: {e}")
        db.session.rollback()
