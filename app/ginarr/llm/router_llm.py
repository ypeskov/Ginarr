from typing import Literal

from icecream import ic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.tools import tool

from app.ginarr.llm.llm_provider import router_selector_llm

ic.configureOutput(includeContext=True)


@tool
def route_selector(route: Literal["memory", "tool", "llm", "write"]):
    """Выбирает маршрут: memory (поиск в памяти), tool (вызов инструмента), llm (LLM обработка), write (запись в память)"""
    return route


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Ты маршрутизатор. Получаешь пользовательский запрос и выбираешь, что с ним делать. "
                "Ответь только ОДНИМ словом, без пояснений. Возможные опции: memory, tool, llm."
                "Пояснения: "
                "memory - поиск в памяти (там находится Postgres + векторный  семантический поиск), "
                "tool - вызов инструмента, "
                "llm - вызов LLM, "
                "Если однозначно нельзя определить, то ответь llm."
            ),
        ),
        ("user", "{input}"),
    ]
)


def safe_bind_tools(llm, tools, tool_choice=None):
    """Safe bind tools to LLM
    Args:
       llm: (BaseChatModel) LLM to bind tools to
       tools: (list) List of tools to bind
       tool_choice: (str) Tool choice to use
    Returns:
       (BaseChatModel) LLM with tools bound
    """
    if getattr(llm, "supports_tools", False) and hasattr(llm, "bind_tools"):
        return llm.bind_tools(tools, tool_choice=tool_choice)
    return llm


def create_router_llm(prompt, llm) -> Runnable:
    def extract_route(msg) -> dict:
        # OpenAI-style tool calling
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            try:
                return {"route": msg.tool_calls[0]["args"]["route"]}
            except Exception:
                pass
        # Fallback: plain text from model
        text = getattr(msg, "content", "").strip().lower()
        return {"route": text if text in {"memory", "tool", "llm"} else "llm"}

    # Try bind_tools, but fallback gracefully
    try:
        llm = safe_bind_tools(llm, [route_selector], tool_choice="route_selector")
    except Exception:
        pass

    return prompt | llm | RunnableLambda(extract_route)


router_llm = create_router_llm(prompt, router_selector_llm)
