import secrets
import string
from datetime import datetime

from backend.core.config import settings
from backend.database.models import Role, User
from backend.services.auth_service import get_password_hash
from backend.utils.enums import SystemRoles

from .base import BaseSeeder


class UserSeeder(BaseSeeder):
    """Seeder for initial users"""

    @staticmethod
    def _generate_secure_password(length=12):
        """Generate a secure random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    @classmethod
    def run(cls):
        from backend.database.db import db

        with db.get_session() as session:
            # Check if users already exist
            existing_users = session.query(User).count()
            if existing_users > 0:
                print('⏩ Users already exist, skipping user seeding...')
                return

            # Get roles
            roles = session.query(Role).all()
            role_dict = {role.name: role for role in roles}

            # Initial users data - CHANGE PASSWORDS IN PRODUCTION!
            initial_users = [
                {
                    'email': 'admin@example.com',
                    'username': 'admin',
                    'password': cls._generate_secure_password(),
                    'first_name': 'Jane',
                    'last_name': 'Doe',
                    'role_names': [SystemRoles.ADMIN.value],
                    'department': 'IT Security',
                    'job_title': 'Security Administrator',
                    'timezone': 'UTC',
                },
                {
                    'email': 'manager@example.com',
                    'username': 'manager',
                    'password': cls._generate_secure_password(),
                    'first_name': 'Leo',
                    'last_name': 'Mario',
                    'role_names': [SystemRoles.MANAGER.value],
                    'department': 'IT Security',
                    'job_title': 'Security Manager',
                    'timezone': 'US/Eastern',
                },
                {
                    'email': 'analyst@example.com',
                    'username': 'analyst',
                    'password': cls._generate_secure_password(),
                    'first_name': 'Alice',
                    'last_name': 'Burns',
                    'role_names': [SystemRoles.ANALYST.value],
                    'department': 'SOC',
                    'job_title': 'Security Analyst',
                    'timezone': 'US/Eastern',
                },
                {
                    'email': 'viewer@example.com',
                    'username': 'viewer',
                    'password': cls._generate_secure_password(),
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'role_names': [SystemRoles.VIEWER.value],
                    'department': 'IT Security',
                    'job_title': 'Security Viewer',
                    'timezone': 'Africa/Nairobi',
                },
            ]

            users_created = 0
            for user_data in initial_users:
                # Check if user already exists
                existing_user = session.query(User).filter_by(email=user_data['email']).first()
                if existing_user:
                    continue

                # Hash password
                password_hash = get_password_hash(user_data['password'])

                # Get default preferences
                default_prefs = settings.DEFAULT_USER_PREFERENCES

                # Create user with enhanced profile
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    department=user_data['department'],
                    job_title=user_data['job_title'],
                    timezone=user_data['timezone'],
                    password_hash=password_hash,
                    preferences=default_prefs,
                    profile_completed=True,
                    is_active=True,
                    created_at=datetime.now(),
                )

                # Assign roles
                for role_name in user_data['role_names']:
                    role_obj = role_dict.get(role_name)
                    if role_obj:
                        user.roles.append(role_obj)

                session.add(user)
                users_created += 1

            if users_created > 0:
                session.commit()
                cls.log_seeding('User', users_created)

                # Print login credentials for development
                print('\n🔐 Initial user credentials (CHANGE IN PRODUCTION!):')
                print('=' * 50)
                for user_data in initial_users:
                    print(f'Email: {user_data["email"]}')
                    print(f'Password: {user_data["password"]}')
                    print(f'Roles: {", ".join(user_data["role_names"])}')
                    print('-' * 30)
            else:
                print('⏩ Users already seeded, skipping...')
