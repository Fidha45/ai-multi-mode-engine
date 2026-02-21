import os


AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()

# OpenAI settings
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"

# Web auth settings
WEB_AUTH_ENABLED = os.getenv("WEB_AUTH_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
WEB_USERNAME = os.getenv("WEB_USERNAME", "admin")
WEB_PASSWORD = os.getenv("WEB_PASSWORD", "admin123")
WEB_SECRET_KEY = os.getenv("WEB_SECRET_KEY", "change-this-secret-key")