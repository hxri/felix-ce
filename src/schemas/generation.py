from typing import List, Optional
from pydantic import BaseModel, field_validator


class ImageGenerationRequest(BaseModel):
    prompt: str
    resolution: str = "1024x1024"
    aspect_ratio: str = "1:1"
    num_images: int = 1

    # keep backward-compatible singular fields
    reference_image_path: Optional[str] = None
    reference_image_data_uri: Optional[str] = None

    # new: allow passing multiple reference images (used by edit pipeline)
    reference_images: Optional[List[str]] = None


class VideoGenerationRequest(BaseModel):
    prompt: str
    reference_image: str  # path or data URI to the generated person image
    duration_sec: int = 4
    num_videos: int = 1

    @field_validator("duration_sec")
    @classmethod
    def validate_duration(cls, v):
        """Ensure duration is one of the supported values for veo3."""
        supported = [4, 5, 6, 8, 9]
        if v not in supported:
            raise ValueError(f"duration_sec must be one of {supported}, got {v}")
        return v

