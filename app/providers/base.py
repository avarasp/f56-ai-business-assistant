from abc import ABC, abstractmethod
from typing import TypeVar, Type

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    def structured_call(
        self,
        *,
        system: str,
        user: str,
        schema: Type[T],
    ) -> T:
        raise NotImplementedError

    @abstractmethod
    def text_call(
        self,
        *,
        system: str,
        user: str,
    ) -> str:
        raise NotImplementedError
