from typing import Literal, TypedDict
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel

from app.core.logger.app_logger import log
from app.ginarr.settings import settings as ginarr_settings

ModelProvider = Literal["ollama", "openai", "google", "deepseek"]


class ModelConfig(TypedDict):
    provider: ModelProvider


MODEL_REGISTRY: dict[str, ModelConfig] = {
    "mistral": {"provider": "ollama"},
    "llama3": {"provider": "ollama"},
    "gpt-4": {"provider": "openai"},
    "gpt-4o": {"provider": "openai"},
    "gemini-pro": {"provider": "google"},
    "deepseek-chat": {"provider": "deepseek"},
}


def create_llm(model_name: str) -> BaseChatModel:
    """
    Create an LLM instance for the given model name.
    Args:
        model_name: (str) Name of the model to create
    Returns:
        (BaseChatModel) An LLM instance
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Model '{model_name}' is not registered in MODEL_REGISTRY")

    model_cfg = MODEL_REGISTRY[model_name]
    provider = model_cfg["provider"]

    log.info(f"Using model '{model_name}' from provider '{provider}'")

    match provider:
        case "ollama":
            if ginarr_settings.LLM_USE_LOCAL:
                return init_chat_model(
                    f"ollama:{model_name}",
                    config={
                        "base_url": ginarr_settings.OLLAMA_BASE_URL,
                        "temperature": ginarr_settings.LLM_TEMPERATURE,
                    },
                )
            else:
                raise ValueError("Remote (non-local) usage of Ollama models is not supported")
        case "openai":
            return init_chat_model(
                f"openai:{model_name}",
                temperature=ginarr_settings.LLM_TEMPERATURE,
                openai_api_key=ginarr_settings.OPENAI_API_KEY,
            )
        case "google":
            return init_chat_model(
                f"google:{model_name}",
                temperature=ginarr_settings.LLM_TEMPERATURE,
                google_api_key=ginarr_settings.GOOGLE_API_KEY,
            )
        case "deepseek":
            return init_chat_model(
                f"openai:{model_name}",
                temperature=ginarr_settings.LLM_TEMPERATURE,
                openai_api_key=ginarr_settings.DEEPSEEK_API_KEY,
                base_url=ginarr_settings.DEEPSEEK_BASE_URL,
            )
        case _:
            raise ValueError(f"Unsupported model provider: {provider}")


router_selector_llm = create_llm(ginarr_settings.LLM_MODEL)
chat_llm = create_llm(ginarr_settings.LLM_MODEL)
