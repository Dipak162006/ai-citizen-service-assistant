from flask import Blueprint, request, jsonify, session
from models import db, UserSession, ChatMessage, UserProfile
from services.ai_service import extract_profile, generate_response, translate_text
from services.scheme_service import find_eligible_schemes
import os
import re
import uuid

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    # Security Check: Ensure User is Logged In
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access. Please login."}), 401

    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    user_language = data.get('language', 'English')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Get or Create Session
    if session_id:
        db_user_session = UserSession.query.get(session_id)
    else:
        db_user_session = UserSession(session_id=uuid.uuid4())
        db.session.add(db_user_session)
        db.session.commit()
    
    # Check if session exists (if invalid ID passed)
    if not db_user_session:
        db_user_session = UserSession(session_id=uuid.uuid4())
        db.session.add(db_user_session)
        db.session.commit()

    # Update session profile with detected language if passed
    current_profile = db_user_session.profile_data or {}
    if user_language:
        current_profile['detected_language'] = user_language
        session['language'] = user_language # Sync with flask session

    # Save User Message
    user_msg_entry = ChatMessage(session_id=db_user_session.session_id, role='user', content=user_message)
    db.session.add(user_msg_entry)
    db.session.commit()

    # Retrieve Chat History
    history = ChatMessage.query.filter_by(session_id=db_user_session.session_id).order_by(ChatMessage.timestamp).all()
    chat_history = [{"role": msg.role, "content": msg.content} for msg in history]

    # AI Process: Extract Profile from Message History
    extracted_profile = extract_profile(chat_history)
    
    # Merge with existing profile (Update logic)
    # Only update fields that are NOT null in extracted data
    # Merge with existing profile (Update logic)
    # Only update fields that are NOT null in extracted data
    for key, value in extracted_profile.items():
        if value:
            # SANITIZATION: Ensure State/Occupation/etc are strings, not lists
            if isinstance(value, list) and len(value) > 0:
                value = value[0] # Take first item if list
            
            if isinstance(value, str):
                current_profile[key] = value
            elif isinstance(value, (int, float)):
                current_profile[key] = value # Allow numbers
            # Ignore other types to prevent DB errors

    # Save updated profile to Session
    db_user_session.profile_data = current_profile
    db.session.commit()

    # Save to UserProfile Table if User is Logged In
    if 'user_id' in session:
        user_id = session['user_id']
        user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not user_profile:
            user_profile = UserProfile(user_id=user_id)
            db.session.add(user_profile)
        
        # Update fields if present in extracted data
        if current_profile.get('occupation'): user_profile.occupation = current_profile['occupation']
        if current_profile.get('income_range'): user_profile.income_range = current_profile['income_range']
        if current_profile.get('education'): user_profile.education = current_profile['education']
        if current_profile.get('age'): user_profile.age_group = str(current_profile['age'])
        if current_profile.get('age'): user_profile.age_group = str(current_profile['age'])
        
        # Safe State Extraction
        if current_profile.get('state'): 
            state_val = current_profile['state']
            # If AI returns a list (e.g., ['Gujarat', 'Maharashtra']), join/pick one
            if isinstance(state_val, list):
                state_val = state_val[0] if state_val else None
            
            # Ensure it fits in DB (VARCHAR 100)
            if state_val and isinstance(state_val, str) and len(state_val) <= 100:
                user_profile.location = state_val
        
        db.session.commit()

    # Identify Missing Critical Fields for AI
    required_fields = ['occupation', 'income_range', 'state', 'age']
    missing_fields = [field for field in required_fields if not current_profile.get(field)]

    # Determine Language for Response
    # ALWAYS generate in English for consistency. Frontend handles translation.
    final_language = 'English'
    
    # Extract Intent Category & Query Type
    intent_category = extracted_profile.get('intent_category')
    query_type = extracted_profile.get('query_type', 'general')

    # Find Eligible Schemes (Only for Scheme/Eligibility Queries)
    eligible_schemes = []
    if query_type in ['scheme_inquiry', 'eligibility_check']:
        eligible_schemes = find_eligible_schemes(current_profile, intent_category=intent_category)

    # Generate Response
    response_text = generate_response(
        user_message, 
        eligible_schemes, 
        current_profile, 
        missing_fields=missing_fields,
        language=final_language,
        intent=query_type
    )

    # Save Assistant Message
    bot_msg_entry = ChatMessage(session_id=db_user_session.session_id, role='assistant', content=response_text)
    db.session.add(bot_msg_entry)
    db.session.commit()

    return jsonify({
        "response": response_text,
        "session_id": db_user_session.session_id,
        "profile": current_profile,
        "schemes_found": len(eligible_schemes)
    })

