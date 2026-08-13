from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "ollama"
    ollama_model: str = "qwen2.5:3b"
    ollama_host: str = "http://127.0.0.1:11434"

    # MySQL
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str
    mysql_user: str
    mysql_password: str = ""

    sales_table: str = "pay_event"
    products_table: str = "product"
    contacts_table: str = "contact"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
