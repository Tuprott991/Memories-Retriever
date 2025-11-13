"""
Upload API Endpoints
Handles media file uploads (photos, videos, audio)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pathlib import Path
import uuid
from loguru import logger

from app.db.database import get_db
from app.models import Memory, MemoryType
from app.schemas import UploadResponse, BulkUploadResponse
from app.services.gcs_service import GCSService
from app.core.config import settings

router = APIRouter()


def get_gcs_service(request: Request) -> GCSService:
    """Get GCS service from app state"""
    return request.app.state.gcs_service


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions


def get_content_type(filename: str) -> str:
    """Get content type from filename"""
    ext = Path(filename).suffix.lower()
    
    # Images
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".png":
        return "image/png"
    elif ext == ".gif":
        return "image/gif"
    elif ext == ".webp":
        return "image/webp"
    
    # Videos
    elif ext == ".mp4":
        return "video/mp4"
    elif ext == ".mov":
        return "video/quicktime"
    elif ext == ".avi":
        return "video/x-msvideo"
    elif ext == ".mkv":
        return "video/x-matroska"
    
    # Audio
    elif ext == ".mp3":
        return "audio/mpeg"
    elif ext == ".wav":
        return "audio/wav"
    elif ext == ".m4a":
        return "audio/mp4"
    elif ext == ".ogg":
        return "audio/ogg"
    
    return "application/octet-stream"


@router.post("/photo", response_model=UploadResponse)
async def upload_photo(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
    gcs: GCSService = Depends(get_gcs_service)
):
    """Upload a photo"""
    # Validate file
    if not validate_file_extension(file.filename, settings.ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
        )
    
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    try:
        # Upload to GCS
        from io import BytesIO
        file_data = BytesIO(content)
        
        media_url = await gcs.upload_photo(
            file_data=file_data,
            filename=file.filename,
            user_id=user_id,
            content_type=get_content_type(file.filename)
        )
        
        # Create memory record
        memory = Memory(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if user_id != "default" else uuid.uuid4(),
            type=MemoryType.PHOTO,
            title=title,
            description=description,
            media_url=media_url,
            tags=[t.strip() for t in tags.split(",")] if tags else []
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        logger.info(f"✅ Uploaded photo {memory.id}")
        
        return UploadResponse(
            memory_id=str(memory.id),
            media_url=media_url,
            message="Photo uploaded successfully"
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to upload photo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
    gcs: GCSService = Depends(get_gcs_service)
):
    """Upload a video"""
    # Validate file
    if not validate_file_extension(file.filename, settings.ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_VIDEO_EXTENSIONS}"
        )
    
    # Check file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    try:
        # Upload to GCS
        from io import BytesIO
        file_data = BytesIO(content)
        
        media_url = await gcs.upload_video(
            file_data=file_data,
            filename=file.filename,
            user_id=user_id,
            content_type=get_content_type(file.filename)
        )
        
        # TODO: Generate thumbnail
        
        # Create memory record
        memory = Memory(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if user_id != "default" else uuid.uuid4(),
            type=MemoryType.VIDEO,
            title=title,
            description=description,
            media_url=media_url,
            tags=[t.strip() for t in tags.split(",")] if tags else []
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        logger.info(f"✅ Uploaded video {memory.id}")
        
        return UploadResponse(
            memory_id=str(memory.id),
            media_url=media_url,
            message="Video uploaded successfully"
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to upload video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
    gcs: GCSService = Depends(get_gcs_service)
):
    """Upload audio/voice note"""
    # Validate file
    if not validate_file_extension(file.filename, settings.ALLOWED_AUDIO_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_AUDIO_EXTENSIONS}"
        )
    
    # Check file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    try:
        # Upload to GCS
        from io import BytesIO
        file_data = BytesIO(content)
        
        media_url = await gcs.upload_audio(
            file_data=file_data,
            filename=file.filename,
            user_id=user_id,
            content_type=get_content_type(file.filename)
        )
        
        # Create memory record
        memory = Memory(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if user_id != "default" else uuid.uuid4(),
            type=MemoryType.VOICE,
            title=title,
            description=description,
            media_url=media_url,
            tags=[t.strip() for t in tags.split(",")] if tags else []
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        logger.info(f"✅ Uploaded audio {memory.id}")
        
        return UploadResponse(
            memory_id=str(memory.id),
            media_url=media_url,
            message="Audio uploaded successfully"
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to upload audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=BulkUploadResponse)
async def bulk_upload(
    files: List[UploadFile] = File(...),
    user_id: str = "default",  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
    gcs: GCSService = Depends(get_gcs_service)
):
    """Bulk upload multiple files"""
    successful = []
    failed = []
    
    for file in files:
        try:
            # Determine file type
            ext = Path(file.filename).suffix.lower()
            
            if ext in settings.ALLOWED_IMAGE_EXTENSIONS:
                memory_type = MemoryType.PHOTO
                upload_func = gcs.upload_photo
            elif ext in settings.ALLOWED_VIDEO_EXTENSIONS:
                memory_type = MemoryType.VIDEO
                upload_func = gcs.upload_video
            elif ext in settings.ALLOWED_AUDIO_EXTENSIONS:
                memory_type = MemoryType.VOICE
                upload_func = gcs.upload_audio
            else:
                failed.append({
                    "filename": file.filename,
                    "error": "Unsupported file type"
                })
                continue
            
            # Read and upload
            content = await file.read()
            from io import BytesIO
            file_data = BytesIO(content)
            
            media_url = await upload_func(
                file_data=file_data,
                filename=file.filename,
                user_id=user_id,
                content_type=get_content_type(file.filename)
            )
            
            # Create memory
            memory = Memory(
                id=uuid.uuid4(),
                user_id=uuid.UUID(user_id) if user_id != "default" else uuid.uuid4(),
                type=memory_type,
                title=Path(file.filename).stem,  # Use filename as title
                media_url=media_url
            )
            
            db.add(memory)
            await db.flush()
            
            successful.append(UploadResponse(
                memory_id=str(memory.id),
                media_url=media_url,
                message=f"{file.filename} uploaded successfully"
            ))
            
        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    await db.commit()
    
    logger.info(f"✅ Bulk upload: {len(successful)} successful, {len(failed)} failed")
    
    return BulkUploadResponse(
        successful=successful,
        failed=failed,
        total=len(files),
        success_count=len(successful),
        failure_count=len(failed)
    )
