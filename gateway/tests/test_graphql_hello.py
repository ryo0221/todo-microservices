import pytest
from starlette.testclient import TestClient
from gateway.app.main import app


@pytest.mark.asyncio
async def test_hello_query():
    client = TestClient(app)
    query = {"query": "{ hello }"}
    res = client.post("/graphql", json=query)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["hello"] == "Hello, GraphQL!"
