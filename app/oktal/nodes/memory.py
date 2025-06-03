from icecream import ic
from langchain_core.runnables import RunnableConfig

from app.services.search.embedding_search import search_embeddings

ic.configureOutput(includeContext=True)


# The node that performs retrieval (RAG) using your embedding backend
async def memory_node(state: dict, config: RunnableConfig) -> dict:
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
        "matches": matches,
    }

    return state
