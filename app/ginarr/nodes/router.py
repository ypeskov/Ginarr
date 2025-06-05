from icecream import ic

from app.ginarr.llm.router_llm import router_llm

ic.configureOutput(includeContext=True)


async def router_node(state: dict) -> dict:
    user_input = state["input"]
    result = await router_llm.ainvoke({"input": user_input})
    ic(result)
    state["route"] = result["route"]
    return state
