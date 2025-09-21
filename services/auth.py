from datetime import datetime, timedelta

import bcrypt
import pyotp

from database.db import db
from database.models import User


class AuthService:
    @staticmethod
    def create_user(email: str, password: str) -> int:
        with db.get_session() as session:
            existing_user = session.query(User).filter(User.email == email).first()

            if existing_user:
                raise ValueError("User already exists")

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_user = User(
                email=email,
                password_hash=password_hash,
                mfa_secret=pyotp.random_base32(),
            )

            session.add(new_user)
            session.flush()
            return new_user.id

    @staticmethod
    def verify_login(email: str, password: str):
        with db.get_session() as session:
            user = session.query(User).filter(User.email == email, User.is_active).first()

            if not user:
                return None, "Invalid credentials."

            # Check account lock
            if user.locked_until and user.locked_until > datetime.now():
                return None, "Account is locked."

            # Verify password
            if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.now()
                roles = [role.name for role in user.roles]
                return {"user_id": user.id, "roles": roles, "email": user.email}, None

            else:
                user.failed_login_attempts += 1

                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=10)
                    account_locked_msg = (
                        "Account locked due to too many failed attempts. " "Please try again in 10 minutes.",
                    )
                    return (None, account_locked_msg)

                return None, "Invalid credentials."

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        with db.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all_users():
        with db.get_session() as session:
            return session.query(User).order_by(User.created_at.desc()).all()
