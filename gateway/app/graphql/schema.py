import strawberry
import httpx


@strawberry.type
class Todo:
    id: int
    title: str
    done: bool


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, GraphQL!"

    @strawberry.field
    async def todos(self) -> list[Todo]:
        """
        REST API (/todos) を叩いて Todo の一覧を返す。
        GatewayからTodoサービスのRESTエンドポイントを呼び出す。
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://todo:8000/todos")
            resp.raise_for_status()
            return resp.json()


schema = strawberry.Schema(Query)
