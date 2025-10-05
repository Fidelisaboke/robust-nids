from fastapi import FastAPI

from .routers import auth, nids, users

app = FastAPI(title='Robust NIDS API', version='1.0.0')

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(nids.router)



@app.get('/')
def health_check():
    return {'message': 'API is running smoothly!'}
