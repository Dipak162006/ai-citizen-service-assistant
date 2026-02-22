from models import Scheme

def find_eligible_schemes(profile, intent_category=None):
    """
    Queries the database and filters schemes based on user profile.
    If intent_category is provided, fetches ALL schemes in that category 
    but tags them with eligibility status.
    """
    if intent_category:
        # Fetch schemes specifically for the requested category
        all_schemes = Scheme.query.filter(Scheme.category.ilike(f"%{intent_category}%")).all()
    else:
        # Default: Fetch all schemes to find eligible ones
        all_schemes = Scheme.query.all()
    
    eligible_schemes = []

    for scheme in all_schemes:
        criteria = scheme.eligibility or {}
        matched_rules = []
        failed_rules = []
        
        # --- 1. Age Check ---
        user_age = profile.get('age')
        if user_age:
            try:
                user_age_int = int(str(user_age).split('-')[0].strip())
                min_age = criteria.get('min_age')
                max_age = criteria.get('max_age')
                
                if min_age and max_age:
                    if user_age_int < int(min_age):
                        failed_rules.append(f"Age {user_age_int} is below minimum {min_age}")
                    elif user_age_int > int(max_age):
                        failed_rules.append(f"Age {user_age_int} is above maximum {max_age}")
                    else:
                        matched_rules.append(f"Age {user_age_int} is within allowed range ({min_age}-{max_age})")
                elif min_age:
                    if user_age_int < int(min_age):
                        failed_rules.append(f"Age {user_age_int} is below minimum {min_age}")
                    else:
                        matched_rules.append(f"Age {user_age_int} meets minimum requirement ({min_age}+)")
                elif max_age:
                     if user_age_int > int(max_age):
                        failed_rules.append(f"Age {user_age_int} is above maximum {max_age}")
                     else:
                        matched_rules.append(f"Age {user_age_int} is within limits (Up to {max_age})")
            except ValueError:
                pass 

        # --- 2. Gender Check ---
        user_gender = profile.get('gender')
        scheme_gender = criteria.get('gender')
        if user_gender and scheme_gender and scheme_gender.lower() != 'all':
            if scheme_gender.lower() != user_gender.lower():
                failed_rules.append(f"Scheme is for {scheme_gender}, your profile states {user_gender}")
            else:
                matched_rules.append(f"Gender matches requirement ({scheme_gender})")

        # --- 3. Income / Poverty Status ---
        user_income_group = profile.get('income_group')
        scheme_income_status = criteria.get('income_status') or criteria.get('poverty_status')
        if user_income_group and scheme_income_status:
            u_inc = user_income_group.lower()
            s_inc = scheme_income_status.lower()
            if 'bpl' in s_inc and 'bpl' not in u_inc and 'low' not in u_inc:
                failed_rules.append("Scheme requires BPL or Low Income status")
            else:
                matched_rules.append("Income bracket matches requirements")

        # --- 4. Occupation Check ---
        user_occ = profile.get('occupation')
        scheme_occ = criteria.get('occupation')
        if user_occ and scheme_occ:
            if scheme_occ.lower() not in user_occ.lower():
                failed_rules.append(f"Occupation mismatch (requires {scheme_occ})")
            else:
                matched_rules.append(f"Occupation '{user_occ}' matches requirements")

        # --- 5. State / Location Check ---
        user_state = profile.get('state')
        scheme_state = scheme.state 
        if user_state and scheme_state:
            if isinstance(user_state, list):
                user_state = user_state[0] if user_state else ""
            
            if scheme_state.lower() != 'all india' and scheme_state.lower() not in str(user_state).lower():
                failed_rules.append(f"Scheme is limited to {scheme_state}")
            elif scheme_state.lower() != 'all india':
                matched_rules.append(f"State '{user_state}' is eligible")

        # --- 6. Caste / Category Check ---
        user_cat = profile.get('category')
        scheme_cat = criteria.get('category')
        if user_cat and scheme_cat and scheme_cat.lower() != 'all':
            if scheme_cat.lower() != user_cat.lower():
                failed_rules.append(f"Scheme is for {scheme_cat} category")
            else:
                matched_rules.append(f"Category '{user_cat}' meets requirement")

        # --- Status & Scoring Logic ---
        score = 50 
        is_eligible = len(failed_rules) == 0
        
        if is_eligible:
            score += 50
            if scheme_state and user_state and scheme_state.lower() != 'all india' and scheme_state.lower() in user_state.lower():
                 score += 10
            # Penalty: Missing Info
            if not user_age and (criteria.get('min_age') or criteria.get('max_age')):
                score -= 10 
            if not user_income_group and (criteria.get('income_status')):
                score -= 10
        else:
            # If failed rules exist, adjust score down heavily
            score -= (10 * len(failed_rules))

        score = max(0, min(score, 100))

        # Determine Final Label
        if is_eligible:
            status_label = "Eligible"
        elif len(matched_rules) > 0 and len(failed_rules) > 0:
            status_label = "Check Criteria" # Partial match
        else:
            status_label = "Not Eligible"

        # DECISION: Add to list?
        scheme_dict = scheme.to_dict()
        scheme_dict['score'] = score
        scheme_dict['matched_rules'] = matched_rules
        scheme_dict['failed_rules'] = failed_rules
        scheme_dict['eligibility_status'] = status_label
        
        if is_eligible or (intent_category and status_label in ["Eligible", "Check Criteria", "Not Eligible"]):
             # Include if eligible or if requested via intent (so they can see why they failed)
             eligible_schemes.append(scheme_dict)
        elif not intent_category and len(matched_rules) > 0 and len(failed_rules) <= 1:
             # If just general fetching, include close partials (only 1 fail)
             eligible_schemes.append(scheme_dict)

    eligible_schemes.sort(key=lambda x: (x['eligibility_status'] != 'Eligible', -x['score']))
    return eligible_schemes
