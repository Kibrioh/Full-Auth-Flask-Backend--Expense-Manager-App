"""Session-based authentication endpoints.

Matches the provided client-with-sessions contract:
  POST   /signup          -> 201 + user
  POST   /login           -> 200 + user
  GET    /check_session   -> 200 + user | 401
  DELETE /logout          -> 204
Error responses use {"errors": [...]} so the frontend can render them.
"""

from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError

from models import db, User

# No url_prefix: the client calls /signup, /login, etc. at the root.
auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    confirmation = data.get("password_confirmation")

    errors = []
    if not username:
        errors.append("Username is required.")
    if not password:
        errors.append("Password is required.")
    # The frontend sends password_confirmation; enforce it when present.
    if confirmation is not None and password != confirmation:
        errors.append("Passwords do not match.")
    if errors:
        return {"errors": errors}, 422

    # The signup form has no email field, so derive a unique placeholder
    # from the (unique) username to satisfy the NOT NULL/UNIQUE column.
    email = (data.get("email") or f"{username}@example.com").strip()

    user = User(username=username, email=email)
    user.password_hash = password  # triggers the bcrypt setter

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"errors": ["Username or email already taken."]}, 422

    session["user_id"] = user.id  # log the new user in immediately
    return user.to_dict(), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if user and user.authenticate(password):
        session["user_id"] = user.id
        return user.to_dict(), 200

    return {"errors": ["Invalid username or password."]}, 401


@auth_bp.get("/check_session")
def check_session():
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            return user.to_dict(), 200
    return {"errors": ["Not authenticated."]}, 401


@auth_bp.delete("/logout")
def logout():
    session.pop("user_id", None)
    return "", 204