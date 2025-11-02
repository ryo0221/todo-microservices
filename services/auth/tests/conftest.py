import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# App pieces
from app.main import app
from app.db.session import get_db
from app.models.user import Base


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
    # Create tables once per test session
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
    # Override FastAPI dependency to use our test session
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
    # Provide a fresh TestClient per test function
    with TestClient(app) as c:
        yield c

