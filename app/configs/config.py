import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Cargar el archivo .env desde la raíz del proyecto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class Database(BaseSettings):
    class Posgres_Backoffice:
        db_hostname: str = os.getenv("PGSQL_HOSTNAME", "localhost")
        db_password: str = os.getenv("PGSQL_PASSWORD", "postgres_password")
        db_username: str = os.getenv("PGSQL_USERNAME", "postgres")
        db_port = os.getenv("PGSQL_PORT", "5432")
        db_name: str = os.getenv("PGSQL_DBNAME", "vota_bien")

    class Config:
        env_file = ".env"
        extra = "ignore"


database = Database()
db_port_pgsql = (
    database.Posgres_Backoffice.db_port
    if database.Posgres_Backoffice.db_port
    else "5432"
)

connection_string_pgsql = f"postgresql://{database.Posgres_Backoffice.db_username}:{database.Posgres_Backoffice.db_password}@{database.Posgres_Backoffice.db_hostname}:{db_port_pgsql}/{database.Posgres_Backoffice.db_name}"