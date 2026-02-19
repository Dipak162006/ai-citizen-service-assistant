import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def create_database():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    result = urlparse(db_url)
    username = result.username
    password = result.password
    host = result.hostname
    port = result.port
    dbname = result.path[1:]

    print(f"Attempting to connect to postgres to create '{dbname}'...")

    try:
        # Connect to 'postgres' database to create new db
        con = psycopg2.connect(
            dbname='postgres',
            user=username,
            host=host,
            password=password,
            port=port
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database {dbname}...")
            cur.execute(f"CREATE DATABASE {dbname}")
            print("Database created successfully!")
        else:
            print(f"Database {dbname} already exists.")
            
        cur.close()
        con.close()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nPossible fixes:")
        print("1. Check if PostgreSQL service is running.")
        print("2. Check username/password in .env.")
        print("3. Ensure you can connect to 'postgres' database.")

if __name__ == "__main__":
    create_database()
    
