from app.config import settings
from app.ai.base import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.cloud_provider import CloudAIProvider
from app.ai.local_provider import LocalModelProvider

def get_ai_provider() -> AIProvider:
    """Factory creating configured AIProvider instance."""
    provider_type = (settings.AI_PROVIDER or "mock").lower().strip()
    if provider_type == "cloud":
        return CloudAIProvider()
    elif provider_type == "local":
        return LocalModelProvider()
    else:
        return MockAIProvider()
