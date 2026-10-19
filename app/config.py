from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NairaHash"
    environment: str = "production"
    secret_key: str = "CHANGE_ME_IN_ENV"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nairhash"
    frontend_url: str = "https://nairhash.com"
    app_url: str = "https://nairhash.com"
    admin_email: str = "admin@nairhash.com"
    admin_password: str = "Admin@NairaHash123"
    btc_reference_currency: str = "NGN"
    enable_background_tasks: bool = True
    schedule_interval_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
