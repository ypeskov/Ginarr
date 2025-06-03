from langchain_openai import ChatOpenAI

from app.config.settings import settings

# Create an LLM instance (can be moved outside for reuse)
llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=settings.OPENAI_API_KEY)


async def llm_node(state: dict) -> dict:
    user_input = state.get("input", "")
    response = llm.invoke(user_input)

    state["result"] = {
        "type": "llm",
        "input": user_input,
        "output": response.content,
    }

    return state
