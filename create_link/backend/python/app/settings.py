import functools

import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    log_level: str = "INFO"
    moneykit_url: str = "https://api.moneykit.com"
    moneykit_client_id: str
    moneykit_client_secret: pydantic.SecretStr
    frontend_oauth_redirect_uri: str = "http://localhost:3000"

    class Config:
        case_sensitive = False


@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()
