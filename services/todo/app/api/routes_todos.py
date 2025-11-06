from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.todo import Todo
from ..schemas.todo import TodoCreate, TodoOut, TodoUpdate, TodoResponse
from ..core.security import get_current_user_id

router = APIRouter()


@router.get("", response_model=List[TodoOut])
def list_my_todos(
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    rows = db.query(Todo).filter(Todo.owner_id == user_id).order_by(Todo.id).all()
    return rows


@router.post("", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    row = Todo(owner_id=user_id, title=payload.title, completed=False)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{todo_id}", response_model=TodoOut)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    row = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user_id).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )
    if payload.title is not None:
        row.title = payload.title
    if payload.completed is not None:
        row.completed = payload.completed
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    row = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user_id).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )
    db.delete(row)
    db.commit()
    return None
