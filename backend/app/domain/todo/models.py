from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.infrastructure.database.base import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    period = Column(String, default="daily")  # daily, weekly, monthly

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="todos")
