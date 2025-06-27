import importlib

from app.core.logger.app_logger import log

_PROMPTS = {}


def load_prompts(locale: str) -> dict:
    try:
        module_path = f"app.core.i18n.locales.{locale}.prompts"
        mod = importlib.import_module(module_path)
        return mod.PROMPTS
    except Exception:
        log.error(f"Error loading prompts for locale: {locale}", exc_info=True)
        fallback_mod = importlib.import_module("app.core.i18n.locales.en_US.prompts")
        return fallback_mod.PROMPTS


def get_prompt(key: str, locale: str = "ru_UA") -> str:
    if locale not in _PROMPTS:
        _PROMPTS[locale] = load_prompts(locale)
    template = _PROMPTS[locale].get(key)
    if template is None:
        raise KeyError(f"Prompt '{key}' not found in locale [{locale}]")
    return template
