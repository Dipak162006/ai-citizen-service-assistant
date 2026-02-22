from flask import Blueprint, jsonify, session, request
from models import UserProfile, Scheme, db
from services.scheme_service import find_eligible_schemes

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/api/schemes/all', methods=['GET'])
def get_all_schemes():
    schemes = Scheme.query.order_by(Scheme.created_at.desc()).all()
    scheme_dicts = []
    for s in schemes:
        sd = s.to_dict()
        sd['matched_rules'] = []
        sd['failed_rules'] = []
        sd['eligibility_status'] = "Check Criteria"
        scheme_dicts.append(sd)
    return jsonify({"schemes": scheme_dicts, "mode": "default"}), 200


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

    mode = "filtered"
    if not eligible_schemes:
        mode = "fallback"
        all_schemes = Scheme.query.order_by(Scheme.created_at.desc()).all()
        eligible_schemes = [s.to_dict() for s in all_schemes]
        for s in eligible_schemes:
            s['eligibility_status'] = 'Check Details'
            s['matched_rules'] = []
            s['failed_rules'] = []

    # Return ALL matched schemes with mode flag
    return jsonify({"schemes": eligible_schemes, "mode": mode}), 200


@recommendation_bp.route('/api/schemes/compare', methods=['POST'])
def compare_schemes():
    data = request.get_json()
    if not data or 'scheme_ids' not in data:
        return jsonify({"error": "Missing scheme_ids"}), 400
        
    scheme_ids = data['scheme_ids']
    if not isinstance(scheme_ids, list) or len(scheme_ids) > 2:
        return jsonify({"error": "Invalid scheme_ids list (max 2 allowed)"}), 400

    schemes = Scheme.query.filter(Scheme.id.in_(scheme_ids)).all()
    
    # Sort them to match input order if possible, or just build dict
    schemes_dict = {str(s.id): s for s in schemes}
    
    # Prepare comparison structure
    # { "Feature Name": [ValueA, ValueB] }
    # Feature Name -> values array mapped by requested order
    comparison_data = {
        "Name": [],
        "Category": [],
        "Benefit Summary": [],
        "Target Age": [],
        "Income Limit": [],
        "Occupation": [],
        "State": []
    }
    
    for sid in scheme_ids:
        s = schemes_dict.get(str(sid))
        if s:
            comparison_data["Name"].append(s.scheme_name)
            comparison_data["Category"].append(s.category)
            comparison_data["Benefit Summary"].append(s.benefits if s.benefits else "N/A")
            
            # Parse eligibility JSON
            elig = s.eligibility or {}
            
            min_age = elig.get('min_age', '')
            max_age = elig.get('max_age', '')
            if min_age and max_age:
                age_str = f"{min_age} - {max_age} yrs"
            elif min_age:
                age_str = f"{min_age}+ yrs"
            elif max_age:
                age_str = f"Up to {max_age} yrs"
            else:
                age_str = "Any Age"
            comparison_data["Target Age"].append(age_str)
            
            inc_status = elig.get('income_status') or elig.get('poverty_status') or "No Limit"
            comparison_data["Income Limit"].append(inc_status.title())
            
            occ = elig.get('occupation') or "Any"
            comparison_data["Occupation"].append(occ.title())
            
            comparison_data["State"].append(s.state if s.state else "All India")
        else:
            # Missing scheme
            comparison_data["Name"].append("Unknown")
            comparison_data["Category"].append("N/A")
            comparison_data["Benefit Summary"].append("N/A")
            comparison_data["Target Age"].append("N/A")
            comparison_data["Income Limit"].append("N/A")
            comparison_data["Occupation"].append("N/A")
            comparison_data["State"].append("N/A")

    return jsonify({"comparison": comparison_data}), 200
