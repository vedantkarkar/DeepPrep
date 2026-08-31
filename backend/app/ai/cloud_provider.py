import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.ai.base import AIProvider, AIProviderError
from app.config import settings

T = TypeVar("T", bound=BaseModel)

class CloudAIProvider(AIProvider):
    """Cloud AI Provider supporting Google Gemini and OpenAI compatible APIs."""

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    async def extract_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        if not self.gemini_key and not self.openai_key:
            raise AIProviderError("No cloud API keys configured (GEMINI_API_KEY or OPENAI_API_KEY).")

        json_schema = schema.model_json_schema()
        
        if self.gemini_key:
            return await self._call_gemini_structured(prompt, schema, json_schema, system_instruction)
        else:
            return await self._call_openai_structured(prompt, schema, json_schema, system_instruction)

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        if not self.gemini_key and not self.openai_key:
            raise AIProviderError("No cloud API keys configured.")
        return "Cloud AI generated text response."

    async def _call_gemini_structured(self, prompt: str, schema: Type[T], json_schema: dict, system_inst: Optional[str]) -> T:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "response_schema": json_schema,
            }
        }
        if system_inst:
            payload["systemInstruction"] = {"parts": [{"text": system_inst}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise AIProviderError(f"Gemini API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            raw_json_str = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_data = json.loads(raw_json_str)
            return schema(**parsed_data)

    async def _call_openai_structured(self, prompt: str, schema: Type[T], json_schema: dict, system_inst: Optional[str]) -> T:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        messages = []
        if system_inst:
            messages.append({"role": "system", "content": system_inst})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise AIProviderError(f"OpenAI API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            raw_json_str = data["choices"][0]["message"]["content"]
            parsed_data = json.loads(raw_json_str)
            return schema(**parsed_data)
