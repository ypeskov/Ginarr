from datetime import datetime, timezone


# A placeholder tool execution node
async def tool_node(state: dict) -> dict:
    user_input = state.get("input", "")

    # TODO: implement tool execution
    # TODO: implement tool selection
    tool_result = [
        {
            "text": f"Tool executed with input: {user_input}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "score": 1.0,
        }
    ]

    state["result"] = {
        "type": "tool",
        "input": user_input,
        "output": tool_result,
    }

    return state
