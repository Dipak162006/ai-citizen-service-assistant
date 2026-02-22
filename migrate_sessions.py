import sys
import os

# Add the project root and backend directory to sys.path
root_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, 'backend')
sys.path.append(root_dir)
sys.path.append(backend_dir)

from backend.app import create_app
from backend.models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Check if columns exist first by trying to alter
        # PostgreSQL syntax for adding columns if they don't exist
        print("Checking/Updating user_sessions table...")
        
        # We'll use a transaction block
        db.session.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS user_id INTEGER;"))
        db.session.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS title VARCHAR(255);"))
        
        # Add foreign key constraint if it doesn't exist
        # This is trickier in Postgres without a function, but we can try basic alter
        try:
            db.session.execute(text("ALTER TABLE user_sessions ADD CONSTRAINT fk_user_sessions_user FOREIGN KEY (user_id) REFERENCES users(id);"))
        except Exception:
            db.session.rollback()
            print("Constraint might already exist, skipping...")
            # Re-open session if it rolled back
            db.session.begin()
            
        db.session.commit()
        print("Database schema updated successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error during migration: {e}")
