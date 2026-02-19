from flask import Blueprint, jsonify, session
from models import UserProfile, Scheme, db
from services.scheme_service import find_eligible_schemes

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if 'user_id' not in session:
        return jsonify([]), 200 # Return empty if not logged in

    user_id = session['user_id']
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not user_profile:
        return jsonify([]), 200

    # Get Session ID from query params to find Intent
    from flask import request
    from models import UserSession
    session_id = request.args.get('session_id')
    intent_category = None
    
    if session_id:
        user_session = UserSession.query.get(session_id)
        if user_session and user_session.profile_data:
            intent_category = user_session.profile_data.get('intent_category')

    # Convert UserProfile model to dictionary for eligibility engine
    profile_dict = {
        'occupation': user_profile.occupation,
        'income_group': user_profile.income_range,
        'education': user_profile.education,
        'age': int(user_profile.age_group) if user_profile.age_group and user_profile.age_group.isdigit() else None,
        'state': user_profile.location
    }

    # Find Eligible Schemes (Hybrid: Profile + Intent)
    eligible_schemes = find_eligible_schemes(profile_dict, intent_category=intent_category)

    # Return ALL matched schemes (Frontend will handle display/scroll)
    return jsonify(eligible_schemes), 200
