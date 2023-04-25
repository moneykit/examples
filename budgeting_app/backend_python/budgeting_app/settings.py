import functools

import pydantic


class Settings(pydantic.BaseSettings):
    base_url: str = "http://localhost:8000"
    database_echo_sql: bool = False
    database_url: pydantic.SecretStr
    log_level: str = "INFO"
    moneykit_url: str
    moneykit_client_id: str
    moneykit_client_secret: pydantic.SecretStr

    class Config:
        case_sensitive = False


@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()
