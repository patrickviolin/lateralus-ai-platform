from app.ai.agent import Agent
from app.ai.agent.tools.factory import default_tool_factory
from app.ai.application import ApplicationContainer
from app.ai.graph import Graph
from app.ai.infra.http_initializer import create_http_client
from app.ai.infra.postgres_initializer import create_postgres_resources
from app.ai.infra.redis_initializer import create_redis_resources
from app.ai.model import Model
from app.ai.runtime.runner import Runner
from app.ai.streaming.dispatcher import StreamDispatcher
from app.config import get_settings


async def build_container() -> ApplicationContainer:
    settings = get_settings()
    http_client = await create_http_client()
    redis = await create_redis_resources(settings)
    postgres = await create_postgres_resources(settings)

    tools = default_tool_factory().create_tools()
    model = Model(
        tools,
        model=settings.openai_model,
        timeout=settings.openai_timeout,
        max_retries=settings.openai_max_retries,
    )
    graph = Graph(model, checkpointer=redis.checkpointer)
    agent = Agent(graph=graph, dispatcher=StreamDispatcher.default())
    runner = Runner(agent=agent)

    return ApplicationContainer(
        settings=settings,
        runner=runner,
        http_client=http_client,
        redis=redis,
        postgres=postgres,
    )
