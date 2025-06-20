import json
from typing import Literal

from icecream import ic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.tools import tool, BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage

from app.ginarr.llm.llm_provider import router_selector_llm
from app.core.i18n.prompts import get_prompt

ic.configureOutput(includeContext=True)

type RouteName = Literal["memory", "tool", "llm", "web_search", "memorize"]


@tool
def route_selector(
    route: RouteName,
) -> RouteName:
    """Selects a route:
        memory (search in memory),
        tool (tool call),
        llm (LLM processing),
        web_search (web search).
        memorize (memorize conversation).
        If you can't determine the route, return llm.
    Args:
        route: (str) Route to select
    Returns:
        (str) Route to select
    """
    return route


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", get_prompt("router.llm.route_selector")),
        ("user", "{input}"),
    ]
)


def safe_bind_tools(llm: BaseChatModel, tools: list[BaseTool], tool_choice: str | None = None) -> BaseChatModel:
    """Safe bind tools to LLM
    Args:
       llm: (BaseChatModel) LLM to bind tools to
       tools: (list) List of tools to bind
       tool_choice: (str) Tool choice to use
    Returns:
       (BaseChatModel) LLM with tools bound
    """
    if getattr(llm, "supports_tools", False) and hasattr(llm, "bind_tools"):
        return llm.bind_tools(tools, tool_choice=tool_choice)  # type: ignore
    return llm


def create_router_llm(prompt: ChatPromptTemplate, llm: BaseChatModel) -> Runnable:
    def extract_route(msg: AIMessage) -> dict:
        # ✅ OpenAI-style tool calling
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            try:
                args = msg.tool_calls[0]["args"]
                return {"route": args["route"]}
            except Exception:
                pass

        # ✅ JSON string (LLaMA-style)
        text = getattr(msg, "content", "").strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "route" in parsed:
                return parsed
        except Exception:
            pass

        # 🧯 Fallback: plain string match
        text_lower = text.lower()
        fallback = {"route": text_lower if text_lower in {"memory", "tool", "llm", "web_search", "memorize"} else "llm"}

        return fallback

    # Try bind_tools, but fallback gracefully
    try:
        llm = safe_bind_tools(llm, [route_selector], tool_choice="route_selector")
    except Exception:
        pass

    route_result = prompt | llm | RunnableLambda(extract_route)

    return route_result


router_llm = create_router_llm(prompt, router_selector_llm)
