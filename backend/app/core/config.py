from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Project Manager"
    DEBUG: bool = False

    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.2

    # Jira
    JIRA_URL: str = ""
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""

    # GitHub
    GITHUB_TOKEN: str = ""

    # Microsoft Teams (Graph API)
    TEAMS_ACCESS_TOKEN: str = ""
    TEAMS_TEAM_ID: str = ""

    # LangSmith Observability
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://apac.api.smith.langchain.com"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "ai-project-manager"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": False,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
