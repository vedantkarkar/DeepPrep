from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class AIProviderError(Exception):
    """Base exception for AI provider operations."""
    pass

class AIProvider(ABC):
    """Abstract interface for all AI model providers (Mock, Cloud, Local)."""

    @abstractmethod
    async def extract_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Extracts structured data strictly conforming to a Pydantic schema."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generates natural language response text."""
        pass
