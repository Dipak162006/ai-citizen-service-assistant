from flask import Blueprint, request, jsonify
import json
import os

eligibility_bp = Blueprint('eligibility_bp', __name__)

# Load schemes database logic
def load_schemes():
    # Attempting to gracefully pull active schemes from existing db_schemes.json or similar data store
    # Since we lack advanced DB integration in this context, we'll mock the extraction
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db_schemes.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('schemes', [])
    except Exception as e:
        print(f"Error loading schemes: {e}")
        # Fallback to a hardcoded MVP list if the file is missing
        return [
            {
                "id": 1,
                "name": "PM Kisan Samman Nidhi",
                "short_description": "Financial benefit of Rs 6000/- per year to all landholding farmers' families.",
                "criteria": {"occupation": "farmer"}
            },
            {
                "id": 2,
                "name": "Post Matric Scholarship",
                "short_description": "Financial assistance to students studying at post matriculation or post-secondary stage.",
                "criteria": {"occupation": "student", "max_income": 250000}
            },
            {
                "id": 3,
                "name": "Mudra Yojana",
                "short_description": "Loans up to Rs. 10 Lakhs to non-corporate, non-farm small/micro enterprises.",
                "criteria": {"occupation": "business"}
            }
        ]

@eligibility_bp.route('/api/eligibility/check', methods=['POST'])
def check_eligibility():
    user_data = request.json
    if not user_data:
        return jsonify({"error": "No payload provided"}), 400

    schemes = load_schemes()
    result = {
        "eligible": [],
        "partial": [],
        "not_eligible": []
    }

    # Normalize user inputs
    user_age = int(user_data.get('age', 0))
    user_income = int(user_data.get('income', 0))
    user_gender = user_data.get('gender', '').lower()
    user_occupation = user_data.get('occupation', '').lower()
    user_state = user_data.get('state', '').lower()
    user_category = user_data.get('category', '').lower()

    for scheme in schemes:
        criteria = scheme.get('criteria', {})
        reasons = []
        conditions_met = 0
        total_conditions = 0

        # Feature Check: Occupation
        if 'occupation' in criteria:
            total_conditions += 1
            if criteria['occupation'].lower() == user_occupation or criteria['occupation'].lower() == 'all':
                conditions_met += 1
                reasons.append({"met": True, "detail": f"Matches {criteria['occupation'].capitalize()} occupation requirement"})
            else:
                reasons.append({"met": False, "detail": f"Requires {criteria['occupation'].capitalize()} occupation"})

        # Feature Check: Income
        if 'max_income' in criteria:
            req_income = int(criteria['max_income'])
            total_conditions += 1
            if user_income <= req_income:
                conditions_met += 1
                reasons.append({"met": True, "detail": f"Income under ₹{req_income:,}"})
            else:
                reasons.append({"met": False, "detail": f"Income must be strictly below ₹{req_income:,}"})

        # Feature Check: Age (if defined min_age or max_age in criteria)
        if 'min_age' in criteria or 'max_age' in criteria:
            total_conditions += 1
            min_age = int(criteria.get('min_age', 0))
            max_age = int(criteria.get('max_age', 120))
            if min_age <= user_age <= max_age:
                conditions_met += 1
                reasons.append({"met": True, "detail": f"Age {user_age} is within {min_age}-{max_age}"})
            else:
                reasons.append({"met": False, "detail": f"Requires age between {min_age} and {max_age}"})
                
        # Feature Check: Gender
        if 'gender' in criteria:
            total_conditions += 1
            if criteria['gender'].lower() == user_gender or criteria['gender'].lower() == 'all':
                conditions_met += 1
                reasons.append({"met": True, "detail": "Matches gender requirements"})
            else:
                 reasons.append({"met": False, "detail": f"Scheme specifically designed for {criteria['gender']}s"})

        # Build output structure
        scheme_output = {
            "id": scheme.get('id', 'unknown'),
            "name": scheme.get('name', 'Unknown Scheme'),
            "description": scheme.get('short_description', ''),
            "reasons": reasons if len(reasons) > 0 else [{"met": True, "detail": "No specific constraints found. Broad eligibility."}]
        }

        # Handle schemes with no hard constraints natively as eligible
        if total_conditions == 0:
            result['eligible'].append(scheme_output)
        elif conditions_met == total_conditions:
            result['eligible'].append(scheme_output)
        elif conditions_met > 0:
            result['partial'].append(scheme_output)
        else:
            result['not_eligible'].append(scheme_output)

    return jsonify(result), 200
