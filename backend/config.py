from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str
    database_url: str
    use_ollama: bool = True
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434"


    smtp_email: str
    smtp_password: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    admin_email: str = "admin@gmail.com"
    admin_password: str = "admin3967"

    jwt_secret: str = "change_this_secret_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    upload_dir: str = "uploads"


try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    # Fallback or re-raise with more info if needed
    raise e
