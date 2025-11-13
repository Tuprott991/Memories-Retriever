"""
Memory API Endpoints
CRUD operations for memories
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from loguru import logger
import uuid

from app.db.database import get_db
from app.models import Memory, Face, MemoryType
from app.schemas import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    FaceResponse
)

router = APIRouter()


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(
    memory: MemoryCreate,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Create a new memory"""
    try:
        # Create memory instance
        db_memory = Memory(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if user_id != "default" else uuid.uuid4(),
            type=memory.type,
            title=memory.title,
            description=memory.description,
            note_content=memory.note_content,
            timestamp=memory.timestamp,
            tags=memory.tags or [],
            metadata=memory.metadata,
            has_faces=bool(memory.faces)
        )
        
        db.add(db_memory)
        await db.flush()
        
        # Create face annotations if provided
        if memory.faces:
            for face_data in memory.faces:
                db_face = Face(
                    id=uuid.uuid4(),
                    memory_id=db_memory.id,
                    x=face_data.x,
                    y=face_data.y,
                    width=face_data.width,
                    height=face_data.height,
                    name=face_data.name,
                    description=face_data.description
                )
                db.add(db_face)
        
        await db.commit()
        await db.refresh(db_memory)
        
        # Load faces relationship
        query = select(Face).where(Face.memory_id == db_memory.id)
        result = await db.execute(query)
        db_memory.faces = result.scalars().all()
        
        logger.info(f"✅ Created memory {db_memory.id}")
        return db_memory
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to create memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    user_id: str = "default",  # TODO: Get from auth
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[MemoryType] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    db: AsyncSession = Depends(get_db)
):
    """List memories with pagination and filters"""
    query = select(Memory).where(Memory.user_id == user_id)
    
    # Apply filters
    if type:
        query = query.where(Memory.type == type)
    
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.where(Memory.tags.overlap(tag_list))
    
    # Order and paginate
    query = query.order_by(Memory.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    memories = result.scalars().all()
    
    # Load faces for each memory
    for memory in memories:
        face_query = select(Face).where(Face.memory_id == memory.id)
        face_result = await db.execute(face_query)
        memory.faces = face_result.scalars().all()
    
    return memories


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Get specific memory by ID"""
    query = select(Memory).where(
        Memory.id == memory_id,
        Memory.user_id == user_id
    )
    
    result = await db.execute(query)
    memory = result.scalar_one_or_none()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Load faces
    face_query = select(Face).where(Face.memory_id == memory.id)
    face_result = await db.execute(face_query)
    memory.faces = face_result.scalars().all()
    
    return memory


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Update memory"""
    # Get existing memory
    query = select(Memory).where(
        Memory.id == memory_id,
        Memory.user_id == user_id
    )
    
    result = await db.execute(query)
    memory = result.scalar_one_or_none()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Update fields
    update_data = memory_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memory, field, value)
    
    await db.commit()
    await db.refresh(memory)
    
    # Load faces
    face_query = select(Face).where(Face.memory_id == memory.id)
    face_result = await db.execute(face_query)
    memory.faces = face_result.scalars().all()
    
    logger.info(f"✅ Updated memory {memory_id}")
    return memory


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Delete memory"""
    query = select(Memory).where(
        Memory.id == memory_id,
        Memory.user_id == user_id
    )
    
    result = await db.execute(query)
    memory = result.scalar_one_or_none()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # TODO: Delete associated media from GCS
    
    await db.delete(memory)
    await db.commit()
    
    logger.info(f"✅ Deleted memory {memory_id}")
    return {"message": "Memory deleted successfully"}


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    search_request: MemorySearchRequest,
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Search memories using semantic search"""
    # TODO: Implement semantic search with embeddings
    # For now, simple text search
    
    query = select(Memory).where(Memory.user_id == user_id)
    
    # Simple text search in title and description
    search_term = f"%{search_request.query}%"
    query = query.where(
        (Memory.title.ilike(search_term)) | 
        (Memory.description.ilike(search_term))
    )
    
    query = query.order_by(Memory.created_at.desc()).limit(search_request.limit)
    
    result = await db.execute(query)
    memories = result.scalars().all()
    
    # Load faces
    for memory in memories:
        face_query = select(Face).where(Face.memory_id == memory.id)
        face_result = await db.execute(face_query)
        memory.faces = face_result.scalars().all()
    
    return MemorySearchResponse(
        memories=memories,
        total=len(memories),
        query=search_request.query,
        reasoning=f"Searched for '{search_request.query}' in titles and descriptions"
    )


@router.get("/stats/summary")
async def get_memory_stats(
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db)
):
    """Get memory statistics"""
    # Total count
    total_query = select(func.count()).select_from(Memory).where(Memory.user_id == user_id)
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Count by type
    type_query = select(Memory.type, func.count()).where(
        Memory.user_id == user_id
    ).group_by(Memory.type)
    type_result = await db.execute(type_query)
    by_type = {row[0].value: row[1] for row in type_result.all()}
    
    return {
        "total": total,
        "by_type": by_type,
        "photos": by_type.get("photo", 0),
        "videos": by_type.get("video", 0),
        "voice_notes": by_type.get("voice", 0),
        "text_notes": by_type.get("note", 0)
    }
