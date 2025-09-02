# ============================
# SETTINGS
# ============================

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

# Carga variables desde .env en la raíz del proyecto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- DB ----------
    db_url: str = Field(default="", alias="DB_URL")

    # ---------- API/CORS ----------
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

settings = Settings()

# DB_URL, Construirla desde Variables PGSQL_
if not settings.db_url:
    PGSQL_HOSTNAME = os.getenv("PGSQL_HOSTNAME", "localhost")
    PGSQL_PORT     = os.getenv("PGSQL_PORT", "5432")
    PGSQL_USERNAME = os.getenv("PGSQL_USERNAME", "postgres")
    PGSQL_PASSWORD = os.getenv("PGSQL_PASSWORD", "postgres_password")
    PGSQL_DBNAME   = os.getenv("PGSQL_DBNAME", "vota_bien")

    settings.db_url = (
        f"postgresql://{PGSQL_USERNAME}:{PGSQL_PASSWORD}"
        f"@{PGSQL_HOSTNAME}:{PGSQL_PORT}/{PGSQL_DBNAME}"
    )