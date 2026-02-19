import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from app import create_app
from models import db, Scheme
from sqlalchemy.exc import OperationalError

load_dotenv()

def ensure_database():
    """Create database if it doesn't exist using safe raw connection."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL missing in .env")
        return False

    try:
        parsed = urlparse(db_url)
        dbname = parsed.path[1:]
        
        # Connect to 'postgres' system db
        con = psycopg2.connect(
            dbname='postgres',
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        if not cur.fetchone():
            print(f"🔨 Creating database '{dbname}'...")
            cur.execute(f"CREATE DATABASE {dbname}")
            print("✅ Database created.")
        else:
            print(f"✅ Database '{dbname}' exists.")
            
        cur.close()
        con.close()
        return True
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def init_and_seed():
    """Initialize tables and seed data using Flask-SQLAlchemy."""
    app = create_app()
    with app.app_context():
        try:
            print("🔨 Creating tables...")
            db.create_all()
            print("✅ Tables created.")
            
            # Check if schemes exist
            if Scheme.query.first():
                print("✅ Data already seeded.")
                return

            print("🌱 Seeding data...")
            # Sample Schemes
            schemes_data = [
                {
                    "name": "PM-KISAN Samman Nidhi",
                    "description": "Financial benefit of Rs. 6000/- per year to eligible farmer families.",
                    "benefits": {"amount": 6000, "frequency": "yearly", "installments": 3},
                    "eligibility_criteria": {"occupation": "Farmer", "land_holding_limit": 2},
                    "documents": ["Aadhaar", "Land Record", "Bank Account"],
                    "category": "Agriculture"
                },
                {
                    "name": "Pradhan Mantri Awas Yojana (Urban)",
                    "description": "Affordable housing for the urban poor with interest subsidies.",
                    "benefits": {"subsidy_amount": 267000, "type": "Interest Subsidy"},
                    "eligibility_criteria": {"income_group": "EWS/LIG/MIG", "location_type": "Urban"},
                    "documents": ["Aadhaar", "Income Certificate", "Property Documents"],
                    "category": "Housing"
                },
                {
                    "name": "Ayushman Bharat PM-JAY",
                    "description": "Health insurance coverage of up to Rs. 5 lakhs per family per year.",
                    "benefits": {"coverage": 500000, "type": "Health Insurance"},
                    "eligibility_criteria": {"income_status": "Low Income/BPL", "deprivation_criteria": "SECC 2011"},
                    "documents": ["Aadhaar", "Ration Card", "Family ID"],
                    "category": "Health"
                }
            ]
            
            for s in schemes_data:
                db.session.add(Scheme(**s))
            db.session.commit()
            print(f"✅ Seeded {len(schemes_data)} schemes.")
            
        except OperationalError as e:
            print(f"❌ Connection failed during seed: {e}")
            print("💡 Tip: Check if DATABASE_URL in .env is correct.")
        except Exception as e:
            print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    print("🚀 Starting Setup...")
    if ensure_database():
        init_and_seed()
    print("🏁 Setup Complete.")
