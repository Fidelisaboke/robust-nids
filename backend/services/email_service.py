"""
Email service module for sending emails.
It uses the fastapi-mail package to handle email sending functionality.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from core.config import settings
from database.models import Alert
from services.exceptions.email import EmailDeliveryException

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, conf: ConnectionConfig = None):
        if conf is None:
            conf = ConnectionConfig(
                MAIL_USERNAME=settings.MAIL_USERNAME,
                MAIL_PASSWORD=settings.MAIL_PASSWORD,
                MAIL_FROM=settings.MAIL_FROM,
                MAIL_PORT=settings.MAIL_PORT,
                MAIL_SERVER=settings.MAIL_SERVER,
                MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
                MAIL_STARTTLS=settings.MAIL_STARTTLS,
                MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
                USE_CREDENTIALS=settings.USE_CREDENTIALS,
                VALIDATE_CERTS=settings.VALIDATE_CERTS,
                TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
            )
        self.conf = conf
        self.fm = FastMail(self.conf)

    async def send_email_async(
        self,
        subject: str,
        recipients: List[EmailStr],
        template_body: Dict[str, Any],
        template_name: str = "email.html",
    ) -> None:
        """
        Send email asynchronously and wait for completion.
        Used for critical emails where you need to know if they were sent.
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=template_body,
                subtype=MessageType.html,
            )

            await self.fm.send_message(message, template_name=template_name)
            logger.info(f"Email sent successfully to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {str(e)}")
            raise EmailDeliveryException(f"Failed to send email: {str(e)}")

    def send_email_background(
        self,
        background_tasks: BackgroundTasks,
        subject: str,
        recipients: List[EmailStr],
        template_body: Dict[str, Any],
        template_name: str = "email.html",
    ) -> None:
        """
        Send email in the background using FastAPI's BackgroundTasks.
        This is the preferred method for non-critical emails.
        """
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=template_body,
            subtype=MessageType.html,
        )

        background_tasks.add_task(self.fm.send_message, message, template_name=template_name)
        logger.info(f"Background email task added for {recipients}")

    async def send_mfa_recovery_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str, recovery_token: str
    ) -> None:
        """Send MFA recovery email"""
        recovery_url = f"{settings.FRONTEND_URL}/mfa-recovery?token={recovery_token}"

        template_data = {
            "user_name": user_name,
            "recovery_url": recovery_url,
            "expiry_hours": settings.MFA_RECOVERY_TOKEN_EXPIRES_HOURS,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="MFA Recovery - NIDS",
            recipients=[email],
            template_body=template_data,
            template_name="mfa_recovery.html",
        )

    async def send_mfa_recovery_complete_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str
    ) -> None:
        """Send MFA recovery completion notification"""
        template_data = {
            "user_name": user_name,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="MFA Disabled - NIDS",
            recipients=[email],
            template_body=template_data,
            template_name="mfa_recovery_complete.html",
        )

    async def send_email_verification_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str, verification_token: str
    ) -> None:
        """Send email verification email"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

        template_data = {
            "user_name": user_name,
            "verification_url": verification_url,
            "expiry_minutes": settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Verify Your Email Address - NIDS",
            recipients=[email],
            template_body=template_data,
            template_name="email_verification.html",
        )

    async def send_email_verification_complete_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str
    ):
        """Send email verification complete email"""
        login_url = f"{settings.FRONTEND_URL}/login"

        template_data = {
            "user_name": user_name,
            "login_url": login_url,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Email Verification Complete - NIDS",
            recipients=[email],
            template_body=template_data,
            template_name="email_verification_complete.html",
        )

    async def send_password_reset_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str, reset_token: str
    ) -> None:
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        template_data = {
            "user_name": user_name,
            "reset_url": reset_url,
            "expiry_minutes": settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Reset Your Password - NIDS",
            recipients=[email],
            template_body=template_data,
            template_name="password_reset.html",
        )

    async def send_password_change_notification_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str
    ) -> None:
        """Send password change notification email"""
        template_data = {
            "user_name": user_name,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Password Changed - NIDS",
            recipients=[email],
            template_body=template_data,
            template_name="password_changed.html",
        )

    async def send_user_registration_confirmation_email(
        self, background_tasks: BackgroundTasks, user_email: str, user_name: str
    ):
        """Send confirmation email to user about their registration."""
        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Your NIDS Account Registration - Pending Approval",
            recipients=[user_email],
            template_body=template_data,
            template_name="user_registration_confirmation.html",
        )

    async def send_admin_user_registered_notification_email(
        self, background_tasks: BackgroundTasks, user_email: str, user_name: str
    ):
        """Send notification to admins about new user registration."""
        admin_panel_url = f"{settings.FRONTEND_URL}/admin"

        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "admin_panel_url": admin_panel_url,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="New User Registration - NIDS",
            recipients=[settings.SUPPORT_EMAIL],
            template_body=template_data,
            template_name="new_user_registration.html",
        )

    async def send_user_account_activated_email(
        self, background_tasks: BackgroundTasks, user_email: EmailStr, user_name: str
    ):
        """Send an email to user about their account being activated."""
        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Account Activated - NIDS",
            recipients=[user_email],
            template_body=template_data,
            template_name="user_account_activated.html",
        )

    async def send_admin_user_account_activated_email(
        self, background_tasks: BackgroundTasks, user_email: EmailStr, user_name: str
    ):
        """Send notification to admins about user account activation."""
        admin_panel_url = f"{settings.FRONTEND_URL}/admin"

        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "admin_panel_url": admin_panel_url,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="User Account Activated - NIDS",
            recipients=[settings.SUPPORT_EMAIL],
            template_body=template_data,
            template_name="account_activation.html",
        )

    async def send_user_account_deactivated_email(
        self, background_tasks: BackgroundTasks, user_email: EmailStr, user_name: str
    ):
        """Send an email to user about their account being deactivated."""
        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Account Deactivated - NIDS",
            recipients=[user_email],
            template_body=template_data,
            template_name="user_account_deactivated.html",
        )

    async def send_admin_user_account_deactivated_email(
        self, background_tasks: BackgroundTasks, user_email: EmailStr, user_name: str
    ):
        """Send notification to admins about user account deactivation."""
        admin_panel_url = f"{settings.FRONTEND_URL}/admin"

        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "admin_panel_url": admin_panel_url,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="User Account Deactivated - NIDS",
            recipients=[settings.SUPPORT_EMAIL],
            template_body=template_data,
            template_name="account_deactivation.html",
        )

    async def send_user_account_updated_email(
        self, background_tasks: BackgroundTasks, user_email: EmailStr, user_name: str
    ):
        """Send an email to user about their account being updated."""
        template_data = {
            "user_email": user_email,
            "user_name": user_name,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject="Account Updated - NIDS",
            recipients=[user_email],
            template_body=template_data,
            template_name="user_account_updated.html",
        )

    async def send_critical_alert_notification(self, background_tasks: BackgroundTasks, alert: Alert):
        """
        Send a high-priority notification to admins about a new critical alert.
        """
        admin_emails = [settings.SUPPORT_EMAIL]
        if not admin_emails:
            logger.warning("No SUPPORT_EMAIL configured, skipping critical alert notification.")
            return

        alert_url = f"{settings.FRONTEND_URL}/dashboard/alerts/{alert.id}"
        model_output = alert.model_output or {}

        # Get confidence and format in percentage in 2 decimal places
        confidence = model_output.get("binary", {}).get("confidence", None)
        if confidence is not None:
            confidence = f"{confidence * 100:.2f}%"
        else:
            confidence = "N/A"

        template_data = {
            "alert_title": alert.title,
            "alert_severity": str(alert.severity.value).upper(),
            "alert_category": alert.category,
            "alert_url": alert_url,
            "src_ip": alert.src_ip,
            "dst_ip": alert.dst_ip,
            "dst_port": alert.dst_port,
            "flow_timestamp": alert.flow_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "confidence": confidence,
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@example.com"),
            "current_year": datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject=f"🚨 CRITICAL NIDS ALERT: {alert.title}",
            recipients=admin_emails,
            template_body=template_data,
            template_name="critical_alert.html",
        )


# Email service dependency for dependency injection
def get_email_service() -> EmailService:
    return EmailService()