@chat_bp.route('/api/clear_chat', methods=['POST'])
def clear_chat():
    if 'conversation_history' in session:
        session.pop('conversation_history')
    return jsonify({"status": "success", "message": "Chat history cleared"})

@chat_bp.route('/api/update_profile', methods=['POST'])
def update_profile():
    return jsonify({"error": "Profile editing is disabled"}), 403

@chat_bp.route('/scheme-details', methods=['POST'])
def scheme_details():
    try:
        data = request.json
        scheme_name = data.get('scheme_name')
        session_id = data.get('session_id')
        
        if not scheme_name:
            return jsonify({"error": "Scheme name is required"}), 400

        # Construct a simulated user message to get the AI explanation
        user_message = f"Tell me detailed information about the scheme: {scheme_name}. Explain its benefits, eligibility, and how to apply in simple terms."
        
        from models import Scheme
        scheme = Scheme.query.filter(Scheme.scheme_name.ilike(f"%{scheme_name}%")).first()
        
        scheme_context = ""
        if scheme:
            scheme_context = f"""
            Scheme Details:
            Name: {scheme.scheme_name}
            Description: {scheme.description}
            Benefits: {scheme.benefits}
            Eligibility: {scheme.eligibility}
            Documents Required: {scheme.documents}
            Official Link: {scheme.official_link}
            """
            
        from services.ai_service import call_llm
        
        system_prompt = f"""
        You are a helpful government scheme assistant.
        The user wants to know about: {scheme_name}
        
        Using the following official details (if available) and your general knowledge, provide a helpful, easy-to-understand explanation.
        Use bullet points for readability.
        
        {scheme_context}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response_text = call_llm(messages)
        
        if not response_text:
            response_text = "I'm sorry, I couldn't generate details for this scheme right now."

        # Translation handled by Frontend now
        # language = data.get('language', 'English')
        # if language and language != 'English':
        #      response_text = translate_text(response_text, language)

        return jsonify({"response": response_text})

    except Exception as e:
        print(f"Error in scheme-details: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@chat_bp.route('/api/translate_history', methods=['POST'])
def translate_history():
    try:
        data = request.json
        session_id = data.get('session_id')
        target_language = data.get('language')
        
        if not session_id or not target_language:
             return jsonify({"error": "Missing params"}), 400
             
        # Fetch History
        history = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        
        translated_history = []
        for msg in history:
            # We translate on the fly, preserving original DB content
            translated_content = translate_text(msg.content, target_language)
            translated_history.append({
                "role": msg.role, 
                "content": translated_content
            })
            
        return jsonify({"history": translated_history})

    except Exception as e:
        print(f"Error translating history: {e}")
        return jsonify({"error": "Translation failed"}), 500

@chat_bp.route('/api/translate', methods=['POST'])
def translate_text_endpoint():
    try:
        data = request.json
        text = data.get('text')
        target_language = data.get('language')
        
        if not text or not target_language:
             return jsonify({"error": "Missing params"}), 400
             
        translated_text = translate_text(text, target_language)
        return jsonify({"translated_text": translated_text})

    except Exception as e:
        print(f"Error translating text: {e}")
        return jsonify({"error": "Translation failed"}), 500

@chat_bp.route('/change-language', methods=['POST'])
def change_language():
    try:
        data = request.json
        language = data.get('language')
        
        if not language:
            return jsonify({"error": "Language is required"}), 400
            
        # Update Session
        session['language'] = language
        
        # Also update UserSession if exists
        session_id = data.get('session_id')
        if session_id:
            db_user_session = UserSession.query.get(session_id)
            if db_user_session:
                current_profile = db_user_session.profile_data or {}
                current_profile['detected_language'] = language
                db_user_session.profile_data = current_profile
                db.session.commit()
                
        return jsonify({"message": "Language updated", "language": language})
        
    except Exception as e:
        print(f"Error changing language: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
