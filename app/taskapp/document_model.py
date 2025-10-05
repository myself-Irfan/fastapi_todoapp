from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Collection title")
    description: Optional[str] = Field(None, max_length=200, description="Collection description")


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Collection title")
    description: Optional[str] = Field(None, max_length=200, description="Collection description")


class DocumentRead(DocumentBase):
    id: int = Field(..., gt=0, description="Collection ID")
    created_at: datetime = Field(..., description="Collection creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Collection last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel):
    """API response wrapper."""
    message: str = Field(..., description="Response message")

    model_config = ConfigDict(from_attributes=True)


# Specific response schemas for better type safety
class DocumentListResponse(ApiResponse):
    """Response schema for taskapp list endpoints."""
    data: Optional[List[DocumentRead]] = None


class DocumentResponse(ApiResponse):
    """Response schema for single taskapp endpoints."""
    data: Optional[DocumentRead] = None