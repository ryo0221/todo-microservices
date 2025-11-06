from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def get_engine():
    """
    Settingsを遅延ロードして、CI時にはSQLiteを使う。
    """
    from app.core.settings import settings  # ← インポートを関数内に遅延させる

    url = settings.SQLALCHEMY_DATABASE_URI
    print("Database URL:", url)
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )


engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
