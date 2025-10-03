# database/seeders/users.py
from datetime import datetime

import bcrypt

from core.config import DEFAULT_USER_PREFERENCES
from database.models import User, Role
from .base import BaseSeeder
from utils.constants import SystemRoles


class UserSeeder(BaseSeeder):
    """Seeder for initial users"""

    @classmethod
    def run(cls):
        from database.db import db

        with db.get_session() as session:
            # Check if users already exist
            existing_users = session.query(User).count()
            if existing_users > 0:
                print("⏩ Users already exist, skipping user seeding...")
                return

            # Get roles
            roles = session.query(Role).all()
            role_dict = {role.name: role for role in roles}

            # Initial users data - CHANGE PASSWORDS IN PRODUCTION!
            initial_users = [
                {
                    "email": "admin@nids.local",
                    "username": "admin",
                    "password": "Admin123!",  # Change in production!
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "role_names": [SystemRoles.ADMIN.value],
                    "department": "IT Security",
                    "job_title": "Security Administrator",
                    "timezone": "UTC",
                },
                {
                    "email": "manager@nids.local",
                    "username": "manager",
                    "password": "Manager123!",
                    "first_name": "Leo",
                    "last_name": "Mario",
                    "role_names": [SystemRoles.MANAGER.value],
                    "department": "IT Security",
                    "job_title": "Security Manager",
                    "timezone": "US/Eastern",
                },
                {
                    "email": "analyst@nids.local",
                    "username": "analyst",
                    "password": "Analyst123!",
                    "first_name": "Alice",
                    "last_name": "Burns",
                    "role_names": [SystemRoles.ANALYST.value],
                    "department": "SOC",
                    "job_title": "Security Analyst",
                    "timezone": "US/Eastern",
                },
                {
                    "email": "viewer@nids.local",
                    "username": "viewer",
                    "password": "Viewer123!",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role_names": [SystemRoles.VIEWER.value],
                    "department": "IT Security",
                    "job_title": "Security Viewer",
                    "timezone": "Africa/Nairobi",
                },
            ]

            users_created = 0
            for user_data in initial_users:
                # Check if user already exists
                existing_user = (
                    session.query(User).filter_by(email=user_data["email"]).first()
                )
                if existing_user:
                    continue

                # Hash password
                password_hash = bcrypt.hashpw(
                    user_data["password"].encode(), bcrypt.gensalt()
                ).decode()

                # Get default preferences
                default_prefs = DEFAULT_USER_PREFERENCES

                # Create user with enhanced profile
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    department=user_data["department"],
                    job_title=user_data["job_title"],
                    timezone=user_data["timezone"],
                    password_hash=password_hash,
                    preferences=default_prefs,
                    profile_completed=True,
                    is_active=True,
                    created_at=datetime.now(),
                )

                # Assign roles
                for role_name in user_data["role_names"]:
                    role_obj = role_dict.get(role_name)
                    if role_obj:
                        user.roles.append(role_obj)

                session.add(user)
                users_created += 1

            if users_created > 0:
                session.commit()
                cls.log_seeding("User", users_created)

                # Print login credentials for development
                print("\n🔐 Initial user credentials (CHANGE IN PRODUCTION!):")
                print("=" * 50)
                for user_data in initial_users:
                    print(f"Email: {user_data['email']}")
                    print(f"Password: {user_data['password']}")
                    print(f"Roles: {', '.join(user_data['role_names'])}")
                    print("-" * 30)
            else:
                print("⏩ Users already seeded, skipping...")
