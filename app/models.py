from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, Date
from app.database import Base


class Task(Base):
    __tablename__ = 'todo_tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', is_complete={self.is_complete})>"