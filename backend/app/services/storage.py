"""Storage service for snapshots and video clips"""
import os
import logging
from typing import BinaryIO, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Abstract storage service"""
    
    async def upload_snapshot(self, camera_id: str, image_data: bytes, alert_id: str) -> str:
        """Upload snapshot to storage"""
        raise NotImplementedError
    
    async def upload_video_clip(self, camera_id: str, video_data: bytes, alert_id: str) -> str:
        """Upload video clip to storage"""
        raise NotImplementedError
    
    async def get_snapshot(self, url: str) -> bytes:
        """Retrieve snapshot from storage"""
        raise NotImplementedError
    
    async def delete_old_files(self, days: int):
        """Delete files older than specified days"""
        raise NotImplementedError


class LocalStorageService(StorageService):
    """Local file system storage"""
    
    def __init__(self):
        self.base_path = "storage"
        os.makedirs(f"{self.base_path}/snapshots", exist_ok=True)
        os.makedirs(f"{self.base_path}/videos", exist_ok=True)
    
    async def upload_snapshot(self, camera_id: str, image_data: bytes, alert_id: str) -> str:
        """Save snapshot locally"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{camera_id}_{alert_id}_{timestamp}.jpg"
            path = f"{self.base_path}/snapshots/{filename}"
            
            with open(path, "wb") as f:
                f.write(image_data)
            
            return f"/storage/snapshots/{filename}"
        except Exception as e:
            logger.error(f"Error uploading snapshot: {str(e)}")
            return None
    
    async def upload_video_clip(self, camera_id: str, video_data: bytes, alert_id: str) -> str:
        """Save video clip locally"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{camera_id}_{alert_id}_{timestamp}.mp4"
            path = f"{self.base_path}/videos/{filename}"
            
            with open(path, "wb") as f:
                f.write(video_data)
            
            return f"/storage/videos/{filename}"
        except Exception as e:
            logger.error(f"Error uploading video clip: {str(e)}")
            return None
    
    async def get_snapshot(self, url: str) -> bytes:
        """Retrieve snapshot"""
        try:
            path = url.replace("/storage/", f"{self.base_path}/")
            with open(path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error retrieving snapshot: {str(e)}")
            return None


class S3StorageService(StorageService):
    """AWS S3 storage"""
    
    def __init__(self):
        import boto3
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION
        )
        self.bucket = settings.AWS_S3_BUCKET
    
    async def upload_snapshot(self, camera_id: str, image_data: bytes, alert_id: str) -> str:
        """Upload snapshot to S3"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            key = f"snapshots/{camera_id}/{alert_id}_{timestamp}.jpg"
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=image_data,
                ContentType="image/jpeg"
            )
            
            return f"s3://{self.bucket}/{key}"
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return None
    
    async def upload_video_clip(self, camera_id: str, video_data: bytes, alert_id: str) -> str:
        """Upload video clip to S3"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            key = f"videos/{camera_id}/{alert_id}_{timestamp}.mp4"
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=video_data,
                ContentType="video/mp4"
            )
            
            return f"s3://{self.bucket}/{key}"
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return None


def get_storage_service() -> StorageService:
    """Factory function to get storage service"""
    if settings.STORAGE_TYPE == "s3":
        return S3StorageService()
    else:
        return LocalStorageService()
