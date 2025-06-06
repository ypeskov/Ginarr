from langchain.chat_models import init_chat_model
from app.ginarr.settings import settings as ginarr_settings


def create_llm(model_name: str, use_local: bool = False):
    """
    Create an LLM instance from a model name
    Args:
        model_name: (str) The name of the model to create
        use_local: (bool) Whether to use a local model
    Returns:
        (ChatOpenAI) An LLM instance
    """
    if use_local:
        return init_chat_model(
            f"ollama:{model_name}",
            config={
                "base_url": "http://localhost:11434",
                "temperature": 0,
            },
        )

    return init_chat_model(
        f"openai:{model_name}",
        temperature=0,
        openai_api_key=ginarr_settings.OPENAI_API_KEY,
    )


router_selector_llm = create_llm("mistral", use_local=True)
# router_selector_llm = create_llm("gpt-4.1-nano", use_local=False)

# chat_llm = create_llm("gpt-4o", use_local=False)
chat_llm = create_llm("mistral", use_local=True)
# chat_llm = create_llm("llama3", use_local=True)
