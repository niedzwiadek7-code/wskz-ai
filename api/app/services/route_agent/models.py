from collections.abc import Callable

from pydantic import BaseModel


class AgentTool(BaseModel):
    name: str
    description: str
    func: Callable
