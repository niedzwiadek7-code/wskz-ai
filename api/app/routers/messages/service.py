from pydantic_ai import ModelSettings

from app.config import Settings
from app.routers.messages.models import Department, MessageRequest
from app.routers.messages.prompts import ASSIGN_MESSAGE_TO_SECTION_PROMPT, SEND_EMAIL_DESCRIPTION, USER_MESSAGE_PROMPT
from app.services.email.base import EmailService
from app.services.route_agent.base import RouteAgentService
from app.services.route_agent.models import AgentTool

_DEPARTMENT_TO_EMAIL = {
    Department.HUMAN_RESOURCES: 'human-resources@example.com',
    Department.HELP_DESK: 'help-desk@example.com',
    Department.IT: 'it@example.com',
    Department.HR_RECORDS: 'kadry@example.com',
    Department.OTHER: 'other@example.com',
}


async def process_received_message(
    payload: MessageRequest,
    settings: Settings,
) -> None:
    async def send_email(
        department: Department,
        subject: str,
        body: str,
        reply_to: str,
    ) -> None:
        try:
            EmailService(settings).send(
                recipient=_DEPARTMENT_TO_EMAIL[department],
                subject=subject,
                body=body,
                reply_to=reply_to,
            )
        except Exception as e:
            raise ValueError(f'Failed to send email: {e}')

    await (
        RouteAgentService(settings)
        .build_agent(
            system_prompt=ASSIGN_MESSAGE_TO_SECTION_PROMPT,
            tool=AgentTool(
                name='send_email',
                description=SEND_EMAIL_DESCRIPTION,
                func=send_email,
            ),
            model_settings=ModelSettings(
                temperature=0,
                top_p=0.1,
                thinking=False,
                seed=42,
            ),
        )
        .run(USER_MESSAGE_PROMPT.format(email=payload.email, message=payload.message))
    )
