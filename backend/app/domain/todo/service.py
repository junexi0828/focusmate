from typing import Sequence
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo.models import Todo
from app.domain.todo.schemas import TodoCreate, TodoUpdate
from app.infrastructure.repositories.todo_repository import TodoRepository

class TodoService:
    def __init__(self, db: AsyncSession):
        self.todo_repo = TodoRepository(db)

    async def create_todo(self, user_id: str, todo_data: TodoCreate) -> Todo:
        return await self.todo_repo.create(todo_data, user_id)

    async def get_todos(self, user_id: str, period: str | None = None) -> Sequence[Todo]:
        return await self.todo_repo.get_by_user_id(user_id, period)

    async def update_todo(self, todo_id: int, user_id: str, todo_update: TodoUpdate) -> Todo:
        todo = await self.todo_repo.update(todo_id, user_id, todo_update)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo

    async def delete_todo(self, todo_id: int, user_id: str) -> None:
        deleted = await self.todo_repo.delete(todo_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Todo not found")
