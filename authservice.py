from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db


def validate_username(username):
    if not username:
        return False, "Username is required."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(username) > 20:
        return False, "Username must be 20 characters or less."

    if not username.replace("_", "").isalnum():
        return False, "Username can only contain letters, numbers, and underscores."

    return True, ""


def create_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    valid_username, message = validate_username(username)

    if not valid_username:
        return False, message

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return False, "Username or email already exists."

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return True, "Account created successfully. You can now log in."


def authenticate_user(email, password):
    email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        return True, "Logged in successfully.", user

    return False, "Invalid email or password.", None