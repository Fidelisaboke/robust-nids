"""
Email service module for sending emails.
It uses the fastapi-mail package to handle email sending functionality.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from core.config import settings
from services.exceptions.email import EmailDeliveryException

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
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
        self.fm = FastMail(self.conf)

    async def send_email_async(
        self,
        subject: str,
        recipients: List[EmailStr],
        template_body: Dict[str, Any],
        template_name: str = 'email.html',
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
            logger.info(f'Email sent successfully to {recipients}')
        except Exception as e:
            logger.error(f'Failed to send email to {recipients}: {str(e)}')
            raise EmailDeliveryException(f'Failed to send email: {str(e)}')

    def send_email_background(
        self,
        background_tasks: BackgroundTasks,
        subject: str,
        recipients: List[EmailStr],
        template_body: Dict[str, Any],
        template_name: str = 'email.html',
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
        logger.info(f'Background email task added for {recipients}')

    async def send_verification_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str, verification_token: str
    ) -> None:
        """Send email verification email"""
        verification_url = f'{settings.FRONTEND_URL}/verify-email?token={verification_token}'

        template_data = {
            'user_name': user_name,
            'verification_url': verification_url,
            'expiry_minutes': settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
            'current_year': datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject='Verify Your Email Address - NIDS',
            recipients=[email],
            template_body=template_data,
            template_name='email_verification.html',
        )

    async def send_password_reset_email(
        self, background_tasks: BackgroundTasks, email: EmailStr, user_name: str, reset_token: str
    ) -> None:
        """Send password reset email"""
        reset_url = f'{settings.FRONTEND_URL}/reset-password?token={reset_token}'

        template_data = {
            'user_name': user_name,
            'reset_url': reset_url,
            'expiry_minutes': settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
            'current_year': datetime.now().year,
        }

        self.send_email_background(
            background_tasks=background_tasks,
            subject='Reset Your Password - NIDS',
            recipients=[email],
            template_body=template_data,
            template_name='password_reset.html',
        )


# Email service dependency for dependency injection
def get_email_service() -> EmailService:
    return EmailService()
