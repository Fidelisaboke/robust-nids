import json
import logging
import time
from typing import Any, Dict

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from services.exceptions.base import ServiceException
from services.exceptions.mfa import MFAException
from services.exceptions.user import (
    EmailAlreadyExistsError,
    UserException,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)

# --- Logging Setup ---
app_logger = logging.getLogger("uvicorn.error")
audit_logger = logging.getLogger("audit")

# --- Skip and Sensitivity Filters ---
# These paths will not be logged at all
SKIP_AUDIT_PATHS = [
    "/docs",
    "/openapi.json",
    "/health",
    "/api/v1/nids/live-events",
    "/favicon.ico",
]

# Request bodies for these paths will NOT be logged
SENSITIVE_REQUEST_PATHS = [
    "/api/v1/auth/login",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/change-password",
]

# Response bodies for these paths will NOT be logged (e.g., to hide tokens)
SENSITIVE_RESPONSE_PATHS = [
    "/api/v1/auth/login",
    "/api/v1/auth/token",
    "/api/v1/users/me",
]

EXCEPTION_TO_STATUS_CODE = {
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    EmailAlreadyExistsError: status.HTTP_409_CONFLICT,
    UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
    UserException: status.HTTP_400_BAD_REQUEST,
    MFAException: status.HTTP_400_BAD_REQUEST,
    ServiceException: status.HTTP_400_BAD_REQUEST,
}


# --- Utility Functions ---
def path_matches(path: str, patterns: list[str]) -> bool:
    """Check if path starts with any of the given prefixes."""
    return any(path.startswith(p) for p in patterns)


def sanitize_json(obj: Any, max_len: int = 2000) -> Any:
    """Recursively redact sensitive fields and truncate long strings."""
    SENSITIVE_KEYS = {
        "password",
        "token",
        "secret",
        "key",
        "current_password",
        "new_password",
        "confirm_password",
    }

    if isinstance(obj, dict):
        return {
            k: ("[REDACTED]" if k.lower() in SENSITIVE_KEYS else sanitize_json(v, max_len))
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [sanitize_json(v, max_len) for v in obj]
    elif isinstance(obj, str):
        if len(obj) > max_len:
            return obj[:max_len] + "...[TRUNCATED]"
        return obj
    return obj


# --- Exception Middleware ---
class ServiceExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            return await call_next(request)
        except ServiceException as exc:
            status_code = EXCEPTION_TO_STATUS_CODE.get(type(exc), status.HTTP_400_BAD_REQUEST)
            app_logger.warning(
                f"Service Exception Handled: Status={status_code}, "
                f"Detail='{exc.detail}', Path={request.url.path}"
            )
            return JSONResponse(status_code=status_code, content={"detail": exc.detail})


# --- Request Body Buffer Middleware ---
class RequestBodyBufferMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Middleware to read and store request body in state for later use."""
        if "body" not in request.state.__dict__:
            body = await request.body()
            request.state.body = body
            # Make the body available for future reads by other middleware/endpoints
            request._body = body

        response = await call_next(request)
        return response


# --- Enhanced Audit Middleware ---
class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        response_body_bytes = b""
        try:
            response = await call_next(request)
            response_body_bytes = await self._read_response_body(response)
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            self._log_error(request, exc, duration_ms)
            raise exc

        duration_ms = (time.time() - start_time) * 1000
        if path_matches(request.url.path, SKIP_AUDIT_PATHS):
            return self._rebuild_response(response, response_body_bytes)

        audit_data = self._build_audit_data(request, response, response_body_bytes, duration_ms)
        audit_logger.info("http_request", audit_data)
        return self._rebuild_response(response, response_body_bytes)

    async def _read_response_body(self, response: Response) -> bytes:
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        return body

    def _log_error(self, request: Request, exc: Exception, duration_ms: float):
        audit_logger.error(
            "request_error",
            {
                "path": request.url.path,
                "method": request.method,
                "client_ip": getattr(request.client, "host", "unknown"),
                "user": self._get_user_for_log(request),
                "error": str(exc),
                "duration_ms": round(duration_ms, 2),
            },
        )

    def _rebuild_response(self, response: Response, body: bytes) -> Response:
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    def _build_audit_data(
        self, request: Request, response: Response, response_body_bytes: bytes, duration_ms: float
    ) -> Dict[str, Any]:
        client_ip = getattr(request.client, "host", "unknown")
        user_for_log = self._get_user_for_log(request)
        audit_data: Dict[str, Any] = {
            "user": user_for_log,
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
        if not path_matches(request.url.path, SENSITIVE_REQUEST_PATHS) and hasattr(request.state, "body"):
            try:
                parsed = json.loads(request.state.body)
                audit_data["request_body"] = sanitize_json(parsed)
            except Exception:
                audit_data["request_body"] = "[non-json_body]"
        if not path_matches(request.url.path, SENSITIVE_RESPONSE_PATHS) and response_body_bytes:
            try:
                parsed_resp = json.loads(response_body_bytes.decode("utf-8"))
                audit_data["response_body"] = sanitize_json(parsed_resp)
            except Exception:
                audit_data["response_body"] = "[non-json_body]"
        return audit_data

    def _get_user_for_log(self, request: Request) -> str:
        user_scope = request.scope.get("user")
        if user_scope and getattr(user_scope, "is_authenticated", False):
            username = getattr(user_scope, "email", None)
            user_id = getattr(user_scope, "user_id", None)
            return username or f"user_id:{user_id}"
        return "anonymous"
