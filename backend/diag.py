import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

load_dotenv()

db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL found: {'Yes' if db_url else 'No'}")

if not db_url:
    exit(1)

# Masked URL
try:
    parsed = urlparse(db_url)
    masked = db_url.replace(parsed.password, '****') if parsed.password else db_url
    print(f"URL: {masked}")
    
    
    # 0. Test Psycopg2 to 'postgres' DB (Baseline)
    print("\nAttempting Direct Psycopg2 Connection to 'postgres'...")
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
        print("✅ Psycopg2 Connection to 'postgres' Successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Psycopg2 Connection to 'postgres' Failed: {e}")

    # 1. Test Psycopg2 (Direct) to Target DB
    print(f"\nAttempting Direct Psycopg2 Connection to '{parsed.path[1:]}'...")
    try:
        conn = psycopg2.connect(
            dbname=parsed.path[1:],

            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
        print("✅ Psycopg2 Connection Successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Psycopg2 Connection Failed: {e}")

    # 2. Test SQLAlchemy
    print("\nAttempting SQLAlchemy Connection...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ SQLAlchemy Connection Successful! Result: {result.scalar()}")
    except Exception as e:
        print(f"❌ SQLAlchemy Connection Failed: {e}")
        
except Exception as e:
    print(f"Error parsing URL: {e}")
