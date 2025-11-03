import pytest
from fastapi.testclient import TestClient
from gateway.app.main import app
from gateway.app.graphql.schema import Todo

@pytest.mark.asyncio
async def test_todos_query(monkeypatch):
    """
    GraphQLの `/graphql` エンドポイントが
    RESTの /todos サービスを経由して正しいJSONを返すことを確認する。
    """

    # --- モックレスポンスを用意 ---
    async def fake_get(url, *args, **kwargs):
        class FakeResponse:
            def raise_for_status(self): pass
            def json(self):
                return [
                    Todo(id=1, title="Write tests", done=False),
                    Todo(id=2, title="Refactor proxy", done=True),
                ]
        return FakeResponse()

    # httpx.AsyncClient.get をモック
    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    client = TestClient(app)

    # --- GraphQLクエリ ---
    query = {
        "query": """
        {
            todos {
                id
                title
                done
            }
        }
        """
    }

    # --- 実行 ---
    res = client.post("/graphql", json=query)
    assert res.status_code == 200

    data = res.json()["data"]
    todos = data["todos"]

    # --- 検証 ---
    assert len(todos) == 2
    assert todos[0]["title"] == "Write tests"
    assert todos[1]["done"] is True