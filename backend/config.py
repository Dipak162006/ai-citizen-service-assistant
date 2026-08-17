import os
import sys
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

for ca_var in ('CURL_CA_BUNDLE', 'REQUESTS_CA_BUNDLE', 'SSL_CERT_FILE'):
    if ca_var in os.environ and not os.path.exists(os.environ[ca_var]):
        del os.environ[ca_var]

load_dotenv()

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:Dipak123@localhost/ai_govt_schemes')

if db_url and db_url.startswith('postgresql'):
    try:
        from urllib.parse import urlparse
        import psycopg2
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            dbname=parsed.path[1:] or 'postgres',
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            connect_timeout=2
        )
        conn.close()
    except Exception:
        db_url = 'sqlite:///' + os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai_govt_schemes.db'))

class Config:
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Groq API Configuration
    # Uses compatible OpenAI chat completions endpoint
    GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key')
