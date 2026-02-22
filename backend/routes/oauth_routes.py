from flask import Blueprint, redirect, url_for, session, flash, request
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound
from models import db, User
import os

# Create the Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="dashboard", # Goes to dashboard on success
    login_url="/login/google",
    authorized_url="/login/google/authorized"
)

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", category="error")
        return False

    google_info = resp.json()
    google_id = str(google_info.get("id"))
    email = google_info.get("email")
    full_name = google_info.get("name")
    profile_photo = google_info.get("picture")

    if not email:
        flash("Google did not provide an email address.", category="error")
        return False

    # Check if user already exists
    user = User.query.filter_by(oauth_id=google_id).first()

    if not user:
        # Check if email exists (user registered with email before)
        user = User.query.filter_by(email=email).first()
        if user:
            # Link accounts
            user.oauth_provider = 'google'
            user.oauth_id = google_id
            if profile_photo and not user.profile_photo:
                user.profile_photo = profile_photo
            db.session.commit()
        else:
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                oauth_provider='google',
                oauth_id=google_id,
                profile_photo=profile_photo,
                # password_hash is null for Google users
            )
            db.session.add(user)
            db.session.commit()

    # Log user in
    session['user_id'] = user.id
    session['user_name'] = user.full_name
    
    # We return False to prevent Flask-Dance from trying to save the OAuth token 
    # to a database using its default SQLAlchemy storage setup (since we don't need token storage)
    return False
