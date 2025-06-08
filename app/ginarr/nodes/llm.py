from icecream import ic
from langchain_core.prompts import ChatPromptTemplate

from app.ginarr.llm.llm_provider import chat_llm

ic.configureOutput(includeContext=True)


async def llm_node(state: dict) -> dict:
    user_input = state.get("input", "")
    history = state.get("history", [])
    history.append({"role": "user", "content": user_input})
    if len(history) > 20:
        history = history[-20:]

    messages = [("system", "Ты помощник. Отвечай на русском. Учитывай весь предыдущий диалог.")] + [
        (h["role"], h["content"]) for h in history
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    response = chat_llm.invoke(prompt.invoke({"input": user_input}))

    history.append({"role": "assistant", "content": response.content})

    state["result"] = {
        "type": "llm",
        "input": user_input,
        "output": response.content,
    }

    if len(history) > 20:
        history = history[-20:]
    state["history"] = history

    return state


def summarize_found_result_node(state: dict) -> dict:
    found_results = state.get("result", {}).get("output", [])
    user_input = state.get("input", "")
    history = state.get("history", [])
    history.append({"role": "user", "content": user_input})

    found_results_str = "\n\n".join(
        [
            f"{i + 1}. Text: {result['text']}\nScore: {result['score']:.3f}\nDate: {result['created_at']}"
            for i, result in enumerate(found_results)
        ]
    )

    messages = [
        (
            "system",
            "Ты аналитик. Получаешь найденные результаты (с текстом, датой и score) и составляешь краткий вывод. "
            "Вывод должен быть на русском языке. Не более 100 слов.",
        )
    ]

    for turn in history:
        messages.append((turn["role"], turn["content"]))

    messages.append(("user", f"Пользователь запросил: [{user_input}]\nНайденные результаты: [{found_results_str}]"))
    prompt = ChatPromptTemplate.from_messages(messages)

    response = chat_llm.invoke(prompt.invoke({"input": found_results_str}))

    state["result"] = {
        "type": "llm",
        "input": f"Пользователь запросил: {user_input}\nНайденные результаты: {found_results_str[:300]}...",
        "output": response.content,
    }

    return state
