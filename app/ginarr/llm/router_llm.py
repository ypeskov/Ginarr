import json
from typing import Any

from icecream import ic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda

from app.core.i18n.prompts import get_prompt
from app.core.logger.app_logger import log
from app.ginarr.llm.allowed_routes import RouteNameEnum, parse_route_or_default
from app.ginarr.llm.llm_provider import chat_llm

ic.configureOutput(includeContext=True)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", get_prompt("router.llm.route_selector")),
        ("user", "{input}"),
    ]
)


def create_router_llm(prompt: ChatPromptTemplate, llm: BaseChatModel) -> Runnable:
    """
    Create a router LLM
    Args:
        prompt: (ChatPromptTemplate) The prompt to use for the router LLM
        llm: (BaseChatModel) The LLM to use for the router LLM
    Returns:
        Runnable: The router LLM
    """

    def extract_route(msg: AIMessage) -> dict[str, Any]:
        """Extract the route from the message
        Args:
            msg: (AIMessage) The message to extract the route from
        Returns:
            dict: The route
        """
        text = str((msg.content or "")).strip()

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "route" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

        # Fallback: interpret raw text as route name
        text_lower = text.lower()
        return {
            "route": text_lower
            if parse_route_or_default(text_lower)
            else RouteNameEnum.LLM
        }

    route_result = prompt | llm | RunnableLambda(extract_route)

    return route_result


router_llm = create_router_llm(prompt, chat_llm)
log.info("router_llm created")
