import asyncio
import time

import app.config
from app.ai.agent import Agent


async def main():
    agent = Agent()
    start_time = time.perf_counter()
    async for frame in agent.use_agent("Qual o clima em São Paulo?"):
        elapsed = time.perf_counter() - start_time
        print(f"{elapsed:.2f}s | {frame}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
