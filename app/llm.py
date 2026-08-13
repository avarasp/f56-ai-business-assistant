from typing import TypeVar, Type

from pydantic import BaseModel

from app.config import settings
from app.providers.base import LLMProvider
from app.providers.ollama_provider import OllamaProvider


T = TypeVar("T", bound=BaseModel)


def _build_provider() -> LLMProvider:
    provider = settings.llm_provider.strip().lower()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER={settings.llm_provider!r}. "
        "Currently supported: ollama"
    )


_provider = _build_provider()


def structured_call(
    *,
    system: str,
    user: str,
    schema: Type[T],
) -> T:
    return _provider.structured_call(
        system=system,
        user=user,
        schema=schema,
    )


def text_call(
    *,
    system: str,
    user: str,
) -> str:
    return _provider.text_call(
        system=system,
        user=user,
    )
