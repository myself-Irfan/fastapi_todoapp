from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    """Base taskapp schema with common fields."""
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=200, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    is_complete: bool = Field(False, description="Whether the taskapp is completed")


class TaskCreate(TaskBase):
    """Schema for creating a new taskapp."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing taskapp."""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=200, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    is_complete: Optional[bool] = Field(None, description="Whether the taskapp is completed")


class TaskRead(TaskBase):
    """Schema for reading a taskapp from the database."""
    id: int = Field(..., gt=0, description="Task ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Task last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel):
    """API response wrapper."""
    message: str = Field(..., description="Response message")
    # data: Optional[Any] = Field(None, description="Response data")

    model_config = ConfigDict(from_attributes=True)


# Specific response schemas for better type safety
class TaskListResponse(ApiResponse):
    """Response schema for taskapp list endpoints."""
    data: Optional[List[TaskRead]] = None


class TaskResponse(ApiResponse):
    """Response schema for single taskapp endpoints."""
    data: Optional[TaskRead] = None