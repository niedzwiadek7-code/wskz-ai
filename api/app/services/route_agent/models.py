from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class AgentTool(BaseModel):
    name: str
    description: str
    func: Callable

class ToolCallResult(BaseModel):
    tool_name: str = Field(..., description="Name of the tool that was called by the agent.")
    params: dict[str, Any] = Field(..., description="Arguments the tool was called with, keyed by parameter name.")
    result: Any = Field(..., description="Value returned by the tool after execution.")