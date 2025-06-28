import time
from icecream import ic
from langchain_core.prompts import ChatPromptTemplate

from app.ginarr.llm.llm_provider import chat_llm
from app.ginarr.graph_state import GinarrState
from app.core.logger.app_logger import log
from app.core.i18n.prompts import get_prompt

ic.configureOutput(includeContext=True)


async def llm_node(state: GinarrState) -> GinarrState:
    log.info("Entering llm_node")
    user_input = state.input
    history = state.history

    history.append({"role": "user", "content": user_input})

    messages = [("system", get_prompt("router.llm.system_prompt"))]
    # Extend history with user and assistant messages
    messages.extend([(h["role"], h["content"]) for h in history])
    # Add final answer prompt if LLM decided to end the conversation
    messages.append(("system", get_prompt("router.llm.system_prompt_final_answer_after_found_results")))

    prompt = ChatPromptTemplate.from_messages(messages)

    response = await chat_llm.ainvoke(prompt.invoke({"input": user_input}))
    
    # Handle both single message and message list responses
    content = ""
    if hasattr(response, 'content'):
        content = str(response.content)
    elif isinstance(response, list) and len(response) > 0:
        content = str(response[0].content)
    else:
        content = str(response)
    
    if content.endswith("[[FINAL_ANSWER]]"):
        state.is_done = True
        content = content.replace("[[FINAL_ANSWER]]", "").strip()

    history.append({"role": "assistant", "content": content})

    # Keep only the last 20 user-assistant pairs (i.e., 40 messages)
    history = history[-40:]

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

    messages = [
        ("system", get_prompt("router.memory.summary")),
        ("user", get_prompt("router.llm.context")),
        ("user", get_prompt("router.summary.prompt.user")),
        ("user", get_prompt("router.summary.prompt.found_results")),
    ]
    messages.append(("user", get_prompt("router.llm.system_prompt_final_answer_after_found_results")))

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
    if hasattr(response, 'content'):
        content = str(response.content)
    elif isinstance(response, list) and len(response) > 0:
        content = str(response[0].content)
    else:
        content = str(response)

    if content.endswith("[[FINAL_ANSWER]]"):
        log.info("Final answer detected")
        state.is_done = True
        content = content.replace("[[FINAL_ANSWER]]", "").strip()

    state.result = {
        "type": "llm",
        "input": user_input,
        "output": content,
    }

    state.context = user_input + "\n" + str(content)

    log.info("Exiting summarize_found_result_node")
    return state
