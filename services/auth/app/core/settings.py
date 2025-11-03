import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://auth_user:auth_pass@postgres:5432/auth_db"
    JWT_SECRET: str = "please_change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTH_JWKS_URL: str | None = None
    UVICORN_PORT: int = 8000

    # CI / テスト用
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # 未定義の環境変数を無視
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        DATABASE_URL が明示されていればそれを使い、
        TESTING=true のときは SQLite にフォールバック。
        """
        if self.TESTING:
            return "sqlite:///./test.db"
        return self.DATABASE_URL


settings = Settings()