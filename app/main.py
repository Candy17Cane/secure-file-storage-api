from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base
from app.routers import auth, files


# ===== CREATE APPLICATION =====
app = FastAPI(title=settings.APP_NAME)


# ===== CREATE BASE =====
Base.metadata.create_all(bind=engine)


# ===== CONNECTING ROUTERS =====
app.include_router(auth.router)
app.include_router(files.router)


# ===== TESTING ENDPOINT =====
@app.get('/')
def root():
    return {'message': 'Secure File Storage APIis running'}