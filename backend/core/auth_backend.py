import logging

import jwt
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.requests import Request

from core.security import decode_token

logger = logging.getLogger("uvicorn.error")


class AuthUser(SimpleUser):
    """Custom User class to hold user ID and username."""
    def __init__(self, user_id: str, username: str | None = None):
        super().__init__(username or user_id)
        self.user_id = int(user_id)


class JWTAuthBackend(AuthenticationBackend):
    """
    Custom Starlette authentication backend.
    It reads the JWT 'access_token' from cookies or headers
    and populates request.scope["user"].
    """

    async def authenticate(self, conn: Request):
        # Default unauthenticated state
        guest_creds = AuthCredentials(["unauthenticated"])

        # Try to get the token.
        token = conn.headers.get("Authorization")
        if token:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
        else:
            token = conn.cookies.get("access_token", None)

        if not token:
            # No token, user is anonymous
            return guest_creds, None

        # Try to decode the token
        try:
            payload = decode_token(token)
            if payload is None:
                logger.warning("AuthBackend: invalid or expired token")
                return guest_creds, None

            # The 'sub' (subject) of our JWT is the User ID (as a string)
            user_id: str = payload.get("sub")
            if not user_id:
                # Invalid token payload
                return guest_creds, None

            # Success! Attach the user to the request scope.
            # We attach a SimpleUser, where .username will hold the user_id
            creds = AuthCredentials(["authenticated"])
            user = AuthUser(user_id=user_id)
            return creds, user

        except jwt.PyJWTError:
            # Token is invalid, expired, or malformed
            return guest_creds, None
