"""
Conversation Session Database Model
Stores chat sessions with the memory retrieval agent
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


class ConversationSession(Base):
    """Conversation session model"""
    __tablename__ = "conversation_sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session metadata
    title = Column(String(500), nullable=True)  # Session title (generated from first query)
    summary = Column(Text, nullable=True)  # Session summary
    
    # ZEP session ID
    zep_session_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Session context (for maintaining conversation state)
    context = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<ConversationSession(id={self.id}, user_id={self.user_id}, title={self.title})>"
