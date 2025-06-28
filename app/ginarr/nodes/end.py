from icecream import ic

from app.ginarr.graph_state import GinarrState
from app.core.logger.app_logger import log
from app.services.chat.logger import save_chat_message
from app.models.ChatMessage import ChatMessage, AnswerGeneratedBy
from langchain_core.runnables import RunnableConfig

ic.configureOutput(includeContext=True)


async def end_node(state: GinarrState, config: RunnableConfig) -> GinarrState:
    """End node. Just clears state.
    Args:
        state: (GinarrState) State to clear
    Returns:
        GinarrState: State with cleared fields
    """
    log.info("Entering end_node")

    db_session = config.get("configurable", {}).get("db_session", None)
    if db_session is None:
        raise ValueError("DB session is required")

    user_id = state.user_id
    if user_id is None:
        raise ValueError("User ID is required")

    thread_id = state.user_id
    if thread_id is None:
        raise ValueError("Thread ID is required")
    thread_id = str(thread_id)

    user_input = state.input
    assistant_output = state.result.get("output", "")
    answer_generated_by = state.result.get("type", None)

    await save_chat_message(
        db_session=db_session,
        chat_message=ChatMessage(
            user_id=user_id,
            langgraph_thread_id=thread_id,
            role="user",
            content=user_input,
            preserved=False,
            answer_generated_by=AnswerGeneratedBy.USER_INPUT,
        ),
    )
    await save_chat_message(
        db_session=db_session,
        chat_message=ChatMessage(
            user_id=user_id,
            langgraph_thread_id=thread_id,
            role="assistant",
            content=assistant_output,
            preserved=False,
            answer_generated_by=answer_generated_by,
        ),
    )

    state.route = None
    log.info("Exiting end_node")

    return state
