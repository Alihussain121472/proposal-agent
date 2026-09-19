"""
Configuration for the Freelance Proposal Strategist Agent.
Supports environment variables and manual configuration.
"""

import os
from typing import Optional
from pydantic import BaseModel

class AgentConfig(BaseModel):
    # LLM Provider: 'gemini', 'openai', 'groq', 'ollama', or 'offline'
    default_provider: str = "offline"
    
    # API Keys (loaded from env or UI)
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Model names
    gemini_model: str = "gemini-2.5-flash"
    openai_model: str = "gpt-4o-mini"
    groq_model: str = "llama-3.3-70b-versatile"
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434/v1"

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000

def get_config() -> AgentConfig:
    """Load configuration from environment variables with defaults."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # Determine default provider based on available keys
    if gemini_key:
        default_provider = "gemini"
    elif groq_key:
        default_provider = "groq"
    elif openai_key:
        default_provider = "openai"
    else:
        default_provider = "offline"

    return AgentConfig(
        default_provider=default_provider,
        gemini_api_key=gemini_key,
        openai_api_key=openai_key,
        groq_api_key=groq_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )
