from icecream import ic

from app.ginarr.llm.llm_provider import chat_llm

ic.configureOutput(includeContext=True)


async def llm_node(state: dict) -> dict:
    user_input = state.get("input", "")
    response = chat_llm.invoke(user_input)

    state["result"] = {
        "type": "llm",
        "input": user_input,
        "output": response.content,
    }

    return state
