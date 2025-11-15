"""
SQLAlchemy models for the application.
Each model represents a database table.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship

from utils.enums import AlertSeverity, AlertStatus, ReportStatus, SystemRoles


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # MFA fields
    mfa_secret = Column(String(255), nullable=True)
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_method = Column(String(20), default="totp")  # 'totp', 'email', 'sms', 'backup_code'
    mfa_backup_codes = Column(ARRAY(Text), nullable=True)
    mfa_configured_at = Column(DateTime(timezone=True), nullable=True)
    mfa_recovery_token = Column(String(255), nullable=True)
    mfa_recovery_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Security fields
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Profile information
    username = Column(String(15), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    timezone = Column(String(50), default="UTC")

    # User preferences (UI, notifications, etc...)
    preferences = Column(JSON, default=dict)

    # Profile completion
    profile_completed = Column(Boolean, default=False)
    last_profile_update = Column(DateTime(timezone=True), nullable=True)

    # Account verification
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified = Column(Boolean, default=False)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Email verification token
    email_verification_token = Column(String(255), nullable=True)
    email_verification_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Password reset token
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    sessions = relationship("UserSession", back_populates="user")
    alerts = relationship("Alert", back_populates="assigned_user")
    reports = relationship("Report", back_populates="owner")

    @property
    def is_admin(self) -> bool:
        """Check if the user has admin role."""
        return any(role.name == SystemRoles.ADMIN for role in self.roles)


class UserSession(Base):
    """Database model for user session tracking."""

    __tablename__ = "user_sessions"

    id = Column(String(255), primary_key=True)  # Session ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_info = Column(String(255))  # Browser/device info
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    login_time = Column(DateTime(timezone=True), default=func.now())
    last_activity = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


# Association table for many-to-many between users and roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), default=func.now()),
)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    category = Column(String(50), nullable=True)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


# Association table for role-permission many-to-many
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
    Column("granted_at", DateTime(timezone=True), default=func.now()),
)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    # User assigned to alert
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Alert title and description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Alert severity, resolution status, and category
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.LOW)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE)
    category = Column(String(100), nullable=True)  # e.g. Bruteforce, Mirai

    # Source and destination identifiers
    src_ip = Column(String(50), nullable=True)
    dst_ip = Column(String(50), nullable=True)
    dst_port = Column(Integer, index=True)

    # Full API JSON
    model_output = Column(JSON, nullable=True)

    # Raw flow data
    flow_data = Column(JSON, nullable=True)

    # Timestamp from thhe packet flow
    flow_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Timestamp for database record
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    assigned_user = relationship("User", back_populates="alerts")


class Report(Base):
    """Model for storing report generation requests and metadata."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    # Who requested this report?
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)

    # Stores the filters used to generate this report
    parameters = Column(JSON, nullable=True)

    # Where the file is stored, e.g., "reports/my_report.csv"
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    owner = relationship("User", back_populates="reports")


class RobustnessReport(Base):
    """Model for storing robustness metrics from adversarial training and evaluation."""

    __tablename__ = "robustness_reports"
    id = Column(Integer, primary_key=True)
    model = Column(String, nullable=False)
    accuracy = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
