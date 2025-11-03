from pydantic import BaseModel, ConfigDict
from typing import Optional


class TodoBase(BaseModel):
    """共通: Todoの基本情報"""
    title: str


class TodoCreate(TodoBase):
    """Todo作成リクエスト"""
    pass


class TodoUpdate(BaseModel):
    """Todo更新リクエスト"""
    title: Optional[str] = None
    completed: Optional[bool] = None


class TodoOut(TodoBase):
    """レスポンス: 単一Todo"""
    id: int
    owner_id: int
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class TodoResponse(BaseModel):
    """レスポンス: 複数TodoやAPI統一レスポンスに拡張可能"""
    todos: list[TodoOut]