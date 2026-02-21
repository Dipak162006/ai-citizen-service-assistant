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
        # Check if column exists
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='profile_photo';"))
        row = result.fetchone()
        if not row:
            db.session.execute(text("ALTER TABLE users ADD COLUMN profile_photo TEXT;"))
            db.session.commit()
            print("Successfully added profile_photo to users table.")
        else:
            print("Column profile_photo already exists.")
    except Exception as e:
        print(f"Error executing migration: {e}")
        db.session.rollback()
