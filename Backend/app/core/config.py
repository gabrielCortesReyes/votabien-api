# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # Pydantic v2: configura .env, insensibilidad a mayúsculas y que ignore extras
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    db_url: str = Field(default="sqlite:///./dev.db", alias="DB_URL")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    # 👇 Campo en minúscula, pero leyendo del env USE_MOCK
    use_mock: bool = Field(default=True, alias="USE_MOCK")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

settings = Settings()

