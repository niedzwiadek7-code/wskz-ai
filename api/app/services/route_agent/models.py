from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class AgentTool(BaseModel):
    name: str
    description: str
    func: Callable


class ToolCallResult(BaseModel):
    tool_name: str
    params: dict[str, Any]
    result: Any
