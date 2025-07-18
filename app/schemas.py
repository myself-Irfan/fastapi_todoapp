from datetime import datetime, date
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


# User schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="User password")


class UserRead(UserBase):
    """Schema for reading a user from the database."""
    id: int = Field(..., gt=0, description="User ID")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="User last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None


# Task schemas
class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=200, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    is_complete: bool = Field(False, description="Whether the task is completed")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=200, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    is_complete: Optional[bool] = Field(None, description="Whether the task is completed")


class TaskRead(TaskBase):
    """Schema for reading a task from the database."""
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
    """Response schema for task list endpoints."""
    data: Optional[List[TaskRead]] = None


class TaskResponse(ApiResponse):
    """Response schema for single task endpoints."""
    data: Optional[TaskRead] = None


class UserResponse(ApiResponse):
    """Response schema for user endpoints."""
    data: Optional[UserRead] = None