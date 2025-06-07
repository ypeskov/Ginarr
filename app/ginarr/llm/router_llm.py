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
                "Ответь только ОДНИМ словом, без пояснений. Возможные опции: memory, tool, llm, write."
                "Пояснения: memory - поиск в памяти, tool - вызов инструмента, llm - вызов LLM, write - запись в память."
                "Если однозначно нельзя определить, то ответь llm."
            ),
        ),
        ("user", "{input}"),
    ]
)


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
        return {"route": text if text in {"memory", "tool", "llm", "write"} else "llm"}

    # Try bind_tools, but fallback gracefully
    try:
        if hasattr(llm, "bind_tools"):
            llm = llm.bind_tools([route_selector], tool_choice="route_selector")
    except Exception:
        pass

    return prompt | llm | RunnableLambda(extract_route)


router_llm = create_router_llm(prompt, router_selector_llm)
