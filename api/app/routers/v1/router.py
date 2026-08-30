from fastapi import APIRouter

from app.routers.v1.messages import router as messages_v1_router

api_v1_router = APIRouter()

api_v1_router.include_router(messages_v1_router, prefix='/messages', tags=['Messages'])
