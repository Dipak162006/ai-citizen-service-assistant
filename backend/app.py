from flask import Flask, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from config import Config
from models import db
import os

def create_app():
    # Point to the frontend folder relative to this backend file
    frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    static_folder = os.path.join(frontend_folder, 'static')
    
    # Set template_folder to frontend directory
    app = Flask(__name__, static_folder=static_folder, template_folder=frontend_folder)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize DB
    db.init_app(app)

    # Import routes
    from routes.chat_routes import chat_bp
    from routes.auth_routes import auth_bp
    from routes.recommendation_routes import recommendation_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recommendation_bp)

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect('/dashboard')
        return send_from_directory(frontend_folder, 'landing.html')

    @app.route('/login')
    def login_page():
        return send_from_directory(frontend_folder, 'login.html')

    @app.route('/register')
    def register_page():
        return send_from_directory(frontend_folder, 'register.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect('/login')
        
        # Pass user_name to template, default to 'User'
        user_name = session.get('user_name', 'User')
        
        # Fetch Dynamic Categories
        from models import Scheme
        categories = db.session.query(Scheme.category).distinct().all()
        category_list = sorted([c[0] for c in categories if c[0]])
        
        # Helper for icons (pass as context)
        def get_category_icon(category):
            cat_lower = category.lower()
            if 'farm' in cat_lower or 'agri' in cat_lower: return 'fa-tractor'
            if 'student' in cat_lower or 'edu' in cat_lower: return 'fa-user-graduate'
            if 'health' in cat_lower or 'med' in cat_lower: return 'fa-heartbeat'
            if 'woman' in cat_lower or 'female' in cat_lower: return 'fa-venus'
            if 'senior' in cat_lower or 'pension' in cat_lower: return 'fa-blind'
            if 'business' in cat_lower or 'loan' in cat_lower: return 'fa-briefcase'
            if 'hous' in cat_lower: return 'fa-home'
            if 'employ' in cat_lower or 'job' in cat_lower: return 'fa-briefcase'
            return 'fa-hand-holding-heart'

        from flask import render_template
        return render_template('dashboard.html', user_name=user_name, categories=category_list, get_icon=get_category_icon)

    @app.route('/<path:path>')
    def serve_static_files(path):
        return send_from_directory(frontend_folder, path)

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "AI Citizen Assistant"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("Database initialized.")
    app.run(debug=True, port=5000)
