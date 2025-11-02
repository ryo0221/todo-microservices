from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://todo_user:todo_pass@postgres:5432/todo_db"
    JWT_SECRET: str = "please_change_me"
    JWT_ALGORITHM: str = "HS256"

   # 任意: あってもなくても動くようにしておく
    AUTH_JWKS_URL: str | None = None
    UVICORN_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",           # ← これで未定義の環境変数を無視
    )

settings = Settings()