from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(default="", alias="BOT_TOKEN")
    lms_api_base_url: str = Field(default="http://10.93.26.102:42002", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field(default="", alias="LMS_API_KEY")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_api_base_url: str = Field(default="", alias="LLM_API_BASE_URL")
    llm_api_model: str = Field(default="coder-model", alias="LLM_API_MODEL")

    model_config = SettingsConfigDict(
        env_file="../.env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )
