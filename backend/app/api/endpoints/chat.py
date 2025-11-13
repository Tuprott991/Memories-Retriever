"""
Chat API Endpoints
Handles conversations with the memory retrieval agent
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
from loguru import logger

from app.db.database import get_db
from app.schemas import ChatRequest, ChatMessage, SessionResponse
from app.services.agent_service import VertexAIAgentService
from app.services.embedding_service import EmbeddingService
from app.services.memory_graph_service import MemoryGraphService

router = APIRouter()


def get_agent_service(request: Request) -> VertexAIAgentService:
    """Get agent service from app state"""
    embedding_service: EmbeddingService = request.app.state.embedding_service
    memory_graph_service: MemoryGraphService = request.app.state.memory_graph_service
    
    agent = VertexAIAgentService(embedding_service, memory_graph_service)
    return agent


@router.post("/", response_class=StreamingResponse)
async def chat(
    request: ChatRequest,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
    agent: VertexAIAgentService = Depends(get_agent_service)
):
    """
    Chat with the memory retrieval agent (streaming)
    
    Streams response chunks as Server-Sent Events (SSE)
    """
    if not agent.initialized:
        await agent.initialize()
    
    async def generate():
        """Generate streaming response"""
        try:
            async for chunk in agent.chat(
                user_id=user_id,
                message=request.message,
                session_id=request.session_id
            ):
                # Format as SSE
                data = json.dumps(chunk)
                yield f"data: {data}\n\n"
            
            # End of stream
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            error_chunk = {
                "type": "error",
                "content": str(e)
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    user_id: str = "default",  # TODO: Get from auth
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation sessions for user"""
    from sqlalchemy import select
    from app.models import ConversationSession
    
    query = select(ConversationSession).where(
        ConversationSession.user_id == user_id
    ).order_by(
        ConversationSession.updated_at.desc()
    ).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Get specific conversation session"""
    from sqlalchemy import select
    from app.models import ConversationSession
    
    query = select(ConversationSession).where(
        ConversationSession.id == session_id,
        ConversationSession.user_id == user_id
    )
    
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Delete conversation session"""
    from sqlalchemy import select, delete
    from app.models import ConversationSession
    
    # Verify session belongs to user
    query = select(ConversationSession).where(
        ConversationSession.id == session_id,
        ConversationSession.user_id == user_id
    )
    
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete session
    await db.delete(session)
    await db.commit()
    
    return {"message": "Session deleted successfully"}
