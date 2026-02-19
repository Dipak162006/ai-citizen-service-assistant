# AI Citizen Service Assistant 🇮🇳

A full-stack AI agent to help citizens discover government schemes.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- PostgreSQL (Local or Cloud)
- OpenAI API Key

### 2. Backend Setup
1. Navigate to `/backend`:
   ```bash
   cd backend
   ```
2. Install dependencies (create a virtual environment first):
   ```bash
   pip install flask flask-sqlalchemy flask-cors openai psycopg2-binary
   ```
3. Set Environment Variables (Create `.env` or set in terminal):
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/ai_govt_schemes"
   export OPENAI_API_KEY="sk-..."
   ```
4. Seed the Database:
   ```bash
   python seeds.py
   ```
5. Run the Server:
   ```bash
   python app.py
   ```
   *Server will start at `http://localhost:5000`*

### 3. Frontend Setup
1. Open `frontend/index.html` in your browser.
   - You can just drag-and-drop the file or serve it via `python -m http.server` inside `/frontend`.
   - **Note**: Ensure the backend is running on port 5000.

## 🚀 Features
- **Hybrid RAG**: Uses SQL for strict eligibility (Age, Income) and LLM for natural language.
- **Persistent Sessions**: chat history is saved in Postgres.
- **Multilingual Support**: Prompts are designed to reply in the requested language.

## 🏆 Competition Tips
- **Demo Flow**: Start with "I am a farmer", then ask "What schemes for me?", then "How to apply?".
- **Highlight**: Show the *JSON* profile extraction in the debug console to prove it's real AI, not just keywords.
