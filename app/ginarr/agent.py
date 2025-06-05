from langchain_core.runnables import RunnableConfig
from langchain_core.runnables import Runnable
from app.models.User import User
from sqlalchemy.ext.asyncio import AsyncSession
from icecream import ic

ic.configureOutput(includeContext=True)


async def run_ginarr_agent(user_input: str, graph_instance: Runnable, user: User, db_session: AsyncSession) -> dict:
    state = {"input": user_input, "user_id": user.id}
    config: RunnableConfig = {"configurable": {"thread_id": user.id, "db_session": db_session}}
    result = await graph_instance.ainvoke(state, config=config)
    output = result.get("result", {})

    return {
        "type": output.get("type"),
        "input": output.get("input"),
        "output": output.get("output") or output.get("matches"),
    }
