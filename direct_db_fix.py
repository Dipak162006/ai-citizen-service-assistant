import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:Dipak123@localhost/ai_govt_schemes')

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Updating user_sessions table...")
    
    # Add columns if they don't exist
    cur.execute("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS user_id INTEGER;")
    cur.execute("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS title VARCHAR(255);")
    
    # Add foreign key constraint
    # We check if it exists first to avoid error
    cur.execute("""
        SELECT count(*) FROM pg_constraint WHERE conname = 'fk_user_sessions_user';
    """)
    if cur.fetchone()[0] == 0:
        print("Adding foreign key constraint...")
        cur.execute("ALTER TABLE user_sessions ADD CONSTRAINT fk_user_sessions_user FOREIGN KEY (user_id) REFERENCES users(id);")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database schema updated successfully via direct psycopg2!")
except Exception as e:
    print(f"Direct update error: {e}")
