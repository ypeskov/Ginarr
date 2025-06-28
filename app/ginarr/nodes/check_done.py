from icecream import ic
from langchain_core.prompts import ChatPromptTemplate

from app.ginarr.llm.llm_provider import chat_llm
from app.ginarr.graph_state import GinarrState
from app.core.logger.app_logger import log
from app.core.i18n.prompts import get_prompt


def check_done_node(state: GinarrState) -> GinarrState:
    log.info("Entering check_done_node")

    if state.is_done:
        log.info("Conversation is done")
        state.route = "custom_end"
    else:
        log.info("Conversation is not done. Reasoning...")
        state.route = "llm"

    log.info("Exiting check_done_node")
    return state
