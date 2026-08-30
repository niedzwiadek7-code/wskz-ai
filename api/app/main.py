from fastapi import FastAPI

from app.config import get_settings
from app.routers.router import api_router

settings = get_settings()

app = FastAPI(
    title='WSKZ AI Message Router',
    description='AI-powered message categorization and routing PoC.',
    version='0.1.0',
    docs_url='/api/v1/docs',
    redoc_url='/api/v1/redoc',
    openapi_url='/api/v1/openapi.json',
)


app.include_router(api_router, prefix='/api/v1')


@app.get('/health', tags=['health'])
async def health() -> dict[str, str]:
    return {'status': 'ok'}
