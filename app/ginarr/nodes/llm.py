from icecream import ic
from langchain_core.prompts import ChatPromptTemplate

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


def summarize_found_result_node(state: dict) -> dict:
    found_results = state.get("result", {}).get("output", [])
    user_input = state.get("input", "")

    found_results_str = "\n\n".join(
        [
            f"{i + 1}. Text: {result['text']}\nScore: {result['score']:.3f}\nDate: {result['created_at']}"
            for i, result in enumerate(found_results)
        ]
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Ты суммаризатор. Получаешь найденные результаты и суммируешь их в один текст."),
            ("user", f"Пользователь запросил: {user_input}\nНайденные результаты: {found_results_str}"),
        ]
    )

    response = chat_llm.invoke(prompt.invoke({"input": found_results_str}))

    state["result"] = {
        "type": "llm",
        "input": f"Пользователь запросил: {user_input}\nНайденные результаты: {found_results_str[:300]}...",
        "output": response.content,
    }

    return state
