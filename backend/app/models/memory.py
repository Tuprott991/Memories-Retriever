"""
Memory Database Model
Stores metadata about memories (photos, videos, voice notes)
Actual media is stored in GCS
"""

from sqlalchemy import Column, String, Text, DateTime, Float, JSON, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.database import Base


class MemoryType(str, enum.Enum):
    """Memory type enumeration"""
    PHOTO = "photo"
    VIDEO = "video"
    VOICE = "voice"
    NOTE = "note"


class Memory(Base):
    """Memory model - stores metadata for memories"""
    __tablename__ = "memories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Memory metadata
    type = Column(Enum(MemoryType), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Media storage (GCS paths)
    media_url = Column(String(1000), nullable=True)  # GCS URL
    thumbnail_url = Column(String(1000), nullable=True)  # Thumbnail for videos
    
    # Note content (for text-only memories)
    note_content = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=True)  # When the memory occurred
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Embeddings for retrieval
    embedding = Column(ARRAY(Float), nullable=True)  # Vector embedding
    embedding_model = Column(String(100), nullable=True)  # Model used for embedding
    
    # LongMatrix late interaction vectors
    query_vectors = Column(JSON, nullable=True)  # Top-k query token vectors
    doc_vectors = Column(JSON, nullable=True)  # Top-k document token vectors
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional metadata (location, weather, etc.)
    tags = Column(ARRAY(String), nullable=True, default=[])  # User tags
    
    # Face detection
    has_faces = Column(String(50), default=False)  # Whether faces were detected
    
    # Relationships
    faces = relationship("Face", back_populates="memory", cascade="all, delete-orphan")
    user = relationship("User", back_populates="memories")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_memory_user_created", "user_id", "created_at"),
        Index("idx_memory_type_user", "type", "user_id"),
        Index("idx_memory_timestamp", "timestamp"),
    )
    
    def __repr__(self):
        return f"<Memory(id={self.id}, type={self.type}, title={self.title[:30]})>"
