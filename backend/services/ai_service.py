import os
from groq import Groq
import json
from config import Config

# Initialize Groq Client
client = None
if Config.GROQ_API_KEY:
    try:
        client = Groq(api_key=Config.GROQ_API_KEY)
    except Exception as e:
        print(f"Error initializing Groq client: {e}")

def call_llm(messages, json_mode=False):
    """
    Helper function to call Groq API using official SDK.
    """
    if not client:
        print("❌ Error: Groq Client not initialized (Check API Key)")
        return None

    try:
        # Prepare parameters
        params = {
            "model": Config.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.5
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}

        # Call API
        chat_completion = client.chat.completions.create(**params)
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"❌ Error calling Groq: {e}")
        return None

def extract_profile(chat_history):
    """
    Extracts structured user profile from chat history using Groq (JSON mode).
    """
    system_prompt = """
    You are an expert data extractor for a government scheme assistant.
    Analyze the user's input and extract the following details into a JSON object.
    Use null if the information is not explicitly provided.
    
    Output JSON Keys:
    - age: (int or string, e.g., "25" or "20-30")
    - occupation: (string, e.g., "Farmer", "Student", "Unemployed")
    - income_range: (string, normalized annual income, e.g., "0-1 Lakh", "1-2.5 Lakh")
    - education: (string, e.g., "10th Pass", "Graduate")
    - state: (string, normalized to valid Indian state names)
    - detected_language: (string, "English", "Hindi", "Gujarati")
    - intent_category: (string, One of: "Agriculture", "Housing", "Health", "Education", "Women & Child", "Senior Citizens", "Employment", or null if general)
    - query_type: (string, One of: "general", "scheme_inquiry", "eligibility_check", "casual")

    Rules:
    - If user asks a general fact like "What is GST?", query_type="general", intent_category=null.
    - If user says "Hello" or "Thanks", query_type="casual".
    - If user asks for schemes, query_type="scheme_inquiry".
    - If user asks "Am I eligible?", query_type="eligibility_check".
    - Do not guess values. Only extract what is clearly stated.
    """

    messages = [{"role": "system", "content": system_prompt}]
    # Limit context to last 10 messages
    for msg in chat_history[-10:]:
        messages.append({"role": msg['role'], "content": msg['content']})

    content = call_llm(messages, json_mode=True)
    
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("❌ Failed to decode JSON from Groq")
    
    return {}

def generate_response(user_query, schemes, profile, missing_fields=None, language="English", intent="general"):
    """
    Generates a natural language response using Groq.
    """
    # 1. Handle General / Casual Intents (Skip Scheme Logic)
    if intent in ['general', 'casual']:
        system_prompt = f"""
        You are a helpful and knowledgeable AI Assistant for Indian Citizens.
        
        User Query Intent: {intent}
        Language: {language}

        Instructions:
        1. Answer the user's question clearly, accurately, and concisely.
        2. If the user greets you, greet them back warmly.
        3. Do NOT mention specific government schemes unless explicitly asked.
        4. Do NOT ask for personal details (age, income, etc.) unless absolutely necessary for the answer.
        5. Maintain a professional yet friendly tone.
        6. Respond ONLY in {language}.
        """
    
    # 2. Handle Scheme / Eligibility Intents (Use Scheme Logic)
    else:
        schemes_text = "No specific schemes found yet."
        if schemes:
            schemes_text = "Found Schemes:\n"
            for s in schemes:
                status = s.get('eligibility_status', 'Eligible')
                schemes_text += f"• **{s['name']}** ({status}): {s.get('description', '')[:100]}...\n"

        system_prompt = f"""
        You are a friendly and helpful Government Scheme Assistant.
        
        Current User Profile: {json.dumps(profile)}
        Missing Details: {missing_fields if missing_fields else "None"}
        Language: {language}
        
        Available Schemes Data:
        {schemes_text}
        
        Instructions:
        1. **Acknowledge**: Confirm understood details (e.g., "I see you are interested in Education schemes.").
        2. **Schemes**: List the found schemes.
           - If status is 'Eligible', recommend it strongly.
           - If status is 'Check Details' or 'Possibly Eligible', explain that they might need to check specific criteria.
        3. **Missing Info**: If I miss critical info (Occupation, Income, State, Age) *for the eligible schemes*, politely ask.
        4. **Tone**: Professional, encouraging, and clear.
        5. **Output**: Respond ONLY in {language}.
        """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    response = call_llm(messages)
    return response if response else "I am processing your request, but the AI service is busy. Please try again."

def translate_text(text, target_language):
    """
    Translates text to target_language using Groq.
    """
    if not target_language or target_language.lower() == 'english':
        return text

    system_prompt = f"You are a professional translator. Translate the following text into {target_language}. Maintain the original formatting and tone. Do not add any conversational filler."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    translated = call_llm(messages)
    return translated if translated else text
