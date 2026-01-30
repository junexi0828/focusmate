from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.domain.todo.schemas import TodoCreate, TodoResponse, TodoUpdate
from app.domain.todo.service import TodoService
from app.infrastructure.database.models import User

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_in: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    return await service.create_todo(current_user.id, todo_in)

@router.get("", response_model=List[TodoResponse])
async def get_todos(
    period: Optional[str] = Query(None, description="Filter by period (daily, weekly, monthly)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    return await service.get_todos(current_user.id, period)

@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    return await service.update_todo(todo_id, current_user.id, todo_update)

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TodoService(db)
    await service.delete_todo(todo_id, current_user.id)
