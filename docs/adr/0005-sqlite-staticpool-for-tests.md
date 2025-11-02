# ADR-0005: Use SQLite + StaticPool for Fast, Reliable Tests

- **Status**: Draft
- **Date**: 2025-11-02
- **Deciders**: Project Owner RT
- **Supersedes**: -
- **Superseded by**: -

## Context

ユニット／機能テストを高速に回すため、本番の Postgres を立ち上げず**軽量なSQLite**で代替したい。`:memory:` は高速だが接続ごとに別DBとなるため共有の工夫が必要。一方、**一時ファイルSQLite**であれば接続を跨いでも同じDBにアクセスでき、FastAPI の TestClient が内部で張る別スレッドの接続とも整合する。

## Decision

テストでは **一時ファイルSQLite** を採用する。セッション全体で1つの一時DBファイルを生成し、テスト完了時に削除する。

```python
# conftest.py（抜粋）
import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.models.user import Base  # or Base of your models

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

# FastAPI の依存をテスト用セッションに差し替える
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
```

> メモ: `check_same_thread=False` は TestClient 等の並行実行で必要。

## Consequences

### Positive

* **安定**：接続を跨いでも同一DBファイルを参照できる
* **高速**：外部DB不要でTDDの反復が速い
* **シンプル**：`:memory:`の共有やプール設定を意識せずに済む

### Negative / Trade-offs

* **ファイルI/O** が発生（多くのケースで十分高速だが、`:memory:`よりは遅い）
* **方言差**：SQLite と Postgres の挙動差（制約、トランザクション分離、`RETURNING`、JSON、FK厳格性）に注意

## Alternatives Considered

* **A. `:memory:` + StaticPool**
  *Pros*: 最高速／完全メモリ、`no such table` を防げる
  *Cons*: プール設定や共有の理解が必要、デバッグ時にファイルが残らない
* **B. Docker Postgres をテストで起動**
  *Pros*: 本番に近い再現性
  *Cons*: 起動・初期化が重く、反復速度が落ちる
* **C. Testcontainers (Postgres)**
  *Pros*: 実DBで高い再現性、テストごとに隔離
  *Cons*: セットアップ／CIチューニングが重い

## Implementation Notes

* `Base.metadata.create_all()` は `scope="session"` で一度だけ実行
* もしスキーマ再作成が必要なテストがある場合は、対象テスト内で `drop_all → create_all` を実行（※本番コードには入れない）
* E2E/CI では **Postgres での統合テスト**も別途用意して差異を吸収
* 将来的に速度をさらに上げたい場合は、`:memory:` + `StaticPool` へ切替も検討

## Links

* ADR: Adopt TDD for Microservices
* ADR: Local Dev with Docker Compose Override & Hot Reload
* ADR: Split Services into Auth and Todo (with API Gateway)
