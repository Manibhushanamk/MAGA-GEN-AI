from abc import ABC, abstractmethod
from typing import Dict, Optional

class BaseLLMService(ABC):
    @abstractmethod
    def generate_summary(self, project_data: Dict) -> str:
        pass

class LLMFactory:
    @staticmethod
    def get_service(provider: str, api_key: str):
        if provider.lower() == "gemini":
            from backend.gemini_service import GeminiService
            return GeminiService(api_key)
        elif provider.lower() == "groq":
            from backend.groq_service import GroqService
            return GroqService(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
