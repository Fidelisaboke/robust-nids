from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .exception_handlers import exc_handlers
from .middleware import ServiceExceptionHandlerMiddleware
from .routers import auth, mfa, nids, users

app = FastAPI(title='Robust NIDS API', version='1.0.0')

# Origins (Frontend URLs)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# Service exception handling middleware
app.add_middleware(ServiceExceptionHandlerMiddleware) # noqa

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_body_to_state(request: Request, call_next):
    """Middleware to read and store request body in state for rate limiting."""
    if "body" not in request.state.__dict__:
        body = await request.body()
        request.state.body = body

        # Make the body available for future reads
        request._body = body

    response = await call_next(request)
    return response


# Include API routers
app.include_router(auth.router)
app.include_router(mfa.router)
app.include_router(users.router)
app.include_router(nids.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    handler = exc_handlers.get(type(exc))
    if handler:
        return await handler(request, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'An unexpected error occurred.'},
    )


# Health check endpoint
@app.get('/')
def health_check():
    return {'message': 'API is running smoothly!'}
