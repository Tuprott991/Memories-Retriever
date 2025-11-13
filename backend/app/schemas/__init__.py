"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class MemoryType(str, Enum):
    """Memory type enum"""
    PHOTO = "photo"
    VIDEO = "video"
    VOICE = "voice"
    NOTE = "note"


# ===== Memory Schemas =====

class FaceCreate(BaseModel):
    """Schema for creating face annotation"""
    x: float = Field(..., ge=0, le=1, description="X coordinate (normalized 0-1)")
    y: float = Field(..., ge=0, le=1, description="Y coordinate (normalized 0-1)")
    width: float = Field(..., ge=0, le=1, description="Width (normalized 0-1)")
    height: float = Field(..., ge=0, le=1, description="Height (normalized 0-1)")
    name: Optional[str] = Field(None, max_length=200, description="Person's name")
    description: Optional[str] = Field(None, max_length=1000, description="Description")


class FaceResponse(FaceCreate):
    """Schema for face response"""
    id: str
    memory_id: str


class MemoryCreate(BaseModel):
    """Schema for creating memory"""
    type: MemoryType
    title: str = Field(..., max_length=500, min_length=1)
    description: Optional[str] = None
    note_content: Optional[str] = None
    timestamp: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    faces: Optional[List[FaceCreate]] = Field(default_factory=list)


class MemoryUpdate(BaseModel):
    """Schema for updating memory"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    note_content: Optional[str] = None
    timestamp: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    """Schema for memory response"""
    id: str
    user_id: str
    type: MemoryType
    title: str
    description: Optional[str]
    media_url: Optional[str]
    thumbnail_url: Optional[str]
    note_content: Optional[str]
    timestamp: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    metadata: Optional[Dict[str, Any]]
    has_faces: bool
    faces: List[FaceResponse] = []
    
    class Config:
        from_attributes = True


class MemorySearchRequest(BaseModel):
    """Schema for memory search request"""
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = None


class MemorySearchResponse(BaseModel):
    """Schema for memory search response"""
    memories: List[MemoryResponse]
    total: int
    query: str
    reasoning: Optional[str] = None


# ===== User Schemas =====

class UserCreate(BaseModel):
    """Schema for creating user"""
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    description: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== Chat Schemas =====

class ChatMessage(BaseModel):
    """Schema for chat message"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    include_reasoning: bool = Field(default=True)


class ChatResponseChunk(BaseModel):
    """Schema for streaming chat response chunk"""
    type: str = Field(..., description="Type: text, reasoning, function_result, memories, error")
    content: Optional[str] = None
    memories: Optional[List[MemoryResponse]] = None
    function: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Schema for conversation session response"""
    id: str
    user_id: str
    title: Optional[str]
    summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== Upload Schemas =====

class UploadResponse(BaseModel):
    """Schema for upload response"""
    memory_id: str
    media_url: str
    thumbnail_url: Optional[str] = None
    message: str


class BulkUploadResponse(BaseModel):
    """Schema for bulk upload response"""
    successful: List[UploadResponse]
    failed: List[Dict[str, str]]
    total: int
    success_count: int
    failure_count: int


# ===== Error Schemas =====

class ErrorResponse(BaseModel):
    """Schema for error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ===== Health Check =====

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Optional[Dict[str, str]] = None
