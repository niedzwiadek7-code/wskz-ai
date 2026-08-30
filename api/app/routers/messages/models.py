from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field

from app.services.route_agent.models import ToolCallResult


class MessageRequest(BaseModel):
    email: EmailStr = Field(
        description='Email address of the sender, used as the Reply-To header on the routed message',
    )
    message: str = Field(
        description='Free-form, unstructured message content to be classified and routed to the appropriate department',
        min_length=1,
    )

class MessageResult(BaseModel):
    success: bool
    tool_result: ToolCallResult

class Department(StrEnum):
    HUMAN_RESOURCES = 'human resources'
    HELP_DESK = 'help desk'
    IT = 'IT'
    HR_RECORDS = 'HR records'
    OTHER = 'other'
