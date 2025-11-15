from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from starlette.middleware.authentication import AuthenticationMiddleware

from api.exception_handlers import exc_handlers
from api.middleware import AuditMiddleware, RequestBodyBufferMiddleware, ServiceExceptionHandlerMiddleware
from api.routers import auth, mfa, nids, reports, roles, users
from core.auth_backend import JWTAuthBackend
from core.config import settings
from core.logging import setup_logging
from ml.models.loader import MODEL_BUNDLE

# Set up logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load ML models on startup."""
    MODEL_BUNDLE.load_all()
    print("ML model loader meta: ", MODEL_BUNDLE.meta)
    yield


app = FastAPI(lifespan=lifespan, title=f"{settings.APP_NAME} API", version="0.1.0")

# Origins (Frontend URLs)
origins = settings.BACKEND_CORS_ORIGINS

# Custom Middlewares - added in order
app.add_middleware(ServiceExceptionHandlerMiddleware)  # noqa
app.add_middleware(RequestBodyBufferMiddleware)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())
app.add_middleware(AuditMiddleware)

# Pagination support
add_pagination(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(mfa.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(nids.router)
app.include_router(reports.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    handler = exc_handlers.get(type(exc))
    if handler:
        return await handler(request, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint to check if API is running.
    """
    return {
        "message": "API is running smoothly!",
        "app_name": settings.APP_NAME,
        "version": app.version,
        "debug": settings.DEBUG,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    Returns 200 OK if all services are healthy.
    """
    return {"status": "healthy"}
