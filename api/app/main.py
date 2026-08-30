from fastapi import FastAPI

from app.config import get_settings
from app.routers.v1.router import api_v1_router

settings = get_settings()

app = FastAPI(
    title='WSKZ AI Message Router',
    description='AI-powered message categorization and routing PoC.',
)

v1_app = FastAPI(
    title='WSKZ AI Message Router',
    description='AI-powered message categorization and routing PoC.',
    version='0.1.0',
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)

v1_app.include_router(api_v1_router)

app.mount('/api/v1', v1_app)

@app.get('/health', tags=['health'])
async def health() -> dict[str, str]:
    return {'status': 'ok'}
