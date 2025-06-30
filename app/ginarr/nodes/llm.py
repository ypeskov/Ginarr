import time

from icecream import ic
from langchain_core.prompts import ChatPromptTemplate

from app.core.i18n.prompts import get_prompt
from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState
from app.ginarr.llm.llm_provider import chat_llm

ic.configureOutput(includeContext=True)


async def llm_node(state: GinarrState) -> GinarrState:
    log.info("Entering llm_node")
    user_input = state.input
    history = state.history

    history.append({"role": "user", "content": user_input})

    messages = [{"role": "system", "content": get_prompt("router.llm.system_prompt")}]
    # Extend history with user and assistant messages
    messages.extend([{"role": h["role"], "content": h["content"]} for h in history])
    # Add final answer prompt if LLM decided to end the conversation
    messages.append({"role": "system", "content": get_prompt("router.llm.system_prompt_answer_after_found_results")})
    # remove empty assistant messages. Llama3 fails if there are empty assistant messages
    messages = [m for m in history if not (m["role"] == "assistant" and not m["content"].strip())]

    prompt = ChatPromptTemplate.from_messages(messages)
    response = await chat_llm.ainvoke(prompt.invoke({"input": user_input}))

    # Handle both single message and message list responses
    content = ""
    if hasattr(response, "content"):
        content = str(response.content)
    elif isinstance(response, list) and len(response) > 0:
        content = str(response[0].content)
    else:
        content = str(response)

    if content.endswith("[[FINAL_ANSWER]]"):
        state.is_done = True
        content = content.replace("[[FINAL_ANSWER]]", "").strip()

    history.append({"role": "assistant", "content": content})

    # Keep only the last 10 user-assistant pairs (i.e., 20 messages)
    history = history[-20:]

    # Update state
    state.history = history
    state.result = {
        "type": "llm",
        "input": user_input,
        "output": content,
    }

    log.info("Exiting llm_node")
    return state


def summarize_found_result_node(state: GinarrState) -> GinarrState:
    log.info("Entering summarize_found_result_node")

    found_results = state.result.get("output", [])
    user_input = state.input
    previous_context = state.context

    found_results_str = ""
    for i, result in enumerate(found_results):
        result_str = f"{i + 1}. Text: {result['text']}"

        if "score" in result and isinstance(result["score"], (int, float)):
            result_str += f"\nScore: {result['score']:.3f}"

        result_str += f"\nDate: {result.get('created_at', 'unknown')}"

        # add empty line between results
        if i < len(found_results) - 1:
            result_str += "\n\n"

        found_results_str += result_str

    messages = []
    if state.route == "tool":
        messages.append(("system", get_prompt("router.tool.summary")))
        messages.append(("system", get_prompt("router.tool.system_prompt_answer_after_tool_result")))
    elif state.route == "memory":
        messages.append(("system", get_prompt("router.memory.summary")))
        messages.append(("system", get_prompt("router.llm.system_prompt_answer_after_found_results")))
    else:
        messages.append(("system", get_prompt("router.memory.summary")))
        messages.append(("system", get_prompt("router.llm.system_prompt_answer_after_found_results")))

    messages.append(("system", get_prompt("router.llm.context")))
    messages.append(("user", get_prompt("router.summary.prompt.user")))
    messages.append(("system", get_prompt("router.summary.prompt.found_results")))

    prompt = ChatPromptTemplate.from_messages(messages)

    start_time = time.time()
    response = chat_llm.invoke(
        prompt.invoke(
            {
                "input": found_results_str,
                "user_input": user_input,
                "context": previous_context,
                "found_results_str": found_results_str,
            }
        )
    )
    end_time = time.time()
    log.info(f"Time taken to summarize: {end_time - start_time} seconds")

    # Handle both single message and message list responses
    content = ""
    if hasattr(response, "content"):
        content = str(response.content)
    elif isinstance(response, list) and len(response) > 0:
        content = str(response[0].content)
    else:
        content = str(response)

    if content.endswith("[[FINAL_ANSWER]]"):
        log.info("Final answer detected")
        state.is_done = True
        content = content.replace("[[FINAL_ANSWER]]", "").strip()
    elif content.endswith("[[NO_DATA]]"):
        log.info("No data detected")
        state.is_done = False
        content = content.replace("[[NO_DATA]]", "").strip()
    else:
        log.info("No final answer detected")
        content = "Пока информации нет, продолжаю поиск"
        state.is_done = False

    state.result = {
        "type": "llm",
        "input": user_input,
        "output": content,
    }

    state.context = user_input + "\n" + str(content)

    log.info("Exiting summarize_found_result_node")
    return state
