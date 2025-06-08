from icecream import ic
from langchain_core.prompts import ChatPromptTemplate

from app.ginarr.llm.llm_provider import chat_llm
from app.ginarr.graph_state import GinarrState
from app.core.logger.app_logger import log

ic.configureOutput(includeContext=True)


async def llm_node(state: GinarrState) -> GinarrState:
    log.info("Entering llm_node")
    user_input = state.get("input", "")
    history = state.get("history", [])

    history.append({"role": "user", "content": user_input})

    messages = [("system", "Ты помощник. Отвечай на русском. Учитывай весь предыдущий диалог.")] + [
        (h["role"], h["content"]) for h in history
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    response = chat_llm.invoke(prompt.invoke({"input": user_input}))

    history.append({"role": "assistant", "content": str(response.content)})

    # Keep only the last 20 user-assistant pairs (i.e., 40 messages)
    history = history[-40:]

    # Update state
    state["history"] = history
    state["result"] = {
        "type": "llm",
        "input": user_input,
        "output": response.content,
    }

    log.info("Exiting llm_node")
    return state


def summarize_found_result_node(state: GinarrState) -> GinarrState:
    log.info("Entering summarize_found_result_node")
    found_results = state.get("result", {}).get("output", [])
    user_input = state.get("input", "")
    history = state.get("history", [])
    history.append({"role": "user", "content": user_input})

    found_results_str = "\n\n".join(
        [
            f"{i + 1}. Text: {result['text']}"
            + (
                f"\nScore: {result['score']:.3f}"
                if "score" in result and isinstance(result["score"], (int, float))
                else ""
            )
            + f"\nDate: {result.get('created_at', 'unknown')}"
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

    history.append({"role": "assistant", "content": str(response.content)})
    history = history[-40:]
    state["history"] = history

    log.info("Exiting summarize_found_result_node")
    return state
