import functools
import inspect
from collections.abc import Callable
from typing import Any

from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import Settings
from app.services.route_agent.models import AgentTool, ToolCallResult


class ToolExecuted(Exception):
    def __init__(self, tool_name: str, params: dict[str, Any], result: Any):
        self.tool_name = tool_name
        self.params = params
        self.result = result


class RouteAgentService:
    def __init__(self, settings: Settings):
        self.settings = settings

        self._model = OpenAIResponsesModel(
            model_name=self.settings.ollama_model,
            provider=OpenAIProvider(base_url=f'{self.settings.ollama_base_url}/v1'),
            settings=OpenAIResponsesModelSettings(
                temperature=0.2,
                top_k=50,
            ),
        )
        self.agent: Agent | None = None

    def build_agent(
        self,
        system_prompt: str,
        tool: AgentTool,
        model_settings: ModelSettings | None,
    ) -> 'RouteAgentService':
        self.agent = Agent(
            self._model,
            system_prompt=system_prompt,
            model_settings=model_settings,
        )

        if self.agent:
            self.agent.tool_plain(self.wrap_tool(tool))

        return self

    def wrap_tool(self, tool: AgentTool) -> Callable:
        sig = inspect.signature(tool.func)

        async def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = dict(bound.arguments)

            result = tool.func(*args, **kwargs)
            if hasattr(result, '__await__'):
                result = await result

            raise ToolExecuted(
                tool_name=tool.name,
                params=params,
                result=result,
            )

        functools.wraps(tool.func)(wrapper)
        wrapper.__name__ = tool.name
        wrapper.__doc__ = tool.description

        return wrapper

    async def run(self, message: str) -> ToolCallResult:
        if not self.agent:
            raise ValueError('Agent not built')

        try:
            await self.agent.run(message)
        except ToolExecuted as exc:
            return ToolCallResult(
                tool_name=exc.tool_name,
                params=exc.params,
                result=exc.result,
            )

        raise RuntimeError('Agent finished without calling the tool')
