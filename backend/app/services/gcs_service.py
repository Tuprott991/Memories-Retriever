"""
Google Cloud Storage Service
Handles media file uploads and retrieval from GCS
"""

from typing import Optional, BinaryIO
from google.cloud import storage
from google.oauth2 import service_account
from loguru import logger
from pathlib import Path
import uuid
from datetime import timedelta

from app.core.config import settings


class GCSService:
    """Google Cloud Storage service for media files"""
    
    def __init__(self):
        self.client: Optional[storage.Client] = None
        self.bucket: Optional[storage.Bucket] = None
        self.bucket_name = settings.GCS_BUCKET_NAME
        
    async def initialize(self):
        """Initialize GCS client and bucket"""
        try:
            # Load credentials if path is provided
            if settings.GCP_CREDENTIALS_PATH:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GCP_CREDENTIALS_PATH
                )
                self.client = storage.Client(
                    project=settings.GCP_PROJECT_ID,
                    credentials=credentials
                )
            else:
                # Use default credentials (from environment)
                self.client = storage.Client(project=settings.GCP_PROJECT_ID)
            
            # Get or create bucket
            try:
                self.bucket = self.client.get_bucket(self.bucket_name)
                logger.success(f"✅ Connected to GCS bucket: {self.bucket_name}")
            except Exception:
                # Bucket doesn't exist, create it
                logger.info(f"Creating GCS bucket: {self.bucket_name}")
                self.bucket = self.client.create_bucket(
                    self.bucket_name,
                    location=settings.GCP_REGION
                )
                logger.success(f"✅ Created GCS bucket: {self.bucket_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCS service: {e}")
            raise
    
    async def upload_photo(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Upload photo to GCS
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: User ID for organizing files
            content_type: MIME type
            
        Returns:
            Public GCS URL
        """
        return await self._upload_file(
            file_data=file_data,
            filename=filename,
            user_id=user_id,
            prefix=settings.GCS_PHOTO_PREFIX,
            content_type=content_type
        )
    
    async def upload_video(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: str,
        content_type: str = "video/mp4"
    ) -> str:
        """
        Upload video to GCS
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: User ID for organizing files
            content_type: MIME type
            
        Returns:
            Public GCS URL
        """
        return await self._upload_file(
            file_data=file_data,
            filename=filename,
            user_id=user_id,
            prefix=settings.GCS_VIDEO_PREFIX,
            content_type=content_type
        )
    
    async def upload_audio(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: str,
        content_type: str = "audio/mpeg"
    ) -> str:
        """
        Upload audio to GCS
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: User ID for organizing files
            content_type: MIME type
            
        Returns:
            Public GCS URL
        """
        return await self._upload_file(
            file_data=file_data,
            filename=filename,
            user_id=user_id,
            prefix=settings.GCS_AUDIO_PREFIX,
            content_type=content_type
        )
    
    async def _upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        user_id: str,
        prefix: str,
        content_type: str
    ) -> str:
        """
        Upload file to GCS with user-specific organization
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: User ID
            prefix: GCS prefix (photos/, videos/, audio/)
            content_type: MIME type
            
        Returns:
            Public GCS URL
        """
        if not self.bucket:
            raise RuntimeError("GCS bucket not initialized")
        
        try:
            # Generate unique filename
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Construct blob path: prefix/user_id/unique_filename
            blob_path = f"{prefix}{user_id}/{unique_filename}"
            
            # Create blob
            blob = self.bucket.blob(blob_path)
            
            # Set content type
            blob.content_type = content_type
            
            # Upload file
            blob.upload_from_file(file_data, content_type=content_type)
            
            # Make blob public (optional - depends on security requirements)
            # blob.make_public()
            
            # Get public URL
            public_url = f"gs://{self.bucket_name}/{blob_path}"
            
            logger.info(f"✅ Uploaded file to GCS: {blob_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload file to GCS: {e}")
            raise
    
    async def generate_signed_url(
        self,
        blob_path: str,
        expiration: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Generate signed URL for private blob access
        
        Args:
            blob_path: GCS blob path
            expiration: URL expiration time
            
        Returns:
            Signed URL
        """
        if not self.bucket:
            raise RuntimeError("GCS bucket not initialized")
        
        try:
            # Remove gs:// prefix if present
            if blob_path.startswith(f"gs://{self.bucket_name}/"):
                blob_path = blob_path.replace(f"gs://{self.bucket_name}/", "")
            
            blob = self.bucket.blob(blob_path)
            
            # Generate signed URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            
            return signed_url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate signed URL: {e}")
            raise
    
    async def delete_file(self, blob_path: str) -> bool:
        """
        Delete file from GCS
        
        Args:
            blob_path: GCS blob path
            
        Returns:
            Success status
        """
        if not self.bucket:
            raise RuntimeError("GCS bucket not initialized")
        
        try:
            # Remove gs:// prefix if present
            if blob_path.startswith(f"gs://{self.bucket_name}/"):
                blob_path = blob_path.replace(f"gs://{self.bucket_name}/", "")
            
            blob = self.bucket.blob(blob_path)
            blob.delete()
            
            logger.info(f"✅ Deleted file from GCS: {blob_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete file from GCS: {e}")
            return False
    
    async def list_user_files(
        self,
        user_id: str,
        prefix: Optional[str] = None,
        max_results: int = 1000
    ) -> list[str]:
        """
        List all files for a user
        
        Args:
            user_id: User ID
            prefix: Optional prefix filter (photos/, videos/, audio/)
            max_results: Maximum number of results
            
        Returns:
            List of blob paths
        """
        if not self.bucket:
            raise RuntimeError("GCS bucket not initialized")
        
        try:
            # Construct prefix
            search_prefix = f"{prefix}{user_id}/" if prefix else f"{user_id}/"
            
            # List blobs
            blobs = self.bucket.list_blobs(prefix=search_prefix, max_results=max_results)
            
            # Extract blob names
            blob_paths = [blob.name for blob in blobs]
            
            logger.info(f"✅ Found {len(blob_paths)} files for user {user_id}")
            return blob_paths
            
        except Exception as e:
            logger.error(f"❌ Failed to list user files: {e}")
            return []
