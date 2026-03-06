"""Configurações centralizadas do Agent."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações do Agent."""

    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Modelos
    default_model: str = "gpt-4"
    fallback_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"

    # RAG
    vector_store_path: Path = Path("data/vector_store")
    psychology_guides_path: Path = Path("data/psychology_guides")
    top_k_retrieval: int = 3

    # Intent Analysis Thresholds
    intent_threshold_medium: float = 0.4
    intent_threshold_high: float = 0.7
    intent_threshold_critical: float = 0.9

    # Routing
    auto_route_on_critical: bool = True
    routing_keywords: list[str] = [
        "suicídio",
        "me matar",
        "quero morrer",
        "acabar com tudo",
        "não aguento mais",
    ]

    # Validation
    validation_policy_path: Path = Path("src/compliance/validation_policy.yaml")

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json ou text

    # Performance
    max_tokens: int = 500
    temperature: float = 0.7
    timeout_seconds: int = 30

    # Segurança
    enable_sanitization: bool = True
    enable_judge: bool = True
    max_message_length: int = 2000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton
settings = Settings()
