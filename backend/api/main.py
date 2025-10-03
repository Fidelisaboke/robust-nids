from fastapi import FastAPI
from .routers import auth

app = FastAPI(title='Robust NIDS API', version='1.0.0')

# Include API routers
app.include_router(auth.router)


@app.get('/')
def health_check():
    return {'message': 'API is running smoothly!'}
