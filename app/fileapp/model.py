from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.taskapp.document_model import ApiResponse


class FileBase(BaseModel):
    title: str = Field(...,  min_length=1, max_length=100, description="File title")

class FileCreate(FileBase):
    document_id: int = Field(..., description="Document associated with file")

class FileUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    document_id: Optional[int] = Field(None, description="move file to this document (null for standalone)")

    model_config = ConfigDict(extra="forbid")

class FileRead(FileBase):
    id: int
    is_active: bool
    file_path: str
    file_size: int
    mime_type: str
    extension: str
    checksum: Optional[str]
    created_at: datetime
    updated_at: datetime
    document_id: Optional[int]
    user_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class FileReadResponse(ApiResponse):
    data: Optional[FileRead] = None

class FileListResponse(BaseModel):
    message: str
    data: list[FileRead]