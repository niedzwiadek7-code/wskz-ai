from fastapi import APIRouter

from app.routers.messages.router import router as messages_router

api_router = APIRouter()

api_router.include_router(messages_router, prefix='/messages', tags=['Messages'])
