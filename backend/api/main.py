from fastapi import FastAPI, Request

from .routers import auth, mfa, nids, users

app = FastAPI(title='Robust NIDS API', version='1.0.0')


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


@app.get('/')
def health_check():
    return {'message': 'API is running smoothly!'}
