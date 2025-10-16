"""
SQLAlchemy models for the application.
Each model represents a database table.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # MFA fields
    mfa_secret = Column(String(255), nullable=True)
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_method = Column(String(20), default='totp')  # 'totp', 'email', 'sms', 'backup_code'
    mfa_backup_codes = Column(ARRAY(Text), nullable=True)
    mfa_configured_at = Column(DateTime, nullable=True)
    mfa_recovery_token = Column(String(255), nullable=True)
    mfa_recovery_token_expires = Column(DateTime, nullable=True)

    # Security fields
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Profile information
    username = Column(String(15), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    timezone = Column(String(50), default='UTC')

    # User preferences (UI, notifications, etc...)
    preferences = Column(JSON, default=dict)

    # Profile completion
    profile_completed = Column(Boolean, default=False)
    last_profile_update = Column(DateTime, nullable=True)

    # Account verification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)

    # Relationship
    roles = relationship('Role', secondary='user_roles', back_populates='users')
    sessions = relationship('UserSession', back_populates='user')


class UserSession(Base):
    """Database model for user session tracking."""

    __tablename__ = 'user_sessions'

    id = Column(String(255), primary_key=True)  # Session ID
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    device_info = Column(String(255))  # Browser/device info
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    login_time = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship('User', back_populates='sessions')


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    users = relationship('User', secondary='user_roles', back_populates='roles')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')


# Association table for many-to-many between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=func.now()),
)


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    category = Column(String(50), nullable=True)

    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')


# Association table for role-permission many-to-many
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('granted_at', DateTime, default=func.now()),
)
