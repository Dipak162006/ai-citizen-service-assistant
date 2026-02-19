import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:Dipak123@localhost/ai_govt_schemes')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Groq API Configuration
    # Uses compatible OpenAI chat completions endpoint
    GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key')
