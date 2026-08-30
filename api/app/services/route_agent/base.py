import functools
from collections.abc import Callable

from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import Settings
from app.services.route_agent.models import AgentTool


class ToolExecuted(Exception):
    def __init__(self, result):
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
        async def wrapper(*args, **kwargs):
            result = tool.func(*args, **kwargs)

            if hasattr(result, '__await__'):
                result = await result

            raise ToolExecuted(result)

        functools.wraps(tool.func)(wrapper)
        wrapper.__name__ = tool.name
        wrapper.__doc__ = tool.description

        return wrapper

    async def run(self, message: str) -> None:
        if not self.agent:
            raise ValueError('Agent not built')

        try:
            await self.agent.run(message)
        except ToolExecuted as exc:
            return exc.result
