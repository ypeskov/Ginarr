from datetime import datetime, timezone

from icecream import ic

from app.core.logger.app_logger import log
from app.ginarr.graph_state import GinarrState
from app.ginarr.tools.universal_answer import universal_question_tool

ic.configureOutput(includeContext=True)

REGISTERED_TOOLS = {
    "universal_question_tool": universal_question_tool,
}


# A placeholder tool execution node
async def tool_node(state: GinarrState) -> GinarrState:
    log.info("Entering tool_node")
    user_input = state.input

    # TODO: implement tool execution
    # TODO: implement tool selection
    tool_result = [
        {
            "text": f"Tool executed with input: {user_input}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "score": 1.0,
        }
    ]

    state.result = {
        "type": "tool",
        "input": user_input,
        "output": tool_result,
    }

    log.info("Exiting tool_node")
    return state
