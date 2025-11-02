import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import jwt

# App pieces (to be implemented)
from app.main import app
from app.db.session import get_db
from app.models.todo import Base  # will exist after implementation

JWT_SECRET = os.getenv("JWT_SECRET", "please_change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def make_token(user_id: int) -> str:
    return jwt.encode({"sub": str(user_id), "typ": "access"}, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest.fixture(scope="session")
def _test_db_url():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    url = f"sqlite:///{tmp.name}"
    yield url
    try:
        os.unlink(tmp.name)
    except FileNotFoundError:
        pass

@pytest.fixture(scope="session")
def _engine(_test_db_url):
    engine = create_engine(_test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(_engine):
    TestingSessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _override_get_db(db_session):
    def _get_db_for_tests():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db_for_tests
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
