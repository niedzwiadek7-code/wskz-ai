from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.routers.messages.models import MessageRequest
from app.routers.messages.service import process_received_message

router = APIRouter()


@router.post(
    '',
    summary='Route an incoming message to the correct department',
    description=(
        'Analyzes the content of a message using an AI agent backed by a local LLM, '
        'determines the most relevant department, and sends an email to that department. '
        'The outgoing email includes a Reply-To header set to the original sender.'
    ),
)
async def process_message(
    payload: MessageRequest,
    settings: Settings = Depends(get_settings),
):
    try:
        await process_received_message(
            payload,
            settings,
        )

        return {'success': True}
    except Exception as e:
        return {'error': str(e)}
