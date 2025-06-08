from icecream import ic
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate

from app.ginarr.settings import settings
from app.core.logger.app_logger import log
from app.ginarr.llm.llm_provider import chat_llm
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
async def memory_node(state: dict, config: RunnableConfig) -> dict:
    state["fallback_to_llm"] = False

    user_input = state.get("input", "")
    user_id = state.get("user_id", "")

    db_session = config.get("configurable", {}).get("db_session", None)

    results = await search_embeddings(db_session, user_id, user_input, embedding_types=["text"])

    matches = [
        {
            "id": chunk.id,
            "text": chunk.content,
            "score": chunk.score,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
        }
        for chunk in results
    ]

    state["result"] = {
        "type": "memory",
        "input": user_input,
        "output": matches,
        "is_relevant": False,
        "top_score": 0,
    }

    if matches:
        top_score = matches[0]["score"]
        state["result"]["top_score"] = top_score
        ic(top_score)

        if top_score < settings.MEMORY_RELEVANCE_THRESHOLD:
            is_relevant = await relevance_checker.ainvoke({"query": state["input"], "found": matches[0]["text"]})
            ic(is_relevant)

            state["result"]["is_relevant"] = is_relevant if is_relevant is not None else False

            if not is_relevant:
                log.info("Searches are not relevant. Setting fallback_to_llm to True in memory_node")
                state["fallback_to_llm"] = True
        else:
            log.info("Searches are relevant. Setting is_relevant to True in memory_node")
            state["result"]["is_relevant"] = True
    else:
        state["fallback_to_llm"] = True

    return state
