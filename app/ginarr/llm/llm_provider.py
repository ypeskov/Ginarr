from typing import Literal
from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel

from app.core.logger.app_logger import log
from app.ginarr.settings import settings as ginarr_settings

type ModelProvider = Literal["ollama", "openai", "google", "deepseek"]


def create_llm(model_name: str) -> BaseChatModel:
    """
    Create an LLM instance for the given model name.
    Args:
        model_name: (str) Name of the model to create
    Returns:
        BaseChatModel: An LLM instance
    """
    try:
        log.info(f"Initializing LLM with model: '{model_name}'")

        provider = model_name.split(":")[0]

        provider_api_keys = {
            "openai": ginarr_settings.OPENAI_API_KEY,
            "google": ginarr_settings.GOOGLE_API_KEY,
            "deepseek": ginarr_settings.DEEPSEEK_API_KEY,
        }

        kwargs = {
            "temperature": ginarr_settings.LLM_TEMPERATURE,
            "api_key": provider_api_keys.get(provider),
        }

        if provider == "ollama":
            kwargs["base_url"] = ginarr_settings.OLLAMA_BASE_URL

        return init_chat_model(model_name, **kwargs)

    except Exception as e:
        log.error(f"Failed to initialize model '{model_name}': {e}")
        raise ValueError(f"Could not create LLM for '{model_name}'") from e

chat_llm = create_llm(ginarr_settings.LLM_MODEL)
