from typing import Optional

from src.schemas.generation import VideoGenerationRequest
from src.services.video_generation.veo3_service import Veo3VideoService
from src.services.video_generation.ltx_service import LtxVideoService
from src.services.video_generation.kling_service import KlingVideoService
from src.services.video_generation.grok_service import GrokVideoService
from src.services.video_generation.luma_service import LumaVideoService
from src.services.video_generation.pika_service import PikaVideoService
from src.services.video_generation.seedance_service import SeedanceVideoService
from src.services.video_generation.hunyuan_service import HunyuanVideoService


class VideoPipeline:
    """Generates a video from a reference image using a configurable video model."""

    def __init__(self, video_model: str = "veo3"):
        """
        Args:
            video_model: The video generation model to use ("veo3", "ltx", "kling", "grok", "luma", "pika", "seedance", "hunyuan", etc.)
        """
        self.video_model = video_model
        self.video_service = self._init_video_service(video_model)

    def _init_video_service(self, model_name: str):
        """Factory to instantiate the appropriate video service."""
        if model_name == "veo3":
            return Veo3VideoService()
        elif model_name == "ltx":
            return LtxVideoService()
        elif model_name == "kling":
            return KlingVideoService()
        elif model_name == "grok":
            return GrokVideoService()
        elif model_name == "luma":
            return LumaVideoService()
        elif model_name == "pika":
            return PikaVideoService()
        elif model_name == "seedance":
            return SeedanceVideoService()
        elif model_name == "hunyuan":
            return HunyuanVideoService()
        else:
            raise ValueError(f"Unknown video model: {model_name}")

    def run(
        self,
        reference_image: str,
        apparel_description: str,
        motion_description: str,
        duration_sec: int,
        no_download: bool = False,
    ) -> dict:
        """
        Generate a video of the person in the reference image.

        Args:
            reference_image: Path or URL to the generated person image.
            apparel_description: Description of the outfit (e.g., "wearing blue shirt and khaki shorts").
            motion_description: Description of the person's motion/action (e.g., "turns around smiling").
            duration_sec: Video duration in seconds (default: 4).

        Returns:
            dict with keys: raw, local_files, metadata_file, latency_sec
        """

        # Build comprehensive prompt with motion description
        prompt = (
            f"A professional video of a person in a realistic setting. "
            f"Outfit: {apparel_description}. "
            f"Motion: {motion_description} "
            f"Professional lighting, clear video quality, smooth motion, no talking."
        )

        req = VideoGenerationRequest(
            prompt=prompt,
            reference_image=reference_image,
            duration_sec=duration_sec,
            num_videos=1,
        )

        print(f"[VideoPipeline] Generating video using {self.video_model}...")
        print(f"  Motion: {motion_description[:60]}...")
        result = self.video_service.generate_video(req, no_download=no_download)
        return {"stage": "video", "video_model": self.video_model, **result}