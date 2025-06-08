from langchain_core.runnables import RunnableConfig
from langchain_core.runnables import Runnable
from sqlalchemy.ext.asyncio import AsyncSession
from icecream import ic

from app.core.logger.app_logger import log
from app.models.User import User

ic.configureOutput(includeContext=True)


async def run_ginarr_agent(user_input: str, graph_instance: Runnable, user: User, db_session: AsyncSession) -> dict:
    try:
        checkpoint_tuple = await graph_instance.checkpointer.aget_tuple({"configurable": {"thread_id": str(user.id)}})  # type: ignore
        state = checkpoint_tuple.checkpoint if checkpoint_tuple else {}
        log.info("Loaded previous state")
    except Exception as e:
        log.error(f"Error loading previous state: {e}", exc_info=True)
        state = {}
        log.info("No previous state, starting fresh")

    state["input"] = user_input
    state["user_id"] = user.id

    config: RunnableConfig = {
        "configurable": {
            "thread_id": user.id,
            "db_session": db_session,
        },
    }
    result = await graph_instance.ainvoke(state, config=config)
    output = result.get("result", {})

    return {
        "type": output.get("type"),
        "input": output.get("input"),
        "output": output.get("output") or output.get("matches"),
    }
