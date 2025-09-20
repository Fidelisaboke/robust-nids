# database/seeders/users.py
from datetime import datetime

import bcrypt

from database.models import User, Role
from .base import BaseSeeder
from utils.roles import SystemRoles


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
                    "password": "Admin123!",  # Change in production!
                    "role_names": [SystemRoles.ADMIN.value],
                    "name": "System Administrator"
                },
                {
                    "email": "manager@nids.local",
                    "password": "Manager123!",
                    "role_names": [SystemRoles.MANAGER.value],
                    "name": "Security Manager"
                },
                {
                    "email": "analyst@nids.local",
                    "password": "Analyst123!",
                    "role_names": [SystemRoles.MANAGER.value],
                    "name": "Security Analyst"
                },
                {
                    "email": "viewer@nids.local",
                    "password": "Viewer123!",
                    "role_names": [SystemRoles.VIEWER.value],
                    "name": "Security Viewer"
                }
            ]

            users_created = 0
            for user_data in initial_users:
                # Check if user already exists
                existing_user = session.query(User).filter_by(email=user_data["email"]).first()
                if existing_user:
                    continue

                # Hash password
                password_hash = bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt()).decode()

                # Create user
                user = User(
                    email=user_data["email"],
                    password_hash=password_hash,
                    mfa_secret="",  # MFA can be set up later
                    is_active=True,
                    created_at=datetime.now()
                )

                # Assign roles
                for role_name in user_data["role_names"]:
                    role = role_dict.get(role_name)
                    if role:
                        user.roles.append(role)

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
