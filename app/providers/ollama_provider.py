from typing import TypeVar, Type

from ollama import Client
from pydantic import BaseModel

from app.config import settings
from app.providers.base import LLMProvider


T = TypeVar("T", bound=BaseModel)


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self.client = Client(host=settings.ollama_host)
        self.model = settings.ollama_model

    def structured_call(
        self,
        *,
        system: str,
        user: str,
        schema: Type[T],
    ) -> T:
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Ollama supports a JSON Schema here.
            format=schema.model_json_schema(),
            stream=False,
            options={
                # Low temperature is useful for routing and tool planning.
                "temperature": 0,
            },
        )

        content = response.message.content
        if not content:
            raise RuntimeError("Ollama returned an empty structured response.")

        # Do not trust the model merely because JSON was requested.
        # Pydantic validates the returned payload again in application code.
        return schema.model_validate_json(content)

    def text_call(
        self,
        *,
        system: str,
        user: str,
    ) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=False,
            options={
                "temperature": 0.2,
            },
        )

        content = response.message.content
        if not content:
            raise RuntimeError("Ollama returned an empty text response.")

        return content.strip()
