from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not all([full_name, email, password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(full_name=full_name, email=email, password_hash=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Registration successful! Please login."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['user_name'] = user.full_name
        return jsonify({"message": "Login successful", "redirect": "/dashboard"}), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@auth_bp.route('/check_auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({"authenticated": True, "user": session['user_name']}), 200
    return jsonify({"authenticated": False}), 401

@auth_bp.route('/api/user/profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if 'full_name' in data:
        user.full_name = data['full_name']
        session['user_name'] = user.full_name
        
    try:
        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "full_name": user.full_name
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/api/user/password', methods=['PUT'])
def change_password():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400
        
    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400
        
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Incorrect current password"}), 401
        
    user.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
