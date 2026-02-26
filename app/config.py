"""Application configuration loaded from environment variables via Pydantic Settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All application settings derived from environment variables (or .env file)."""

    # Odoo 16 connection
    odoo_url: str = Field("http://localhost:8069", description="Odoo instance base URL")
    odoo_db: str = Field("odoo", description="Odoo database name")
    odoo_user: str = Field("admin@example.com", description="Odoo login e-mail")
    odoo_api_key: str = Field("", description="Odoo API Key")
    odoo_password: str = Field("", description="Odoo user password (optional fallback for web auth)")
    odoo_version: int = Field(16, description="Odoo major version number")

    # LLM (OpenAI)
    openai_api_key: str = Field("", description="OpenAI API key")
    supervisor_model: str = Field("gpt-4o", description="LLM model for Supervisor Agent")
    kb_agent_model: str = Field("gpt-4o-mini", description="LLM model for KB Agent")
    workflow_agent_model: str = Field("gpt-4o", description="LLM model for Workflow Agent")
    odoo_api_agent_model: str = Field("gpt-4o-mini", description="LLM model for Odoo API Agent")

    # Storage
    database_url: str = Field(
        "sqlite:///./storage/sessions.db", description="SQLAlchemy database URL"
    )
    chroma_persist_dir: str = Field(
        "./storage/chroma_db", description="ChromaDB persistence directory"
    )
    chroma_collection: str = Field("odoo_crm_kb", description="ChromaDB collection name")

    # Application
    app_env: str = Field("development", description="Application environment")
    log_level: str = Field("INFO", description="Log level")
    webhook_secret: str = Field("change_me_in_production", description="Webhook HMAC secret")

    @property
    def odoo_version_int(self) -> int:
        """Return the Odoo major version as an integer."""
        return int(self.odoo_version)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()


settings = get_settings()
