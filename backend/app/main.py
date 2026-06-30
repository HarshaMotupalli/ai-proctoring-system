"""
Main FastAPI application
"""

from fastapi import FastAPI

# Import routers
from app.api.routes.identity import router as identity_router
from app.api.websocket import router as websocket_router
from app.core.database import engine, Base
from app.models.user import User
from app.models.session import ExamSession
from app.models.violation import Violation
from app.models.exam_log import ExamLog

app = FastAPI()

from app.api.routes.logs import router as logs_router
app.include_router(logs_router)

from app.api.routes.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)

app.include_router(dashboard_router, prefix="/dashboard")

from app.api.routes.auth import router as auth_router

app.include_router(auth_router, prefix="/auth")

from app.api.routes.verify import router as verify_router

app.include_router(verify_router, prefix="/verify")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Proctoring System Running"}

# Include HTTP routes
app.include_router(identity_router, prefix="/identity")

# Include WebSocket routes
app.include_router(websocket_router)

print("MAIN.PY LOADED - WEBSOCKET ROUTER INCLUDED")

