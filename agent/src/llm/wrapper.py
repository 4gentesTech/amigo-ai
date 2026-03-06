"""Factory de modelos LLM."""

from typing import Literal

from langchain_openai import ChatOpenAI

from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)


class LLMFactory:
    """Factory para criar instâncias de LLM."""

    @staticmethod
    def create(
        provider: Literal["openai", "groq", "llama"] = "openai",
        model: str | None = None,
        temperature: float | None = None,
    ) -> ChatOpenAI:
        """Cria instância de LLM baseado no provider."""

        model_name = model or settings.default_model
        temp = temperature if temperature is not None else settings.temperature

        if provider == "openai":
            logger.info("Criando LLM OpenAI", model=model_name)
            return ChatOpenAI(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                timeout=settings.timeout_seconds,
                api_key=settings.openai_api_key,
            )

        elif provider == "groq":
            logger.info("Criando LLM Groq", model=model_name)
            # Groq usa a mesma interface do OpenAI
            return ChatOpenAI(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                timeout=settings.timeout_seconds,
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
            )

        elif provider == "llama":
            logger.info("Criando LLM Llama local", model=model_name)
            # Para Llama local via Ollama
            return ChatOpenAI(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # Ollama não requer key
            )

        else:
            raise ValueError(f"Provider não suportado: {provider}")

    @staticmethod
    def create_with_fallback() -> ChatOpenAI:
        """Cria LLM com fallback automático."""
        try:
            return LLMFactory.create("openai", settings.default_model)
        except Exception as e:
            logger.warning(
                "Falha ao criar modelo principal, usando fallback",
                error=str(type(e).__name__),
            )
            return LLMFactory.create("openai", settings.fallback_model)
