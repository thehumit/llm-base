from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl

class Settings(BaseSettings):
    model_name: str
    api_key: str
    litellm_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # optionally set a prefix for env vars if you like:
        # env_prefix="LLM_"
    )

settings = Settings()
