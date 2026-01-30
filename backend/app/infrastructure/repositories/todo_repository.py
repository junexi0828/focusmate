from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo.models import Todo
from app.domain.todo.schemas import TodoCreate, TodoUpdate

class TodoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, todo_create: TodoCreate, user_id: str) -> Todo:
        todo = Todo(
            user_id=user_id,
            content=todo_create.content,
            period=todo_create.period,
            is_completed=todo_create.is_completed,
        )
        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def get_by_user_id(self, user_id: str, period: str | None = None) -> Sequence[Todo]:
        query = select(Todo).where(Todo.user_id == user_id)

        if period:
            query = query.where(Todo.period == period)

        query = query.order_by(Todo.created_at.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, todo_id: int, user_id: str) -> Todo | None:
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update(self, todo_id: int, user_id: str, todo_update: TodoUpdate) -> Todo | None:
        todo = await self.get_by_id(todo_id, user_id)
        if not todo:
            return None

        update_data = todo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)

        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def delete(self, todo_id: int, user_id: str) -> bool:
        todo = await self.get_by_id(todo_id, user_id)
        if not todo:
            return False

        await self.session.delete(todo)
        await self.session.commit()
        return True
