"""
Face Database Model
Stores detected faces in photos/videos
"""

from sqlalchemy import Column, String, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Face(Base):
    """Face model - stores detected faces and their annotations"""
    __tablename__ = "faces"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Memory association
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Face bounding box (normalized coordinates 0-1)
    x = Column(Float, nullable=False)  # X coordinate of top-left corner
    y = Column(Float, nullable=False)  # Y coordinate of top-left corner
    width = Column(Float, nullable=False)  # Width of bounding box
    height = Column(Float, nullable=False)  # Height of bounding box
    
    # Face annotation
    name = Column(String(200), nullable=True)  # Person's name
    description = Column(String(1000), nullable=True)  # Description/notes about person
    
    # Face recognition (optional - for future implementation)
    face_encoding = Column(String(10000), nullable=True)  # Serialized face encoding
    
    # Relationships
    memory = relationship("Memory", back_populates="faces")
    
    # Indexes
    __table_args__ = (
        Index("idx_face_memory", "memory_id"),
        Index("idx_face_name", "name"),
    )
    
    def __repr__(self):
        return f"<Face(id={self.id}, name={self.name}, memory_id={self.memory_id})>"
