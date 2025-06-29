import json
from typing import Literal, get_args

from icecream import ic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage

from app.ginarr.llm.llm_provider import router_selector_llm
from app.core.i18n.prompts import get_prompt
from app.core.logger.app_logger import log

ic.configureOutput(includeContext=True)

type RouteName = Literal["memory", "tool", "llm", "web_search", "memorize", "custom_end", "llm_reasoning"]

ALLOWED_ROUTES = set(get_args(RouteName))

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", get_prompt("router.llm.route_selector")),
        ("user", "{input}"),
    ]
)

def create_router_llm(prompt: ChatPromptTemplate, llm: BaseChatModel) -> Runnable:
    def extract_route(msg: AIMessage) -> dict:
        log.info(msg.content)
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
            "route": text_lower if text_lower in ALLOWED_ROUTES else "llm"
        }

    route_result = prompt | llm | RunnableLambda(extract_route)

    return route_result

router_llm = create_router_llm(prompt, router_selector_llm)
log.info("router_llm created")
