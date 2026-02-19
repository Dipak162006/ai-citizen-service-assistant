from models import Scheme

def find_eligible_schemes(profile, intent_category=None):
    """
    Queries the database and filters schemes based on user profile.
    If intent_category is provided, fetches ALL schemes in that category 
    but tags them with eligibility status.
    """
    if intent_category:
        # Fetch schemes specifically for the requested category
        # Using ILIKE for case-insensitive partial match (e.g., "Health" in "Health & Insurance")
        all_schemes = Scheme.query.filter(Scheme.category.ilike(f"%{intent_category}%")).all()
    else:
        # Default: Fetch all schemes to find eligible ones
        all_schemes = Scheme.query.all()
    
    eligible_schemes = []

    for scheme in all_schemes:
        criteria = scheme.eligibility or {}
        is_eligible = True
        rejection_reason = None
        
        # --- 1. Age Check ---
        user_age = profile.get('age')
        if user_age:
            try:
                user_age_int = int(str(user_age).split('-')[0].strip()) # Handle "25" or "20-30"
                
                min_age = criteria.get('min_age')
                max_age = criteria.get('max_age')
                
                if min_age and user_age_int < int(min_age):
                    is_eligible = False
                    rejection_reason = f"Age {user_age_int} < Min {min_age}"
                elif max_age and user_age_int > int(max_age):
                    is_eligible = False
                    rejection_reason = f"Age {user_age_int} > Max {max_age}"
            except ValueError:
                pass # Skip check if age invalid

        # --- 2. Gender Check ---
        user_gender = profile.get('gender')
        scheme_gender = criteria.get('gender')
        if is_eligible and user_gender and scheme_gender:
            if scheme_gender.lower() != 'all' and scheme_gender.lower() != user_gender.lower():
                is_eligible = False
                rejection_reason = f"Gender {user_gender} != {scheme_gender}"

        # --- 3. Income / Poverty Status ---
        user_income_group = profile.get('income_group')
        scheme_income_status = criteria.get('income_status') or criteria.get('poverty_status')
        if is_eligible and user_income_group and scheme_income_status:
            # Normalize to lower
            u_inc = user_income_group.lower()
            s_inc = scheme_income_status.lower()
            
            # Logic: If scheme is for BPL, user must be BPL or Low Income
            if 'bpl' in s_inc and 'bpl' not in u_inc and 'low' not in u_inc:
                is_eligible = False
                rejection_reason = "Not BPL/Low Income"

        # --- 4. Occupation Check ---
        user_occ = profile.get('occupation')
        scheme_occ = criteria.get('occupation')
        if is_eligible and user_occ and scheme_occ:
            if scheme_occ.lower() not in user_occ.lower():
                is_eligible = False
                rejection_reason = f"Occupation mismatch ({scheme_occ} required)"

        # --- 5. State / Location Check ---
        user_state = profile.get('state')
        scheme_state = scheme.state  # Now a direct column
        if is_eligible and user_state and scheme_state:
            # Handle list case just in case
            if isinstance(user_state, list):
                user_state = user_state[0] if user_state else ""
            
            # Check if scheme is All India or matches user state
            if scheme_state.lower() != 'all india' and scheme_state.lower() not in str(user_state).lower():
                is_eligible = False
                rejection_reason = "State mismatch"

        # --- 6. Caste / Category Check ---
        user_cat = profile.get('category')
        scheme_cat = criteria.get('category')
        if is_eligible and user_cat and scheme_cat:
            if scheme_cat.lower() != 'all' and scheme_cat.lower() != user_cat.lower():
                is_eligible = False
                rejection_reason = "Category mismatch"

        # --- Scoring Logic ---
        score = 0
        
        # Calculate Score regardless of eligibility if intent_category is present
        # Baseline score
        score = 50 
        
        if is_eligible:
            score += 50
            
            # Bonus: Exact State Match
            if scheme_state and user_state and scheme_state.lower() != 'all india' and scheme_state.lower() in user_state.lower():
                 score += 10
            
            # Penalty: Missing Info (Unsure)
            if not user_age and (criteria.get('min_age') or criteria.get('max_age')):
                score -= 10 
            if not user_income_group and (criteria.get('income_status')):
                score -= 10

        score = max(0, min(score, 100)) # Clamp 0-100

        # DECISION: Add to list?
        # IF intent_category: Add ALL, but mark status
        # ELSE: Add ONLY if is_eligible
        
        scheme_dict = scheme.to_dict()
        scheme_dict['score'] = score
        
        if is_eligible:
            scheme_dict['eligibility_status'] = "Eligible"
            eligible_schemes.append(scheme_dict)
        elif intent_category:
            # If specifically asked for, show even if not eligible, but mark it
            scheme_dict['eligibility_status'] = "Check Criteria" if rejection_reason else "Possibly Eligible"
            eligible_schemes.append(scheme_dict)

    # Sort by score desc
    eligible_schemes.sort(key=lambda x: x['score'], reverse=True)
    return eligible_schemes
