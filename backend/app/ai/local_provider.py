import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.ai.base import AIProvider, AIProviderError
from app.config import settings

T = TypeVar("T", bound=BaseModel)

class LocalModelProvider(AIProvider):
    """Local AI model provider utilizing Ollama endpoint."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")

    async def extract_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        if system_instruction:
            payload["system"] = system_instruction

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    raise AIProviderError(f"Ollama local model error ({resp.status_code}): {resp.text}")
                data = resp.json()
                raw_response = data.get("response", "{}")
                parsed_json = json.loads(raw_response)
                return schema(**parsed_json)
        except httpx.ConnectError as e:
            raise AIProviderError(
                f"Could not connect to local Ollama server at {self.base_url}. Ensure Ollama is running."
            ) from e
        except Exception as e:
            raise AIProviderError(f"Local model extraction failed: {str(e)}") from e

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        return "Local model generated response text."
