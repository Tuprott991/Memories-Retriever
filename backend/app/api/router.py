"""
API Router - Main router for all API endpoints
"""

from fastapi import APIRouter
from app.api.endpoints import memories, chat, users, upload

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    memories.router,
    prefix="/memories",
    tags=["memories"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"]
)
