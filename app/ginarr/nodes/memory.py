from icecream import ic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState
from app.ginarr.llm.allowed_routes import RouteNameEnum
from app.ginarr.llm.llm_provider import chat_llm
from app.models.MemoryChunk import MemoryChunk
from app.services.search.embedding_search import search_embeddings

ic.configureOutput(includeContext=True)


relevance_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Ты проверяешь, насколько найденный текст отвечает на запрос пользователя. Ответь 'yes' или 'no'."),
        ("user", "Запрос: {query}\nНайденный текст: {found}"),
    ]
)

relevance_checker = relevance_prompt | chat_llm | RunnableLambda(lambda msg: msg.content.strip().lower() == "yes")


# The node that performs retrieval (RAG) using your embedding backend
async def memory_node(state: GinarrState, config: RunnableConfig) -> GinarrState:
    log.info("Entering memory_node")

    state.visited_routes.append(RouteNameEnum.MEMORY)

    user_input = state.input
    user_id = state.user_id

    db_session = config.get("configurable", {}).get("db_session", None)

    # search in longterm memory
    results: list[MemoryChunk] = await search_embeddings(db_session, user_id, user_input, embedding_types=["text"])
    matches = [
        {
            "id": chunk.id,
            "text": chunk.content,
            "score": chunk.score,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
        }
        for chunk in results
    ]

    state.result = {
        "type": "memory",
        "input": user_input,
        "output": matches,
    }

    log.info("Exiting memory_node")
    return state
