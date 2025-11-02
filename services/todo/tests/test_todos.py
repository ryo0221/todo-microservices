from typing import Dict

from fastapi import status


def _auth_header(user_id: int) -> Dict[str, str]:
    from tests.conftest import make_token
    return {"Authorization": f"Bearer {make_token(user_id)}"}


def test_list_requires_auth(client):
    r = client.get("/todos")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_and_list_own_todos(client):
    headers = _auth_header(1)

    # create
    r1 = client.post("/todos", json={"title": "write tests"}, headers=headers)
    assert r1.status_code == status.HTTP_201_CREATED
    todo = r1.json()
    assert todo["title"] == "write tests"
    assert todo["completed"] is False

    # list
    r2 = client.get("/todos", headers=headers)
    assert r2.status_code == 200
    items = r2.json()
    assert len(items) == 1
    assert items[0]["title"] == "write tests"


def test_user_cannot_see_others_todos(client):
    # user 1 creates
    client.post("/todos", json={"title": "secret"}, headers=_auth_header(1))

    # user 2 lists
    r = client.get("/todos", headers=_auth_header(2))
    assert r.status_code == 200
    assert r.json() == []


def test_update_and_delete(client):
    headers = _auth_header(1)
    created = client.post("/todos", json={"title": "rename me"}, headers=headers).json()
    tid = created["id"]

    # update title and complete
    r_up = client.patch(f"/todos/{tid}", json={"title": "renamed", "completed": True}, headers=headers)
    assert r_up.status_code == 200
    updated = r_up.json()
    assert updated["title"] == "renamed"
    assert updated["completed"] is True

    # delete
    r_del = client.delete(f"/todos/{tid}", headers=headers)
    assert r_del.status_code == 204

    # ensure gone
    r_list = client.get("/todos", headers=headers)
    assert all(item["id"] != tid for item in r_list.json())
